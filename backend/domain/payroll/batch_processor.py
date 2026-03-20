"""
Batch Payroll Run Processor (Enhanced).

Processes payroll for multiple employees within a single PAYROLL_RUN
by delegating to the single-employee executor and aggregating results.

Supports logical isolation modes:
- ATOMIC: stop on first failure
- ISOLATED: continue processing and capture failures

Pure computation only. No database writes.
"""
from decimal import Decimal
from typing import Literal
from backend.domain.payroll.executor import execute_single_employee_payroll
from backend.application.execution_tracer import NULL_TRACER

ExecutionMode = Literal["atomic", "isolation"]

def process_payroll_run(
    payroll_run_id: str,
    employees: list[dict],
    tax_bands: list[dict],
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str],
    performed_by: str,
    execution_mode: ExecutionMode = "isolated",
    component_metadata: list | None = None,
    context: dict | None = None,
    tracer=None,
) -> dict:
    """Process payroll for all employees in a single payroll run.

    Iterates through each employee, executes a deterministic payroll
    calculation, and aggregates results with totals.
    Supports logical execution isolation:

        - atomic: stop immediately on first failure
        - isolated: capture failure and continue processing

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        employees: List of employee dicts, each with "employee_id" and
            "components" (list of salary component dicts).
        tax_bands: Progressive tax brackets for PAYE calculation.
        statutory_rule_id: Identifier of the statutory rule applied.
        statutory_version: Version number of the statutory rule.
        payroll_rule_ids: List of workspace-specific payroll rule IDs applied.
        performed_by: Identifier of the user or system triggering the run.
        execution_mode: "atomic" or "isolated" processing mode.
    
    Returns:
        Dict containing:
            - payroll_run_id: The run identifier.
            - results: List of per-employee execution outputs.
            - totals: Aggregated totals including total_net_pay.
    """

    tracer = tracer or NULL_TRACER

    results = []

    total_gross = Decimal("0")
    total_deductions = Decimal("0")
    total_net = Decimal("0")

    success_count = 0
    failure_count = 0

    for emp in employees:

        emp_id = emp["employee_id"]
        components = emp["components"]
        inputs = emp.get("inputs", {})
        short_id = emp_id[:8]

        tracer.info(f"[bold]Employee {short_id}[/bold]")
        tracer.info(
            f"  {len(components)} components: "
            + "  ".join(f"[cyan]{c['code']}[/cyan]={c['amount']}" for c in components)
        )
        if inputs:
            tracer.info(
                f"  {len(inputs)} inputs: "
                + ", ".join(f"[magenta]{c}[/magenta]" for c in inputs)
            )

        try:
            result = execute_single_employee_payroll(
                payroll_run_id=payroll_run_id,
                employee_id=emp_id,
                components=components,
                tax_bands=tax_bands,
                statutory_rule_id=statutory_rule_id,
                statutory_version=statutory_version,
                payroll_rule_ids=payroll_rule_ids,
                performed_by=performed_by,
                inputs=inputs,
                component_metadata=component_metadata,
                context=context,
                tracer=tracer,
            )

            payroll_result = result["payroll_result"]
            snapshot = payroll_result["calculations_snapshot_json"]

            total_gross += Decimal(snapshot["gross"])
            total_deductions += Decimal(snapshot["paye"])
            total_net += Decimal(snapshot["net"])

            tracer.info(
                f"  Gross: [green]{snapshot['gross']}[/green]  │  "
                f"PAYE: [yellow]{snapshot['paye']}[/yellow]  │  "
                f"Net: [bold green]{snapshot['net']}[/bold green]  │  "
                f"[bold green]SUCCESS[/bold green]"
            )

            results.append({
                "employee_id": emp_id,
                "status": "SUCCESS",
                "output": result,
                "error": None,
            })

            success_count += 1

        except Exception as e:

            tracer.warn(f"Employee {short_id} calculation failed: {e}")

            if execution_mode == "atomic":
                raise

            results.append({
                "employee_id": emp_id,
                "status": "FAILED",
                "output": None,
                "error": str(e),
            })

            failure_count += 1

    return {
        "payroll_run_id": payroll_run_id,
        "results": results,
        "totals": {
            "total_gross_pay": total_gross,
            "total_deduction": total_deductions,
            "total_net_pay": total_net,
            "success_count": success_count,
            "failure_count": failure_count,
        },
    }