from backend.application.exports.paye_export import export_paye_summary_csv

dummy_results = [
    {
        "employee_id": "emp1",
        "payroll_result": {
            "deductions_jsonb": {"PAYE": 84000},
            "net_pay": 716000,
        },
    },
    {
        "employee_id": "emp2",
        "payroll_result": {
            "deductions_jsonb": {"PAYE": 84000},
            "net_pay": 716000,
        },
    },
]

export_paye_summary_csv(dummy_results, "paye_summary.csv")

print("Exported paye_summary.csv")

