import json
import uuid
from datetime import date as _date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from backend.infra.db.session import SessionLocal
from backend.application import onboarding_service
from backend.api.schemas.pay_cycle import PayCycleCreateSchema
from backend.api.schemas.grade import GradeCreateSchema
from backend.api.schemas.designation import DesignationCreateSchema
from backend.api.schemas.salary_definition import SalaryDefinitionCreateSchema
from backend.api.schemas.payroll_rule import PayrollRuleCreateSchema, RuleSetPublishSchema
from backend.api.schemas.component_metadata import ComponentMetadataCreateSchema
from backend.domain.onboarding.onboarding_status import get_onboarding_status
from backend.domain.onboarding.workspace_state_machine import transition_workspace
from backend.domain.onboarding.hard_validator import validate_workspace_for_state
from backend.infra.repositories.workspace_config_repo import (
    get_workspace_payroll_config,
    upsert_workspace_payroll_config,
)
from backend.infra.repositories.rate_code_repo import (
    list_rate_codes,
    create_rate_code,
    delete_rate_code,
)
from backend.infra.repositories.public_holiday_repo import (
    list_workspace_holidays,
    add_workspace_holiday,
    delete_workspace_holiday,
)


router = APIRouter()


class WorkspaceCreateSchema(BaseModel):
    name: str
    country_code: str
    base_currency: str = "NGN"


@router.post("/workspace")
def create_workspace(payload: WorkspaceCreateSchema):
    db = SessionLocal()
    try:
        # Validate country_code has statutory rules configured
        cc_exists = db.execute(
            text("SELECT 1 FROM statutory_rule WHERE country_code = :cc LIMIT 1"),
            {"cc": payload.country_code},
        ).fetchone()
        if not cc_exists:
            raise HTTPException(
                status_code=422,
                detail=f"No statutory rules configured for country_code '{payload.country_code}'. "
                       "Contact your administrator.",
            )

        workspace_id = str(uuid.uuid4())

        db.execute(
            text("""
                INSERT INTO workspace (workspace_id, name, country_code, base_currency, status)
                VALUES (:wid, :name, :country_code, :base_currency, 'DRAFT')
            """),
            {
                "wid": workspace_id,
                "name": payload.name,
                "country_code": payload.country_code,
                "base_currency": payload.base_currency,
            },
        )
        db.commit()
        return {
            "workspace_id": workspace_id,
            "name": payload.name,
            "country_code": payload.country_code,
            "base_currency": payload.base_currency,
            "status": "DRAFT",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/workspaces")
def list_workspaces():
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    w.workspace_id,
                    w.name,
                    w.country_code,
                    w.base_currency,
                    w.status,
                    COUNT(e.employee_id) FILTER (WHERE e.status = 'ACTIVE') AS active_employees
                FROM workspace w
                LEFT JOIN employee e ON e.workspace_id = w.workspace_id
                GROUP BY w.workspace_id, w.name, w.country_code, w.base_currency, w.status
                ORDER BY w.name
            """)
        ).fetchall()

        return [
            {
                "workspace_id": str(row[0]),
                "name": row[1],
                "country_code": row[2],
                "base_currency": row[3],
                "status": row[4] or "DRAFT",
                "active_employee_count": row[5] or 0,
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/workspace/info")
def workspace_info():
    db = SessionLocal()

    workspace = db.execute(
        text("SELECT workspace_id, name FROM workspace LIMIT 1")
    ).fetchone()

    if not workspace:
        db.close()
        return {"workspace_name": "Not Found", "active_employee_count": 0}

    workspace_id = workspace[0]
    workspace_name = workspace[1]

    count = db.execute(
        text("""
            SELECT COUNT(*)
            FROM employee
            WHERE workspace_id = :wid
              AND status = 'ACTIVE'
        """),
        {"wid": workspace_id}
    ).scalar()

    db.close()

    return {
        "workspace_id": str(workspace_id),
        "workspace_name": workspace_name,
        "active_employee_count": count
    }


@router.post("/{workspace_id}/transition")
def transition_workspace_endpoint(workspace_id: str, target_state: str):
    db = SessionLocal()

    try:
        result = transition_workspace(
            db,
            workspace_id,
            target_state,
            validate_workspace_for_state,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/{workspace_id}/onboarding-status")
def onboarding_status(workspace_id: str):
    db = SessionLocal()
    try:
        return get_onboarding_status(db, workspace_id)
    finally:
        db.close()


@router.get("/{workspace_id}/employees")
def list_employees(workspace_id: str):
    """Return all active employees for a workspace with contract details."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    e.employee_id,
                    e.full_name,
                    e.employee_number,
                    e.status,
                    d.designation_code   AS designation,
                    g.grade_code         AS grade,
                    ec.start_date        AS contract_start,
                    ec.end_date          AS contract_end,
                    (ec.end_date IS NOT NULL AND ec.end_date < CURRENT_DATE) AS is_ended,
                    ec.shift_type,
                    ec.state_of_tax,
                    ec.skill_level,
                    (ec.salary_definition_id IS NOT NULL) AS is_enrolled,
                    ec.imported_grade_label,
                    ec.imported_designation_label,
                    ec.contract_id
                FROM employee e
                LEFT JOIN LATERAL (
                    SELECT ec2.*
                    FROM employee_contract ec2
                    WHERE ec2.employee_id = e.employee_id
                    ORDER BY COALESCE(ec2.end_date, '9999-12-31') DESC,
                             ec2.start_date DESC NULLS LAST
                    LIMIT 1
                ) ec ON true
                LEFT JOIN designation d ON d.designation_id = ec.designation_id
                LEFT JOIN grade       g ON g.grade_id       = ec.grade_id
                WHERE e.workspace_id = :wid
                ORDER BY e.full_name
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "employee_id":    str(row[0]),
                "full_name":      row[1],
                "employee_number": row[2],
                "status":         row[3],
                "designation":    row[4],
                "grade":          row[5],
                "contract_start": str(row[6]) if row[6] else None,
                "contract_end":   str(row[7]) if row[7] else None,
                "is_ended":       bool(row[8]) if row[8] is not None else False,
                "shift_type":     row[9],
                "state_of_tax":   row[10],
                "skill_level":    row[11],
                "is_enrolled":               bool(row[12]) if row[12] is not None else False,
                "imported_grade_label":       row[13],
                "imported_designation_label": row[14],
                "contract_id":               str(row[15]) if row[15] else None,
            }
            for row in rows
        ]
    finally:
        db.close()


class CreateEmployeeSchema(BaseModel):
    first_name: str
    last_name: str
    employee_number: str
    salary_definition_code: str | None = None
    grade_code: str | None = None
    designation_code: str | None = None
    contract_start: str | None = None
    contract_end: str | None = None
    tin: str | None = None
    rsa: str | None = None
    bank: str | None = None
    account_number: str | None = None
    shift_type: str | None = None
    state_of_tax: str | None = Field(default=None, max_length=50)
    skill_level: str | None = Field(default=None, max_length=50)
    imported_grade_label: str | None = Field(default=None, max_length=100)
    imported_designation_label: str | None = Field(default=None, max_length=100)


@router.post("/{workspace_id}/employees")
def create_employee(workspace_id: str, payload: CreateEmployeeSchema):
    """Create a single employee with an employee_contract in one transaction."""
    from uuid import uuid4 as _uuid4
    from psycopg2.extras import Json

    _VALID_SHIFT_TYPES = {"DAY", "2_SHIFT", "4_SHIFT"}
    if payload.shift_type is not None and payload.shift_type not in _VALID_SHIFT_TYPES:
        raise HTTPException(status_code=422, detail=f"shift_type must be one of: DAY, 2_SHIFT, 4_SHIFT")

    db = SessionLocal()
    try:
        # Duplicate employee_number check
        dup = db.execute(
            text("SELECT 1 FROM employee WHERE workspace_id = :wid AND employee_number = :num"),
            {"wid": workspace_id, "num": payload.employee_number},
        ).fetchone()
        if dup:
            raise HTTPException(status_code=409, detail=f"Employee number '{payload.employee_number}' already exists in this workspace")

        # Resolve salary definition (optional — None means not-enrolled)
        salary_definition_id = None
        if payload.salary_definition_code:
            sd_row = db.execute(
                text("SELECT salary_definition_id, effective_from FROM salary_definition WHERE workspace_id = :wid AND code = :code"),
                {"wid": workspace_id, "code": payload.salary_definition_code},
            ).fetchone()
            if not sd_row:
                raise HTTPException(status_code=400, detail=f"Salary definition '{payload.salary_definition_code}' not found")
            salary_definition_id = str(sd_row[0])
            _sd_effective_from = sd_row[1]
            if payload.contract_start and _sd_effective_from is not None:
                from datetime import date as _date_cls
                try:
                    _cs = _date_cls.fromisoformat(payload.contract_start)
                    if _sd_effective_from > _cs:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Salary definition '{payload.salary_definition_code}' is not effective until {_sd_effective_from} — cannot use for a contract starting {_cs}",
                        )
                except ValueError:
                    pass  # date parse error caught below

        # Resolve grade
        grade_id = None
        if payload.grade_code:
            g_row = db.execute(
                text("SELECT grade_id FROM grade WHERE workspace_id = :wid AND grade_code = :code"),
                {"wid": workspace_id, "code": payload.grade_code},
            ).fetchone()
            if not g_row:
                raise HTTPException(status_code=400, detail=f"Grade '{payload.grade_code}' not found")
            grade_id = str(g_row[0])

        # Resolve designation
        designation_id = None
        if payload.designation_code:
            d_row = db.execute(
                text("SELECT designation_id FROM designation WHERE workspace_id = :wid AND designation_code = :code"),
                {"wid": workspace_id, "code": payload.designation_code},
            ).fetchone()
            if not d_row:
                raise HTTPException(status_code=400, detail=f"Designation '{payload.designation_code}' not found")
            designation_id = str(d_row[0])

        # Validate dates
        try:
            start_date = _date.fromisoformat(payload.contract_start) if payload.contract_start else None
        except ValueError:
            raise HTTPException(status_code=422, detail=f"contract_start '{payload.contract_start}' is not a valid date (YYYY-MM-DD)")
        try:
            end_date = _date.fromisoformat(payload.contract_end) if payload.contract_end else None
        except ValueError:
            raise HTTPException(status_code=422, detail=f"contract_end '{payload.contract_end}' is not a valid date (YYYY-MM-DD)")
        if start_date and end_date and end_date < start_date:
            raise HTTPException(status_code=422, detail="contract_end must be on or after contract_start")

        full_name = f"{payload.first_name.strip()} {payload.last_name.strip()}".strip()
        employee_id = str(_uuid4())

        biodata = {}
        if payload.tin: biodata["TIN"] = payload.tin
        if payload.rsa: biodata["RSA"] = payload.rsa
        if payload.bank: biodata["BANK"] = payload.bank
        if payload.account_number: biodata["ACCOUNT_NUMBER"] = payload.account_number

        db.execute(
            text("""
                INSERT INTO employee (
                    employee_id, workspace_id, full_name,
                    employee_number, personal_details_encrypted, status
                )
                VALUES (
                    CAST(:eid AS uuid), :wid, :name,
                    :emp_number, :biodata, 'ACTIVE'
                )
            """),
            {
                "eid": employee_id,
                "wid": workspace_id,
                "name": full_name,
                "emp_number": payload.employee_number,
                "biodata": Json(biodata),
            },
        )

        db.execute(
            text("""
                INSERT INTO employee_contract (
                    contract_id, employee_id, salary_definition_id,
                    grade_id, designation_id, start_date, end_date,
                    shift_type, state_of_tax, skill_level, is_union_member,
                    imported_grade_label, imported_designation_label
                )
                VALUES (
                    CAST(:cid AS uuid), CAST(:eid AS uuid), CAST(:sd_id AS uuid),
                    CAST(:grade_id AS uuid), CAST(:designation_id AS uuid),
                    COALESCE(CAST(:start_date AS DATE), CURRENT_DATE),
                    CAST(:end_date AS DATE),
                    :shift_type, :state_of_tax, :skill_level, false,
                    :imported_grade_label, :imported_designation_label
                )
            """),
            {
                "cid":                       str(_uuid4()),
                "eid":                       employee_id,
                "sd_id":                     salary_definition_id,
                "grade_id":                  grade_id,
                "designation_id":            designation_id,
                "start_date":                str(start_date) if start_date else None,
                "end_date":                  str(end_date) if end_date else None,
                "shift_type":                payload.shift_type,
                "state_of_tax":              payload.state_of_tax,
                "skill_level":               payload.skill_level,
                "imported_grade_label":      payload.imported_grade_label,
                "imported_designation_label": payload.imported_designation_label,
            },
        )

        db.commit()
        return {"status": "created", "employee_id": employee_id, "full_name": full_name}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging as _logging
        _logging.getLogger(__name__).error("create_employee failed: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create employee")
    finally:
        db.close()


class EnrollEmployeeSchema(BaseModel):
    salary_definition_code: str
    grade_code: str | None = None
    designation_code: str | None = None


@router.post("/{workspace_id}/employees/{employee_id}/enroll")
def enroll_employee(workspace_id: str, employee_id: str, payload: EnrollEmployeeSchema):
    """Assign a salary definition to a not-enrolled employee, making them payroll-eligible."""
    from backend.infra.repositories import employee_repo as _emp_repo

    db = SessionLocal()
    try:
        # Verify the employee belongs to this workspace
        emp_row = db.execute(
            text("SELECT 1 FROM employee WHERE employee_id = CAST(:eid AS uuid) AND workspace_id = :wid"),
            {"eid": employee_id, "wid": workspace_id},
        ).fetchone()
        if not emp_row:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Verify employee is not already enrolled
        already = db.execute(
            text("""
                SELECT 1 FROM employee_contract
                WHERE employee_id = CAST(:eid AS uuid)
                  AND (end_date IS NULL OR end_date >= CURRENT_DATE)
                  AND salary_definition_id IS NOT NULL
            """),
            {"eid": employee_id},
        ).fetchone()
        if already:
            raise HTTPException(status_code=400, detail="Employee is already enrolled in payroll")

        # Resolve salary definition
        sd_row = db.execute(
            text("SELECT salary_definition_id FROM salary_definition WHERE workspace_id = :wid AND code = :code"),
            {"wid": workspace_id, "code": payload.salary_definition_code},
        ).fetchone()
        if not sd_row:
            raise HTTPException(status_code=400, detail=f"Salary definition '{payload.salary_definition_code}' not found")

        # Resolve optional grade
        grade_id = None
        if payload.grade_code:
            g_row = db.execute(
                text("SELECT grade_id FROM grade WHERE workspace_id = :wid AND grade_code = :code"),
                {"wid": workspace_id, "code": payload.grade_code},
            ).fetchone()
            if not g_row:
                raise HTTPException(status_code=400, detail=f"Grade '{payload.grade_code}' not found")
            grade_id = str(g_row[0])

        # Resolve optional designation
        designation_id = None
        if payload.designation_code:
            d_row = db.execute(
                text("SELECT designation_id FROM designation WHERE workspace_id = :wid AND designation_code = :code"),
                {"wid": workspace_id, "code": payload.designation_code},
            ).fetchone()
            if not d_row:
                raise HTTPException(status_code=400, detail=f"Designation '{payload.designation_code}' not found")
            designation_id = str(d_row[0])

        updated = _emp_repo.enroll_employee_contract(
            db, employee_id, str(sd_row[0]), grade_id, designation_id
        )
        if not updated:
            raise HTTPException(status_code=404, detail="No unenrolled contract found for this employee")

        db.commit()
        return {"status": "enrolled", "employee_id": employee_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging as _logging
        _logging.getLogger(__name__).error("enroll_employee failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to enroll employee")
    finally:
        db.close()


class BulkEnrollEmployeesSchema(BaseModel):
    employee_ids: list[str]
    salary_definition_code: str
    grade_code: str | None = None
    designation_code: str | None = None


@router.post("/{workspace_id}/employees/bulk-enroll")
def bulk_enroll_employees(workspace_id: str, payload: BulkEnrollEmployeesSchema):
    """Enroll multiple not-enrolled employees in a single call.

    Already-enrolled employees are skipped (not an error).
    Returns {enrolled, skipped, failed, details}.
    """
    from backend.infra.repositories import employee_repo as _emp_repo

    if not payload.employee_ids:
        raise HTTPException(status_code=422, detail="employee_ids must not be empty")
    if len(payload.employee_ids) > 500:
        raise HTTPException(status_code=422, detail="Maximum 500 employees per bulk enroll request")

    db = SessionLocal()
    try:
        sd_row = db.execute(
            text("SELECT salary_definition_id FROM salary_definition WHERE workspace_id = :wid AND code = :code"),
            {"wid": workspace_id, "code": payload.salary_definition_code},
        ).fetchone()
        if not sd_row:
            raise HTTPException(status_code=400, detail=f"Salary definition '{payload.salary_definition_code}' not found")

        grade_id = None
        if payload.grade_code:
            g = db.execute(
                text("SELECT grade_id FROM grade WHERE workspace_id = :wid AND grade_code = :c"),
                {"wid": workspace_id, "c": payload.grade_code},
            ).fetchone()
            if not g:
                raise HTTPException(status_code=400, detail=f"Grade '{payload.grade_code}' not found")
            grade_id = str(g[0])

        designation_id = None
        if payload.designation_code:
            d = db.execute(
                text("SELECT designation_id FROM designation WHERE workspace_id = :wid AND designation_code = :c"),
                {"wid": workspace_id, "c": payload.designation_code},
            ).fetchone()
            if not d:
                raise HTTPException(status_code=400, detail=f"Designation '{payload.designation_code}' not found")
            designation_id = str(d[0])

        result = _emp_repo.bulk_enroll_employee_contracts(
            db, workspace_id, payload.employee_ids, str(sd_row[0]), grade_id, designation_id
        )
        db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging as _logging
        _logging.getLogger(__name__).error("bulk_enroll_employees failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to bulk enroll employees")
    finally:
        db.close()


class EmployeeContractUpdateSchema(BaseModel):
    grade_code: str | None = None
    designation_code: str | None = None
    shift_type: str | None = None
    state_of_tax: str | None = Field(default=None, max_length=50)
    skill_level:  str | None = Field(default=None, max_length=50)
    is_union_member: bool | None = None
    contract_end: str | None = None
    set_contract_end: bool = False


@router.patch("/{workspace_id}/employees/contracts")
def bulk_update_employee_contracts(workspace_id: str, payload: list[dict]):
    """Bulk-update employee contract start/end dates by employee_number.

    Accepts a list of ``{employee_number, contract_start, contract_end?}`` dicts.
    For each entry, finds the employee's active contract and updates its start_date
    (and end_date when provided).  Employees not found in the workspace are returned
    in the ``not_found`` list — no error is raised for them.

    Used by the Client Setup page to correct contract dates after initial onboarding.
    """
    from datetime import date as _date

    db = SessionLocal()
    try:
        updated = 0
        not_found: list[str] = []

        for item in payload:
            emp_number = str(item.get("employee_number") or "").strip()
            start_str  = str(item.get("contract_start") or "").strip()
            end_str    = str(item.get("contract_end") or "").strip()

            if not emp_number or not start_str:
                continue

            try:
                start_date = _date.fromisoformat(start_str)
            except ValueError:
                continue

            end_date = None
            if end_str:
                try:
                    end_date = _date.fromisoformat(end_str)
                except ValueError:
                    pass

            row = db.execute(
                text("""
                    SELECT e.employee_id
                    FROM employee e
                    WHERE e.workspace_id    = :wid
                      AND e.employee_number = :num
                      AND e.status          = 'ACTIVE'
                    LIMIT 1
                """),
                {"wid": workspace_id, "num": emp_number},
            ).fetchone()

            if not row:
                not_found.append(emp_number)
                continue

            db.execute(
                text("""
                    UPDATE employee_contract
                    SET start_date = :start_date,
                        end_date   = CAST(:end_date AS DATE)
                    WHERE employee_id = :eid
                      AND (end_date IS NULL OR end_date >= CURRENT_DATE)
                """),
                {"start_date": start_date, "end_date": end_date, "eid": str(row[0])},
            )
            updated += 1

        db.commit()
        return {"updated": updated, "not_found": not_found}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.patch("/{workspace_id}/employees/{employee_id}/contract")
def update_employee_contract(
    workspace_id: str, employee_id: str, payload: EmployeeContractUpdateSchema
):
    db = SessionLocal()
    try:
        _VALID_SHIFT_TYPES = {"DAY", "2_SHIFT", "4_SHIFT"}
        if payload.shift_type is not None and payload.shift_type not in _VALID_SHIFT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"shift_type '{payload.shift_type}' is not valid — allowed values: DAY, 2_SHIFT, 4_SHIFT",
            )

        grade_id = None
        if payload.grade_code:
            row = db.execute(
                text("SELECT grade_id FROM grade WHERE workspace_id = :wid AND grade_code = :code"),
                {"wid": workspace_id, "code": payload.grade_code},
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail=f"Grade '{payload.grade_code}' not found")
            grade_id = str(row[0])

        designation_id = None
        if payload.designation_code:
            row = db.execute(
                text(
                    "SELECT designation_id FROM designation WHERE workspace_id = :wid AND designation_code = :code"
                ),
                {"wid": workspace_id, "code": payload.designation_code},
            ).fetchone()
            if not row:
                raise HTTPException(
                    status_code=400, detail=f"Designation '{payload.designation_code}' not found"
                )
            designation_id = str(row[0])

        # Target the most recent contract regardless of end_date so that
        # ended-contract employees (shown in their own section) can have
        # grade/designation corrected without touching end_date.
        if payload.set_contract_end and payload.contract_end is not None:
            try:
                contract_end_date: _date | None = _date.fromisoformat(payload.contract_end)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"contract_end '{payload.contract_end}' is not a valid date (use YYYY-MM-DD)")
        elif payload.set_contract_end:
            contract_end_date = None
        else:
            contract_end_date = None

        result = db.execute(
            text("""
                UPDATE employee_contract
                SET grade_id        = COALESCE(CAST(:grade_id AS uuid), grade_id),
                    designation_id  = COALESCE(CAST(:designation_id AS uuid), designation_id),
                    shift_type      = CASE WHEN :shift_type_set    THEN :shift_type      ELSE shift_type      END,
                    state_of_tax    = CASE WHEN :state_set         THEN :state_of_tax    ELSE state_of_tax    END,
                    skill_level     = CASE WHEN :skill_set         THEN :skill_level     ELSE skill_level     END,
                    is_union_member = CASE WHEN :union_member_set  THEN :is_union_member ELSE is_union_member  END,
                    end_date        = CASE WHEN :end_date_set      THEN CAST(:end_date AS DATE) ELSE end_date  END
                WHERE contract_id = (
                    SELECT ec2.contract_id
                    FROM employee_contract ec2
                    WHERE ec2.employee_id = CAST(:eid AS uuid)
                      AND ec2.employee_id IN (
                          SELECT employee_id FROM employee WHERE workspace_id = :wid
                      )
                    ORDER BY COALESCE(ec2.end_date, '9999-12-31') DESC,
                             ec2.start_date DESC NULLS LAST
                    LIMIT 1
                )
            """),
            {
                "grade_id":          grade_id,
                "designation_id":    designation_id,
                "shift_type":        payload.shift_type,
                "shift_type_set":    payload.shift_type is not None,
                "state_of_tax":      payload.state_of_tax,
                "state_set":         payload.state_of_tax is not None,
                "skill_level":       payload.skill_level,
                "skill_set":         payload.skill_level is not None,
                "is_union_member":   payload.is_union_member,
                "union_member_set":  payload.is_union_member is not None,
                "end_date":          str(contract_end_date) if contract_end_date else None,
                "end_date_set":      payload.set_contract_end,
                "eid":               employee_id,
                "wid":               workspace_id,
            },
        )
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="No contract record found for this employee. Re-run onboarding to create one.",
            )
        db.commit()
        return {"status": "updated", "employee_id": employee_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/{workspace_id}/salary-definitions")
def list_salary_definitions(workspace_id: str):
    """Return all salary definitions for a workspace with their codes.

    Used by the onboarding UI to populate salary mapping dropdowns.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT salary_definition_id, code, name
                FROM salary_definition
                WHERE workspace_id = :wid
                ORDER BY code
            """),
            {"wid": workspace_id},
        ).fetchall()
        return [
            {
                "salary_definition_id": str(row[0]),
                "code": row[1],
                "name": row[2],
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/{workspace_id}/designations")
def list_designations(workspace_id: str):
    """Return all designation codes for a workspace. Used by the upload UI for designation resolution."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT designation_id, designation_code
                FROM designation
                WHERE workspace_id = :wid
                ORDER BY designation_code
            """),
            {"wid": workspace_id},
        ).fetchall()
        return [{"designation_id": str(row[0]), "code": row[1]} for row in rows]
    finally:
        db.close()


@router.post("/{workspace_id}/salary-definitions")
def create_salary_definition_by_code(workspace_id: str, body: dict):
    """Create a minimal salary definition by code (empty components). Used when a grade code
    from an uploaded Excel file has no matching salary definition in the workspace."""
    code = (body.get("code") or "").strip().upper()
    name = body.get("name") or code
    if not code:
        raise HTTPException(status_code=400, detail="code is required")
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO salary_definition (salary_definition_id, workspace_id, code, name, components_jsonb)
                VALUES (gen_random_uuid(), :wid, :code, :name, '{"BASIC": 0}'::jsonb)
                ON CONFLICT DO NOTHING
                RETURNING salary_definition_id, code, name
            """),
            {"wid": workspace_id, "code": code, "name": name},
        ).fetchone()
        db.commit()
        if not row:
            row = db.execute(
                text("""
                    SELECT salary_definition_id, code, name
                    FROM salary_definition
                    WHERE workspace_id = :wid AND code = :code
                """),
                {"wid": workspace_id, "code": code},
            ).fetchone()
        return {"salary_definition_id": str(row[0]), "code": row[1], "name": row[2]}
    finally:
        db.close()


@router.post("/{workspace_id}/pay-cycle")
def create_pay_cycle_endpoint(workspace_id: str, payload: PayCycleCreateSchema):
    db = SessionLocal()
    try:
        result = onboarding_service.create_pay_cycle(
            db=db,
            workspace_id=workspace_id,
            frequency=payload.frequency,
            run_day=payload.run_day,
            cutoff_day=payload.cutoff_day,
            payment_day=payload.payment_day,
            definition_json=payload.definition_json,
        )
        return result
    finally:
        db.close()

@router.post("/{workspace_id}/grade")
def create_grade_endpoint(workspace_id: str, payload: GradeCreateSchema):
    db = SessionLocal()
    try:
        return onboarding_service.create_grade(
            db=db,
            workspace_id=workspace_id,
            grade_code=payload.grade_code,
            description=payload.description,
        )
    finally:
        db.close()

@router.post("/{workspace_id}/designation")
def create_designation_endpoint(workspace_id: str, payload: DesignationCreateSchema):
    db = SessionLocal()
    try:
        return onboarding_service.create_designation(
            db=db,
            workspace_id=workspace_id,
            designation_code=payload.designation_code,
            description=payload.description,
        )
    finally:
        db.close()

@router.post("/{workspace_id}/salary-definition")
def create_salary_definition_endpoint(workspace_id: str, payload: SalaryDefinitionCreateSchema):
    components = payload.components_jsonb or {}
    if isinstance(components, list):
        components = {item["component_name"]: {"amount": item["amount"]} for item in components}
    mandatory = {"BASIC", "HOUSING", "TRANSPORT"}
    missing = mandatory - {k.upper() for k in components}
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Required components missing: {', '.join(sorted(missing))}.",
        )
    for code, val in components.items():
        amount = val.get("amount", val) if isinstance(val, dict) else val
        try:
            amount = float(Decimal(str(amount)))
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail=f"Invalid amount for '{code}'.")
        if amount <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"Amount for '{code}' must be greater than zero.",
            )
    db = SessionLocal()
    try:
        return onboarding_service.create_salary_definition(
            db=db,
            workspace_id=workspace_id,
            name=payload.name,
            code=payload.code,
            components_jsonb=payload.components_jsonb,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
        )
    finally:
        db.close()


@router.post("/{workspace_id}/payroll-rule")
def create_payroll_rule_endpoint(workspace_id: str, payload: PayrollRuleCreateSchema):
    db = SessionLocal()
    try:
        return onboarding_service.create_payroll_rule(
            db=db,
            workspace_id=workspace_id,
            rule_name=payload.rule_name,
            rule_definition_json=payload.rule_definition_json,
            rule_type=payload.rule_type,
        )
    finally:
        db.close()

@router.post("/{workspace_id}/rule-set")
def publish_rule_set_endpoint(workspace_id: str, payload: RuleSetPublishSchema):
    """Publish a new versioned rule_set snapshot for a workspace.

    Accepts a list of rules each with their own effective_from date.
    Rules sharing the same date are grouped into one rule_set row.
    Use this endpoint for rule version updates after initial onboarding.
    """
    db = SessionLocal()
    try:
        rules = [r.dict() for r in payload.rules]
        result = onboarding_service.publish_rule_sets(
            db, workspace_id, rules, created_by=payload.created_by
        )
        if not result:
            raise HTTPException(status_code=422, detail="No rules with effective_from provided")
        db.commit()
        return {"published": result}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()


@router.post("/{workspace_id}/component-metadata")
def create_component_metadata_endpoint(workspace_id: str, payload: ComponentMetadataCreateSchema):
    db = SessionLocal()
    try:
        return onboarding_service.create_component_metadata(
            db=db,
            workspace_id=workspace_id,
            component_code=payload.component_code,
            overrides_json=payload.overrides_json,
        )
    finally:
        db.close()


@router.get("/{workspace_id}/platform-components")
def list_platform_components(workspace_id: str):
    """Return statutory components available for the workspace's country."""
    db = SessionLocal()
    try:
        workspace = db.execute(
            text("SELECT country_code FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()

        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        country_code = workspace[0]

        rows = db.execute(
            text("""
                SELECT component_code, metadata_json, component_class
                FROM component_metadata
                WHERE country_code = :cc
                  AND is_active = TRUE
                ORDER BY execution_priority
            """),
            {"cc": country_code},
        ).fetchall()

        return [
            {
                "component_code": row[0],
                "label": (row[1] or {}).get("label", row[0]),
                "component_class": row[2],
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/{workspace_id}/component-overrides")
def list_component_overrides(workspace_id: str):
    """Return existing client component overrides for the workspace."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT component_code, overrides_json, is_active, proration_strategy
                FROM client_component_metadata
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "component_code": row[0],
                "overrides_json": row[1],
                "is_active": row[2] if row[2] is not None else True,
                "proration_strategy": row[3],
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/{workspace_id}/configuration")
def get_workspace_configuration(workspace_id: str):
    """Aggregate workspace configuration from multiple tables."""
    db = SessionLocal()
    try:
        # Workspace
        ws = db.execute(
            text("""
                SELECT workspace_id, name, country_code, base_currency, status
                FROM workspace WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchone()

        if not ws:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Pay cycle
        pc = db.execute(
            text("""
                SELECT frequency, run_day, cutoff_day, payment_day
                FROM pay_cycle
                WHERE workspace_id = :wid AND is_active = TRUE
                LIMIT 1
            """),
            {"wid": workspace_id},
        ).fetchone()

        # Grades
        grades = db.execute(
            text("""
                SELECT grade_code, description
                FROM grade WHERE workspace_id = :wid ORDER BY grade_code
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Designations
        designations = db.execute(
            text("""
                SELECT designation_code, description
                FROM designation WHERE workspace_id = :wid ORDER BY designation_code
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Salary definitions — include ID for PATCH routing
        sal_defs = db.execute(
            text("""
                SELECT salary_definition_id, name, code, components_jsonb
                FROM salary_definition WHERE workspace_id = :wid ORDER BY code
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Payroll rules — all rules (active + inactive) for management; historical state in rule_set_item.
        # effective_from is matched via rule_set_item by rule_name + rate to handle same-name rules
        # that have different rates across periods.
        rules = db.execute(
            text("""
                SELECT pr.rule_id, pr.rule_name, pr.rule_type,
                       pr.rule_definition_json->>'calculation_method' AS method,
                       pr.is_active,
                       pr.rule_definition_json,
                       MIN(rs.effective_from) AS effective_from
                FROM payroll_rule pr
                LEFT JOIN rule_set_item rsi
                    ON rsi.rule_name = pr.rule_name
                    AND rsi.rule_definition_json->>'rate' IS NOT DISTINCT FROM pr.rule_definition_json->>'rate'
                    AND rsi.rule_definition_json->>'amount' IS NOT DISTINCT FROM pr.rule_definition_json->>'amount'
                LEFT JOIN rule_set rs
                    ON rs.rule_set_id = rsi.rule_set_id
                    AND rs.workspace_id = :wid
                WHERE pr.workspace_id = :wid
                GROUP BY pr.rule_id, pr.rule_name, pr.rule_type, pr.rule_definition_json, pr.is_active
                ORDER BY pr.rule_name, effective_from
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Component overrides — include is_active + proration_strategy columns (post-migration)
        overrides = db.execute(
            text("""
                SELECT component_code, overrides_json, is_active, proration_strategy
                FROM client_component_metadata WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        def _components_to_list(components_jsonb: dict) -> list:
            """Convert {CODE: amount_or_dict} → [{component_name, amount}]."""
            out = []
            for code, val in (components_jsonb or {}).items():
                amount = val.get("amount", val) if isinstance(val, dict) else val
                try:
                    amount = float(Decimal(str(amount)))
                except (TypeError, ValueError):
                    amount = 0.0
                out.append({"component_name": code, "amount": amount})
            return out

        return {
            "workspace": {
                "id": str(ws[0]),
                "name": ws[1],
                "country_code": ws[2],
                "currency_code": ws[3],
                "status": ws[4],
            },
            "pay_cycle": {
                "frequency": pc[0],
                "run_day": pc[1],
                "cutoff_day": pc[2],
                "payment_day": pc[3],
            } if pc else None,
            "grades": [
                {"code": r[0], "description": r[1]} for r in grades
            ],
            "designations": [
                {"code": r[0], "description": r[1]} for r in designations
            ],
            "salary_definitions": [
                {
                    "salary_definition_id": str(r[0]),
                    "name": r[1],
                    "code": r[2],
                    "components": _components_to_list(r[3]),
                }
                for r in sal_defs
            ],
            "payroll_rules": [
                {
                    "rule_id": str(r[0]),
                    "name": r[1],
                    "rule_type": r[2],
                    "method": r[3] or "—",
                    "is_active": r[4],
                    "rule_definition_json": r[5] or {},
                    "effective_from": str(r[6]) if r[6] else None,
                }
                for r in rules
            ],
            "component_overrides": [
                {
                    "component_name": r[0],
                    "overrides_json": r[1] or {},
                    "is_active": r[2] if r[2] is not None else True,
                    "proration_strategy": r[3],
                }
                for r in overrides
            ],
        }
    finally:
        db.close()


@router.patch("/{workspace_id}/component-overrides/{component_code}")
def patch_component_override(workspace_id: str, component_code: str, payload: dict):
    """Update (or create) a component override for a workspace.

    Accepts any subset of: overrides_json, is_active, proration_strategy.
    Uses ON CONFLICT DO UPDATE so repeated calls are idempotent.

    Guards:
    - D-ARCH-2: Statutory deduction components cannot be disabled.
    - D-ARCH-8: component_code must be valid for this workspace's country.
    """
    _VALID_PRORATION_STRATEGIES = {"work_days", "calendar_days", "fixed_30"}
    strategy = payload.get("proration_strategy")
    if strategy is not None and strategy not in _VALID_PRORATION_STRATEGIES:
        raise HTTPException(
            status_code=422,
            detail=f"proration_strategy must be one of {sorted(_VALID_PRORATION_STRATEGIES)}.",
        )

    db = SessionLocal()
    try:
        code_upper = component_code.upper()

        # D-ARCH-8: validate component_code exists for this workspace's country
        country_row = db.execute(
            text("SELECT country_code FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()
        if not country_row:
            raise HTTPException(status_code=404, detail="Workspace not found")
        country_code = country_row[0]

        valid_code = db.execute(
            text("""
                SELECT 1 FROM component_metadata
                WHERE component_code = :code AND country_code = :country
                LIMIT 1
            """),
            {"code": code_upper, "country": country_code},
        ).fetchone()
        if not valid_code:
            raise HTTPException(
                status_code=422,
                detail=f"Component '{code_upper}' is not valid for country '{country_code}'.",
            )

        # D-ARCH-2: Statutory deduction components cannot be disabled.
        # Guard is intentionally not enforced for now — operators may disable any
        # component per workspace (e.g. NHF, NHIS, Check-Off Dues vary by employer).
        # Re-enable this block to restore the restriction in future.

        has_overrides = "overrides_json" in payload
        db.execute(
            text("""
                INSERT INTO client_component_metadata
                    (workspace_id, component_code, overrides_json, is_active, proration_strategy)
                VALUES
                    (:wid, :code, CAST(:overrides AS jsonb),
                     COALESCE(:is_active, true),
                     :proration)
                ON CONFLICT (workspace_id, component_code) DO UPDATE
                SET overrides_json     = CASE WHEN :has_overrides
                                              THEN EXCLUDED.overrides_json
                                              ELSE client_component_metadata.overrides_json END,
                    is_active          = COALESCE(EXCLUDED.is_active, client_component_metadata.is_active),
                    proration_strategy = COALESCE(EXCLUDED.proration_strategy, client_component_metadata.proration_strategy),
                    updated_at         = NOW()
            """),
            {
                "wid": workspace_id,
                "code": code_upper,
                "overrides": json.dumps(payload.get("overrides_json", {})),
                "is_active": payload.get("is_active"),
                "proration": payload.get("proration_strategy"),
                "has_overrides": has_overrides,
            },
        )
        db.commit()
        return {"status": "ok", "workspace_id": workspace_id, "component_code": code_upper}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Track J — Post-Onboarding Config Management (WC-1 through WC-9)
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


@router.patch("/{workspace_id}/pay-cycle")
def patch_pay_cycle(workspace_id: str, payload: dict):
    """Update the active pay cycle for a workspace (WC-1).

    Guards: D-ARCH-1 (run-state lock), D-ARCH-6 (frequency change mid-year).
    Note: run_day/cutoff_day/payment_day are informational only (D-ARCH-7).
    """
    db = SessionLocal()
    try:
        if not db.execute(
            text("SELECT 1 FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone():
            raise HTTPException(status_code=404, detail="Workspace not found")

        # D-ARCH-1: block while any run is in the lock window
        if _active_run_exists(db, workspace_id):
            raise HTTPException(
                status_code=409,
                detail="Pay cycle cannot be changed while a payroll run is in progress or pending approval.",
            )

        # D-ARCH-6: block frequency change if any PAID run exists this calendar year
        new_freq = payload.get("frequency")
        if new_freq:
            current = db.execute(
                text("SELECT frequency FROM pay_cycle WHERE workspace_id = :wid AND is_active = TRUE LIMIT 1"),
                {"wid": workspace_id},
            ).fetchone()
            if current and current[0] != new_freq:
                paid_this_year = db.execute(
                    text("""
                        SELECT 1 FROM payroll_run
                        WHERE workspace_id = :wid
                          AND status = 'PAID'
                          AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM NOW())
                        LIMIT 1
                    """),
                    {"wid": workspace_id},
                ).fetchone()
                if paid_this_year:
                    raise HTTPException(
                        status_code=409,
                        detail="Pay cycle frequency cannot be changed mid-year. A PAID run for this period exists.",
                    )

        fields = {}
        if new_freq is not None:
            fields["frequency"] = new_freq
        if payload.get("run_day") is not None:
            fields["run_day"] = int(payload["run_day"])
        if payload.get("cutoff_day") is not None:
            fields["cutoff_day"] = int(payload["cutoff_day"])
        if payload.get("payment_day") is not None:
            fields["payment_day"] = int(payload["payment_day"])

        if not fields:
            raise HTTPException(status_code=422, detail="No fields provided to update.")

        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        params = {**fields, "wid": workspace_id}
        db.execute(
            text(f"UPDATE pay_cycle SET {set_clause}, updated_at = NOW() WHERE workspace_id = :wid AND is_active = TRUE"),
            params,
        )
        db.commit()
        return {
            "status": "ok",
            "workspace_id": workspace_id,
            "note": "run_day, cutoff_day, and payment_day are informational only and are not used in payroll calculations.",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.patch("/{workspace_id}/grade/{grade_code}")
def patch_grade(workspace_id: str, grade_code: str, payload: dict):
    """Update a grade description (WC-3). Grade code is immutable."""
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE grade SET description = :desc, updated_at = NOW()
                WHERE workspace_id = :wid AND UPPER(grade_code) = UPPER(:code)
            """),
            {"desc": payload.get("description"), "wid": workspace_id, "code": grade_code},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Grade '{grade_code}' not found.")
        db.commit()
        return {"status": "ok", "workspace_id": workspace_id, "grade_code": grade_code.upper()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.patch("/{workspace_id}/designation/{designation_code}")
def patch_designation(workspace_id: str, designation_code: str, payload: dict):
    """Update a designation description (WC-5). Designation code is immutable."""
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE designation SET description = :desc, updated_at = NOW()
                WHERE workspace_id = :wid AND UPPER(designation_code) = UPPER(:code)
            """),
            {"desc": payload.get("description"), "wid": workspace_id, "code": designation_code},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Designation '{designation_code}' not found.")
        db.commit()
        return {"status": "ok", "workspace_id": workspace_id, "designation_code": designation_code.upper()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.patch("/{workspace_id}/salary-definition/{salary_definition_id}")
def patch_salary_definition(workspace_id: str, salary_definition_id: str, payload: dict):
    """Update components_jsonb for a salary definition (WC-7).

    Guards:
    - D-ARCH-1: edit-lock if any run in SUBMITTED→APPROVED references an employee on this def.
    - D-ARCH-5: workspace isolation via AND workspace_id = :wid.
    - Validation: BASIC, HOUSING, TRANSPORT must be present; all amounts > 0.
    """
    db = SessionLocal()
    try:
        # D-ARCH-5: confirm ownership
        existing = db.execute(
            text("""
                SELECT salary_definition_id FROM salary_definition
                WHERE salary_definition_id = :id AND workspace_id = :wid
            """),
            {"id": salary_definition_id, "wid": workspace_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Salary definition not found.")

        # D-ARCH-1: edit-lock — check for in-flight runs where any employee uses this salary def.
        # Goes payroll_run → employee (workspace match) → employee_contract to avoid joining
        # through payroll_result, which has zero rows for SUBMITTED runs and bypasses the lock.
        blocking = db.execute(
            text("""
                SELECT pr.payroll_run_id, pr.status
                FROM payroll_run pr
                JOIN employee e ON pr.workspace_id = e.workspace_id
                JOIN employee_contract ec ON e.employee_id = ec.employee_id
                WHERE ec.salary_definition_id = :sal_def_id
                  AND pr.workspace_id = :wid
                  AND pr.status IN ('SUBMITTED','PROCESSING','CALCULATED','PARTIAL','APPROVED')
                LIMIT 1
            """),
            {"sal_def_id": salary_definition_id, "wid": workspace_id},
        ).fetchone()
        if blocking:
            raise HTTPException(
                status_code=409,
                detail=f"This salary definition cannot be edited while a payroll run is in progress or pending approval.",
            )

        components = payload.get("components_jsonb", {})
        if not components:
            raise HTTPException(status_code=422, detail="components_jsonb is required.")

        # Normalise: accept list [{component_name, amount}] or dict {CODE: {amount}}
        if isinstance(components, list):
            components = {item["component_name"]: {"amount": item["amount"]} for item in components}

        # Validate mandatory components present
        mandatory = {"BASIC", "HOUSING", "TRANSPORT"}
        missing = mandatory - {k.upper() for k in components}
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Required components missing: {', '.join(sorted(missing))}.",
            )

        # Validate all amounts > 0
        normalised: dict = {}
        for code, val in components.items():
            amount = val.get("amount", val) if isinstance(val, dict) else val
            try:
                amount = float(Decimal(str(amount)))
            except (TypeError, ValueError):
                raise HTTPException(status_code=422, detail=f"Invalid amount for component '{code}'.")
            if amount <= 0:
                raise HTTPException(status_code=422, detail=f"Amount for '{code}' must be greater than zero.")
            normalised[code.upper()] = {"amount": amount}

        db.execute(
            text("""
                UPDATE salary_definition
                SET components_jsonb = CAST(:components AS jsonb), updated_at = NOW()
                WHERE salary_definition_id = :id AND workspace_id = :wid
            """),
            {
                "components": json.dumps(normalised),
                "id": salary_definition_id,
                "wid": workspace_id,
            },
        )
        db.commit()
        return {"status": "ok", "salary_definition_id": salary_definition_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.patch("/{workspace_id}/payroll-rule/{rule_id}")
def patch_payroll_rule(workspace_id: str, rule_id: str, payload: dict):
    """Update a payroll rule's is_active, name, or definition (WC-8/WC-9).

    Note: toggles the source payroll_rule record only. In-progress runs read from
    rule_set_item snapshots and are not affected. Re-publish the rule set for the
    change to take effect on future runs.
    """
    db = SessionLocal()
    try:
        existing = db.execute(
            text("""
                SELECT rule_id FROM payroll_rule
                WHERE rule_id = :rid AND workspace_id = :wid
            """),
            {"rid": rule_id, "wid": workspace_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Payroll rule not found.")

        fields = {}
        if payload.get("is_active") is not None:
            fields["is_active"] = bool(payload["is_active"])
        if payload.get("rule_name") is not None:
            fields["rule_name"] = str(payload["rule_name"])
        if payload.get("rule_definition_json") is not None:
            fields["rule_definition_json"] = json.dumps(payload["rule_definition_json"])

        if not fields:
            raise HTTPException(status_code=422, detail="No fields provided to update.")

        set_parts = []
        params: dict = {"rid": rule_id, "wid": workspace_id}
        for k, v in fields.items():
            if k == "rule_definition_json":
                set_parts.append(f"{k} = CAST(:rule_definition_json AS jsonb)")
            else:
                set_parts.append(f"{k} = :{k}")
            params[k] = v

        set_parts.append("updated_at = NOW()")
        db.execute(
            text(f"UPDATE payroll_rule SET {', '.join(set_parts)} WHERE rule_id = :rid AND workspace_id = :wid"),
            params,
        )
        db.commit()
        return {
            "status": "ok",
            "rule_id": rule_id,
            "note": "Re-publish the rule set for this change to take effect on future runs.",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.delete("/{workspace_id}/payroll-rule/{rule_id}")
def delete_payroll_rule(workspace_id: str, rule_id: str):
    """Delete a payroll rule.

    Safe because rule_set_item snapshots rule content at publish time —
    historical runs are not affected by deleting the source payroll_rule row.
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("DELETE FROM payroll_rule WHERE rule_id = :rid AND workspace_id = :wid"),
            {"rid": rule_id, "wid": workspace_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Payroll rule not found.")
        db.commit()
        return {"status": "ok", "rule_id": rule_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_country_code(workspace_id: str) -> str | None:
    """Return the country_code for a workspace, or raise 404 if not found."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT country_code FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return row[0]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# PH-6 — Workspace Payroll Config
# ---------------------------------------------------------------------------

@router.get("/workspaces/{workspace_id}/payroll-config")
def get_payroll_config(workspace_id: str):
    """Return the active payroll config for a workspace (defaults if none set)."""
    return get_workspace_payroll_config(workspace_id)


class PayrollConfigUpsertSchema(BaseModel):
    effective_from: str
    ph_mode: str | None = None
    ph_rate_code: str | None = None
    saturday_ph_rule: str | None = None
    sunday_ph_rule: str | None = None
    d3_leave_overlap_rule: str | None = None
    d4_absence_rule: str | None = None
    timesheet_enabled: bool | None = None


@router.put("/workspaces/{workspace_id}/payroll-config")
def put_payroll_config(workspace_id: str, payload: PayrollConfigUpsertSchema):
    """Insert or update a versioned payroll config row for a workspace.

    When timesheet_enabled transitions to True and no attendance codes exist yet,
    seeds the workspace from the platform v1 template automatically.
    """
    from backend.infra.repositories import attendance_config_repo as _att_repo

    if payload.timesheet_enabled is True:
        existing_codes = _att_repo.get_all_code_client_codes(workspace_id)
        if not existing_codes:
            _att_repo.seed_from_platform_templates(workspace_id)

    return upsert_workspace_payroll_config(
        workspace_id,
        payload.effective_from,
        ph_mode=payload.ph_mode,
        ph_rate_code=payload.ph_rate_code,
        saturday_ph_rule=payload.saturday_ph_rule,
        sunday_ph_rule=payload.sunday_ph_rule,
        d3_leave_overlap_rule=payload.d3_leave_overlap_rule,
        d4_absence_rule=payload.d4_absence_rule,
        timesheet_enabled=payload.timesheet_enabled,
    )


# ---------------------------------------------------------------------------
# PH-7 — Rate Code Registry
# ---------------------------------------------------------------------------

@router.get("/workspaces/{workspace_id}/rate-codes")
def get_rate_codes(workspace_id: str):
    """Return all active rate codes visible to a workspace.

    Includes both platform seeds (is_platform=True) and workspace-specific rows.
    Workspace rows shadow platform seeds with the same code.
    """
    return list_rate_codes(workspace_id)


class RateCodeCreateSchema(BaseModel):
    code: str
    multiplier: Decimal
    unit: str
    base: str
    description: str | None = None


@router.post("/workspaces/{workspace_id}/rate-codes", status_code=201)
def post_rate_code(workspace_id: str, payload: RateCodeCreateSchema):
    """Create a workspace-specific rate code."""
    try:
        return create_rate_code(
            workspace_id=workspace_id,
            code=payload.code.upper(),
            multiplier=payload.multiplier,
            unit=payload.unit,
            base=payload.base,
            description=payload.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("/workspaces/{workspace_id}/rate-codes/{code}", status_code=200)
def remove_rate_code(workspace_id: str, code: str):
    """Deactivate a workspace-specific rate code.

    Returns 403 if the code is a platform seed (workspace_id IS NULL).
    Returns 404 if the code is not found for this workspace.
    """
    try:
        deleted = delete_rate_code(workspace_id, code.upper())
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Rate code '{code}' not found for this workspace")

    return {"status": "ok", "code": code.upper()}


# ---------------------------------------------------------------------------
# PH-1 — Public Holiday Calendar
# ---------------------------------------------------------------------------

@router.get("/workspaces/{workspace_id}/public-holidays")
def get_public_holidays(
    workspace_id: str,
    year: int | None = Query(default=None, description="Filter by calendar year, e.g. 2026"),
):
    """Return public holidays visible to a workspace.

    Returns both NATIONAL (Tier-1) and WORKSPACE (Tier-2) rows.
    Pass ?year=2026 to filter to a specific calendar year.
    """
    country_code = _get_country_code(workspace_id)
    return list_workspace_holidays(workspace_id, country_code, year=year)


class PublicHolidayCreateSchema(BaseModel):
    date: str          # ISO format: YYYY-MM-DD
    name: str


@router.post("/workspaces/{workspace_id}/public-holidays", status_code=201)
def post_public_holiday(workspace_id: str, payload: PublicHolidayCreateSchema):
    """Add a workspace-specific (Tier-2) public holiday."""
    try:
        return add_workspace_holiday(
            workspace_id=workspace_id,
            holiday_date=payload.date,
            name=payload.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("/workspaces/{workspace_id}/public-holidays/{holiday_id}", status_code=200)
def remove_public_holiday(workspace_id: str, holiday_id: str):
    """Delete a workspace-specific (Tier-2) public holiday.

    Returns 404 if the holiday_id is not found for this workspace.
    National holidays cannot be deleted (they have no holiday_id in the workspace table).
    """
    try:
        deleted = delete_workspace_holiday(holiday_id, workspace_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Holiday not found for this workspace. "
                   "National holidays cannot be deleted via this endpoint.",
        )

    return {"status": "ok", "holiday_id": holiday_id}


# ---------------------------------------------------------------------------
# TM-7 — Attendance Code & Policy Configuration
# ---------------------------------------------------------------------------

from backend.infra.repositories import attendance_config_repo as _att_cfg_repo


def _require_attendance_enabled(workspace_id: str) -> None:
    cfg = get_workspace_payroll_config(workspace_id)
    if not cfg.get("timesheet_enabled"):
        raise HTTPException(
            status_code=400,
            detail="Timesheet is not enabled for this workspace.",
        )


@router.get("/workspaces/{workspace_id}/attendance-codes")
def list_attendance_codes(workspace_id: str):
    """Return all attendance codes for the workspace, joined with their policy rows."""
    _require_attendance_enabled(workspace_id)
    return _att_cfg_repo.get_attendance_codes(workspace_id)


class AttendanceCodeCreateSchema(BaseModel):
    client_code: str = Field(..., max_length=20)
    description: str | None = Field(default=None, max_length=200)
    category: str
    is_active: bool = True
    counts_as_paid: bool = True
    counts_towards_ot_threshold: bool = True
    hours_equivalent: Decimal | None = None
    unit_fraction: Decimal | None = None
    eligible_for_shift_allowance: bool = False
    eligible_for_ot: bool = False


@router.post("/workspaces/{workspace_id}/attendance-codes", status_code=201)
def create_attendance_code(workspace_id: str, payload: AttendanceCodeCreateSchema):
    """Create an attendance code and its policy row atomically.

    Both semantic (code) and pay interpretation (policy) fields are required.
    Returns 400 for invalid policy combinations.
    """
    _require_attendance_enabled(workspace_id)

    valid_categories = {"WORK", "LEAVE", "OT", "SHIFT"}
    if payload.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"category must be one of {sorted(valid_categories)}.",
        )
    if not payload.counts_as_paid and payload.counts_towards_ot_threshold:
        raise HTTPException(
            status_code=400,
            detail="counts_towards_ot_threshold cannot be True when counts_as_paid is False.",
        )
    if payload.hours_equivalent is not None and payload.unit_fraction is not None:
        raise HTTPException(
            status_code=400,
            detail="hours_equivalent and unit_fraction are mutually exclusive.",
        )

    try:
        code_row = _att_cfg_repo.upsert_attendance_code(
            workspace_id,
            payload.client_code.upper(),
            description=payload.description,
            category=payload.category,
            is_active=payload.is_active,
        )
        policy_row = _att_cfg_repo.upsert_attendance_policy(
            workspace_id,
            payload.client_code.upper(),
            counts_as_paid=payload.counts_as_paid,
            counts_towards_ot_threshold=payload.counts_towards_ot_threshold,
            hours_equivalent=payload.hours_equivalent,
            unit_fraction=payload.unit_fraction,
            eligible_for_shift_allowance=payload.eligible_for_shift_allowance,
            eligible_for_ot=payload.eligible_for_ot,
        )
    except Exception as exc:
        import logging as _logging
        _logging.getLogger(__name__).error("create_attendance_code failed: %s", exc)
        raise HTTPException(status_code=400, detail="Failed to create attendance code.")

    return {**code_row, **policy_row}


class AttendanceCodePatchSchema(BaseModel):
    description: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


@router.patch("/workspaces/{workspace_id}/attendance-codes/{client_code}")
def patch_attendance_code(workspace_id: str, client_code: str, payload: dict):
    """Update description or is_active for an attendance code.

    Category is immutable after creation — returns 400 if included in the payload.
    """
    _require_attendance_enabled(workspace_id)

    if "category" in payload:
        raise HTTPException(
            status_code=400,
            detail="attendance code category is immutable after creation.",
        )

    allowed = {"description", "is_active"}
    unknown = set(payload.keys()) - allowed
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown fields: {sorted(unknown)}. Allowed: {sorted(allowed)}.",
        )

    try:
        updated = _att_cfg_repo.upsert_attendance_code(
            workspace_id,
            client_code.upper(),
            **{k: v for k, v in payload.items() if k in allowed},
        )
    except Exception as exc:
        import logging as _logging
        _logging.getLogger(__name__).error("patch_attendance_code failed: %s", exc)
        raise HTTPException(status_code=400, detail="Failed to update attendance code.")

    return updated


class AttendancePolicyPatchSchema(BaseModel):
    counts_as_paid: bool | None = None
    counts_towards_ot_threshold: bool | None = None
    hours_equivalent: Decimal | None = None
    unit_fraction: Decimal | None = None
    eligible_for_shift_allowance: bool | None = None
    eligible_for_ot: bool | None = None


@router.patch("/workspaces/{workspace_id}/attendance-policies/{client_code}")
def patch_attendance_policy(workspace_id: str, client_code: str, payload: AttendancePolicyPatchSchema):
    """Update pay interpretation fields for an attendance policy.

    Returns 400 for invalid combinations (e.g. counts_as_paid=false + counts_towards_ot_threshold=true).
    """
    _require_attendance_enabled(workspace_id)

    update_fields = payload.model_dump(exclude_none=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update.")

    # Validate constraint combinations using the merged state
    existing = _att_cfg_repo.get_attendance_policies_for_derivation(workspace_id)
    existing_policy = existing.get(client_code.upper(), {})
    merged = {**existing_policy, **update_fields}

    if not merged.get("counts_as_paid", True) and merged.get("counts_towards_ot_threshold", False):
        raise HTTPException(
            status_code=400,
            detail="counts_towards_ot_threshold cannot be True when counts_as_paid is False.",
        )
    if merged.get("hours_equivalent") is not None and merged.get("unit_fraction") is not None:
        raise HTTPException(
            status_code=400,
            detail="hours_equivalent and unit_fraction are mutually exclusive.",
        )

    try:
        updated = _att_cfg_repo.upsert_attendance_policy(
            workspace_id,
            client_code.upper(),
            **update_fields,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return updated