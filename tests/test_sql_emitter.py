from backend.domain.onboarding.loader import emit_onboarding_sql


def test_blocked_when_missing_transport():
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
                "biodata": {
                    "TIN": "1234567890",
                    "BANK": "ACCESS",
                    "ACCOUNT_NUMBER": "0012345678",
                    "RSA": "PEN100012345678",
                },
            },
        ],
    }

    result = emit_onboarding_sql(client_json)

    assert result["status"] == "BLOCKED"
    assert result["sql"]["salary_definitions"] == ""
    assert result["sql"]["payroll_rules"] == ""
    assert result["sql"]["employees"] == ""


def test_ready_with_valid_config():
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

    result = emit_onboarding_sql(client_json)

    assert result["status"] == "READY"
    assert "INSERT INTO salary_definition" in result["sql"]["salary_definitions"]
    assert "PENSION_EMPLOYEE" in result["sql"]["payroll_rules"]
