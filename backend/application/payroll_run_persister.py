"""
Payroll Run Persister.

Persists the complete output of a payroll run execution to the database.
Saves per-employee payroll results, audit log entries for state transitions,
and event store records — each via its dedicated repository.

This module bridges the pure domain output and the infrastructure layer.
It contains no business logic; it only routes data to the correct repository.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from decimal import Decimal

from backend.infra.repositories.payroll_run_repo import save_payroll_run
from backend.infra.repositories.payroll_result_repo import save_payroll_result
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event
from backend.application.execution_tracer import NULL_TRACER


def persist_payroll_run_execution(
    workspace_id: str,
    execution_output: dict,
    idempotency_key: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    retry_strategy: str = "PER_EMPLOYEE",
    rule_set_id: str | None = None,
    statutory_effective_date: str | None = None,
    run_type: str = "REGULAR",
    tracer=None,
):
    """Persist all outputs from a payroll run execution.

    Iterates through the execution output and saves:
    1. The payroll_run header row (with financial totals).
    2. Each employee's payroll result to the payroll_result table.
    3. Each audit log entry to the audit_log table.
    4. Each event to the event_store table.

    Args:
        workspace_id: Workspace this run belongs to (required for audit logs).
        execution_output: Dict produced by execute_payroll_run_pure, containing:
            - payroll_run_id (str): The run identifier.
            - results (list[dict]): Per-employee results with employee_id
              and payroll_result keys.
            - totals (dict): Aggregated totals from the batch processor,
              including total_gross_pay, total_deduction, total_net_pay.
            - audit_logs (list[dict]): Audit payloads for state transitions.
            - events (list[dict]): Event payloads for state transitions.
        idempotency_key: Optional caller-supplied idempotency key to store on
            the payroll_run row (enforced unique per workspace by DB index).
        period_start: Optional ISO-format start date of the pay period.
        period_end: Optional ISO-format end date of the pay period.
    """
    tracer = tracer or NULL_TRACER

    payroll_run_id = execution_output["payroll_run_id"]
    totals = execution_output["totals"]
    results = execution_output["results"]
    audit_logs = execution_output["audit_logs"]
    events = execution_output["events"]

    # 1️⃣ Insert payroll_run first (with financial totals for reconciliation)
    final_status = events[-1]["event_payload"]["to"]

    with tracer.step("Save payroll run header"):
        tracer.info(
            f"Status: [bold]{final_status}[/bold]  │  "
            f"Gross: {totals['total_gross_pay']}  │  "
            f"PAYE: {totals['total_deduction']}  │  "
            f"Net: {totals['total_net_pay']}"
        )
        save_payroll_run(
            payroll_run_id=payroll_run_id,
            workspace_id=workspace_id,
            status=final_status,
            rules_context_snapshot=execution_output["rules_context_snapshot"],
            idempotency_key=idempotency_key,
            period_start=period_start,
            period_end=period_end,
            total_gross_pay=Decimal(str(totals["total_gross_pay"])),
            total_tax=Decimal(str(totals["total_deduction"])),
            total_net_pay=Decimal(str(totals["total_net_pay"])),
            retry_strategy=retry_strategy,
            rule_set_id=rule_set_id,
            statutory_effective_date=statutory_effective_date,
            run_type=run_type,
        )

    # 2️⃣ Insert payroll_results
    with tracer.step(f"Save {len(results)} employee results"):
        for r in results:
            tracer.info(
                f"Employee {r['employee_id'][:8]}  →  "
                f"[bold {'green' if r['status'] == 'SUCCESS' else 'red'}]{r['status']}[/bold {'green' if r['status'] == 'SUCCESS' else 'red'}]"
            )
            output = r.get("output")
            component_trace = (
                output["payroll_result"].get("component_trace_jsonb")
                if output and output.get("payroll_result")
                else None
            )
            save_payroll_result(
                payroll_run_id=payroll_run_id,
                employee_id=r["employee_id"],
                status=r["status"],
                payroll_output=output,
                error_message=r.get("error"),
                component_trace=component_trace,
            )

    # 3️⃣ Insert audit logs
    with tracer.step(f"Save {len(audit_logs)} audit entries"):
        for audit in audit_logs:
            save_audit_log(workspace_id, audit)
        tracer.info(f"{len(audit_logs)} audit log entries written")

    # 4️⃣ Insert events
    with tracer.step(f"Save {len(events)} events"):
        for event in events:
            save_event(event)
        tracer.info(f"{len(events)} events written to event store")