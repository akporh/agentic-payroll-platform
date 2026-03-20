"""
Sequential Payroll Executor.

Executes payroll components in execution_priority order, driven by
component_metadata.  Each component's calculation_method determines
what computation is performed and which prior results it consumes.

This is a pure deterministic function — no database access, no side effects.
All monetary values are Decimal throughout.

Execution order for Nigeria (NG):
  10  BASIC                  salary_component
  20  HOUSING                salary_component
  30  TRANSPORT              salary_component
  40  CONSOLIDATED_ALLOWANCE salary_component
 100  GROSS_PAY              sum_earnings
 200  PENSION_EMPLOYEE       pension_rule
 250  RENT_RELIEF            rent_relief      (skipped if ANNUAL_RENT_PAID absent)
 300  TAXABLE_INCOME         taxable_income   (GROSS - PENSION - RENT_RELIEF)
 400  PAYE                   paye_rule        (bands applied to TAXABLE_INCOME)
 410  NHF_CONTRIBUTION       nhf_rule
 420  HEALTH_INSURANCE_EMPLOYEE health_insurance_flat
 430  DEVELOPMENT_LEVY       development_levy_flat
 440  LIFE_INSURANCE         life_insurance_rule
 500  NET_PAY                net_formula
"""

from decimal import Decimal, ROUND_HALF_UP

from backend.domain.rules.nhf import calculate_nhf
from backend.domain.rules.paye import calculate_monthly_paye
from backend.domain.rules.pension import calculate_pension
from backend.domain.rules.rent_relief import calculate_rent_relief


def _check_eligibility(
    conditions: list,
    logic: str,
    employee_inputs: dict,
    results: dict,
) -> bool:
    """Evaluate eligibility conditions. Returns True if eligible to run."""
    if not conditions:
        return True

    checks = []
    for cond in conditions:
        cond_type = cond.get("type")

        if cond_type == "input_present":
            checks.append(cond["input_code"] in employee_inputs)

        elif cond_type == "input_value":
            actual    = Decimal(str(employee_inputs.get(cond["input_code"], {}).get("amount") or 0))
            threshold = Decimal(str(cond.get("value", 0)))
            op        = cond.get("operator", "gt")
            checks.append(
                actual > threshold  if op == "gt"  else
                actual >= threshold if op == "gte" else
                actual < threshold  if op == "lt"  else
                actual == threshold if op == "eq"  else False
            )

        elif cond_type == "component_result":
            actual    = results.get(cond["component_code"], Decimal("0"))
            threshold = Decimal(str(cond.get("value", 0)))
            op        = cond.get("operator", "gt")
            checks.append(
                actual > threshold  if op == "gt"  else
                actual >= threshold if op == "gte" else
                actual < threshold  if op == "lt"  else
                actual == threshold if op == "eq"  else False
            )

        else:
            checks.append(True)

    return any(checks) if logic == "ANY" else all(checks)


def _resolve_inputs(input_requirements: dict, employee_inputs: dict) -> dict:
    """Build {input_code: Decimal} for each declared field present in employee_inputs."""
    resolved = {}
    for field in input_requirements.get("fields", []):
        code = field["input_code"]
        if code in employee_inputs:
            resolved[code] = Decimal(str(employee_inputs[code].get("amount") or 0))
    return resolved


def run_sequential_payroll(
    salary_components: dict,
    component_metadata: list,
    context: dict,
) -> dict:
    """Execute payroll components sequentially by execution_priority.

    Args:
        salary_components:
            Mapping of component_code → Decimal amount for this employee.
            Example: {"BASIC": Decimal("250000"), "HOUSING": Decimal("125000"), ...}

        component_metadata:
            List of component metadata dicts from the component_metadata table.
            Each dict must include: component_code, component_class,
            calculation_method, execution_priority, is_active.

        context:
            Runtime context required by statutory calculation methods:
                - tax_bands (list[dict]): PAYE progressive brackets.
                - pension_employee_rate (Decimal): Employee pension rate.
                - pension_employer_rate (Decimal): Employer pension rate.

    Returns:
        {
            "results": {component_code: Decimal},   # all computed values
            "trace":   [                             # one entry per executed component
                {
                    "component": str,
                    "method":    str,
                    "result":    str,   # Decimal serialised as string
                },
                ...
            ]
        }
    """
    # ------------------------------------------------------------------ #
    # 1. Filter to active components and sort by execution_priority.      #
    #    Components with NULL priority are informational and skipped.     #
    # ------------------------------------------------------------------ #
    active_meta = [m for m in component_metadata if m.get("is_active")]

    ordered = sorted(
        [m for m in active_meta if m.get("execution_priority") is not None],
        key=lambda m: m["execution_priority"],
    )

    # Fast lookup map: component_code → metadata dict
    component_map = {m["component_code"]: m for m in active_meta}

    # ------------------------------------------------------------------ #
    # 2. Unpack context.                                                   #
    # ------------------------------------------------------------------ #
    tax_bands             = context.get("tax_bands", [])
    pension_employee_rate = Decimal(str(context.get("pension_employee_rate", "0.09")))
    pension_employer_rate = Decimal(str(context.get("pension_employer_rate", "0.10")))
    rent_relief_cfg       = context.get("rent_relief_cfg") or {}
    employee_inputs       = context.get("employee_inputs") or {}
    # client_meta: {component_code: metadata_json} — drives pensionable base
    client_meta           = context.get("client_meta") or {}
    nhf_rate                         = Decimal(str(context.get("nhf_rate", "0.025")))
    health_insurance_employee_amount = Decimal(str(context.get("health_insurance_employee_amount", "0")))
    development_levy_amount          = Decimal(str(context.get("development_levy_amount", "0")))
    life_insurance_employer_rate     = Decimal(str(context.get("life_insurance_employer_rate", "0")))

    # ------------------------------------------------------------------ #
    # 3. Execute components sequentially, accumulating results.           #
    # ------------------------------------------------------------------ #
    results: dict[str, Decimal] = {}
    execution_trace: list[dict] = []

    for meta in ordered:
        code      = meta["component_code"]
        method    = meta.get("calculation_method") or ""
        meta_json = meta.get("metadata_json") or {}

        # --- Generic eligibility gate ---
        eligibility_cfg = meta_json.get("eligibility", {})
        if eligibility_cfg:
            eligible = _check_eligibility(
                eligibility_cfg.get("conditions", []),
                eligibility_cfg.get("logic", "ALL"),
                employee_inputs,
                results,
            )
            if not eligible and eligibility_cfg.get("on_ineligible") == "skip":
                continue

        if method == "salary_component":
            results[code] = Decimal(str(salary_components.get(code, "0")))

        elif method == "sum_earnings":
            results[code] = sum(
                (v for k, v in results.items()
                 if component_map.get(k, {}).get("component_class") == "earning"),
                Decimal("0"),
            )

        elif method == "pension_rule":
            # Pensionable base: driven by client_meta.legal_role.is_pensionable.
            # Falls back to the PRA 2014 statutory set if client_meta is absent
            # OR if client_meta exists but no components are flagged is_pensionable.
            if client_meta:
                pensionable_codes = {
                    code for code, meta in client_meta.items()
                    if meta.get("legal_role", {}).get("is_pensionable", False)
                }
                if not pensionable_codes:
                    pensionable_codes = {"BASIC", "HOUSING", "TRANSPORT"}
            else:
                pensionable_codes = {"BASIC", "HOUSING", "TRANSPORT"}
            pensionable_base = sum(
                (results.get(c, Decimal("0")) for c in pensionable_codes if c in results),
                Decimal("0"),
            )
            pension_employee, pension_employer = calculate_pension(
                pensionable_base,
                pension_employee_rate,
                pension_employer_rate,
            )
            results["PENSION_EMPLOYEE"] = pension_employee
            results["PENSION_EMPLOYER"] = pension_employer
            # The trace entry records the employee contribution (the deduction)
            code = "PENSION_EMPLOYEE"

        elif method == "rent_relief":
            resolved         = _resolve_inputs(meta_json.get("input_requirements", {}), employee_inputs)
            annual_rent_paid = resolved.get("ANNUAL_RENT_PAID", Decimal("0"))
            rate = Decimal(str(rent_relief_cfg.get("rate", "0")))
            cap  = Decimal(str(rent_relief_cfg.get("cap",  "0")))
            results[code] = calculate_rent_relief(annual_rent_paid, rate, cap)

        elif method == "taxable_income":
            results[code] = (
                results.get("GROSS_PAY",        Decimal("0"))
                - results.get("PENSION_EMPLOYEE", Decimal("0"))
                - results.get("RENT_RELIEF",      Decimal("0"))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        elif method == "paye_rule":
            results[code] = calculate_monthly_paye(
                results.get("TAXABLE_INCOME", Decimal("0")), tax_bands
            )

        elif method == "nhf_rule":
            results[code] = calculate_nhf(
                results.get("BASIC", Decimal("0")),
                nhf_rate,
            )

        elif method == "health_insurance_flat":
            results[code] = health_insurance_employee_amount

        elif method == "development_levy_flat":
            results[code] = development_levy_amount

        elif method == "life_insurance_rule":
            results[code] = (
                results.get("GROSS_PAY", Decimal("0")) * life_insurance_employer_rate
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        elif method == "net_formula":
            total_deductions = sum(
                (v for k, v in results.items()
                 if component_map.get(k, {}).get("component_class") == "statutory_deduction"),
                Decimal("0"),
            )
            results[code] = (
                results.get("GROSS_PAY", Decimal("0")) - total_deductions
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        execution_trace.append({
            "component": code,
            "method":    method,
            "result":    str(results.get(code)),
        })

    return {
        "results": results,
        "trace":   execution_trace,
    }
