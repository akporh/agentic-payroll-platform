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

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class NoHistoricalRuleVersionError(Exception):
    """Raised when a rule has no version on or before reference_date for this workspace —
    i.e. reference_date genuinely predates all known history for this rule (not merely a
    missing rule_set snapshot, which auto_publish()/the backfill script should have covered).
    """

    def __init__(self, rule_name: str, reference_date):
        self.rule_name = rule_name
        self.reference_date = reference_date
        super().__init__(
            f"No historical rate exists for rule '{rule_name}' as of {reference_date}. "
            "This input predates all known versions of this rule for this workspace — "
            "verify the input's reference_date, or add an earlier payroll_rule version "
            "if this rate genuinely existed before the platform's records begin."
        )

# All recognised calculation_method values in payroll_rule.rule_definition_json.
# D3: Python-level validation mirrors the DB CHECK constraint added in migration
# 2b3c4d5e6f7a. Keep in sync with the constraint when adding new methods.
VALID_CALCULATION_METHODS = frozenset({
    "unit_multiplier",
    "daily_rate_deduction",
    "fixed_amount",
    "ot_multiplier",
    "percentage_of_sum",
})


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
    expected_hours: int | None = None,
    expected_days: int | None = None,
    rate_code_map: dict | None = None,
    shift_type: str | None = None,
    employee_context: dict | None = None,
    rule_floor_dates: dict[str, str] | None = None,
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
        rule_floor_dates:
            {rule_name: earliest_known_effective_from} — when supplied (not None),
            enables strict mode: a historical reference_date earlier than the rule's
            known floor raises NoHistoricalRuleVersionError instead of silently
            falling back to the current rule. None (the default, used by legacy
            callers/tests) preserves the original current_fallback behaviour.

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
                        rule_floor_dates,
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
                    "component":            name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(_total),
                    "result":               str(_total),
                    "note":                 _note,
                    "rule_set_id":          _res_meta["rule_set_id"],
                    "rule_effective_from":  _res_meta["rule_effective_from"],
                    "reference_date":       str(_positive[0].get("reference_date")) if _single else None,
                    "rate_used":            str(_last_rate) if _single else None,
                    "resolution_source":    _res_meta["resolution_source"],
                    "warning":              _res_meta.get("warning"),
                })
            else:
                _resolved_defn, _res_meta = _resolve_rule(
                    name, None, current_rules_by_name,
                    _hist_rule_sets, period_start, period_end,
                    current_rule_set_id, current_rule_set_effective_from,
                    rule_floor_dates,
                )
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "result":               None,
                    "note":                 f"no {input_field!r} in employee_inputs",
                    "rule_set_id":          _res_meta["rule_set_id"],
                    "rule_effective_from":  _res_meta["rule_effective_from"],
                    "reference_date":       None,
                    "rate_used":            None,
                    "resolution_source":    _res_meta["resolution_source"],
                    "warning":              _res_meta.get("warning"),
                })

        # ── daily_rate_deduction ──────────────────────────────────────────
        elif method == "daily_rate_deduction":
            _drd_events = _to_events(employee_inputs.get(input_field))
            input_val = sum(Decimal(str(e.get("quantity") or 0)) for e in _drd_events)

            # Group events by the (working_days, calendar_days) that applies to each
            # event's own reference_date — a deduction spanning both a historical and
            # the current period must apply each portion's own period divisor, not
            # resolve once for the whole batch from the first event's date alone.
            _groups: dict[tuple, dict] = {}
            for _ev in (_drd_events or [{"quantity": 0, "reference_date": None}]):
                _qty = Decimal(str(_ev.get("quantity") or 0))
                _ref = _ev.get("reference_date")
                _resolved_defn, _meta = _resolve_rule(
                    name, _ref, current_rules_by_name,
                    _hist_rule_sets, period_start, period_end,
                    current_rule_set_id, current_rule_set_effective_from,
                    rule_floor_dates,
                )
                _wd, _cd = _resolve_period_ctx(
                    _ref, working_days, calendar_days,
                    _hist_period_ctx, period_start, period_end,
                )
                key = (_wd, _cd)
                g = _groups.setdefault(key, {"qty": Decimal("0"), "meta": _meta, "ref": _ref})
                g["qty"] += _qty

            _single_group = len(_groups) == 1
            if _single_group:
                ((_only_wd, _only_cd), _only_group), = _groups.items()
                resolution_meta = _only_group["meta"]
                ref_date_str = str(_only_group["ref"]) if _only_group["ref"] else None
            else:
                resolution_meta = {
                    "rule_set_id": None, "rule_effective_from": None,
                    "resolution_source": None, "warning": None,
                }
                ref_date_str = None

            if input_val > 0:
                total_deducted = Decimal("0")
                prorated_codes: list[str] = []
                skipped_codes:  list[str] = []
                any_fallback = False
                group_notes: list[str] = []
                for code in list(components.keys()):
                    strategy = (
                        client_meta.get(code, {})
                        .get("calculations_behaviour", {})
                        .get("proration_strategy")
                    )
                    if strategy is None:
                        skipped_codes.append(code)
                        continue  # component is not proratable
                    if strategy not in ("work_days", "calendar_days", "fixed_30"):
                        skipped_codes.append(f"{code}(unknown:{strategy})")
                        continue

                    per_code_deduction = Decimal("0")
                    any_valid_divisor = False
                    for (eff_wd, eff_cd), g in _groups.items():
                        if g["meta"]["resolution_source"] == "current_fallback":
                            any_fallback = True
                        if strategy == "work_days":
                            divisor = Decimal(str(eff_wd))
                        elif strategy == "calendar_days":
                            divisor = Decimal(str(eff_cd))
                        else:
                            divisor = Decimal("30")

                        if not divisor:
                            continue  # this group's divisor is zero — skip only this group's slice

                        any_valid_divisor = True
                        comp_daily_rate = (
                            components[code] / divisor
                        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                        per_code_deduction += (
                            comp_daily_rate * g["qty"]
                        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    if not any_valid_divisor:
                        # Every group's divisor was zero — the code is fully skipped,
                        # never partially "prorated" with a zero amount.
                        skipped_codes.append(f"{code}(zero_divisor)")
                        continue

                    components[code] = max(
                        Decimal("0"),
                        components[code] - per_code_deduction,
                    )
                    total_deducted += per_code_deduction
                    prorated_codes.append(f"{code}({strategy})")

                if not _single_group:
                    group_notes = [
                        f"{g['qty']}d@{eff_wd}wd"
                        f"{'(historical, rule_set ' + str(g['meta']['rule_set_id']) + ')' if g['meta']['resolution_source'] == 'historical' else ''}"
                        f"{'(current fallback — no history)' if g['meta']['resolution_source'] == 'current_fallback' else ''}"
                        for (eff_wd, eff_cd), g in _groups.items()
                    ]

                note = (
                    f"{input_val} absent days — deducted from: {prorated_codes}"
                    + (f"; skipped (no proration_strategy): {skipped_codes}" if skipped_codes else "")
                    + (f"; spans {len(_groups)} periods: {' + '.join(group_notes)}" if not _single_group else "")
                )
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(-total_deducted),
                    "result":               str(-total_deducted),
                    "note":                 note,
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                    "warning":              (
                        resolution_meta.get("warning")
                        if _single_group
                        else ("One or more periods in this multi-period deduction used the "
                              "current rule set because no historical rule set covers them."
                              if any_fallback else None)
                    ),
                })
            else:
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "result":               None,
                    "note":                 f"no {input_field!r} in employee_inputs",
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                    "warning":              resolution_meta.get("warning"),
                })

        # ── fixed_amount ──────────────────────────────────────────────────
        # No input_field / employee event / reference_date concept exists for this
        # method (confirmed: it's a flat, run-scoped amount, e.g. accident-free
        # bonus). reference_date=None is correct by design — do not "fix" this to
        # thread a per-event date without re-verifying that conclusion first.
        elif method == "fixed_amount":
            resolved_defn, resolution_meta = _resolve_rule(
                name, None, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
                rule_floor_dates,
            )
            ref_date_str = None
            amount = Decimal(str(resolved_defn.get("amount", 0)))
            component_source = resolved_defn.get("component_source")
            # If amount is zero and component_source is set, derive from the named salary component.
            # Rule output key is rule `name`; source key is `component_source` — no double-count
            # unless operator names the rule identically to the component (future validation story).
            if amount == Decimal("0") and component_source:
                amount = components.get(component_source, Decimal("0"))
            condition = resolved_defn.get("condition") or {}
            met, reason = _evaluate_condition(condition, employee_inputs)
            if met:
                components[name] = amount
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "applied",
                    "amount":               str(amount),
                    "result":               str(amount),
                    "note":                 "all conditions met",
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            str(amount),
                    "resolution_source":    resolution_meta["resolution_source"],
                    "warning":              resolution_meta.get("warning"),
                })
            else:
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "result":               None,
                    "note":                 reason,
                    "rule_set_id":          resolution_meta["rule_set_id"],
                    "rule_effective_from":  resolution_meta["rule_effective_from"],
                    "reference_date":       ref_date_str,
                    "rate_used":            None,
                    "resolution_source":    resolution_meta["resolution_source"],
                    "warning":              resolution_meta.get("warning"),
                })

        # ── ot_multiplier (C4 — PH-8) ─────────────────────────────────────────
        elif method == "ot_multiplier":
            input_field = current_defn.get("input_field", "")

            # Resolve quantity from employee inputs
            events   = _to_events(employee_inputs.get(input_field))
            quantity = sum(Decimal(str(e.get("quantity") or 0)) for e in events)

            # The rule definition itself (rate_code / input_field / manual_adj_field)
            # IS versioned via payroll_rule, so resolve it per the triggering event's
            # own reference_date — this fixes cases where a workspace changed which
            # rate_code an OT rule maps to over time. rate_code_registry's numeric
            # multiplier/base values have NO versioning column at all (no
            # effective_from) — true historical resolution of those is not possible
            # without a schema change (# TODO(rate-code-versioning): add
            # effective_from/history to rate_code_registry if OT multipliers are ever
            # found to change over time). Until then, the multiplier/base lookup below
            # stays current-only, but resolution_source is labelled honestly rather
            # than hardcoded — see _ot_meta handling after the rate_code_map lookup.
            _ot_ref = events[0].get("reference_date") if events else None
            resolved_defn, _ot_meta = _resolve_rule(
                name, _ot_ref, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
                rule_floor_dates,
            )
            rate_code = resolved_defn.get("rate_code") or current_defn.get("rate_code")
            if _ot_meta["resolution_source"] == "current":
                _ot_resolution_source = "current"
                _ot_warning = None
            else:
                _ot_resolution_source = "current_fallback"
                _ot_warning = (
                    "rate_code_registry has no historical versioning — multiplier/base "
                    f"for '{rate_code}' could not be verified against the rate in effect "
                    f"on {_ot_ref}; current value used."
                )
            _ot_ref_str = str(_ot_ref) if _ot_ref else None

            # Floor validation for MANUAL_PH_ADJUSTMENT inputs (C7 — PH-5)
            manual_adj_field = resolved_defn.get("manual_adj_field") or current_defn.get("manual_adj_field")
            if manual_adj_field:
                adj_events    = _to_events(employee_inputs.get(manual_adj_field))
                manual_adj    = sum(Decimal(str(e.get("quantity") or 0)) for e in adj_events)
                total_quantity = quantity + manual_adj
                if total_quantity < Decimal("0"):
                    raise ValueError(
                        f"Manual adjustment of {manual_adj} on rule '{name}' would result in "
                        f"{total_quantity} total hours. Total cannot be negative."
                    )
                quantity = total_quantity

            if quantity > Decimal("0"):
                # Fetch rate code from pre-fetched map — no infra imports in domain layer
                _rate_code_map = rate_code_map or {}
                registry_row = _rate_code_map.get(rate_code) if rate_code else None
                if not registry_row:
                    raise ValueError(
                        f"rate_code '{rate_code}' not found in rate_code_registry "
                        f"for rule '{name}'"
                    )

                multiplier = Decimal(str(registry_row["multiplier"]))
                base       = registry_row["base"]  # 'basic_hourly' | 'basic_daily'

                # D9 — shift_type gate: basic_daily codes are shift allowances.
                # DAY workers (and unset shift_type) are not entitled to shift allowance.
                if base == "basic_daily" and shift_type in (None, "DAY"):
                    trace.append({
                        "rule":              name,
                        "component":         name,
                        "method":            method,
                        "status":            "not_applied",
                        "amount":            "0",
                        "result":            None,
                        "note":              f"shift_type={shift_type!r} — not a shift worker",
                        "rate_code":         rate_code,
                        "multiplier":        str(multiplier),
                        "base_rate":         None,
                        "quantity":          str(quantity),
                        "rule_set_id":       _ot_meta["rule_set_id"],
                        "rule_effective_from": _ot_meta["rule_effective_from"],
                        "reference_date":    _ot_ref_str,
                        "rate_used":         None,
                        "resolution_source": _ot_resolution_source,
                        "warning":           _ot_warning,
                    })
                    continue

                basic = components.get("BASIC")
                if not basic:
                    raise ValueError(
                        f"BASIC missing from salary_components for ot_multiplier rule '{name}'"
                    )

                if base == "basic_hourly":
                    denominator = Decimal(str(expected_hours or 0))
                    if denominator <= 0:
                        raise ValueError(
                            "expected_hours is zero or missing — cannot compute basic_hourly rate "
                            f"for rule '{name}'"
                        )
                elif base == "basic_daily":
                    denominator = Decimal(str(expected_days or 0))
                    if denominator <= 0:
                        raise ValueError(
                            "expected_days is zero or missing — cannot compute basic_daily rate "
                            f"for rule '{name}'"
                        )
                else:
                    raise ValueError(
                        f"Unknown base '{base}' in rate_code_registry for code '{rate_code}'"
                    )

                base_rate = (basic / denominator).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                amount = (quantity * base_rate * multiplier).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                components[name] = amount
                trace.append({
                    "rule":              name,
                    "component":         name,
                    "method":            method,
                    "status":            "applied",
                    "amount":            str(amount),
                    "result":            str(amount),
                    "note":              (
                        f"{quantity} units × {base_rate} ({base}) × {multiplier} multiplier"
                    ),
                    "rate_code":         rate_code,
                    "multiplier":        str(multiplier),
                    "base_rate":         str(base_rate),
                    "quantity":          str(quantity),
                    "rule_set_id":       _ot_meta["rule_set_id"],
                    "rule_effective_from": _ot_meta["rule_effective_from"],
                    "reference_date":    _ot_ref_str,
                    "rate_used":         str(base_rate),
                    "resolution_source": _ot_resolution_source,
                    "warning":           _ot_warning,
                })
            else:
                trace.append({
                    "rule":              name,
                    "component":         name,
                    "method":            method,
                    "status":            "not_applied",
                    "amount":            "0",
                    "result":            None,
                    "note":              f"no {input_field!r} in employee_inputs or quantity is zero",
                    "rule_set_id":       _ot_meta["rule_set_id"],
                    "rule_effective_from": _ot_meta["rule_effective_from"],
                    "reference_date":    _ot_ref_str,
                    "rate_used":         None,
                    "resolution_source": _ot_resolution_source,
                    "warning":           _ot_warning,
                })

        # ── percentage_of_sum (Sprint 13 M3) ─────────────────────────────────
        # No input_field / employee event / reference_date concept exists for this
        # method — it sums already-computed salary_components for the CURRENT run's
        # own period (e.g. "X% of gross pay this period"), never a dated input.
        # resolution_source="current" is correct by design and accurate; it is not a
        # bug that this branch never calls _resolve_rule. Do not "fix" this without
        # re-verifying that conclusion first.
        elif method == "percentage_of_sum":
            rate_val = current_defn.get("rate")
            if rate_val is None:
                raise ValueError(
                    f"percentage_of_sum rule '{name}': 'rate' missing from rule_definition_json"
                )
            base_component_names: list = current_defn.get("base_components") or []
            eligibility_field: str | None = current_defn.get("eligibility_field")

            if not base_component_names:
                logger.warning(
                    "percentage_of_sum rule '%s': base_components is empty — returning 0",
                    name,
                )
                trace.append({
                    "rule":                 name,
                    "component":            name,
                    "method":               method,
                    "status":               "not_applied",
                    "amount":               "0",
                    "result":               None,
                    "note":                 "base_components list is empty — misconfiguration",
                    "rule_set_id":          current_rule_set_id,
                    "rule_effective_from":  current_rule_set_effective_from,
                    "reference_date":       None,
                    "rate_used":            None,
                    "resolution_source":    "current",
                    "warning":              "base_components is empty",
                })
                continue

            # Eligibility gate — C1: not_applied trace entry is mandatory for auditability.
            if eligibility_field is not None:
                ctx_val = (employee_context or {}).get(eligibility_field)
                if not ctx_val:
                    trace.append({
                        "rule":                 name,
                        "component":            name,
                        "method":               method,
                        "status":               "not_applied",
                        "amount":               "0",
                        "result":               None,
                        "note":                 (
                            f"eligibility_field '{eligibility_field}' "
                            f"resolved to {ctx_val!r} — rule did not fire"
                        ),
                        "eligibility_field":    eligibility_field,
                        "eligibility_value":    str(ctx_val),
                        "rule_set_id":          current_rule_set_id,
                        "rule_effective_from":  current_rule_set_effective_from,
                        "reference_date":       None,
                        "rate_used":            None,
                        "resolution_source":    "current",
                        "warning":              None,
                    })
                    continue

            # Resolve base_components against PRE-RULES salary_components snapshot (D2).
            # salary_components is the original dict passed into apply_payroll_rules —
            # components (the working copy) may already have rule-injected values.
            rate = Decimal(str(rate_val))
            resolved = {
                c: salary_components.get(c, Decimal("0"))
                for c in base_component_names
            }
            base_total = sum(resolved.values(), Decimal("0"))
            amount = (rate * base_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            components[name] = amount

            trace_entry: dict = {
                "rule":                  name,
                "component":             name,
                "method":                method,
                "status":                "applied",
                "amount":                str(amount),
                "result":                str(amount),
                "note":                  (
                    f"rate {rate} × base_total {base_total} = {amount}"
                ),
                "rate":                  str(rate),
                "base_components":       base_component_names,
                "resolved_base_values":  {k: str(v) for k, v in resolved.items()},
                "base_total":            str(base_total),
                "rule_set_id":           current_rule_set_id,
                "rule_effective_from":   current_rule_set_effective_from,
                "reference_date":        None,
                "rate_used":             str(rate),
                "resolution_source":     "current",
                "warning":               None,
            }
            if eligibility_field is not None:
                trace_entry["eligibility_field"] = eligibility_field
            trace.append(trace_entry)

        else:
            _resolved_defn, _res_meta = _resolve_rule(
                name, None, current_rules_by_name,
                _hist_rule_sets, period_start, period_end,
                current_rule_set_id, current_rule_set_effective_from,
                rule_floor_dates,
            )
            trace.append({
                "rule":                 name,
                "component":            name,
                "method":               method or "unknown",
                "status":               "not_applied",
                "amount":               "0",
                "result":               None,
                "note":                 f"unrecognised calculation_method: {method!r}",
                "rule_set_id":          _res_meta["rule_set_id"],
                "rule_effective_from":  _res_meta["rule_effective_from"],
                "reference_date":       None,
                "rate_used":            None,
                "resolution_source":    _res_meta["resolution_source"],
                "warning":              _res_meta.get("warning"),
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
    rule_floor_dates: dict[str, str] | None = None,
) -> tuple[dict, dict]:
    """Return (rule_definition_json, resolution_meta) for the given rule.

    Uses the current rule set when reference_date is None or within the
    current period.  Falls back to the most-recently-effective historical
    rule set whose effective_from <= reference_date for cross-period inputs.

    When rule_floor_dates is supplied (strict mode — always populated by the
    production route/executor), a reference_date earlier than the rule's known
    floor raises NoHistoricalRuleVersionError instead of silently falling back
    to the current rule set. rule_floor_dates=None (legacy/test callers)
    preserves the original current_fallback behaviour unchanged.

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

    # No historical rule_set covers this date. Distinguish a backfill gap (shouldn't
    # happen once every historical payroll_rule.effective_from has a snapshot — fall
    # back defensively, as before) from a genuine gap where the rule never existed
    # this far back for this workspace (must fail loudly, per-employee only).
    if rule_floor_dates is not None:
        floor_str = rule_floor_dates.get(rule_name)
        if floor_str is None or ref_str < floor_str:
            raise NoHistoricalRuleVersionError(rule_name, reference_date)

    row = current_rules_by_name.get(rule_name, {})
    return row.get("rule_definition_json") or {}, {
        "rule_set_id":          current_rule_set_id,
        "rule_effective_from":  current_rule_set_effective_from,
        "resolution_source":    "current_fallback",
        "warning":              (
            f"No historical rule set covers reference_date {ref_str}. "
            f"Fell back to current rule set."
        ),
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


def classify_day(work_date, is_ph: bool, config: dict) -> str:
    """Classify a calendar day for OT rate selection (C5 — PH-3).

    Returns one of: 'PUBLIC_HOLIDAY', 'SATURDAY', 'SUNDAY', 'WEEKDAY'.

    Weekend PH precedence is governed by workspace config fields:
      saturday_ph_rule — 'PH_TAKES_PRECEDENCE' | 'SATURDAY_TAKES_PRECEDENCE'
      sunday_ph_rule   — 'PH_TAKES_PRECEDENCE' | 'SUNDAY_TAKES_PRECEDENCE'
    """
    dow = work_date.weekday()  # 0=Mon … 6=Sun
    if is_ph:
        if dow == 5:  # Saturday
            rule = config.get("saturday_ph_rule", "PH_TAKES_PRECEDENCE")
            return "PUBLIC_HOLIDAY" if rule == "PH_TAKES_PRECEDENCE" else "SATURDAY"
        elif dow == 6:  # Sunday
            rule = config.get("sunday_ph_rule", "PH_TAKES_PRECEDENCE")
            return "PUBLIC_HOLIDAY" if rule == "PH_TAKES_PRECEDENCE" else "SUNDAY"
        else:
            return "PUBLIC_HOLIDAY"  # Weekday PH — always OT3
    elif dow == 5:
        return "SATURDAY"
    elif dow == 6:
        return "SUNDAY"
    else:
        return "WEEKDAY"
