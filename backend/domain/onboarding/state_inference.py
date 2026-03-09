from backend.domain.onboarding.workspace_state_machine import ALLOWED_TRANSITIONS
from backend.domain.onboarding.onboarding_status import get_onboarding_status
from backend.infra.db.repositories.workspace_repo import get_workspace


def infer_and_update_workspace_state(db, workspace_id: str):

    workspace = get_workspace(db, workspace_id)

    if not workspace:
        raise Exception("Workspace not found")

    status_data = get_onboarding_status(db, workspace_id)

    current_state = workspace.status
    missing = status_data["missing"]

    # Determine highest valid state
    if not missing:
        new_state = "READY"
    elif "component_metadata" not in missing:
        new_state = "RULES_DEFINED"
    elif "payroll_rule" not in missing:
        new_state = "COMPENSATION_DEFINED"
    elif "salary_definition" not in missing:
        new_state = "STRUCTURE_DEFINED"
    else:
        new_state = "DRAFT"

    if new_state in ALLOWED_TRANSITIONS.get(current_state, []):
        workspace.status = new_state
        db.commit()

    return {
        "old_state": current_state,
        "new_state": workspace.status
    }