"""
Single Employee Payroll Executor.

Orchestrates a complete deterministic payroll calculation for one employee.
When component_metadata is supplied the sequential executor is used; otherwise
the legacy hard-coded pipeline (calculate_gross → calculate_net_pay) is used
as a fallback so that the retry service and any existing callers continue to
work without modification.

No database writes — pure computation only.

Input format
------------
Payroll inputs arrive from the repository as event lists:
    {input_code: [{quantity, category, reference_date}, ...]}

The rule evaluator accepts this directly.  Each event carries its own
reference_date so the engine can apply the historically correct rate per event.
No flattening step is required.

Temporal params
---------------
Cross-period inputs require historically correct rates.  The route (payroll.py)
populates the following keys in context before calling the executor:
    historical_rule_sets        — [{id, effective_from, items}] from snapshot
    historical_period_contexts  — {(year, month): {working_days, calendar_days}}
    current_rule_set_id         — UUID of the current rule set
    current_rule_set_effective_from — effective_from of the current rule set
"""

import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

from backend.domain.payroll.period_context import (
    PeriodContext,
    build_period_context,
    compute_hire_termination_factor,
)
from backend.domain.payroll.result_builder import build_payroll_result
from backend.domain.payroll.rule_evaluator import apply_payroll_rules
from backend.domain.payroll.sequential_executor import (
    build_runtime_component_registry,
    run_sequential_payroll,
)
from backend.domain.rules.snapshot import build_rules_context_snapshot
from backend.application.trace_decorators import trace_step


@trace_step("Calculate employee payroll")
def execute_single_employee_payroll(
    payroll_run_id: str,
    employee_id: str,
    components: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
    *,
    inputs=None,
    component_metadata: list | None = None,
    context: dict | None = None,
    contract_start: str | None = None,
    contract_end:   str | None = None,
    rules_context_snapshot: dict | None = None,
    employee_context: dict | None = None,
    tracer=None,
) -> dict:
    """Execute a full payroll calculation for a single employee.

    When component_metadata is provided the sequential executor drives the
    pipeline.  When it is absent the legacy calculate_gross → calculate_paye
    path is used so that callers that do not yet supply metadata (e.g. the
    retry service) are unaffected.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        employee_id: Unique identifier of the employee.
        components: Salary component dicts with "code" and "amount" keys.
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.
        inputs: Raw employee inputs from the repository.
            Nested format: {input_code: {quantity, rate, amount, category, reference_date}}
            Also accepts legacy flat format: {input_code: scalar}.
        component_metadata: Optional list of component metadata dicts.  When
            supplied, the sequential executor is used.
        context: Optional runtime context (pension rates, tax_bands, payroll_rules,
            historical_rule_sets, historical_period_contexts, etc.).  Must be
            provided together with component_metadata.
        contract_start: ISO date string for contract start (proration).
        contract_end: ISO date string for contract end (proration).
        rules_context_snapshot: Pre-built v2 snapshot dict.  When provided it is
            used directly, bypassing the internal v1 snapshot builder.  The route
            should always supply this once temporal rule resolution is active.
        tracer: Optional ExecutionTracer for structured trace output.

    Returns:
        Dict containing payroll_run_id, employee_id, rules_context_snapshot,
        and payroll_result (gross_components_jsonb, deductions_jsonb, net_pay,
        calculations_snapshot_json, component_trace_jsonb).
    """
    inputs = inputs or {}

    if component_metadata:
        payroll_result = _run_sequential(
            components, component_metadata, context, tax_bands, inputs,
            contract_start=contract_start,
            contract_end=contract_end,
            employee_context=employee_context,
            tracer=tracer,
        )
    else:
        # DEPRECATED: legacy hard-coded pipeline — no component_trace_jsonb produced.
        # This path fires only when component_metadata is None (e.g. old CLI callers).
        logger.warning(
            "Legacy executor fallback invoked for employee %s in run %s — "
            "component_trace_jsonb will be None. "
            "Migrate callers to pass component_metadata to enable the sequential executor.",
            employee_id,
            payroll_run_id,
        )
        if tracer is not None:
            tracer.warn_persist(
                "legacy_executor_fallback",
                f"employee_id={employee_id}",
            )
        payroll_result = build_payroll_result(components, tax_bands, tracer=tracer)
        payroll_result["component_trace_jsonb"] = None

    # Use pre-built snapshot when provided (v2, snapshot-driven retry);
    # fall back to v1 ID-only snapshot for legacy callers.
    if rules_context_snapshot is None:
        rules_context_snapshot = build_rules_context_snapshot(
            statutory_rule_id, statutory_version, payroll_rule_ids
        )

    return {
        "payroll_run_id":         payroll_run_id,
        "employee_id":            employee_id,
        "rules_context_snapshot": rules_context_snapshot,
        "payroll_result":         payroll_result,
        "inputs_applied":         inputs,
    }


def _run_sequential(
    components: list[dict],
    component_metadata: list,
    context: dict | None,
    tax_bands: list[dict],
    inputs: dict | None = None,
    contract_start: str | None = None,
    contract_end:   str | None = None,
    employee_context: dict | None = None,
    tracer=None,
) -> dict:
    """Run the sequential executor and reshape output into the payroll_result shape."""
    from backend.application.execution_tracer import NULL_TRACER
    _tracer = tracer or NULL_TRACER

    # Convert components list-of-dicts to code→Decimal dict
    salary_components = {
        c["code"]: Decimal(str(c["amount"]))
        for c in components
    }

    # Merge tax_bands and per-employee inputs into context
    full_context = dict(context or {})
    full_context.setdefault("tax_bands", tax_bands)

    # Pass inputs (event lists) directly — no flattening step needed.
    # Each event carries its own reference_date for per-event rate resolution.
    full_context["employee_inputs"] = inputs or {}

    # Extract period context; fall back to v1-compatible MONTHLY defaults when absent.
    # Log the resolved period so the trace shows input → normalization result.
    _period_from_ctx = full_context.get("period")
    if _period_from_ctx:
        _period: PeriodContext = _period_from_ctx
        _tracer.info(
            f"  [dim]period[/dim]  {_period.period_start} → {_period.period_end}  "
            f"({_period.period_type.value})  "
            f"cal={_period.calendar_days}d  wd={_period.working_days}d  "
            f"ann=×{_period.annualization_factor}"
        )
    else:
        _period = build_period_context()
        _tracer.info(
            f"  [dim]period[/dim]  [yellow]no period in context — defaulted to MONTHLY "
            f"{_period.period_start} → {_period.period_end}[/yellow]"
        )
    full_context["period"] = _period

    client_meta = full_context.get("client_meta") or {}
    payroll_rules = full_context.get("payroll_rules") or []

    # Temporal context — populated by payroll.py route once rule sets are wired up
    historical_rule_sets = full_context.get("historical_rule_sets") or []
    historical_period_contexts = full_context.get("historical_period_contexts") or {}
    current_rule_set_id = full_context.get("current_rule_set_id")
    current_rule_set_effective_from = full_context.get("current_rule_set_effective_from")

    # PH & OT context — populated by payroll.py route (C4 — PH-8)
    expected_hours = full_context.get("expected_hours")
    expected_days  = full_context.get("expected_days")
    rate_code_map  = full_context.get("rate_code_map") or {}
    shift_type     = full_context.get("shift_type")

    # --- Mid-period hire / termination proration ---
    _contract_start = date.fromisoformat(contract_start) if contract_start else None
    _contract_end   = date.fromisoformat(contract_end)   if contract_end   else None

    proration_factor = compute_hire_termination_factor(_period, _contract_start, _contract_end)

    if proration_factor < Decimal("1"):
        _tracer.info(
            f"  [dim]proration[/dim]  contract {contract_start} → {contract_end}  "
            f"factor=[bold yellow]{proration_factor}[/bold yellow]  "
            f"(active {_period.working_days - int(_period.working_days * (1 - proration_factor))}/"
            f"{_period.working_days} working days)"
        )
        salary_components = {
            code: (amount * proration_factor).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            for code, amount in salary_components.items()
        }

    # Apply workspace payroll rules (absences, overtime, etc.) before the
    # sequential component chain runs.  No-ops when payroll_rules is empty.
    if payroll_rules:
        _tracer.info(f"  [dim]rules[/dim]  applying {len(payroll_rules)} workspace payroll rules")
        salary_components, _rule_trace = apply_payroll_rules(
            salary_components=salary_components,
            payroll_rules=payroll_rules,
            employee_inputs=inputs or {},
            client_meta=client_meta,
            working_days=_period.working_days,
            calendar_days=_period.calendar_days,
            historical_rule_sets=historical_rule_sets,
            historical_period_contexts=historical_period_contexts,
            period_start=_period.period_start if hasattr(_period, "period_start") else None,
            period_end=_period.period_end if hasattr(_period, "period_end") else None,
            current_rule_set_id=current_rule_set_id,
            current_rule_set_effective_from=current_rule_set_effective_from,
            expected_hours=expected_hours,
            expected_days=expected_days,
            rate_code_map=rate_code_map,
            shift_type=shift_type,
            employee_context=employee_context,
        )
        # Merge percentage_of_sum traces (including not_applied eligibility decisions)
        # into component_trace_jsonb via the sequential executor's supplemental trace
        # mechanism. Other _rule_trace entries remain discarded (tracked as N1).
        _pct_sum_traces = [t for t in _rule_trace if t.get("method") == "percentage_of_sum"]
        if _pct_sum_traces:
            full_context["_supplemental_traces"] = _pct_sum_traces

    # Build unified component registry: platform metadata + rule-injected components.
    # Rule-injected components (unit_multiplier / fixed_amount) get execution_priority=50
    # so they enter results{} before _handle_sum_earnings aggregates them at priority 100.
    unified_meta = build_runtime_component_registry(
        platform_metadata=component_metadata,
        payroll_rules=payroll_rules,
        employee_inputs=inputs or {},
    )

    sequential = run_sequential_payroll(salary_components, unified_meta, full_context)

    results = sequential["results"]
    trace   = sequential["trace"]

    # Build a lookup for component_class — uses unified_meta so rule-injected
    # components (REGULAR_OVERTIME, WEEKEND_ALLOWANCE, etc.) appear in gross_components_jsonb.
    class_map = {m["component_code"]: m.get("component_class") for m in unified_meta}

    # gross_components_jsonb: all earning-class components
    gross_components = {
        code: {"amount": value}
        for code, value in results.items()
        if class_map.get(code) == "earning"
    }

    # deductions_jsonb: all statutory_deduction components (class-driven)
    deductions = {
        code: value
        for code, value in results.items()
        if class_map.get(code) == "statutory_deduction"
    }

    gross  = results.get("GROSS_PAY", Decimal("0"))
    paye   = results.get("PAYE", Decimal("0"))
    net    = results.get("NET_PAY", Decimal("0"))

    return {
        "gross_components_jsonb":    gross_components,
        "deductions_jsonb":          deductions,
        "net_pay":                   net,
        "calculations_snapshot_json": {
            "gross": gross,
            "paye":  paye,
            "net":   net,
        },
        "component_trace_jsonb": trace,
    }


