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


def publish_rule_sets(db, workspace_id: str, rules: list, created_by: str | None = None) -> list:
    """Group rules by effective_from and publish one rule_set per unique date.

    Each item in `rules` must have: rule_name (or rule_code), rule_definition_json,
    effective_from. rule_type is optional. Rules without effective_from are skipped.

    Returns list of {rule_set_id, effective_from, item_count}.
    Does NOT call db.commit() — caller is responsible for committing.
    """
    import json as _json
    import uuid as _uuid
    from collections import defaultdict
    from sqlalchemy import text

    SYSTEM_ACTOR = "00000000-0000-0000-0000-000000000000"
    actor = created_by or SYSTEM_ACTOR

    groups: dict = defaultdict(list)
    for rule in rules:
        eff = rule.get("effective_from")
        if eff:
            groups[eff].append(rule)

    published = []
    for effective_from, group_rules in groups.items():
        rule_set_id = str(_uuid.uuid4())

        db.execute(
            text("""
                INSERT INTO rule_set (rule_set_id, workspace_id, effective_from, created_by)
                VALUES (:id, :wid, :eff, :by)
            """),
            {"id": rule_set_id, "wid": workspace_id, "eff": effective_from, "by": actor},
        )

        for rule in group_rules:
            defn = rule.get("rule_definition_json") or rule.get("definition") or {}
            db.execute(
                text("""
                    INSERT INTO rule_set_item (rule_set_id, rule_name, rule_definition_json, rule_type)
                    VALUES (:rs_id, :name, CAST(:def AS jsonb), :rtype)
                """),
                {
                    "rs_id": rule_set_id,
                    "name":  rule.get("rule_name") or rule.get("rule_code"),
                    "def":   _json.dumps(defn) if isinstance(defn, dict) else defn,
                    "rtype": rule.get("rule_type"),
                },
            )

        published.append({
            "rule_set_id":    rule_set_id,
            "effective_from": effective_from,
            "item_count":     len(group_rules),
        })

    return published