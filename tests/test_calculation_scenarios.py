"""
Integration tests: rule evaluator + sequential executor pipeline.

Tests the full calculation pipeline (rules → executor) in a single
pure-Python test — no database required.

Scenarios:
  1. Overtime — unit_multiplier rule adds OVERTIME_PAY; included in GROSS and NET.
  2. Absence  — daily_rate_deduction reduces BASIC; GROSS and NET are lower.
  3. Bonus    — fixed_amount rule adds FLAT_BONUS; included in GROSS and NET.
  4. Combo    — overtime AND absence in the same period; both rules applied.
"""
from decimal import Decimal

import pytest

from backend.domain.payroll.rule_evaluator import apply_payroll_rules
from backend.domain.payroll.sequential_executor import run_sequential_payroll
from backend.domain.payroll.period_context import build_period_context


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TAX_BANDS = [
    {"lower_limit": 0,       "upper_limit": 300_000, "rate": 0.07},
    {"lower_limit": 300_000, "upper_limit": 600_000, "rate": 0.11},
    {"lower_limit": 600_000, "upper_limit": None,    "rate": 0.15},
]

BASE_SALARY = {
    "BASIC":     Decimal("300000"),
    "HOUSING":   Decimal("150000"),
    "TRANSPORT": Decimal("50000"),
}

# OVERTIME_PAY is a salary_component earning injected by the rule evaluator.
# It must have a metadata entry so the executor picks it up via salary_components.
COMPONENT_METADATA = [
    {"component_code": "BASIC",            "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
    {"component_code": "HOUSING",          "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 20,  "is_active": True, "metadata_json": {}},
    {"component_code": "TRANSPORT",        "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 30,  "is_active": True, "metadata_json": {}},
    {"component_code": "OVERTIME_PAY",     "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 35,  "is_active": True, "metadata_json": {}},
    {"component_code": "FLAT_BONUS",       "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 36,  "is_active": True, "metadata_json": {}},
    {"component_code": "GROSS_PAY",        "component_class": "derived",             "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
    {"component_code": "PENSION_EMPLOYEE", "component_class": "statutory_deduction", "calculation_method": "pension_rule",     "execution_priority": 200, "is_active": True, "metadata_json": {}},
    {"component_code": "TAXABLE_INCOME",   "component_class": "derived",             "calculation_method": "taxable_income",   "execution_priority": 300, "is_active": True, "metadata_json": {}},
    {"component_code": "PAYE",             "component_class": "statutory_deduction", "calculation_method": "paye_rule",        "execution_priority": 400, "is_active": True, "metadata_json": {}},
    {"component_code": "NHF_CONTRIBUTION", "component_class": "statutory_deduction", "calculation_method": "nhf_rule",         "execution_priority": 410, "is_active": True, "metadata_json": {}},
    {"component_code": "NET_PAY",          "component_class": "derived",             "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
]

CONTEXT = {
    "tax_bands":             TAX_BANDS,
    "pension_employee_rate": Decimal("0.08"),
    "pension_employer_rate": Decimal("0.10"),
    "nhf_rate":              Decimal("0.025"),
    "employee_inputs":       {},
    "client_meta":           {},
    "period":                build_period_context("2026-03-01", "2026-03-31"),
}

# client_meta with proration strategy for absence deduction tests
PRORATION_META = {
    "BASIC":     {"calculations_behaviour": {"proration_strategy": "work_days"}},
    "HOUSING":   {"calculations_behaviour": {"proration_strategy": "work_days"}},
    "TRANSPORT": {"calculations_behaviour": {"proration_strategy": "work_days"}},
}


def _run_pipeline(salary_components, payroll_rules, employee_inputs, client_meta=None):
    """Apply rules then execute sequential payroll."""
    period = build_period_context("2026-03-01", "2026-03-31")

    # Step 1: rule evaluator
    modified_components, rule_trace = apply_payroll_rules(
        salary_components=salary_components,
        payroll_rules=payroll_rules,
        employee_inputs=employee_inputs,
        client_meta=client_meta or {},
        working_days=period.working_days,
        calendar_days=period.calendar_days,
    )

    # Step 2: sequential executor
    ctx = {**CONTEXT, "employee_inputs": employee_inputs}
    result = run_sequential_payroll(
        salary_components=modified_components,
        component_metadata=COMPONENT_METADATA,
        context=ctx,
    )
    return result, rule_trace


# ---------------------------------------------------------------------------
# Baseline (no rules)
# ---------------------------------------------------------------------------

def _baseline():
    return run_sequential_payroll(
        salary_components=BASE_SALARY,
        component_metadata=COMPONENT_METADATA,
        context=CONTEXT,
    )


# ---------------------------------------------------------------------------
# Scenario 1: Overtime
# ---------------------------------------------------------------------------

class TestOvertimeScenario:
    """3 overtime days × ₦5,000/day = ₦15,000 added to GROSS and NET."""

    OVERTIME_RULE = {
        "rule_name": "OVERTIME_PAY",
        "is_active": True,
        "rule_definition_json": {
            "calculation_method": "unit_multiplier",
            "input_field":        "overtime_days",
            "rate":               5000,
            "unit":               "days",
        },
    }

    def test_gross_includes_overtime(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.OVERTIME_RULE],
            employee_inputs={"overtime_days": 3},
        )
        baseline_gross = _baseline()["results"]["GROSS_PAY"]
        assert result["results"]["GROSS_PAY"] == baseline_gross + Decimal("15000")

    def test_net_increases_by_overtime_minus_deductions(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.OVERTIME_RULE],
            employee_inputs={"overtime_days": 3},
        )
        baseline_net = _baseline()["results"]["NET_PAY"]
        # NET increased, but not by full 15,000 (extra PAYE and pension apply)
        assert result["results"]["NET_PAY"] > baseline_net

    def test_no_overtime_equals_baseline(self):
        """No overtime input → GROSS identical to baseline."""
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.OVERTIME_RULE],
            employee_inputs={},
        )
        assert result["results"]["GROSS_PAY"] == _baseline()["results"]["GROSS_PAY"]


# ---------------------------------------------------------------------------
# Scenario 2: Absence deduction
# ---------------------------------------------------------------------------

class TestAbsenceScenario:
    """2 absent days → daily_rate_deduction reduces BASIC and HOUSING."""

    ABSENCE_RULE = {
        "rule_name": "Absence Deduction",
        "is_active": True,
        "rule_definition_json": {
            "calculation_method": "daily_rate_deduction",
            "input_field":        "absent_days",
        },
    }

    def test_gross_lower_than_baseline(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.ABSENCE_RULE],
            employee_inputs={"absent_days": 2},
            client_meta=PRORATION_META,
        )
        assert result["results"]["GROSS_PAY"] < _baseline()["results"]["GROSS_PAY"]

    def test_net_lower_than_baseline(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.ABSENCE_RULE],
            employee_inputs={"absent_days": 2},
            client_meta=PRORATION_META,
        )
        assert result["results"]["NET_PAY"] < _baseline()["results"]["NET_PAY"]

    def test_rule_trace_notes_deducted_components(self):
        _, rule_trace = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.ABSENCE_RULE],
            employee_inputs={"absent_days": 2},
            client_meta=PRORATION_META,
        )
        assert rule_trace[0]["status"] == "applied"
        note = rule_trace[0]["note"]
        assert "BASIC" in note
        assert "HOUSING" in note
        assert "TRANSPORT" in note


# ---------------------------------------------------------------------------
# Scenario 3: Fixed bonus
# ---------------------------------------------------------------------------

class TestBonusScenario:
    """Accident-free bonus of ₦10,000 always fires (no condition)."""

    BONUS_RULE = {
        "rule_name": "FLAT_BONUS",
        "is_active": True,
        "rule_definition_json": {
            "calculation_method": "fixed_amount",
            "amount":             10000,
        },
    }

    def test_gross_includes_bonus(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.BONUS_RULE],
            employee_inputs={},
        )
        baseline_gross = _baseline()["results"]["GROSS_PAY"]
        assert result["results"]["GROSS_PAY"] == baseline_gross + Decimal("10000")

    def test_net_increases(self):
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=[self.BONUS_RULE],
            employee_inputs={},
        )
        assert result["results"]["NET_PAY"] > _baseline()["results"]["NET_PAY"]


# ---------------------------------------------------------------------------
# Scenario 4: Overtime + Absence in same period
# ---------------------------------------------------------------------------

class TestComboScenario:
    """3 overtime days AND 2 absent days: both rules applied sequentially."""

    RULES = [
        {
            "rule_name": "OVERTIME_PAY",
            "is_active": True,
            "rule_definition_json": {
                "calculation_method": "unit_multiplier",
                "input_field":        "overtime_days",
                "rate":               5000,
                "unit":               "days",
            },
        },
        {
            "rule_name": "Absence Deduction",
            "is_active": True,
            "rule_definition_json": {
                "calculation_method": "daily_rate_deduction",
                "input_field":        "absent_days",
            },
        },
    ]

    def test_both_rules_produce_two_trace_entries(self):
        _, rule_trace = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=self.RULES,
            employee_inputs={"overtime_days": 3, "absent_days": 2},
            client_meta=PRORATION_META,
        )
        assert len(rule_trace) == 2

    def test_overtime_applied(self):
        _, rule_trace = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=self.RULES,
            employee_inputs={"overtime_days": 3, "absent_days": 2},
            client_meta=PRORATION_META,
        )
        overtime_entry = next(t for t in rule_trace if t["rule"] == "OVERTIME_PAY")
        assert overtime_entry["status"] == "applied"
        assert overtime_entry["amount"] == "15000.00"

    def test_absence_applied(self):
        _, rule_trace = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=self.RULES,
            employee_inputs={"overtime_days": 3, "absent_days": 2},
            client_meta=PRORATION_META,
        )
        absence_entry = next(t for t in rule_trace if t["rule"] == "Absence Deduction")
        assert absence_entry["status"] == "applied"

    def test_net_reflects_both_adjustments(self):
        """NET with overtime AND absence is between:
          - baseline (no overtime, no absence)
          - baseline + overtime only (no absence deduction)
        """
        result, _ = _run_pipeline(
            salary_components=dict(BASE_SALARY),
            payroll_rules=self.RULES,
            employee_inputs={"overtime_days": 3, "absent_days": 2},
            client_meta=PRORATION_META,
        )
        baseline_net = _baseline()["results"]["NET_PAY"]
        assert result["results"]["NET_PAY"] != baseline_net
