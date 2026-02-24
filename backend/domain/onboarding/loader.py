"""
Client Onboarding Loader.

Orchestrates the onboarding review and SQL emission pipeline.
If hard validation fails, no SQL is emitted. If it passes, a
transactional SQL bundle is generated that:
1. Guards against duplicate workspace loads.
2. Wraps all INSERTs in a single BEGIN/COMMIT transaction.
3. Scopes every record to the given workspace_id.

No database access — review + string generation only.

Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.
"""

from backend.domain.onboarding.review_runner import review_client_onboarding
from backend.domain.onboarding.sql_emitter import emit_onboarding_transaction


def emit_onboarding_sql(workspace_id: str, client_json: dict) -> dict:
    """Generate a reviewable, transactional SQL onboarding bundle.

    Runs the full onboarding review first. If hard validation fails,
    returns BLOCKED status with empty SQL. If it passes, returns READY
    status with a single transactional SQL string that includes
    duplicate-prevention, all INSERTs scoped to the workspace, and
    an atomic COMMIT.

    Args:
        workspace_id: The workspace to load data into.
        client_json: The full client onboarding configuration dict.

    Returns:
        Dict with:
            - status: "BLOCKED" or "READY".
            - review: Full validation and AI critic output.
            - sql: Transactional SQL string (empty string if BLOCKED).
    """
    review = review_client_onboarding(client_json)

    if review["hard_validation"]["status"] == "FAIL":
        return {
            "status": "BLOCKED",
            "review": review,
            "sql": "",
        }

    transaction_sql = emit_onboarding_transaction(
        workspace_id=workspace_id,
        salary_definitions=client_json.get("salary_definitions", []),
        payroll_rules=client_json.get("payroll_rules", []),
        employees=client_json.get("employees", []),
    )

    return {
        "status": "READY",
        "review": review,
        "sql": transaction_sql,
    }
