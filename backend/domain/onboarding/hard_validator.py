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
            if not isinstance(comp_val.get("amount"), (int, float)):
                errors.append(
                    ValidationError(
                        category="SALARY_DEFINITION",
                        message=f"{name}: component {comp_code} missing numeric amount",
                    )
                )

    for rule in client_json.get("payroll_rules", []):
        rule_code = rule.get("rule_code", "UNKNOWN")
        definition = rule.get("definition", {})
        method = definition.get("method")

        if method not in SUPPORTED_METHODS:
            errors.append(
                ValidationError(
                    category="PAYROLL_RULE",
                    message=f"{rule_code}: unsupported method '{method}'",
                )
            )
            continue

        required_keys = SUPPORTED_METHODS[method]
        missing_keys = required_keys - set(definition.keys())
        if missing_keys:
            errors.append(
                ValidationError(
                    category="PAYROLL_RULE",
                    message=f"{rule_code}: method '{method}' missing required keys: {', '.join(sorted(missing_keys))}",
                )
            )

    payroll_rules = client_json.get("payroll_rules", [])
    pension_rules = [
        r for r in payroll_rules
        if "PENSION" in r.get("rule_code", "").upper()
        and r.get("definition", {}).get("method") == "percentage"
    ]

    if not pension_rules:
        errors.append(
            ValidationError(
                category="Completeness",
                message="No pension rule found — at least one payroll_rule with method 'percentage' and rule_code containing 'PENSION' is required.",
            )
        )
    else:
        for pr in pension_rules:
            rule_code = pr.get("rule_code", "UNKNOWN")
            base_components = set(pr.get("definition", {}).get("base_components", []))
            missing_base = PENSION_BASE_REQUIRED - base_components
            if missing_base:
                errors.append(
                    ValidationError(
                        category="Completeness",
                        message=f"{rule_code}: pension base_components missing: {', '.join(sorted(missing_base))}",
                    )
                )

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
