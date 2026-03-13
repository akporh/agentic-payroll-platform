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


# Map each status to the numeric level it represents.
# Prerequisites for a state are only reported as missing if the workspace
# has not yet reached or passed that state.
_STATUS_LEVEL = {
    "DRAFT": 0,
    "STRUCTURE_DEFINED": 1,
    "COMPENSATION_DEFINED": 2,
    "RULES_DEFINED": 3,
    "READY": 4,
    "LIVE": 5,
}


def get_onboarding_status(db, workspace_id: str):

    workspace = get_workspace(db, workspace_id)

    if not workspace:
        raise Exception("Workspace not found")

    level = _STATUS_LEVEL.get(workspace.status, 0)
    missing = []

    # Only check a prerequisite if the workspace hasn't already passed
    # the state that requires it.  A workspace at READY or LIVE has
    # definitionally satisfied all prior prerequisites.

    # STRUCTURE_DEFINED prerequisites (level 1)
    if level < 1:
        if not pay_cycle_exists(db, workspace_id):
            missing.append("pay_cycle")
        if not grade_exists(db, workspace_id):
            missing.append("grade")
        if not designation_exists(db, workspace_id):
            missing.append("designation")

    # COMPENSATION_DEFINED prerequisite (level 2)
    if level < 2:
        if not salary_definition_exists(db, workspace_id):
            missing.append("salary_definition")

    # RULES_DEFINED prerequisite (level 3)
    if level < 3:
        if not active_payroll_rule_exists(db, workspace_id):
            missing.append("payroll_rule")

    # READY prerequisite (level 4)
    if level < 4:
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
