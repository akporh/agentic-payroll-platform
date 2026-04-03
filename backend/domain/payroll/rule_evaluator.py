"""
Payroll Rule Evaluator.

Applies workspace-level payroll rules to salary components BEFORE the
sequential executor runs.  Returns a modified salary_components dict and
a rule trace so callers can see exactly what fired (or why it didn't).

Rule calculation methods supported:
  unit_multiplier       — rate × input_days  (overtime, shift, weekend)
  daily_rate_deduction  — (gross / working_days) × absent_days  (absence, suspension)
  fixed_amount          — flat amount, optionally gated by conditions  (accident-free bonus)

Temporal resolution
-------------------
Each input event carries its own reference_date.  For unit_multiplier rules,
the engine iterates every event and resolves the rate for that event's period
from the historical rule set effective on that date.

  employee_inputs  →  {input_code: [{quantity, reference_date}]}  — one list per code
  reference_date travels WITH each event; no separate input_reference_dates dict.

Callers supply:
  historical_rule_sets        — [{id, effective_from, items}] from snapshot v2
  historical_period_contexts  — {(year, month): {working_days, calendar_days}}
  period_start / period_end   — current pay period bounds (date objects)
  current_rule_set_id         — UUID of the current rule set (for trace)
  current_rule_set_effective_from — effective_from of the current rule set (for trace)

All temporal params are optional; omitting them gives identical behaviour to
the original implementation.  Scalar inputs (legacy callers / tests) are
normalised to a single-event list by _to_events().
"""

from decimal import Decimal, ROUND_HALF_UP


def _to_events(raw) -> list[dict]:
    """Normalise any input shape to a list of {quantity, reference_date} dicts.

    Handles:
      - None / missing           → []
      - list of event dicts      → returned as-is (repository format)
      - single event dict        → wrapped in list
      - scalar int/float/Decimal → single-event list with reference_date=None
        (legacy callers and unit tests that pass bare scalars)
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return [{
            "quantity":       raw.get("quantity") or raw.get("amount") or 0,
            "reference_date": raw.get("reference_date"),
        }]
    # scalar
    return [{"quantity": raw, "reference_date": None}]


def apply_payroll_rules(
    salary_components: dict,
    payroll_rules: list,
    employee_inputs: dict,
    client_meta: dict,
    working_days: int = 22,
    calendar_days: int = 30,
    *,
    historical_rule_sets: list[dict] | None = None,
    historical_period_contexts: dict | None = None,
    period_start=None,
    period_end=None,
    current_rule_set_id: str | None = None,
    current_rule_set_effective_from: str | None = None,
) -> tuple[dict, list]:
    """Apply workspace payroll rules to salary components.

    Args:
        salary_components:
            Component code → Decimal amount from the salary definition.
        payroll_rules:
            List of payroll_rule dicts (loaded from DB or rule_set_items).
            Each must have: rule_name, rule_definition_json.
            is_active is treated as True when absent (rule_set_items style).
        employee_inputs:
            Event data keyed by input_field name.  Each value is a list of
            event dicts: [{quantity, reference_date}].  Scalar values and bare
            dicts are accepted and normalised via _to_events() at evaluation
            time (backward compatibility).
            Example: {"regular_overtime_days": [{"quantity": 2, "reference_date": date(2026, 1, 1)}]}
        client_meta:
            component_code → metadata_json from client_component_metadata.
            Used to identify proratable components for daily-rate deductions.
        working_days:
            Standard working days in the current period (default 22).
        calendar_days:
            Calendar days in the current period (default 30).

        -- temporal keyword params (all optional) --
        historical_rule_sets:
            [{id, effective_from, items}] from snapshot.historical_rule_sets.
        historical_period_contexts:
            {(year, month): {working_days, calendar_days}} — period stats for
            each distinct historical month spanned by inputs.
        period_start:
            Start of the current pay period (datetime.date).
        period_end:
            End of the current pay period (datetime.date).
        current_rule_set_id:
            UUID of the current rule set (stored in trace for auditing).
        current_rule_set_effective_from:
            effective_from of the current rule set (stored in trace).

    Returns:
        (modified_salary_components, rule_trace)
        modified_salary_components:
            Copy of salary_components with additive rules injected and
            deduction rules applied.
        rule_trace:
            List of dicts, one per rule evaluated:
            {rule, method, status, amount, note,
             rule_set_id, rule_effective_from, reference_date,
             rate_used, resolution_source}
            status is "applied" | "not_applied".
    """
    components = dict(salary_components)
    trace = []

    _hist_rule_sets = historical_rule_sets or []
    _hist_period_ctx = historical_period_contexts or {}

    # Build current rule lookup (name → rule dict)
    current_rules_by_name: dict = {r["rule_name"]: r for r in payroll_rules}

    for rule in payroll_rules:
        # Treat missing is_active as True (rule_set_item format has no is_active)
        if rule.get("is_active") is False:
            continue

        name = rule["rule_name"]
        current_defn = rule.get("rule_definition_json") or {}
        input_field = current_defn.get("input_field", "")
        # Use current_defn for method dispatch — calculation_method is fixed per rule.
        # Per-event _resolve_rule calls inside each branch supply temporal context.
        method = current_defn.get("calculation_method", "")

        # ── unit_multiplier ───────────────────────────────────────────────
        if method == "unit_multiplier":
            _events = _to_events(employee_inputs.get(input_field))
            _positive = [
                e for e in _events
                if Decimal(str(e.get("quantity") or 0)) > 0
            ]
            if _positive:
                _total = Decimal("0")
                _res_meta = None
                _event_notes: list[str] = []
                _last_rate = Decimal("0")
                for _ev in _positive:
                    _ev_qty = Decimal(str(_ev["quantity"]))
                    _ev_ref = _ev.get("reference_date")
                    _resolved_defn, _res_meta = _resolve_rule(
                        name, _ev_ref, current_rules_by_name,
                        _hist_rule_sets, period_start, period_end,
                        current_rule_set_id, current_rule_set_effective_from,
                    )
                    _last_rate = Decimal(str(_resolved_defn.get("rate", 0)))
                    _total += (_ev_qty * _last_rate).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    _event_notes.append(f"{_ev_qty}×{_last_rate}")
                components[name] = _total
                _unit = current_defn.get("unit", "units")
                _note = (
                    f"{len(_positive)} events: {' + '.join(_event_notes)}"
                    if len(_positive) > 1
                    else f"{_positive[0]['quantity']} {_unit} × {_last_rate}"
                )
                _single = len(_positive) == 1
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(_total),
                    "note":                 _note,
                    "rule_set_id":          _res_meta["rule_set_id"],
                    "rule_effective_from":  _res_meta["rule_effective_from"],
                    "reference_date":       str(_positive[0].get("reference_date")) if _single else None,
                    "rate_used":            str(_last_rate) if _single else None,
                    "resolution_source":    _res_meta["resolution_source"],
                })
            else:
                _resolved_defn, _res_meta = _resolve_rule(
                    name, None, current_rules_by_name,
                    _hist_rule_sets, period_start, period_end,
                    current_rule_set_id, current_rule_set_effective_from,
                )
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "note":                 f"no {input_field!r} in employee_inputs",
                    "rule_set_id":          _res_meta["rule_set_id"],
                    "rule_effective_from":  _res_meta["rule_effective_from"],
                    "reference_date":       None,
                    "rate_used":            None,
                    "resolution_source":    _res_meta["resolution_source"],
                })

        # ── daily_rate_deduction ──────────────────────────────────────────
        elif method == "daily_rate_deduction":
            _drd_events = _to_events(employee_inputs.get(input_field))
            input_val = sum(Decimal(str(e.get("quantity") or 0)) for e in _drd_events)
            _first_ref = _drd_events[0].get("reference_date") if _drd_events else None
            resolved_defn, resolution_meta = _resolve_rule(
                name, _first_ref, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
            )
            eff_wd, eff_cd = _resolve_period_ctx(
                _first_ref, working_days, calendar_days,
                _hist_period_ctx, period_start, period_end,
            )
            eff_wd_dec = Decimal(str(eff_wd))
            ref_date_str = str(_first_ref) if _first_ref else None
            if input_val > 0:
                total_deducted = Decimal("0")
                prorated_codes: list[str] = []
                skipped_codes:  list[str] = []
                for code in list(components.keys()):
                    strategy = (
                        client_meta.get(code, {})
                        .get("calculations_behaviour", {})
                        .get("proration_strategy")
                    )
                    if strategy is None:
                        skipped_codes.append(code)
                        continue  # component is not proratable

                    # Dispatch on the strategy value using period-resolved counts
                    if strategy == "work_days":
                        divisor = eff_wd_dec
                    elif strategy == "calendar_days":
                        divisor = Decimal(str(eff_cd))
                    elif strategy == "fixed_30":
                        divisor = Decimal("30")
                    else:
                        # Unrecognised strategy — skip rather than silently corrupt
                        skipped_codes.append(f"{code}(unknown:{strategy})")
                        continue

                    if not divisor:
                        skipped_codes.append(f"{code}(zero_divisor)")
                        continue

                    comp_daily_rate = (
                        components[code] / divisor
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    deduction_for_component = (
                        comp_daily_rate * input_val
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    components[code] = max(
                        Decimal("0"),
                        components[code] - deduction_for_component,
                    )
                    total_deducted += deduction_for_component
                    prorated_codes.append(f"{code}({strategy})")

                note = (
                    f"{input_val} absent days — deducted from: {prorated_codes}"
                    + (f"; skipped (no proration_strategy): {skipped_codes}" if skipped_codes else "")
                )
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(-total_deducted),
                    "note":                 note,
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                })
            else:
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "note":                 f"no {input_field!r} in employee_inputs",
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                })

        # ── fixed_amount ──────────────────────────────────────────────────
        elif method == "fixed_amount":
            resolved_defn, resolution_meta = _resolve_rule(
                name, None, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
            )
            ref_date_str = None
            amount = Decimal(str(resolved_defn.get("amount", 0)))
            condition = resolved_defn.get("condition") or {}
            met, reason = _evaluate_condition(condition, employee_inputs)
            if met:
                components[name] = amount
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(amount),
                    "note":                 "all conditions met",
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            str(amount),
                    "resolution_source":    resolution_meta["resolution_source"],
                })
            else:
                trace.append({
                    "rule":                 name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "note":                 reason,
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                })

        else:
            _resolved_defn, _res_meta = _resolve_rule(
                name, None, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
            )
            trace.append({
                "rule":                 name,
                "method":               method or "unknown",
                "status":               "not_applied",
                "amount":               "0",
                "note":                 f"unrecognised calculation_method: {method!r}",
                "rule_set_id":          _res_meta["rule_set_id"],
                "rule_effective_from":  _res_meta["rule_effective_from"],
                "reference_date":       None,
                "rate_used":            None,
                "resolution_source":    _res_meta["resolution_source"],
            })

    return components, trace


def _resolve_rule(
    rule_name: str,
    reference_date,
    current_rules_by_name: dict,
    historical_rule_sets: list[dict],
    period_start,
    period_end,
    current_rule_set_id: str | None,
    current_rule_set_effective_from: str | None,
) -> tuple[dict, dict]:
    """Return (rule_definition_json, resolution_meta) for the given rule.

    Uses the current rule set when reference_date is None or within the
    current period.  Falls back to the most-recently-effective historical
    rule set whose effective_from <= reference_date for cross-period inputs.

    resolution_meta keys: rule_set_id, rule_effective_from, resolution_source
    resolution_source values: "current" | "historical" | "current_fallback"
    """
    is_current = (
        reference_date is None
        or period_start is None
        or period_end is None
        or period_start <= reference_date <= period_end
    )

    if is_current:
        row = current_rules_by_name.get(rule_name, {})
        return row.get("rule_definition_json") or {}, {
            "rule_set_id":          current_rule_set_id,
            "rule_effective_from":  current_rule_set_effective_from,
            "resolution_source":    "current",
        }

    # Historical: find the latest rule set whose effective_from <= reference_date
    ref_str = str(reference_date)
    applicable: dict | None = None
    for rs in sorted(historical_rule_sets, key=lambda x: x.get("effective_from", ""), reverse=True):
        if (rs.get("effective_from") or "") <= ref_str:
            applicable = rs
            break

    if applicable:
        items_by_name = {item["rule_name"]: item for item in applicable.get("items", [])}
        row = items_by_name.get(rule_name, {})
        return row.get("rule_definition_json") or {}, {
            "rule_set_id":          applicable.get("id"),
            "rule_effective_from":  applicable.get("effective_from"),
            "resolution_source":    "historical",
        }

    # No historical set covers this date — fall back to current to avoid silent no-op
    row = current_rules_by_name.get(rule_name, {})
    return row.get("rule_definition_json") or {}, {
        "rule_set_id":          current_rule_set_id,
        "rule_effective_from":  current_rule_set_effective_from,
        "resolution_source":    "current_fallback",
    }


def _resolve_period_ctx(
    reference_date,
    working_days: int,
    calendar_days: int,
    historical_period_contexts: dict,
    period_start,
    period_end,
) -> tuple[int, int]:
    """Return (working_days, calendar_days) for the period containing reference_date.

    Falls back to the current period stats when reference_date is None,
    within the current period, or when no historical context is available.

    historical_period_contexts: {(year, month): {"working_days": int, "calendar_days": int}}
    """
    is_current = (
        reference_date is None
        or period_start is None
        or period_end is None
        or period_start <= reference_date <= period_end
    )
    if is_current:
        return working_days, calendar_days

    key = (reference_date.year, reference_date.month)
    ctx = historical_period_contexts.get(key)
    if ctx:
        return ctx.get("working_days", working_days), ctx.get("calendar_days", calendar_days)

    return working_days, calendar_days


def _evaluate_condition(condition: dict, employee_inputs: dict) -> tuple[bool, str]:
    """Check a rule condition dict against employee_inputs.

    Returns (met: bool, reason: str).
    Missing keys in employee_inputs cause the condition to fail gracefully.
    """
    if not condition:
        return True, ""

    for key, expected in condition.items():
        actual = employee_inputs.get(key)
        # Normalise event list to a scalar quantity for condition comparison
        if isinstance(actual, list):
            actual = actual[0].get("quantity") if actual else None
        if actual is None:
            return False, f"no {key!r} in employee_inputs"
        if str(actual) != str(expected):
            return False, f"{key} = {actual!r}, expected {expected!r}"

    return True, ""
