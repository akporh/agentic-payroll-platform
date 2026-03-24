"""
Unit tests for build_period_context() and compute_hire_termination_factor()
in backend/domain/payroll/period_context.py.

Pure function tests — no database access required.

Date arithmetic notes:
  March 2026:  starts Sunday 1st.  Working days = 22 (Mon 2 → Tue 31).
  February 2026: starts Sunday 1st. Working days = 20 (Mon 2 → Fri 27).
"""
from datetime import date
from decimal import Decimal

import pytest

from backend.domain.payroll.period_context import (
    PeriodContext,
    PeriodType,
    build_period_context,
    compute_hire_termination_factor,
)


# ---------------------------------------------------------------------------
# build_period_context
# ---------------------------------------------------------------------------

class TestBuildPeriodContext:
    def test_monthly_type_inferred(self):
        ctx = build_period_context(
            period_start="2026-03-01",
            period_end="2026-03-31",
        )
        assert ctx.period_type == PeriodType.MONTHLY

    def test_monthly_annualization_factor(self):
        ctx = build_period_context("2026-03-01", "2026-03-31")
        assert ctx.annualization_factor == Decimal("12")

    def test_monthly_period_fraction(self):
        ctx = build_period_context("2026-03-01", "2026-03-31")
        # 1 / 12 = 0.083333...
        assert ctx.period_fraction == (Decimal("1") / Decimal("12")).quantize(
            Decimal("0.000001")
        )

    def test_march_2026_working_days(self):
        """March 2026 has 22 Mon–Fri days (starts Sunday)."""
        ctx = build_period_context("2026-03-01", "2026-03-31")
        assert ctx.working_days == 22

    def test_february_2026_working_days(self):
        """February 2026 has 20 Mon–Fri days (28 days, starts Sunday)."""
        ctx = build_period_context("2026-02-01", "2026-02-28")
        assert ctx.working_days == 20

    def test_calendar_days_correct(self):
        ctx = build_period_context("2026-03-01", "2026-03-31")
        assert ctx.calendar_days == 31

    def test_fortnightly_type_inferred(self):
        """14-day span resolves to FORTNIGHTLY."""
        ctx = build_period_context("2026-03-01", "2026-03-14")
        assert ctx.period_type == PeriodType.FORTNIGHTLY

    def test_fortnightly_annualization_factor(self):
        ctx = build_period_context("2026-03-01", "2026-03-14")
        assert ctx.annualization_factor == Decimal("26")

    def test_period_type_explicit_override(self):
        """Explicitly passing period_type='MONTHLY' overrides inference."""
        ctx = build_period_context(
            "2026-03-01", "2026-03-31", period_type="monthly"
        )
        assert ctx.period_type == PeriodType.MONTHLY

    def test_working_days_override(self):
        """Caller can override the working-day count (e.g. client convention)."""
        ctx = build_period_context(
            "2026-03-01", "2026-03-31",
            working_days_override=20,
        )
        assert ctx.working_days == 20

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError, match="must not precede"):
            build_period_context("2026-03-31", "2026-03-01")

    def test_date_objects_accepted(self):
        """build_period_context accepts date objects, not just strings."""
        ctx = build_period_context(
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        assert ctx.period_start == date(2026, 3, 1)
        assert ctx.period_end   == date(2026, 3, 31)

    def test_returns_frozen_dataclass(self):
        ctx = build_period_context("2026-03-01", "2026-03-31")
        assert isinstance(ctx, PeriodContext)
        with pytest.raises((AttributeError, TypeError)):
            ctx.working_days = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# compute_hire_termination_factor
# ---------------------------------------------------------------------------

class TestHireTerminationFactor:

    @pytest.fixture
    def march_ctx(self):
        return build_period_context("2026-03-01", "2026-03-31")

    def test_full_period_returns_one(self, march_ctx):
        """Employee contracted before period and still active → factor = 1."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2025, 1, 1),
            contract_end=None,
        )
        assert factor == Decimal("1")

    def test_no_dates_returns_one(self, march_ctx):
        """No contract dates → factor = 1 (covers full period)."""
        factor = compute_hire_termination_factor(march_ctx, None, None)
        assert factor == Decimal("1")

    def test_hire_mid_month(self, march_ctx):
        """Hired Monday 16 Mar 2026 → 12 working days out of 22."""
        # Mar 16–31 working days: 16,17,18,19,20 + 23,24,25,26,27 + 30,31 = 12
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 16),
            contract_end=None,
        )
        expected = (Decimal("12") / Decimal("22")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_termination_mid_month(self, march_ctx):
        """Terminated Sunday 15 Mar 2026 → 10 working days out of 22."""
        # Mar 1–15 working days: Mar 1 is Sunday so Mon 2–6 (5) + Mon 9–13 (5) = 10
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=None,
            contract_end=date(2026, 3, 15),
        )
        expected = (Decimal("10") / Decimal("22")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_contract_ends_before_period_returns_zero(self, march_ctx):
        """Contract ended before the period started → factor = 0."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2025, 1, 1),
            contract_end=date(2026, 2, 28),
        )
        assert factor == Decimal("0")

    def test_contract_starts_after_period_returns_zero(self, march_ctx):
        """Contract starts after the period ends → factor = 0."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 4, 1),
            contract_end=None,
        )
        assert factor == Decimal("0")
