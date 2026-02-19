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
                "biodata": {"TIN": "1234567890"},
            },
        ],
    }

    result = review_client_onboarding(client_json)

    assert result["hard_validation"]["status"] == "PASS"
    assert len(result["hard_validation"]["errors"]) == 0
