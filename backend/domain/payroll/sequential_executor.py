"""
Sequential Payroll Executor.

Executes payroll components in execution_priority order, driven by
component_metadata.  Each component's calculation_method is dispatched
through a **handler registry** (_HANDLERS dict) rather than a hard-coded
if/elif chain.  New statutory contributions can be added by calling
``register_handler()`` without touching this file.

Execution order for Nigeria (NG):
  10  BASIC                  salary_component
  20  HOUSING                salary_component
  30  TRANSPORT              salary_component
  40  CONSOLIDATED_ALLOWANCE salary_component
 100  GROSS_PAY              sum_earnings
 200  PENSION_EMPLOYEE       pension_rule
 250  RENT_RELIEF            rent_relief      (skipped if ANNUAL_RENT_PAID absent)
 300  TAXABLE_INCOME         taxable_income   (configurable deduct_components)
 400  PAYE                   paye_rule        (bands applied to TAXABLE_INCOME)
 410  NHF_CONTRIBUTION       nhf_rule         (configurable base_component)
 420  HEALTH_INSURANCE_EMPLOYEE health_insurance_flat
 430  DEVELOPMENT_LEVY       development_levy_flat
 440  LIFE_INSURANCE         life_insurance_rule
 450  CHECK_OFF_DUES         salary_component     (value injected by rule_evaluator percentage_of_sum)
 460  NSITF_EMPLOYER_COST    nsitf_employer       (employer cost, excluded from NET_PAY)
 470  ITF_EMPLOYER_COST      itf_employer         (employer cost, excluded from NET_PAY)
 500  NET_PAY                net_formula

Adding a new statutory component (e.g. NSITF):
  1.  Write a pure calculation function (e.g. backend/domain/rules/nsitf.py).
  2.  Register a handler at module level:
        from backend.domain.payroll.sequential_executor import register_handler
        register_handler("nsitf_rule", _handle_nsitf)
  3.  Insert a row in component_metadata with calculation_method="nsitf_rule".
  No changes to this file are needed.
"""

from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

logger = logging.getLogger(__name__)

from backend.domain.payroll.period_context import PeriodContext, build_period_context
from backend.domain.rules.nhf import calculate_nhf
from backend.domain.rules.paye import calculate_paye_for_period
from backend.domain.rules.pension import calculate_pension
from backend.domain.rules.rent_relief import calculate_rent_relief_for_period


# ---------------------------------------------------------------------------
# Handler type and registry
# ---------------------------------------------------------------------------

# Signature: (primary_code, meta_json, accumulated_results, salary_components, ctx)
#   primary_code      — component_code being executed (from component_metadata row)
#   meta_json         — component_metadata.metadata_json for this component
#   accumulated_results — {code: Decimal} built up so far in this run
#   salary_components — original {code: Decimal} salary map (pre-rules)
#   ctx               — merged execution context; includes everything from the
#                       caller's context dict plus two executor-injected keys:
#                         "_component_map": {code: metadata dict}
#                         "period":         PeriodContext (pre-resolved)
#
# Returns: {component_code: Decimal} — all entries are merged into results.
#   Single-output handlers return {primary_code: value}.
#   Multi-output handlers (e.g. pension) may return additional entries
#   (e.g. PENSION_EMPLOYER) as side effects.

_Handler = Callable[
    [str, dict, dict[str, Decimal], dict[str, Decimal], dict],
    dict[str, Decimal],
]

_HANDLERS: dict[str, _Handler] = {}


def register_handler(method_name: str, fn: _Handler) -> None:
    """Register a calculation method handler.

    Call this at module level to add new statutory contributions without
    modifying the executor.

    Args:
        method_name: Value of component_metadata.calculation_method that this
                     handler should be invoked for.
        fn:          Handler function with the signature described in the module
                     docstring.

    Example::

        from backend.domain.payroll.sequential_executor import register_handler
        from decimal import Decimal, ROUND_HALF_UP

        def _handle_nsitf(code, meta_json, results, salary_components, ctx):
            rate = Decimal(str(ctx.get("nsitf_rate", "0.01")))
            return {code: (results.get("GROSS_PAY", Decimal("0")) * rate)
                         .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}

        register_handler("nsitf_rule", _handle_nsitf)
    """
    _HANDLERS[method_name] = fn


# ---------------------------------------------------------------------------
# Internal helpers (shared between executor and handlers)
# ---------------------------------------------------------------------------

def _check_eligibility(
    conditions: list,
    logic: str,
    employee_inputs: dict,
    results: dict,
) -> bool:
    """Evaluate eligibility conditions. Returns True if eligible to run."""
    if not conditions:
        return True

    checks = []
    for cond in conditions:
        cond_type = cond.get("type")

        if cond_type == "input_present":
            checks.append(cond["input_code"] in employee_inputs)

        elif cond_type == "input_value":
            actual    = Decimal(str(employee_inputs.get(cond["input_code"], {}).get("amount") or 0))
            threshold = Decimal(str(cond.get("value", 0)))
            op        = cond.get("operator", "gt")
            checks.append(
                actual > threshold  if op == "gt"  else
                actual >= threshold if op == "gte" else
                actual < threshold  if op == "lt"  else
                actual == threshold if op == "eq"  else False
            )

        elif cond_type == "component_result":
            actual    = results.get(cond["component_code"], Decimal("0"))
            threshold = Decimal(str(cond.get("value", 0)))
            op        = cond.get("operator", "gt")
            checks.append(
                actual > threshold  if op == "gt"  else
                actual >= threshold if op == "gte" else
                actual < threshold  if op == "lt"  else
                actual == threshold if op == "eq"  else False
            )

        else:
            checks.append(True)

    return any(checks) if logic == "ANY" else all(checks)


def _resolve_inputs(input_requirements: dict, employee_inputs: dict) -> dict:
    """Build {input_code: Decimal} for each declared field present in employee_inputs."""
    resolved = {}
    for field in input_requirements.get("fields", []):
        code = field["input_code"]
        if code in employee_inputs:
            raw = employee_inputs[code]
            if isinstance(raw, list):
                total = sum(float(e.get("quantity") or 0) for e in raw if isinstance(e, dict))
            elif isinstance(raw, dict):
                total = float(raw.get("quantity") or raw.get("amount") or 0)
            else:
                total = float(raw or 0)
            resolved[code] = Decimal(str(total))
    return resolved


# ---------------------------------------------------------------------------
# Runtime component registry
# ---------------------------------------------------------------------------

# Execution priority for rule-injected components.
# Slots between base earnings (10–40) and GROSS_PAY (100) so they enter
# results{} before _handle_sum_earnings aggregates them.
RULE_COMPONENT_PRIORITY = 50

_RULE_TYPE_CLASS_MAP: dict[str, str] = {
    "EARNING":   "earning",
    "DEDUCTION": "statutory_deduction",
}


def _infer_component_class(rule_type: str | None) -> str:
    """Map rule_set_item.rule_type to component_class.

    "EARNING"   → "earning"
    "DEDUCTION" → "statutory_deduction"
    None / unrecognised (e.g. legacy "unit_multiplier" stored in rule_type)
        → "earning"  (consistent with payroll_input.py default)
    """
    if not rule_type:
        return "earning"
    return _RULE_TYPE_CLASS_MAP.get(rule_type.upper(), "earning")


def build_runtime_component_registry(
    platform_metadata: list[dict],
    payroll_rules: list[dict],
    employee_inputs: dict,
) -> list[dict]:
    """Build unified component registry at runtime.

    Merges three sources:

    Source 1 — platform_metadata
        component_metadata rows: BASIC, HOUSING, GROSS_PAY, PAYE, NET_PAY, …
        Passed through unchanged.

    Source 2 — dynamic_components_from_rules
        Synthesised from rule_set_item (or legacy payroll_rule) rows whose
        calculation_method is unit_multiplier or fixed_amount.  These methods
        add a *new* key to salary_components (rule_name → computed amount).
        daily_rate_deduction is excluded — it modifies existing keys only.

        Each synthesised entry gets:
          component_class    = _infer_component_class(rule_type)
          calculation_method = "salary_component"   (read pre-computed value)
          execution_priority = RULE_COMPONENT_PRIORITY  (50)
          is_active          = True

        With priority 50, rule-injected components flow through the executor
        and enter results{} before _handle_sum_earnings runs at priority 100.
        No modification to any aggregation handler is required.

    Source 3 — period_input_components
        Direct-pay inputs with no matching rule (future extension point).
        Not yet implemented — parameter accepted for API stability.

    Args:
        platform_metadata: component_metadata rows from the DB.
        payroll_rules:      list of rule dicts (rule_set_item or payroll_rule format).
        employee_inputs:    {input_code: [events]} — reserved for Source 3.

    Returns:
        Merged list ready to pass as component_metadata to run_sequential_payroll.
    """
    existing_codes = {m["component_code"] for m in platform_metadata}
    additions: list[dict] = []

    for rule in (payroll_rules or []):
        code = rule.get("rule_name")
        if not code or code in existing_codes:
            continue
        method = (rule.get("rule_definition_json") or {}).get("calculation_method", "")
        if method not in ("unit_multiplier", "fixed_amount", "ot_multiplier"):
            continue  # daily_rate_deduction modifies existing keys — never adds a new code
        additions.append({
            "component_code":     code,
            "component_class":    _infer_component_class(rule.get("rule_type")),
            "calculation_method": "salary_component",
            "execution_priority": RULE_COMPONENT_PRIORITY,
            "is_active":          True,
            "metadata_json":      {},
        })
        existing_codes.add(code)

    # Source 3: direct-pay period inputs — TODO when direct-pay inputs are introduced.

    return platform_metadata + additions


# ---------------------------------------------------------------------------
# Built-in handlers
# ---------------------------------------------------------------------------

def _handle_salary_component(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    return {code: Decimal(str(salary_components.get(code, "0")))}


def _handle_sum_earnings(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    component_map = ctx["_component_map"]
    total = sum(
        (v for k, v in results.items()
         if component_map.get(k, {}).get("component_class") == "earning"),
        Decimal("0"),
    )
    return {code: total}


def _handle_pension_rule(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """Pension contribution.

    Pensionable base is determined in priority order:
      1. client_meta components flagged legal_role.is_pensionable = True
      2. meta_json.statutory_base_components  (configurable fallback)
      3. Hard statutory default: BASIC + HOUSING + TRANSPORT (PRA 2014)

    Configuring a non-standard salary structure:
      Set component_metadata.metadata_json = {
          "statutory_base_components": ["BASIC_SALARY", "HOUSE_ALLOW", "TRANSPORT_ALLOW"]
      }
    """
    client_meta = ctx.get("client_meta") or {}
    statutory_base = meta_json.get(
        "statutory_base_components", ["BASIC", "HOUSING", "TRANSPORT"]
    )

    if client_meta:
        pensionable_codes = {
            c for c, m in client_meta.items()
            if m.get("legal_role", {}).get("is_pensionable", False)
        }
        if not pensionable_codes:
            pensionable_codes = set(statutory_base)
    else:
        pensionable_codes = set(statutory_base)

    pensionable_base = sum(
        (results.get(c, Decimal("0")) for c in pensionable_codes if c in results),
        Decimal("0"),
    )
    if "pension_employee_rate" not in ctx or "pension_employer_rate" not in ctx:
        raise ValueError(
            "Execution context is missing pension_employee_rate / pension_employer_rate. "
            "Ensure the statutory rule has pension rates configured."
        )
    pension_employee_rate = Decimal(str(ctx["pension_employee_rate"]))
    pension_employer_rate = Decimal(str(ctx["pension_employer_rate"]))
    emp, er = calculate_pension(pensionable_base, pension_employee_rate, pension_employer_rate)
    # PENSION_EMPLOYEE is the statutory deduction; PENSION_EMPLOYER is an employer cost.
    # Both are stored in results. The trace entry is keyed to PENSION_EMPLOYEE (code).
    return {"PENSION_EMPLOYEE": emp, "PENSION_EMPLOYER": er}


def _handle_rent_relief(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    employee_inputs = ctx.get("employee_inputs") or {}
    resolved        = _resolve_inputs(meta_json.get("input_requirements", {}), employee_inputs)
    annual_rent_paid = resolved.get("ANNUAL_RENT_PAID", Decimal("0"))
    rent_relief_cfg  = ctx.get("rent_relief_cfg") or {}
    rate = Decimal(str(rent_relief_cfg.get("rate", "0")))
    cap  = Decimal(str(rent_relief_cfg.get("cap",  "0")))
    period: PeriodContext = ctx["period"]
    return {code: calculate_rent_relief_for_period(annual_rent_paid, rate, cap, period.annualization_factor)}


def _handle_taxable_income(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """Taxable income = GROSS_PAY + PAYE_ONLY_ADDITIONS minus all pre-PAYE deductions.

    The set of deduction components is configurable via meta_json so that
    new pre-PAYE reliefs can be added through DB config alone:
      component_metadata.metadata_json = {
          "deduct_components": ["PENSION_EMPLOYEE", "RENT_RELIEF", "MY_NEW_RELIEF"]
      }
    Default: ["PENSION_EMPLOYEE", "RENT_RELIEF"]

    PAYE_ONLY_ADDITIONS is a statutory aggregate (M2) — hardcoded as a positive
    term because it is never operator-configurable (unlike deduct_components).
    """
    deduct_components = meta_json.get(
        "deduct_components", ["PENSION_EMPLOYEE", "RENT_RELIEF"]
    )
    paye_only_additions = results.get("PAYE_ONLY_ADDITIONS", Decimal("0"))
    value = (
        results.get("GROSS_PAY", Decimal("0"))
        + paye_only_additions
        - sum((results.get(d, Decimal("0")) for d in deduct_components), Decimal("0"))
    )
    return {code: value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}


def _handle_paye_rule(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    tax_bands = ctx.get("tax_bands", [])
    if not tax_bands:
        raise ValueError(
            "tax_bands is empty — cannot calculate PAYE. "
            "Ensure tax bands are seeded for the workspace's statutory rule."
        )
    period: PeriodContext = ctx["period"]
    return {code: calculate_paye_for_period(
        results.get("TAXABLE_INCOME", Decimal("0")),
        tax_bands,
        period.annualization_factor,
    )}


def _handle_nhf_rule(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """NHF contribution.

    Base component is configurable via meta_json so that clients using a
    non-standard code for basic salary still get correct NHF:
      component_metadata.metadata_json = {"base_component": "BASIC_SALARY"}
    Default: "BASIC"
    """
    base_component = meta_json.get("base_component", "BASIC")
    nhf_rate = Decimal(str(ctx.get("nhf_rate", "0.025")))
    return {code: calculate_nhf(results.get(base_component, Decimal("0")), nhf_rate)}


def _handle_health_insurance_flat(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    amount = Decimal(str(ctx.get("health_insurance_employee_amount", "0")))
    return {code: amount}


def _handle_development_levy_flat(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    amount = Decimal(str(ctx.get("development_levy_amount", "0")))
    return {code: amount}


def _store_trace_extra(ctx: dict, code: str, extras: dict) -> None:
    """Write supplemental trace fields for a component into ctx['_trace_extras'].

    The main execution loop reads these after each handler call and merges
    them into the standard trace entry for that component (e.g. 'source' for
    LIFE_INSURANCE, 'rate'/'base_*' for NSITF/ITF).
    """
    ctx.setdefault("_trace_extras", {})[code] = extras


def _handle_life_insurance_rule(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """Life insurance deduction — flat_amount (M4) or legacy rate × GROSS_PAY fallback.

    Workspace override path (Client B and future workspaces):
      client_component_metadata.overrides_json = {"flat_amount": 2000}
      → merged into client_meta[code] by the payroll route.

    Fallback path (all other workspaces):
      rate × GROSS_PAY — logs DEPRECATION warning until workspace migrates.
    """
    client_override = (ctx.get("client_meta") or {}).get(code, {})
    if "flat_amount" in client_override:
        amount = Decimal(str(client_override["flat_amount"]))
        _store_trace_extra(ctx, code, {"source": "flat_amount"})
        return {code: amount}
    rate = Decimal(str(ctx.get("life_insurance_employer_rate", "0")))
    logger.warning(
        "LIFE_INSURANCE component '%s' using deprecated rate×GROSS_PAY fallback; "
        "set flat_amount in client_component_metadata overrides_json to migrate",
        code,
    )
    _store_trace_extra(ctx, code, {"source": "rate_fallback"})
    return {code: (results.get("GROSS_PAY", Decimal("0")) * rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )}


def _handle_nsitf_employer(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """NSITF employer contribution — 1% of (BASIC + HOUSING + TRANSPORT).

    component_class = 'employer_cost' — excluded from NET_PAY by net_formula handler.
    Rate read from component_metadata.metadata_json, not hardcoded.
    Workspace opt-in via client_component_metadata.is_active.
    """
    rate = Decimal(str(meta_json.get("rate", "0.01")))
    base_basic     = results.get("BASIC",     Decimal("0"))
    base_housing   = results.get("HOUSING",   Decimal("0"))
    base_transport = results.get("TRANSPORT", Decimal("0"))
    base = base_basic + base_housing + base_transport
    amount = (rate * base).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    _store_trace_extra(ctx, code, {
        "rate":           str(rate),
        "base_BASIC":     str(base_basic),
        "base_HOUSING":   str(base_housing),
        "base_TRANSPORT": str(base_transport),
    })
    return {code: amount}


def _handle_itf_employer(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """ITF employer contribution — 1% of (BASIC + HOUSING + TRANSPORT).

    Platform-enforced threshold: workspace must have ≥5 active employees AND
    annual payroll YTD ≥ ₦50M. Threshold evaluated in the payroll route and
    passed in ctx['itf_threshold_met']. Returns ₦0 when threshold is not met.

    component_class = 'employer_cost' — excluded from NET_PAY by net_formula handler.
    Rate read from component_metadata.metadata_json, not hardcoded.
    """
    if not ctx.get("itf_threshold_met", False):
        _store_trace_extra(ctx, code, {
            "source":             "threshold_not_met",
            "itf_threshold_met":  False,
        })
        return {code: Decimal("0")}
    rate = Decimal(str(meta_json.get("rate", "0.01")))
    base_basic     = results.get("BASIC",     Decimal("0"))
    base_housing   = results.get("HOUSING",   Decimal("0"))
    base_transport = results.get("TRANSPORT", Decimal("0"))
    base = base_basic + base_housing + base_transport
    amount = (rate * base).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    _store_trace_extra(ctx, code, {
        "rate":           str(rate),
        "base_BASIC":     str(base_basic),
        "base_HOUSING":   str(base_housing),
        "base_TRANSPORT": str(base_transport),
    })
    return {code: amount}


def _handle_net_formula(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    component_map = ctx["_component_map"]
    # Earnings sweep includes 'non_taxable' class (M1): these allowances are paid
    # to the employee but excluded from GROSS_PAY so they never attracted PAYE.
    total_earnings = sum(
        (v for k, v in results.items()
         if component_map.get(k, {}).get("component_class") in ("earning", "non_taxable")),
        Decimal("0"),
    )
    total_deductions = sum(
        (v for k, v in results.items()
         if component_map.get(k, {}).get("component_class") == "statutory_deduction"),
        Decimal("0"),
    )
    return {code: (total_earnings - total_deductions).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )}


def _handle_pension_employer(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    # The employer pension contribution is computed as a side-effect of
    # pension_rule (which fires at a lower execution_priority) and stored in
    # results["PENSION_EMPLOYER"].  This handler simply confirms that value
    # so the component appears in the trace with a standard entry.
    return {code: results.get(code, Decimal("0"))}


def _handle_sum_paye_only_inputs(
    code: str, meta_json: dict,
    results: dict, salary_components: dict, ctx: dict,
) -> dict[str, Decimal]:
    """Aggregate all paye_only inputs into PAYE_ONLY_ADDITIONS (M2).

    Reads employee_inputs event dicts and sums any whose input_category
    (aliased as 'category' in the event dict by the repository) equals
    'PAYE_ONLY'.  These amounts increase TAXABLE_INCOME for PAYE purposes
    without entering GROSS_PAY or NET_PAY.

    Execution priority 95 — runs before TAXABLE_INCOME at priority 300.
    """
    employee_inputs = ctx.get("employee_inputs") or {}
    total = Decimal("0")
    for events in employee_inputs.values():
        if not isinstance(events, list):
            continue
        for event in events:
            if isinstance(event, dict) and event.get("category") == "PAYE_ONLY":
                qty = event.get("quantity") or event.get("amount") or 0
                amount = Decimal(str(qty))
                if amount > Decimal("0"):
                    total += amount
    return {code: total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}


# ---------------------------------------------------------------------------
# Register all built-in handlers
# ---------------------------------------------------------------------------

register_handler("salary_component",          _handle_salary_component)
register_handler("sum_earnings",              _handle_sum_earnings)
register_handler("pension_rule",              _handle_pension_rule)
register_handler("pension_employer",          _handle_pension_employer)
register_handler("rent_relief",               _handle_rent_relief)
register_handler("taxable_income",            _handle_taxable_income)
register_handler("paye_rule",                 _handle_paye_rule)
register_handler("nhf_rule",                  _handle_nhf_rule)
register_handler("health_insurance_flat",     _handle_health_insurance_flat)
register_handler("development_levy_flat",     _handle_development_levy_flat)
register_handler("life_insurance_rule",       _handle_life_insurance_rule)
register_handler("nsitf_employer",            _handle_nsitf_employer)
register_handler("itf_employer",              _handle_itf_employer)
register_handler("net_formula",               _handle_net_formula)
register_handler("sum_paye_only_inputs",      _handle_sum_paye_only_inputs)


# ---------------------------------------------------------------------------
# Public executor
# ---------------------------------------------------------------------------

def run_sequential_payroll(
    salary_components: dict,
    component_metadata: list,
    context: dict,
) -> dict:
    """Execute payroll components sequentially by execution_priority.

    Args:
        salary_components:
            Mapping of component_code → Decimal amount for this employee.
            Example: {"BASIC": Decimal("250000"), "HOUSING": Decimal("125000"), ...}

        component_metadata:
            List of component metadata dicts from the component_metadata table.
            Each dict must include: component_code, component_class,
            calculation_method, execution_priority, is_active.

        context:
            Runtime context required by statutory calculation methods.  Keys used
            by the built-in handlers are documented in each handler's docstring.
            Custom handlers registered via register_handler() may read additional
            keys from context.

    Returns:
        {
            "results": {component_code: Decimal},   # all computed values
            "trace":   [                             # one entry per executed component
                {
                    "component": str,
                    "method":    str,
                    "result":    str,   # Decimal serialised as string
                },
                ...
            ]
        }

    Raises:
        ValueError: If a component's calculation_method has no registered handler,
                    or if a handler raises (e.g. empty tax_bands for paye_rule).
    """
    # ------------------------------------------------------------------ #
    # 1. Filter to active components and sort by execution_priority.      #
    # ------------------------------------------------------------------ #
    active_meta = [m for m in component_metadata if m.get("is_active")]

    ordered = sorted(
        [m for m in active_meta if m.get("execution_priority") is not None],
        key=lambda m: m["execution_priority"],
    )

    component_map = {m["component_code"]: m for m in active_meta}

    # Apply workspace-level component_class overrides (M1 — D-M1-4).
    # client_component_metadata.overrides_json may carry a 'component_class' key
    # that overrides the platform-level class for a specific workspace component.
    # This allows a workspace to mark (e.g.) TRANSPORT as 'non_taxable' without
    # a platform schema change.
    client_meta = context.get("client_meta") or {}
    for comp_code, comp_meta in client_meta.items():
        override_class = comp_meta.get("component_class")
        if override_class and comp_code in component_map:
            component_map[comp_code] = {
                **component_map[comp_code],
                "component_class": override_class,
            }

    # ------------------------------------------------------------------ #
    # 2. Build execution context.                                         #
    #    Pre-resolve PeriodContext once; inject component_map for         #
    #    handlers that need it (sum_earnings, net_formula).               #
    # ------------------------------------------------------------------ #
    _period: PeriodContext = context.get("period") or build_period_context()
    ctx = {
        **context,
        "period":          _period,
        "_component_map":  component_map,   # private — for internal handlers only
    }

    # ------------------------------------------------------------------ #
    # 3. Execute components sequentially, accumulating results.           #
    # ------------------------------------------------------------------ #
    results: dict[str, Decimal] = {}

    # Seed the trace with a period context header so downstream consumers
    # (DB, API, debug output) can see exactly which period was used and
    # how the annualization factor was derived without re-reading context.
    execution_trace: list[dict] = [
        {
            "component":            "_period_context",
            "method":               "period_resolution",
            "period_start":         str(_period.period_start),
            "period_end":           str(_period.period_end),
            "period_type":          _period.period_type.value,
            "calendar_days":        _period.calendar_days,
            "working_days":         _period.working_days,
            "annualization_factor": str(_period.annualization_factor),
            "period_fraction":      str(_period.period_fraction),
            "expected_days":        ctx.get("expected_days"),
            "expected_hours":       ctx.get("expected_hours"),
            "ph_dates_used":        ctx.get("ph_dates_used"),
            "ph_source":            ctx.get("ph_source"),
            "salary_basis":           ctx.get("salary_basis", "salary_definition_absolute"),
            "shift_type":             ctx.get("shift_type"),
            "timesheet_source":       ctx.get("timesheet_source"),
            "hire_proration_applied": ctx.get("_hire_proration_applied", False),
            "result":                 None,
        }
    ]

    # Methods whose output depends on period-level factors (annualization,
    # working-day count).  Their trace entries are annotated with the
    # period values used so auditors can reproduce the exact calculation.
    _PERIOD_SENSITIVE_METHODS = {"paye_rule", "rent_relief", "taxable_income"}

    for meta in ordered:
        code      = meta["component_code"]
        method    = meta.get("calculation_method") or ""
        meta_json = meta.get("metadata_json") or {}

        # --- Generic eligibility gate ---
        eligibility_cfg = meta_json.get("eligibility", {})
        if eligibility_cfg:
            eligible = _check_eligibility(
                eligibility_cfg.get("conditions", []),
                eligibility_cfg.get("logic", "ALL"),
                ctx.get("employee_inputs") or {},
                results,
            )
            if not eligible and eligibility_cfg.get("on_ineligible") == "skip":
                continue

        # --- Dispatch to registered handler ---
        handler = _HANDLERS.get(method)
        if handler is None:
            raise ValueError(
                f"Unknown calculation_method {method!r} for component {code!r}. "
                f"Register a handler with register_handler({method!r}, fn) or "
                f"check component_metadata.calculation_method in the DB."
            )

        output = handler(code, meta_json, results, salary_components, ctx)
        results.update(output)

        trace_entry: dict = {
            "component":       code,
            "method":          method,
            "component_class": meta.get("component_class"),
            "result":          str(results.get(code)),
        }
        # Annotate period-sensitive entries so the trace is self-contained.
        if method in _PERIOD_SENSITIVE_METHODS:
            trace_entry["annualization_factor"] = str(_period.annualization_factor)
            trace_entry["period_fraction"]      = str(_period.period_fraction)
        # Merge any handler-supplied trace extras (e.g. 'source' for LIFE_INSURANCE,
        # 'rate'/'base_*' for NSITF/ITF employer handlers).
        _extras = ctx.get("_trace_extras", {}).get(code)
        if _extras:
            trace_entry.update(_extras)
        execution_trace.append(trace_entry)

    # Append ALL rule_evaluator trace entries (unit_multiplier, daily_rate_deduction,
    # fixed_amount, ot_multiplier, percentage_of_sum — applied + not_applied/eligibility
    # decisions). These include compliance-critical not_applied entries (C1) and
    # resolution_source/warning fields needed to audit historical-rate resolution, and
    # must be in component_trace_jsonb for union audit purposes.
    supplemental = ctx.get("_supplemental_traces") or []
    execution_trace.extend(supplemental)

    return {
        "results": results,
        "trace":   execution_trace,
    }
