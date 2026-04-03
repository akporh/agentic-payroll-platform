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

from backend.domain.payroll.sequential_executor import (
    run_sequential_payroll,
    register_handler,
    build_runtime_component_registry,
    RULE_COMPONENT_PRIORITY,
)
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
        # One trace entry per active, executable component; plus one leading
        # _period_context header entry added by the sequential executor.
        component_entries = [t for t in out["trace"] if t["component"] != "_period_context"]
        assert len(component_entries) == len(COMPONENT_METADATA)

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


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

class TestHandlerRegistry:

    def test_custom_handler_registered_and_executed(self):
        """A handler registered via register_handler() runs without editing the executor."""
        from decimal import Decimal as D

        def _handle_flat_fee(code, meta_json, results, salary_components, ctx):
            return {code: D("999.00")}

        register_handler("flat_fee", _handle_flat_fee)

        meta_with_custom = COMPONENT_METADATA + [{
            "component_code":     "ADMIN_FEE",
            "component_class":    "statutory_deduction",
            "calculation_method": "flat_fee",
            "execution_priority": 450,
            "is_active":          True,
            "metadata_json":      {},
        }]

        out = run(meta=meta_with_custom)
        assert out["results"]["ADMIN_FEE"] == D("999.00")
        # ADMIN_FEE is a statutory_deduction so it reduces NET_PAY
        assert out["results"]["NET_PAY"] == Decimal("386500.00") - D("999.00")

    def test_unknown_method_raises_with_helpful_message(self):
        """Error message names the method and tells the developer what to do."""
        bad_meta = COMPONENT_METADATA + [{
            "component_code":     "MYSTERY",
            "component_class":    "earning",
            "calculation_method": "unknown_magic",
            "execution_priority": 15,
            "is_active":          True,
            "metadata_json":      {},
        }]
        with pytest.raises(ValueError, match="unknown_magic"):
            run(meta=bad_meta)

        with pytest.raises(ValueError, match="register_handler"):
            run(meta=bad_meta)


# ---------------------------------------------------------------------------
# Configurable component names (non-standard salary structures)
# ---------------------------------------------------------------------------

class TestConfigurableComponentNames:

    def test_nhf_configurable_base_component(self):
        """A client using BASIC_SALARY instead of BASIC: set meta_json.base_component."""
        salary_alt = {
            "BASIC_SALARY": Decimal("300000"),
            "HOUSING":      Decimal("150000"),
            "TRANSPORT":    Decimal("50000"),
        }
        meta_alt = [
            {**m, "component_code": "BASIC_SALARY"} if m["component_code"] == "BASIC" else m
            for m in COMPONENT_METADATA
        ]
        # NHF component now points to the renamed base
        meta_alt = [
            {**m, "metadata_json": {"base_component": "BASIC_SALARY"}}
            if m["component_code"] == "NHF_CONTRIBUTION" else m
            for m in meta_alt
        ]
        out = run_sequential_payroll(
            salary_components=salary_alt,
            component_metadata=meta_alt,
            context=BASE_CONTEXT,
        )
        # NHF should still be 300,000 × 2.5% = 7,500
        assert out["results"]["NHF_CONTRIBUTION"] == Decimal("7500.00")

    def test_nhf_default_base_is_basic(self):
        """Without meta_json.base_component, NHF defaults to BASIC."""
        out = run()
        assert out["results"]["NHF_CONTRIBUTION"] == Decimal("7500.00")

    def test_pension_configurable_statutory_base(self):
        """Client with BASIC_SALARY naming: statutory_base_components overrides the default."""
        salary_alt = {
            "BASIC_SALARY": Decimal("300000"),
            "HOUSING":      Decimal("150000"),
            "TRANSPORT":    Decimal("50000"),
        }
        meta_alt = [
            {**m, "component_code": "BASIC_SALARY"} if m["component_code"] == "BASIC" else m
            for m in COMPONENT_METADATA
        ]
        # Pension component's metadata_json points to BASIC_SALARY in the fallback set
        meta_alt = [
            {**m, "metadata_json": {"statutory_base_components": ["BASIC_SALARY", "HOUSING", "TRANSPORT"]}}
            if m["component_code"] == "PENSION_EMPLOYEE" else m
            for m in meta_alt
        ]
        out = run_sequential_payroll(
            salary_components=salary_alt,
            component_metadata=meta_alt,
            context={**BASE_CONTEXT, "client_meta": {}},
        )
        # Pension base = 300,000 + 150,000 + 50,000 = 500,000 × 8% = 40,000
        assert out["results"]["PENSION_EMPLOYEE"] == Decimal("40000.00")

    def test_taxable_income_configurable_deductions(self):
        """Adding a new pre-PAYE relief via meta_json.deduct_components (no code change)."""
        # Inject a new relief into results by adding a custom component at priority 290
        def _handle_extra_relief(code, meta_json, results, salary_components, ctx):
            return {code: Decimal("10000.00")}

        register_handler("extra_relief", _handle_extra_relief)

        meta_with_relief = [
            # TAXABLE_INCOME now deducts EXTRA_RELIEF as well
            {**m, "metadata_json": {"deduct_components": ["PENSION_EMPLOYEE", "RENT_RELIEF", "EXTRA_RELIEF"]}}
            if m["component_code"] == "TAXABLE_INCOME" else m
            for m in COMPONENT_METADATA
        ] + [{
            "component_code":     "EXTRA_RELIEF",
            "component_class":    "derived",
            "calculation_method": "extra_relief",
            "execution_priority": 290,
            "is_active":          True,
            "metadata_json":      {},
        }]

        out = run_sequential_payroll(
            salary_components=SALARY,
            component_metadata=meta_with_relief,
            context=BASE_CONTEXT,
        )
        # TAXABLE_INCOME = GROSS(500k) - PENSION(40k) - EXTRA_RELIEF(10k) = 450,000
        assert out["results"]["TAXABLE_INCOME"] == Decimal("450000.00")


# ---------------------------------------------------------------------------
# build_runtime_component_registry
# ---------------------------------------------------------------------------

class TestBuildRuntimeComponentRegistry:
    """Unit tests for build_runtime_component_registry().

    Validates that the unified component registry correctly merges
    platform_metadata with rule-injected components from rule_set_items.
    """

    PLATFORM = [
        {"component_code": "BASIC",     "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
        {"component_code": "GROSS_PAY", "component_class": "derived",             "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
        {"component_code": "NET_PAY",   "component_class": "derived",             "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
    ]

    def test_no_rules_returns_platform_unchanged(self):
        result = build_runtime_component_registry(self.PLATFORM, [], {})
        assert result == self.PLATFORM

    def test_unit_multiplier_rule_added_as_earning(self):
        rules = [{"rule_name": "OVERTIME_PAY", "rule_definition_json": {"calculation_method": "unit_multiplier"}, "rule_type": "EARNING"}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        codes = {m["component_code"]: m for m in result}
        assert "OVERTIME_PAY" in codes
        entry = codes["OVERTIME_PAY"]
        assert entry["component_class"]    == "earning"
        assert entry["calculation_method"] == "salary_component"
        assert entry["execution_priority"] == RULE_COMPONENT_PRIORITY
        assert entry["is_active"] is True

    def test_fixed_amount_rule_added_as_earning(self):
        rules = [{"rule_name": "ACCIDENT_BONUS", "rule_definition_json": {"calculation_method": "fixed_amount"}, "rule_type": None}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        codes = {m["component_code"] for m in result}
        assert "ACCIDENT_BONUS" in codes

    def test_rule_type_deduction_gets_correct_class(self):
        rules = [{"rule_name": "PENALTY_FEE", "rule_definition_json": {"calculation_method": "unit_multiplier"}, "rule_type": "DEDUCTION"}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        entry = next(m for m in result if m["component_code"] == "PENALTY_FEE")
        assert entry["component_class"] == "statutory_deduction"

    def test_daily_rate_deduction_not_added(self):
        rules = [{"rule_name": "ABSENCE_DEDUCTION", "rule_definition_json": {"calculation_method": "daily_rate_deduction"}, "rule_type": "DEDUCTION"}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        codes = {m["component_code"] for m in result}
        assert "ABSENCE_DEDUCTION" not in codes

    def test_rule_name_already_in_platform_not_duplicated(self):
        # BASIC is already in PLATFORM — should not be added again
        rules = [{"rule_name": "BASIC", "rule_definition_json": {"calculation_method": "unit_multiplier"}, "rule_type": "EARNING"}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        basics = [m for m in result if m["component_code"] == "BASIC"]
        assert len(basics) == 1

    def test_null_rule_type_defaults_to_earning(self):
        rules = [{"rule_name": "WEEKEND_PAY", "rule_definition_json": {"calculation_method": "unit_multiplier"}, "rule_type": None}]
        result = build_runtime_component_registry(self.PLATFORM, rules, {})
        entry = next(m for m in result if m["component_code"] == "WEEKEND_PAY")
        assert entry["component_class"] == "earning"


class TestRuleInjectedEarningInGrossPay:
    """Integration test: rule-injected earning flows through unified registry into GROSS_PAY."""

    def test_rule_injected_earning_included_in_gross_pay(self):
        # salary_components includes a rule-injected key (e.g. from apply_payroll_rules)
        salary = {
            "BASIC":         Decimal("300000"),
            "HOUSING":       Decimal("150000"),
            "TRANSPORT":     Decimal("50000"),
            "OVERTIME_PAY":  Decimal("20000"),   # rule-injected — not in platform metadata
        }

        # Build unified registry: platform + OVERTIME_PAY rule
        rules = [{"rule_name": "OVERTIME_PAY", "rule_definition_json": {"calculation_method": "unit_multiplier"}, "rule_type": "EARNING"}]
        unified = build_runtime_component_registry(COMPONENT_METADATA, rules, {})

        context = {
            "tax_bands":              TAX_BANDS,
            "pension_employee_rate":  Decimal("0.08"),
            "pension_employer_rate":  Decimal("0.10"),
            "nhf_rate":               Decimal("0.025"),
        }
        out = run_sequential_payroll(salary, unified, context)

        # GROSS_PAY must include the rule-injected OVERTIME_PAY
        assert out["results"]["GROSS_PAY"] == Decimal("520000.00")  # 300k+150k+50k+20k
        assert "OVERTIME_PAY" in out["results"]

    def test_rule_free_employee_gross_pay_unchanged(self):
        # No rules → unified registry = platform metadata → identical output
        unified = build_runtime_component_registry(COMPONENT_METADATA, [], {})
        context = {
            "tax_bands":              TAX_BANDS,
            "pension_employee_rate":  Decimal("0.08"),
            "pension_employer_rate":  Decimal("0.10"),
            "nhf_rate":               Decimal("0.025"),
        }
        out = run_sequential_payroll(SALARY, unified, context)
        assert out["results"]["GROSS_PAY"] == Decimal("500000.00")
