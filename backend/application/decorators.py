from functools import wraps
from backend.domain.onboarding.state_inference import infer_and_update_workspace_state


def auto_infer_workspace_state(func):
    """
    Decorator for onboarding service functions.
    Expects:
        - db passed as kwarg or first positional arg
        - workspace_id passed as kwarg or positional arg
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Extract db
        db = kwargs.get("db") or args[0]

        # Extract workspace_id
        workspace_id = kwargs.get("workspace_id")

        if not workspace_id:
            # Assume second positional argument
            workspace_id = args[1]

        # Run original function
        result = func(*args, **kwargs)

        # Auto infer state AFTER successful execution
        infer_and_update_workspace_state(db, workspace_id)

        return result

    return wrapper