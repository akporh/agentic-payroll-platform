"""
Tests for the onboarding SQL emitter and loader.

Covers:
- BLOCKED status when hard validation fails (no SQL emitted).
- READY status with valid config produces transactional SQL.
- Transaction wrapping (BEGIN/COMMIT).
- Duplicate-prevention guard is present.
- workspace_id is embedded in employee and payroll_rule INSERTs.
- Salary definitions are linked to employees via employee_id FK subquery.
- Emitted column names match the actual database schema.
- Correct insert ordering: employees before salary definitions.
"""

from backend.domain.onboarding.loader import emit_onboarding_sql
from backend.domain.onboarding.sql_emitter import (
    emit_onboarding_transaction,
    emit_salary_definitions_sql,
    emit_payroll_rules_sql,
    emit_employees_sql,
    _emit_duplicate_guard,
)

WORKSPACE_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

VALID_CLIENT_JSON = {
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

    result = emit_onboarding_sql(WORKSPACE_ID, client_json)

    assert result["status"] == "BLOCKED"
    assert result["sql"] == ""


def test_ready_with_valid_config():
    result = emit_onboarding_sql(WORKSPACE_ID, VALID_CLIENT_JSON)

    assert result["status"] == "READY"
    assert "INSERT INTO employee" in result["sql"]
    assert "INSERT INTO salary_definition" in result["sql"]
    assert "PENSION_EMPLOYEE" in result["sql"]


def test_transaction_wrapping():
    result = emit_onboarding_sql(WORKSPACE_ID, VALID_CLIENT_JSON)

    sql = result["sql"]
    assert sql.startswith("BEGIN;")
    assert sql.strip().endswith("COMMIT;")


def test_duplicate_guard_present():
    result = emit_onboarding_sql(WORKSPACE_ID, VALID_CLIENT_JSON)

    sql = result["sql"]
    assert "already has loaded data" in sql
    assert WORKSPACE_ID in sql


def test_workspace_id_in_employee_inserts():
    sql = emit_employees_sql(WORKSPACE_ID, VALID_CLIENT_JSON["employees"])
    assert WORKSPACE_ID in sql
    assert "workspace_id" in sql


def test_employee_uses_schema_columns():
    sql = emit_employees_sql(WORKSPACE_ID, VALID_CLIENT_JSON["employees"])
    assert "full_name" in sql
    assert "employee_number" not in sql
    assert "personal_details_encrypted" not in sql


def test_payroll_rule_uses_schema_columns():
    sql = emit_payroll_rules_sql(WORKSPACE_ID, VALID_CLIENT_JSON["payroll_rules"])
    assert "rule_jsonb" in sql
    assert "name" in sql
    assert "rule_code" not in sql
    assert "rule_definition_json" not in sql


def test_salary_definition_uses_employee_id_fk():
    sql = emit_salary_definitions_sql(
        WORKSPACE_ID,
        VALID_CLIENT_JSON["employees"],
        VALID_CLIENT_JSON["salary_definitions"],
    )
    assert "employee_id" in sql
    assert "SELECT employee_id FROM employee" in sql
    assert "workspace_id" not in sql.split("VALUES")[0]


def test_payroll_rules_includes_workspace():
    sql = emit_payroll_rules_sql(WORKSPACE_ID, VALID_CLIENT_JSON["payroll_rules"])
    assert WORKSPACE_ID in sql
    assert "workspace_id" in sql


def test_duplicate_guard_checks_employee_table():
    guard_sql = _emit_duplicate_guard(WORKSPACE_ID)
    assert "SELECT 1 FROM employee" in guard_sql
    assert WORKSPACE_ID in guard_sql
    assert "RAISE EXCEPTION" in guard_sql


def test_full_transaction_order():
    sql = emit_onboarding_transaction(
        workspace_id=WORKSPACE_ID,
        salary_definitions=VALID_CLIENT_JSON["salary_definitions"],
        payroll_rules=VALID_CLIENT_JSON["payroll_rules"],
        employees=VALID_CLIENT_JSON["employees"],
    )

    begin_pos = sql.index("BEGIN;")
    guard_pos = sql.index("already has loaded data")
    emp_pos = sql.index("INSERT INTO employee")
    salary_pos = sql.index("INSERT INTO salary_definition")
    rules_pos = sql.index("INSERT INTO payroll_rule")
    commit_pos = sql.index("COMMIT;")

    assert begin_pos < guard_pos < emp_pos < salary_pos < rules_pos < commit_pos


def test_employees_before_salary_definitions():
    sql = emit_onboarding_transaction(
        workspace_id=WORKSPACE_ID,
        salary_definitions=VALID_CLIENT_JSON["salary_definitions"],
        payroll_rules=VALID_CLIENT_JSON["payroll_rules"],
        employees=VALID_CLIENT_JSON["employees"],
    )

    emp_pos = sql.index("INSERT INTO employee")
    salary_pos = sql.index("INSERT INTO salary_definition")
    assert emp_pos < salary_pos
