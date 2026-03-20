"""
PAYE (Pay-As-You-Earn) Tax Calculation Module.

Implements Nigerian PAYE tax computation using progressive tax bands.
This is a pure deterministic function with no database dependencies.

Reference: Phase 1 Business Spec — Statutory Deductions (PAYE).
"""
from decimal import Decimal, ROUND_HALF_UP

print("Loaded PAYE from:", __file__)

def calculate_paye(gross_income: Decimal, tax_bands: list[dict]) -> Decimal:
    """Calculate PAYE tax using progressive tax band brackets.

    Applies each tax band sequentially to the relevant portion of gross income.
    Bands are sorted by lower_limit to ensure correct bracket ordering.

    Args:
        gross_income: Total taxable gross income for the period.
        tax_bands: Ordered list of tax brackets. Each dict must contain:
            - lower_limit (float): Start of the bracket (inclusive).
            - upper_limit (float | None): End of the bracket (exclusive).
              None indicates an unbounded top bracket.
            - rate (float): Tax rate for this bracket (e.g. 0.07 = 7%).

    Returns:
        Total PAYE tax amount, rounded to 2 decimal places.

    Example:
        >>> bands = [
        ...     {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
        ...     {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
        ...     {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
        ... ]
        >>> calculate_paye(800000, bands)
        84000.0
    """
    gross = Decimal(str(gross_income))
    sorted_bands = sorted(tax_bands, key=lambda b: b["lower_limit"])
    total_tax = Decimal("0")

    for band in sorted_bands:
        lower = Decimal(str(band["lower_limit"]))
        upper = Decimal(str(band["upper_limit"])) if band.get("upper_limit") is not None else None
        rate = Decimal(str(band["rate"]))

        if gross <= lower:
            break

        if upper is None:
            taxable = gross - lower
        else:
            taxable = min(gross, upper) - lower

        total_tax += taxable * rate

    return total_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_monthly_paye(
    monthly_taxable_income: Decimal,
    tax_bands: list[dict],
) -> Decimal:
    """Calculate monthly PAYE by annualising taxable income and applying bands.

    Nigeria PAYE is assessed on annual income. All pre-PAYE reductions
    (pension, reliefs) are computed upstream by the sequential executor
    and reflected in monthly_taxable_income before this is called.

    Steps:
      1. Annualise taxable income (× 12).
      2. Apply progressive tax bands to annual taxable income.
      3. Return monthly PAYE (annual ÷ 12).

    Args:
        monthly_taxable_income: Already-reduced monthly taxable income
            (GROSS_PAY − PENSION_EMPLOYEE − any reliefs like RENT_RELIEF).
        tax_bands: Progressive FIRS tax brackets (same format as calculate_paye).

    Returns:
        Monthly PAYE rounded to 2 decimal places.
    """
    annual_taxable = monthly_taxable_income * 12
    annual_paye = calculate_paye(annual_taxable, tax_bands)
    return (annual_paye / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
