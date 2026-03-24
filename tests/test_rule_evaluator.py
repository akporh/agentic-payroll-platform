"""
Unit tests for apply_payroll_rules() in backend/domain/payroll/rule_evaluator.py.

Pure function tests — no database access required.

All monetary values use Decimal. The rule evaluator is called by the payroll
service BEFORE the sequential executor — it modifies salary_components by
adding earnings (unit_multiplier) or reducing proratable components
(daily_rate_deduction).
"""
from decimal import Decimal

import pytest

from backend.domain.payroll.rule_evaluator import apply_payroll_rules


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
