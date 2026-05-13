"""
Timesheet Derivation Domain Layer.

Pure computation — no database access, no infrastructure imports.
All monetary/hours values use Decimal throughout.

Entry point: derive_payroll_inputs()
Key helpers: resolve_hours(), classify_day(), is_numeric()

AC references: TM-3-AC-7 (resolve_hours), TM-3-AC-8 (day loop),
               TM-3-AC-5 (three-step cap formula)
"""

from __future__ import annotations

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


# ---------------------------------------------------------------------------
# Day classification
# ---------------------------------------------------------------------------

class DayType(enum.Enum):
    WEEKDAY            = "WEEKDAY"
    SATURDAY_DAY_SHIFT = "SATURDAY_DAY_SHIFT"
    PUBLIC_HOLIDAY     = "PUBLIC_HOLIDAY"


def classify_day(d: date, shift_type: str, ph_date_set: set[date]) -> DayType:
    """Classify a calendar day for OT routing.

    Precedence: PUBLIC_HOLIDAY > SATURDAY (DAY shift only) > WEEKDAY.
    For rotating-shift employees (non-DAY), Saturday accumulates toward
    the OT1 threshold like any other weekday (TM-3-AC-8).
    """
    if d in ph_date_set:
        return DayType.PUBLIC_HOLIDAY
    if d.weekday() == 5 and shift_type == "DAY":
        return DayType.SATURDAY_DAY_SHIFT
    return DayType.WEEKDAY


# ---------------------------------------------------------------------------
# Cell helpers
# ---------------------------------------------------------------------------

def is_numeric(cell: Any) -> bool:
    """Return True if cell can be interpreted as a non-negative number of hours."""
    if cell is None:
        return False
    try:
        val = float(str(cell))
        return val >= 0
    except (ValueError, TypeError):
        return False


def resolve_hours(cell: Any, policy: dict | None, hours_per_day: Decimal) -> Decimal:
    """Compute the hours value for a single attendance cell (TM-3-AC-7).

    | Cell value  | Policy state              | Result                          |
    |-------------|---------------------------|---------------------------------|
    | None / ''   | —                         | Decimal('0')                    |
    | Numeric     | —                         | Decimal(str(cell)) — face value |
    | Leave code  | hours_equivalent set      | Decimal(hours_equivalent)       |
    | Leave code  | unit_fraction set         | unit_fraction × hours_per_day   |
    | Leave code  | both NULL                 | Decimal('0')                    |
    | Leave code  | no policy row             | raises ValueError               |
    """
    if cell is None or cell == "":
        return Decimal("0")
    if is_numeric(cell):
        return Decimal(str(cell))
    if policy is None:
        raise ValueError(f"No policy configured for attendance code: {cell!r}")
    if policy["hours_equivalent"] is not None:
        return Decimal(str(policy["hours_equivalent"]))
    if policy["unit_fraction"] is not None:
        return (Decimal(str(policy["unit_fraction"])) * hours_per_day).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    return Decimal("0")


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class DerivationSummary:
    expected_hours:        Decimal
    actual_hours:          Decimal
    paid_hours_accumulator: Decimal
    total_hours_accumulated: Decimal
    excess_ot1_hours:      Decimal
    total_hours_paid:      Decimal
    proration_factor:      Decimal
    shift_days_worked:     int
    ot_buckets:            dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "expected_hours":          float(self.expected_hours),
            "actual_hours":            float(self.actual_hours),
            "paid_hours_accumulator":  float(self.paid_hours_accumulator),
            "total_hours_accumulated": float(self.total_hours_accumulated),
            "excess_ot1_hours":        float(self.excess_ot1_hours),
            "total_hours_paid":        float(self.total_hours_paid),
            "proration_factor":        float(self.proration_factor),
            "shift_days_worked":       self.shift_days_worked,
            "ot_buckets":              {k: float(v) for k, v in self.ot_buckets.items()},
        }


# ---------------------------------------------------------------------------
# OT trigger config helpers
# ---------------------------------------------------------------------------

_TRIGGER_TYPE_OT1 = "EXCESS_HOURS"
_TRIGGER_TYPE_OT2 = "SATURDAY"
_TRIGGER_TYPE_OT3 = "PUBLIC_HOLIDAY"


def _resolve_ot_rate_codes(ot_trigger_config: list[dict]) -> tuple[str, str, str]:
    """Extract OT1/OT2/OT3 rate codes from workspace ot_trigger_config.

    Returns (ot1_code, ot2_code, ot3_code). Falls back to platform defaults
    OT001/OT002/OT003 if a trigger type is absent from the workspace config.
    """
    ot1 = ot2 = ot3 = None
    for rule in ot_trigger_config:
        trigger_type = rule.get("trigger_type", "")
        if trigger_type == _TRIGGER_TYPE_OT1:
            ot1 = rule.get("rate_code")
        elif trigger_type == _TRIGGER_TYPE_OT2:
            ot2 = rule.get("rate_code")
        elif trigger_type == _TRIGGER_TYPE_OT3:
            ot3 = rule.get("rate_code")
    return (
        ot1 or "OT001",
        ot2 or "OT002",
        ot3 or "OT003",
    )


# ---------------------------------------------------------------------------
# Main derivation function
# ---------------------------------------------------------------------------

def derive_payroll_inputs(
    attendance_grid:     dict,        # {date_str_or_date: cell_value}
    attendance_policies: dict,        # {client_code: policy_dict} — pre-fetched and validated
    ot_trigger_config:   list[dict],  # [{trigger_type, rate_code}]
    ph_date_set:         set[date],
    shift_type:          str,
    contract_window:     tuple[date, date],  # (active_start, active_end) — already clamped
    hours_per_day:       Decimal,
    expected_hours:      Decimal,
) -> tuple[list[dict], DerivationSummary]:
    """Derive payroll_input dicts from a raw attendance grid.

    The caller (timesheet_derivation_service) is responsible for:
    - Pre-fetching and validating all attendance policies before calling this.
    - Clamping contract_window to the period (H1).
    - Resolving hours_per_day per employee shift_type (C1).

    This function performs NO database access.

    Returns:
        (payroll_input_dicts, DerivationSummary)

    payroll_input_dicts: one dict per OT rate code with hours > 0, plus one
        shift_days_worked dict. Each dict has keys: input_code, input_category,
        quantity (Decimal), source='TIMESHEET'.
    """
    # Normalise grid keys to date objects
    normalised_grid: dict[date, Any] = {}
    for k, v in attendance_grid.items():
        if isinstance(k, date):
            normalised_grid[k] = v
        else:
            try:
                normalised_grid[date.fromisoformat(str(k))] = v
            except ValueError:
                pass  # skip malformed date keys

    ot1_code, ot2_code, ot3_code = _resolve_ot_rate_codes(ot_trigger_config)

    active_start, active_end = contract_window
    active_window_days = [
        active_start + timedelta(days=i)
        for i in range((active_end - active_start).days + 1)
    ]

    # Accumulators — all Decimal
    actual_hours            = Decimal("0")
    paid_hours_accumulator  = Decimal("0")
    shift_days_worked       = 0
    ot_buckets: dict[str, Decimal] = defaultdict(Decimal)

    for day in active_window_days:
        day_type = classify_day(day, shift_type, ph_date_set)
        cell = normalised_grid.get(day)

        if day_type == DayType.PUBLIC_HOLIDAY:
            # PH hours go directly to OT3; excluded from base-pay accumulation
            ph_hours = resolve_hours(cell, attendance_policies.get(str(cell)) if cell and not is_numeric(cell) else None, hours_per_day)
            if ph_hours > Decimal("0"):
                ot_buckets[ot3_code] += ph_hours
            continue

        if day_type == DayType.SATURDAY_DAY_SHIFT:
            # Saturday for DAY shift goes to OT2
            sat_hours = resolve_hours(cell, attendance_policies.get(str(cell)) if cell and not is_numeric(cell) else None, hours_per_day)
            if sat_hours > Decimal("0"):
                ot_buckets[ot2_code] += sat_hours
            continue

        # WEEKDAY (including Saturday for rotating shifts)
        if cell is None or cell == "":
            continue

        if is_numeric(cell):
            actual_hours      += Decimal(str(cell))
            shift_days_worked += 1
        else:
            code   = str(cell)
            policy = attendance_policies.get(code)
            # KeyError is impossible here — pre-fetch in the service layer validated all codes
            hours  = resolve_hours(cell, policy, hours_per_day)

            if policy and policy.get("counts_as_paid"):
                paid_hours_accumulator += hours

            if policy and policy.get("eligible_for_shift_allowance"):
                shift_days_worked += 1

    # Three-step cap formula (TM-3-AC-5)
    total_hours_accumulated = actual_hours + paid_hours_accumulator
    excess_ot1              = max(Decimal("0"), total_hours_accumulated - expected_hours)
    total_hours_paid        = total_hours_accumulated - excess_ot1  # always <= expected_hours

    if expected_hours > Decimal("0"):
        proration_factor = (total_hours_paid / expected_hours).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
    else:
        proration_factor = Decimal("1.0000")

    if excess_ot1 > Decimal("0"):
        ot_buckets[ot1_code] += excess_ot1

    summary = DerivationSummary(
        expected_hours=expected_hours,
        actual_hours=actual_hours,
        paid_hours_accumulator=paid_hours_accumulator,
        total_hours_accumulated=total_hours_accumulated,
        excess_ot1_hours=excess_ot1,
        total_hours_paid=total_hours_paid,
        proration_factor=proration_factor,
        shift_days_worked=shift_days_worked,
        ot_buckets=dict(ot_buckets),
    )

    # Build payroll_input dicts
    payroll_inputs: list[dict] = []

    for rate_code, hours in ot_buckets.items():
        if hours > Decimal("0"):
            payroll_inputs.append({
                "input_code":     rate_code,
                "input_category": "EARNING",
                "quantity":       hours,
                "source":         "TIMESHEET",
            })

    # Shift allowance row (consumed by ot_multiplier rule on basic_daily)
    payroll_inputs.append({
        "input_code":     "shift_days_worked",
        "input_category": "EARNING",
        "quantity":       Decimal(str(shift_days_worked)),
        "source":         "TIMESHEET",
    })

    return payroll_inputs, summary
