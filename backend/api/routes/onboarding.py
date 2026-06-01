"""
Onboarding routes.

Exposes upload and preview endpoints for the onboarding pipeline.
No business logic lives here — validation, review, and SQL generation
happen in the domain layer.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""
import logging
from datetime import date as _date
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal

logger = logging.getLogger(__name__)

from backend.domain.onboarding.loader import emit_onboarding_sql
from backend.domain.onboarding.workspace_state_machine import transition_workspace
from backend.domain.onboarding.hard_validator import validate_workspace_for_state
from backend.domain.onboarding.sql_emitter import (
    emit_employees_sql,
    emit_salary_definitions_sql,
    emit_payroll_rules_sql,
)
from backend.domain.onboarding.review_runner import review_client_onboarding
from backend.application import onboarding_service
from backend.infra.repositories.workspace_config_repo import upsert_workspace_payroll_config
from backend.infra.repositories.employee_repo import insert_employee, insert_employee_contract

router = APIRouter()

# S2 — Enum allowlists for workspace_payroll_config fields (must match DB check constraints)
_WPC_PH_MODE_VALUES            = frozenset({"AUTOMATIC", "FILE_BASED"})
_WPC_PH_RULE_VALUES            = frozenset({"PH_TAKES_PRECEDENCE", "DAY_OF_WEEK_TAKES_PRECEDENCE"})
_WPC_D3_LEAVE_OVERLAP_VALUES   = frozenset({"LEAVE_ABSORBS_PH", "PH_ADDITIVE"})
_WPC_D4_ABSENCE_RULE_VALUES    = frozenset({"ABSENT_IS_DEDUCTIBLE", "PH_EXCUSES_ABSENCE"})

_WPC_ENUM_FIELDS = [
    ("ph_mode",              _WPC_PH_MODE_VALUES),
    ("saturday_ph_rule",     _WPC_PH_RULE_VALUES),
    ("sunday_ph_rule",       _WPC_PH_RULE_VALUES),
    ("d3_leave_overlap_rule", _WPC_D3_LEAVE_OVERLAP_VALUES),
    ("d4_absence_rule",      _WPC_D4_ABSENCE_RULE_VALUES),
]


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
            sd_name = sd.get("name", "UNKNOWN")
            sd_code = sd.get("code") or sd_name.upper().replace(" ", "_")

            row = db.execute(
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
                    ON CONFLICT (workspace_id, name)
                    DO UPDATE SET
                        code            = EXCLUDED.code,
                        components_jsonb = EXCLUDED.components_jsonb
                    RETURNING salary_definition_id
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "code": sd_code,
                    "name": sd_name,
                    "components": Json(sd.get("components", {})),
                },
            ).first()

            actual_id = str(row[0])
            # Register under both name and code for flexible employee lookup
            salary_def_id_map[sd_name] = actual_id
            salary_def_id_map[sd_code] = actual_id

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
                        rule_id, workspace_id, rule_name, rule_definition_json, rule_type, is_active
                    )
                    VALUES (:id, :workspace_id, :name, :definition, :rule_type, TRUE)
                """),
                {
                    "id": str(uuid4()),
                    "workspace_id": workspace_id,
                    "name": rule.get("rule_name") or rule.get("rule_code") or "UNKNOWN",
                    "definition": Json(
                        rule.get("definition") or rule.get("rule_definition_json") or {}
                    ),
                    "rule_type": rule.get("rule_type"),
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
            definition_json = pay_cycle_data.get("definition_json") or {}
            execution_window = (
                pay_cycle_data.get("execution_window")
                or definition_json.get("execution_window")
                or {}
            )
            frequency   = pay_cycle_data.get("frequency") or "monthly"
            run_day     = int(pay_cycle_data.get("run_day")     or execution_window.get("run_day", 1))
            cutoff_day  = int(pay_cycle_data.get("cutoff_day")  or execution_window.get("adjustment_cutoff_day", 1))
            payment_day = int(pay_cycle_data.get("payment_day") or execution_window.get("payment_day", 1))
            definition_json = definition_json or pay_cycle_data
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

        # ----------------------------
        # INSERT STRUCTURE: COMPONENT OVERRIDES
        # Optional — upserts per-component proration_strategy (and other
        # calculations_behaviour flags) into client_component_metadata.
        # ----------------------------
        component_overrides = structure.get("component_overrides", []) if isinstance(structure, dict) else []
        for co in component_overrides:
            comp_code = str(co.get("component_code") or "").strip().upper()
            if not comp_code:
                continue
            proration_strategy = str(co.get("proration_strategy") or "").strip().lower()
            overrides_json: dict = {}
            if proration_strategy:
                overrides_json["calculations_behaviour"] = {"proration_strategy": proration_strategy}
            db.execute(
                text("""
                    INSERT INTO client_component_metadata (
                        workspace_id, component_code, overrides_json
                    )
                    VALUES (:wid, :code, :overrides)
                    ON CONFLICT (workspace_id, component_code)
                    DO UPDATE SET overrides_json = EXCLUDED.overrides_json
                """),
                {
                    "wid":      workspace_id,
                    "code":     comp_code,
                    "overrides": Json(overrides_json),
                },
            )

        # Build grade and designation code→id maps from all DB rows for this
        # workspace (covers both newly inserted and pre-existing records).
        grade_id_map: dict[str, str] = {}
        for row in db.execute(
            text("SELECT grade_id, grade_code FROM grade WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall():
            key_upper = str(row[1]).upper()
            grade_id_map[key_upper] = str(row[0])
            # Also index by spaces→underscores so frontend-normalized codes match
            # e.g. "STEP 1_Driver" → "STEP_1_DRIVER"
            key_norm = key_upper.replace(" ", "_")
            grade_id_map.setdefault(key_norm, str(row[0]))

        designation_id_map: dict[str, str] = {}
        for row in db.execute(
            text("SELECT designation_id, designation_code FROM designation WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall():
            key_upper = str(row[1]).upper()
            designation_id_map[key_upper] = str(row[0])
            key_norm = key_upper.replace(" ", "_")
            designation_id_map.setdefault(key_norm, str(row[0]))

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
            emp_number = emp.get("employee_number")
            if not emp_number:
                _emp_idx = payload.get("employees", []).index(emp)
                raise ValueError(
                    f"Employee at index {_emp_idx} is missing employee_number — this field is required."
                )

            insert_employee(db, workspace_id, employee_id, full_name, emp_number, biodata)

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

            # Resolve grade FK — simple upper() lookup first; if not found, fall
            # back to deriving from the salary def code (e.g. DRIVER_STEP_1 → STEP_1).
            emp_grade = str(emp.get("grade") or "").upper()
            grade_id  = grade_id_map.get(emp_grade)

            # Resolve designation FK — try upper() and spaces→underscores first;
            # if still unresolved, derive from the salary def code.
            emp_desig_raw = str(emp.get("designation") or "")
            emp_desig     = emp_desig_raw.strip().upper()
            designation_id = (
                designation_id_map.get(emp_desig)
                or designation_id_map.get(emp_desig.replace(" ", "_"))
            )

            # Fallback: parse grade + designation directly from the salary def code.
            # Salary def codes are built as DESIGNATION_GRADE (e.g. DISPATCH_RIDER_STEP_1B).
            # Sort by descending key length so longer codes are preferred over shorter ones.
            if not grade_id or not designation_id:
                sal_upper = (sd_code or "").upper()
                sorted_grades = sorted(grade_id_map.keys(), key=len, reverse=True)

                if not grade_id:
                    for g_upper in sorted_grades:
                        if sal_upper == g_upper or sal_upper.endswith("_" + g_upper):
                            grade_id = grade_id_map[g_upper]
                            emp_grade = g_upper
                            break

                if not designation_id:
                    if sal_upper.endswith("_" + emp_grade):
                        des_part = sal_upper[: -(len(emp_grade) + 1)]
                    elif sal_upper == emp_grade:
                        des_part = ""
                    else:
                        des_part = sal_upper
                    if des_part:
                        designation_id = designation_id_map.get(des_part)

            # Resolve contract dates from payload; default start to CURRENT_DATE.
            emp_start_str = emp.get("contract_start")
            emp_end_str   = emp.get("contract_end")
            try:
                emp_start_date = _date.fromisoformat(emp_start_str) if emp_start_str else None
            except ValueError:
                raise Exception(
                    f"Employee '{emp_number}': invalid contract_start '{emp_start_str}' (use YYYY-MM-DD)"
                )
            try:
                emp_end_date = _date.fromisoformat(emp_end_str) if emp_end_str else None
            except ValueError:
                raise Exception(
                    f"Employee '{emp_number}': invalid contract_end '{emp_end_str}' (use YYYY-MM-DD)"
                )

            # O1 — shift_type / state_of_tax / skill_level / is_union_member
            _shift_type      = emp.get("shift_type") or None
            _state_of_tax    = emp.get("state_of_tax") or None
            _skill_level     = emp.get("skill_level") or None
            _is_union_member = bool(emp.get("is_union_member", False))
            _VALID_SHIFT_TYPES = {"DAY", "2_SHIFT", "4_SHIFT"}
            if _shift_type is not None and _shift_type not in _VALID_SHIFT_TYPES:
                raise Exception(
                    f"Employee '{emp_number}': shift_type '{_shift_type}' is not valid — "
                    f"allowed values: DAY, 2_SHIFT, 4_SHIFT"
                )
            if _state_of_tax is not None and len(_state_of_tax) > 50:
                raise Exception(
                    f"Employee '{emp_number}': state_of_tax exceeds 50 characters"
                )
            if _skill_level is not None and len(_skill_level) > 50:
                raise Exception(
                    f"Employee '{emp_number}': skill_level exceeds 50 characters"
                )

            insert_employee_contract(
                db,
                employee_id=employee_id,
                salary_definition_id=salary_definition_id,
                start_date=emp_start_date,
                grade_id=grade_id,
                designation_id=designation_id,
                shift_type=_shift_type,
                state_of_tax=_state_of_tax,
                skill_level=_skill_level,
                is_union_member=_is_union_member,
                end_date=emp_end_date,
            )

        # Publish rule_set snapshots for rules that carry an effective_from date.
        # Rules without effective_from are inserted into payroll_rule only (legacy path).
        _rules_for_publish = [
            {
                "rule_name":            rule.get("rule_name") or rule.get("rule_code") or "UNKNOWN",
                "rule_definition_json": rule.get("definition") or rule.get("rule_definition_json") or {},
                "rule_type":            rule.get("rule_type"),
                "effective_from":       rule.get("effective_from"),
            }
            for rule in payload.get("payroll_rules", [])
        ]
        onboarding_service.publish_rule_sets(db, workspace_id, _rules_for_publish)

        db.commit()

        # Seed workspace_payroll_config — best-effort; failure here does not rollback employee data.
        _wpc = payload.get("workspace_payroll_config") or {}

        # S2 — Validate enum fields before hitting the DB
        _wpc_validation_errors: list[str] = []
        for _field, _allowed in _WPC_ENUM_FIELDS:
            _val = _wpc.get(_field)
            if _val is not None and _val not in _allowed:
                _wpc_validation_errors.append(
                    f"'{_field}' must be one of {sorted(_allowed)}, got {_val!r}"
                )
        if _wpc_validation_errors:
            raise HTTPException(
                status_code=422,
                detail={"errors": _wpc_validation_errors},
            )

        try:
            upsert_workspace_payroll_config(
                workspace_id=workspace_id,
                effective_from=str(_date.today()),
                ph_mode=_wpc.get("ph_mode") or None,
                ph_rate_code=_wpc.get("ph_rate_code") or None,
                saturday_ph_rule=_wpc.get("saturday_ph_rule") or None,
                sunday_ph_rule=_wpc.get("sunday_ph_rule") or None,
                d3_leave_overlap_rule=_wpc.get("d3_leave_overlap_rule") or None,
                d4_absence_rule=_wpc.get("d4_absence_rule") or None,
                updated_by=None,
            )
        except Exception as _wpc_err:
            # S1 — Log the full exception server-side; return a generic message to the caller.
            logger.error(
                "workspace_payroll_config seed failed for workspace %s: %s",
                workspace_id, _wpc_err, exc_info=True,
            )
            warnings.append(
                "Workspace payroll configuration could not be applied. "
                "Check the submitted values and try again."
            )

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
