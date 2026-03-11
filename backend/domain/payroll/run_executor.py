"""
Pure PayrollRun Executor.

Orchestrates a complete payroll run end-to-end: transitions the run through
DRAFT → CALCULATING → CALCULATED, executes batch payroll processing, and
produces all audit/event payloads — without any database access.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from backend.domain.payroll.batch_processor import process_payroll_run
from backend.domain.payroll.state_machine import transition
from backend.domain.payroll.status import PayrollRunStatus
from backend.domain.payroll.audit_events import (
    build_transition_audit,
    build_transition_event,
)
from backend.domain.rules.snapshot import build_rules_context_snapshot
from backend.application.execution_tracer import NULL_TRACER


def execute_payroll_run_pure(
    payroll_run_id: str,
    workspace_id: str,
    employees: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
    execution_mode: str = "isolated",
    pay_cycle_definition: dict | None = None,
    tracer=None,
) -> dict:
    """Execute a full payroll run end-to-end as a pure function.

    Performs state transitions and batch payroll processing, producing
    all calculation results plus audit and event payloads.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        workspace_id: Workspace this run belongs to.
        employees: List of employee dicts with "employee_id" and "components".
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.

    Returns:
        Dict containing:
            - payroll_run_id: The run identifier.
            - results: List of per-employee execution outputs.
            - totals: Aggregated totals including total_net_pay.
            - audit_logs: Audit payloads for each state transition.
            - events: Event payloads for each state transition.
    """
    tracer = tracer or NULL_TRACER
    audit_logs = []
    events = []

    with tracer.step("Transition: DRAFT → CALCULATING"):
        transition(PayrollRunStatus.DRAFT, PayrollRunStatus.CALCULATING)
        audit_logs.append(
            build_transition_audit(
                payroll_run_id=payroll_run_id,
                old_status=PayrollRunStatus.DRAFT,
                new_status=PayrollRunStatus.CALCULATING,
                performed_by=performed_by,
            )
        )
        events.append(
            build_transition_event(
                payroll_run_id=payroll_run_id,
                old_status=PayrollRunStatus.DRAFT,
                new_status=PayrollRunStatus.CALCULATING,
            )
        )

    with tracer.step(f"Batch process: {len(employees)} employees (mode={execution_mode})"):
        batch_result = process_payroll_run(
            payroll_run_id=payroll_run_id,
            employees=employees,
            tax_bands=tax_bands,
            statutory_rule_id=statutory_rule_id,
            statutory_version=statutory_version,
            payroll_rule_ids=payroll_rule_ids,
            performed_by=performed_by,
            execution_mode=execution_mode,
            tracer=tracer,
        )
        totals = batch_result["totals"]
        tracer.info(
            f"Results: [bold green]{totals['success_count']} success[/bold green]  │  "
            f"[bold red]{totals['failure_count']} failed[/bold red]"
        )
        tracer.info(
            f"Gross: {totals['total_gross_pay']}  │  "
            f"PAYE: {totals['total_deduction']}  │  "
            f"Net: {totals['total_net_pay']}"
        )

    if totals["failure_count"] > 0:
        new_status = PayrollRunStatus.PARTIAL
    else:
        new_status = PayrollRunStatus.CALCULATED

    with tracer.step(f"Transition: CALCULATING → {new_status.value}"):
        transition(PayrollRunStatus.CALCULATING, new_status)
        audit_logs.append(
            build_transition_audit(
                payroll_run_id=payroll_run_id,
                old_status=PayrollRunStatus.CALCULATING,
                new_status=new_status,
                performed_by=performed_by,
            )
        )
        events.append(
            build_transition_event(
                payroll_run_id=payroll_run_id,
                old_status=PayrollRunStatus.CALCULATING,
                new_status=new_status,
            )
        )

    return {
        "payroll_run_id": payroll_run_id,
        "results": batch_result["results"],
        "totals": batch_result["totals"],
        "audit_logs": audit_logs,
        "events": events,
        "rules_context_snapshot": build_rules_context_snapshot(
            statutory_rule_id, statutory_version, payroll_rule_ids
        ),
        "pay_cycle_definition": pay_cycle_definition,
    }
