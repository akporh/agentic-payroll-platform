"""
SQL Emitter for Client Onboarding.

Generates reviewable SQL INSERT statements from validated client
onboarding JSON. Does not execute any SQL — emits strings only.

No database access — pure string generation.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

import json


def emit_salary_definitions_sql(salary_definitions: list[dict]) -> str:
    """Emit INSERT statements for salary_definition records.

    Args:
        salary_definitions: List of salary definition dicts from client JSON.

    Returns:
        SQL string containing one INSERT per salary definition.
    """
    statements = []
    for sd in salary_definitions:
        name = sd.get("name", "UNKNOWN")
        components_json = json.dumps(sd.get("components", {}))
        stmt = (
            "INSERT INTO salary_definition\n"
            "(salary_definition_id, name, components_jsonb)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{name}', '{components_json}'::jsonb);"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_payroll_rules_sql(payroll_rules: list[dict]) -> str:
    """Emit INSERT statements for payroll_rule records.

    Args:
        payroll_rules: List of payroll rule dicts from client JSON.

    Returns:
        SQL string containing one INSERT per payroll rule.
    """
    statements = []
    for rule in payroll_rules:
        rule_code = rule.get("rule_code", "UNKNOWN")
        definition_json = json.dumps(rule.get("definition", {}))
        stmt = (
            "INSERT INTO payroll_rule\n"
            "(payroll_rule_id, rule_code, rule_definition_json)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{rule_code}', '{definition_json}'::jsonb);"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_employees_sql(employees: list[dict]) -> str:
    """Emit INSERT statements for employee records.

    Args:
        employees: List of employee dicts from client JSON.

    Returns:
        SQL string containing one INSERT per employee.
    """
    statements = []
    for emp in employees:
        employee_number = emp.get("employee_number", "UNKNOWN")
        biodata_json = json.dumps(emp.get("biodata", {}))
        stmt = (
            "INSERT INTO employee\n"
            "(employee_id, employee_number, personal_details_encrypted)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{employee_number}', '{biodata_json}'::jsonb);"
        )
        statements.append(stmt)
    return "\n\n".join(statements)
