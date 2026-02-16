"""
Batch Payroll Run Processor.

Processes payroll for multiple employees within a single PAYROLL_RUN
by delegating to the single-employee executor and aggregating results.

No database writes — pure computation only.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from backend.domain.payroll.executor import execute_single_employee_payroll


def process_payroll_run(
    payroll_run_id: str,
    employees: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
) -> dict:
    """Process payroll for all employees in a single payroll run.

    Iterates through each employee, executes a deterministic payroll
    calculation, and aggregates results with totals.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        employees: List of employee dicts, each with "employee_id" and
            "components" (list of salary component dicts).
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.

    Returns:
        Dict containing:
            - payroll_run_id: The run identifier.
            - results: List of per-employee execution outputs.
            - totals: Aggregated totals including total_net_pay.
    """
    results = []
    for emp in employees:
        result = execute_single_employee_payroll(
            payroll_run_id=payroll_run_id,
            employee_id=emp["employee_id"],
            components=emp["components"],
            tax_bands=tax_bands,
            statutory_rule_id=statutory_rule_id,
            statutory_version=statutory_version,
            payroll_rule_ids=payroll_rule_ids,
            performed_by=performed_by,
        )
        results.append(result)

    total_net_pay = sum(r["payroll_result"]["net_pay"] for r in results)

    return {
        "payroll_run_id": payroll_run_id,
        "results": results,
        "totals": {
            "total_net_pay": total_net_pay,
        },
    }
