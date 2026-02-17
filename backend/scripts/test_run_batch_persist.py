import uuid

from backend.application.payroll_run_service import execute_and_persist_payroll_run

payroll_run_id = str(uuid.uuid4())
workspace_id = "PASTE_WORKSPACE_UUID_HERE"

employees = [
    {
        "employee_id": str(uuid.uuid4()),
        "components": [
            {"code": "BASIC", "amount": 500000},
            {"code": "HOUSING", "amount": 300000},
        ],
    },
    {
        "employee_id": str(uuid.uuid4()),
        "components": [
            {"code": "BASIC", "amount": 500000},
            {"code": "HOUSING", "amount": 300000},
        ],
    },
]

tax_bands = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]

output = execute_and_persist_payroll_run(
    payroll_run_id=payroll_run_id,
    workspace_id=workspace_id,
    employees=employees,
    tax_bands=tax_bands,
    statutory_rule_id="rule2026",
    statutory_version=1,
    payroll_rule_ids=["r1"],
    performed_by="admin@test.com",
)

print("Batch payroll persisted successfully!")
print(output["totals"])

