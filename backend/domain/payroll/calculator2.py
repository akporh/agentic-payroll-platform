from backend.domain.rules.paye import calculate_paye

def calculate_net_pay(gross_income: float, tax_bands: list[dict]) -> dict:
    paye = calculate_paye(gross_income, tax_bands)

    return {
        "gross": gross_income,
        "paye": paye,
        "net": gross_income - paye,
    }
