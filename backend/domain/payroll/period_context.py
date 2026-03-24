"""
Period Context.

Encapsulates all period-related facts for a single payroll run.
Created once at the API layer and injected into the execution context
so that the pure domain layer can derive correct working_days,
annualization factors, and proration divisors without re-reading the DB.
"""

from __future__ import annotations

import calendar
import datetime
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class PeriodType(str, Enum):
    MONTHLY     = "MONTHLY"
    FORTNIGHTLY = "FORTNIGHTLY"
    CUSTOM      = "CUSTOM"


@dataclass(frozen=True)
class PeriodContext:
    period_start:         date
    period_end:           date
    period_type:          PeriodType
    calendar_days:        int
    working_days:         int      # actual Mon–Fri count within the period
    annualization_factor: Decimal  # 12 / 26 / (365 / calendar_days)
    period_fraction:      Decimal  # 1 / annualization_factor


def _count_working_days(start: date, end: date) -> int:
    """Count Mon–Fri days between start and end inclusive."""
    total = 0
    current = start
    while current <= end:
        if current.weekday() < 5:   # 0=Mon … 4=Fri
            total += 1
        current += datetime.timedelta(days=1)
    return max(1, total)


# Maps values stored in pay_cycle.frequency (and common aliases) to PeriodType.
# Unrecognised values fall through to CUSTOM.
_FREQUENCY_ALIASES: dict[str, PeriodType] = {
    "monthly":     PeriodType.MONTHLY,
    "biweekly":    PeriodType.FORTNIGHTLY,
    "fortnightly": PeriodType.FORTNIGHTLY,
    "weekly":      PeriodType.CUSTOM,
    "custom":      PeriodType.CUSTOM,
}


def _resolve_period_type(raw: str) -> PeriodType:
    """Normalise a raw period_type string to a PeriodType.

    Accepts PeriodType enum values ("MONTHLY", "FORTNIGHTLY", "CUSTOM") and
    pay_cycle.frequency values ("monthly", "biweekly", "weekly") interchangeably.
    Unrecognised values resolve to CUSTOM rather than raising.
    """
    key = raw.strip().lower()
    if key in _FREQUENCY_ALIASES:
        return _FREQUENCY_ALIASES[key]
    # Try direct enum match (e.g. "MONTHLY", "FORTNIGHTLY")
    try:
        return PeriodType(raw.upper())
    except ValueError:
        return PeriodType.CUSTOM


_DEFAULT_ANNUALIZATION: dict[PeriodType, Decimal] = {
    PeriodType.MONTHLY:     Decimal("12"),
    PeriodType.FORTNIGHTLY: Decimal("26"),
}

# Maximum calendar days permitted per period type.
# CUSTOM has no cap — the caller has explicitly opted in to a non-standard span.
_MAX_CALENDAR_DAYS: dict[PeriodType, int] = {
    PeriodType.MONTHLY:     31,
    PeriodType.FORTNIGHTLY: 15,
}


def compute_hire_termination_factor(
    period: PeriodContext,
    contract_start: date | None,
    contract_end:   date | None,
) -> Decimal:
    """Return the fraction of the period the employee was active, as a Decimal in [0, 1].

    Returns Decimal("1") when the employee was active for the full period
    (no proration needed).

    Mid-period hire:        contract_start falls inside the period.
    Mid-period termination: contract_end falls inside the period.
    Both:                   only the overlap window is counted.

    Args:
        period:         The current PeriodContext.
        contract_start: Employee contract start date (None = pre-dates the period).
        contract_end:   Employee contract end date (None = open-ended).

    Returns:
        Decimal proration factor, rounded to 6 decimal places.
    """
    active_from = max(period.period_start, contract_start) if contract_start else period.period_start
    active_to   = min(period.period_end,   contract_end)   if contract_end   else period.period_end

    if active_to < active_from:
        return Decimal("0")

    if active_from == period.period_start and active_to == period.period_end:
        return Decimal("1")

    days_active = _count_working_days(active_from, active_to)
    if period.working_days == 0:
        return Decimal("1")

    return (Decimal(str(days_active)) / Decimal(str(period.working_days))).quantize(
        Decimal("0.000001")
    )


def build_period_context(
    period_start:          date | str | None = None,
    period_end:            date | str | None = None,
    period_type:           str | None = None,
    working_days_override: int | None = None,
) -> PeriodContext:
    """Derive a PeriodContext from raw API inputs.

    All parameters are optional.  Absent inputs produce a MONTHLY context
    whose working_days is the actual Mon–Fri count of the current month.

    Args:
        period_start:          ISO-format date string or date object.
                               Defaults to the first day of the current month.
        period_end:            ISO-format date string or date object.
                               Defaults to the last day of period_start's month.
        period_type:           One of "MONTHLY", "FORTNIGHTLY", "CUSTOM".
                               Inferred from the calendar span when absent.
        working_days_override: Explicit working-day count.  When absent,
                               the actual Mon–Fri days in the period are counted.

    Returns:
        Immutable PeriodContext.

    Raises:
        ValueError: If period_end precedes period_start.
    """
    today = date.today()

    # --- Resolve dates ---
    if period_start is None:
        start = today.replace(day=1)
    elif isinstance(period_start, str):
        start = date.fromisoformat(period_start)
    else:
        start = period_start

    if period_end is None:
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = start.replace(day=last_day)
    elif isinstance(period_end, str):
        end = date.fromisoformat(period_end)
    else:
        end = period_end

    if end < start:
        raise ValueError(
            f"period_end {end} must not precede period_start {start}"
        )

    cal_days = (end - start).days + 1

    # --- Resolve period type ---
    if period_type is not None:
        ptype = _resolve_period_type(period_type)
    elif 28 <= cal_days <= 31:
        ptype = PeriodType.MONTHLY
    elif 13 <= cal_days <= 15:
        ptype = PeriodType.FORTNIGHTLY
    else:
        ptype = PeriodType.CUSTOM

    # --- Validate period length against type ---
    max_days = _MAX_CALENDAR_DAYS.get(ptype)
    if max_days is not None and cal_days > max_days:
        raise ValueError(
            f"{ptype.value} period cannot exceed {max_days} calendar days "
            f"(got {cal_days} days: {start} to {end}). "
            f"Use period_type=CUSTOM for non-standard spans."
        )

    # --- Resolve working days ---
    if working_days_override is not None:
        wd = int(working_days_override)
    else:
        # Count actual Mon–Fri days in the period for all period types.
        # This gives the real figure (e.g. Feb 2026 = 20, not 22).
        wd = _count_working_days(start, end)

    # --- Resolve annualization factor ---
    if ptype in _DEFAULT_ANNUALIZATION:
        ann = _DEFAULT_ANNUALIZATION[ptype]
    else:
        ann = (Decimal("365") / Decimal(str(cal_days))).quantize(
            Decimal("0.000001")
        )

    fraction = (Decimal("1") / ann).quantize(Decimal("0.000001"))

    return PeriodContext(
        period_start         = start,
        period_end           = end,
        period_type          = ptype,
        calendar_days        = cal_days,
        working_days         = wd,
        annualization_factor = ann,
        period_fraction      = fraction,
    )
