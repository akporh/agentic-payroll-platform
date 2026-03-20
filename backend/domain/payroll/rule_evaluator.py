"""
Payroll Rule Evaluator.

Applies workspace-level payroll rules to salary components BEFORE the
sequential executor runs.  Returns a modified salary_components dict and
a rule trace so callers can see exactly what fired (or why it didn't).

Rule calculation methods supported:
  unit_multiplier       — rate × input_days  (overtime, shift, weekend)
  daily_rate_deduction  — (gross / working_days) × absent_days  (absence, suspension)
  fixed_amount          — flat amount, optionally gated by conditions  (accident-free bonus)
"""

from decimal import Decimal, ROUND_HALF_UP


def apply_payroll_rules(
    salary_components: dict,
    payroll_rules: list,
    employee_inputs: dict,
    client_meta: dict,
    working_days: int = 22,
) -> tuple[dict, list]:
    """Apply workspace payroll rules to salary components.

    Args:
        salary_components:
            Component code → Decimal amount from the salary definition.
        payroll_rules:
            List of payroll_rule dicts (loaded from DB).
            Each must have: rule_name, rule_definition_json, is_active.
        employee_inputs:
            Event data for this pay period, keyed by input_field name.
            Example: {"regular_overtime_days": 2, "shift_days": 5}
            Pass an empty dict when no event data is available.
        client_meta:
            component_code → metadata_json from client_component_metadata.
            Used to identify proratable components for daily-rate deductions.
        working_days:
            Standard working days in the period (default 22).

    Returns:
        (modified_salary_components, rule_trace)
        modified_salary_components:
            Copy of salary_components with additive rules injected and
            deduction rules applied.
        rule_trace:
            List of dicts, one per rule:
            {"rule", "method", "status", "amount", "note"}
            status is "applied" | "not_applied".
    """
    components = dict(salary_components)
    trace = []

    # Base gross for daily-rate calculations (sum of original salary components)
    base_gross = sum(components.values(), Decimal("0"))
    wd = Decimal(str(working_days))
    daily_rate = (
        (base_gross / wd).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if wd
        else Decimal("0")
    )

    for rule in payroll_rules:
        if not rule.get("is_active"):
            continue

        name = rule["rule_name"]
        defn = rule.get("rule_definition_json") or {}
        method = defn.get("calculation_method", "")
        input_field = defn.get("input_field", "")
        input_val = Decimal(str(employee_inputs.get(input_field, 0)))

        # ── unit_multiplier ───────────────────────────────────────────────
        if method == "unit_multiplier":
            if input_val > 0:
                rate = Decimal(str(defn.get("rate", 0)))
                amount = (input_val * rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                components[name] = amount
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "applied",
                    "amount": str(amount),
                    "note":   f"{input_val} {defn.get('unit', 'units')} × {rate}",
                })
            else:
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "not_applied",
                    "amount": "0",
                    "note":   f"no {input_field!r} in employee_inputs",
                })

        # ── daily_rate_deduction ──────────────────────────────────────────
        elif method == "daily_rate_deduction":
            if input_val > 0:
                deduction = (daily_rate * input_val).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                # Reduce each proratable component proportionally
                proration_ratio = (
                    (Decimal("1") - input_val / wd).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )
                    if wd
                    else Decimal("1")
                )
                for code in list(components.keys()):
                    is_proratable = (
                        client_meta.get(code, {})
                        .get("calculations_behaviour", {})
                        .get("proration_strategy") is not None
                    )
                    if is_proratable:
                        original = components[code]
                        components[code] = (original * proration_ratio).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "applied",
                    "amount": str(-deduction),
                    "note":   (
                        f"{input_val} absent days × {daily_rate}/day daily rate "
                        f"(ratio {proration_ratio})"
                    ),
                })
            else:
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "not_applied",
                    "amount": "0",
                    "note":   f"no {input_field!r} in employee_inputs",
                })

        # ── fixed_amount ──────────────────────────────────────────────────
        elif method == "fixed_amount":
            amount = Decimal(str(defn.get("amount", 0)))
            condition = defn.get("condition") or {}
            met, reason = _evaluate_condition(condition, employee_inputs)
            if met:
                components[name] = amount
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "applied",
                    "amount": str(amount),
                    "note":   "all conditions met",
                })
            else:
                trace.append({
                    "rule":   name,
                    "method": method,
                    "status": "not_applied",
                    "amount": "0",
                    "note":   reason,
                })

        else:
            trace.append({
                "rule":   name,
                "method": method or "unknown",
                "status": "not_applied",
                "amount": "0",
                "note":   f"unrecognised calculation_method: {method!r}",
            })

    return components, trace


def _evaluate_condition(condition: dict, employee_inputs: dict) -> tuple[bool, str]:
    """Check a rule condition dict against employee_inputs.

    Returns (met: bool, reason: str).
    Missing keys in employee_inputs cause the condition to fail gracefully.
    """
    if not condition:
        return True, ""

    for key, expected in condition.items():
        actual = employee_inputs.get(key)
        if actual is None:
            return False, f"no {key!r} in employee_inputs"
        if str(actual) != str(expected):
            return False, f"{key} = {actual!r}, expected {expected!r}"

    return True, ""
