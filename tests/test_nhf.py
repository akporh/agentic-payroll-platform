"""
Unit tests for calculate_nhf() in backend/domain/rules/nhf.py.

Pure function tests — no database access required.
"""
from decimal import Decimal

from backend.domain.rules.nhf import calculate_nhf


def test_statutory_rate():
    """2.5% of BASIC = correct NHF amount (NHF Act statutory rate)."""
    result = calculate_nhf(Decimal("300000"), Decimal("0.025"))
    assert result == Decimal("7500.00")


def test_zero_basic_returns_zero():
    """Zero BASIC salary produces zero NHF contribution."""
    result = calculate_nhf(Decimal("0"), Decimal("0.025"))
    assert result == Decimal("0.00")


def test_rate_override_applied():
    """A custom rate (e.g. 2%) is applied correctly."""
    result = calculate_nhf(Decimal("200000"), Decimal("0.02"))
    assert result == Decimal("4000.00")


def test_rounding_half_up():
    """Fractional results are rounded to 2 decimal places."""
    # 100001 × 0.025 = 2500.025 → rounds to 2500.03
    result = calculate_nhf(Decimal("100001"), Decimal("0.025"))
    assert result == Decimal("2500.03")


def test_nhf_based_on_basic_only():
    """NHF uses the basic value passed in — the caller is responsible for
    passing only BASIC, not GROSS or any other component."""
    basic_only  = calculate_nhf(Decimal("300000"), Decimal("0.025"))
    gross_based = calculate_nhf(Decimal("500000"), Decimal("0.025"))
    # Basic-only (statutory) should be less than gross-based
    assert basic_only < gross_based
    assert basic_only == Decimal("7500.00")
