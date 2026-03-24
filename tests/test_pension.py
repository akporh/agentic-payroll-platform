"""
Unit tests for calculate_pension() in backend/domain/rules/pension.py.

Pure function tests — no database access required.
"""
from decimal import Decimal
import pytest

from backend.domain.rules.pension import calculate_pension


def test_standard_rates():
    """8% employee, 10% employer on 500,000 base (PRA 2014 defaults)."""
    emp, er = calculate_pension(
        Decimal("500000"),
        Decimal("0.08"),
        Decimal("0.10"),
    )
    assert emp == Decimal("40000.00")
    assert er  == Decimal("50000.00")


def test_custom_rates():
    """Custom 12% employee / 13% employer rates are applied correctly."""
    emp, er = calculate_pension(
        Decimal("400000"),
        Decimal("0.12"),
        Decimal("0.13"),
    )
    assert emp == Decimal("48000.00")
    assert er  == Decimal("52000.00")


def test_zero_base_returns_zero():
    """Zero pensionable base produces zero contributions."""
    emp, er = calculate_pension(Decimal("0"), Decimal("0.08"), Decimal("0.10"))
    assert emp == Decimal("0.00")
    assert er  == Decimal("0.00")


def test_rounding_half_up():
    """Fractional results are rounded to 2 decimal places (ROUND_HALF_UP)."""
    # 123456.789 × 0.08 = 9876.54312 → rounds to 9876.54
    emp, _ = calculate_pension(
        Decimal("123456.789"),
        Decimal("0.08"),
        Decimal("0.10"),
    )
    assert emp == Decimal("9876.54")


def test_employee_and_employer_are_independent():
    """Employee and employer contributions are calculated independently."""
    emp, er = calculate_pension(
        Decimal("300000"),
        Decimal("0.08"),
        Decimal("0.10"),
    )
    assert emp == Decimal("24000.00")
    assert er  == Decimal("30000.00")
    assert emp != er
