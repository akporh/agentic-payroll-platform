# Audit Review — Sprint 10 (Client B Gap Closure)
**Date:** 2026-05-01
**Reviewer:** Claude Code (`/auditor` skill)
**Branch:** `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution`

---

## Scope

Calculation changes introduced in Sprint 10:

| Ref | File | Change |
|-----|------|--------|
| CB-1 (GAP-2) | `backend/api/routes/payroll.py:514` | Removed double subtraction of PH weekday dates from working_days — `period_ctx.working_days` already excludes PHs |
| CB-2 (GAP-5) | `backend/domain/payroll/period_context.py:79–82` | CUSTOM period type annualization changed from `365/period_days` (≈13× for Feb 21–Mar 20) to fixed ×12 |
| CB-6 (FIX-4) | `backend/application/payroll_retry_service.py:213–218` | `tax_bands` now uses explicit `Decimal(str(r[n]))` conversion instead of raw DB values |
| CB-7 (WI-04) | `backend/domain/payroll/rule_evaluator.py:317–322` | `fixed_amount` handler falls back to `component_source` salary component when `amount == 0` |

---

## Findings

### AUD-1 — `component_source` Resolution Not Recorded in Trace
**Type:** Observation (improvement recommended)
**Status:** Open
**Location:** `backend/domain/payroll/rule_evaluator.py:327–338`

**Control Gap:** When the CB-7 `component_source` fallback fires, the trace entry records `"rate_used": str(amount)` — the resolved number — but does not record *which* salary component sourced it. An auditor reviewing a `fixed_amount` rule trace sees a non-zero amount with no derivation path.

**Risk:** If a salary component is later amended and a past run is reviewed, the trace cannot prove which salary figure was in effect at the time. A regulator reviewing a PAYE trace would see a number without its source.

**Evidence Required:** The trace entry must include `"component_source"` when the fallback was used, so the derivation is unambiguous.

**Recommended Fix:**
```python
# rule_evaluator.py — fixed_amount trace entry (~line 327)
trace.append({
    ...
    "rate_used":        str(amount),
    "component_source": component_source if (amount != Decimal("0") and component_source) else None,
    ...
})
```

**Roadmap ref:** AUD-1

---

### AUD-2 — Retry Service Does Not Preserve `period_type` for CUSTOM Runs
**Type:** Observation (improvement recommended)
**Status:** Open
**Location:** `backend/application/payroll_retry_service.py:147–151`

**Control Gap:** The retry service calls `build_period_context(period_start, period_end, public_holiday_dates)` without passing `period_type`. Neither the `payroll_run` table (confirmed — no `period_type` column) nor `rules_context_snapshot` stores the original `period_type`. Period type is inferred from the date span on retry.

**After CB-2:** CUSTOM correctly uses ×12 (same as MONTHLY), so the *annualization number* is likely identical on retry for most spans. However, the inference logic can produce FORTNIGHTLY (×26) for spans ≤ 14 days — a CUSTOM 14-day run could retry with the wrong annualization factor.

**Risk:** A 14-day CUSTOM period run retried could produce a materially different PAYE annualization (×26 instead of ×12). The original run's annualization factor is stored in `component_trace_jsonb` per employee but is inaccessible to the retry orchestrator.

**Evidence Required:** `period_type` must be stored at the `payroll_run` level and read back on retry so the period context is reconstructed faithfully.

**Recommended Fix:**
1. Migration: add `period_type VARCHAR(20)` to `payroll_run`.
2. `payroll_retry_service.py`: read `period_type` from the run row and pass to `build_period_context`.

**Roadmap ref:** AUD-2

---

### AUD-3 — Simulate Script Uses Raw DB Mapping for Tax Bands
**Type:** Observation (low urgency)
**Status:** Open
**Location:** `scripts/simulate_payroll_components.py:508`

**Control Gap:** `tax_bands = [dict(b) for b in bands]` uses a raw DB mapping. The production path (`payroll.py:201–204`) and retry path (`payroll_retry_service.py:213–218`) both use explicit `Decimal(str(r[n]))` conversion. While psycopg2 returns `NUMERIC` as Python `Decimal` by default, the simulate script's approach is implicit.

**Risk:** A DB driver upgrade that changes the return type of `NUMERIC` (e.g. to `float`) would leave the simulate script silently using float arithmetic for PAYE band comparisons while the production engine remains correct — undermining the script as a validation tool.

**Recommended Fix:**
```python
tax_bands = [
    {
        "lower_limit": Decimal(str(b["lower_limit"])) if b["lower_limit"] is not None else None,
        "upper_limit": Decimal(str(b["upper_limit"])) if b["upper_limit"] is not None else None,
        "rate":        Decimal(str(b["rate"]))         if b["rate"]        is not None else None,
    }
    for b in bands
]
```

**Roadmap ref:** AUD-3

---

## Passes

| Check | Result | Detail |
|-------|--------|--------|
| NHF key `employee_rate` — all 3 callers | ✅ PASS | `payroll.py:188`, `payroll_retry_service.py:197`, `simulate_payroll.py:639` — identical key |
| Health insurance key `employee_amount` — all 3 callers | ✅ PASS | Consistent across route, retry service, simulate script |
| Development levy key `amount` — all 3 callers | ✅ PASS | Consistent across route, retry service, simulate script |
| CB-6: Tax bands Decimal — retry matches original run | ✅ PASS | Both use `Decimal(str(r[n]))` — original `payroll.py:201–204`, retry `payroll_retry_service.py:213–218` |
| CB-2: Annualization factor captured in trace | ✅ PASS | `sequential_executor.py:559` — `"annualization_factor"` in `_period_context` trace header per employee |
| CB-1: Working days snapshot complete | ✅ PASS | `ph_dates_used`, `ph_source`, `expected_days` captured in `rules_ctx_snapshot` and per-employee trace |
| Decimal throughout calculation path | ✅ PASS | No `float()` in calculation path; `float()` only in API response serialisation |
| Statutory rule version pinning | ✅ PASS | `statutory_rule_id`, `version`, `effective_from` in snapshot; `statutory_effective_date` on `payroll_run` |
| Immutability of APPROVED/PAID runs | ✅ PASS | DB trigger + application guard in place; not touched by Sprint 10 |
| Pre-existing NHF test failures — not a regression | ✅ CONFIRMED | `git stash` confirmed identical failures before Sprint 10; ₦12,500 delta = NHF on ₦500k basic |

---

## Summary

| Type | Count | Items |
|------|-------|-------|
| Finding (blocks sign-off) | 0 | — |
| Observation (improvement recommended) | 3 | AUD-1, AUD-2, AUD-3 |
| Pass | 10 | See table above |

**Sprint 10 closure is unblocked.** No Finding-level gaps introduced by the four calculation changes. AUD-1 should be addressed before external audit or UAT sign-off. AUD-2 before CUSTOM periods are used in production. AUD-3 is low urgency.
