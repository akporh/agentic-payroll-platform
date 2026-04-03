"""
Payroll Input API Routes.

Provides CRUD endpoints for managing unclaimed payroll_input rows
(the variable-event inbox consumed on the next payroll run).

Valid input codes are not hardcoded — they are derived at runtime from the
workspace's active payroll rules.  Each rule whose rule_definition_json
contains an `input_field` key contributes one valid code; the rule_type
(EARNING / DEDUCTION) becomes the input_category stored on the row.
"""

from datetime import date
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from backend.infra.db.session import SessionLocal
from backend.infra.repositories.payroll_input_repo import (
    list_unclaimed_inputs,
    create_input,
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
            except Exception as exc:
                errors.append({"row": row_num, "detail": str(exc)})

        return {"created": created, "errors": errors}
    finally:
        db.close()


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
