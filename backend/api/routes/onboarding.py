"""
Onboarding routes.

Exposes upload and preview endpoints for the onboarding pipeline.
No business logic lives here — validation, review, and SQL generation
happen in the domain layer.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import text
from backend.infra.db.session import SessionLocal
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



@router.post("/onboarding/commit")
async def commit_onboarding(request: Request):
    """
    Commit a validated onboarding payload to the database.

    Re-runs validation before committing.
    Uses a single atomic transaction.
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

    # 🔎 Re-run validation (never trust preview)
    review = review_client_onboarding(payload)

    warnings = review.get("ai_review", {}).get("warnings", [])

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

    db = SessionLocal()

    try:
        # Ensure workspace exists
        exists = db.execute(
            text("SELECT 1 FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id}
        ).scalar()

        if not exists:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # ----------------------------
        # INSERT SALARY DEFINITIONS
        # ----------------------------
        salary_def_id_map = {}

        for sd in payload.get("salary_definitions", []):
            new_id = str(uuid4())
            salary_def_id_map[sd["name"]] = new_id

            db.execute(
                text("""
                    INSERT INTO salary_definition (
                        salary_definition_id,
                        workspace_id,
                        name,
                        components_jsonb
                    )
                    VALUES (
                        :id,
                        :workspace_id,
                        :name,
                        :components
                    )
                """),
                {
                    "id": new_id,
                    "workspace_id": workspace_id,
                    "name": sd["name"],
                    "components": sd["components"],
                },
            )

        # ----------------------------
        # INSERT PAYROLL RULES
        # ----------------------------
        for rule in payload.get("payroll_rules", []):
            db.execute(
                text("""
                    INSERT INTO payroll_rule (
                        rule_id,
                        workspace_id,
                        rule_name,
                        rule_definition_json,
                        is_active
                    )
                    VALUES (
                        :id,
                        :workspace_id,
                        :name,
                        :definition,
                        TRUE
                    )
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "name": rule["rule_name"],
                    "definition": rule["definition"],
                },
            )

        # ----------------------------
        # INSERT EMPLOYEES + CONTRACTS
        # ----------------------------
        for emp in payload.get("employees", []):

            employee_id = str(uuid4())

            db.execute(
                text("""
                    INSERT INTO employee (
                        employee_id,
                        workspace_id,
                        full_name,
                        status
                    )
                    VALUES (
                        :eid,
                        :workspace_id,
                        :name,
                        'ACTIVE'
                    )
                """),
                {
                    "eid": employee_id,
                    "workspace_id": workspace_id,
                    "name": emp["full_name"],
                },
            )

            # Link to salary definition by name
            salary_definition_id = salary_def_id_map.get(
                emp["salary_definition_name"]
            )

            if not salary_definition_id:
                raise Exception(
                    f"Salary definition '{emp['salary_definition_name']}' not found"
                )

            db.execute(
                text("""
                    INSERT INTO employee_contract (
                        contract_id,
                        employee_id,
                        salary_definition_id,
                        start_date
                    )
                    VALUES (
                        :cid,
                        :employee_id,
                        :salary_definition_id,
                        CURRENT_DATE
                    )
                """),
                {
                    "cid": str(uuid4()),
                    "employee_id": employee_id,
                    "salary_definition_id": salary_definition_id,
                },
            )

        db.commit()

        return {
            "status": "success",
            "message": "Onboarding committed successfully",
            "warnings": warnings,
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
        }

    finally:
        db.close()
