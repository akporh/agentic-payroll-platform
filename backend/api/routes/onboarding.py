"""
Onboarding upload route.

Accepts a full client JSON payload and delegates to the existing
onboarding loader. No business logic lives here — validation and
SQL generation happen in the domain layer.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

from fastapi import APIRouter, Request

from backend.domain.onboarding.loader import emit_onboarding_sql

router = APIRouter()


@router.post("/onboarding/upload")
async def upload_onboarding(request: Request):
    """Accept a full onboarding JSON payload and process it.

    Extracts workspace_id from the payload and passes the entire
    payload to the existing onboarding loader as-is. Returns the
    loader's structured response (status, review, SQL).

    No business logic here — all validation and SQL generation
    is handled by the domain layer.
    """
    try:
        payload = await request.json()

        workspace = payload.get("workspace", {})
        workspace_id = workspace.get("workspace_id", "")

        if not workspace_id:
            return {
                "status": "error",
                "message": "Missing workspace_id in workspace object",
            }

        result = emit_onboarding_sql(workspace_id, payload)

        if result["status"] == "BLOCKED":
            return {
                "status": "error",
                "message": "Onboarding blocked by validation",
                "review": result["review"],
            }

        return {
            "status": "success",
            "message": "Onboarding completed",
            "review": result["review"],
            "sql": result["sql"],
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
