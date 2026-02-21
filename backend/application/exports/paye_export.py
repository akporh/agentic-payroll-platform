"""
PAYE Summary CSV Export Module.

Generates a compliance-ready CSV listing each employee's PAYE tax
deduction and a total across all employees. Used by the payroll bureau
to prepare PAYE remittance filings with the Federal Inland Revenue
Service (FIRS).

No database access — reads from in-memory payroll result dicts only.

Reference: Phase 1 Business Spec — Statutory Compliance Exports.
"""

import csv
from decimal import Decimal


def export_paye_summary_csv(payroll_results: list[dict], output_path: str):
    """Export a PAYE summary CSV with per-employee deductions and a total.

    Writes a CSV with columns (employee_id, paye_amount) followed by a
    blank row and a TOTAL_PAYE footer row.

    Args:
        payroll_results: List of per-employee result dicts as produced by
            execute_payroll_run_pure. Each dict must contain:
            - employee_id (str): The employee identifier.
            - payroll_result (dict): Must include "deductions_jsonb" with
              a "PAYE" key holding the deduction amount (Decimal).
        output_path: File path where the CSV will be written.
    """
    total_paye = Decimal("0")

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "paye_amount"])

        for r in payroll_results:
            employee_id = r["employee_id"]

            deductions = r["payroll_result"]["deductions_jsonb"]
            paye = Decimal(str(deductions.get("PAYE", 0)))

            total_paye += paye
            writer.writerow([employee_id, paye])

        writer.writerow([])
        writer.writerow(["TOTAL_PAYE", total_paye])

