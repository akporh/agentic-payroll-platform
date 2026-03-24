"""
Single Employee Payroll Executor.

Orchestrates a complete deterministic payroll calculation for one employee.
When component_metadata is supplied the sequential executor is used; otherwise
the legacy hard-coded pipeline (calculate_gross → calculate_net_pay) is used
as a fallback so that the retry service and any existing callers continue to
work without modification.

No database writes — pure computation only.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from backend.domain.payroll.period_context import (
    PeriodContext,
    build_period_context,
    compute_hire_termination_factor,
)
from backend.domain.payroll.result_builder import build_payroll_result
from backend.domain.payroll.rule_evaluator import apply_payroll_rules
from backend.domain.payroll.sequential_executor import run_sequential_payroll
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
        component_metadata: Optional list of component metadata dicts.  When
            supplied, the sequential executor is used.
        context: Optional runtime context (pension rates, tax_bands).  Must be
            provided together with component_metadata.
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
        )
    else:
        payroll_result = build_payroll_result(components, tax_bands, tracer=tracer)
        payroll_result["component_trace_jsonb"] = None

    rules_snapshot = build_rules_context_snapshot(
        statutory_rule_id, statutory_version, payroll_rule_ids
    )

    return {
        "payroll_run_id":        payroll_run_id,
        "employee_id":           employee_id,
        "rules_context_snapshot": rules_snapshot,
        "payroll_result":        payroll_result,
        "inputs_applied":        inputs,
    }


def _run_sequential(
    components: list[dict],
    component_metadata: list,
    context: dict | None,
    tax_bands: list[dict],
    inputs: dict | None = None,
    contract_start: str | None = None,
    contract_end:   str | None = None,
) -> dict:
    """Run the sequential executor and reshape output into the payroll_result shape."""
    # Convert components list-of-dicts to code→Decimal dict
    salary_components = {
        c["code"]: Decimal(str(c["amount"]))
        for c in components
    }

    # Merge tax_bands and per-employee inputs into context
    full_context = dict(context or {})
    full_context.setdefault("tax_bands", tax_bands)
    full_context["employee_inputs"] = inputs or {}

    # Extract period context; fall back to v1-compatible MONTHLY defaults when absent
    _period: PeriodContext = full_context.get("period") or build_period_context()
    client_meta = full_context.get("client_meta") or {}
    payroll_rules = full_context.get("payroll_rules") or []

    # --- Mid-period hire / termination proration ---
    # Parse contract dates and compute what fraction of the period the
    # employee was actually active.  Factor = 1 for full-period employees.
    _contract_start = date.fromisoformat(contract_start) if contract_start else None
    _contract_end   = date.fromisoformat(contract_end)   if contract_end   else None

    proration_factor = compute_hire_termination_factor(_period, _contract_start, _contract_end)

    if proration_factor < Decimal("1"):
        salary_components = {
            code: (amount * proration_factor).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            for code, amount in salary_components.items()
        }

    # Apply workspace payroll rules (absences, overtime, etc.) before the
    # sequential component chain runs.  No-ops when payroll_rules is empty.
    if payroll_rules:
        salary_components, _rule_trace = apply_payroll_rules(
            salary_components=salary_components,
            payroll_rules=payroll_rules,
            employee_inputs=inputs or {},
            client_meta=client_meta,
            working_days=_period.working_days,
            calendar_days=_period.calendar_days,
        )

    sequential = run_sequential_payroll(salary_components, component_metadata, full_context)

    results = sequential["results"]
    trace   = sequential["trace"]

    # Build a lookup for component_class
    class_map = {m["component_code"]: m.get("component_class") for m in component_metadata}

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
