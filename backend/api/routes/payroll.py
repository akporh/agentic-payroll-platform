"""
Payroll API Routes.

Exposes endpoints for triggering payroll runs.
"""

import uuid
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InternalError as SQLInternalError
from backend.infra.db.session import SessionLocal
from backend.application.payroll_run_service import execute_and_persist
from backend.application.payroll_retry_service import retry_failed_payroll_employees
from backend.application.payroll_approval_service import approve_payroll_run, lock_payroll_run, mark_payroll_run_paid
from backend.application.reconciliation_service import reconcile_payroll_run, get_reconciliation_status

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

    workspace_id = payload.get("workspace_id")
    period_start  = payload.get("period_start")
    period_end    = payload.get("period_end")

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")

    db = SessionLocal()

    # --- Verify workspace exists ---
    workspace = db.execute(
        text("SELECT workspace_id FROM workspace WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchone()

    if not workspace:
        db.close()
        raise HTTPException(status_code=404, detail="Workspace not found")

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
        SELECT e.employee_id, sd.components_jsonb
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
            "employee_id": str(row[0]),
            "components": [
                {"code": k, "amount": v["amount"]}
                for k, v in row[1].items()
            ],
        })

    if not employees:
        db.close()
        raise HTTPException(status_code=400, detail="No active employees found")

    print("Employees being processed:", len(employees))
    for e in employees:
        print(e["employee_id"])

    # --- Load Latest Statutory Rule ---
    stat_row = db.execute(text("""
        SELECT statutory_rule_id, version
        FROM statutory_rule
        ORDER BY version DESC
        LIMIT 1
    """)).fetchone()

    if not stat_row:
        db.close()
        raise HTTPException(status_code=400, detail="No statutory rule found")

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]

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

    # --- Load Active Payroll Rules ---
    rule_rows = db.execute(text("""
        SELECT rule_id
        FROM payroll_rule
        WHERE is_active = TRUE
          AND workspace_id = :workspace_id
    """), {"workspace_id": workspace_id}).fetchall()

    payroll_rule_ids = [str(r[0]) for r in rule_rows]

    db.close()

    payroll_run_id = str(uuid.uuid4())

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
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except SQLInternalError as exc:
        if "PAYROLL_ALREADY_EXISTS" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="A payroll run already exists for this period.",
            )
        raise

    return {
        "status":         "success",
        "payroll_run_id": payroll_run_id,
        "summary":        result["totals"],
    }


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
