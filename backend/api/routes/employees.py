"""Employee CRUD routes — Sprint 17 Track B.

GET  /{workspace_id}/employees and POST /{workspace_id}/employees live in
workspace.py (pre-existing).  This module adds the four new endpoints:

    GET  /{workspace_id}/employees/{employee_id}            single employee with contract history
    PATCH /{workspace_id}/employees/{employee_id}           update name / status
    POST /{workspace_id}/employees/{employee_id}/contracts  add new contract (closes current)
    PATCH /{workspace_id}/employee-contracts/{contract_id}  update end_date / change_reason
"""

import logging
from datetime import date as _date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

_log = logging.getLogger(__name__)

from backend.infra.db.session import SessionLocal
from backend.infra.repositories.employee_repo import (
    get_employee_with_contract_history,
    get_current_contract,
    insert_employee_contract,
    update_employee,
    update_employee_contract,
)

router = APIRouter()

_VALID_STATUSES    = {"ACTIVE", "INACTIVE"}
_VALID_SHIFT_TYPES = {"DAY", "2_SHIFT", "4_SHIFT"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active_run_exists(db, workspace_id: str) -> bool:
    """Return True if any run for this workspace is in the edit-lock window."""
    row = db.execute(
        text("""
            SELECT 1 FROM payroll_run
            WHERE workspace_id = :wid
              AND status IN ('SUBMITTED','PROCESSING','CALCULATED','PARTIAL','APPROVED')
            LIMIT 1
        """),
        {"wid": workspace_id},
    ).fetchone()
    return row is not None


def _validate_salary_definition(db, workspace_id: str, salary_definition_id: str, start_date: _date) -> None:
    """Raise 422 if the salary definition is not in this workspace or not yet effective."""
    row = db.execute(
        text("""
            SELECT effective_from
            FROM   salary_definition
            WHERE  salary_definition_id = CAST(:sd_id AS uuid)
              AND  workspace_id         = :wid
        """),
        {"sd_id": salary_definition_id, "wid": workspace_id},
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=422, detail="Salary definition not found in this workspace")

    effective_from = row[0]
    if effective_from is not None and effective_from > start_date:
        raise HTTPException(
            status_code=422,
            detail=f"Salary definition is not effective until {effective_from} — cannot use for a contract starting {start_date}",
        )


def _resolve_optional_id(db, workspace_id: str, table: str, code_col: str, id_col: str, code_val: str | None) -> str | None:
    """Resolve a grade/designation code to its UUID. Returns None if code_val is None."""
    if code_val is None:
        return None
    row = db.execute(
        text(f"SELECT {id_col} FROM {table} WHERE workspace_id = :wid AND {code_col} = :code"),  # noqa: S608
        {"wid": workspace_id, "code": code_val},
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=422, detail=f"{table} code '{code_val}' not found in this workspace")
    return str(row[0])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PatchEmployeeSchema(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    status:    str | None = None


class AddContractSchema(BaseModel):
    salary_definition_id: str
    start_date:           str
    grade_code:           str | None = None
    designation_code:     str | None = None
    shift_type:           str | None = None
    state_of_tax:         str | None = Field(default=None, max_length=50)
    skill_level:          str | None = Field(default=None, max_length=50)
    change_reason:        str | None = Field(default=None, max_length=255)


class PatchContractSchema(BaseModel):
    end_date:      str | None = None
    change_reason: str | None = Field(default=None, max_length=255)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/{workspace_id}/employees/{employee_id}")
def get_employee(workspace_id: str, employee_id: str):
    db = SessionLocal()
    try:
        result = get_employee_with_contract_history(db, workspace_id, employee_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return result
    finally:
        db.close()


@router.patch("/{workspace_id}/employees/{employee_id}")
def patch_employee(workspace_id: str, employee_id: str, payload: PatchEmployeeSchema):
    if payload.status is not None and payload.status not in _VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of: {', '.join(sorted(_VALID_STATUSES))}")

    db = SessionLocal()
    try:
        updated = update_employee(
            db,
            workspace_id=workspace_id,
            employee_id=employee_id,
            full_name=payload.full_name.strip() if payload.full_name is not None else None,
            status=payload.status,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Employee not found")
        db.commit()
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log.error("patch_employee error: %s", e)
        raise HTTPException(status_code=400, detail="Failed to update employee")
    finally:
        db.close()


@router.post("/{workspace_id}/employees/{employee_id}/contracts", status_code=201)
def add_contract(workspace_id: str, employee_id: str, payload: AddContractSchema):
    try:
        start_date = _date.fromisoformat(payload.start_date)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"start_date '{payload.start_date}' is not a valid date (YYYY-MM-DD)")

    if payload.shift_type is not None and payload.shift_type not in _VALID_SHIFT_TYPES:
        raise HTTPException(status_code=422, detail=f"shift_type must be one of: {', '.join(sorted(_VALID_SHIFT_TYPES))}")

    db = SessionLocal()
    try:
        # Confirm employee belongs to workspace
        if not db.execute(
            text("SELECT 1 FROM employee WHERE workspace_id = :wid AND employee_id = CAST(:eid AS uuid)"),
            {"wid": workspace_id, "eid": employee_id},
        ).fetchone():
            raise HTTPException(status_code=404, detail="Employee not found")

        # D-ARCH-1: block while any run is in the lock window
        if _active_run_exists(db, workspace_id):
            raise HTTPException(
                status_code=409,
                detail="Employee contract cannot be changed while a payroll run is in progress or pending approval",
            )

        # Backdating guard: new start_date must be strictly after current contract start_date
        current = get_current_contract(db, employee_id)
        if current and start_date <= current["start_date"]:
            raise HTTPException(
                status_code=422,
                detail=f"New contract start_date must be after the current contract start_date ({current['start_date']})",
            )

        _validate_salary_definition(db, workspace_id, payload.salary_definition_id, start_date)

        grade_id       = _resolve_optional_id(db, workspace_id, "grade", "grade_code", "grade_id", payload.grade_code)
        designation_id = _resolve_optional_id(db, workspace_id, "designation", "designation_code", "designation_id", payload.designation_code)

        contract_id = insert_employee_contract(
            db,
            employee_id=employee_id,
            salary_definition_id=payload.salary_definition_id,
            start_date=start_date,
            grade_id=grade_id,
            designation_id=designation_id,
            shift_type=payload.shift_type,
            state_of_tax=payload.state_of_tax,
            skill_level=payload.skill_level,
            change_reason=payload.change_reason,
            close_current=True,
        )
        db.commit()
        return {"status": "created", "contract_id": contract_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log.error("add_contract error: %s", e)
        raise HTTPException(status_code=400, detail="Failed to add contract")
    finally:
        db.close()


@router.patch("/{workspace_id}/employee-contracts/{contract_id}")
def patch_contract(workspace_id: str, contract_id: str, payload: PatchContractSchema):
    end_date = None
    if payload.end_date is not None:
        try:
            end_date = _date.fromisoformat(payload.end_date)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"end_date '{payload.end_date}' is not a valid date (YYYY-MM-DD)")

    db = SessionLocal()
    try:
        updated = update_employee_contract(
            db,
            workspace_id=workspace_id,
            contract_id=contract_id,
            end_date=end_date,
            change_reason=payload.change_reason,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Contract not found")
        db.commit()
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log.error("patch_contract error: %s", e)
        raise HTTPException(status_code=400, detail="Failed to update contract")
    finally:
        db.close()
