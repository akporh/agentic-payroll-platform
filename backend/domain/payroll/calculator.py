"""
Net Pay Calculator Module.

Computes net pay by applying PAYE tax deductions to gross income.
This is a pure deterministic function with no database dependencies.

Reference: Phase 1 Business Spec — Payroll Calculation Pipeline.
"""

from decimal import Decimal, ROUND_HALF_UP
from backend.domain.rules.paye import calculate_paye
from backend.application.trace_decorators import trace_step


@trace_step("Calculate net pay (PAYE)")
def calculate_net_pay(gross_income: Decimal, tax_bands: list[dict], *, tracer=None) -> dict:
    """Calculate net pay after PAYE deduction.

    Args:
        gross_income: Total gross income as Decimal.
        tax_bands: Progressive tax brackets for PAYE calculation.
            See calculate_paye() for band format.
        tracer: Optional ExecutionTracer for structured trace output.

    Returns:
        Dict with Decimal values:
            - gross (Decimal): Original gross income.
            - paye (Decimal): Computed PAYE tax.
            - net (Decimal): Take-home pay (gross minus paye).

    Example:
        >>> result = calculate_net_pay(Decimal("800000"), tax_bands)
        >>> result["net"]
        Decimal('716000.00')
    """
    gross = Decimal(str(gross_income))
    computed_tax = calculate_paye(gross, tax_bands)
    net = (gross - computed_tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "gross": gross,
        "paye": computed_tax,
        "net": net,
    }
