"""
Client Onboarding Loader.

Orchestrates the onboarding review and SQL emission pipeline.
If hard validation fails, no SQL is emitted. If it passes, reviewable
INSERT statements are generated for all onboarding entities.

No database access — review + string generation only.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

from backend.domain.onboarding.review_runner import review_client_onboarding
from backend.domain.onboarding.sql_emitter import (
    emit_salary_definitions_sql,
    emit_payroll_rules_sql,
    emit_employees_sql,
)


def emit_onboarding_sql(client_json: dict) -> dict:
    """Generate a reviewable SQL onboarding bundle from client JSON.

    Runs the full onboarding review first. If hard validation fails,
    returns BLOCKED status with empty SQL. If it passes, returns READY
    status with INSERT statements for all entities.

    Args:
        client_json: The full client onboarding configuration dict.

    Returns:
        Dict with status, full review output, and SQL strings.
    """
    review = review_client_onboarding(client_json)

    if review["hard_validation"]["status"] == "FAIL":
        return {
            "status": "BLOCKED",
            "review": review,
            "sql": {
                "salary_definitions": "",
                "payroll_rules": "",
                "employees": "",
            },
        }

    return {
        "status": "READY",
        "review": review,
        "sql": {
            "salary_definitions": emit_salary_definitions_sql(
                client_json.get("salary_definitions", [])
            ),
            "payroll_rules": emit_payroll_rules_sql(
                client_json.get("payroll_rules", [])
            ),
            "employees": emit_employees_sql(
                client_json.get("employees", [])
            ),
        },
    }
