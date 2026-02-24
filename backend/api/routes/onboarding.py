"""
Onboarding routes.

Exposes upload and preview endpoints for the onboarding pipeline.
No business logic lives here — validation, review, and SQL generation
happen in the domain layer.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

from fastapi import APIRouter, Request

from backend.domain.onboarding.loader import emit_onboarding_sql
from backend.domain.onboarding.sql_emitter import (
    emit_employees_sql,
    emit_salary_definitions_sql,
    emit_payroll_rules_sql,
)
from backend.domain.onboarding.review_runner import review_client_onboarding

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


@router.post("/onboarding/preview")
async def preview_onboarding(request: Request):
    """Generate a SQL preview for an onboarding payload.

    Validates the payload first using the existing review pipeline.
    If invalid, returns validation errors. If valid, generates
    structured SQL statements for each entity type without executing
    anything.

    No DB writes. No execution. Preview only.
    """
    try:
        payload = await request.json()
    except Exception:
        return {
            "status": "invalid",
            "errors": [{"field": "body", "message": "Invalid JSON payload"}],
            "warnings": [],
        }

    workspace_id = payload.get("workspace_id", "")
    if not workspace_id:
        return {
            "status": "invalid",
            "errors": [{"field": "workspace_id", "message": "Missing workspace_id"}],
            "warnings": [],
        }

    try:
        review = review_client_onboarding(payload)

        warnings = []
        if review.get("ai_review", {}).get("warnings"):
            warnings = review["ai_review"]["warnings"]

        if review["hard_validation"]["status"] == "FAIL":
            errors = [
                {"field": e.get("category", "unknown"), "message": e["message"]}
                for e in review["hard_validation"]["errors"]
            ]
            return {
                "status": "invalid",
                "errors": errors,
                "warnings": warnings,
            }

        employees = payload.get("employees", [])
        salary_definitions = payload.get("salary_definitions", [])
        payroll_rules = payload.get("payroll_rules", [])

        return {
            "status": "valid",
            "warnings": warnings,
            "preview": {
                "employees_sql": emit_employees_sql(workspace_id, employees),
                "salary_definitions_sql": emit_salary_definitions_sql(
                    workspace_id, salary_definitions
                ),
                "payroll_rules_sql": emit_payroll_rules_sql(
                    workspace_id, payroll_rules
                ),
            },
        }

    except Exception as e:
        return {
            "status": "invalid",
            "errors": [{"field": "internal", "message": str(e)}],
            "warnings": [],
        }
