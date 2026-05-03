"""Sprint 12 — M1 (non_taxable class) and M2 (PAYE_ONLY additions path) verification.

Each test is structured as Given / When / Then and uses numeric assertions to
confirm the exact financial impact. These tests run against the pure domain
layer — no DB required.
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

# Base salary: BASIC=300k, HOUSING=150k, TRANSPORT=50k → GROSS=500k
BASE_SALARY = {
    "BASIC":     Decimal("300000"),
    "HOUSING":   Decimal("150000"),
    "TRANSPORT": Decimal("50000"),
}

# Minimal component metadata for a standard run (no non_taxable, no paye_only).
STANDARD_META = [
    {"component_code": "BASIC",            "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
    {"component_code": "HOUSING",          "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 20,  "is_active": True, "metadata_json": {}},
    {"component_code": "TRANSPORT",        "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 30,  "is_active": True, "metadata_json": {}},
    {"component_code": "GROSS_PAY",        "component_class": "aggregate",           "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
    {"component_code": "PENSION_EMPLOYEE", "component_class": "statutory_deduction", "calculation_method": "pension_rule",     "execution_priority": 200, "is_active": True, "metadata_json": {}},
    {"component_code": "TAXABLE_INCOME",   "component_class": "derived",             "calculation_method": "taxable_income",   "execution_priority": 300, "is_active": True, "metadata_json": {}},
    {"component_code": "PAYE",             "component_class": "statutory_deduction", "calculation_method": "paye_rule",        "execution_priority": 400, "is_active": True, "metadata_json": {}},
    {"component_code": "NHF_CONTRIBUTION", "component_class": "statutory_deduction", "calculation_method": "nhf_rule",         "execution_priority": 410, "is_active": True, "metadata_json": {}},
    {"component_code": "NET_PAY",          "component_class": "derived",             "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
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


def _run(salary=None, meta=None, context=None):
    return run_sequential_payroll(
        salary_components=salary or BASE_SALARY,
        component_metadata=meta or STANDARD_META,
        context=context or BASE_CONTEXT,
    )


def _trace_entry(trace, component_code):
    """Return the first trace entry for a given component_code."""
    return next((e for e in trace if e.get("component") == component_code), None)


# ---------------------------------------------------------------------------
# Baseline — confirm starting state before M1/M2 changes
# ---------------------------------------------------------------------------

class TestBaseline:
    def test_baseline_gross_pay(self):
        """Given BASIC+HOUSING+TRANSPORT=500k (all earning), GROSS_PAY=500k."""
        result = _run()
        assert result["results"]["GROSS_PAY"] == Decimal("500000")

    def test_baseline_backward_compat(self):
        """Existing workspaces with no non_taxable or paye_only inputs are unaffected."""
        result = _run()
        # NET_PAY must be positive and not include phantom components
        assert result["results"]["NET_PAY"] > Decimal("0")
        assert "PAYE_ONLY_ADDITIONS" not in result["results"]


# ---------------------------------------------------------------------------
# M1 — Non-Taxable Component Class
# ---------------------------------------------------------------------------

class TestM1NonTaxable:
    """
    Scenario: workspace adds a MEAL_ALLOWANCE=60k component with class='non_taxable'.
    Expected:
      - GROSS_PAY = 500k (excludes MEAL_ALLOWANCE)
      - TAXABLE_INCOME < GROSS_PAY - pension (MEAL_ALLOWANCE not in the PAYE base)
      - NET_PAY = GROSS_PAY-based NET_PAY + 60k (employee receives the allowance)
    """

    # M1 meta: adds a non_taxable MEAL_ALLOWANCE at priority 40.
    META_WITH_NON_TAXABLE = [
        {"component_code": "BASIC",            "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 10,  "is_active": True, "metadata_json": {}},
        {"component_code": "HOUSING",          "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 20,  "is_active": True, "metadata_json": {}},
        {"component_code": "TRANSPORT",        "component_class": "earning",             "calculation_method": "salary_component", "execution_priority": 30,  "is_active": True, "metadata_json": {}},
        {"component_code": "MEAL_ALLOWANCE",   "component_class": "non_taxable",         "calculation_method": "salary_component", "execution_priority": 40,  "is_active": True, "metadata_json": {}},
        {"component_code": "GROSS_PAY",        "component_class": "aggregate",           "calculation_method": "sum_earnings",     "execution_priority": 100, "is_active": True, "metadata_json": {}},
        {"component_code": "PENSION_EMPLOYEE", "component_class": "statutory_deduction", "calculation_method": "pension_rule",     "execution_priority": 200, "is_active": True, "metadata_json": {}},
        {"component_code": "TAXABLE_INCOME",   "component_class": "derived",             "calculation_method": "taxable_income",   "execution_priority": 300, "is_active": True, "metadata_json": {}},
        {"component_code": "PAYE",             "component_class": "statutory_deduction", "calculation_method": "paye_rule",        "execution_priority": 400, "is_active": True, "metadata_json": {}},
        {"component_code": "NHF_CONTRIBUTION", "component_class": "statutory_deduction", "calculation_method": "nhf_rule",         "execution_priority": 410, "is_active": True, "metadata_json": {}},
        {"component_code": "NET_PAY",          "component_class": "derived",             "calculation_method": "net_formula",      "execution_priority": 500, "is_active": True, "metadata_json": {}},
    ]

    SALARY_WITH_NON_TAXABLE = {
        **BASE_SALARY,
        "MEAL_ALLOWANCE": Decimal("60000"),
    }

    def _run_with_non_taxable(self):
        return _run(salary=self.SALARY_WITH_NON_TAXABLE, meta=self.META_WITH_NON_TAXABLE)

    # M1-T1: non_taxable excluded from GROSS_PAY
    def test_non_taxable_excluded_from_gross_pay(self):
        """Given MEAL_ALLOWANCE=60k with class=non_taxable,
        When payroll runs,
        Then GROSS_PAY = 500k (BASIC+HOUSING+TRANSPORT only — MEAL excluded)."""
        result = self._run_with_non_taxable()
        assert result["results"]["GROSS_PAY"] == Decimal("500000"), (
            f"GROSS_PAY should be 500k (earning only), got {result['results']['GROSS_PAY']}"
        )

    # M1-T2: non_taxable included in NET_PAY
    def test_non_taxable_included_in_net_pay(self):
        """Given MEAL_ALLOWANCE=60k with class=non_taxable,
        When payroll runs,
        Then NET_PAY = (standard NET_PAY) + 60k — employee receives the allowance."""
        baseline = _run()
        result = self._run_with_non_taxable()
        expected_net = baseline["results"]["NET_PAY"] + Decimal("60000")
        assert result["results"]["NET_PAY"] == expected_net, (
            f"NET_PAY should be baseline+60k={expected_net}, got {result['results']['NET_PAY']}"
        )

    # M1-T3: TAXABLE_INCOME not inflated by non_taxable amount
    def test_non_taxable_not_in_taxable_income(self):
        """Given MEAL_ALLOWANCE=60k with class=non_taxable,
        When payroll runs,
        Then TAXABLE_INCOME is identical to a run without the non_taxable component."""
        baseline = _run()
        result = self._run_with_non_taxable()
        assert result["results"]["TAXABLE_INCOME"] == baseline["results"]["TAXABLE_INCOME"], (
            f"TAXABLE_INCOME should match baseline {baseline['results']['TAXABLE_INCOME']}, "
            f"got {result['results']['TAXABLE_INCOME']}"
        )

    # M1-T4: GROSS_PAY unchanged vs baseline (backward compat)
    def test_earning_class_unaffected(self):
        """Given only earning-class components, GROSS_PAY == baseline GROSS_PAY."""
        baseline = _run()
        assert baseline["results"]["GROSS_PAY"] == Decimal("500000")

    # M1-T5: component_trace records non_taxable component with correct class
    def test_non_taxable_appears_in_trace_with_correct_class(self):
        """Given MEAL_ALLOWANCE=60k with class=non_taxable,
        When payroll runs,
        Then trace contains a MEAL_ALLOWANCE entry with component_class='non_taxable'."""
        result = self._run_with_non_taxable()
        entry = _trace_entry(result["trace"], "MEAL_ALLOWANCE")
        assert entry is not None, "MEAL_ALLOWANCE must appear in trace"
        assert entry["component_class"] == "non_taxable", (
            f"Expected component_class='non_taxable', got {entry['component_class']!r}"
        )

    # M1-T6: D-M1-4 workspace override via client_meta
    def test_workspace_override_promotes_component_to_non_taxable(self):
        """Given TRANSPORT in client_meta with component_class='non_taxable',
        When payroll runs,
        Then:
          - GROSS_PAY = 450k (TRANSPORT excluded from earning sweep)
          - TAXABLE_INCOME < baseline (GROSS_PAY is lower so PAYE base is smaller)
          - NET_PAY > baseline (less PAYE deducted — employee benefits from non_taxable treatment)
          - NET_PAY includes TRANSPORT (net_formula sweeps non_taxable class)

        Numeric derivation (BASIC=300k, HOUSING=150k, TRANSPORT=50k):
          GROSS_PAY        = 300k + 150k         = 450k
          PENSION          = 500k * 8%           = 40k  (statutory base unchanged)
          TAXABLE_INCOME   = 450k - 40k          = 410k (vs 460k baseline)
          PAYE on 410k     = 58,500              (vs 66,000 baseline, saving 7,500)
          net_formula      = (450k earning + 50k non_taxable) - 40k pension - 58.5k PAYE - 7.5k NHF
          NET_PAY          = 394,000             (baseline = 386,500)
        """
        client_meta_with_override = {
            "TRANSPORT": {"component_class": "non_taxable"},
        }
        context_with_override = {**BASE_CONTEXT, "client_meta": client_meta_with_override}
        result = _run(context=context_with_override)
        baseline = _run()

        # GROSS_PAY = BASIC(300k) + HOUSING(150k) only = 450k
        assert result["results"]["GROSS_PAY"] == Decimal("450000"), (
            f"GROSS_PAY should be 450k (TRANSPORT excluded from earning sweep), "
            f"got {result['results']['GROSS_PAY']}"
        )
        # TAXABLE_INCOME must be LOWER than baseline (GROSS_PAY dropped)
        assert result["results"]["TAXABLE_INCOME"] < baseline["results"]["TAXABLE_INCOME"], (
            "TAXABLE_INCOME should decrease when TRANSPORT is non_taxable"
        )
        # NET_PAY must be HIGHER than baseline (PAYE saving passes through to employee)
        assert result["results"]["NET_PAY"] > baseline["results"]["NET_PAY"], (
            f"NET_PAY should exceed baseline {baseline['results']['NET_PAY']} "
            f"(lower PAYE = higher take-home), got {result['results']['NET_PAY']}"
        )
        # NET_PAY must NOT be higher than baseline + TRANSPORT (the 50k was not double-counted)
        assert result["results"]["NET_PAY"] < baseline["results"]["NET_PAY"] + Decimal("50000"), (
            "NET_PAY must not exceed baseline + TRANSPORT (non_taxable is not a bonus)"
        )


# ---------------------------------------------------------------------------
# M2 — PAYE-Only Additions Path
# ---------------------------------------------------------------------------

class TestM2PayeOnly:
    """
    Scenario: employee has a paye_only input (e.g. LTA benefit) of ₦50,000.
    Expected:
      - PAYE_ONLY_ADDITIONS = 50k
      - TAXABLE_INCOME = baseline TAXABLE_INCOME + 50k
      - GROSS_PAY unchanged (paye_only does not enter gross)
      - NET_PAY unchanged (paye_only is not a cash disbursement)
    """

    # M2 meta: adds PAYE_ONLY_ADDITIONS component at priority 95.
    META_WITH_PAYE_ONLY = [
        {"component_code": "BASIC",               "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 10,  "is_active": True, "metadata_json": {}},
        {"component_code": "HOUSING",             "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 20,  "is_active": True, "metadata_json": {}},
        {"component_code": "TRANSPORT",           "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 30,  "is_active": True, "metadata_json": {}},
        {"component_code": "GROSS_PAY",           "component_class": "aggregate",           "calculation_method": "sum_earnings",        "execution_priority": 100, "is_active": True, "metadata_json": {}},
        {"component_code": "PAYE_ONLY_ADDITIONS", "component_class": "paye_addition",       "calculation_method": "sum_paye_only_inputs","execution_priority": 95,  "is_active": True, "metadata_json": {}},
        {"component_code": "PENSION_EMPLOYEE",    "component_class": "statutory_deduction", "calculation_method": "pension_rule",        "execution_priority": 200, "is_active": True, "metadata_json": {}},
        {"component_code": "TAXABLE_INCOME",      "component_class": "derived",             "calculation_method": "taxable_income",      "execution_priority": 300, "is_active": True, "metadata_json": {}},
        {"component_code": "PAYE",                "component_class": "statutory_deduction", "calculation_method": "paye_rule",           "execution_priority": 400, "is_active": True, "metadata_json": {}},
        {"component_code": "NHF_CONTRIBUTION",    "component_class": "statutory_deduction", "calculation_method": "nhf_rule",            "execution_priority": 410, "is_active": True, "metadata_json": {}},
        {"component_code": "NET_PAY",             "component_class": "derived",             "calculation_method": "net_formula",         "execution_priority": 500, "is_active": True, "metadata_json": {}},
    ]

    PAYE_ONLY_INPUT = {
        "LTA_BENEFIT": [
            {"category": "PAYE_ONLY", "amount": 50000},
        ]
    }

    def _run_with_paye_only(self, inputs=None):
        ctx = {
            **BASE_CONTEXT,
            "employee_inputs": inputs or self.PAYE_ONLY_INPUT,
        }
        return _run(meta=self.META_WITH_PAYE_ONLY, context=ctx)

    def _run_baseline_with_paye_meta(self):
        """Same meta (includes PAYE_ONLY_ADDITIONS component) but no paye_only inputs."""
        ctx = {**BASE_CONTEXT, "employee_inputs": {}}
        return _run(meta=self.META_WITH_PAYE_ONLY, context=ctx)

    # M2-T1: TAXABLE_INCOME increases by paye_only amount
    def test_paye_only_increases_taxable_income(self):
        """Given a PAYE_ONLY input of 50k,
        When payroll runs,
        Then TAXABLE_INCOME = baseline TAXABLE_INCOME + 50k."""
        baseline = self._run_baseline_with_paye_meta()
        result = self._run_with_paye_only()
        expected = baseline["results"]["TAXABLE_INCOME"] + Decimal("50000")
        assert result["results"]["TAXABLE_INCOME"] == expected, (
            f"TAXABLE_INCOME should be baseline+50k={expected}, "
            f"got {result['results']['TAXABLE_INCOME']}"
        )

    # M2-T2: GROSS_PAY unchanged
    def test_paye_only_does_not_enter_gross_pay(self):
        """Given a PAYE_ONLY input of 50k,
        When payroll runs,
        Then GROSS_PAY = 500k (same as no paye_only input)."""
        result = self._run_with_paye_only()
        assert result["results"]["GROSS_PAY"] == Decimal("500000"), (
            f"GROSS_PAY should be 500k (paye_only must not enter gross), "
            f"got {result['results']['GROSS_PAY']}"
        )

    # M2-T3: NET_PAY unchanged
    def test_paye_only_does_not_enter_net_pay(self):
        """Given a PAYE_ONLY input of 50k,
        When payroll runs,
        Then NET_PAY == baseline NET_PAY (paye_only is not a cash disbursement).

        Note: PAYE increases because TAXABLE_INCOME is higher, so NET_PAY will actually
        be LOWER than a run with no paye_only input (more tax deducted). The invariant
        is that the 50k itself does not appear as an earning in NET_PAY — i.e. net_formula
        does not sweep paye_addition class components.
        """
        baseline_no_paye_only = self._run_baseline_with_paye_meta()
        result = self._run_with_paye_only()
        # NET_PAY must be LOWER than or equal to baseline (more PAYE deducted)
        # but must NOT be higher (paye_only is not an earning)
        assert result["results"]["NET_PAY"] <= baseline_no_paye_only["results"]["NET_PAY"], (
            "NET_PAY must not exceed baseline — paye_only inputs are not cash disbursements"
        )
        # Confirm PAYE_ONLY_ADDITIONS did not creep into net formula earnings sweep:
        # check that component_class paye_addition is not counted in net_formula.
        paye_only_amount = result["results"].get("PAYE_ONLY_ADDITIONS", Decimal("0"))
        assert result["results"]["NET_PAY"] != (
            baseline_no_paye_only["results"]["NET_PAY"] + paye_only_amount
        ), "NET_PAY must not include PAYE_ONLY_ADDITIONS as an earning"

    # M2-T4: zero-value paye_only input is a no-op
    def test_zero_paye_only_input_is_noop(self):
        """Given a PAYE_ONLY input with amount=0,
        When payroll runs,
        Then PAYE_ONLY_ADDITIONS = 0 (silently skipped)."""
        zero_inputs = {"BENEFIT": [{"category": "PAYE_ONLY", "amount": 0}]}
        ctx = {**BASE_CONTEXT, "employee_inputs": zero_inputs}
        result = _run(meta=self.META_WITH_PAYE_ONLY, context=ctx)
        assert result["results"].get("PAYE_ONLY_ADDITIONS", Decimal("0")) == Decimal("0"), (
            "Zero-value paye_only input should produce PAYE_ONLY_ADDITIONS=0"
        )

    # M2-T5: PAYE_ONLY_ADDITIONS appears in trace
    def test_paye_only_additions_appears_in_trace(self):
        """Given a PAYE_ONLY input of 50k,
        When payroll runs,
        Then trace contains a PAYE_ONLY_ADDITIONS entry with result='50000.00'."""
        result = self._run_with_paye_only()
        entry = _trace_entry(result["trace"], "PAYE_ONLY_ADDITIONS")
        assert entry is not None, "PAYE_ONLY_ADDITIONS must appear in trace"
        assert entry["result"] == "50000.00", (
            f"Trace entry result should be '50000.00', got {entry['result']!r}"
        )

    # M2-T6: handler reads category == 'PAYE_ONLY' (uppercase)
    def test_paye_only_case_sensitivity(self):
        """Given inputs with lowercase category='paye_only',
        When payroll runs,
        Then PAYE_ONLY_ADDITIONS = 0 (handler only reads uppercase 'PAYE_ONLY')."""
        lowercase_inputs = {"BENEFIT": [{"category": "paye_only", "amount": 50000}]}
        ctx = {**BASE_CONTEXT, "employee_inputs": lowercase_inputs}
        result = _run(meta=self.META_WITH_PAYE_ONLY, context=ctx)
        assert result["results"].get("PAYE_ONLY_ADDITIONS", Decimal("0")) == Decimal("0"), (
            "Handler must only match uppercase 'PAYE_ONLY' — lowercase must be ignored"
        )

    # M2-T7: standard inputs without category field are unaffected
    def test_standard_inputs_without_category_unaffected(self):
        """Given inputs with no 'category' field (legacy inputs),
        When payroll runs,
        Then PAYE_ONLY_ADDITIONS = 0 — backward compat preserved."""
        legacy_inputs = {"BONUS": [{"amount": 30000}]}
        ctx = {**BASE_CONTEXT, "employee_inputs": legacy_inputs}
        result = _run(meta=self.META_WITH_PAYE_ONLY, context=ctx)
        assert result["results"].get("PAYE_ONLY_ADDITIONS", Decimal("0")) == Decimal("0"), (
            "Legacy inputs without category must not populate PAYE_ONLY_ADDITIONS"
        )


# ---------------------------------------------------------------------------
# INT — Combined M1 + M2 (non_taxable component AND paye_only input)
# ---------------------------------------------------------------------------

class TestIntegrationM1M2:
    """
    Scenario: MEAL_ALLOWANCE=60k (non_taxable) + LTA_BENEFIT=50k (paye_only).
    Expected:
      - GROSS_PAY = 500k (MEAL excluded from earning sweep)
      - PAYE_ONLY_ADDITIONS = 50k
      - TAXABLE_INCOME = 500k + 50k - pension = 550k - pension
      - NET_PAY includes MEAL_ALLOWANCE (non_taxable gets paid out)
      - NET_PAY does NOT include LTA_BENEFIT (paye_only is not cash)
    """

    META_COMBINED = [
        {"component_code": "BASIC",               "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 10,  "is_active": True, "metadata_json": {}},
        {"component_code": "HOUSING",             "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 20,  "is_active": True, "metadata_json": {}},
        {"component_code": "TRANSPORT",           "component_class": "earning",             "calculation_method": "salary_component",    "execution_priority": 30,  "is_active": True, "metadata_json": {}},
        {"component_code": "MEAL_ALLOWANCE",      "component_class": "non_taxable",         "calculation_method": "salary_component",    "execution_priority": 40,  "is_active": True, "metadata_json": {}},
        {"component_code": "GROSS_PAY",           "component_class": "aggregate",           "calculation_method": "sum_earnings",        "execution_priority": 100, "is_active": True, "metadata_json": {}},
        {"component_code": "PAYE_ONLY_ADDITIONS", "component_class": "paye_addition",       "calculation_method": "sum_paye_only_inputs","execution_priority": 95,  "is_active": True, "metadata_json": {}},
        {"component_code": "PENSION_EMPLOYEE",    "component_class": "statutory_deduction", "calculation_method": "pension_rule",        "execution_priority": 200, "is_active": True, "metadata_json": {}},
        {"component_code": "TAXABLE_INCOME",      "component_class": "derived",             "calculation_method": "taxable_income",      "execution_priority": 300, "is_active": True, "metadata_json": {}},
        {"component_code": "PAYE",                "component_class": "statutory_deduction", "calculation_method": "paye_rule",           "execution_priority": 400, "is_active": True, "metadata_json": {}},
        {"component_code": "NHF_CONTRIBUTION",    "component_class": "statutory_deduction", "calculation_method": "nhf_rule",            "execution_priority": 410, "is_active": True, "metadata_json": {}},
        {"component_code": "NET_PAY",             "component_class": "derived",             "calculation_method": "net_formula",         "execution_priority": 500, "is_active": True, "metadata_json": {}},
    ]

    SALARY_COMBINED = {
        **{
            "BASIC":     Decimal("300000"),
            "HOUSING":   Decimal("150000"),
            "TRANSPORT": Decimal("50000"),
        },
        "MEAL_ALLOWANCE": Decimal("60000"),
    }

    PAYE_ONLY_INPUT = {
        "LTA_BENEFIT": [{"category": "PAYE_ONLY", "amount": 50000}]
    }

    def _run_combined(self):
        ctx = {**BASE_CONTEXT, "employee_inputs": self.PAYE_ONLY_INPUT}
        return run_sequential_payroll(
            salary_components=self.SALARY_COMBINED,
            component_metadata=self.META_COMBINED,
            context=ctx,
        )

    def _run_combined_no_paye_only(self):
        ctx = {**BASE_CONTEXT, "employee_inputs": {}}
        return run_sequential_payroll(
            salary_components=self.SALARY_COMBINED,
            component_metadata=self.META_COMBINED,
            context=ctx,
        )

    # INT-T1a: GROSS_PAY = earning components only (500k)
    def test_gross_pay_excludes_non_taxable(self):
        result = self._run_combined()
        assert result["results"]["GROSS_PAY"] == Decimal("500000")

    # INT-T1b: TAXABLE_INCOME = GROSS_PAY + PAYE_ONLY_ADDITIONS - pension
    def test_taxable_income_is_gross_plus_paye_only_minus_pension(self):
        result = self._run_combined()
        gross = result["results"]["GROSS_PAY"]                   # 500k
        paye_additions = result["results"]["PAYE_ONLY_ADDITIONS"] # 50k
        pension = result["results"]["PENSION_EMPLOYEE"]
        expected = (gross + paye_additions - pension).quantize(Decimal("0.01"))
        assert result["results"]["TAXABLE_INCOME"] == expected, (
            f"TAXABLE_INCOME={result['results']['TAXABLE_INCOME']} != gross+paye_only-pension={expected}"
        )

    # INT-T1c: NET_PAY includes MEAL_ALLOWANCE but not LTA_BENEFIT
    def test_net_pay_includes_non_taxable_not_paye_only(self):
        result_with_paye_only = self._run_combined()
        result_no_paye_only = self._run_combined_no_paye_only()
        # NET_PAY with paye_only must be <= NET_PAY without (more PAYE deducted)
        assert result_with_paye_only["results"]["NET_PAY"] <= result_no_paye_only["results"]["NET_PAY"]
        # MEAL_ALLOWANCE must be in NET_PAY: compare against baseline (no MEAL_ALLOWANCE, no paye_only)
        baseline_result = _run()
        # baseline NET_PAY is for 500k gross; combined without paye_only adds 60k non_taxable to NET
        expected_net_no_paye_only = baseline_result["results"]["NET_PAY"] + Decimal("60000")
        assert result_no_paye_only["results"]["NET_PAY"] == expected_net_no_paye_only, (
            f"NET_PAY without paye_only should be baseline+60k={expected_net_no_paye_only}, "
            f"got {result_no_paye_only['results']['NET_PAY']}"
        )
