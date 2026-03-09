from backend.infra.db.models import (
    Workspace,
    PayCycle,
    Grade,
    Designation,
    SalaryDefinition,
    PayrollRule,
    ComponentMetadata,
)


def get_workspace(db, workspace_id):
    return db.query(Workspace).get(workspace_id)


def has_pay_cycle(db, workspace_id):
    return db.query(PayCycle).filter_by(workspace_id=workspace_id).first() is not None


def has_grade(db, workspace_id):
    return db.query(Grade).filter_by(workspace_id=workspace_id).first() is not None


def has_designation(db, workspace_id):
    return db.query(Designation).filter_by(workspace_id=workspace_id).first() is not None


def has_salary_definition(db, workspace_id):
    return db.query(SalaryDefinition).filter_by(workspace_id=workspace_id).first() is not None


def has_active_payroll_rule(db, workspace_id):
    return db.query(PayrollRule).filter_by(
        workspace_id=workspace_id,
        is_active=True,
    ).first() is not None


def has_component_metadata(db, workspace_id):
    workspace = db.query(Workspace).get(workspace_id)
    return db.query(ComponentMetadata).filter_by(
        country_code=workspace.country_code,
        is_active=True,
    ).first() is not None
