"""
Payroll API Routes.

Exposes endpoints for triggering payroll runs.
"""

import uuid
from decimal import Decimal
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InternalError as SQLInternalError
from backend.domain.payroll.period_context import build_period_context
from backend.infra.db.session import SessionLocal
from backend.application.payroll_run_service import execute_and_persist
from backend.application.payroll_retry_service import retry_failed_payroll_employees
from backend.application.payroll_approval_service import approve_payroll_run, lock_payroll_run, mark_payroll_run_paid
from backend.application.reconciliation_service import reconcile_payroll_run, get_reconciliation_status
from backend.infra.repositories.execution_trace_repo import get_trace_steps
from backend.infra.repositories.payroll_input_repo import link_inputs_to_run, load_unclaimed_inputs_by_employee

router = APIRouter()


@router.post("/payroll/run")
def run_payroll(
    payload: dict,
    idempotency_key: str | None = Header(default=None),
):
    """
    Trigger a payroll run for a workspace.

    Accepts an optional ``Idempotency-Key`` HTTP header.  When supplied,
    a second request with the same key for the same workspace returns the
    original payroll_run_id without re-executing the calculation.

    The payload may include optional ``period_start`` and ``period_end``
    (ISO-format dates).  When provided, the unique index
    ``uq_payroll_run_period`` prevents a second run for the same period,
    returning HTTP 409.
    """

    workspace_id       = payload.get("workspace_id")
    period_start       = payload.get("period_start")
    period_end         = payload.get("period_end")
    period_type_raw    = payload.get("period_type")
    working_days_input = payload.get("working_days")
    retry_strategy     = payload.get("retry_strategy", "PER_EMPLOYEE")

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")

    if period_type_raw and period_type_raw.upper() == "CUSTOM" and not working_days_input:
        raise HTTPException(
            status_code=422,
            detail="working_days is required when period_type is CUSTOM",
        )

    db = SessionLocal()

    # --- Verify workspace exists, load country_code ---
    workspace = db.execute(
        text("SELECT workspace_id, country_code FROM workspace WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchone()

    if not workspace:
        db.close()
        raise HTTPException(status_code=404, detail="Workspace not found")

    country_code = workspace[1]

    # --- Idempotency check: return existing run without re-executing ---
    if idempotency_key:
        existing = db.execute(
            text("""
                SELECT payroll_run_id
                FROM   payroll_run
                WHERE  workspace_id    = :wid
                  AND  idempotency_key = :key
            """),
            {"wid": workspace_id, "key": idempotency_key},
        ).fetchone()

        if existing:
            db.close()
            return {
                "status":          "success",
                "payroll_run_id":  str(existing[0]),
                "idempotent":      True,
            }

    # --- Load Employees ---
    employee_rows = db.execute(text("""
        SELECT e.employee_id, sd.components_jsonb, ec.start_date, ec.end_date
        FROM employee e
        JOIN employee_contract ec
          ON e.employee_id = ec.employee_id
        JOIN salary_definition sd
          ON ec.salary_definition_id = sd.salary_definition_id
        WHERE e.workspace_id = :workspace_id
          AND e.status = 'ACTIVE'
          AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
    """), {"workspace_id": workspace_id}).fetchall()

    employees = []
    for row in employee_rows:
        employees.append({
            "employee_id":     str(row[0]),
            "components": [
                {"code": k, "amount": v["amount"] if isinstance(v, dict) else v}
                for k, v in row[1].items()
            ],
            "contract_start": row[2].isoformat() if row[2] else None,
            "contract_end":   row[3].isoformat() if row[3] else None,
        })

    if not employees:
        db.close()
        raise HTTPException(status_code=400, detail="No active employees found")

    print("Employees being processed:", len(employees))
    for e in employees:
        print(e["employee_id"])

    # --- Load Statutory Rule — platform-level, resolved by workspace country_code ---
    stat_row = db.execute(text("""
        SELECT sr.statutory_rule_id, sr.version, sr.rules_jsonb
        FROM statutory_rule sr
        JOIN workspace w ON sr.country_code = w.country_code
        WHERE w.workspace_id = :workspace_id
        ORDER BY sr.version DESC
        LIMIT 1
    """), {"workspace_id": workspace_id}).fetchone()

    if not stat_row:
        db.close()
        raise HTTPException(status_code=400, detail="No statutory rule found for this workspace's country")

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]
    rules_jsonb       = stat_row[2] or {}

    # Extract pension rates; fall back to PRA 2014 defaults (9% / 10%)
    pension_config        = rules_jsonb.get("pension", {})
    pension_employee_rate = Decimal(str(pension_config.get("employee_rate", "0.09")))
    pension_employer_rate = Decimal(str(pension_config.get("employer_rate", "0.10")))

    # Extract rent relief config (used by sequential executor for PAYE annualisation)
    rent_relief_cfg = rules_jsonb.get("reliefs", {}).get("rent_relief", {})

    # Extract workspace-level statutory component rates/amounts
    nhf_rate                         = Decimal(str(rules_jsonb.get("nhf", {}).get("rate", "0.025")))
    health_insurance_employee_amount = Decimal(str(rules_jsonb.get("health_insurance", {}).get("employee_monthly_amount", "0")))
    development_levy_amount          = Decimal(str(rules_jsonb.get("development_levy", {}).get("monthly_amount", "0")))
    life_insurance_employer_rate     = Decimal(str(rules_jsonb.get("life_insurance", {}).get("employer_rate", "0")))

    # --- Load Tax Bands (scoped to the selected statutory rule) ---
    tax_rows = db.execute(text("""
        SELECT lower_limit, upper_limit, rate
        FROM tax_band
        WHERE statutory_rule_id = :sr_id
        ORDER BY lower_limit
    """), {"sr_id": statutory_rule_id}).fetchall()

    tax_bands = [
        {"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]}
        for r in tax_rows
    ]

    # --- Load Active Payroll Rules (IDs for snapshot + full dicts for rule evaluator) ---
    rule_rows = db.execute(text("""
        SELECT rule_id, rule_name, rule_definition_json, is_active
        FROM payroll_rule
        WHERE is_active = TRUE
          AND workspace_id = :workspace_id
    """), {"workspace_id": workspace_id}).fetchall()

    payroll_rule_ids  = [str(r[0]) for r in rule_rows]
    payroll_rules_full = [
        {
            "rule_id":              str(r[0]),
            "rule_name":            r[1],
            "rule_definition_json": r[2],
            "is_active":            r[3],
        }
        for r in rule_rows
    ]

    # --- Load Pay Cycle (frequency drives period_type default; definition_json is extension data) ---
    pay_cycle_row = db.execute(text("""
        SELECT frequency, definition_json
        FROM pay_cycle
        WHERE workspace_id = :workspace_id
          AND is_active = TRUE
        LIMIT 1
    """), {"workspace_id": workspace_id}).fetchone()

    pay_cycle_frequency  = pay_cycle_row[0] if pay_cycle_row else None
    pay_cycle_definition = pay_cycle_row[1] if pay_cycle_row else None

    # Build PeriodContext now that we have the workspace's configured frequency.
    # Priority: explicit API field > workspace pay_cycle.frequency > infer from dates.
    try:
        period_ctx = build_period_context(
            period_start=period_start,
            period_end=period_end,
            period_type=period_type_raw or pay_cycle_frequency,
            working_days_override=working_days_input,
        )
    except ValueError as exc:
        db.close()
        raise HTTPException(status_code=422, detail=str(exc))

    # --- Load Component Metadata for sequential executor ---
    component_metadata_rows = db.execute(text("""
        SELECT component_code, component_class, calculation_method,
               execution_priority, is_active, metadata_json
        FROM component_metadata
        WHERE country_code = :country_code
          AND is_active    = TRUE
        ORDER BY execution_priority
    """), {"country_code": country_code}).fetchall()

    component_metadata = [
        {
            "component_code":     r[0],
            "component_class":    r[1],
            "calculation_method": r[2],
            "execution_priority": r[3],
            "is_active":          r[4],
            "metadata_json":      r[5],
        }
        for r in component_metadata_rows
    ]

    # --- Load workspace component overrides (is_active suppression + flat-amount overrides) ---
    override_rows = db.execute(text("""
        SELECT component_code, overrides_json
        FROM client_component_metadata
        WHERE workspace_id = :wid
    """), {"wid": workspace_id}).fetchall()

    client_overrides = {r[0]: r[1] for r in override_rows}

    # Remove components the workspace has disabled
    disabled_codes = {code for code, ov in client_overrides.items() if not ov.get("is_active", True)}
    if disabled_codes:
        component_metadata = [m for m in component_metadata if m["component_code"] not in disabled_codes]

    # Apply flat-amount overrides for workspace-configurable components
    if "DEVELOPMENT_LEVY" in client_overrides and "monthly_amount" in client_overrides["DEVELOPMENT_LEVY"]:
        development_levy_amount = Decimal(str(client_overrides["DEVELOPMENT_LEVY"]["monthly_amount"]))

    if "HEALTH_INSURANCE_EMPLOYEE" in client_overrides and "employee_monthly_amount" in client_overrides["HEALTH_INSURANCE_EMPLOYEE"]:
        health_insurance_employee_amount = Decimal(str(client_overrides["HEALTH_INSURANCE_EMPLOYEE"]["employee_monthly_amount"]))

    # Build client_meta: global component metadata as the base layer with
    # workspace-specific overrides layered on top (one-level-deep merge).
    # This makes proration_strategy available for all earning components
    # even when client_component_metadata has no rows for this workspace.
    client_meta = {
        m["component_code"]: dict(m.get("metadata_json") or {})
        for m in component_metadata
    }
    for code, ws_override in client_overrides.items():
        if code not in client_meta:
            client_meta[code] = {}
        for key, val in ws_override.items():
            if (
                key in client_meta[code]
                and isinstance(client_meta[code][key], dict)
                and isinstance(val, dict)
            ):
                # Deep-merge nested dicts (e.g. calculations_behaviour)
                client_meta[code][key] = {**client_meta[code][key], **val}
            else:
                client_meta[code][key] = val

    db.close()

    payroll_run_id = str(uuid.uuid4())

    # Load unclaimed inputs without linking (payroll_run row doesn't exist yet —
    # linking here would violate the FK constraint on payroll_input.payroll_run_id).
    inputs_by_employee = load_unclaimed_inputs_by_employee(
        workspace_id,
        period_start=period_ctx.period_start,
        period_end=period_ctx.period_end,
    )
    for emp in employees:
        emp["inputs"] = inputs_by_employee.get(emp["employee_id"], {})

    context = {
        "tax_bands":                        tax_bands,
        "pension_employee_rate":            pension_employee_rate,
        "pension_employer_rate":            pension_employer_rate,
        "rent_relief_cfg":                  rent_relief_cfg,
        "nhf_rate":                         nhf_rate,
        "health_insurance_employee_amount": health_insurance_employee_amount,
        "development_levy_amount":          development_levy_amount,
        "life_insurance_employer_rate":     life_insurance_employer_rate,
        "client_meta":                      client_meta,
        "period":                           period_ctx,
        "payroll_rules":                    payroll_rules_full,
    }

    try:
        result = execute_and_persist(
            payroll_run_id=payroll_run_id,
            workspace_id=workspace_id,
            employees=employees,
            tax_bands=tax_bands,
            statutory_rule_id=statutory_rule_id,
            statutory_version=statutory_version,
            payroll_rule_ids=payroll_rule_ids,
            performed_by="admin@internal",
            execution_mode="isolated",
            idempotency_key=idempotency_key,
            period_start=period_start,
            period_end=period_end,
            pay_cycle_definition=pay_cycle_definition,
            retry_strategy=retry_strategy,
            component_metadata=component_metadata or None,
            context=context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except SQLInternalError as exc:
        error_str = str(exc)
        if "PAYROLL_ALREADY_EXISTS" in error_str:
            raise HTTPException(
                status_code=409,
                detail="A payroll run already exists for this period.",
            )
        if "Payroll readiness failed:" in error_str:
            import re, json as _json
            match = re.search(r'Payroll readiness failed: (\[.*?\])', error_str, re.DOTALL)
            if match:
                try:
                    errors = _json.loads(match.group(1))
                    messages = " | ".join(e["message"] for e in errors)
                    raise HTTPException(
                        status_code=422,
                        detail={"error": "PAYROLL_NOT_READY", "message": messages},
                    )
                except (ValueError, KeyError):
                    pass
            raise HTTPException(
                status_code=422,
                detail={"error": "PAYROLL_NOT_READY", "message": "Payroll readiness check failed."},
            )
        raise

    # payroll_run row now exists — safe to claim inputs against it
    link_inputs_to_run(
        workspace_id=workspace_id,
        payroll_run_id=payroll_run_id,
        period_start=period_ctx.period_start,
        period_end=period_ctx.period_end,
    )

    return {
        "status":         "success",
        "payroll_run_id": payroll_run_id,
        "summary":        result["totals"],
    }


@router.post("/{workspace_id}/payroll/run")
def run_payroll_scoped(
    workspace_id: str,
    payload: dict,
    idempotency_key: str | None = Header(default=None),
):
    """Workspace-scoped payroll run trigger. Delegates to the core run logic."""
    payload["workspace_id"] = workspace_id
    result = run_payroll(payload, idempotency_key)
    # Normalise response key for the frontend (run_id vs payroll_run_id)
    return {
        "run_id": result.get("payroll_run_id", result.get("run_id")),
        "status": result.get("status"),
    }


@router.get("/{workspace_id}/payroll/runs")
def list_payroll_runs(workspace_id: str):
    """List all payroll runs for a workspace, newest first."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT payroll_run_id, workspace_id, status,
                       period_start, period_end, pay_date,
                       created_at, total_net_pay, total_gross_pay, total_deduction
                FROM payroll_run
                WHERE workspace_id = :wid
                ORDER BY created_at DESC
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "run_id":       str(r[0]),
                "workspace_id": str(r[1]),
                "status":       r[2],
                "period_start": str(r[3]) if r[3] else None,
                "period_end":   str(r[4]) if r[4] else None,
                "pay_date":     str(r[5]) if r[5] else None,
                "created_at":   str(r[6]) if r[6] else None,
                "total_net_pay": float(r[7]) if r[7] is not None else 0,
            }
            for r in rows
        ]
    finally:
        db.close()


@router.get("/{workspace_id}/payroll/runs/{run_id}")
def get_payroll_run(workspace_id: str, run_id: str):
    """Get a single payroll run."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT payroll_run_id, workspace_id, status,
                       period_start, period_end, pay_date, created_at
                FROM payroll_run
                WHERE payroll_run_id = :rid AND workspace_id = :wid
            """),
            {"rid": run_id, "wid": workspace_id},
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Payroll run not found")

        return {
            "run_id":       str(row[0]),
            "workspace_id": str(row[1]),
            "status":       row[2],
            "period_start": str(row[3]) if row[3] else None,
            "period_end":   str(row[4]) if row[4] else None,
            "pay_date":     str(row[5]) if row[5] else None,
            "created_at":   str(row[6]) if row[6] else None,
        }
    finally:
        db.close()


@router.get("/{workspace_id}/payroll/runs/{run_id}/results")
def get_payroll_run_results(workspace_id: str, run_id: str):
    """Get per-employee results and totals for a payroll run."""
    db = SessionLocal()
    try:
        run_row = db.execute(
            text("""
                SELECT status, total_gross_pay, total_deduction, total_net_pay
                FROM payroll_run
                WHERE payroll_run_id = :rid AND workspace_id = :wid
            """),
            {"rid": run_id, "wid": workspace_id},
        ).fetchone()

        if not run_row:
            raise HTTPException(status_code=404, detail="Payroll run not found")

        result_rows = db.execute(
            text("""
                SELECT
                    pr.employee_id,
                    e.full_name,
                    e.employee_number,
                    pr.net_pay,
                    pr.gross_components_jsonb,
                    pr.deductions_jsonb,
                    pr.status
                FROM payroll_result pr
                JOIN employee e ON e.employee_id = pr.employee_id
                WHERE pr.payroll_run_id = :rid
                ORDER BY e.full_name
            """),
            {"rid": run_id},
        ).fetchall()

        results = []
        for r in result_rows:
            status = r[6]
            gross_components = r[4] or {}
            deductions = r[5] or {}
            gross_total = sum(
                float(v.get("amount", v) if isinstance(v, dict) else v)
                for v in gross_components.values()
            )
            deductions_total = sum(
                float(v.get("amount", v) if isinstance(v, dict) else v)
                for v in deductions.values()
            )
            results.append({
                "employee_id":      str(r[0]),
                "employee_name":    r[1] or "",
                "employee_number":  r[2] or "",
                "gross_pay":        float(gross_total) if status == "SUCCESS" else None,
                "total_deductions": float(deductions_total) if status == "SUCCESS" else None,
                "net_pay":          float(r[3]) if r[3] is not None else None,
                "status":           status,
            })

        return {
            "results": results,
            "totals": {
                "gross":          float(run_row[1] or 0),
                "deductions":     float(run_row[2] or 0),
                "net":            float(run_row[3] or 0),
                "employee_count": len(results),
            },
        }
    finally:
        db.close()


@router.post("/payroll/run/{run_id}/retry")
def retry_payroll_run(run_id: str):
    """
    Retry all FAILED employees in a PARTIAL payroll run.

    Only employees with status='FAILED' are reprocessed. Employees that
    already succeeded are never touched. If the corrected data now passes
    calculation the result is updated to SUCCESS and the run transitions
    to CALCULATED once all failures are resolved.

    Returns 400 if the run does not exist, is PAID, or is not PARTIAL.
    """
    try:
        result = retry_failed_payroll_employees(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status":       "success",
        "run_id":       result["payroll_run_id"],
        "retried":      result["retried"],
        "success":      result["success"],
        "still_failed": result["still_failed"],
    }


@router.post("/payroll/run/{run_id}/approve")
def approve_run(run_id: str):
    """
    Approve a CALCULATED payroll run (CALCULATED → APPROVED).

    Once approved the run can only be locked — it cannot be retried or
    recalculated.  Returns 400 if the run is not in CALCULATED state.
    """
    try:
        result = approve_payroll_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status":     "success",
        "run_id":     result["payroll_run_id"],
        "run_status": result["status"],
    }


@router.post("/payroll/run/{run_id}/lock")
def lock_run(run_id: str):
    """
    Lock an APPROVED payroll run (APPROVED → LOCKED).

    A LOCKED run is permanently immutable.  Returns 400 if the run is not
    in APPROVED state.
    """
    try:
        result = lock_payroll_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status":     "success",
        "run_id":     result["payroll_run_id"],
        "run_status": result["status"],
    }


@router.post("/payroll/run/{run_id}/pay")
def pay_run(run_id: str, payload: dict = {}):
    """
    Mark a LOCKED payroll run as PAID (LOCKED → PAID).

    PAID is the terminal state.  After this transition the DB trigger
    trg_prevent_paid_run_update enforces full immutability — no further
    changes are possible.  Returns 400 if the run is not in LOCKED state.
    """
    actor_id = payload.get("actor_id", "system@internal")

    try:
        result = mark_payroll_run_paid(run_id, actor_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status":     "success",
        "run_id":     result["payroll_run_id"],
        "run_status": result["status"],
    }


@router.post("/payroll/run/{run_id}/reconcile")
def reconcile_run(run_id: str, payload: dict):
    """
    Reconcile a payroll run against an externally confirmed payment total.

    Compares payroll_run.total_net_pay (the engine's expected total) against
    the caller-supplied ``actual_total`` and writes a payroll_reconciliation
    record with status MATCHED or MISMATCH.

    Only one reconciliation record is allowed per run (HTTP 409 on retry).

    Body: ``{ "actual_total": <number> }``
    """
    actual_total = payload.get("actual_total")
    if actual_total is None:
        raise HTTPException(status_code=400, detail="actual_total is required")

    try:
        from decimal import Decimal
        record = reconcile_payroll_run(run_id, Decimal(str(actual_total)))
    except ValueError as exc:
        error = str(exc)
        status_code = 409 if "already exists" in error else 404 if "not found" in error else 400
        raise HTTPException(status_code=status_code, detail=error)

    return {"status": "success", "reconciliation": record}


@router.get("/payroll/run/{run_id}/reconcile")
def get_reconciliation(run_id: str):
    """
    Retrieve the reconciliation record for a payroll run.

    Returns 404 if no reconciliation has been created yet.
    """
    record = get_reconciliation_status(run_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No reconciliation found for run {run_id}.",
        )
    return {"status": "success", "reconciliation": record}


def _to_reconciliation_record(record: dict) -> dict:
    """Map backend field names to frontend ReconciliationRecord shape."""
    return {
        "run_id":         record.get("payroll_run_id"),
        "expected_total": float(record["expected_total"]) if record.get("expected_total") is not None else None,
        "actual_payment": float(record["actual_total"]) if record.get("actual_total") is not None else None,
        "status":         record.get("status"),
    }


@router.get("/{workspace_id}/payroll/runs/{run_id}/reconciliation")
def get_reconciliation_scoped(workspace_id: str, run_id: str):
    """Get the reconciliation record for a payroll run (workspace-scoped)."""
    record = get_reconciliation_status(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No reconciliation found for run {run_id}.")
    return _to_reconciliation_record(record)


@router.post("/{workspace_id}/payroll/runs/{run_id}/reconciliation")
def submit_reconciliation_scoped(workspace_id: str, run_id: str, payload: dict):
    """Submit an actual payment total and create a reconciliation record (workspace-scoped)."""
    actual_payment = payload.get("actual_payment")
    if actual_payment is None:
        raise HTTPException(status_code=400, detail="actual_payment is required")
    try:
        from decimal import Decimal
        record = reconcile_payroll_run(run_id, Decimal(str(actual_payment)))
    except ValueError as exc:
        error = str(exc)
        status_code = 409 if "already exists" in error else 404 if "not found" in error else 400
        raise HTTPException(status_code=status_code, detail=error)
    return _to_reconciliation_record(record)


@router.get("/{workspace_id}/payroll/runs/{run_id}/timeline")
def get_run_timeline(workspace_id: str, run_id: str):
    """Return all execution trace steps for a payroll run, ordered by time."""
    steps = get_trace_steps(run_id)
    return steps
