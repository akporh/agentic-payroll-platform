import csv


def export_payroll_register_csv(payroll_results: list[dict], output_path: str):
    """
    Phase 1 Payroll Register Export (Bureau Master Sheet)

    Columns:
    - employee_id
    - gross_pay
    - paye
    - pension (Phase 1 placeholder)
    - net_pay
    """

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow(
            ["employee_id", "gross_pay", "paye", "pension", "net_pay"]
        )

        for r in payroll_results:
            employee_id = r["employee_id"]

            payroll = r["payroll_result"]

            # Gross pay = sum of gross components
            gross_components = payroll["gross_components_jsonb"]
            gross_pay = sum(c["amount"] for c in gross_components)

            # PAYE deduction
            deductions = payroll["deductions_jsonb"]
            paye = deductions.get("PAYE", 0)

            # Pension placeholder (Phase 1 not implemented yet)
            pension = deductions.get("PENSION", 0)

            net_pay = payroll["net_pay"]

            writer.writerow(
                [employee_id, gross_pay, paye, pension, net_pay]
            )

