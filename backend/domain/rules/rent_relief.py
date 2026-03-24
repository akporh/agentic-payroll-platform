"""
Rent Relief Calculation.

Calculates the monthly rent relief deduction from taxable income under
the Nigeria Tax Act 2025.  Pure deterministic function — no DB access.

Rate and cap are read from statutory_rule.rules_jsonb.reliefs.rent_relief
and passed in by the caller.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_rent_relief_for_period(
    annual_rent_paid:     Decimal,
    rate:                 Decimal,
    cap:                  Decimal,
    annualization_factor: Decimal,
) -> Decimal:
    """Calculate rent relief for an arbitrary pay period.

    For a MONTHLY period with annualization_factor=12 this is numerically
    identical to calculate_rent_relief().

    Args:
        annual_rent_paid:     Employee-declared annual rent payment.
        rate:                 Relief rate from statutory config (e.g. 0.20).
        cap:                  Maximum annual relief allowed.
        annualization_factor: 12 for monthly, 26 for fortnightly, etc.

    Returns:
        Period rent relief rounded to 2 decimal places.
    """
    annual_relief = min(annual_rent_paid * rate, cap)
    return (annual_relief / annualization_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_rent_relief(
    annual_rent_paid: Decimal,
    rate: Decimal,
    cap: Decimal,
) -> Decimal:
    """Calculate monthly rent relief from annual rent paid.

    Args:
        annual_rent_paid: Employee-declared annual rent payment (from payroll_input).
        rate: Relief rate from statutory config (e.g. 0.20 = 20%).
        cap:  Maximum annual relief allowed (e.g. 500000).

    Returns:
        Monthly rent relief amount, rounded to 2 decimal places.
    """
    annual_relief = min(annual_rent_paid * rate, cap)
    return (annual_relief / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
