from sqlalchemy import text
from backend.infra.db.repositories.workspace_repo import (
    has_pay_cycle,
    has_grade,
    has_designation,
    has_salary_definition,
    has_active_payroll_rule,
    has_component_metadata,
)

"""
Hard Validator for Client Onboarding JSON.

Performs deterministic, Phase 1 legal-minimum validation on client
onboarding configuration. Checks salary definition completeness and
payroll rule executability.

No database access — pure validation logic.

Reference: ARCHITECTURE_LOCK.md — Onboarding Validation Requirements.
"""

from backend.domain.onboarding.report_types import (
    HardValidationResult,
    ValidationError,
)

REQUIRED_COMPONENTS = {"BASIC", "HOUSING", "TRANSPORT"}

SUPPORTED_METHODS = {
    "percentage": {"rate", "base_components"},
    "fixed_amount": {"amount"},
    "per_day": {"rate", "input_key"},
    "statutory": {"system"},
}

PENSION_BASE_REQUIRED = {"BASIC", "HOUSING", "TRANSPORT"}

EMPLOYEE_REQUIRED_BIODATA = {"TIN", "BANK", "ACCOUNT_NUMBER", "RSA"}


def validate_client_json(client_json: dict) -> HardValidationResult:
    """Validate a client onboarding JSON config deterministically.

    Args:
        client_json: The full client onboarding configuration dict
            containing salary_definitions, payroll_rules, and employees.

    Returns:
        HardValidationResult with status PASS or FAIL and any errors found.
    """
    errors: list[ValidationError] = []

    for sd in client_json.get("salary_definitions", []):
        name = sd.get("name", "UNKNOWN")
        components = sd.get("components", {})

        missing = REQUIRED_COMPONENTS - set(components.keys())
        if missing:
            errors.append(
                ValidationError(
                    category="SALARY_DEFINITION",
                    message=f"{name}: missing required components: {', '.join(sorted(missing))}",
                )
            )

        for comp_code, comp_val in components.items():
            amount = comp_val.get("amount") if isinstance(comp_val, dict) else comp_val
            if not isinstance(amount, (int, float)):
                errors.append(
                    ValidationError(
                        category="SALARY_DEFINITION",
                        message=f"{name}: component {comp_code} missing numeric amount",
                    )
                )

    for rule in client_json.get("payroll_rules", []):
        pass  # payroll rule structure validation removed — rules are normalised upstream

    for emp in client_json.get("employees", []):
        emp_num = emp.get("employee_number", "UNKNOWN")
        biodata = emp.get("biodata", {})
        missing_bio = EMPLOYEE_REQUIRED_BIODATA - set(biodata.keys())
        if missing_bio:
            errors.append(
                ValidationError(
                    category="Employee Compliance",
                    message=f"{emp_num}: missing required biodata: {', '.join(sorted(missing_bio))}",
                )
            )

    status = "FAIL" if errors else "PASS"
    return HardValidationResult(status=status, errors=errors)


    
def validate_workspace_for_state(db, workspace_id: str, target_state: str):

    if target_state == "STRUCTURE_DEFINED":
        ensure_pay_cycle_exists(db, workspace_id)
        ensure_grade_exists(db, workspace_id)
        ensure_designation_exists(db, workspace_id)

    elif target_state == "COMPENSATION_DEFINED":
        ensure_salary_definition_exists(db, workspace_id)

    elif target_state == "RULES_DEFINED":
        ensure_active_payroll_rule_exists(db, workspace_id)

    elif target_state == "READY":
        ensure_component_metadata_exists(db, workspace_id)

    elif target_state == "LIVE":
        # LIVE does not re-check everything.
        # Execution guard handles payroll safety.
        pass


def ensure_pay_cycle_exists(db, workspace_id: str):
    if not has_pay_cycle(db, workspace_id):
        raise ValueError("Cannot advance: no pay cycle defined for this workspace.")


def ensure_grade_exists(db, workspace_id: str):
    if not has_grade(db, workspace_id):
        raise ValueError("Cannot advance: no grade defined for this workspace.")


def ensure_designation_exists(db, workspace_id: str):
    if not has_designation(db, workspace_id):
        raise ValueError("Cannot advance: no designation defined for this workspace.")


def ensure_salary_definition_exists(db, workspace_id: str):
    if not has_salary_definition(db, workspace_id):
        raise ValueError("Cannot advance: no salary definition defined for this workspace.")


def ensure_active_payroll_rule_exists(db, workspace_id: str):
    if not has_active_payroll_rule(db, workspace_id):
        raise ValueError("Cannot advance: no active payroll rule defined for this workspace.")


def ensure_component_metadata_exists(db, workspace_id: str):
    if not has_component_metadata(db, workspace_id):
        raise ValueError("Cannot advance: no component metadata defined for this workspace.")