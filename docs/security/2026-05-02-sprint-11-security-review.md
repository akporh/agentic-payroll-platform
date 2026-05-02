# Security Review — Sprint 11 (Track O — Employee Schema, Shift Allowance, Salary Derivation)
**Date:** 2026-05-02
**Reviewer:** Claude Code (`/security` skill)
**Branch:** `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution`

---

## Scope

Changes introduced in Sprint 11 (Track O):

| File | Change |
|------|--------|
| `backend/api/routes/onboarding.py` | O1: shift_type/state_of_tax/skill_level accepted on employee create |
| `backend/api/routes/payroll.py` | Grade bulk load + `derive_salary_components` call; `derivation_error` handling |
| `backend/api/routes/workspace.py` | GET /employees returns 3 new fields; PATCH /contract accepts + patches all 3 |
| `backend/domain/payroll/salary_derivation.py` | NEW pure function — no DB access |
| `backend/domain/payroll/batch_processor.py` | `derivation_error` re-raised inside per-employee error boundary |
| `backend/domain/payroll/rule_evaluator.py` | D9 shift_type gate for basic_daily ot_multiplier rules |
| `backend/application/payroll_retry_service.py` | `derive_salary_components` wired into FULL_RUN and PER_EMPLOYEE retry paths |

---

## Findings

### SEC-S4 — Grade bulk query missing workspace_id filter
**Severity:** Medium
**Status:** Fixed this sprint

**Location:** `backend/api/routes/payroll.py:142–148` (before fix)

**Vulnerable code (before fix):**
```python
SELECT grade_id, total_monthly, basic_pct, housing_pct, transport_pct, utility_pct
FROM grade
WHERE grade_id = ANY(:ids)
```

**Attack vector:** The `grade_ids` list is derived from a workspace-scoped employee query, so cross-workspace grade access is not reachable today. But there was no defence-in-depth — any future change to the upstream employee query could silently expose another tenant's grade configuration (salary percentages, total_monthly).

**Impact:** Grade salary structure (total_monthly, pct splits) from another workspace visible in payroll calculations.

**Fix applied:**
```python
WHERE grade_id = ANY(:ids)
  AND workspace_id = :wid
```

**Roadmap ref:** SEC-S4

---

### SEC-S5 — `state_of_tax` and `skill_level` had no length validation at the API boundary
**Severity:** Medium
**Status:** Fixed this sprint

**Location:** `backend/api/routes/workspace.py:239–240` (`EmployeeContractUpdateSchema`); `backend/api/routes/onboarding.py:537–538`

**Issue:** Both fields were `str | None` with no `max_length`. DB column is `VARCHAR(50)`. An oversized string hits a DB truncation error whose `str(e)` is returned in the response via `raise HTTPException(status_code=400, detail=str(e))`, leaking the column name.

**Impact:** Schema internals in error response; mild DoS vector.

**Fix applied:**
```python
# workspace.py — EmployeeContractUpdateSchema
state_of_tax: str | None = Field(default=None, max_length=50)
skill_level:  str | None = Field(default=None, max_length=50)
```
```python
# onboarding.py — employee loop
if _state_of_tax is not None and len(_state_of_tax) > 50:
    raise Exception(f"Employee '{emp_number}': state_of_tax exceeds 50 characters")
if _skill_level is not None and len(_skill_level) > 50:
    raise Exception(f"Employee '{emp_number}': skill_level exceeds 50 characters")
```

**Roadmap ref:** SEC-S5

---

## Passes (No Finding)

| Check | Result | Notes |
|-------|--------|-------|
| SQL injection — all new queries | ✅ PASS | All use parameterised `text()` with `:param` bindings; no string concatenation |
| `derivation_error` exposure to client | ✅ PASS | Stored in DB `error_message` column; not returned in any API response (run results endpoint omits it) |
| `shift_type` validation at API boundary | ✅ PASS | Validated against `{"DAY", "2_SHIFT", "4_SHIFT"}` in onboarding (line 540) and workspace PATCH (line 326) before DB write; DB CHECK constraint is second layer |
| Decimal integrity — `salary_derivation.py` | ✅ PASS | All arithmetic uses `Decimal(str(...))` throughout; no float operations |
| Workspace scoping — `PATCH /contract` | ✅ PASS | UPDATE gated by `ec.employee_id IN (SELECT employee_id FROM employee WHERE workspace_id = :wid)` |
| Workspace scoping — `GET /employees` | ✅ PASS | `WHERE e.workspace_id = :wid` on the query |
| Workspace scoping — grade query (post-fix) | ✅ PASS | `AND workspace_id = :wid` added |
| No new dependencies | ✅ PASS | No new packages introduced |
| PII in logs | ✅ PASS | No names, salaries, or bank details in any new log statement |
| Secret / credential exposure | ✅ PASS | No new secrets, tokens, or credentials |

---

## Pre-Existing Issues (Not New to Sprint 11)

| Ref | Location | Issue |
|-----|----------|-------|
| SEC-S1 | `onboarding.py:589` | Raw DB exception in `workspace_payroll_config` seed warning — Open |
| SEC-S2 | `onboarding.py:575–586` | No app-level enum validation on workspace_payroll_config fields — Open |
| SEC-S3 | `payroll.py:498` | `import logging` inside hot execution path — Open |
| (unnamed) | workspace.py, payroll.py | `str(e)`/`str(exc)` returned verbatim in 20+ 400-level responses — Open (broad cleanup needed) |
| (unnamed) | `payroll.py:884–896` | `float()` in results response — cosmetic only, no calculation impact — Low priority |

---

## Summary

| Severity | Count | Items |
|----------|-------|-------|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 2 | SEC-S4 (fixed), SEC-S5 (fixed) |
| Low | 0 (new this sprint) | — |
| Pass | 10 | See table above |

Both Medium findings were fixed during the review. Sprint 11 closure is unblocked.
