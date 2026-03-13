"""
Payroll Input API Routes.

Provides CRUD endpoints for managing unclaimed payroll_input rows
(the variable-event inbox consumed on the next payroll run).
"""

from fastapi import APIRouter, HTTPException
from backend.infra.repositories.payroll_input_repo import (
    list_unclaimed_inputs,
    create_input,
    delete_input,
)
from backend.infra.db.models.payroll_input import INPUT_CODES

router = APIRouter()


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

    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id is required")
    if not input_code:
        raise HTTPException(status_code=400, detail="input_code is required")
    if input_code not in INPUT_CODES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown input_code '{input_code}'. Valid codes: {list(INPUT_CODES)}",
        )

    input_category = INPUT_CODES[input_code]
    result = create_input(
        workspace_id=workspace_id,
        employee_id=employee_id,
        input_code=input_code,
        input_category=input_category,
        quantity=quantity,
        rate=rate,
        amount=amount,
    )
    return {"status": "created", "payroll_input_id": result["payroll_input_id"]}


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
