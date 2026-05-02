"""Salary component derivation — pure function, no DB access.

Arch-council D5: isolated pure function called by both the payroll route and
the retry service so both paths produce identical salary_components.
Arch-council D6: grade pct wins when total_monthly is non-null.
Arch-council D7: round-half-up each component; adjust largest to absorb residual.
"""

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

logger = logging.getLogger(__name__)

_TWO_PLACES = Decimal("0.01")


def derive_salary_components(
    components_jsonb: dict,
    grade: Optional[dict],
) -> tuple[dict[str, Decimal], str]:
    """Derive the salary_components dict for a single employee.

    Args:
        components_jsonb: The raw dict from salary_definition.components_jsonb.
        grade: The grade row dict (with optional total_monthly / pct fields),
               or None if the employee has no grade assigned.

    Returns:
        (salary_components, salary_basis) where:
          salary_components — {component_code: Decimal}
          salary_basis      — "grade_percentage" or "salary_definition_absolute"
    """
    if grade is not None and grade.get("total_monthly") is not None:
        return _derive_from_grade_pct(components_jsonb, grade)
    return _derive_from_components_jsonb(components_jsonb), "salary_definition_absolute"


def _derive_from_components_jsonb(components_jsonb: dict) -> dict[str, Decimal]:
    return {
        code: Decimal(str(v["amount"] if isinstance(v, dict) else v))
        for code, v in components_jsonb.items()
    }


def _derive_from_grade_pct(
    components_jsonb: dict,
    grade: dict,
) -> tuple[dict[str, Decimal], str]:
    total = Decimal(str(grade["total_monthly"]))

    pct_map = {
        "BASIC":     Decimal(str(grade["basic_pct"])),
        "HOUSING":   Decimal(str(grade["housing_pct"])),
        "TRANSPORT": Decimal(str(grade["transport_pct"])),
        "UTILITY":   Decimal(str(grade["utility_pct"])),
    }

    # Warn if salary_definition also has non-zero amounts for these components
    for code, pct in pct_map.items():
        raw = components_jsonb.get(code)
        if raw is not None:
            raw_amount = Decimal(str(raw["amount"] if isinstance(raw, dict) else raw))
            if raw_amount != Decimal("0"):
                logger.warning(
                    "Grade pct and salary_definition both define %s — "
                    "grade pct takes precedence (D6)", code
                )

    # Derive each component and round to 2 decimal places
    derived: dict[str, Decimal] = {}
    for code, pct in pct_map.items():
        derived[code] = (total * pct).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    # Adjust largest component so derived values sum exactly to total_monthly (D7)
    residual = total - sum(derived.values())
    if residual != Decimal("0"):
        largest_code = max(derived, key=lambda c: derived[c])
        derived[largest_code] += residual

    # Pass through any additional components from components_jsonb that are not
    # in the pct_map (e.g. custom allowances defined on the salary_definition)
    for code, v in components_jsonb.items():
        if code not in derived:
            derived[code] = Decimal(str(v["amount"] if isinstance(v, dict) else v))

    return derived, "grade_percentage"
