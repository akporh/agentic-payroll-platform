"""
Salary Component Gross Summation Module.

Computes total gross pay from a list of salary components.
This is a pure deterministic function with no database dependencies.

Reference: Phase 1 Business Spec — SALARY_DEFINITION.components_jsonb.
"""


def calculate_gross(components: list[dict]) -> float:
    """Sum all salary component amounts to produce total gross pay.

    Args:
        components: List of salary component dicts. Each must contain:
            - code (str): Component identifier (e.g. "BASIC", "HOUSING").
            - amount (float): Monetary value for this component.

    Returns:
        Total gross pay as a float.

    Example:
        >>> components = [
        ...     {"code": "BASIC", "amount": 500000},
        ...     {"code": "HOUSING", "amount": 300000},
        ... ]
        >>> calculate_gross(components)
        800000.0
    """
    return float(sum(c["amount"] for c in components))
