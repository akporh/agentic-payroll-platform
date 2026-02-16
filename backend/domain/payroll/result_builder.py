from backend.domain.payroll.salary import calculate_gross
from backend.domain.payroll.calculator import calculate_net_pay


def build_payroll_result(
    components: list[dict],
    tax_bands: list[dict],
) -> dict:
    gross = calculate_gross(components)
    pay_result = calculate_net_pay(gross, tax_bands)
    paye = pay_result["paye"]
    net = pay_result["net"]

    return {
        "gross_components_jsonb": components,
        "deductions_jsonb": {"PAYE": paye},
        "net_pay": net,
        "calculations_snapshot_json": {
            "gross": gross,
            "paye": paye,
            "net": net,
        },
    }
