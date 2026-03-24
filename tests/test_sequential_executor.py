"""
Unit tests for run_sequential_payroll() in backend/domain/payroll/sequential_executor.py.

Pure function tests — no database access required.

Salary fixture:
  BASIC      = 300,000
  HOUSING    = 150,000
  TRANSPORT  =  50,000
  GROSS      = 500,000

Tax bands (simplified 3-tier):
  0–300k   @ 7%
  300k–600k @ 11%
  600k+     @ 15%

Expected monthly values (annualize × 12, de-annualize ÷ 12):
  Annual taxable (GROSS - PENSION)  = (500,000 - 40,000) × 12 = 5,520,000
  Annual PAYE  = 300k×7% + 300k×11% + 4,920k×15% = 21,000+33,000+738,000 = 792,000
  Monthly PAYE = 792,000 / 12 = 66,000.00
  NHF          = 300,000 × 2.5%   = 7,500.00
  PENSION_EMP  = 500,000 × 8%     = 40,000.00
  NET_PAY      = 500,000 - 40,000 - 66,000 - 7,500 = 386,500.00
"""
from decimal import Decimal

import pytest

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

SALARY = {
    "BASIC":     Decimal("300000"),
    "HOUSING":   Decimal("150000"),
    "TRANSPORT": Decimal("50000"),
}

# Standard component metadata — mirrors the Nigerian statutory execution order
COMPONENT_METADATA = [
    {"component_code": "BASIC",            "component_class": "earning",              "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
    {"component_code": "HOUSING",          "component_class": "earning",              "calculation_method": "salary_component", "execution_priority": 20,  "is_active": True, "metadata_json": {}},
    {"component_code": "TRANSPORT",        "component_class": "earning",              "calculation_method": "salary_component", "execution_priority": 30,  "is_active": True, "metadata_json": {}},
    {"component_code": "GROSS_PAY",        "component_class": "derived",              "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
    {"component_code": "PENSION_EMPLOYEE", "component_class": "statutory_deduction",  "calculation_method": "pension_rule",     "execution_priority": 200, "is_active": True, "metadata_json": {}},
    {"component_code": "TAXABLE_INCOME",   "component_class": "derived",              "calculation_method": "taxable_income",   "execution_priority": 300, "is_active": True, "metadata_json": {}},
    {"component_code": "PAYE",             "component_class": "statutory_deduction",  "calculation_method": "paye_rule",        "execution_priority": 400, "is_active": True, "metadata_json": {}},
    {"component_code": "NHF_CONTRIBUTION", "component_class": "statutory_deduction",  "calculation_method": "nhf_rule",         "execution_priority": 410, "is_active": True, "metadata_json": {}},
    {"component_code": "NET_PAY",          "component_class": "derived",              "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
]

BASE_CONTEXT = {
    "tax_bands":             TAX_BANDS,
    "pension_employee_rate": Decimal("0.08"),
    "pension_employer_rate": Decimal("0.10"),
    "nhf_rate":              Decimal("0.025"),
    "employee_inputs":       {},
    "client_meta":           {},
    "period":                build_period_context("2026-03-01", "2026-03-31"),
}


def run(salary=None, meta=None, context=None):
    """Convenience wrapper."""
    return run_sequential_payroll(
        salary_components=salary or SALARY,
        component_metadata=meta or COMPONENT_METADATA,
        context=context or BASE_CONTEXT,
    )


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

class TestFullMonthlyPayroll:

    def test_gross_pay(self):
        out = run()
        assert out["results"]["GROSS_PAY"] == Decimal("500000")

    def test_pension_employee(self):
        out = run()
        assert out["results"]["PENSION_EMPLOYEE"] == Decimal("40000.00")

    def test_taxable_income(self):
        out = run()
        assert out["results"]["TAXABLE_INCOME"] == Decimal("460000.00")

    def test_paye(self):
        out = run()
        assert out["results"]["PAYE"] == Decimal("66000.00")

    def test_nhf(self):
        out = run()
        assert out["results"]["NHF_CONTRIBUTION"] == Decimal("7500.00")

    def test_net_pay(self):
        out = run()
        assert out["results"]["NET_PAY"] == Decimal("386500.00")

    def test_trace_has_one_entry_per_component(self):
        out = run()
        # One trace entry per active, executable component
        assert len(out["trace"]) == len(COMPONENT_METADATA)

    def test_inactive_components_excluded(self):
        """is_active=False components are not executed and not in results."""
        meta = [
            {**m, "is_active": False} if m["component_code"] == "NHF_CONTRIBUTION" else m
            for m in COMPONENT_METADATA
        ]
        out = run(meta=meta)
        # NHF not in results
        assert "NHF_CONTRIBUTION" not in out["results"]
        # NET_PAY is higher without NHF deduction
        assert out["results"]["NET_PAY"] == Decimal("394000.00")


# ---------------------------------------------------------------------------
# PAYE guard
# ---------------------------------------------------------------------------

class TestPayeGuard:

    def test_empty_tax_bands_raises(self):
        ctx = {**BASE_CONTEXT, "tax_bands": []}
        with pytest.raises(ValueError, match="tax_bands is empty"):
            run(context=ctx)


# ---------------------------------------------------------------------------
# Unknown calculation method
# ---------------------------------------------------------------------------

class TestUnknownMethod:

    def test_unknown_method_raises(self):
        bad_meta = COMPONENT_METADATA + [{
            "component_code":     "MYSTERY_COMP",
            "component_class":    "earning",
            "calculation_method": "magic_formula",
            "execution_priority": 15,
            "is_active":          True,
            "metadata_json":      {},
        }]
        with pytest.raises(ValueError, match="Unknown calculation_method"):
            run(meta=bad_meta)


# ---------------------------------------------------------------------------
# Pension base variants
# ---------------------------------------------------------------------------

class TestPensionBase:

    def test_uses_client_meta_pensionable_flags(self):
        """Only BASIC flagged is_pensionable → pension base = 300,000."""
        ctx = {
            **BASE_CONTEXT,
            "client_meta": {
                "BASIC":     {"legal_role": {"is_pensionable": True}},
                "HOUSING":   {"legal_role": {"is_pensionable": False}},
                "TRANSPORT": {"legal_role": {"is_pensionable": False}},
            },
        }
        out = run(context=ctx)
        # 300,000 × 8% = 24,000
        assert out["results"]["PENSION_EMPLOYEE"] == Decimal("24000.00")

    def test_falls_back_to_statutory_set_when_no_flags(self):
        """client_meta present but no is_pensionable=True → BHT fallback."""
        ctx = {
            **BASE_CONTEXT,
            "client_meta": {
                "BASIC":     {"legal_role": {"is_pensionable": False}},
                "HOUSING":   {"legal_role": {"is_pensionable": False}},
            },
        }
        out = run(context=ctx)
        # Falls back to BASIC+HOUSING+TRANSPORT = 500,000 × 8% = 40,000
        assert out["results"]["PENSION_EMPLOYEE"] == Decimal("40000.00")

    def test_falls_back_to_statutory_set_when_client_meta_absent(self):
        """Empty client_meta → BHT fallback."""
        ctx = {**BASE_CONTEXT, "client_meta": {}}
        out = run(context=ctx)
        assert out["results"]["PENSION_EMPLOYEE"] == Decimal("40000.00")


# ---------------------------------------------------------------------------
# NHF uses BASIC only
# ---------------------------------------------------------------------------

class TestNhf:

    def test_nhf_uses_basic_only(self):
        """NHF = BASIC × nhf_rate, not GROSS."""
        out = run()
        expected = Decimal("300000") * Decimal("0.025")
        assert out["results"]["NHF_CONTRIBUTION"] == expected.quantize(Decimal("0.01"))

    def test_nhf_custom_rate(self):
        ctx = {**BASE_CONTEXT, "nhf_rate": Decimal("0.02")}
        out = run(context=ctx)
        assert out["results"]["NHF_CONTRIBUTION"] == Decimal("6000.00")


# ---------------------------------------------------------------------------
# Net pay deducts all statutory deductions
# ---------------------------------------------------------------------------

class TestNetPay:

    def test_net_equals_gross_minus_all_statutory(self):
        out = run()
        r = out["results"]
        statutory_total = (
            r["PENSION_EMPLOYEE"]
            + r["PAYE"]
            + r["NHF_CONTRIBUTION"]
        )
        assert r["NET_PAY"] == r["GROSS_PAY"] - statutory_total

    def test_net_cannot_be_negative(self):
        """With very high deductions the floor is 0 (not tested here — the
        executor does not enforce a floor, so we just verify the arithmetic)."""
        # This is a documentation test — verifying that the executor's net
        # formula is: GROSS − sum(statutory_deductions)
        out = run()
        assert out["results"]["NET_PAY"] > Decimal("0")


# ---------------------------------------------------------------------------
# Pre-prorated salary (mid-period hire)
# ---------------------------------------------------------------------------

class TestProration:

    def test_half_salary_produces_half_gross(self):
        """The caller pre-prorates salary_components before calling the executor.
        Verify the executor chains correctly when components are halved."""
        half_salary = {k: v / 2 for k, v in SALARY.items()}
        out = run(salary=half_salary)
        assert out["results"]["GROSS_PAY"] == Decimal("250000")

    def test_half_salary_net_pay_is_proportional(self):
        """Pre-prorated salary → NET_PAY approximately half of full-month NET."""
        full_net = run()["results"]["NET_PAY"]
        half_salary = {k: v / 2 for k, v in SALARY.items()}
        half_net = run(salary=half_salary)["results"]["NET_PAY"]
        # NET is not exactly half due to progressive PAYE, but it should be lower
        assert half_net < full_net


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:

    def test_same_inputs_produce_same_results(self):
        out1 = run()
        out2 = run()
        assert out1["results"] == out2["results"]
