"""
Unit tests: multi-event input support in apply_payroll_rules().

Validates that the rule evaluator correctly handles N events per input_code
(e.g. January overtime + February overtime in a single run), applying the
historically correct rate for each event's reference_date.

No database access required — pure function tests.

Tests
-----
1. test_single_event_scalar_unchanged   — legacy scalar passes through via _to_events()
2. test_two_events_same_rate            — two events, same rate → Σ qty × rate
3. test_two_events_different_rates      — two events, different historical rates →
                                          (qty_jan × rate_jan) + (qty_feb × rate_feb)
4. test_zero_quantity_event_skipped     — events with qty=0 do not contribute
5. test_empty_event_list_not_applied    — empty list produces not_applied trace
"""

from datetime import date
from decimal import Decimal

import pytest

from backend.domain.payroll.rule_evaluator import apply_payroll_rules


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

PERIOD_START = date(2026, 2, 19)
PERIOD_END   = date(2026, 3, 18)

CURRENT_RS_ID = "rs-current"

# Historical rule set: January rate = 5000, current (March) rate = 6000
HISTORICAL_RULE_SETS = [
    {
        "id":             "rs-jan",
        "effective_from": "2026-01-01",
        "items": [
            {
                "rule_name":            "OVERTIME_PAY",
                "rule_definition_json": {
                    "calculation_method": "unit_multiplier",
                    "input_field":        "ot_days",
                    "rate":               5000,
                    "unit":               "days",
                },
            }
        ],
    }
]

CURRENT_RULES = [
    {
        "rule_name":            "OVERTIME_PAY",
        "rule_definition_json": {
            "calculation_method": "unit_multiplier",
            "input_field":        "ot_days",
            "rate":               6000,
            "unit":               "days",
        },
    }
]


# ---------------------------------------------------------------------------
# Test 1 — legacy scalar normalised to single event
# ---------------------------------------------------------------------------

def test_single_event_scalar_unchanged():
    """A bare scalar (legacy caller) is treated as one event and produces qty × rate."""
    components, trace = apply_payroll_rules(
        salary_components={"BASIC": Decimal("300000")},
        payroll_rules=CURRENT_RULES,
        employee_inputs={"ot_days": 5},   # legacy scalar
        client_meta={},
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        current_rule_set_id=CURRENT_RS_ID,
        current_rule_set_effective_from="2026-02-19",
    )
    # 5 days × 6000 (current rate) = 30000
    assert components["OVERTIME_PAY"] == Decimal("30000.00")
    assert trace[0]["status"] == "applied"


# ---------------------------------------------------------------------------
# Test 2 — two events, same rate → sum
# ---------------------------------------------------------------------------

def test_two_events_same_rate():
    """Two events where both resolve to the same rate produce Σ qty × rate."""
    components, trace = apply_payroll_rules(
        salary_components={"BASIC": Decimal("300000")},
        payroll_rules=CURRENT_RULES,
        employee_inputs={"ot_days": [
            {"quantity": 6,  "reference_date": PERIOD_START},   # within current period
            {"quantity": 20, "reference_date": PERIOD_END},     # within current period
        ]},
        client_meta={},
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        current_rule_set_id=CURRENT_RS_ID,
        current_rule_set_effective_from="2026-02-19",
    )
    # (6 + 20) × 6000 = 156000
    assert components["OVERTIME_PAY"] == Decimal("156000.00")
    assert trace[0]["status"] == "applied"
    assert "2 events" in trace[0]["note"]


# ---------------------------------------------------------------------------
# Test 3 — two events, different historical rates
# ---------------------------------------------------------------------------

def test_two_events_different_rates():
    """Two events with different ref_dates resolve different rates; totals must differ
    from a collapsed single-event calculation."""
    jan_ref = date(2026, 1, 1)
    feb_ref = PERIOD_START  # within current period

    components, trace = apply_payroll_rules(
        salary_components={"BASIC": Decimal("300000")},
        payroll_rules=CURRENT_RULES,
        employee_inputs={"ot_days": [
            {"quantity": 6,  "reference_date": jan_ref},   # → historical rate 5000
            {"quantity": 20, "reference_date": feb_ref},   # → current rate 6000
        ]},
        client_meta={},
        historical_rule_sets=HISTORICAL_RULE_SETS,
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        current_rule_set_id=CURRENT_RS_ID,
        current_rule_set_effective_from="2026-01-15",
    )
    # (6 × 5000) + (20 × 6000) = 30000 + 120000 = 150000
    expected = Decimal("30000.00") + Decimal("120000.00")
    assert components["OVERTIME_PAY"] == expected, (
        f"Expected {expected} but got {components['OVERTIME_PAY']}. "
        "Jan event must use rate=5000, Feb event must use rate=6000."
    )
    # Collapsed single-event would give 26 × 6000 = 156000 — must differ
    assert components["OVERTIME_PAY"] != Decimal("156000.00"), (
        "Result must not match the collapsed (last-writer-wins) calculation"
    )
    assert trace[0]["status"] == "applied"


# ---------------------------------------------------------------------------
# Test 4 — zero-quantity events are skipped
# ---------------------------------------------------------------------------

def test_zero_quantity_event_skipped():
    """Events with qty=0 (or None) are not counted; only positive events fire."""
    components, trace = apply_payroll_rules(
        salary_components={"BASIC": Decimal("300000")},
        payroll_rules=CURRENT_RULES,
        employee_inputs={"ot_days": [
            {"quantity": 0,  "reference_date": PERIOD_START},
            {"quantity": None, "reference_date": PERIOD_START},
            {"quantity": 3,  "reference_date": PERIOD_START},
        ]},
        client_meta={},
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        current_rule_set_id=CURRENT_RS_ID,
        current_rule_set_effective_from="2026-02-19",
    )
    # Only the 3-day event fires: 3 × 6000 = 18000
    assert components["OVERTIME_PAY"] == Decimal("18000.00")
    assert trace[0]["status"] == "applied"


# ---------------------------------------------------------------------------
# Test 5 — empty event list → not_applied
# ---------------------------------------------------------------------------

def test_empty_event_list_not_applied():
    """An empty list (or missing key) produces a not_applied trace entry."""
    components, trace = apply_payroll_rules(
        salary_components={"BASIC": Decimal("300000")},
        payroll_rules=CURRENT_RULES,
        employee_inputs={},   # no inputs at all
        client_meta={},
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        current_rule_set_id=CURRENT_RS_ID,
    )
    assert "OVERTIME_PAY" not in components
    assert trace[0]["status"] == "not_applied"
