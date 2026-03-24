import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from backend.infra.db.session import SessionLocal
from backend.application import onboarding_service
from backend.api.schemas.pay_cycle import PayCycleCreateSchema
from backend.api.schemas.grade import GradeCreateSchema
from backend.api.schemas.designation import DesignationCreateSchema
from backend.api.schemas.salary_definition import SalaryDefinitionCreateSchema
from backend.api.schemas.payroll_rule import PayrollRuleCreateSchema
from backend.api.schemas.component_metadata import ComponentMetadataCreateSchema
from backend.domain.onboarding.onboarding_status import get_onboarding_status
from backend.domain.onboarding.workspace_state_machine import transition_workspace
from backend.domain.onboarding.hard_validator import validate_workspace_for_state


router = APIRouter()


class WorkspaceCreateSchema(BaseModel):
    name: str
    country_code: str
    base_currency: str = "NGN"


@router.post("/workspace")
def create_workspace(payload: WorkspaceCreateSchema):
    db = SessionLocal()
    try:
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
                    ec.start_date        AS contract_start
                FROM employee e
                LEFT JOIN employee_contract ec
                    ON ec.employee_id = e.employee_id
                    AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
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
            }
            for row in rows
        ]
    finally:
        db.close()


class EmployeeContractUpdateSchema(BaseModel):
    grade_code: str | None = None
    designation_code: str | None = None


@router.patch("/{workspace_id}/employees/{employee_id}/contract")
def update_employee_contract(
    workspace_id: str, employee_id: str, payload: EmployeeContractUpdateSchema
):
    db = SessionLocal()
    try:
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

        db.execute(
            text("""
                UPDATE employee_contract
                SET grade_id       = COALESCE(:grade_id::uuid, grade_id),
                    designation_id = COALESCE(:designation_id::uuid, designation_id)
                WHERE employee_id = :eid
                  AND (end_date IS NULL OR end_date >= CURRENT_DATE)
            """),
            {"grade_id": grade_id, "designation_id": designation_id, "eid": employee_id},
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
                VALUES (gen_random_uuid(), :wid, :code, :name, '{}'::jsonb)
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
    db = SessionLocal()
    try:
        return onboarding_service.create_salary_definition(
            db=db,
            workspace_id=workspace_id,
            name=payload.name,
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
                  AND component_class = 'statutory_deduction'
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
                SELECT component_code, overrides_json
                FROM client_component_metadata
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "component_code": row[0],
                "overrides_json": row[1],
                "is_active": True,
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

        # Salary definitions
        sal_defs = db.execute(
            text("""
                SELECT name, code, components_jsonb
                FROM salary_definition WHERE workspace_id = :wid ORDER BY code
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Payroll rules
        rules = db.execute(
            text("""
                SELECT rule_name, rule_type,
                       rule_definition_json->>'calculation_method' AS method
                FROM payroll_rule
                WHERE workspace_id = :wid AND is_active = TRUE
                ORDER BY rule_name
            """),
            {"wid": workspace_id},
        ).fetchall()

        # Component overrides
        overrides = db.execute(
            text("""
                SELECT component_code, overrides_json
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
                    amount = float(amount)
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
                    "name": r[0],
                    "code": r[1],
                    "components": _components_to_list(r[2]),
                }
                for r in sal_defs
            ],
            "payroll_rules": [
                {"name": r[0], "rule_type": r[1], "method": r[2] or "—"} for r in rules
            ],
            "component_overrides": [
                {
                    "component_name": r[0],
                    "is_active": (r[1] or {}).get("is_active", True),
                }
                for r in overrides
            ],
        }
    finally:
        db.close()