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
            version=payload.version,
            rules_jsonb=payload.rules_jsonb,
            effective_from=payload.effective_from,
        )
    finally:
        db.close()