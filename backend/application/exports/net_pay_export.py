"""
Net Pay CSV Export Module.

Generates a CSV file listing each employee and their net (take-home) pay
for a completed payroll run. Intended for Phase 1 manual bank upload
workflows where the bureau needs a simple employee-to-amount mapping.

No database access — reads from in-memory payroll result dicts only.

Reference: Phase 1 Business Spec — Manual Export Requirements.
"""

import csv


def export_net_pay_csv(payroll_results: list[dict], output_path: str):
    """Export a net pay CSV for all employees in a payroll run.

    Writes a two-column CSV (employee_id, net_pay) to the specified path.

    Args:
        payroll_results: List of per-employee result dicts as produced by
            execute_payroll_run_pure. Each dict must contain:
            - employee_id (str): The employee identifier.
            - payroll_result (dict): Must include "net_pay" (Decimal).
        output_path: File path where the CSV will be written.
    """
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "net_pay"])

        for r in payroll_results:
            writer.writerow([r["employee_id"], r["payroll_result"]["net_pay"]])

