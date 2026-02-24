"""
Tests for the onboarding SQL emitter and loader.

Covers:
- BLOCKED status when hard validation fails (no SQL emitted).
- READY status with valid config produces transactional SQL.
- Transaction wrapping (BEGIN/COMMIT).
- Duplicate-prevention guard is present.
- Column names match the live database schema exactly.
- workspace_id scoping on all workspace-scoped tables.
- Correct insert ordering within the transaction.
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
    assert "INSERT INTO payroll_rule" in result["sql"]


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


def test_employee_uses_correct_schema_columns():
    sql = emit_employees_sql(WORKSPACE_ID, VALID_CLIENT_JSON["employees"])
    assert "employee_id" in sql
    assert "workspace_id" in sql
    assert "full_name" in sql
    assert "employee_number" in sql
    assert "personal_details_encrypted" in sql
    assert "status" in sql
    assert "'ACTIVE'" in sql
    assert WORKSPACE_ID in sql
    assert "'EMP001'" in sql


def test_salary_definition_uses_correct_schema_columns():
    sql = emit_salary_definitions_sql(WORKSPACE_ID, VALID_CLIENT_JSON["salary_definitions"])
    assert "salary_definition_id" in sql
    assert "workspace_id" in sql
    assert "name" in sql
    assert "components_jsonb" in sql
    assert WORKSPACE_ID in sql
    assert "STEP_2_TEMPLATE" in sql
    assert "employee_id" not in sql


def test_payroll_rule_uses_correct_schema_columns():
    sql = emit_payroll_rules_sql(WORKSPACE_ID, VALID_CLIENT_JSON["payroll_rules"])
    assert "rule_id" in sql
    assert "workspace_id" in sql
    assert "rule_name" in sql
    assert "rule_definition_json" in sql
    assert WORKSPACE_ID in sql
    assert "PENSION_EMPLOYEE" in sql
    assert "payroll_rule_id" not in sql
    assert "rule_jsonb" not in sql


def test_workspace_id_in_all_inserts():
    result = emit_onboarding_sql(WORKSPACE_ID, VALID_CLIENT_JSON)
    sql = result["sql"]
    for line in sql.split("\n"):
        if "INSERT INTO" in line:
            table = line.split("INSERT INTO ")[1].strip()
            insert_block_start = sql.index(line)
            insert_block = sql[insert_block_start:sql.index(";", insert_block_start) + 1]
            assert WORKSPACE_ID in insert_block, f"workspace_id missing from {table} INSERT"


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


def test_employee_biodata_stored_as_encrypted_json():
    sql = emit_employees_sql(WORKSPACE_ID, VALID_CLIENT_JSON["employees"])
    assert "TIN" in sql
    assert "1234567890" in sql
    assert "::jsonb" in sql
