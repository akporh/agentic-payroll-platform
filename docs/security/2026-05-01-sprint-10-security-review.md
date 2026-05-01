# Security Review — Sprint 10 (Client B Gap Closure)
**Date:** 2026-05-01
**Reviewer:** Claude Code (`/security` skill)
**Branch:** `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution`

---

## Scope

Changes introduced in Sprint 10 (Client B gap closure):

| File | Change |
|------|--------|
| `backend/api/routes/payroll.py` | CB-1: removed double PH subtraction in AUTOMATIC mode; CB-12: `PH_ADDITIVE` graceful fallback with WARN log |
| `backend/api/routes/onboarding.py` | CB-11/WI-06: calls `upsert_workspace_payroll_config()` after `db.commit()` — best-effort, failure adds warning |
| `backend/infra/repositories/workspace_config_repo.py` | `upsert_workspace_payroll_config()` function (new); uses parameterised SQL with ON CONFLICT upsert |

---

## Findings

### SEC-S1 — Information Disclosure via Raw Exception in API Response
**Severity:** Medium
**Status:** Open
**Location:** `backend/api/routes/onboarding.py:589`

**Vulnerable code:**
```python
except Exception as _wpc_err:
    warnings.append(f"workspace_payroll_config seed failed: {_wpc_err!s}")
```

**Attack vector:** A caller submits an invalid enum value for a `workspace_payroll_config` field (e.g. `"ph_mode": "INVALID"`). The DB CHECK constraint fires. The raw PostgreSQL error — `new row for relation "workspace_payroll_config" violates check constraint "ck_wpc_ph_mode"` — is serialised into the `warnings` array and returned in the HTTP response body.

**Impact:** Leaks internal table names (`workspace_payroll_config`), constraint names (`ck_wpc_ph_mode`), and column names. Reduces attacker effort to enumerate the DB schema. In a multi-tenant deployment this information assists lateral enumeration attempts.

**Fix:**
```python
except Exception as _wpc_err:
    logger.warning(
        "workspace_payroll_config seed failed for workspace %s: %s",
        workspace_id, _wpc_err,
    )
    warnings.append(
        "workspace_payroll_config seed failed — payroll config was not applied. "
        "Contact your administrator."
    )
```

**Roadmap ref:** SEC-S1

---

### SEC-S2 — No Application-Level Enum Validation on `workspace_payroll_config` Fields
**Severity:** Low
**Status:** Open
**Location:** `backend/api/routes/onboarding.py:575–586`

**Issue:** `ph_mode`, `saturday_ph_rule`, `sunday_ph_rule`, `d3_leave_overlap_rule`, and `d4_absence_rule` are passed directly from the request payload to the repo without any application-layer allowlist check. DB CHECK constraints are the only guard.

**Impact:** Invalid values produce a raw DB error (see SEC-S1 above). Triggering this is trivially easy — any unexpected enum value in the `workspace_payroll_config` block of the onboarding payload hits the path. Combined with SEC-S1, this is a reliable schema enumeration vector.

**Fix:** Add an allowlist check before calling `upsert_workspace_payroll_config`:
```python
_VALID_PH_MODES = {"AUTOMATIC", "FILE_BASED"}
_VALID_SAT_RULES = {"PH_TAKES_PRECEDENCE", "DAY_OF_WEEK_TAKES_PRECEDENCE"}
_VALID_SUN_RULES = {"PH_TAKES_PRECEDENCE", "DAY_OF_WEEK_TAKES_PRECEDENCE"}
_VALID_D3 = {"LEAVE_ABSORBS_PH", "PH_ADDITIVE"}
_VALID_D4 = {"ABSENT_IS_DEDUCTIBLE", "PH_EXCUSES_ABSENCE"}

def _coerce_enum(value, valid_set, field_name, warnings_list):
    if value and value not in valid_set:
        warnings_list.append(f"Unknown {field_name} '{value}' — ignored.")
        return None
    return value or None
```

**Roadmap ref:** SEC-S2

---

### SEC-S3 — `import logging` Inside Hot Execution Path
**Severity:** Low (code quality, not directly exploitable)
**Status:** Open
**Location:** `backend/api/routes/payroll.py:498`

**Issue:** `import logging as _logging` is placed inside `run_payroll()` — a function called on every payroll run. Python caches modules so this is not a performance cliff, but it signals a missing module-level logger and creates inconsistency with the rest of the module's logging pattern.

**Fix:** Add to module-level imports:
```python
import logging
logger = logging.getLogger(__name__)
```
Then replace `_logging.getLogger(__name__).warning(...)` with `logger.warning(...)`.

**Roadmap ref:** SEC-S3

---

## Passes (No Finding)

| Check | Result | Notes |
|-------|--------|-------|
| Workspace scoping — `upsert_workspace_payroll_config` | ✅ PASS | All writes/reads bound to `:wid`; ON CONFLICT key is `(workspace_id, effective_from)` — cross-workspace write not possible |
| SQL injection — `workspace_config_repo.py` | ✅ PASS | All SQL uses `text()` with named parameters; no string concatenation |
| SQL injection — `payroll.py` (CB-1, CB-12 paths) | ✅ PASS | No new raw SQL introduced |
| Decimal integrity — calculation path | ✅ PASS | Monetary values use `Decimal` throughout execution; `float()` only in API response serialisation (display layer) |
| PII in logs — PH_ADDITIVE fallback | ✅ PASS | Warning log at `payroll.py:500` logs `workspace_id` (UUID) only; no names, salaries, or bank details |
| Secret / credential exposure | ✅ PASS | No new secrets, tokens, or credentials introduced |
| Workspace existence check — onboarding commit | ✅ PASS | `SELECT 1 FROM workspace WHERE workspace_id = :wid` at `onboarding.py:197–200` before any write |

---

## Pre-Existing Architecture Notes (Not New to Sprint 10)

These are not regressions introduced by Sprint 10 but are worth recording for future audit reference:

- **No authentication middleware** on `/onboarding/commit` or `/payroll/run` — `workspace_id` comes from the request payload, not a signed session or token. This is the current architecture (Phase 3: RBAC deferred as P4-5). All routes are implicitly trusted-network-only.
- **`float()` in API response serialisation** — `payroll.py:756–860` converts Decimal to float for JSON output. Calculation is Decimal-safe; this only affects display precision in the response body.

---

## Summary

| Severity | Count | Items |
|----------|-------|-------|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 1 | SEC-S1 |
| Low | 2 | SEC-S2, SEC-S3 |
| Pass | 7 | See table above |

No Sprint 10 change introduced a Critical or High severity issue. Sprint closure is unblocked. The three findings are straightforward and can be addressed in the next sprint or batched into Track S.
