import csv


def export_paye_summary_csv(payroll_results: list[dict], output_path: str):
    """
    Phase 1 Compliance Export:
    Employee → PAYE deduction

    Assumes deductions_jsonb contains {"PAYE": amount}
    """

    total_paye = 0

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "paye_amount"])

        for r in payroll_results:
            employee_id = r["employee_id"]

            deductions = r["payroll_result"]["deductions_jsonb"]
            paye = deductions.get("PAYE", 0)

            total_paye += paye
            writer.writerow([employee_id, paye])

        # Footer row
        writer.writerow([])
        writer.writerow(["TOTAL_PAYE", total_paye])

