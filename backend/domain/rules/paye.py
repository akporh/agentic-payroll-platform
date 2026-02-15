def calculate_paye(gross_income: float, tax_bands: list[dict]) -> float:
    sorted_bands = sorted(tax_bands, key=lambda b: b["lower_limit"])
    total_tax = 0.0

    for band in sorted_bands:
        lower = band["lower_limit"]
        upper = band.get("upper_limit")
        rate = band["rate"]

        if gross_income <= lower:
            break

        if upper is None:
            taxable = gross_income - lower
        else:
            taxable = min(gross_income, upper) - lower

        total_tax += taxable * rate

    return round(total_tax, 2)
