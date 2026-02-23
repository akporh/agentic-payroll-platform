from backend.domain.payroll.run_executor import execute_payroll_run_pure
from backend.application.payroll_run_persister import persist_payroll_run_execution


def execute_and_persist(
    payroll_run_id: str,
    workspace_id: str,
    employees: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
    execution_mode: str = "isolated",
) -> dict:
    """
    Execute a full payroll run and persist all outputs.

    Supports execution isolation modes:
        - "atomic"
        - "isolated" (default)

    Domain remains pure.
    Persistence handled via repositories.
    """

    output = execute_payroll_run_pure(
        payroll_run_id=payroll_run_id,
        workspace_id=workspace_id,
        employees=employees,
        tax_bands=tax_bands,
        statutory_rule_id=statutory_rule_id,
        statutory_version=statutory_version,
        payroll_rule_ids=payroll_rule_ids,
        performed_by=performed_by,
        execution_mode=execution_mode,
    )

    persist_payroll_run_execution(workspace_id, output)

    return output