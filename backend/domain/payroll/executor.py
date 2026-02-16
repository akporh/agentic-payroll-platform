"""
Single Employee Payroll Executor.

Orchestrates a complete deterministic payroll calculation for one employee,
combining the payroll result and rules context snapshot into a single
Phase 1-ready output payload.

No database writes — pure computation only.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from backend.domain.payroll.result_builder import build_payroll_result
from backend.domain.rules.snapshot import build_rules_context_snapshot


def execute_single_employee_payroll(
    payroll_run_id: str,
    employee_id: str,
    components: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
) -> dict:
    """Execute a full payroll calculation for a single employee.

    Combines:
    1. Payroll result (gross, PAYE, net) from salary components and tax bands.
    2. Rules context snapshot recording which rules were applied.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        employee_id: Unique identifier of the employee.
        components: Salary component dicts with "code" and "amount" keys.
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.

    Returns:
        Dict containing:
            - payroll_run_id: The run this result belongs to.
            - employee_id: The employee this result is for.
            - rules_context_snapshot: Captured rules at time of calculation.
            - payroll_result: Full calculation output (gross, deductions, net).
    """
    payroll_result = build_payroll_result(components, tax_bands)
    rules_snapshot = build_rules_context_snapshot(
        statutory_rule_id, statutory_version, payroll_rule_ids
    )

    return {
        "payroll_run_id": payroll_run_id,
        "employee_id": employee_id,
        "rules_context_snapshot": rules_snapshot,
        "payroll_result": payroll_result,
    }
