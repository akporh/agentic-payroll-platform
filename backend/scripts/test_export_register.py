from backend.application.exports.payroll_register_export import (
    export_payroll_register_csv,
)

dummy_results = [
    {
        "employee_id": "emp1",
        "payroll_result": {
            "gross_components_jsonb": [
                {"code": "BASIC", "amount": 800000},
            ],
            "deductions_jsonb": {"PAYE": 84000},
            "net_pay": 716000,
        },
    },
    {
        "employee_id": "emp2",
        "payroll_result": {
            "gross_components_jsonb": [
                {"code": "BASIC", "amount": 800000},
            ],
            "deductions_jsonb": {"PAYE": 84000},
            "net_pay": 716000,
        },
    },
]

export_payroll_register_csv(dummy_results, "payroll_register.csv")

print("Exported payroll_register.csv")

