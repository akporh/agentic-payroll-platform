"""
Payroll API Routes.

Exposes endpoints for triggering payroll runs.
"""

import calendar
import csv as _csv
import io
import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.exc import InternalError as SQLInternalError
from backend.domain.payroll.period_context import build_period_context
from backend.domain.rules.snapshot import build_rules_context_snapshot
from backend.infra.db.session import SessionLocal
from backend.application.payroll_run_service import execute_and_persist
from backend.application.payroll_retry_service import retry_failed_payroll_employees
from backend.application.payroll_approval_service import approve_payroll_run, lock_payroll_run, mark_payroll_run_paid
from backend.application.reconciliation_service import reconcile_payroll_run, get_reconciliation_status, resolve_reconciliation
from backend.infra.repositories.execution_trace_repo import get_trace_steps, get_legacy_executor_stats
from backend.infra.repositories.payroll_input_repo import link_inputs_to_run, load_unclaimed_inputs_by_employee
from backend.infra.repositories.workspace_config_repo import get_workspace_payroll_config
from backend.infra.repositories.public_holiday_repo import get_effective_ph_list
from backend.infra.repositories.rate_code_repo import list_rate_codes

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
    run_type           = payload.get("run_type", "REGULAR").upper()
    # Optional rule_set_id override for ADJUSTMENT runs targeting a specific rule set
    override_rule_set_id = payload.get("rule_set_id")

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")

    if period_type_raw and period_type_raw.upper() == "CUSTOM" and not working_days_input:
        raise HTTPException(
            status_code=422,
            detail="working_days is required when period_type is CUSTOM",
        )

    # ── Compute statutory_effective_date early (needed for temporal rule queries) ─
    # Use period_end when provided; otherwise last day of the current month.
    if period_end:
        statutory_effective_date = (
            date.fromisoformat(period_end) if isinstance(period_end, str) else period_end
        )
    else:
        _today = date.today()
        statutory_effective_date = _today.replace(
            day=calendar.monthrange(_today.year, _today.month)[1]
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
          AND (sd.effective_from IS NULL OR sd.effective_from <= :period_end_date)
          AND (sd.effective_to   IS NULL OR sd.effective_to   >= :period_start_date)
    """), {
        "workspace_id": workspace_id,
        "period_end_date":   period_end   or str(statutory_effective_date),
        "period_start_date": period_start or str(statutory_effective_date.replace(day=1)),
    }).fetchall()

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

    # ── A1-A2: Statutory rule — temporal selection using statutory_effective_date ─
    # SELECT the rule whose effective_from is <= statutory_effective_date,
    # breaking ties by most recently published (effective_from DESC, version DESC).
    stat_row = db.execute(text("""
        SELECT sr.statutory_rule_id, sr.version, sr.rules_jsonb, sr.effective_from
        FROM statutory_rule sr
        JOIN workspace w ON sr.country_code = w.country_code
        WHERE w.workspace_id = :workspace_id
          AND sr.effective_from <= :as_of_date
        ORDER BY sr.effective_from DESC, sr.version DESC
        LIMIT 1
    """), {"workspace_id": workspace_id, "as_of_date": statutory_effective_date}).fetchone()

    if not stat_row:
        db.close()
        raise HTTPException(status_code=400, detail="No statutory rule found for this workspace's country")

    statutory_rule_id      = str(stat_row[0])
    statutory_version      = stat_row[1]
    rules_jsonb            = stat_row[2] or {}
    stat_effective_from    = str(stat_row[3]) if stat_row[3] else None

    # Extract pension rates from statutory rule — required, no hardcoded fallback.
    pension_config = rules_jsonb.get("pension")
    if not pension_config or "employee_rate" not in pension_config or "employer_rate" not in pension_config:
        db.close()
        raise HTTPException(
            status_code=500,
            detail="Statutory rule is missing pension rates (employee_rate / employer_rate). Run the pension rates migration.",
        )
    pension_employee_rate = Decimal(str(pension_config["employee_rate"]))
    pension_employer_rate = Decimal(str(pension_config["employer_rate"]))

    # Extract rent relief config (used by sequential executor for PAYE annualisation)
    rent_relief_cfg = rules_jsonb.get("reliefs", {}).get("rent_relief", {})

    # Extract workspace-level statutory component rates/amounts
    nhf_rate                         = Decimal(str(rules_jsonb.get("nhf", {}).get("employee_rate", "0.025")))
    health_insurance_employee_amount = Decimal(str(rules_jsonb.get("health_insurance", {}).get("employee_amount", "0")))
    development_levy_amount          = Decimal(str(rules_jsonb.get("development_levy", {}).get("amount", "0")))
    life_insurance_employer_rate     = Decimal(str(rules_jsonb.get("life_insurance", {}).get("employer_rate", "0")))

    # --- Load Tax Bands (scoped to the selected statutory rule) ---
    tax_rows = db.execute(text("""
        SELECT lower_limit, upper_limit, rate
        FROM tax_band
        WHERE statutory_rule_id = :sr_id
        ORDER BY lower_limit
    """), {"sr_id": statutory_rule_id}).fetchall()

    tax_bands = [
        {
            "lower_limit": Decimal(str(r[0])) if r[0] is not None else None,
            "upper_limit": Decimal(str(r[1])) if r[1] is not None else None,
            "rate":        Decimal(str(r[2])) if r[2] is not None else None,
        }
        for r in tax_rows
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

    # Load public holidays (national + workspace overrides) for the period.
    ph_rows = db.execute(text("""
        SELECT holiday_date FROM national_public_holiday
        WHERE country_code = :cc
          AND holiday_date BETWEEN :start AND :end
        UNION
        SELECT holiday_date FROM workspace_public_holiday
        WHERE workspace_id = :wid
          AND holiday_date BETWEEN :start AND :end
    """), {
        "cc":    country_code,
        "wid":   workspace_id,
        "start": period_start or date.today().replace(day=1),
        "end":   period_end   or date.today(),
    }).fetchall()
    public_holiday_dates = {r[0] for r in ph_rows}

    # Build PeriodContext now that we have the workspace's configured frequency.
    # Priority: explicit API field > workspace pay_cycle.frequency > infer from dates.
    try:
        period_ctx = build_period_context(
            period_start=period_start,
            period_end=period_end,
            period_type=period_type_raw or pay_cycle_frequency,
            working_days_override=working_days_input,
            public_holiday_dates=public_holiday_dates,
        )
    except ValueError as exc:
        db.close()
        raise HTTPException(status_code=422, detail=str(exc))

    # ── A3-A4: Rule set resolution ────────────────────────────────────────────
    # Find the rule set effective on statutory_effective_date.
    # ADJUSTMENT runs may supply a specific rule_set_id override.
    # Falls back to legacy is_active query when no rule set exists yet.
    if override_rule_set_id:
        rs_row = db.execute(text("""
            SELECT rs.rule_set_id, rs.effective_from
            FROM rule_set rs
            WHERE rs.rule_set_id  = :rs_id
              AND rs.workspace_id = :wid
        """), {"rs_id": override_rule_set_id, "wid": workspace_id}).fetchone()
    else:
        rs_row = db.execute(text("""
            SELECT rs.rule_set_id, rs.effective_from
            FROM rule_set rs
            WHERE rs.workspace_id  = :wid
              AND rs.effective_from <= :as_of_date
            ORDER BY rs.effective_from DESC, rs.created_at DESC
            LIMIT 1
        """), {"wid": workspace_id, "as_of_date": statutory_effective_date}).fetchone()

    if rs_row:
        rule_set_id              = str(rs_row[0])
        rule_set_effective_from  = str(rs_row[1])

        rule_item_rows = db.execute(text("""
            SELECT rsi.rule_set_id, rsi.rule_name, rsi.rule_definition_json, rsi.rule_type
            FROM rule_set_item rsi
            WHERE rsi.rule_set_id = :rs_id
        """), {"rs_id": rule_set_id}).fetchall()

        payroll_rule_ids   = []     # no legacy rule_id for rule_set_item format
        payroll_rules_full = [
            {
                "rule_set_id":          str(r[0]),
                "rule_name":            r[1],
                "rule_definition_json": r[2],
                "rule_type":            r[3],
            }
            for r in rule_item_rows
        ]
        rule_set_items_for_snapshot = [
            {"rule_name": r[1], "rule_definition_json": r[2], "rule_type": r[3]}
            for r in rule_item_rows
        ]
    else:
        # Legacy path — no rule sets published yet for this workspace
        rule_set_id             = None
        rule_set_effective_from = None
        rule_set_items_for_snapshot = []

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

    # ── Load unclaimed inputs (own session — payroll_run row doesn't exist yet) ─
    inputs_by_employee = load_unclaimed_inputs_by_employee(
        workspace_id,
        period_start=period_ctx.period_start,
        period_end=period_ctx.period_end,
    )
    for emp in employees:
        emp["inputs"] = inputs_by_employee.get(emp["employee_id"], {})

    # ── A5: Cross-period prefetch — collect distinct historical rule sets ──────
    # Identify inputs whose reference_date falls outside the current period.
    # For each distinct historical month, resolve and cache the rule set that
    # was in effect, then compute its PeriodContext (for correct working_days).
    cross_period_ref_dates: set = set()
    for emp in employees:
        for _data in emp.get("inputs", {}).values():
            if not isinstance(_data, list):
                continue
            ref_dt = _data.get("reference_date")
            if ref_dt and (
                ref_dt < period_ctx.period_start or ref_dt > period_ctx.period_end
            ):
                cross_period_ref_dates.add(ref_dt)

    historical_rule_sets_list: list[dict] = []
    historical_period_contexts: dict = {}

    if cross_period_ref_dates:
        hist_db = SessionLocal()
        try:
            seen_rs_ids: set = {rule_set_id} if rule_set_id else set()
            hist_rs_map: dict = {}  # {rule_set_id: {id, effective_from, items}}

            for ref_dt in sorted(cross_period_ref_dates):
                hist_row = hist_db.execute(text("""
                    SELECT rs.rule_set_id, rs.effective_from
                    FROM rule_set rs
                    WHERE rs.workspace_id  = :wid
                      AND rs.effective_from <= :as_of_date
                    ORDER BY rs.effective_from DESC, rs.created_at DESC
                    LIMIT 1
                """), {"wid": workspace_id, "as_of_date": ref_dt}).fetchone()

                if hist_row:
                    h_rs_id = str(hist_row[0])
                    if h_rs_id not in seen_rs_ids:
                        seen_rs_ids.add(h_rs_id)
                        h_items = hist_db.execute(text("""
                            SELECT rule_name, rule_definition_json, rule_type
                            FROM rule_set_item
                            WHERE rule_set_id = :rs_id
                        """), {"rs_id": h_rs_id}).fetchall()

                        hist_rs_map[h_rs_id] = {
                            "id":            h_rs_id,
                            "effective_from": str(hist_row[1]),
                            "items": [
                                {
                                    "rule_name":            r[0],
                                    "rule_definition_json": r[1],
                                    "rule_type":            r[2],
                                }
                                for r in h_items
                            ],
                        }

                # Build historical PeriodContext for this month (F5 fix: correct working_days)
                key = (ref_dt.year, ref_dt.month)
                if key not in historical_period_contexts:
                    h_start = ref_dt.replace(day=1)
                    h_end   = ref_dt.replace(day=calendar.monthrange(ref_dt.year, ref_dt.month)[1])
                    h_ctx   = build_period_context(h_start, h_end, public_holiday_dates=public_holiday_dates)
                    historical_period_contexts[key] = {
                        "working_days":  h_ctx.working_days,
                        "calendar_days": h_ctx.calendar_days,
                    }

            historical_rule_sets_list = list(hist_rs_map.values())
        finally:
            hist_db.close()

    # ── Build rules context snapshot ──────────────────────────────────────────
    # v2 (full content) when a rule set is resolved; v1 (ID-only) for legacy.
    if rule_set_id:
        rules_ctx_snapshot = build_rules_context_snapshot(
            statutory_rule_id         = statutory_rule_id,
            statutory_version         = statutory_version,
            statutory_effective_from  = stat_effective_from,
            statutory_rules_jsonb     = rules_jsonb,
            statutory_tax_bands       = tax_bands,
            rule_set_id               = rule_set_id,
            rule_set_effective_from   = rule_set_effective_from,
            rule_set_items            = rule_set_items_for_snapshot,
            historical_rule_sets      = historical_rule_sets_list,
        )
    else:
        rules_ctx_snapshot = build_rules_context_snapshot(
            statutory_rule_id, statutory_version, payroll_rule_ids
        )

    # ── Public Holiday & rate-code context (C1 — PH-2, C4 — PH-8) ──────────────
    workspace_payroll_config = get_workspace_payroll_config(workspace_id)
    if workspace_payroll_config["ph_mode"] == "AUTOMATIC":
        ph_list = get_effective_ph_list(
            workspace_id, country_code,
            str(period_ctx.period_start), str(period_ctx.period_end),
        )
        ph_weekday_dates = [
            ph["date"] for ph in ph_list
            if ph["date"].weekday() < 5  # Mon–Fri only
        ]
        expected_working_days = period_ctx.working_days - len(ph_weekday_dates)
        ph_source = "AUTOMATIC"
    else:
        ph_weekday_dates = []
        expected_working_days = period_ctx.working_days
        ph_source = "FILE_BASED"

    expected_hours = expected_working_days * 8
    expected_days  = expected_working_days
    ph_dates_used  = [str(d) for d in ph_weekday_dates]
    rate_code_map  = {row["code"]: row for row in list_rate_codes(workspace_id)}

    # ── Extend rules snapshot with PH context (C3 — PH-9) ───────────────────
    rules_ctx_snapshot.update({
        "expected_hours": expected_hours,
        "expected_days":  expected_days,
        "ph_dates_used":  ph_dates_used,
        "ph_source":      ph_source,
    })

    # ── D1/D2: PH validation warnings (PH-10, PH-11) ─────────────────────────
    _ph_pre_warnings: list[tuple[str, str]] = []

    # D2 — PH-11: AUTOMATIC mode empty-calendar pre-flight
    if workspace_payroll_config["ph_mode"] == "AUTOMATIC" and len(ph_list) == 0:
        _ph_pre_warnings.append((
            "PH_CALENDAR_EMPTY",
            f"No public holidays found in the calendar for {country_code} "
            f"period {period_ctx.period_start}–{period_ctx.period_end}. "
            "expected_days will equal working_days.",
        ))

    # D1 — PH-10: Cross-check calendar national count vs. file-submitted PH entries.
    # Applies in all ph_mode configurations — fetch calendar when FILE_BASED.
    if workspace_payroll_config["ph_mode"] != "AUTOMATIC":
        _calendar_ph_list = get_effective_ph_list(
            workspace_id, country_code,
            str(period_ctx.period_start), str(period_ctx.period_end),
        )
    else:
        _calendar_ph_list = ph_list  # already fetched above

    # Cross-check only makes sense in FILE_BASED mode — in AUTOMATIC mode there is
    # no input file for PH data so comparing file count vs. calendar is meaningless.
    if workspace_payroll_config["ph_mode"] != "AUTOMATIC":
        _calendar_ph_count = sum(1 for d in _calendar_ph_list if d["source"] == "NATIONAL")
        _file_ph_count = sum(
            len(emp.get("inputs", {}).get("ph_hours_worked", []))
            for emp in employees
        )

        if _file_ph_count > _calendar_ph_count:
            _ph_pre_warnings.append((
                "PH_COUNT_MISMATCH_EXCESS",
                (
                    f"File contains {_file_ph_count} PH entries but calendar shows "
                    f"{_calendar_ph_count} for this period. Review whether the extra "
                    "entry is a contractual rate day that should be handled separately."
                ),
            ))
        elif _file_ph_count < _calendar_ph_count:
            _ph_pre_warnings.append((
                "PH_COUNT_MISMATCH_DEFICIT",
                (
                    f"Calendar shows {_calendar_ph_count} PHs for this period but only "
                    f"{_file_ph_count} appear in the input file. A public holiday may be "
                    "missing — review to avoid underpayment."
                ),
            ))

    # Duplicate ph_hours_worked entries for the same employee on the same date
    for _emp in employees:
        _emp_id = _emp["employee_id"]
        _ph_events = _emp.get("inputs", {}).get("ph_hours_worked", [])
        _seen_dates: set = set()
        for _event in _ph_events:
            if not isinstance(_event, dict):
                continue
            _ref = _event.get("reference_date")
            if _ref:
                if _ref in _seen_dates:
                    _ph_pre_warnings.append((
                        "PH_DUPLICATE_IN_FILE",
                        f"Employee {_emp_id} has duplicate ph_hours_worked entries "
                        f"for {_ref}. This may cause double-counting.",
                    ))
                    break  # one warning per employee
                _seen_dates.add(_ref)

    # ph_hours_worked entries with reference_date outside the pay period
    for _emp in employees:
        _emp_id = _emp["employee_id"]
        _ph_events = _emp.get("inputs", {}).get("ph_hours_worked", [])
        for _event in _ph_events:
            if not isinstance(_event, dict):
                continue
            _ref = _event.get("reference_date")
            if _ref and (
                _ref < period_ctx.period_start or _ref > period_ctx.period_end
            ):
                _ph_pre_warnings.append((
                    "PH_OUT_OF_PERIOD",
                    f"Input row has reference_date {_ref} which falls outside "
                    f"the period {period_ctx.period_start}–{period_ctx.period_end}. "
                    "Verify this is not a data entry error.",
                ))

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
        # ── Temporal context — consumed by rule_evaluator for cross-period inputs ─
        "historical_rule_sets":             historical_rule_sets_list,
        "historical_period_contexts":       historical_period_contexts,
        "current_rule_set_id":              rule_set_id,
        "current_rule_set_effective_from":  rule_set_effective_from,
        # ── PH & OT context (C1 — PH-2, C4 — PH-8) ─────────────────────────
        "expected_hours":                   expected_hours,
        "expected_days":                    expected_days,
        "ph_dates_used":                    ph_dates_used,
        "ph_source":                        ph_source,
        "workspace_ph_config":              workspace_payroll_config,
        "rate_code_map":                    rate_code_map,
    }

    try:
        result = execute_and_persist(
            payroll_run_id           = payroll_run_id,
            workspace_id             = workspace_id,
            employees                = employees,
            tax_bands                = tax_bands,
            statutory_rule_id        = statutory_rule_id,
            statutory_version        = statutory_version,
            payroll_rule_ids         = payroll_rule_ids,
            performed_by             = "admin@internal",
            execution_mode           = "isolated",
            idempotency_key          = idempotency_key,
            period_start             = period_start,
            period_end               = period_end,
            pay_cycle_definition     = pay_cycle_definition,
            retry_strategy           = retry_strategy,
            component_metadata       = component_metadata or None,
            context                  = context,
            rules_context_snapshot   = rules_ctx_snapshot,
            rule_set_id              = rule_set_id,
            statutory_effective_date = str(statutory_effective_date),
            run_type                 = run_type,
            pre_warnings             = _ph_pre_warnings or None,
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
                    pr.status,
                    pr.component_trace_jsonb
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
                "employee_id":       str(r[0]),
                "employee_name":     r[1] or "",
                "employee_number":   r[2] or "",
                "gross_pay":         float(gross_total) if status == "SUCCESS" else None,
                "total_deductions":  float(deductions_total) if status == "SUCCESS" else None,
                "net_pay":           float(r[3]) if r[3] is not None else None,
                "status":            status,
                "component_trace":   r[7] or [],
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
def retry_payroll_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
    """
    Retry all FAILED employees in a PARTIAL payroll run.

    Only employees with status='FAILED' are reprocessed. Employees that
    already succeeded are never touched. If the corrected data now passes
    calculation the result is updated to SUCCESS and the run transitions
    to CALCULATED once all failures are resolved.

    Returns 400 if the run does not exist, is PAID, or is not PARTIAL.
    """
    try:
        result = retry_failed_payroll_employees(run_id, performed_by=performed_by)
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
def approve_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
    """
    Approve a CALCULATED payroll run (CALCULATED → APPROVED).

    Once approved the run can only be locked — it cannot be retried or
    recalculated.  Returns 400 if the run is not in CALCULATED state.
    """
    try:
        result = approve_payroll_run(run_id, performed_by=performed_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status":     "success",
        "run_id":     result["payroll_run_id"],
        "run_status": result["status"],
    }


@router.post("/payroll/run/{run_id}/lock")
def lock_run(run_id: str, performed_by: str = Header(default="admin@internal", alias="X-Performed-By")):
    """
    Lock an APPROVED payroll run (APPROVED → LOCKED).

    A LOCKED run is permanently immutable.  Returns 400 if the run is not
    in APPROVED state.
    """
    try:
        result = lock_payroll_run(run_id, performed_by=performed_by)
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

    Body (optional): ``{ "actor_id": "<identity>" }``
    """
    actor_id = payload.get("actor_id", "system@internal")
    try:
        result = mark_payroll_run_paid(run_id, performed_by=actor_id)
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
        "notes":          record.get("notes"),
        "resolved_by":    record.get("resolved_by"),
        "resolved_at":    record.get("resolved_at"),
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


@router.patch("/{workspace_id}/payroll/runs/{run_id}/reconciliation")
def resolve_reconciliation_scoped(workspace_id: str, run_id: str, payload: dict):
    """Mark a MISMATCH reconciliation as resolved (workspace-scoped).

    Body: { "notes": str, "resolved_by": str }
    """
    notes = payload.get("notes", "").strip()
    resolved_by = payload.get("resolved_by", "").strip()
    if not notes:
        raise HTTPException(status_code=400, detail="notes is required")
    if not resolved_by:
        raise HTTPException(status_code=400, detail="resolved_by is required")
    try:
        record = resolve_reconciliation(run_id, notes=notes, resolved_by=resolved_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _to_reconciliation_record(record)


@router.get("/{workspace_id}/payroll/runs/{run_id}/timeline")
def get_run_timeline(workspace_id: str, run_id: str):
    """Return all execution trace steps for a payroll run, ordered by time."""
    steps = get_trace_steps(run_id)
    return steps


@router.get("/{workspace_id}/payroll/ops/legacy-executor-stats")
def legacy_executor_stats(workspace_id: str):
    """Return aggregate stats on legacy executor fallback usage.

    Tracks how often the deprecated legacy calculation path is invoked
    (when component_metadata is absent). Useful for monitoring migration
    progress away from the legacy executor.

    Returns:
        total_runs:          total runs with at least one trace step
        runs_with_legacy:    runs where legacy fallback fired at least once
        pct_runs_affected:   percentage of runs that hit the legacy path
        total_legacy_events: total employee-level fallback events across all runs
        by_run:              per-run breakdown (only runs with legacy events)
    """
    return get_legacy_executor_stats()


@router.get("/{workspace_id}/payroll/runs/{run_id}/audit")
def get_run_audit_log(workspace_id: str, run_id: str):
    """Return the audit log entries for a payroll run, ordered by time."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT entity_type, action, old_value_jsonb, new_value_jsonb,
                       performed_by, performed_at
                FROM   audit_log
                WHERE  workspace_id = :wid
                  AND  entity_id    = :eid::uuid
                ORDER  BY performed_at ASC
            """),
            {"wid": workspace_id, "eid": run_id},
        ).fetchall()
    finally:
        db.close()

    return [
        {
            "entity_type":  r[0],
            "action":       r[1],
            "old_value":    r[2],
            "new_value":    r[3],
            "performed_by": r[4],
            "performed_at": r[5].isoformat() if r[5] else None,
        }
        for r in rows
    ]


# ── H1/H2/H3 — CSV Export helpers ────────────────────────────────────────────

_EXPORT_RESULT_SQL = text("""
    SELECT
        e.employee_number,
        e.full_name,
        e.personal_details_encrypted,
        pr.net_pay,
        pr.gross_components_jsonb,
        pr.deductions_jsonb,
        pr.component_trace_jsonb,
        r.period_start
    FROM payroll_result pr
    JOIN employee e ON e.employee_id = pr.employee_id
    JOIN payroll_run r ON r.payroll_run_id = pr.payroll_run_id
    WHERE pr.payroll_run_id = :run_id
      AND pr.status = 'SUCCESS'
    ORDER BY e.full_name
""")


def _guard_locked_or_paid(db, workspace_id: str, run_id: str) -> None:
    """Raise HTTPException if run is not found for workspace or not LOCKED/PAID."""
    row = db.execute(
        text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid AND workspace_id = :wid"),
        {"rid": run_id, "wid": workspace_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    if row[0] not in ("LOCKED", "PAID"):
        raise HTTPException(
            status_code=409,
            detail=f"Export requires LOCKED or PAID status. Current status: {row[0]}",
        )


def _streaming_csv(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── H1 — Bank Upload CSV ──────────────────────────────────────────────────────

@router.get("/{workspace_id}/payroll/runs/{run_id}/exports/bank-upload")
def export_bank_upload(workspace_id: str, run_id: str):
    """Download net pay bank upload CSV (LOCKED or PAID runs only).

    Columns: employee_number, employee_name, bank_name, account_number, net_pay
    """
    db = SessionLocal()
    try:
        _guard_locked_or_paid(db, workspace_id, run_id)
        rows = db.execute(_EXPORT_RESULT_SQL, {"run_id": run_id}).fetchall()
    finally:
        db.close()

    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow(["employee_number", "employee_name", "bank_name", "account_number", "net_pay"])
    for r in rows:
        biodata = r[2] or {}
        writer.writerow([
            r[0] or "",
            r[1] or "",
            biodata.get("BANK", ""),
            biodata.get("ACCOUNT_NUMBER", ""),
            f"{float(r[3]):.2f}" if r[3] is not None else "0.00",
        ])

    return _streaming_csv(buf.getvalue(), f"bank_upload_{run_id[:8]}.csv")


# ── H2 — PAYE Remittance CSV ─────────────────────────────────────────────────

@router.get("/{workspace_id}/payroll/runs/{run_id}/exports/paye")
def export_paye_remittance(workspace_id: str, run_id: str):
    """Download PAYE remittance CSV (LOCKED or PAID runs only).

    Columns: employee_number, employee_name, tin, gross_pay, paye_withheld, period
    """
    db = SessionLocal()
    try:
        _guard_locked_or_paid(db, workspace_id, run_id)
        rows = db.execute(_EXPORT_RESULT_SQL, {"run_id": run_id}).fetchall()
    finally:
        db.close()

    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow(["employee_number", "employee_name", "tin", "gross_pay", "paye_withheld", "period"])
    for r in rows:
        biodata = r[2] or {}
        gross_components = r[4] or {}
        deductions = r[5] or {}
        gross_pay = sum(
            float(v.get("amount", v) if isinstance(v, dict) else v)
            for v in gross_components.values()
        )
        paye = float(deductions.get("PAYE", 0))
        period = r[7].strftime("%Y-%m") if r[7] else ""
        writer.writerow([
            r[0] or "",
            r[1] or "",
            biodata.get("TIN", ""),
            f"{gross_pay:.2f}",
            f"{paye:.2f}",
            period,
        ])

    return _streaming_csv(buf.getvalue(), f"paye_remittance_{run_id[:8]}.csv")


# ── H3 — Pension Contribution CSV ────────────────────────────────────────────

@router.get("/{workspace_id}/payroll/runs/{run_id}/exports/pension")
def export_pension_contribution(workspace_id: str, run_id: str):
    """Download pension contribution CSV (LOCKED or PAID runs only).

    Columns: employee_number, employee_name, rsa_pin, basic_pay,
             pension_base, employee_contribution, employer_contribution, period
    """
    db = SessionLocal()
    try:
        _guard_locked_or_paid(db, workspace_id, run_id)
        rows = db.execute(_EXPORT_RESULT_SQL, {"run_id": run_id}).fetchall()
    finally:
        db.close()

    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow([
        "employee_number", "employee_name", "rsa_pin",
        "basic_pay", "pension_base",
        "employee_contribution", "employer_contribution", "period",
    ])
    for r in rows:
        biodata = r[2] or {}
        gross_components = r[4] or {}
        deductions = r[5] or {}
        trace = r[6] or []

        basic_amount = gross_components.get("BASIC", {})
        basic_pay = float(
            basic_amount.get("amount", basic_amount)
            if isinstance(basic_amount, dict) else basic_amount
        ) if basic_amount else 0.0

        emp_contrib = float(deductions.get("PENSION_EMPLOYEE", 0))

        # Employer contribution is an employer cost (not a statutory deduction) —
        # read from the component trace where it is always recorded.
        er_contrib = 0.0
        for entry in (trace if isinstance(trace, list) else []):
            if isinstance(entry, dict) and entry.get("component") == "PENSION_EMPLOYER":
                try:
                    er_contrib = float(entry.get("result", 0))
                except (ValueError, TypeError):
                    pass
                break

        # pension_base ≈ BASIC (standard Nigerian statutory base)
        pension_base = basic_pay
        period = r[7].strftime("%Y-%m") if r[7] else ""

        writer.writerow([
            r[0] or "",
            r[1] or "",
            biodata.get("RSA", ""),
            f"{basic_pay:.2f}",
            f"{pension_base:.2f}",
            f"{emp_contrib:.2f}",
            f"{er_contrib:.2f}",
            period,
        ])

    return _streaming_csv(buf.getvalue(), f"pension_contribution_{run_id[:8]}.csv")
