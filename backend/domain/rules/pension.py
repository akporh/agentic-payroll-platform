"""
Pension Contribution Calculation Module.

Implements Nigerian PRA 2014 pension contribution computation.
Pure deterministic function with no database dependencies.

Reference: PRA 2014 — Pension Reform Act, Nigeria.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_pension(
    pensionable_base: Decimal,
    employee_rate: Decimal,
    employer_rate: Decimal,
) -> tuple[Decimal, Decimal]:
    """Calculate employee and employer pension contributions.

    Args:
        pensionable_base: Sum of BASIC + HOUSING + TRANSPORT for the period.
        employee_rate: Employee contribution rate (e.g. Decimal("0.08") = 8%).
        employer_rate: Employer contribution rate (e.g. Decimal("0.10") = 10%).

    Returns:
        Tuple of (employee_contribution, employer_contribution), each rounded to 2dp.
    """
    base = Decimal(str(pensionable_base))
    emp_rate = Decimal(str(employee_rate))
    er_rate = Decimal(str(employer_rate))

    employee_contribution = (base * emp_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    employer_contribution = (base * er_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return employee_contribution, employer_contribution
