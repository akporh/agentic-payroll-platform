from typing import Dict, List
from backend.infra.db.models import Workspace

ALLOWED_TRANSITIONS = {
    "DRAFT": ["STRUCTURE_DEFINED"],
    "STRUCTURE_DEFINED": ["COMPENSATION_DEFINED"],
    "COMPENSATION_DEFINED": ["RULES_DEFINED"],
    "RULES_DEFINED": ["READY"],
    "READY": ["LIVE"],
    "LIVE": [],
}


class InvalidTransition(Exception):
    pass


class WorkspaceNotFound(Exception):
    pass


def transition_workspace(db, workspace_id: str, target_state: str, validator):
    workspace = db.query(Workspace).get(workspace_id)

    if not workspace:
        raise WorkspaceNotFound("Workspace not found")

    current_state = workspace.status

    if target_state not in ALLOWED_TRANSITIONS.get(current_state, []):
        raise InvalidTransition(
            f"Cannot transition from {current_state} to {target_state}"
        )

    # Run readiness validation before transition
    validator(db, workspace_id, target_state)

    workspace.status = target_state
    db.commit()

    return {
        "workspace_id": workspace_id,
        "from": current_state,
        "to": target_state,
    }