"""
NHF (National Housing Fund) Contribution Calculation Module.

Implements employee NHF contribution under the National Housing Fund Act.
This is a pure deterministic function with no database dependencies.

Reference: National Housing Fund Act — 2.5% of basic salary per employee.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_nhf(basic: Decimal, rate: Decimal) -> Decimal:
    """Calculate employee NHF contribution.

    NHF_CONTRIBUTION = rate × BASIC salary.
    The statutory rate is 2.5% (0.025) per the NHF Act.

    Args:
        basic: Employee's basic salary for the period.
        rate: NHF contribution rate (default 0.025 = 2.5%).

    Returns:
        NHF contribution rounded to 2 decimal places.
    """
    return (Decimal(str(basic)) * Decimal(str(rate))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
