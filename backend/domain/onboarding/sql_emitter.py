"""
SQL Emitter for Client Onboarding.

Generates reviewable SQL INSERT statements from validated client
onboarding JSON. Does not execute any SQL — emits strings only.

All emitted SQL is:
1. Scoped to a workspace_id (tenant isolation from day one).
2. Wrapped in a BEGIN/COMMIT transaction block so the load is
   all-or-nothing — a failure rolls back everything.
3. Guarded by a duplicate-prevention check that aborts the
   transaction if the workspace already has loaded data.

Column names match the live database schema exactly:
- employee: employee_id, workspace_id, full_name, employee_number,
            personal_details_encrypted, status
- salary_definition: salary_definition_id, workspace_id, name,
                     components_jsonb
- payroll_rule: rule_id, workspace_id, rule_name, rule_definition_json

No database access — pure string generation.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

import json


def _emit_duplicate_guard(workspace_id: str) -> str:
    """Emit a DO block that aborts if the workspace already has data.

    Checks the employee table for any rows scoped to the workspace.
    If rows exist, raises an exception that rolls back the transaction.

    Args:
        workspace_id: The workspace to check for existing data.

    Returns:
        SQL DO block string.
    """
    return (
        "DO $$\n"
        "BEGIN\n"
        "  IF EXISTS (\n"
        f"    SELECT 1 FROM employee WHERE workspace_id = '{workspace_id}'\n"
        "  ) THEN\n"
        f"    RAISE EXCEPTION 'Workspace {workspace_id} already has loaded data. "
        "Aborting to prevent duplicates.';\n"
        "  END IF;\n"
        "END\n"
        "$$;"
    )


def emit_employees_sql(workspace_id: str, employees: list[dict]) -> str:
    """Emit INSERT statements for employee records.

    Schema columns used:
        employee_id          — gen_random_uuid()
        workspace_id         — from argument
        full_name            — from biodata or employee_number fallback
        employee_number      — from client JSON (unique per workspace)
        personal_details_encrypted — biodata JSONB (TIN, BANK, etc.)
        status               — defaults to 'ACTIVE'

    Args:
        workspace_id: The workspace these employees belong to.
        employees: List of employee dicts from client JSON.

    Returns:
        SQL string containing one INSERT per employee,
        scoped to the workspace.
    """
    statements = []
    for emp in employees:
        employee_number = emp.get("employee_number")
        if not employee_number:
            raise ValueError(f"Employee at index {employees.index(emp)} is missing employee_number.")
        biodata = emp.get("biodata", {})
        full_name = biodata.get("FULL_NAME", employee_number)
        biodata_json = json.dumps(biodata)
        stmt = (
            "INSERT INTO employee\n"
            "(employee_id, workspace_id, full_name, employee_number,"
            " personal_details_encrypted, status)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{workspace_id}', '{full_name}',"
            f" '{employee_number}', '{biodata_json}'::jsonb, 'ACTIVE');"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_salary_definitions_sql(workspace_id: str, salary_definitions: list[dict]) -> str:
    """Emit INSERT statements for salary_definition records.

    Schema columns used:
        salary_definition_id — gen_random_uuid()
        workspace_id         — from argument
        name                 — template name from client JSON
        components_jsonb     — salary components JSONB

    Salary definitions are workspace-scoped (not employee-scoped).
    The link from employee to salary definition goes through the
    employee_contract table.

    Args:
        workspace_id: The workspace these definitions belong to.
        salary_definitions: List of salary definition dicts from client JSON.

    Returns:
        SQL string containing one INSERT per salary definition,
        scoped to the workspace.
    """
    statements = []
    for sd in salary_definitions:
        name = sd.get("name", "UNKNOWN")
        code = sd.get("code") or name.upper().replace(" ", "_")
        components_json = json.dumps(sd.get("components", {}))
        stmt = (
            "INSERT INTO salary_definition\n"
            "(salary_definition_id, workspace_id, code, name, components_jsonb)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{workspace_id}', '{code}', '{name}',"
            f" '{components_json}'::jsonb);"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_payroll_rules_sql(workspace_id: str, payroll_rules: list[dict]) -> str:
    """Emit INSERT statements for payroll_rule records.

    Schema columns used:
        rule_id              — gen_random_uuid()
        workspace_id         — from argument
        rule_name            — mapped from rule_code in client JSON
        rule_definition_json — mapped from definition in client JSON

    Args:
        workspace_id: The workspace these rules belong to.
        payroll_rules: List of payroll rule dicts from client JSON.

    Returns:
        SQL string containing one INSERT per payroll rule,
        scoped to the workspace.
    """
    statements = []
    for rule in payroll_rules:
        rule_name = rule.get("rule_code", "UNKNOWN")
        definition_json = json.dumps(rule.get("definition", {}))
        stmt = (
            "INSERT INTO payroll_rule\n"
            "(rule_id, workspace_id, rule_name, rule_definition_json)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{workspace_id}', '{rule_name}',"
            f" '{definition_json}'::jsonb);"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_onboarding_transaction(
    workspace_id: str,
    salary_definitions: list[dict],
    payroll_rules: list[dict],
    employees: list[dict],
) -> str:
    """Emit a complete onboarding SQL bundle wrapped in a transaction.

    The emitted SQL includes:
    1. BEGIN — starts the transaction.
    2. Duplicate guard — aborts if workspace already has data.
    3. Employee INSERTs.
    4. Salary definition INSERTs (workspace-scoped).
    5. Payroll rule INSERTs.
    6. COMMIT — finalises all inserts atomically.

    If any statement fails, the entire transaction rolls back
    automatically, leaving no partial data.

    Args:
        workspace_id: The workspace to load data into.
        salary_definitions: List of salary definition dicts.
        payroll_rules: List of payroll rule dicts.
        employees: List of employee dicts.

    Returns:
        A single SQL string containing the full transactional load.
    """
    parts = [
        "BEGIN;",
        "",
        "-- Duplicate prevention: abort if workspace already loaded",
        _emit_duplicate_guard(workspace_id),
        "",
        "-- Employees",
        emit_employees_sql(workspace_id, employees),
        "",
        "-- Salary definitions (workspace-scoped templates)",
        emit_salary_definitions_sql(workspace_id, salary_definitions),
        "",
        "-- Payroll rules",
        emit_payroll_rules_sql(workspace_id, payroll_rules),
        "",
        "COMMIT;",
    ]
    return "\n".join(parts)
