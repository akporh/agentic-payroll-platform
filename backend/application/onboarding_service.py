from backend.application.decorators import auto_infer_workspace_state
from backend.infra.db.models import (
    PayCycle,
    Designation,
    Grade,
    SalaryDefinition,
    PayrollRule,
    ClientComponentMetadata,
    Workspace,
)


@auto_infer_workspace_state
def create_pay_cycle(db, workspace_id: str, frequency: str, run_day: int, cutoff_day: int, payment_day: int, definition_json: dict | None = None):

    pay_cycle = PayCycle(
        workspace_id=workspace_id,
        frequency=frequency,
        run_day=run_day,
        cutoff_day=cutoff_day,
        payment_day=payment_day,
        is_active=True,
        definition_json=definition_json,
    )

    db.add(pay_cycle)
    db.commit()

    return pay_cycle


@auto_infer_workspace_state
def create_designation(db, workspace_id: str, designation_code: str, description: str | None = None):

    designation = Designation(
        workspace_id=workspace_id,
        designation_code=designation_code,
        description=description,
    )

    db.add(designation)
    db.commit()

    return designation


@auto_infer_workspace_state
def create_grade(db, workspace_id: str, grade_code: str, description: str | None = None):

    grade = Grade(
        workspace_id=workspace_id,
        grade_code=grade_code,
        description=description,
    )

    db.add(grade)
    db.commit()

    return grade


@auto_infer_workspace_state
def create_salary_definition(
    db,
    workspace_id: str,
    name: str,
    components_jsonb: dict,
    effective_from=None,
    effective_to=None,
):

    salary_definition = SalaryDefinition(
        workspace_id=workspace_id,
        name=name,
        components_jsonb=components_jsonb,
        effective_from=effective_from,
        effective_to=effective_to,
    )

    db.add(salary_definition)
    db.commit()

    return salary_definition



@auto_infer_workspace_state
def create_payroll_rule(
    db,
    workspace_id: str,
    rule_name: str,
    rule_definition_json: dict,
    rule_type: str,
):

    payroll_rule = PayrollRule(
        workspace_id=workspace_id,
        rule_name=rule_name,
        rule_definition_json=rule_definition_json,
        rule_type=rule_type,
        is_active=True,
    )

    db.add(payroll_rule)
    db.commit()

    return payroll_rule



@auto_infer_workspace_state
def create_component_metadata(
    db,
    workspace_id: str,
    component_code: str,
    overrides_json: dict,
):
    import json
    from sqlalchemy import text

    result = db.execute(
        text("""
            INSERT INTO client_component_metadata
                (client_component_metadata_id, workspace_id, component_code, overrides_json)
            VALUES (gen_random_uuid(), :wid, :code, CAST(:overrides AS jsonb))
            ON CONFLICT (workspace_id, component_code)
            DO UPDATE SET overrides_json = EXCLUDED.overrides_json
            RETURNING client_component_metadata_id, workspace_id, component_code, overrides_json
        """),
        {
            "wid": workspace_id,
            "code": component_code,
            "overrides": json.dumps(overrides_json),
        },
    ).fetchone()

    db.commit()

    return {
        "client_component_metadata_id": str(result[0]),
        "workspace_id": str(result[1]),
        "component_code": result[2],
        "overrides_json": result[3],
    }