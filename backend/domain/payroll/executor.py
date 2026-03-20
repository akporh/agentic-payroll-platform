"""
Single Employee Payroll Executor.

Orchestrates a complete deterministic payroll calculation for one employee.
When component_metadata is supplied the sequential executor is used; otherwise
the legacy hard-coded pipeline (calculate_gross → calculate_net_pay) is used
as a fallback so that the retry service and any existing callers continue to
work without modification.

No database writes — pure computation only.
"""

from decimal import Decimal

from backend.domain.payroll.result_builder import build_payroll_result
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
        payroll_result = _run_sequential(components, component_metadata, context, tax_bands, inputs)
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
