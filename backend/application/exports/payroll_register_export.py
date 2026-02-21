"""
Payroll Register CSV Export Module.

Generates the bureau master sheet — a full payroll register CSV with
gross pay, PAYE deduction, pension deduction, and net pay for every
employee in a completed payroll run.

Pension is included as a Phase 1 placeholder (defaults to 0 until
pension rules are fully implemented).

No database access — reads from in-memory payroll result dicts only.

Reference: Phase 1 Business Spec — Bureau Master Sheet Export.
"""

import csv
from decimal import Decimal


def export_payroll_register_csv(payroll_results: list[dict], output_path: str):
    """Export a full payroll register CSV for a completed run.

    Writes a CSV with columns:
    employee_id, gross_pay, paye, pension, net_pay.

    Args:
        payroll_results: List of per-employee result dicts as produced by
            execute_payroll_run_pure. Each dict must contain:
            - employee_id (str): The employee identifier.
            - payroll_result (dict): Must include:
                - gross_components_jsonb (list[dict]): Salary components
                  with "amount" keys.
                - deductions_jsonb (dict): Must include "PAYE" key;
                  "PENSION" key used if present (defaults to 0).
                - net_pay (Decimal): Final take-home amount.
        output_path: File path where the CSV will be written.
    """
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(
            ["employee_id", "gross_pay", "paye", "pension", "net_pay"]
        )

        for r in payroll_results:
            employee_id = r["employee_id"]

            payroll = r["payroll_result"]

            gross_components = payroll["gross_components_jsonb"]
            gross_pay = sum(
                (Decimal(str(c["amount"])) for c in gross_components),
                Decimal("0"),
            )

            deductions = payroll["deductions_jsonb"]
            paye = Decimal(str(deductions.get("PAYE", 0)))

            pension = Decimal(str(deductions.get("PENSION", 0)))

            net_pay = payroll["net_pay"]

            writer.writerow(
                [employee_id, gross_pay, paye, pension, net_pay]
            )

