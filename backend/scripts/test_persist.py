
import uuid
from backend.infra.repositories.payroll_result_repo import save_payroll_result
from backend.infra.repositories.audit_log_repo import save_audit_log
from backend.infra.repositories.event_store_repo import save_event

dummy = {
    "gross_components_jsonb": [{"code": "BASIC", "amount": 800000}],
    "deductions_jsonb": {"PAYE": 84000},
    "net_pay": 716000,
    "calculations_snapshot_json": {
        "gross": 800000,
        "paye": 84000,
        "net": 716000
    },
}

payroll_run_id =  "bec9157b-a6db-49d8-a88c-99ab0b448aa7"
employee_id = "92d4ee52-385a-4617-ab18-62f2e4c603ed"

save_payroll_result(payroll_run_id, employee_id, dummy)

# ---- Audit Log ----
audit = {
    "entity_type": "PAYROLL_RESULT",
    "entity_id": employee_id,
    "action": "CREATE_RESULT",
    "old_value_jsonb": None,
    "new_value_jsonb": dummy,
    "performed_by": "admin@test.com",
}

# Use the workspace_id you created earlier in DB
workspace_id = "6b70612c-b2e1-4275-800c-33140e7f4ebd"

save_audit_log(workspace_id, audit)

# ---- Event Store ----
event = {
    "aggregate_type": "PAYROLL_RUN",
    "aggregate_id": payroll_run_id,
    "event_type": "PAYROLL_RESULT_CREATED",
    "event_payload": {
        "employee_id": employee_id,
        "net_pay": dummy["net_pay"],
    },
}

save_event(event)

print("Inserted payroll_result + audit_log + event_store rows.")


print("Inserted payroll_result row.")

