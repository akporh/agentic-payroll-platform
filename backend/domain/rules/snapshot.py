"""
Rules Context Snapshot Builder.

Captures a deterministic record of which statutory and payroll rules were
applied during a payroll run. This snapshot is stored on the PAYROLL_RUN
record to ensure calculations are reproducible and auditable.

No database access — payload construction only.

Reference: Phase 1 Business Spec — PAYROLL_RUN.rules_context_snapshot.
"""


def build_rules_context_snapshot(
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
) -> dict:
    """Build a rules context snapshot for a payroll run.

    Args:
        statutory_rule_id: Identifier of the statutory rule applied (e.g. PAYE).
        statutory_version: Version number of the statutory rule at time of run.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.

    Returns:
        Dict capturing the exact rules used, suitable for storing in
        PAYROLL_RUN.rules_context_snapshot.
    """
    return {
        "statutory_rule": {
            "id": statutory_rule_id,
            "version": statutory_version,
        },
        "payroll_rules": payroll_rule_ids,
    }
