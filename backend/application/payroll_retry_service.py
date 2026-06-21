"""
Payroll Retry Service.

Retries only the FAILED employees from a PARTIAL payroll run.
Successful employees are never touched.

Retry flow (per employee)
--------------------------
1. Load the employee's current salary components from the DB.
2. Attempt payroll calculation (pure, no side-effects).
3. DELETE the old FAILED row  ← only after calculation completes (or fails).
4. INSERT the new result row (SUCCESS or FAILED).

The DELETE happens AFTER the calculation attempt — not before.  This means
the old row stays alive until we are certain of the replacement, so a crash
between step 2 and step 4 leaves the data in a consistent state (old FAILED
row is still there, not deleted).

Why DELETE + INSERT rather than UPDATE
---------------------------------------
trg_snapshot_immutable (migration fe0bad282b7d) fires BEFORE UPDATE OF
calculations_snapshot_json when the value changes.  FAILED rows store {},
a successful retry writes real values — so any UPDATE that touches that
column is rejected.  INSERT on a fresh row is not subject to this trigger.

The unique index uq_payroll_result_employee_run (migration 6f5b05ff4690)
enforces one result per (payroll_run_id, employee_id), so the DELETE must
precede the INSERT.

DELETE guard (status = 'FAILED')
---------------------------------
The DELETE includes AND status = 'FAILED'.  This prevents accidental
removal of a SUCCESS row in the (unlikely) event of a race between two
concurrent retry calls.  The FOR UPDATE lock on payroll_run makes such
races impossible under normal conditions, but the guard is a safety net.

Run status recomputation
------------------------
After all employees are processed, the new run status is derived by
counting ALL remaining FAILED rows for the run — not from local counters.
This is correct even if the DB already had partially inconsistent state
before the retry.

  remaining_failed == 0  →  CALCULATED
  remaining_failed  > 0  →  PARTIAL

The DB state machine trigger (migration 9901bc4ed0c5) only enforces
DRAFT, PROCESSING, COMPLETED, and PAID transitions.  PARTIAL → CALCULATED
falls through to RETURN NEW and is therefore allowed.

Idempotency
-----------
If no FAILED rows exist the function returns immediately with retried=0
without touching any data.

Blocked states
--------------
PAID runs are rejected before any work begins.  The DB triggers would also
reject any writes, but the early ValueError is cleaner.
"""

from datetime import date
from decimal import Decimal

from psycopg2.extras import Json
from sqlalchemy import text

from backend.application.execution_tracer import ExecutionTracer
from backend.domain.payroll.audit_events import build_transition_audit, build_transition_event
from backend.domain.payroll.executor import execute_single_employee_payroll
from backend.domain.payroll.period_context import build_period_context
from backend.domain.payroll.salary_derivation import derive_salary_components
from backend.domain.payroll.status import PayrollRunStatus
from backend.infra.db.session import SessionLocal
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event
from backend.infra.repositories.payroll_input_repo import load_inputs_for_run
from backend.infra.repositories.payroll_result_repo import get_employee_context_from_result
from backend.infra.json_utils import sanitize_jsonb as _sanitize
from backend.infra.repositories.rate_code_repo import list_rate_codes
from backend.application.snapshot_service import validate_snapshot_complete


def _build_shared_context(db, workspace_id: str, payroll_run_id: str) -> dict:
    """Build the same execution context that the original /payroll/run route builds.

    Loads period dates from the payroll_run row, resolves statutory rule via
    country_code and statutory_effective_date (temporal selection), loads
    component_metadata, client_meta, payroll_rules (from rule_set_id if present),
    and all statutory rate parameters.  Returns a dict with keys:

        "context"            — full context dict for execute_single_employee_payroll
        "component_metadata" — list of component dicts for the sequential executor
        "tax_bands"          — list of tax band dicts
        "statutory_rule_id"  — str
        "statutory_version"  — int
        "payroll_rule_ids"   — list[str]  (legacy v1 snapshot only; empty for v2)
        "rules_context_snapshot" — original run snapshot (for snapshot-driven retry)
    """
    # ── Load workspace country_code, run period dates, and new temporal columns ─
    row = db.execute(
        text("""
            SELECT w.country_code, pr.period_start, pr.period_end,
                   pr.rule_set_id, pr.statutory_effective_date,
                   pr.rules_context_snapshot, pr.public_holidays_snapshot
            FROM   payroll_run pr
            JOIN   workspace   w  ON pr.workspace_id = w.workspace_id
            WHERE  pr.payroll_run_id = :run_id
        """),
        {"run_id": payroll_run_id},
    ).fetchone()

    if row is None:
        raise ValueError(f"Payroll run not found: {payroll_run_id}")

    country_code              = row[0]
    period_start              = row[1]
    period_end                = row[2]
    rule_set_id               = str(row[3]) if row[3] else None
    statutory_effective_date  = row[4]
    original_snapshot         = row[5] or {}
    ph_snapshot               = row[6]

    if period_start is None or period_end is None:
        raise ValueError(
            f"Run {payroll_run_id} has no period dates — cannot retry."
        )

    if ph_snapshot is None:
        raise ValueError(
            f"Run {payroll_run_id} has no public holiday snapshot — open a correction run."
        )
    public_holiday_dates = {date.fromisoformat(d) for d in ph_snapshot}

    # D3/D6: abort if snapshot is absent or incomplete — hard-fail, not skip
    validate_snapshot_complete(db, payroll_run_id)

    period_ctx = build_period_context(
        period_start=period_start,
        period_end=period_end,
        public_holiday_dates=public_holiday_dates,
    )

    # ── Statutory rule — temporal selection ──────────────────────────────────
    # Use statutory_effective_date from the original run so that retry picks the
    # same statutory rule as the run that created the snapshot.  Fall back to
    # latest-version query for legacy runs without the column.
    if statutory_effective_date:
        stat_row = db.execute(
            text("""
                SELECT sr.statutory_rule_id, sr.version, sr.rules_jsonb
                FROM   statutory_rule sr
                WHERE  sr.country_code    = :cc
                  AND  sr.effective_from <= :as_of_date
                ORDER  BY sr.effective_from DESC, sr.version DESC
                LIMIT  1
            """),
            {"cc": country_code, "as_of_date": statutory_effective_date},
        ).fetchone()
    else:
        raise ValueError(
            f"Run {payroll_run_id} predates snapshot engine — open a correction run."
        )

    if stat_row is None:
        raise ValueError(f"No statutory rule found for country_code '{country_code}'")

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]
    rules_jsonb       = stat_row[2] or {}

    pension_config = rules_jsonb.get("pension")
    if not pension_config or "employee_rate" not in pension_config or "employer_rate" not in pension_config:
        raise ValueError(
            "Statutory rule is missing pension rates (employee_rate / employer_rate). "
            "Run the pension rates migration."
        )
    pension_employee_rate = Decimal(str(pension_config["employee_rate"]))
    pension_employer_rate = Decimal(str(pension_config["employer_rate"]))
    rent_relief_cfg       = rules_jsonb.get("reliefs", {}).get("rent_relief", {})
    nhf_rate              = Decimal(str(rules_jsonb.get("nhf", {}).get("employee_rate", "0.025")))
    health_ins_amount     = Decimal(str(rules_jsonb.get("health_insurance", {}).get("employee_amount", "0")))
    dev_levy_amount       = Decimal(str(rules_jsonb.get("development_levy", {}).get("amount", "0")))
    life_ins_rate         = Decimal(str(rules_jsonb.get("life_insurance", {}).get("employer_rate", "0")))

    # ── Tax bands ─────────────────────────────────────────────────────────────
    tax_rows = db.execute(
        text("""
            SELECT lower_limit, upper_limit, rate
            FROM   tax_band
            WHERE  statutory_rule_id = :sr_id
            ORDER  BY lower_limit
        """),
        {"sr_id": statutory_rule_id},
    ).fetchall()

    tax_bands = [
        {
            "lower_limit": Decimal(str(r[0])) if r[0] is not None else None,
            "upper_limit": Decimal(str(r[1])) if r[1] is not None else None,
            "rate":        Decimal(str(r[2])) if r[2] is not None else None,
        }
        for r in tax_rows
    ]

    # ── Component metadata — read from snapshot (not live table) ─────────────
    comp_rows = db.execute(
        text("""
            SELECT component_code, component_class, calculation_method,
                   execution_priority, is_active, metadata_json
            FROM   component_metadata_snapshot
            WHERE  payroll_run_id = :run_id
            ORDER  BY execution_priority
        """),
        {"run_id": payroll_run_id},
    ).fetchall()

    component_metadata = [
        {
            "component_code":     r[0],
            "component_class":    r[1],
            "calculation_method": r[2],
            "execution_priority": r[3],
            "is_active":          r[4],
            "metadata_json":      r[5],
        }
        for r in comp_rows
    ]

    # ── Workspace component overrides — read from snapshot (D2 workspace scoping) ─
    override_rows = db.execute(
        text("""
            SELECT component_code, overrides_json, proration_strategy, is_active
            FROM   client_component_metadata_snapshot
            WHERE  payroll_run_id = :run_id
              AND  workspace_id   = :wid
        """),
        {"run_id": payroll_run_id, "wid": workspace_id},
    ).fetchall()

    client_overrides = {r[0]: r[1] for r in override_rows}
    ws_proration_col = {r[0]: r[2] for r in override_rows if r[2] is not None}

    # Read is_active from the dedicated snapshot column (r[3]).
    # NULL means the snapshot predates this column — treat as active to preserve
    # existing behaviour for runs created before migration bc1de2f3a4b5.
    disabled_codes = {r[0] for r in override_rows if r[3] is False}
    if disabled_codes:
        component_metadata = [m for m in component_metadata if m["component_code"] not in disabled_codes]

    if "DEVELOPMENT_LEVY" in client_overrides and "monthly_amount" in client_overrides["DEVELOPMENT_LEVY"]:
        dev_levy_amount = Decimal(str(client_overrides["DEVELOPMENT_LEVY"]["monthly_amount"]))
    if "HEALTH_INSURANCE_EMPLOYEE" in client_overrides and "employee_monthly_amount" in client_overrides["HEALTH_INSURANCE_EMPLOYEE"]:
        health_ins_amount = Decimal(str(client_overrides["HEALTH_INSURANCE_EMPLOYEE"]["employee_monthly_amount"]))

    # Build client_meta: global defaults as base, workspace overrides on top
    client_meta = {m["component_code"]: dict(m.get("metadata_json") or {}) for m in component_metadata}
    for code, ws_override in client_overrides.items():
        if code not in client_meta:
            client_meta[code] = {}
        for key, val in ws_override.items():
            if (
                key in client_meta[code]
                and isinstance(client_meta[code][key], dict)
                and isinstance(val, dict)
            ):
                client_meta[code][key] = {**client_meta[code][key], **val}
            else:
                client_meta[code][key] = val

    # Reconcile the dedicated proration_strategy column into calculations_behaviour.
    # The PATCH endpoint writes to client_component_metadata.proration_strategy; the
    # engine reads client_meta[code]["calculations_behaviour"]["proration_strategy"].
    for code, strategy in ws_proration_col.items():
        if code not in client_meta:
            client_meta[code] = {}
        cb = client_meta[code].get("calculations_behaviour")
        if isinstance(cb, dict):
            cb["proration_strategy"] = strategy
        else:
            client_meta[code]["calculations_behaviour"] = {"proration_strategy": strategy}

    # ── Payroll rules ─────────────────────────────────────────────────────────
    # When the run has a rule_set_id (v2 temporal runs) load items from
    # rule_set_item — these are immutable and always match the original run.
    # Fall back to the legacy is_active query for runs created before rule sets.
    if rule_set_id:
        rule_rows = db.execute(
            text("""
                SELECT rsi.rule_set_id, rsi.rule_name, rsi.rule_definition_json, rsi.rule_type
                FROM   rule_set_item rsi
                WHERE  rsi.rule_set_id = :rs_id
            """),
            {"rs_id": rule_set_id},
        ).fetchall()

        payroll_rule_ids = []   # no legacy rule_id for rule_set_item format
        payroll_rules_full = [
            {
                "rule_set_id":          str(r[0]),
                "rule_name":            r[1],
                "rule_definition_json": r[2],
                "rule_type":            r[3],
            }
            for r in rule_rows
        ]
        # rule_set effective_from comes from the snapshot (already in original_snapshot)
        current_rule_set_effective_from = (
            original_snapshot.get("rule_set", {}).get("effective_from")
        )
    else:
        rule_rows = db.execute(
            text("""
                SELECT rule_id, rule_name, rule_definition_json, is_active
                FROM   payroll_rule
                WHERE  is_active    = TRUE
                  AND  workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        payroll_rule_ids = [str(r[0]) for r in rule_rows]
        payroll_rules_full = [
            {
                "rule_id":              str(r[0]),
                "rule_name":            r[1],
                "rule_definition_json": r[2],
                "is_active":            r[3],
            }
            for r in rule_rows
        ]
        current_rule_set_effective_from = None

    # ── Historical rule sets — read from original snapshot (F2 fix) ───────────
    # Retry must never re-query live rule tables for historical rate resolution.
    # The snapshot embedded in the payroll_run row is the authoritative source.
    snapshot_version = original_snapshot.get("snapshot_version", 1)
    if snapshot_version == 2:
        historical_rule_sets = original_snapshot.get("historical_rule_sets", [])
    else:
        historical_rule_sets = []

    expected_hours  = original_snapshot.get("expected_hours")
    expected_days   = original_snapshot.get("expected_days")
    ph_dates_used   = original_snapshot.get("ph_dates_used", [])
    ph_source       = original_snapshot.get("ph_source", "FILE_BASED")

    # rate_code_map must match what the original run route loaded so that
    # ot_multiplier and shift-allowance rules resolve correctly on retry.
    rate_code_map = {row["code"]: row for row in list_rate_codes(workspace_id)}

    context = {
        "tax_bands":                        tax_bands,
        "pension_employee_rate":            pension_employee_rate,
        "pension_employer_rate":            pension_employer_rate,
        "rent_relief_cfg":                  rent_relief_cfg,
        "nhf_rate":                         nhf_rate,
        "health_insurance_employee_amount": health_ins_amount,
        "development_levy_amount":          dev_levy_amount,
        "life_insurance_employer_rate":     life_ins_rate,
        "client_meta":                      client_meta,
        "period":                           period_ctx,
        "payroll_rules":                    payroll_rules_full,
        "historical_rule_sets":             historical_rule_sets,
        "current_rule_set_id":              rule_set_id,
        "current_rule_set_effective_from":  current_rule_set_effective_from,
        "expected_hours":                   expected_hours,
        "expected_days":                    expected_days,
        "ph_dates_used":                    ph_dates_used,
        "ph_source":                        ph_source,
        "rate_code_map":                    rate_code_map,
    }

    return {
        "context":                context,
        "component_metadata":     component_metadata,
        "tax_bands":              tax_bands,
        "statutory_rule_id":      statutory_rule_id,
        "statutory_version":      statutory_version,
        "payroll_rule_ids":       payroll_rule_ids,
        "rules_context_snapshot": original_snapshot or None,
        "period_start":           period_start,
        "period_end":             period_end,
    }


def _insert_result(
    db,
    *,
    payroll_run_id: str,
    employee_id: str,
    status: str,
    payroll_output: dict | None,
    error_message: str | None,
    employee_context: dict | None = None,
    salary_inputs_snapshot: dict | None = None,
) -> None:
    """Insert a single payroll_result row."""

    if status == "SUCCESS" and payroll_output is not None:
        pr            = payroll_output["payroll_result"]
        gross_out     = _sanitize(pr["gross_components_jsonb"])
        ded_out       = _sanitize(pr["deductions_jsonb"])
        snap_out      = _sanitize(pr["calculations_snapshot_json"])
        net_pay       = pr["net_pay"]
        trace_raw     = pr.get("component_trace_jsonb")
        trace_out     = _sanitize(trace_raw) if trace_raw else None
    else:
        gross_out     = {}
        ded_out       = {}
        snap_out      = {}
        net_pay       = 0
        trace_out     = None

    db.execute(
        text("""
            INSERT INTO payroll_result (
                payroll_result_id,
                payroll_run_id,
                employee_id,
                gross_components_jsonb,
                deductions_jsonb,
                net_pay,
                calculations_snapshot_json,
                component_trace_jsonb,
                status,
                error_message,
                per_employee_context_json,
                salary_inputs_snapshot
            )
            VALUES (
                gen_random_uuid(),
                :run_id,
                :eid,
                :gross,
                :deductions,
                :net_pay,
                :snapshot,
                :trace,
                :status,
                :error,
                :per_employee_context_json,
                :salary_inputs_snapshot
            )
        """),
        {
            "run_id":     payroll_run_id,
            "eid":        employee_id,
            "gross":      Json(gross_out),
            "deductions": Json(ded_out),
            "net_pay":    net_pay,
            "snapshot":   Json(snap_out),
            "trace":      Json(trace_out) if trace_out is not None else None,
            "status":     status,
            "error":      error_message,
            "per_employee_context_json": (
                Json(_sanitize(employee_context)) if employee_context else None
            ),
            "salary_inputs_snapshot": Json(salary_inputs_snapshot or {}),
        },
    )


def _delete_failed_row(db, *, payroll_run_id: str, employee_id: str) -> None:
    """Delete the FAILED result for one employee.

    The AND status = 'FAILED' guard ensures this never removes a SUCCESS row
    even if called in an unexpected order.
    """
    db.execute(
        text("""
            DELETE FROM payroll_result
            WHERE payroll_run_id = :run_id
              AND employee_id    = :eid
              AND status         = 'FAILED'
        """),
        {"run_id": payroll_run_id, "eid": employee_id},
    )


# ---------------------------------------------------------------------------
# FULL_RUN retry helper
# ---------------------------------------------------------------------------

def _retry_full_run(db, payroll_run_id: str, workspace_id: str, performed_by: str = "admin@internal") -> dict:
    """FULL_RUN retry is permanently disabled. Use PER_EMPLOYEE retry or open a correction run."""
    raise ValueError(
        "FULL_RUN retry is disabled. Use PER_EMPLOYEE retry or open a new correction run."
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def retry_failed_payroll_employees(payroll_run_id: str, performed_by: str = "admin@internal") -> dict:
    """Retry all FAILED employees in a PARTIAL payroll run.

    Args:
        payroll_run_id: The run to retry.

    Returns:
        {
            "payroll_run_id": str,
            "retried":        int,   # employees attempted
            "success":        int,   # newly successful
            "still_failed":   int,   # still failing after retry
        }

    Raises:
        ValueError: Run not found, is PAID, or is not PARTIAL.
    """

    tracer = ExecutionTracer(payroll_run_id)
    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # Step 1 — Lock the run row for the life of this transaction.
        #
        # FOR UPDATE prevents a concurrent /retry or /run call from
        # modifying the same run while we process employees.
        # -------------------------------------------------------------------
        run_row = db.execute(
            text("""
                SELECT workspace_id, status, retry_strategy
                FROM   payroll_run
                WHERE  payroll_run_id = :run_id
                FOR UPDATE
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        if run_row is None:
            raise ValueError(f"Payroll run not found: {payroll_run_id}")

        workspace_id   = str(run_row[0])
        current_status = run_row[1]
        retry_strategy = run_row[2] or "PER_EMPLOYEE"

        if current_status == "PAID":
            raise ValueError("Cannot retry a PAID payroll run")

        # Explicit guard for approved/locked runs — these are intentionally
        # immutable by business rule, not just incidentally wrong status.
        if current_status in ("APPROVED", "LOCKED"):
            raise ValueError(
                f"Payroll run is {current_status} and cannot be modified. "
                f"Only PARTIAL runs are eligible for retry."
            )

        if current_status != "PARTIAL":
            raise ValueError(
                f"Only PARTIAL runs can be retried. "
                f"Current status: {current_status}"
            )

        # -------------------------------------------------------------------
        # Step 2 — Find FAILED employees (explicit status guard).
        # -------------------------------------------------------------------
        failed_rows = db.execute(
            text("""
                SELECT employee_id
                FROM   payroll_result
                WHERE  payroll_run_id = :run_id
                  AND  status         = 'FAILED'
            """),
            {"run_id": payroll_run_id},
        ).fetchall()

        # Idempotent: nothing to do
        if not failed_rows:
            db.commit()
            return {
                "payroll_run_id": payroll_run_id,
                "retried":        0,
                "success":        0,
                "still_failed":   0,
            }

        failed_employee_ids = [str(r[0]) for r in failed_rows]

        # -------------------------------------------------------------------
        # Step 3 — Build shared execution context (period, statutory rates,
        #          component_metadata, client_meta, payroll_rules) using the
        #          same logic as the original /payroll/run route.
        # -------------------------------------------------------------------
        shared_ctx = _build_shared_context(db, workspace_id, payroll_run_id)

        # Load inputs claimed by the original run so retry reproduces the
        # same input state (OT hours, shift days, absence days, etc.).
        inputs_by_employee = load_inputs_for_run(payroll_run_id)

        # -------------------------------------------------------------------
        # Step 4 — Process each FAILED employee.
        #
        # Pattern (per employee):
        #   a) Attempt calculation  (pure, no DB writes)
        #   b) DELETE old FAILED row  ← after the attempt, never before
        #   c) INSERT new result (SUCCESS or FAILED)
        #
        # Keeping the old row alive until step (b) ensures the DB is never
        # left without a result row for this employee, even if the process
        # crashes between steps (a) and (c).
        # -------------------------------------------------------------------
        retried      = 0
        success_count = 0
        still_failed  = 0

        for employee_id in failed_employee_ids:

            # D1: structural fields from employee_contract_snapshot; salary amounts
            # from live salary_definition joined on the frozen salary_definition_id.
            # D6: hard-fail (raise) if no snapshot row — do not silently skip.
            snap_row = db.execute(
                text("""
                    SELECT ecs.salary_definition_id,
                           ecs.contract_start, ecs.contract_end,
                           ecs.shift_type, ecs.grade_id, ecs.grade_jsonb,
                           sd.components_jsonb
                    FROM   employee_contract_snapshot ecs
                    JOIN   salary_definition sd
                           ON sd.salary_definition_id = ecs.salary_definition_id
                    WHERE  ecs.payroll_run_id = :run_id
                      AND  ecs.employee_id    = :eid
                """),
                {"run_id": payroll_run_id, "eid": employee_id},
            ).fetchone()

            if snap_row is None:
                raise ValueError(
                    f"No snapshot row for employee {employee_id} on run {payroll_run_id} "
                    "— data integrity failure (D6)"
                )

            # ----------------------------------------------------------------
            # a) Attempt calculation — pure, no DB side-effects.
            # ----------------------------------------------------------------

            # D4: read frozen employee context BEFORE deleting the FAILED row.
            # Preserves eligibility flags (e.g. is_union_member) from original run.
            # Rows predating the migration yield {} — eligibility gates suppressed.
            frozen_ctx = get_employee_context_from_result(db, payroll_run_id, employee_id)

            _shift_type    = snap_row[3]
            _grade_id      = str(snap_row[4]) if snap_row[4] is not None else None
            _grade         = snap_row[5]   # grade_jsonb frozen at run time
            _components_jsonb = snap_row[6]  # live components from salary_definition (D1)

            _sal_components, _salary_basis = derive_salary_components(_components_jsonb, _grade)
            components    = [{"code": k, "amount": v} for k, v in _sal_components.items()]
            contract_start = snap_row[1].isoformat() if snap_row[1] else None
            contract_end   = snap_row[2].isoformat() if snap_row[2] else None
            emp_context    = {**shared_ctx["context"], "shift_type": _shift_type, "salary_basis": _salary_basis}

            # D4: salary_inputs_snapshot for audit trail (detects live vs original divergence)
            sal_snap = {c["code"]: str(c["amount"]) for c in components}

            try:
                calc_result = execute_single_employee_payroll(
                    payroll_run_id          = payroll_run_id,
                    employee_id             = employee_id,
                    components              = components,
                    tax_bands               = shared_ctx["tax_bands"],
                    statutory_rule_id       = shared_ctx["statutory_rule_id"],
                    statutory_version       = shared_ctx["statutory_version"],
                    payroll_rule_ids        = shared_ctx["payroll_rule_ids"],
                    performed_by            = "admin@internal",
                    component_metadata      = shared_ctx["component_metadata"],
                    context                 = emp_context,
                    contract_start          = contract_start,
                    contract_end            = contract_end,
                    rules_context_snapshot  = shared_ctx["rules_context_snapshot"],
                    inputs                  = inputs_by_employee.get(employee_id, {}),
                    employee_context        = frozen_ctx or None,
                    tracer                  = tracer,
                )
                calc_error = None
            except Exception as exc:
                calc_result = None
                calc_error  = str(exc)

            # ----------------------------------------------------------------
            # b) DELETE the old FAILED row — only after the attempt.
            #    status = 'FAILED' guard prevents touching SUCCESS rows.
            # ----------------------------------------------------------------
            _delete_failed_row(db, payroll_run_id=payroll_run_id, employee_id=employee_id)

            # ----------------------------------------------------------------
            # c) INSERT new result row (sal_snap written for D4 audit trail).
            # ----------------------------------------------------------------
            if calc_error is None:
                _insert_result(
                    db,
                    payroll_run_id          = payroll_run_id,
                    employee_id             = employee_id,
                    status                  = "SUCCESS",
                    payroll_output          = calc_result,
                    error_message           = None,
                    employee_context        = frozen_ctx or None,
                    salary_inputs_snapshot  = sal_snap,
                )
                success_count += 1
            else:
                _insert_result(
                    db,
                    payroll_run_id          = payroll_run_id,
                    employee_id             = employee_id,
                    status                  = "FAILED",
                    payroll_output          = None,
                    error_message           = calc_error,
                    employee_context        = frozen_ctx or None,
                    salary_inputs_snapshot  = sal_snap,
                )
                still_failed += 1

            retried += 1

        # -------------------------------------------------------------------
        # Step 5 — Recompute run status from the DB (not from local counters).
        #
        # This is authoritative even if earlier state was inconsistent.
        # -------------------------------------------------------------------
        remaining_failed = db.execute(
            text("""
                SELECT COUNT(*)
                FROM   payroll_result
                WHERE  payroll_run_id = :run_id
                  AND  status         = 'FAILED'
            """),
            {"run_id": payroll_run_id},
        ).scalar()

        new_run_status = "CALCULATED" if remaining_failed == 0 else "PARTIAL"

        # Recompute run totals from SUCCESS rows (authoritative DB aggregate).
        # FAILED rows contribute nothing; COALESCE guards against empty result set.
        totals_row = db.execute(
            text("""
                SELECT
                    COALESCE(SUM(net_pay), 0),
                    COALESCE(SUM((
                        SELECT SUM((val->>'amount')::numeric)
                        FROM   jsonb_each(gross_components_jsonb) AS j(key, val)
                    )), 0),
                    COALESCE(SUM((
                        SELECT SUM(val::text::numeric)
                        FROM   jsonb_each(deductions_jsonb) AS j(key, val)
                    )), 0),
                    COALESCE(SUM((deductions_jsonb->>'PAYE')::numeric), 0)
                FROM payroll_result
                WHERE payroll_run_id = :run_id
                  AND status         = 'SUCCESS'
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        paye_total = totals_row[3]

        # trg_payroll_run_state_machine allows PARTIAL → CALCULATED
        # (only DRAFT / PROCESSING / COMPLETED / PAID transitions are enforced)
        db.execute(
            text("""
                UPDATE payroll_run
                SET    status          = :status,
                       total_net_pay   = :net,
                       total_gross_pay = :gross,
                       total_deduction = :ded,
                       total_tax       = :tax
                WHERE  payroll_run_id  = :run_id
            """),
            {
                "run_id": payroll_run_id,
                "status": new_run_status,
                "net":    totals_row[0],
                "gross":  totals_row[1],
                "ded":    totals_row[2],
                "tax":    paye_total,
            },
        )

        db.commit()

        # Write audit trail after successful commit — same pattern as approval service
        save_audit_log(workspace_id, build_transition_audit(
            payroll_run_id=payroll_run_id,
            old_status=PayrollRunStatus.PARTIAL,
            new_status=PayrollRunStatus(new_run_status),
            performed_by=performed_by,
        ))
        save_event(build_transition_event(
            payroll_run_id=payroll_run_id,
            old_status=PayrollRunStatus.PARTIAL,
            new_status=PayrollRunStatus(new_run_status),
        ))

        return {
            "payroll_run_id": payroll_run_id,
            "retried":        retried,
            "success":        success_count,
            "still_failed":   still_failed,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
