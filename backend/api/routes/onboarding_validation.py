"""
Onboarding structural validation route (workspace-scoped).

Performs deterministic structural and cross-reference validation
on a workspace-level onboarding payload. No business logic, no
writes, no statutory validation. Only checks that the payload
is well-formed and internally consistent.

The only DB access is a single read to confirm the workspace exists.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

from fastapi import APIRouter, Request
from sqlalchemy import text

from backend.infra.db.session import SessionLocal

router = APIRouter()


def _validate_required_fields(payload: dict, errors: list):
    """Check that required top-level keys are present."""
    required = ["workspace_id", "employees", "salary_definitions"]
    for key in required:
        if key not in payload or payload[key] is None:
            errors.append({
                "field": key,
                "message": f"Missing required field: {key}",
            })


def _validate_employees(employees: list, errors: list):
    """Check each employee has required fields and no duplicates."""
    seen_ids = set()
    for i, emp in enumerate(employees):
        if "employee_id" not in emp and "employee_number" not in emp:
            errors.append({
                "field": f"employees[{i}]",
                "message": "Employee must have employee_id or employee_number",
            })

        emp_id = emp.get("employee_id") or emp.get("employee_number")
        if emp_id in seen_ids:
            errors.append({
                "field": f"employees[{i}]",
                "message": f"Duplicate employee identifier: {emp_id}",
            })
        if emp_id:
            seen_ids.add(emp_id)


def _validate_salary_definitions(salary_definitions: list, errors: list):
    """Check each salary definition has required structure and no duplicates."""
    seen_ids = set()
    for i, sd in enumerate(salary_definitions):
        sd_id = sd.get("salary_definition_id") or sd.get("name")

        if not sd.get("name"):
            errors.append({
                "field": f"salary_definitions[{i}]",
                "message": "Salary definition must have a name",
            })

        if not sd.get("components"):
            errors.append({
                "field": f"salary_definitions[{i}]",
                "message": "Salary definition must have components",
            })
        else:
            components = sd["components"]
            if isinstance(components, dict):
                for code, comp in components.items():
                    if isinstance(comp, dict) and "amount" not in comp:
                        errors.append({
                            "field": f"salary_definitions[{i}].components.{code}",
                            "message": f"Component {code} must have an amount",
                        })
            elif isinstance(components, list):
                for j, comp in enumerate(components):
                    if not comp.get("code"):
                        errors.append({
                            "field": f"salary_definitions[{i}].components[{j}]",
                            "message": "Component must have a code",
                        })
                    if "amount" not in comp:
                        errors.append({
                            "field": f"salary_definitions[{i}].components[{j}]",
                            "message": f"Component {comp.get('code', 'UNKNOWN')} must have an amount",
                        })

        if sd_id and sd_id in seen_ids:
            errors.append({
                "field": f"salary_definitions[{i}]",
                "message": f"Duplicate salary definition: {sd_id}",
            })
        if sd_id:
            seen_ids.add(sd_id)


def _validate_cross_references(employees: list, salary_definitions: list, errors: list):
    """Check that employee salary_definition references are valid."""
    sd_names = {sd.get("name") for sd in salary_definitions if sd.get("name")}
    sd_ids = {str(sd.get("salary_definition_id")) for sd in salary_definitions if sd.get("salary_definition_id")}
    valid_refs = sd_names | sd_ids

    for i, emp in enumerate(employees):
        sd_ref = emp.get("salary_definition_id") or emp.get("salary_definition_name")
        if sd_ref and str(sd_ref) not in valid_refs:
            errors.append({
                "field": f"employees[{i}].salary_definition_id",
                "message": f"References non-existent salary definition: {sd_ref}",
            })


def _check_workspace_exists(workspace_id: str) -> bool | None:
    """Check if the workspace exists in the database.

    This is the only DB access in this module — a single read query.
    Returns True if found, False if not found, None if DB is unavailable.
    """
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT 1 FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        return result.fetchone() is not None
    except Exception:
        return None
    finally:
        session.close()


def _build_warnings(payload: dict) -> list:
    """Generate non-blocking warnings for optional issues."""
    warnings = []

    if not payload.get("payroll_rules"):
        warnings.append({
            "field": "payroll_rules",
            "message": "No payroll rules provided — workspace will have no custom rules",
        })

    return warnings


@router.post("/onboarding/validate")
async def validate_onboarding(request: Request):
    """Validate an onboarding payload structurally and cross-referentially.

    Checks:
    1. Required top-level fields are present.
    2. Workspace exists in the database (single read).
    3. Each employee has an identifier and no duplicates.
    4. Each salary definition has name, components, and no duplicates.
    5. Employee salary definition references are valid.

    No writes. No business logic. No statutory validation.
    """
    try:
        payload = await request.json()
    except Exception:
        return {
            "status": "invalid",
            "errors": [{"field": "body", "message": "Invalid JSON payload"}],
            "warnings": [],
        }

    errors = []
    _validate_required_fields(payload, errors)

    if errors:
        return {
            "status": "invalid",
            "errors": errors,
            "warnings": [],
        }

    workspace_id = payload["workspace_id"]
    workspace_check = _check_workspace_exists(workspace_id)
    if workspace_check is None:
        errors.append({
            "field": "workspace_id",
            "message": "Unable to verify workspace — database unavailable",
        })
        return {
            "status": "invalid",
            "errors": errors,
            "warnings": [],
        }
    if not workspace_check:
        errors.append({
            "field": "workspace_id",
            "message": f"Workspace {workspace_id} does not exist",
        })
        return {
            "status": "invalid",
            "errors": errors,
            "warnings": [],
        }

    employees = payload.get("employees", [])
    salary_definitions = payload.get("salary_definitions", [])

    _validate_employees(employees, errors)
    _validate_salary_definitions(salary_definitions, errors)
    _validate_cross_references(employees, salary_definitions, errors)

    warnings = _build_warnings(payload)

    if errors:
        return {
            "status": "invalid",
            "errors": errors,
            "warnings": warnings,
        }

    return {
        "status": "valid",
        "errors": [],
        "warnings": warnings,
    }
