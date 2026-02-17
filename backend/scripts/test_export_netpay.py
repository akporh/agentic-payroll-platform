from backend.application.exports.net_pay_export import export_net_pay_csv

dummy_results = [
    {"employee_id": "emp1", "payroll_result": {"net_pay": 716000}},
    {"employee_id": "emp2", "payroll_result": {"net_pay": 716000}},
]

export_net_pay_csv(dummy_results, "netpay.csv")

print("Exported netpay.csv")

