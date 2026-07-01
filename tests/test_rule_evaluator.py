"""
Unit tests for apply_payroll_rules() in backend/domain/payroll/rule_evaluator.py.

Pure function tests — no database access required.

All monetary values use Decimal. The rule evaluator is called by the payroll
service BEFORE the sequential executor — it modifies salary_components by
adding earnings (unit_multiplier) or reducing proratable components
(daily_rate_deduction).
"""
from datetime import date
from decimal import Decimal

import pytest

from backend.domain.payroll.rule_evaluator import (
    apply_payroll_rules,
    _resolve_rule,
    _resolve_period_ctx,
    NoHistoricalRuleVersionError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rule(name, method, **kwargs):
    """Build a minimal payroll rule dict."""
    return {
        "rule_name": name,
        "is_active": True,
        "rule_definition_json": {"calculation_method": method, **kwargs},
    }


def _inactive_rule(name, method):
    return {"rule_name": name, "is_active": False,
            "rule_definition_json": {"calculation_method": method}}


# ---------------------------------------------------------------------------
# unit_multiplier
# ---------------------------------------------------------------------------

class TestUnitMultiplier:

    def test_applied_when_input_present(self):
        """3 overtime days × ₦5,000/day → OVERTIME_PAY = 15,000."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000, unit="days")],
            employee_inputs={"overtime_days": 3},
            client_meta={},
        )
        assert components["OVERTIME_PAY"] == Decimal("15000.00")
        assert trace[0]["status"] == "applied"
        assert trace[0]["amount"] == "15000.00"

    def test_not_applied_when_input_absent(self):
        """No overtime_days in inputs → rule skipped."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000)],
            employee_inputs={},
            client_meta={},
        )
        assert "OVERTIME_PAY" not in components
        assert trace[0]["status"] == "not_applied"

    def test_not_applied_when_input_is_zero(self):
        """overtime_days=0 → rule skipped (input_val > 0 guard)."""
        components, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000)],
            employee_inputs={"overtime_days": 0},
            client_meta={},
        )
        assert "OVERTIME_PAY" not in components
        assert trace[0]["status"] == "not_applied"

    def test_existing_component_overwritten(self):
        """If the component already exists, the rule overwrites it."""
        components, _ = apply_payroll_rules(
            salary_components={"OVERTIME_PAY": Decimal("1000")},
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000)],
            employee_inputs={"overtime_days": 2},
            client_meta={},
        )
        assert components["OVERTIME_PAY"] == Decimal("10000.00")

    def test_original_components_unchanged(self):
        """The rule adds a new key; existing salary components are unmodified."""
        original = {"BASIC": Decimal("300000")}
        components, _ = apply_payroll_rules(
            salary_components=original,
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000)],
            employee_inputs={"overtime_days": 1},
            client_meta={},
        )
        assert components["BASIC"] == Decimal("300000")


# ---------------------------------------------------------------------------
# daily_rate_deduction
# ---------------------------------------------------------------------------

class TestDailyRateDeduction:

    def test_work_days_strategy(self):
        """2 absent days, BASIC=300,000, 22 working days.

        daily_rate = round(300000/22, 2) = 13636.36
        deduction  = 13636.36 × 2       = 27272.72
        BASIC after = 300000 - 27272.72 = 272727.28
        """
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "work_days"}}
        }
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={"absent_days": 2},
            client_meta=client_meta,
            working_days=22,
        )
        assert components["BASIC"] == Decimal("272727.28")
        assert trace[0]["status"] == "applied"
        assert "BASIC(work_days)" in trace[0]["note"]

    def test_calendar_days_strategy(self):
        """2 absent days, BASIC=300,000, 30 calendar days.

        daily_rate = 300000/30 = 10000.00
        deduction  = 10000 × 2 = 20000.00
        BASIC after = 280000.00
        """
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "calendar_days"}}
        }
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={"absent_days": 2},
            client_meta=client_meta,
            calendar_days=30,
        )
        assert components["BASIC"] == Decimal("280000.00")

    def test_fixed_30_strategy(self):
        """2 absent days, BASIC=300,000, fixed divisor of 30 regardless of month.

        Identical result to calendar_days=30 but divisor is always 30.
        """
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "fixed_30"}}
        }
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={"absent_days": 2},
            client_meta=client_meta,
            working_days=22,
            calendar_days=31,   # real month is 31 days, but fixed_30 ignores this
        )
        assert components["BASIC"] == Decimal("280000.00")

    def test_non_proratable_component_skipped(self):
        """Component with no proration_strategy is skipped and noted in trace."""
        # TRANSPORT has no proration_strategy → skipped
        client_meta = {
            "BASIC":      {"calculations_behaviour": {"proration_strategy": "work_days"}},
            "TRANSPORT":  {},   # no calculations_behaviour → skipped
        }
        components, trace = apply_payroll_rules(
            salary_components={
                "BASIC":      Decimal("300000"),
                "TRANSPORT":  Decimal("50000"),
            },
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={"absent_days": 1},
            client_meta=client_meta,
            working_days=22,
        )
        # TRANSPORT unchanged
        assert components["TRANSPORT"] == Decimal("50000")
        # BASIC was deducted
        assert components["BASIC"] < Decimal("300000")
        # Trace note mentions the skip
        assert "TRANSPORT" in trace[0]["note"]
        assert "skipped" in trace[0]["note"]

    def test_not_applied_when_absent_days_zero(self):
        """No absent_days in inputs → rule skipped."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={},
            client_meta={"BASIC": {"calculations_behaviour": {"proration_strategy": "work_days"}}},
        )
        assert components["BASIC"] == Decimal("300000")
        assert trace[0]["status"] == "not_applied"

    def test_deduction_floored_at_zero(self):
        """More absent days than there are days → component floored at 0, not negative."""
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "work_days"}}
        }
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("10000")},
            payroll_rules=[_rule("Absence Deduction", "daily_rate_deduction",
                                 input_field="absent_days")],
            employee_inputs={"absent_days": 30},   # more than working days
            client_meta=client_meta,
            working_days=22,
        )
        assert components["BASIC"] == Decimal("0")


# ---------------------------------------------------------------------------
# fixed_amount
# ---------------------------------------------------------------------------

class TestFixedAmount:

    def test_applied_when_condition_met(self):
        """no_accident flag set → accident-free bonus applied."""
        components, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=[_rule("ACCIDENT_FREE_BONUS", "fixed_amount",
                                 amount=5000,
                                 condition={"no_accident": "True"})],
            employee_inputs={"no_accident": "True"},
            client_meta={},
        )
        assert components["ACCIDENT_FREE_BONUS"] == Decimal("5000")
        assert trace[0]["status"] == "applied"

    def test_not_applied_when_condition_not_met(self):
        """Condition key absent from inputs → not applied with reason in trace."""
        components, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=[_rule("ACCIDENT_FREE_BONUS", "fixed_amount",
                                 amount=5000,
                                 condition={"no_accident": "True"})],
            employee_inputs={},
            client_meta={},
        )
        assert "ACCIDENT_FREE_BONUS" not in components
        assert trace[0]["status"] == "not_applied"
        assert "no_accident" in trace[0]["note"]

    def test_no_condition_always_applied(self):
        """No condition dict → rule always fires."""
        components, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=[_rule("FLAT_BONUS", "fixed_amount", amount=10000)],
            employee_inputs={},
            client_meta={},
        )
        assert components["FLAT_BONUS"] == Decimal("10000")
        assert trace[0]["status"] == "applied"


# ---------------------------------------------------------------------------
# Inactive / unknown rules
# ---------------------------------------------------------------------------

class TestRuleGuards:

    def test_inactive_rule_skipped(self):
        """is_active=False → rule body never evaluated."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_inactive_rule("OVERTIME_PAY", "unit_multiplier")],
            employee_inputs={"overtime_days": 5},
            client_meta={},
        )
        assert "OVERTIME_PAY" not in components
        assert trace == []   # inactive rules produce no trace entry

    def test_unknown_method_recorded_as_not_applied(self):
        """Unrecognised calculation_method → trace entry with not_applied."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("MYSTERY", "percentage_of_gross")],
            employee_inputs={},
            client_meta={},
        )
        assert "MYSTERY" not in components
        assert trace[0]["status"] == "not_applied"
        assert "percentage_of_gross" in trace[0]["note"]

    def test_multiple_rules_all_traced(self):
        """Each active rule produces exactly one trace entry."""
        rules = [
            _rule("OVERTIME_PAY", "unit_multiplier",
                  input_field="overtime_days", rate=5000),
            _rule("FLAT_BONUS", "fixed_amount", amount=2000),
        ]
        _, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=rules,
            employee_inputs={"overtime_days": 2},
            client_meta={},
        )
        assert len(trace) == 2
        rule_names = {t["rule"] for t in trace}
        assert rule_names == {"OVERTIME_PAY", "FLAT_BONUS"}

    def test_rule_set_item_format_no_is_active_treated_as_active(self):
        """rule_set_item rows have no is_active key — treated as active."""
        rule_without_is_active = {
            "rule_name":            "OVERTIME_PAY",
            "rule_definition_json": {"calculation_method": "unit_multiplier",
                                     "input_field": "overtime_days", "rate": 5000},
            # is_active key intentionally absent
        }
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[rule_without_is_active],
            employee_inputs={"overtime_days": 2},
            client_meta={},
        )
        assert components["OVERTIME_PAY"] == Decimal("10000.00")
        assert len(trace) == 1


# ---------------------------------------------------------------------------
# Trace temporal fields
# ---------------------------------------------------------------------------

class TestTraceTemporalFields:

    def test_trace_entry_contains_temporal_fields(self):
        """Every trace entry now includes resolution metadata fields."""
        _, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=[_rule("OVERTIME_PAY", "unit_multiplier",
                                 input_field="overtime_days", rate=5000)],
            employee_inputs={"overtime_days": 2},
            client_meta={},
            current_rule_set_id="rs-123",
            current_rule_set_effective_from="2024-01-01",
        )
        entry = trace[0]
        assert "rule_set_id"         in entry
        assert "rule_effective_from" in entry
        assert "reference_date"      in entry
        assert "rate_used"           in entry
        assert "resolution_source"   in entry

    def test_current_resolution_source_when_no_reference_date(self):
        """No reference_date → resolution_source = 'current'."""
        _, trace = apply_payroll_rules(
            salary_components={},
            payroll_rules=[_rule("FLAT_BONUS", "fixed_amount", amount=1000)],
            employee_inputs={},
            client_meta={},
            current_rule_set_id="rs-1",
        )
        assert trace[0]["resolution_source"] == "current"
        assert trace[0]["rule_set_id"] == "rs-1"


# ---------------------------------------------------------------------------
# Temporal resolution — _resolve_rule
# ---------------------------------------------------------------------------

CURRENT_RS_ID  = "rs-current"
HIST_RS_ID     = "rs-hist"
PERIOD_START   = date(2024, 3, 1)
PERIOD_END     = date(2024, 3, 31)

CURRENT_RULES = {
    "OVERTIME_PAY": {
        "rule_definition_json": {
            "calculation_method": "unit_multiplier",
            "input_field": "overtime_days",
            "rate": 6000,
        }
    }
}

HISTORICAL_RULE_SETS = [
    {
        "id": HIST_RS_ID,
        "effective_from": "2024-01-01",
        "items": [
            {
                "rule_name": "OVERTIME_PAY",
                "rule_definition_json": {
                    "calculation_method": "unit_multiplier",
                    "input_field": "overtime_days",
                    "rate": 5000,    # January rate (lower)
                },
            }
        ],
    }
]


class TestResolveRule:

    def test_current_period_uses_current_rate(self):
        """Reference date within current period → current rule definition."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY",
            date(2024, 3, 15),   # within period
            CURRENT_RULES,
            HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert defn["rate"] == 6000
        assert meta["resolution_source"] == "current"

    def test_no_reference_date_uses_current(self):
        """None reference_date (period-agnostic) → current rule definition."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY", None,
            CURRENT_RULES, HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert defn["rate"] == 6000
        assert meta["resolution_source"] == "current"

    def test_historical_date_uses_historical_rate(self):
        """Reference date in January → historical rule set → rate 5000."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY",
            date(2024, 1, 15),   # before period_start
            CURRENT_RULES,
            HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert defn["rate"] == 5000
        assert meta["resolution_source"] == "historical"
        assert meta["rule_set_id"] == HIST_RS_ID

    def test_historical_date_no_matching_set_falls_back_to_current(self):
        """Historical date but no rule set covers it → current_fallback."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY",
            date(2020, 6, 1),    # before any historical rule set
            CURRENT_RULES,
            HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert meta["resolution_source"] == "current_fallback"
        assert defn["rate"] == 6000

    def test_unknown_rule_returns_empty_defn(self):
        """Rule not in any rule set → empty definition, resolution still works."""
        defn, meta = _resolve_rule(
            "UNKNOWN_RULE", None,
            CURRENT_RULES, HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert defn == {}
        assert meta["resolution_source"] == "current"

    # -- rule_floor_dates (strict mode) --------------------------------------

    def test_no_matching_set_with_floor_date_backfill_gap_falls_back(self):
        """rule_floor_dates says the rule existed as far back as 2023-06-01, but
        the earliest historical rule_set snapshot only covers 2024-01-01 onward
        (a backfill gap) — falls back to current, does not raise."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY",
            date(2023, 8, 1),    # after the rule's floor, before any covering rule_set
            CURRENT_RULES,
            HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
            {"OVERTIME_PAY": "2023-06-01"},
        )
        assert meta["resolution_source"] == "current_fallback"
        assert defn["rate"] == 6000

    def test_no_matching_set_before_floor_date_raises(self):
        """rule_floor_dates supplied and reference_date predates the rule's known
        floor — genuinely no history exists this far back — must raise."""
        with pytest.raises(NoHistoricalRuleVersionError):
            _resolve_rule(
                "OVERTIME_PAY",
                date(2020, 6, 1),    # before the rule's floor (2024-01-01)
                CURRENT_RULES,
                HISTORICAL_RULE_SETS,
                PERIOD_START, PERIOD_END,
                CURRENT_RS_ID, "2024-03-01",
                {"OVERTIME_PAY": "2024-01-01"},
            )

    def test_no_floor_date_entry_raises(self):
        """rule_floor_dates supplied but has no entry for this rule at all
        (workspace has zero payroll_rule rows for this rule_name) — must raise."""
        with pytest.raises(NoHistoricalRuleVersionError):
            _resolve_rule(
                "OVERTIME_PAY",
                date(2020, 6, 1),
                CURRENT_RULES,
                HISTORICAL_RULE_SETS,
                PERIOD_START, PERIOD_END,
                CURRENT_RS_ID, "2024-03-01",
                {},
            )

    def test_none_rule_floor_dates_preserves_legacy_fallback(self):
        """rule_floor_dates=None (the default, all legacy/test callers) preserves
        the original current_fallback behaviour — no raise, ever."""
        defn, meta = _resolve_rule(
            "OVERTIME_PAY",
            date(2020, 6, 1),
            CURRENT_RULES,
            HISTORICAL_RULE_SETS,
            PERIOD_START, PERIOD_END,
            CURRENT_RS_ID, "2024-03-01",
        )
        assert meta["resolution_source"] == "current_fallback"


# ---------------------------------------------------------------------------
# Temporal resolution — _resolve_period_ctx
# ---------------------------------------------------------------------------

class TestResolvePeriodCtx:

    def test_current_period_returns_current_stats(self):
        wd, cd = _resolve_period_ctx(
            date(2024, 3, 15), 23, 31, {},
            PERIOD_START, PERIOD_END,
        )
        assert wd == 23
        assert cd == 31

    def test_none_date_returns_current(self):
        wd, cd = _resolve_period_ctx(None, 22, 30, {}, PERIOD_START, PERIOD_END)
        assert wd == 22
        assert cd == 30

    def test_historical_date_returns_historical_stats(self):
        hist_ctx = {(2024, 1): {"working_days": 23, "calendar_days": 31}}
        wd, cd = _resolve_period_ctx(
            date(2024, 1, 15), 22, 28, hist_ctx,
            PERIOD_START, PERIOD_END,
        )
        assert wd == 23
        assert cd == 31

    def test_historical_date_no_context_falls_back_to_current(self):
        wd, cd = _resolve_period_ctx(
            date(2024, 1, 15), 22, 28, {},
            PERIOD_START, PERIOD_END,
        )
        assert wd == 22
        assert cd == 28


# ---------------------------------------------------------------------------
# end-to-end: historical rate applied via apply_payroll_rules
# ---------------------------------------------------------------------------

class TestTemporalRateResolution:

    def test_cross_period_input_uses_historical_rate(self):
        """January overtime input should use January rule set (rate=5000)
        not March's (rate=6000)."""
        rules = [
            {
                "rule_name":            "OVERTIME_PAY",
                "rule_definition_json": {
                    "calculation_method": "unit_multiplier",
                    "input_field":        "overtime_days",
                    "rate":               6000,   # March rate
                },
            }
        ]
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=rules,
            employee_inputs={"overtime_days": [{"quantity": 2, "reference_date": date(2024, 1, 15)}]},
            client_meta={},
            historical_rule_sets=HISTORICAL_RULE_SETS,
            period_start=PERIOD_START,
            period_end=PERIOD_END,
            current_rule_set_id=CURRENT_RS_ID,
            current_rule_set_effective_from="2024-03-01",
        )
        # 2 days × 5000 (January rate) = 10000
        assert components["OVERTIME_PAY"] == Decimal("10000.00")
        assert trace[0]["resolution_source"] == "historical"

    def test_current_period_input_uses_current_rate(self):
        """March input uses current rule set (rate=6000)."""
        rules = [
            {
                "rule_name":            "OVERTIME_PAY",
                "rule_definition_json": {
                    "calculation_method": "unit_multiplier",
                    "input_field":        "overtime_days",
                    "rate":               6000,
                },
            }
        ]
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("300000")},
            payroll_rules=rules,
            employee_inputs={"overtime_days": [{"quantity": 2, "reference_date": date(2024, 3, 15)}]},
            client_meta={},
            historical_rule_sets=HISTORICAL_RULE_SETS,
            period_start=PERIOD_START,
            period_end=PERIOD_END,
            current_rule_set_id=CURRENT_RS_ID,
            current_rule_set_effective_from="2024-03-01",
        )
        # 2 days × 6000 (March rate) = 12000
        assert components["OVERTIME_PAY"] == Decimal("12000.00")
        assert trace[0]["resolution_source"] == "current"

    def test_cross_period_deduction_uses_historical_working_days(self):
        """January absence input uses January working_days (23) not March's (21)."""
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "work_days"}}
        }
        rules = [_rule("Absence Deduction", "daily_rate_deduction", input_field="absent_days")]
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("230000")},
            payroll_rules=rules,
            employee_inputs={"absent_days": [{"quantity": 1, "reference_date": date(2024, 1, 15)}]},
            client_meta=client_meta,
            working_days=21,   # March
            calendar_days=31,
            historical_period_contexts={(2024, 1): {"working_days": 23, "calendar_days": 31}},
            period_start=PERIOD_START,
            period_end=PERIOD_END,
        )
        # daily rate for January = 230000 / 23 = 10000.00
        # deduction = 10000.00 × 1 = 10000.00
        # BASIC after = 230000 - 10000 = 220000
        assert components["BASIC"] == Decimal("220000.00")

    def test_deduction_spanning_two_periods_uses_each_periods_own_divisor(self):
        """3 absence days in January (working_days=23) + 2 in March (working_days=21)
        must each be deducted at their OWN period's daily divisor — not resolved
        once from the first event's date for the whole 5-day total (the bug this
        test guards against: pre-fix, only the first event's period applied to the
        entire summed quantity)."""
        client_meta = {
            "BASIC": {"calculations_behaviour": {"proration_strategy": "work_days"}}
        }
        rules = [_rule("Absence Deduction", "daily_rate_deduction", input_field="absent_days")]
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("230000")},
            payroll_rules=rules,
            employee_inputs={"absent_days": [
                {"quantity": 3, "reference_date": date(2024, 1, 15)},
                {"quantity": 2, "reference_date": date(2024, 3, 15)},
            ]},
            client_meta=client_meta,
            working_days=21,   # March (current period)
            calendar_days=31,
            historical_period_contexts={(2024, 1): {"working_days": 23, "calendar_days": 31}},
            period_start=PERIOD_START,
            period_end=PERIOD_END,
        )
        # January: 230000/23 = 10000.00/day × 3 = 30000.00
        # March:   230000/21 = 10952.38/day × 2 = 21904.76
        # total deducted = 51904.76
        assert components["BASIC"] == Decimal("178095.24")
        assert trace[0]["status"] == "applied"
        assert "spans 2 periods" in trace[0]["note"]


