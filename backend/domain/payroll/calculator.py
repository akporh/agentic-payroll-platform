"""
Net Pay Calculator Module.

Computes net pay by applying PAYE tax deductions to gross income.
This is a pure deterministic function with no database dependencies.

Reference: Phase 1 Business Spec — Payroll Calculation Pipeline.
"""

from decimal import Decimal
from backend.domain.rules.paye import calculate_paye


def calculate_net_pay(gross_income: Decimal, tax_bands: list[dict]) -> dict:
    """Calculate net pay after PAYE deduction.

    Args:
        gross_income: Total gross income for the period.
        tax_bands: Progressive tax brackets for PAYE calculation.
            See calculate_paye() for band format.

    Returns:
        Dict with keys:
            - gross (float): Original gross income.
            - paye (float): Computed PAYE tax.
            - net (float): Take-home pay (gross minus paye).

    Example:
        >>> result = calculate_net_pay(800000, tax_bands)
        >>> result["net"]
        716000.0
    """
    computed_tax = calculate_paye(gross_income, tax_bands)
    return {
        "gross": gross_income,
        "paye": computed_tax,
        "net": round(gross_income - computed_tax, 2),
    }
 