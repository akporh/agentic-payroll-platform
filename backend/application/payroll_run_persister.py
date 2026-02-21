"""
Payroll Run Persister.

Persists the complete output of a payroll run execution to the database.
Saves per-employee payroll results, audit log entries for state transitions,
and event store records — each via its dedicated repository.

This module bridges the pure domain output and the infrastructure layer.
It contains no business logic; it only routes data to the correct repository.

Reference: Phase 1 Business Spec — Payroll Processing Pipeline.
"""

from backend.infra.repositories.payroll_run_repo import save_payroll_run
from backend.infra.repositories.payroll_result_repo import save_payroll_result
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event


def persist_payroll_run_execution(workspace_id: str, execution_output: dict):
    """Persist all outputs from a payroll run execution.

    Iterates through the execution output and saves:
    1. Each employee's payroll result to the payroll_result table.
    2. Each audit log entry to the audit_log table.
    3. Each event to the event_store table.

    Args:
        workspace_id: Workspace this run belongs to (required for audit logs).
        execution_output: Dict produced by execute_payroll_run_pure, containing:
            - payroll_run_id (str): The run identifier.
            - results (list[dict]): Per-employee results with employee_id
              and payroll_result keys.
            - audit_logs (list[dict]): Audit payloads for state transitions.
            - events (list[dict]): Event payloads for state transitions.
    """
    payroll_run_id = execution_output["payroll_run_id"]

    print("DEBUG LAST EVENT:", execution_output["events"][-1])

    # 1️⃣ Insert payroll_run first
    final_status = execution_output["events"][-1]["event_payload"]["to"]

    save_payroll_run(
        payroll_run_id=payroll_run_id,
        workspace_id=workspace_id,
        status=final_status,
    )

    # 2️⃣ Insert payroll_results
    for r in execution_output["results"]:
        save_payroll_result(
            payroll_run_id=payroll_run_id,
            employee_id=r["employee_id"],
            status=r["status"],
            payroll_output=r.get("output"),
            error_message=r.get("error"),
        )

    # 3️⃣ Insert audit logs
    for audit in execution_output["audit_logs"]:
        save_audit_log(workspace_id, audit)

    # 4️⃣ Insert events
    for event in execution_output["events"]:
        save_event(event)