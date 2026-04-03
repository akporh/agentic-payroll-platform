"""
Payroll Run Application Service.

Coordinates the full payroll run lifecycle: executes the pure domain
calculation pipeline and then persists the results, audit logs, and
events to the database via the infrastructure layer.

This is the main entry point for triggering a payroll run from an
API handler or CLI script.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from backend.domain.payroll.run_executor import execute_payroll_run_pure
from backend.application.payroll_run_persister import persist_payroll_run_execution
from backend.application.execution_tracer import ExecutionTracer


def execute_and_persist(
    payroll_run_id: str,
    workspace_id: str,
    employees: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
    execution_mode: str = "isolated",
    idempotency_key: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    pay_cycle_definition: dict | None = None,
    retry_strategy: str = "PER_EMPLOYEE",
    component_metadata: list | None = None,
    context: dict | None = None,
    rules_context_snapshot: dict | None = None,
    rule_set_id: str | None = None,
    statutory_effective_date: str | None = None,
    run_type: str = "REGULAR",
) -> dict:

    """Execute a full payroll run and persist all outputs.
    Supports execution isolation modes:
        - "atomic"
        - "isolated" (default)
    Orchestrates two steps:
    1. Run the pure domain calculation (no side effects).
    2. Persist results, audit logs, and events to the database.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        workspace_id: Workspace this run belongs to.
        employees: List of employee dicts with "employee_id" and "components".
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.
        idempotency_key: Optional caller key stored on the run for deduplication.
        period_start: Optional ISO-format start date of the pay period.
        period_end: Optional ISO-format end date of the pay period.

    Returns:
        Dict containing payroll_run_id, per-employee results, totals,
        audit_logs, and events (as produced by execute_payroll_run_pure).
    """

    tracer = ExecutionTracer(payroll_run_id)
    tracer.info(
        f"{len(employees)} employees  │  "
        f"{len(tax_bands)} tax bands  │  "
        f"{len(payroll_rule_ids)} workspace rules"
    )
    tracer.info(
        f"Statutory rule v{statutory_version}  │  "
        f"execution_mode={execution_mode}  │  "
        f"workspace={workspace_id}"
    )

    # --- Period context: show input → normalization result ---
    if context and (p := context.get("period")):
        tracer.info(
            f"Period: [bold]{p.period_start}[/bold] → [bold]{p.period_end}[/bold]  "
            f"[dim]({p.period_type.value})[/dim]  │  "
            f"[cyan]{p.calendar_days}[/cyan] cal days  │  "
            f"[cyan]{p.working_days}[/cyan] working days"
        )
        tracer.info(
            f"Annualization: ×{p.annualization_factor}  │  "
            f"Period fraction: {p.period_fraction}"
        )

    tracer.separator()

    with tracer.step("Execute payroll engine"):
        output = execute_payroll_run_pure(
            payroll_run_id=payroll_run_id,
            workspace_id=workspace_id,
            employees=employees,
            tax_bands=tax_bands,
            statutory_rule_id=statutory_rule_id,
            statutory_version=statutory_version,
            payroll_rule_ids=payroll_rule_ids,
            performed_by=performed_by,
            execution_mode=execution_mode,
            pay_cycle_definition=pay_cycle_definition,
            component_metadata=component_metadata,
            context=context,
            rules_context_snapshot=rules_context_snapshot,
            tracer=tracer,
        )

    tracer.separator()

    with tracer.step("Persist results"):
        persist_payroll_run_execution(
            workspace_id,
            output,
            idempotency_key=idempotency_key,
            period_start=period_start,
            period_end=period_end,
            retry_strategy=retry_strategy,
            rule_set_id=rule_set_id,
            statutory_effective_date=statutory_effective_date,
            run_type=run_type,
            tracer=tracer,
        )

    tracer.separator()

    return output