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
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal
from fastapi import APIRouter, Request

from backend.domain.onboarding.loader import emit_onboarding_sql
from backend.domain.onboarding.workspace_state_machine import transition_workspace
from backend.domain.onboarding.hard_validator import validate_workspace_for_state
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

        workspace_id = payload.get("workspace_id", "")

        if not workspace_id:
            return {
                "status": "error",
                "message": "Missing workspace_id",
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
        # Keyed by both name and code so employees can be linked either way.
        # ----------------------------
        salary_def_id_map: dict[str, str] = {}

        for sd in payload.get("salary_definitions", []):
            new_id = str(uuid4())
            sd_name = sd.get("name", "UNKNOWN")
            sd_code = sd.get("code") or sd_name.upper().replace(" ", "_")

            # Register under both name and code for flexible employee lookup
            salary_def_id_map[sd_name] = new_id
            salary_def_id_map[sd_code] = new_id

            db.execute(
                text("""
                    INSERT INTO salary_definition (
                        salary_definition_id,
                        workspace_id,
                        code,
                        name,
                        components_jsonb
                    )
                    VALUES (
                        :id,
                        :workspace_id,
                        :code,
                        :name,
                        :components
                    )
                """),
                {
                    "id": new_id,
                    "workspace_id": workspace_id,
                    "code": sd_code,
                    "name": sd_name,
                    "components": Json(sd.get("components", {})),
                },
            )

        # Also load any pre-existing salary definitions for this workspace
        # so Excel-uploaded employees can link to them by code.
        existing_rows = db.execute(
            text("""
                SELECT salary_definition_id, name, code
                FROM salary_definition
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()
        for row in existing_rows:
            existing_id = str(row[0])
            if row[1] and row[1] not in salary_def_id_map:
                salary_def_id_map[row[1]] = existing_id  # by name
            if row[2] and row[2] not in salary_def_id_map:
                salary_def_id_map[row[2]] = existing_id  # by code

        # ----------------------------
        # INSERT PAYROLL RULES
        # ----------------------------
        for rule in payload.get("payroll_rules", []):
            db.execute(
                text("""
                    INSERT INTO payroll_rule (
                        rule_id, workspace_id, rule_name, rule_definition_json, is_active
                    )
                    VALUES (:id, :workspace_id, :name, :definition, TRUE)
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "name": rule.get("rule_name") or rule.get("rule_code") or "UNKNOWN",
                    "definition": Json(
                        rule.get("definition") or rule.get("rule_definition_json") or {}
                    ),
                },
            )

        # ----------------------------
        # INSERT STRUCTURE: PAY CYCLE
        # Accepts flat {frequency, run_day, ...} or definition_json
        # {execution_window: {run_day, ...}} format.
        # ----------------------------
        structure = payload.get("structure", {})
        pay_cycle_data = structure.get("pay_cycle", {}) if isinstance(structure, dict) else {}
        if pay_cycle_data and isinstance(pay_cycle_data, dict):
            execution_window = pay_cycle_data.get("execution_window") or {}
            frequency   = pay_cycle_data.get("frequency") or "monthly"
            run_day     = int(pay_cycle_data.get("run_day")     or execution_window.get("run_day", 1))
            cutoff_day  = int(pay_cycle_data.get("cutoff_day")  or execution_window.get("adjustment_cutoff_day", 1))
            payment_day = int(pay_cycle_data.get("payment_day") or execution_window.get("payment_day", 1))
            definition_json = pay_cycle_data.get("definition_json") or pay_cycle_data
            db.execute(
                text("""
                    INSERT INTO pay_cycle (
                        pay_cycle_id, workspace_id, frequency,
                        run_day, cutoff_day, payment_day, is_active, definition_json
                    )
                    VALUES (
                        :id, :workspace_id, :frequency,
                        :run_day, :cutoff_day, :payment_day, TRUE, :definition_json
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "frequency": frequency,
                    "run_day": run_day,
                    "cutoff_day": cutoff_day,
                    "payment_day": payment_day,
                    "definition_json": Json(definition_json),
                },
            )

        # ----------------------------
        # INSERT STRUCTURE: GRADES
        # Build a code→id map so employee contracts can reference them.
        # ----------------------------
        grades = structure.get("grades", []) if isinstance(structure, dict) else []
        for grade in grades:
            grade_code = grade.get("grade_code") or grade.get("code") or grade.get("name")
            if not grade_code:
                continue
            db.execute(
                text("""
                    INSERT INTO grade (grade_id, workspace_id, grade_code, description)
                    VALUES (:id, :workspace_id, :grade_code, :description)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "grade_code": grade_code,
                    "description": grade.get("description"),
                },
            )

        # ----------------------------
        # INSERT STRUCTURE: DESIGNATIONS
        # ----------------------------
        designations = structure.get("designations", []) if isinstance(structure, dict) else []
        for desig in designations:
            desig_code = desig.get("designation_code") or desig.get("code") or desig.get("name")
            if not desig_code:
                continue
            db.execute(
                text("""
                    INSERT INTO designation (designation_id, workspace_id, designation_code, description)
                    VALUES (:id, :workspace_id, :designation_code, :description)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "designation_code": desig_code,
                    "description": desig.get("description"),
                },
            )

        # Build grade and designation code→id maps from all DB rows for this
        # workspace (covers both newly inserted and pre-existing records).
        grade_id_map: dict[str, str] = {}
        for row in db.execute(
            text("SELECT grade_id, grade_code FROM grade WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall():
            grade_id_map[str(row[1]).upper()] = str(row[0])

        designation_id_map: dict[str, str] = {}
        for row in db.execute(
            text("SELECT designation_id, designation_code FROM designation WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall():
            designation_id_map[str(row[1]).upper()] = str(row[0])

        # ----------------------------
        # INSERT EMPLOYEES + CONTRACTS
        # Grade and designation are resolved by code from the maps above.
        # ----------------------------
        for emp in payload.get("employees", []):

            employee_id = str(uuid4())
            biodata = emp.get("biodata", {})
            full_name = (
                emp.get("full_name")
                or biodata.get("FULL_NAME")
                or emp.get("employee_number", "UNKNOWN")
            )
            emp_number = emp.get("employee_number") or emp.get("employee_id")

            db.execute(
                text("""
                    INSERT INTO employee (
                        employee_id, workspace_id, full_name,
                        employee_number, personal_details_encrypted, status
                    )
                    VALUES (
                        :eid, :workspace_id, :name,
                        :employee_number, :biodata, 'ACTIVE'
                    )
                """),
                {
                    "eid": employee_id,
                    "workspace_id": workspace_id,
                    "name": full_name,
                    "employee_number": emp_number,
                    "biodata": Json(biodata),
                },
            )

            # Resolve salary definition: prefer code, fall back to name.
            sd_code = emp.get("salary_definition_code")
            sd_name = emp.get("salary_definition_name")
            salary_definition_id = (
                salary_def_id_map.get(sd_code)
                if sd_code
                else salary_def_id_map.get(sd_name)
            )

            if not salary_definition_id:
                ref = sd_code or sd_name or "(none)"
                raise Exception(
                    f"Employee '{emp_number}': salary definition '{ref}' not found"
                )

            # Resolve grade and designation FKs by code (uppercase for consistency)
            emp_grade = str(emp.get("grade") or "").upper()
            emp_desig = str(emp.get("designation") or "").upper()
            grade_id       = grade_id_map.get(emp_grade)
            designation_id = designation_id_map.get(emp_desig)

            db.execute(
                text("""
                    INSERT INTO employee_contract (
                        contract_id, employee_id, salary_definition_id,
                        grade_id, designation_id, start_date
                    )
                    VALUES (
                        :cid, :employee_id, :salary_definition_id,
                        :grade_id, :designation_id, CURRENT_DATE
                    )
                """),
                {
                    "cid": str(uuid4()),
                    "employee_id": employee_id,
                    "salary_definition_id": salary_definition_id,
                    "grade_id": grade_id,
                    "designation_id": designation_id,
                },
            )

        db.commit()

        # ----------------------------
        # AUTO-ADVANCE STATE MACHINE
        # Attempt each transition in order; stop at the first one that fails.
        # This advances the workspace as far as its data allows.
        # ----------------------------
        for target_state in ["STRUCTURE_DEFINED", "COMPENSATION_DEFINED", "RULES_DEFINED", "READY"]:
            try:
                transition_workspace(db, workspace_id, target_state, validate_workspace_for_state)
            except Exception:
                break

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
