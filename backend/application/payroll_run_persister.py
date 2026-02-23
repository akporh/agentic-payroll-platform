from backend.infra.repositories.payroll_run_repo import save_payroll_run
from backend.infra.repositories.payroll_result_repo import save_payroll_result
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event


def persist_payroll_run_execution(workspace_id: str, execution_output: dict):

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