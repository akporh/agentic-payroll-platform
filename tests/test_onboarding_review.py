from backend.domain.onboarding.review_runner import review_client_onboarding


def test_hard_fail_and_ai_suggestion():
    client_json = {
        "salary_definitions": [
            {
                "name": "STEP_1_TEMPLATE",
                "components": {
                    "BASIC": {"amount": 500000},
                    "HOUSING": {"amount": 300000},
                },
            },
        ],
        "payroll_rules": [
            {
                "rule_code": "PENSION_EMPLOYEE",
                "definition": {
                    "method": "percentage",
                    "rate": 0.08,
                    "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                },
            },
        ],
        "employees": [
            {
                "employee_number": "EMP001",
                "biodata": {},
            },
        ],
    }

    result = review_client_onboarding(client_json)

    assert result["hard_validation"]["status"] == "FAIL"
    assert any(
        "TRANSPORT" in e["message"]
        for e in result["hard_validation"]["errors"]
    )

    assert any(
        "missing TIN" in s
        for s in result["ai_review"]["suggestions"]
    )

    assert "ai_review" in result
    assert "summary" in result["ai_review"]


def test_hard_pass_valid_config():
    client_json = {
        "salary_definitions": [
            {
                "name": "STEP_2_TEMPLATE",
                "components": {
                    "BASIC": {"amount": 500000},
                    "HOUSING": {"amount": 300000},
                    "TRANSPORT": {"amount": 200000},
                    "CONSOLIDATED": {"amount": 100000},
                },
            },
        ],
        "payroll_rules": [
            {
                "rule_code": "PENSION_EMPLOYEE",
                "definition": {
                    "method": "percentage",
                    "rate": 0.08,
                    "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                },
            },
        ],
        "employees": [
            {
                "employee_number": "EMP001",
                "biodata": {
                    "TIN": "1234567890",
                    "BANK": "ACCESS",
                    "ACCOUNT_NUMBER": "0012345678",
                    "RSA": "PEN100012345678",
                },
            },
        ],
    }

    result = review_client_onboarding(client_json)

    assert result["hard_validation"]["status"] == "PASS"
    assert len(result["hard_validation"]["errors"]) == 0


def test_overtime_only_passes_without_pension_rule():
    """Pension is statutory — not required as a client-defined payroll rule.
    A payload with only an OVERTIME rule and no explicit pension rule must pass
    hard_validation because pension rates are sourced from statutory_rule at
    execution time, not from the onboarding payload.
    """
    client_json = {
        "salary_definitions": [
            {
                "name": "STEP_1_TEMPLATE",
                "components": {
                    "BASIC": {"amount": 500000},
                    "HOUSING": {"amount": 300000},
                    "TRANSPORT": {"amount": 200000},
                },
            },
        ],
        "payroll_rules": [
            {
                "rule_code": "OVERTIME",
                "definition": {
                    "method": "fixed_amount",
                    "amount": 50000,
                },
            },
        ],
        "employees": [
            {
                "employee_number": "EMP001",
                "biodata": {
                    "TIN": "1234567890",
                    "BANK": "ACCESS",
                    "ACCOUNT_NUMBER": "0012345678",
                    "RSA": "PEN100012345678",
                },
            },
        ],
    }

    result = review_client_onboarding(client_json)

    # Pension is statutory — no client pension rule required.
    assert result["hard_validation"]["status"] == "PASS", (
        f"Expected PASS but got FAIL: {result['hard_validation']['errors']}"
    )


def test_fail_employee_missing_rsa():
    client_json = {
        "salary_definitions": [
            {
                "name": "STEP_1_TEMPLATE",
                "components": {
                    "BASIC": {"amount": 500000},
                    "HOUSING": {"amount": 300000},
                    "TRANSPORT": {"amount": 200000},
                },
            },
        ],
        "payroll_rules": [
            {
                "rule_code": "PENSION_EMPLOYEE",
                "definition": {
                    "method": "percentage",
                    "rate": 0.08,
                    "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                },
            },
        ],
        "employees": [
            {
                "employee_number": "EMP001",
                "biodata": {
                    "TIN": "1234567890",
                    "BANK": "ACCESS",
                    "ACCOUNT_NUMBER": "0012345678",
                },
            },
        ],
    }

    result = review_client_onboarding(client_json)

    assert result["hard_validation"]["status"] == "FAIL"
    assert any(
        e["category"] == "Employee Compliance" and "RSA" in e["message"]
        for e in result["hard_validation"]["errors"]
    )
