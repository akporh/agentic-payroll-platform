"""
Payroll Input API Routes.

Provides CRUD endpoints for managing unclaimed payroll_input rows
(the variable-event inbox consumed on the next payroll run).
"""

from datetime import date
from fastapi import APIRouter, HTTPException
from backend.infra.repositories.payroll_input_repo import (
    list_unclaimed_inputs,
    create_input,
    delete_input,
)
from backend.infra.db.models.payroll_input import INPUT_CODES

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
    # Try YYYY-MM short form first
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


@router.get("/{workspace_id}/payroll/inputs")
def list_inputs(workspace_id: str):
    """Return all unclaimed payroll_input rows for a workspace."""
    inputs = list_unclaimed_inputs(workspace_id)
    return {"inputs": inputs, "count": len(inputs)}


@router.post("/{workspace_id}/payroll/inputs")
def add_input(workspace_id: str, payload: dict):
    """Create an unclaimed payroll_input row."""
    employee_id  = payload.get("employee_id")
    input_code   = payload.get("input_code")
    quantity     = payload.get("quantity")
    rate         = payload.get("rate")
    amount       = payload.get("amount")
    raw_date     = payload.get("reference_date")

    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id is required")
    if not input_code:
        raise HTTPException(status_code=400, detail="input_code is required")
    if input_code not in INPUT_CODES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown input_code '{input_code}'. Valid codes: {list(INPUT_CODES)}",
        )

    reference_date = _parse_period_date(raw_date) if raw_date else None

    input_category = INPUT_CODES[input_code]
    result = create_input(
        workspace_id=workspace_id,
        employee_id=employee_id,
        input_code=input_code,
        input_category=input_category,
        quantity=quantity,
        rate=rate,
        amount=amount,
        reference_date=reference_date,
    )
    return {"status": "created", "payroll_input_id": result["payroll_input_id"]}


@router.post("/{workspace_id}/payroll/inputs/bulk")
def bulk_add_inputs(workspace_id: str, payload: dict):
    """Bulk-create unclaimed payroll_input rows from an Excel upload.

    Accepts a list of rows, processes each independently, and returns
    a summary of how many were created and any per-row errors.

    Body: { "rows": [ { employee_id, input_code, quantity?, rate?, amount?, reference_date? } ] }
    Returns: { "created": N, "errors": [ { "row": i, "detail": "..." } ] }
    """
    rows = payload.get("rows", [])
    if not rows:
        raise HTTPException(status_code=400, detail="rows is required and must be non-empty")

    created = 0
    errors = []

    for i, row in enumerate(rows):
        employee_id = row.get("employee_id")
        input_code  = row.get("input_code")
        quantity    = row.get("quantity")
        rate        = row.get("rate")
        amount      = row.get("amount")
        raw_date    = row.get("reference_date")

        row_num = i + 1

        if not employee_id:
            errors.append({"row": row_num, "detail": "employee_id is required"})
            continue
        if not input_code:
            errors.append({"row": row_num, "detail": "input_code is required"})
            continue
        if input_code not in INPUT_CODES:
            errors.append({"row": row_num, "detail": f"Unknown input_code '{input_code}'"})
            continue

        reference_date = None
        if raw_date:
            try:
                reference_date = _parse_period_date(str(raw_date))
            except HTTPException as exc:
                errors.append({"row": row_num, "detail": exc.detail})
                continue

        try:
            input_category = INPUT_CODES[input_code]
            create_input(
                workspace_id=workspace_id,
                employee_id=str(employee_id),
                input_code=input_code,
                input_category=input_category,
                quantity=quantity,
                rate=rate,
                amount=amount,
                reference_date=reference_date,
            )
            created += 1
        except Exception as exc:
            errors.append({"row": row_num, "detail": str(exc)})

    return {"created": created, "errors": errors}


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
