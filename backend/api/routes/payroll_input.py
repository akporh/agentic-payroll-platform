"""
Payroll Input API Routes.

Provides CRUD endpoints for managing unclaimed payroll_input rows
(the variable-event inbox consumed on the next payroll run).

Valid input codes are not hardcoded — they are derived at runtime from the
workspace's active payroll rules.  Each rule whose rule_definition_json
contains an `input_field` key contributes one valid code; the rule_type
(EARNING / DEDUCTION) becomes the input_category stored on the row.
"""

import logging
from datetime import date
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

_log = logging.getLogger(__name__)
from backend.infra.db.session import SessionLocal
from backend.infra.repositories.payroll_input_repo import (
    list_unclaimed_inputs,
    create_input,
    update_input,
    delete_input,
)

router = APIRouter()


def _parse_period_date(raw: str) -> date:
    """Normalise an optional reference_date to the first day of its month.

    Accepts:
        "2026-03"       → date(2026, 3, 1)
        "2026-03-15"    → date(2026, 3, 1)   (any day → first of that month)

    Raises:
        HTTPException 422 if the string cannot be parsed.
    """
    raw = raw.strip()
    if len(raw) == 7:
        raw = raw + "-01"
    try:
        d = date.fromisoformat(raw)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid reference_date '{raw}'. Use 'YYYY-MM' or 'YYYY-MM-DD'.",
        )
    return d.replace(day=1)


def _load_workspace_input_codes(db, workspace_id: str) -> dict:
    """Return {input_field: rule_type} for all active rules in the workspace.

    Only rules whose rule_definition_json contains an `input_field` key are
    included — these are the rules the engine can receive event data for.
    """
    rows = db.execute(
        text("""
            SELECT rule_definition_json, rule_type
            FROM payroll_rule
            WHERE workspace_id = :wid AND is_active = true
        """),
        {"wid": workspace_id},
    ).fetchall()

    codes: dict = {}
    for defn, rule_type in rows:
        input_field = (defn or {}).get("input_field")
        if input_field:
            codes[input_field] = rule_type or "EARNING"
    return codes


@router.get("/{workspace_id}/payroll/input-codes")
def list_input_codes(workspace_id: str):
    """Return valid input codes for the workspace, derived from active payroll rules.

    Each active rule that declares an `input_field` in its rule_definition_json
    contributes one entry.  The frontend uses this list to populate dropdowns
    and validate uploads — no hardcoded list is needed.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT rule_name, rule_definition_json, rule_type
                FROM payroll_rule
                WHERE workspace_id = :wid AND is_active = true
                ORDER BY rule_name
            """),
            {"wid": workspace_id},
        ).fetchall()

        codes = []
        for rule_name, defn, rule_type in rows:
            input_field = (defn or {}).get("input_field")
            if input_field:
                codes.append({
                    "code":               input_field,
                    "category":           rule_type or "EARNING",
                    "rule_name":          rule_name,
                    "calculation_method": (defn or {}).get("calculation_method", ""),
                    "rule_rate":          (defn or {}).get("rate"),
                    "rule_amount":        (defn or {}).get("amount"),
                })

        return {"input_codes": codes}
    finally:
        db.close()


@router.get("/{workspace_id}/payroll/inputs")
def list_inputs(workspace_id: str):
    """Return all unclaimed payroll_input rows for a workspace."""
    inputs = list_unclaimed_inputs(workspace_id)
    return {"inputs": inputs, "count": len(inputs)}


@router.post("/{workspace_id}/payroll/inputs")
def add_input(workspace_id: str, payload: dict):
    """Create an unclaimed payroll_input row."""
    employee_id = payload.get("employee_id")
    input_code  = payload.get("input_code")
    quantity    = payload.get("quantity")
    raw_date    = payload.get("reference_date")

    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id is required")
    if not input_code:
        raise HTTPException(status_code=400, detail="input_code is required")
    if quantity is not None:
        if not isinstance(quantity, (int, float)):
            raise HTTPException(status_code=400, detail="quantity must be a number")
        if quantity < 0:
            raise HTTPException(status_code=400, detail="quantity must be >= 0")

    db = SessionLocal()
    try:
        valid_codes = _load_workspace_input_codes(db, workspace_id)
        if input_code not in valid_codes:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown input_code '{input_code}'. Valid codes: {sorted(valid_codes)}",
            )

        reference_date = _parse_period_date(raw_date) if raw_date else None
        input_category = valid_codes[input_code]

        result = create_input(
            workspace_id=workspace_id,
            employee_id=employee_id,
            input_code=input_code,
            input_category=input_category,
            quantity=quantity,
            reference_date=reference_date,
        )
        return {"status": "created", "payroll_input_id": result["payroll_input_id"]}
    finally:
        db.close()


@router.post("/{workspace_id}/payroll/inputs/bulk")
def bulk_add_inputs(workspace_id: str, payload: dict):
    """Bulk-create unclaimed payroll_input rows from an Excel upload.

    Accepts a list of rows keyed by employee_number (not UUID). The backend
    resolves each employee_number to employee_id scoped to the workspace,
    so cross-workspace collisions are impossible.

    Body: { "rows": [ { employee_number, input_code, quantity?, reference_date? } ] }
    Returns: { "created": N, "errors": [ { "row": i, "detail": "..." } ] }
    """
    rows = payload.get("rows", [])
    if not rows:
        raise HTTPException(status_code=400, detail="rows is required and must be non-empty")
    if len(rows) > 2000:
        raise HTTPException(status_code=400, detail="Bulk upload limit is 2000 rows per request")

    db = SessionLocal()
    try:
        valid_codes = _load_workspace_input_codes(db, workspace_id)

        # Build workspace-scoped employee_number → employee_id map once
        emp_rows = db.execute(
            text("""
                SELECT employee_number, employee_id
                FROM employee
                WHERE workspace_id = :wid AND status = 'ACTIVE'
            """),
            {"wid": workspace_id},
        ).fetchall()
        emp_map = {r[0]: str(r[1]) for r in emp_rows}

        created = 0
        skipped = 0
        errors  = []

        for i, row in enumerate(rows):
            employee_number = str(row.get("employee_number") or row.get("employee_no") or "").strip()
            input_code      = row.get("input_code")
            quantity        = row.get("quantity")
            raw_date        = row.get("reference_date")
            row_num         = i + 1

            if not employee_number:
                errors.append({"row": row_num, "detail": "employee_number is required"})
                continue
            if not input_code:
                errors.append({"row": row_num, "detail": "input_code is required"})
                continue
            if quantity is not None:
                if not isinstance(quantity, (int, float)):
                    errors.append({"row": row_num, "detail": "quantity must be a number"})
                    continue
                if quantity < 0:
                    errors.append({"row": row_num, "detail": "quantity must be >= 0"})
                    continue
            if input_code not in valid_codes:
                errors.append({"row": row_num, "detail": f"Unknown input_code '{input_code}'"})
                continue

            employee_id = emp_map.get(employee_number)
            if not employee_id:
                errors.append({"row": row_num, "detail": f"Employee '{employee_number}' not found in this workspace"})
                continue

            reference_date = None
            if raw_date:
                try:
                    reference_date = _parse_period_date(str(raw_date))
                except HTTPException as exc:
                    errors.append({"row": row_num, "detail": exc.detail})
                    continue

            try:
                input_category = valid_codes[input_code]
                create_input(
                    workspace_id=workspace_id,
                    employee_id=employee_id,
                    input_code=input_code,
                    input_category=input_category,
                    quantity=quantity,
                    reference_date=reference_date,
                )
                created += 1
            except IntegrityError as exc:
                if isinstance(exc.orig, UniqueViolation):
                    # Duplicate (employee, input_code, period) — skip silently; re-upload is idempotent.
                    skipped += 1
                else:
                    _log.error("Unexpected IntegrityError on row %d: %s", row_num, exc)
                    errors.append({"row": row_num, "detail": "Failed to save input — data constraint violation"})
            except Exception as exc:
                _log.error("Unexpected error on row %d: %s", row_num, exc)
                errors.append({"row": row_num, "detail": "Failed to save input — unexpected error"})

        return {"created": created, "skipped": skipped, "errors": errors}
    finally:
        db.close()


@router.get("/workspaces/{workspace_id}/payroll/inputs/issues")
def get_input_issues(workspace_id: str):
    """Return a count of payroll inputs that require attention before the next run.

    Scoped to unclaimed inputs (payroll_run_id IS NULL) for the current calendar month.
    Two conditions counted:
      - deactivated_with_inputs: inputs for employees whose contract has ended
        (contract_end IS NOT NULL AND contract_end < first day of current month)
      - unmatched_with_inputs: inputs for employees missing grade or salary definition
    """
    from datetime import date as _date
    today       = _date.today()
    period_start = today.replace(day=1)

    db = SessionLocal()
    try:
        deactivated = db.execute(
            text("""
                SELECT COUNT(DISTINCT pi.payroll_input_id) AS cnt
                FROM   payroll_input pi
                JOIN   employee e ON pi.employee_id = e.employee_id
                LEFT JOIN LATERAL (
                    SELECT ec2.end_date
                    FROM   employee_contract ec2
                    WHERE  ec2.employee_id = e.employee_id
                    ORDER  BY COALESCE(ec2.end_date, '9999-12-31') DESC,
                              ec2.start_date DESC NULLS LAST
                    LIMIT  1
                ) ec ON true
                WHERE  e.workspace_id      = :wid
                  AND  pi.payroll_run_id   IS NULL
                  AND  ec.end_date         IS NOT NULL
                  AND  ec.end_date         < CAST(:period_start AS DATE)
            """),
            {"wid": workspace_id, "period_start": str(period_start)},
        ).scalar() or 0

        unmatched = db.execute(
            text("""
                SELECT COUNT(DISTINCT pi.payroll_input_id) AS cnt
                FROM   payroll_input pi
                JOIN   employee e ON pi.employee_id = e.employee_id
                LEFT JOIN LATERAL (
                    SELECT ec2.grade_id, ec2.salary_definition_id
                    FROM   employee_contract ec2
                    WHERE  ec2.employee_id = e.employee_id
                      AND  (ec2.end_date IS NULL OR ec2.end_date >= CAST(:period_start AS DATE))
                    ORDER  BY COALESCE(ec2.end_date, '9999-12-31') DESC,
                              ec2.start_date DESC NULLS LAST
                    LIMIT  1
                ) ec ON true
                WHERE  e.workspace_id    = :wid
                  AND  pi.payroll_run_id IS NULL
                  AND  (ec.grade_id IS NULL OR ec.salary_definition_id IS NULL)
            """),
            {"wid": workspace_id, "period_start": str(period_start)},
        ).scalar() or 0

        pending = db.execute(
            text("""
                SELECT COUNT(*) FROM payroll_input
                WHERE workspace_id = :wid AND payroll_run_id IS NULL
            """),
            {"wid": workspace_id},
        ).scalar() or 0

        month_name = today.strftime("%B %Y")

        return {
            "total":                    int(deactivated) + int(unmatched),
            "deactivated_with_inputs":  int(deactivated),
            "unmatched_with_inputs":    int(unmatched),
            "pending_count":            int(pending),
            "period_label":             month_name,
        }
    finally:
        db.close()


@router.patch("/{workspace_id}/payroll/inputs/{input_id}")
def edit_input(workspace_id: str, input_id: str, payload: dict):
    """Update quantity and reference_date on an unclaimed payroll_input row."""
    quantity = payload.get("quantity")
    raw_date = payload.get("reference_date")

    if quantity is not None and quantity < 0:
        raise HTTPException(status_code=400, detail="quantity must be >= 0")

    reference_date = _parse_period_date(raw_date) if raw_date else None

    updated = update_input(workspace_id, input_id, quantity, reference_date)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Input not found or already claimed by a payroll run",
        )
    return {"status": "updated"}


@router.delete("/{workspace_id}/payroll/inputs/{input_id}")
def remove_input(workspace_id: str, input_id: str):
    """Delete an unclaimed payroll_input row."""
    deleted = delete_input(workspace_id, input_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Input not found or already claimed by a payroll run",
        )
    return {"status": "deleted"}
