"""
Salary Component Gross Summation Module.

Computes total gross pay from a list of salary components.
This is a pure deterministic function with no database dependencies.

Reference: Phase 1 Business Spec — SALARY_DEFINITION.components_jsonb.
"""


from decimal import Decimal

from backend.application.trace_decorators import trace_step


@trace_step("Calculate gross pay")
def calculate_gross(components: list[dict], *, tracer=None) -> Decimal:
    """Sum all salary component amounts to produce total gross pay.

    Args:
        components: List of salary component dicts. Each must contain:
            - code (str): Component identifier (e.g. "BASIC", "HOUSING").
            - amount (Decimal|int|float): Monetary value for this component.
        tracer: Optional ExecutionTracer for structured trace output.

    Returns:
        Total gross pay as Decimal.

    Example:
        >>> components = [
        ...     {"code": "BASIC", "amount": 500000},
        ...     {"code": "HOUSING", "amount": 300000},
        ... ]
        >>> calculate_gross(components)
        Decimal('800000')
    """
    return sum(
        (Decimal(str(c["amount"] if isinstance(c, dict) else c)) for c in components),
        Decimal("0"),
    )
