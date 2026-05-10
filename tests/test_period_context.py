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


# ---------------------------------------------------------------------------
# strategy="fixed_30"
#
# Month is treated as exactly 30 days. Day 31 of a 31-day month is phantom
# and is never counted as active or missed. Termination date is inclusive.
# Formula: (30 − missed_days_before_hire − missed_days_after_term) / 30
#
# March 2026 reference: period 2026-03-01 → 2026-03-31, 31 calendar days,
#   22 working days (March 1 is Sunday).
# ---------------------------------------------------------------------------

class TestHireTerminationFactorFixed30:

    @pytest.fixture
    def march_ctx(self):
        return build_period_context("2026-03-01", "2026-03-31")

    @pytest.fixture
    def feb_ctx(self):
        return build_period_context("2026-02-01", "2026-02-28")

    def test_full_period_returns_one(self, march_ctx):
        """Pre-period hire with open contract is full-period — early-return path."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2025, 1, 1),
            contract_end=None,
            strategy="fixed_30",
        )
        assert factor == Decimal("1")

    def test_no_dates_returns_one(self, march_ctx):
        """No contract dates → factor = 1 regardless of strategy."""
        factor = compute_hire_termination_factor(
            march_ctx, None, None, strategy="fixed_30"
        )
        assert factor == Decimal("1")

    def test_march_4_hire_hp1(self, march_ctx):
        """HP-1 acceptance criterion: March 4 hire, fixed_30 → 27/30 = 0.9.

        Missed days = Mar 1, 2, 3 (3 days). Day 31 is phantom.
        Active positions 4–30 = 27 days.
        """
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 4),
            contract_end=None,
            strategy="fixed_30",
        )
        assert factor == Decimal("0.900000")

    def test_termination_march_15(self, march_ctx):
        """Terminated March 15 (inclusive): positions 1–15 = 15/30 = 0.5."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=None,
            contract_end=date(2026, 3, 15),
            strategy="fixed_30",
        )
        assert factor == Decimal("0.500000")

    def test_hire_and_termination_same_period(self, march_ctx):
        """March 4 hire, terminated March 15: positions 4–15 = 12/30."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 4),
            contract_end=date(2026, 3, 15),
            strategy="fixed_30",
        )
        expected = (Decimal("12") / Decimal("30")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_day_31_is_phantom(self, march_ctx):
        """Hired on day 31 of a 31-day month → 0/30.

        Position 31 is the phantom day and is never counted as active.
        """
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 31),
            contract_end=None,
            strategy="fixed_30",
        )
        assert factor == Decimal("0")

    def test_hired_march_2_one_missed_day(self, march_ctx):
        """Hired March 2 in a 31-day month: position 2–30 = 29/30."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 2),
            contract_end=None,
            strategy="fixed_30",
        )
        expected = (Decimal("29") / Decimal("30")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_february_hire_28_day_month(self, feb_ctx):
        """Feb 4 hire in a 28-day month: positions 4–28 = 25/30.

        fixed_30 always uses denominator 30 regardless of actual month length.
        """
        factor = compute_hire_termination_factor(
            feb_ctx,
            contract_start=date(2026, 2, 4),
            contract_end=None,
            strategy="fixed_30",
        )
        expected = (Decimal("25") / Decimal("30")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_factor_capped_at_one(self, march_ctx):
        """Factor is always ≤ 1 — cap enforced by min()."""
        factor = compute_hire_termination_factor(
            march_ctx, None, None, strategy="fixed_30"
        )
        assert factor <= Decimal("1")


# ---------------------------------------------------------------------------
# strategy="calendar_days"
#
# Formula: calendar_days_active / period.calendar_days
# Both numerator and denominator count every calendar day (Mon–Sun inclusive).
#
# March 2026: 31 calendar days.
# February 2026: 28 calendar days.
# ---------------------------------------------------------------------------

class TestHireTerminationFactorCalendarDays:

    @pytest.fixture
    def march_ctx(self):
        return build_period_context("2026-03-01", "2026-03-31")

    def test_full_period_returns_one(self, march_ctx):
        """Pre-period hire with open contract → full period → early-return 1."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2025, 1, 1),
            contract_end=None,
            strategy="calendar_days",
        )
        assert factor == Decimal("1")

    def test_march_4_hire_hp2(self, march_ctx):
        """HP-2 acceptance criterion: March 4 hire, calendar_days → 28/31.

        Active calendar days Mar 4–31 = 28. Period has 31 calendar days.
        """
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 4),
            contract_end=None,
            strategy="calendar_days",
        )
        expected = (Decimal("28") / Decimal("31")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_termination_march_15(self, march_ctx):
        """Terminated March 15: active Mar 1–15 = 15 calendar days / 31."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=None,
            contract_end=date(2026, 3, 15),
            strategy="calendar_days",
        )
        expected = (Decimal("15") / Decimal("31")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_hire_and_termination_same_period(self, march_ctx):
        """March 10 hire, terminated March 20: 11 calendar days / 31."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 10),
            contract_end=date(2026, 3, 20),
            strategy="calendar_days",
        )
        expected = (Decimal("11") / Decimal("31")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_single_day_hire(self, march_ctx):
        """Hired and terminated on March 1: 1 calendar day / 31."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 1),
            contract_end=date(2026, 3, 1),
            strategy="calendar_days",
        )
        # active_from == period_start but active_to != period_end → no early return
        expected = (Decimal("1") / Decimal("31")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_day_31_counts_as_active(self, march_ctx):
        """Unlike fixed_30, day 31 is real in calendar_days. March 31 hire = 1/31."""
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 31),
            contract_end=None,
            strategy="calendar_days",
        )
        expected = (Decimal("1") / Decimal("31")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_factor_capped_at_one(self, march_ctx):
        """Factor is always ≤ 1."""
        factor = compute_hire_termination_factor(
            march_ctx, None, None, strategy="calendar_days"
        )
        assert factor <= Decimal("1")


# ---------------------------------------------------------------------------
# strategy="work_days" — explicit parameter tests
#
# Regression guard for HP-3: explicit strategy='work_days' must produce
# exactly the same result as the default (no strategy argument).
# ---------------------------------------------------------------------------

class TestHireTerminationFactorWorkDaysExplicit:

    @pytest.fixture
    def march_ctx(self):
        return build_period_context("2026-03-01", "2026-03-31")

    def test_hp3_explicit_matches_default(self, march_ctx):
        """HP-3: strategy='work_days' is identical to the pre-sprint default."""
        default = compute_hire_termination_factor(
            march_ctx, contract_start=date(2026, 3, 16), contract_end=None
        )
        explicit = compute_hire_termination_factor(
            march_ctx, contract_start=date(2026, 3, 16), contract_end=None,
            strategy="work_days",
        )
        assert default == explicit

    def test_march_16_hire_work_days(self, march_ctx):
        """March 16 hire (Monday): 12 working days active / 22 total.

        Active working days Mar 16–31:
          Mar 16,17,18,19,20 (5) + Mar 23,24,25,26,27 (5) + Mar 30,31 (2) = 12
        """
        factor = compute_hire_termination_factor(
            march_ctx,
            contract_start=date(2026, 3, 16),
            contract_end=None,
            strategy="work_days",
        )
        expected = (Decimal("12") / Decimal("22")).quantize(Decimal("0.000001"))
        assert factor == expected

    def test_unknown_strategy_falls_back_to_work_days(self, march_ctx):
        """Unrecognised strategy string falls through the else-branch (work_days)."""
        work_days_result = compute_hire_termination_factor(
            march_ctx, contract_start=date(2026, 3, 16), contract_end=None,
            strategy="work_days",
        )
        unknown_result = compute_hire_termination_factor(
            march_ctx, contract_start=date(2026, 3, 16), contract_end=None,
            strategy="nonexistent_strategy",
        )
        assert unknown_result == work_days_result


# ---------------------------------------------------------------------------
# Cross-strategy comparison
#
# For a mid-period hire, each strategy produces a distinct factor.
# Verifies all three branches are active and produces no accidental equality.
# ---------------------------------------------------------------------------

class TestHireTerminationFactorStrategyComparison:

    def test_three_strategies_give_distinct_factors_for_march_4_hire(self):
        """March 4 hire in March 2026 — each strategy produces a unique factor.

        work_days:     20 / 22 ≈ 0.909091  (Wed 4 → Tue 31 = 20 working days)
        calendar_days: 28 / 31 ≈ 0.903226  (28 calendar days active)
        fixed_30:      27 / 30  = 0.900000  (3 missed days; day 31 phantom)

        Ordering: work_days > calendar_days > fixed_30
        """
        ctx = build_period_context("2026-03-01", "2026-03-31")
        hire = date(2026, 3, 4)

        f_work = compute_hire_termination_factor(ctx, hire, None, strategy="work_days")
        f_cal  = compute_hire_termination_factor(ctx, hire, None, strategy="calendar_days")
        f_fixed = compute_hire_termination_factor(ctx, hire, None, strategy="fixed_30")

        assert f_fixed == Decimal("0.900000")
        assert f_cal  == (Decimal("28") / Decimal("31")).quantize(Decimal("0.000001"))
        assert f_work == (Decimal("20") / Decimal("22")).quantize(Decimal("0.000001"))

        assert f_work > f_cal > f_fixed

    def test_full_period_all_strategies_return_one(self):
        """Full-period employee returns 1 for every strategy — early-return path."""
        ctx = build_period_context("2026-03-01", "2026-03-31")
        for strategy in ("work_days", "calendar_days", "fixed_30"):
            factor = compute_hire_termination_factor(
                ctx,
                contract_start=date(2025, 6, 1),
                contract_end=None,
                strategy=strategy,
            )
            assert factor == Decimal("1"), f"strategy={strategy} did not return 1"

    def test_contract_before_period_all_strategies_return_zero(self):
        """Contract ended before period — returns 0 regardless of strategy."""
        ctx = build_period_context("2026-03-01", "2026-03-31")
        for strategy in ("work_days", "calendar_days", "fixed_30"):
            factor = compute_hire_termination_factor(
                ctx,
                contract_start=date(2025, 1, 1),
                contract_end=date(2026, 2, 28),
                strategy=strategy,
            )
            assert factor == Decimal("0"), f"strategy={strategy} did not return 0"
