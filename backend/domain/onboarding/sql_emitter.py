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

    Maps onboarding JSON fields to the actual schema:
        employee_number → full_name (schema column).

    Args:
        workspace_id: The workspace these employees belong to.
        employees: List of employee dicts from client JSON.

    Returns:
        SQL string containing one INSERT per employee,
        scoped to the workspace.
    """
    statements = []
    for emp in employees:
        full_name = emp.get("employee_number", "UNKNOWN")
        stmt = (
            "INSERT INTO employee\n"
            "(employee_id, workspace_id, full_name)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{workspace_id}', '{full_name}');"
        )
        statements.append(stmt)
    return "\n\n".join(statements)


def emit_salary_definitions_sql(workspace_id: str, employees: list[dict], salary_definitions: list[dict]) -> str:
    """Emit INSERT statements for salary_definition records.

    Salary definitions are linked to employees via employee_id (FK).
    Uses a subquery to look up employee_id by full_name within the
    workspace, so employees must be inserted first in the transaction.

    Each salary definition is assigned to the first employee in the
    workspace. For Phase 1 (single bureau, uniform salary templates),
    this is correct. Multi-employee salary mapping is a Phase 2 concern.

    Args:
        workspace_id: The workspace (used to scope the employee lookup).
        employees: List of employee dicts (to resolve employee_id FK).
        salary_definitions: List of salary definition dicts from client JSON.

    Returns:
        SQL string containing one INSERT per salary definition.
    """
    statements = []
    for sd in salary_definitions:
        components_json = json.dumps(sd.get("components", {}))
        for emp in employees:
            full_name = emp.get("employee_number", "UNKNOWN")
            stmt = (
                "INSERT INTO salary_definition\n"
                "(salary_definition_id, employee_id, components_jsonb)\n"
                "VALUES\n"
                f"(gen_random_uuid(), "
                f"(SELECT employee_id FROM employee WHERE workspace_id = '{workspace_id}' "
                f"AND full_name = '{full_name}' LIMIT 1), "
                f"'{components_json}'::jsonb);"
            )
            statements.append(stmt)
    return "\n\n".join(statements)


def emit_payroll_rules_sql(workspace_id: str, payroll_rules: list[dict]) -> str:
    """Emit INSERT statements for payroll_rule records.

    Maps onboarding JSON fields to the actual schema:
        rule_code → name (schema column).
        definition → rule_jsonb (schema column).

    Args:
        workspace_id: The workspace these rules belong to.
        payroll_rules: List of payroll rule dicts from client JSON.

    Returns:
        SQL string containing one INSERT per payroll rule,
        scoped to the workspace.
    """
    statements = []
    for rule in payroll_rules:
        name = rule.get("rule_code", "UNKNOWN")
        rule_jsonb = json.dumps(rule.get("definition", {}))
        stmt = (
            "INSERT INTO payroll_rule\n"
            "(payroll_rule_id, workspace_id, name, rule_jsonb)\n"
            "VALUES\n"
            f"(gen_random_uuid(), '{workspace_id}', '{name}', '{rule_jsonb}'::jsonb);"
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
    3. Salary definition INSERTs.
    4. Payroll rule INSERTs.
    5. Employee INSERTs.
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
        "-- Employees (inserted first — salary definitions reference them)",
        emit_employees_sql(workspace_id, employees),
        "",
        "-- Salary definitions (linked to employees via employee_id FK)",
        emit_salary_definitions_sql(workspace_id, employees, salary_definitions),
        "",
        "-- Payroll rules",
        emit_payroll_rules_sql(workspace_id, payroll_rules),
        "",
        "COMMIT;",
    ]
    return "\n".join(parts)
