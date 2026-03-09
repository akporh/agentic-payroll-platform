from backend.domain.onboarding.workspace_state_machine import ALLOWED_TRANSITIONS
from backend.infra.db.repositories.workspace_repo import (
    get_workspace,
    has_pay_cycle,
    has_grade,
    has_designation,
    has_salary_definition,
    has_active_payroll_rule,
    has_component_metadata,
)


def get_onboarding_status(db, workspace_id: str):

    workspace = get_workspace(db, workspace_id)

    if not workspace:
        raise Exception("Workspace not found")

    missing = []

    # STRUCTURE
    if not pay_cycle_exists(db, workspace_id):
        missing.append("pay_cycle")

    if not grade_exists(db, workspace_id):
        missing.append("grade")

    if not designation_exists(db, workspace_id):
        missing.append("designation")

    # COMPENSATION
    if not salary_definition_exists(db, workspace_id):
        missing.append("salary_definition")

    # RULES
    if not active_payroll_rule_exists(db, workspace_id):
        missing.append("payroll_rule")

    # COMPONENT METADATA
    if not component_metadata_exists(db, workspace_id):
        missing.append("component_metadata")

    progress = calculate_progress(missing)

    return {
        "status": workspace.status,
        "progress_percent": progress,
        "missing": missing,
        "next_allowed_states": ALLOWED_TRANSITIONS.get(workspace.status, [])
    }


def calculate_progress(missing: list):

    total_checks = 6  # adjust if you add more
    completed = total_checks - len(missing)

    return int((completed / total_checks) * 100)


def pay_cycle_exists(db, workspace_id):
    return has_pay_cycle(db, workspace_id)


def grade_exists(db, workspace_id):
    return has_grade(db, workspace_id)


def designation_exists(db, workspace_id):
    return has_designation(db, workspace_id)


def salary_definition_exists(db, workspace_id):
    return has_salary_definition(db, workspace_id)


def active_payroll_rule_exists(db, workspace_id):
    return has_active_payroll_rule(db, workspace_id)


def component_metadata_exists(db, workspace_id):
    return has_component_metadata(db, workspace_id)
