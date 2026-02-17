from backend.domain.payroll.run_executor import execute_payroll_run_pure
from backend.application.payroll_run_persister import persist_payroll_run_execution


def execute_and_persist(...):
    output = execute_payroll_run_pure(...)
    persist_payroll_run_execution(workspace_id, output)
    return output

