import csv


def export_net_pay_csv(payroll_results: list[dict], output_path: str):
    """
    Phase 1 manual export:
    Employee → Net Pay
    """

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "net_pay"])

        for r in payroll_results:
            writer.writerow([r["employee_id"], r["payroll_result"]["net_pay"]])

