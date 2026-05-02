# Audit Review — Sprint 11 (Track O — Employee Schema, Shift Allowance, Salary Derivation)
**Date:** 2026-05-02
**Reviewer:** Claude Code (`/auditor` skill)
**Branch:** `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution`

---

## Scope

Calculation changes introduced in Sprint 11:

| Ref | File | Change |
|-----|------|--------|
| O2/D6 | `backend/domain/payroll/salary_derivation.py` (NEW) | Grade percentage salary derivation — `total_monthly × pct` per component; grade wins when `total_monthly` non-null |
| O3/D9 | `backend/domain/payroll/rule_evaluator.py` | Shift gate: `ot_multiplier` rules with `basic_daily` base return ₦0 for `shift_type` in `(None, "DAY")` |
| Phase 0 Fix A | `backend/application/payroll_retry_service.py` | `load_inputs_for_run` wired into both retry paths — retried employees now receive original claimed inputs |
| Phase 0 Fix B | `backend/application/payroll_retry_service.py` | `rate_code_map` added to `_build_shared_context` — OT/shift rules no longer hard-fail on retry |
| O1 | `migrations/versions/f1e2d3c4b5a6` | shift_type/state_of_tax/skill_level added to `employee_contract` |
| O2 | `migrations/versions/a2b3c4d5e6f7` | total_monthly/basic_pct/housing_pct/transport_pct/utility_pct added to `grade` |

---

## Findings

### AUD-4 — `shift_type` not recorded in `component_trace_jsonb` header
**Type:** Finding (must fix before shift allowance audit sign-off)
**Status:** Fixed this sprint

**Location:** `backend/domain/payroll/sequential_executor.py:550–568`

**Control Gap:** The `_period_context` trace header recorded `salary_basis` but not `shift_type`. The value that controlled whether an employee received a shift allowance appeared only in the `note` string of a D9-gated rule entry (e.g. `"shift_type='DAY' — not a shift worker"`). Not a dedicated machine-readable field.

**Risk:** An automated audit query cannot filter on `shift_type` from the trace. An auditor verifying why an employee received zero shift allowance must parse a free-text string rather than reading a structured field. The calculation is reproducible by a human from the note, but not by an automated compliance report.

**Evidence Required:** Structured `shift_type` field in the trace header.

**Fix applied:**
```python
# sequential_executor.py — _period_context header
"salary_basis":  ctx.get("salary_basis", "salary_definition_absolute"),
"shift_type":    ctx.get("shift_type"),   # added
```

**Roadmap ref:** AUD-4

---

### AUD-5 — `shift_type` not retained in snapshot; retry reads live DB value
**Type:** Observation (improvement recommended)
**Status:** Open — partial closure via AUD-4 fix

**Location:** `backend/domain/rules/snapshot.py`; `backend/application/payroll_retry_service.py`

**Control Gap:** `build_rules_context_snapshot` stores statutory rules, tax bands, and rule set items — not per-employee `shift_type`. On retry, `shift_type` is re-read live from `employee_contract`. If an employee's shift_type changes between the original run and a retry, the retry will silently produce a different shift allowance with no audit trail distinguishing which value was used when.

**Risk:** Retry reproducibility guarantee (Auditor Check 10) is not fully met for shift allowance. A retried employee could receive a different amount than in the original run.

**Partial closure:** The AUD-4 fix means the original run's trace header now records `shift_type`. An auditor can compare the original trace against the retry trace to detect divergence.

**Full closure:** Retry reads `shift_type` from the original trace rather than live DB. Deferred — larger change.

**Recommended Fix (deferred):**
1. Store per-employee `shift_type` in the original run's persisted results (or read from trace header on retry).
2. Pass the stored value to the retry executor instead of querying `employee_contract`.

**Roadmap ref:** AUD-5

---

## Passes

| Check | Result | Detail |
|-------|--------|--------|
| NHF key `employee_rate` — all callers | ✅ PASS | `payroll.py:225` and `payroll_retry_service.py:200` both use `rules_jsonb.get("nhf", {}).get("employee_rate", "0.025")` — identical |
| Pension key `employee_rate` / `employer_rate` — all callers | ✅ PASS | Consistent across route and retry service |
| `salary_basis` in component trace | ✅ PASS | Recorded in `_period_context` trace header at `sequential_executor.py:565` — auditor can determine derivation path from trace alone |
| D9 trace completeness (gated entries) | ✅ PASS | Trace records `rate_code`, `multiplier`, `base_rate=None`, `quantity`, `amount="0"`, `note` with embedded shift_type value |
| D9 trace completeness (applied entries) | ✅ PASS | `base_rate`, `multiplier`, `quantity`, `amount` all populated; note includes formula `"N units × rate (base) × multiplier"` |
| Grade pct derivation — Decimal throughout | ✅ PASS | `salary_derivation.py` uses `Decimal(str(...))` for all conversions; residual adjustment uses `Decimal("0.01")` quantize with ROUND_HALF_UP |
| Grade pct derivation — D7 residual absorbed | ✅ PASS | Largest component absorbs residual; sum of derived components equals `total_monthly` exactly |
| New schema columns have active read paths | ✅ PASS | All 7 new columns are queried and acted upon (no dead columns) |
| Phase 0 Fix A — inputs on retry | ✅ PASS | `load_inputs_for_run` confirmed imported and called in both FULL_RUN (~483) and PER_EMPLOYEE (~739) retry paths |
| Phase 0 Fix B — rate_code_map on retry | ✅ PASS | `list_rate_codes` confirmed imported; `rate_code_map` in `_build_shared_context` |
| Statutory rule version pinning | ✅ PASS | Not touched by Sprint 11 — carries forward from Sprint 10 PASS |
| Immutability of APPROVED/PAID runs | ✅ PASS | Not touched by Sprint 11 |
| `period_type` in retry | ✅ CONFIRMED PRE-EXISTING | AUD-2 from Sprint 10 — unchanged, still open |

---

## Pre-Existing Open Findings (Carried Forward)

| Ref | Status | Summary |
|-----|--------|---------|
| AUD-1 | Open | `component_source` resolution not recorded in fixed_amount trace |
| AUD-2 | Open | Retry does not preserve `period_type` for CUSTOM runs |
| AUD-3 | Open | Simulate script uses raw DB mapping for tax bands |

---

## Summary

| Type | Count | Items |
|------|-------|-------|
| Finding (blocks sign-off) | 1 | AUD-4 (fixed during review) |
| Observation (improvement recommended) | 1 | AUD-5 |
| Pass | 13 | See table above |

**Sprint 11 closure is unblocked.** AUD-4 was fixed during the review. AUD-5 is a partial-closure observation — accepted for current stage, documented for future sprint. No Finding-level gaps remain open for Sprint 11 items.
