"""
Payroll Result Builder Module.

Assembles a complete Phase 1 PAYROLL_RESULT payload from salary components
and tax bands. Combines gross summation, PAYE calculation, and net pay into
the structure expected by the payroll_result table.

This is a pure deterministic function with no database dependencies.
All monetary values are Decimal throughout — no floats in the pipeline.

Reference: Phase 1 Business Spec — PAYROLL_RESULT schema.
"""

from backend.domain.payroll.salary import calculate_gross
from backend.domain.payroll.calculator import calculate_net_pay


def build_payroll_result(
    components: list[dict],
    tax_bands: list[dict],
) -> dict:
    """Build a complete payroll result payload for one employee.

    Orchestrates the full calculation pipeline:
    1. Sum salary components to get gross pay.
    2. Apply PAYE tax bands to compute deductions.
    3. Derive net pay.

    All monetary values in the returned dict are Decimal.

    Args:
        components: Salary component dicts with "code" and "amount" keys.
        tax_bands: Progressive tax brackets for PAYE calculation.
            See calculate_paye() for band format.

    Returns:
        Dict matching the Phase 1 PAYROLL_RESULT schema:
            - gross_components_jsonb: Original salary components.
            - deductions_jsonb: Applied deductions (currently PAYE only).
            - net_pay (Decimal): Final take-home amount.
            - calculations_snapshot_json: Full breakdown for audit trail.

    Example:
        >>> result = build_payroll_result(components, tax_bands)
        >>> result["net_pay"]
        Decimal('716000.00')
    """
    gross = calculate_gross(components)
    pay_result = calculate_net_pay(gross, tax_bands)
    paye = pay_result["paye"]
    net = pay_result["net"]

    return {
        "gross_components_jsonb": {
            component["code"]: {
                "amount": component["amount"]
            }
            for component in components
        },
        "deductions_jsonb": {"PAYE": paye},
        "net_pay": net,
        "calculations_snapshot_json": {
            "gross": gross,
            "paye": paye,
            "net": net,
        },
    }
