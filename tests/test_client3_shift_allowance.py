"""
PH-12 — Client 3 Shift Allowance Verification (E1 — Track E).

Verifies that the ot_multiplier calculation method handles basic_daily base
correctly for Client 3's SHIFT2, SHIFT3, and SHIFT4 rate codes.

Client 3 configuration:
  - SHIFT2: multiplier=0.10, unit=day, base=basic_daily, is_pensionable=TRUE
  - SHIFT3: multiplier=0.15, unit=day, base=basic_daily, is_pensionable=TRUE
  - SHIFT4: multiplier=0.25, unit=day, base=basic_daily, is_pensionable=TRUE

Payroll rules (one per shift tier):
  { "calculation_method": "ot_multiplier", "rate_code": "SHIFT2", "unit": "day", "input_field": "shift2_days" }
  { "calculation_method": "ot_multiplier", "rate_code": "SHIFT3", "unit": "day", "input_field": "shift3_days" }
  { "calculation_method": "ot_multiplier", "rate_code": "SHIFT4", "unit": "day", "input_field": "shift4_days" }

Formula: shift_allowance = (BASIC / expected_days) × multiplier × shift_days_worked

ph_mode = AUTOMATIC — expected_days comes from the PH calendar, NOT working_days.

All tests are pure function tests — no database access.
"""
from decimal import Decimal

import pytest

from backend.domain.payroll.rule_evaluator import apply_payroll_rules
from backend.domain.payroll.sequential_executor import (
    build_runtime_component_registry,
    run_sequential_payroll,
    RULE_COMPONENT_PRIORITY,
)
from backend.domain.payroll.period_context import build_period_context

# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------

def _shift_rule(name: str, rate_code: str, input_field: str) -> dict:
    """Build an ot_multiplier payroll rule dict for a Client 3 shift tier."""
    return {
        "rule_name":            name,
        "rule_type":            "earning",
        "is_active":            True,
        "rule_definition_json": {
            "calculation_method": "ot_multiplier",
            "rate_code":          rate_code,
            "unit":               "day",
            "input_field":        input_field,
        },
    }


RATE_CODE_MAP = {
    "SHIFT2": {"code": "SHIFT2", "multiplier": 0.10, "unit": "day", "base": "basic_daily"},
    "SHIFT3": {"code": "SHIFT3", "multiplier": 0.15, "unit": "day", "base": "basic_daily"},
    "SHIFT4": {"code": "SHIFT4", "multiplier": 0.25, "unit": "day", "base": "basic_daily"},
}

SHIFT2_RULE = _shift_rule("SHIFT2", "SHIFT2", "shift2_days")
SHIFT3_RULE = _shift_rule("SHIFT3", "SHIFT3", "shift3_days")
SHIFT4_RULE = _shift_rule("SHIFT4", "SHIFT4", "shift4_days")

ALL_SHIFT_RULES = [SHIFT2_RULE, SHIFT3_RULE, SHIFT4_RULE]


# ---------------------------------------------------------------------------
# Rule-evaluator unit tests
# ---------------------------------------------------------------------------

class TestShift2RuleEvaluator:
    """SHIFT2 at 10% of basic_daily."""

    def test_full_month_acceptance_criteria(self):
        """Story AC: BASIC=200,000, expected_days=20, shift2_days=20 → ₦20,000."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={"shift2_days": [{"quantity": 20, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert components["SHIFT2"] == Decimal("20000.00")

    def test_partial_attendance(self):
        """Story AC: BASIC=200,000, expected_days=20, shift2_days=15 → ₦15,000."""
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={"shift2_days": [{"quantity": 15, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert components["SHIFT2"] == Decimal("15000.00")

    def test_zero_shift_days_not_applied(self):
        """shift2_days = 0 → rule not applied, SHIFT2 absent from components."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={"shift2_days": [{"quantity": 0, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert "SHIFT2" not in components
        assert trace[0]["status"] == "not_applied"

    def test_no_shift_days_input_not_applied(self):
        """shift2_days absent from inputs → rule not applied."""
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert "SHIFT2" not in components

    def test_missing_rate_code_raises(self):
        """rate_code_map missing SHIFT2 → ValueError with clear message."""
        with pytest.raises(ValueError, match="SHIFT2"):
            apply_payroll_rules(
                salary_components={"BASIC": Decimal("200000")},
                payroll_rules=[SHIFT2_RULE],
                employee_inputs={"shift2_days": [{"quantity": 5, "reference_date": None}]},
                client_meta={},
                expected_days=20,
                rate_code_map={},  # empty — SHIFT2 missing
            )

    def test_missing_expected_days_raises(self):
        """expected_days=0 with basic_daily base → ValueError."""
        with pytest.raises(ValueError, match="expected_days"):
            apply_payroll_rules(
                salary_components={"BASIC": Decimal("200000")},
                payroll_rules=[SHIFT2_RULE],
                employee_inputs={"shift2_days": [{"quantity": 5, "reference_date": None}]},
                client_meta={},
                expected_days=0,
                rate_code_map=RATE_CODE_MAP,
            )

    def test_trace_contains_rate_code_and_multiplier(self):
        """Trace entry includes rate_code, multiplier, base_rate, quantity, amount."""
        _, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={"shift2_days": [{"quantity": 10, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        entry = trace[0]
        assert entry["rate_code"]  == "SHIFT2"
        assert Decimal(entry["multiplier"]) == Decimal("0.10")
        assert entry["base_rate"]  == "10000.00"   # 200,000 / 20
        assert entry["quantity"]   == "10"
        assert entry["amount"]     == "10000.00"   # 10 × 10,000 × 0.10


class TestShift3RuleEvaluator:
    """SHIFT3 at 15% of basic_daily."""

    def test_full_month(self):
        """BASIC=200,000, expected_days=20, shift3_days=20 → ₦30,000."""
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT3_RULE],
            employee_inputs={"shift3_days": [{"quantity": 20, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert components["SHIFT3"] == Decimal("30000.00")


class TestShift4RuleEvaluator:
    """SHIFT4 at 25% of basic_daily."""

    def test_full_month(self):
        """BASIC=200,000, expected_days=20, shift4_days=20 → ₦50,000."""
        components, _ = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=[SHIFT4_RULE],
            employee_inputs={"shift4_days": [{"quantity": 20, "reference_date": None}]},
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        assert components["SHIFT4"] == Decimal("50000.00")


class TestAllShiftTiers:
    """Verify all three shift tiers can coexist in the same payroll run."""

    def test_all_three_tiers_applied(self):
        """Employee works all three shift types — each allowance computed independently."""
        components, trace = apply_payroll_rules(
            salary_components={"BASIC": Decimal("200000")},
            payroll_rules=ALL_SHIFT_RULES,
            employee_inputs={
                "shift2_days": [{"quantity": 10, "reference_date": None}],
                "shift3_days": [{"quantity": 5,  "reference_date": None}],
                "shift4_days": [{"quantity": 3,  "reference_date": None}],
            },
            client_meta={},
            expected_days=20,
            rate_code_map=RATE_CODE_MAP,
        )
        # SHIFT2: (200,000/20) × 0.10 × 10 = 10,000 × 0.10 × 10 = 10,000
        assert components["SHIFT2"] == Decimal("10000.00")
        # SHIFT3: (200,000/20) × 0.15 × 5  = 10,000 × 0.15 × 5  = 7,500
        assert components["SHIFT3"] == Decimal("7500.00")
        # SHIFT4: (200,000/20) × 0.25 × 3  = 10,000 × 0.25 × 3  = 7,500
        assert components["SHIFT4"] == Decimal("7500.00")


# ---------------------------------------------------------------------------
# Sequential executor pipeline tests
# ---------------------------------------------------------------------------

# Minimal platform metadata for the sequential executor (no PAYE/pension needed
# to verify the shift component mechanics).
PLATFORM_METADATA = [
    {"component_code": "BASIC",     "component_class": "earning",  "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
    {"component_code": "GROSS_PAY", "component_class": "derived",  "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
    {"component_code": "NET_PAY",   "component_class": "derived",  "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
]

BASE_PERIOD = build_period_context("2026-03-01", "2026-03-31")

BASE_CONTEXT = {
    "tax_bands":             [],
    "pension_employee_rate": Decimal("0.08"),
    "pension_employer_rate": Decimal("0.10"),
    "nhf_rate":              Decimal("0.025"),
    "client_meta":           {},
    "period":                BASE_PERIOD,
    "expected_days":         20,
    "rate_code_map":         RATE_CODE_MAP,
}


class TestShiftAllowanceInSequentialExecutor:
    """Verify shift allowances enter GROSS_PAY via the sequential executor."""

    def _run(self, salary, inputs, rules):
        """Run the full executor pipeline for Client 3 configuration."""
        # Rule evaluator pre-computes ot_multiplier → injects into salary_components
        modified_salary, _ = apply_payroll_rules(
            salary_components=salary,
            payroll_rules=rules,
            employee_inputs=inputs,
            client_meta={},
            expected_days=BASE_CONTEXT["expected_days"],
            rate_code_map=BASE_CONTEXT["rate_code_map"],
        )
        # Build unified component registry (SHIFT2/3/4 added as salary_component at priority 50)
        unified_meta = build_runtime_component_registry(
            platform_metadata=PLATFORM_METADATA,
            payroll_rules=rules,
            employee_inputs=inputs,
        )
        ctx = {**BASE_CONTEXT, "employee_inputs": inputs}
        return run_sequential_payroll(modified_salary, unified_meta, ctx)

    def test_shift2_enters_gross_pay(self):
        """SHIFT2 allowance is included in GROSS_PAY."""
        salary = {"BASIC": Decimal("200000")}
        inputs = {"shift2_days": [{"quantity": 20, "reference_date": None}]}
        out = self._run(salary, inputs, [SHIFT2_RULE])

        assert out["results"]["SHIFT2"]    == Decimal("20000.00")
        assert out["results"]["GROSS_PAY"] == Decimal("220000.00")   # 200,000 + 20,000

    def test_all_shift_tiers_enter_gross_pay(self):
        """All three shift allowances are summed into GROSS_PAY."""
        salary = {"BASIC": Decimal("200000")}
        inputs = {
            "shift2_days": [{"quantity": 10, "reference_date": None}],
            "shift3_days": [{"quantity": 5,  "reference_date": None}],
            "shift4_days": [{"quantity": 3,  "reference_date": None}],
        }
        out = self._run(salary, inputs, ALL_SHIFT_RULES)

        assert out["results"]["SHIFT2"]    == Decimal("10000.00")
        assert out["results"]["SHIFT3"]    == Decimal("7500.00")
        assert out["results"]["SHIFT4"]    == Decimal("7500.00")
        # GROSS_PAY = 200,000 + 10,000 + 7,500 + 7,500
        assert out["results"]["GROSS_PAY"] == Decimal("225000.00")

    def test_shift_component_in_trace(self):
        """Shift allowance component appears in execution trace."""
        salary = {"BASIC": Decimal("200000")}
        inputs = {"shift2_days": [{"quantity": 20, "reference_date": None}]}
        out = self._run(salary, inputs, [SHIFT2_RULE])

        component_codes = [t["component"] for t in out["trace"]]
        assert "SHIFT2" in component_codes

    def test_shift_component_priority(self):
        """SHIFT2 runs at RULE_COMPONENT_PRIORITY (50) — before GROSS_PAY at 100."""
        unified_meta = build_runtime_component_registry(
            platform_metadata=PLATFORM_METADATA,
            payroll_rules=[SHIFT2_RULE],
            employee_inputs={},
        )
        shift_entry = next(m for m in unified_meta if m["component_code"] == "SHIFT2")
        assert shift_entry["execution_priority"] == RULE_COMPONENT_PRIORITY

    def test_no_shift_days_gross_pay_unchanged(self):
        """Employee with no shift inputs → GROSS_PAY = BASIC only."""
        salary = {"BASIC": Decimal("200000")}
        out = self._run(salary, {}, [SHIFT2_RULE])

        assert "SHIFT2" not in out["results"] or out["results"].get("SHIFT2") == Decimal("0")
        assert out["results"]["GROSS_PAY"] == Decimal("200000")
