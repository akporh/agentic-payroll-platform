from backend.infra.repositories.payroll_result_repo import save_payroll_result
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event


def persist_payroll_run_execution(workspace_id: str, execution_output: dict):

    payroll_run_id = execution_output["payroll_run_id"]

    for r in execution_output["results"]:
        save_payroll_result(payroll_run_id, r["employee_id"], r["payroll_result"])

    for audit in execution_output["audit_logs"]:
        save_audit_log(workspace_id, audit)

    for event in execution_output["events"]:
        save_event(event)

