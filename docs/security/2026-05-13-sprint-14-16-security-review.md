# Security Review — Sprints 14 & 16 (Hire Proration Config + Timesheet Layer)
**Date:** 2026-05-13  
**Reviewer:** Claude Code (`/security` skill)  
**Branch:** `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution`

---

## Scope

### Sprint 14 — Workspace-configurable hire proration + WorkspaceConfig P2 fix

| File | Change |
|------|--------|
| `backend/api/routes/payroll.py` | `proration_strategy` reconciliation from dedicated column into `client_meta` |
| `backend/api/routes/workspace.py` | `PATCH /{wid}/component-overrides/{code}` — accepts `proration_strategy` field |
| `backend/application/payroll_retry_service.py` | `proration_strategy` propagated through retry paths |
| `backend/domain/payroll/executor.py` | `proration_strategy` read from `client_meta` per component |
| `backend/domain/payroll/sequential_executor.py` | `proration_strategy` read from `client_meta` per component |

### Sprint 16 — Timesheet derivation layer (TM-1 through TM-7, C1, C2)

| File | Change |
|------|--------|
| `backend/api/routes/payroll.py` | 5 new timesheet endpoints (upload, derive, approve, status, audit) |
| `backend/api/routes/workspace.py` | 4 new attendance config endpoints (GET/POST codes, PATCH code, PATCH policy) |
| `backend/application/payroll_readiness_service.py` | C2 timesheet completeness gate |
| `backend/application/timesheet_derivation_service.py` | NEW — orchestrates upload, derivation, approval |
| `backend/domain/payroll/timesheet_derivation.py` | NEW — pure domain derivation logic |
| `backend/infra/repositories/attendance_config_repo.py` | NEW — workspace-scoped attendance code/policy queries |
| `backend/infra/repositories/timesheet_repo.py` | NEW — workspace-scoped timesheet entry CRUD |
| `backend/infra/repositories/payroll_input_repo.py` | `source` column added to load/delete paths |
| `backend/infra/repositories/workspace_config_repo.py` | `timesheet_enabled` added |
| `requirements.txt` | `python-multipart` added (unpinned) |

---

## Findings

### SEC-S5 — `proration_strategy` accepted arbitrary string — no enum validation
**Severity:** Medium  
**Status:** Fixed 2026-05-13  
**Sprint:** 14

**Location:** `backend/api/routes/workspace.py` — `PATCH /{workspace_id}/component-overrides/{component_code}`

**Description:** `proration_strategy` was accepted from the request payload and written directly to `client_component_metadata.proration_strategy VARCHAR(50)` with no API-level validation and no DB CHECK constraint. The executor reads this value back and silently falls back to its default proration method for any unrecognised string — producing wrong proration with no observable error.

**Fix applied:** Guard added before the DB session in `patch_component_override`. Rejects any value not in `{"calendar_days", "fixed_30", "work_days"}` with HTTP 422 before any DB interaction.

```python
_VALID_PRORATION_STRATEGIES = {"work_days", "calendar_days", "fixed_30"}
strategy = payload.get("proration_strategy")
if strategy is not None and strategy not in _VALID_PRORATION_STRATEGIES:
    raise HTTPException(
        status_code=422,
        detail=f"proration_strategy must be one of {sorted(_VALID_PRORATION_STRATEGIES)}.",
    )
```

**Remaining gap:** No DB-level CHECK constraint on `client_component_metadata.proration_strategy`. A future migration should add: `CHECK (proration_strategy IS NULL OR proration_strategy IN ('work_days', 'calendar_days', 'fixed_30'))`. Logged as a low-priority hardening item.

---

### SEC-S6 — Missing `max_length` on attendance code schema fields
**Severity:** Medium  
**Status:** Fixed 2026-05-13  
**Sprint:** 16

**Location:** `backend/api/routes/workspace.py` — `AttendanceCodeCreateSchema`, `AttendanceCodePatchSchema`

**Description:** `client_code: str` mapped to `VARCHAR(20)` and `description: str | None` mapped to `VARCHAR(200)` with no `max_length` constraints in the Pydantic schemas. An oversized value would reach the DB, trigger a PG truncation error, and leak the column name and type via `str(exc)` in the 400 response.

**Fix applied:**

```python
class AttendanceCodeCreateSchema(BaseModel):
    client_code: str = Field(..., max_length=20)
    description: str | None = Field(default=None, max_length=200)

class AttendanceCodePatchSchema(BaseModel):
    description: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None
```

Pydantic now rejects oversized values at the route boundary with a structured 422 before any DB interaction.

---

### SEC-S7 — `str(exc)` leaked DB constraint names in attendance code create/patch
**Severity:** Medium  
**Status:** Fixed 2026-05-13  
**Sprint:** 16

**Location:** `backend/api/routes/workspace.py:1530` (create), `workspace.py:1568` (patch)

**Description:** Both attendance code handlers wrapped the repo calls in `except Exception as exc: raise HTTPException(status_code=400, detail=str(exc))`. A duplicate `client_code` (unique constraint violation) or a bad `hours_equivalent` value (CHECK constraint violation) would return the raw PostgreSQL error string, exposing table name, constraint name, and offending value to the caller.

**Fix applied:** Exception logged server-side; generic message returned to client.

```python
except Exception as exc:
    import logging as _logging
    _logging.getLogger(__name__).error("create_attendance_code failed: %s", exc)
    raise HTTPException(status_code=400, detail="Failed to create attendance code.")
```

---

## Checks Passed (No Issues Found)

| Check | Result |
|---|---|
| Workspace scoping — all Sprint 16 attendance/timesheet repo queries | PASS — every query has `WHERE workspace_id = :wid` |
| Workspace scoping — `payroll_readiness_service` timesheet gate | PASS — scoped through `workspace_config_repo` and `timesheet_repo` |
| `timesheet_derivation.py` — no infra imports | PASS — stdlib only; pure domain |
| Decimal used for all financial calculations in derivation domain | PASS — `float()` in `is_numeric()` (validation only) and `to_dict()` (serialisation only); no float in accumulators or formula |
| `hours_equivalent` / `unit_fraction` negative-value protection | PASS — DB `CHECK (hours_equivalent > 0)` and `CHECK (unit_fraction > 0 AND unit_fraction <= 1)` enforce at DB level |
| `category` immutability enforced at API boundary | PASS — `workspace.py` rejects any payload containing `category` key |
| `counts_as_paid=False + counts_towards_ot_threshold=True` rejected | PASS — checked at both create and patch, merged with existing policy state |
| `patch_attendance_code` allowlist enforced | PASS — `unknown = set(payload.keys()) - allowed` rejects any unlisted field |
| Bulk queries scoped by workspace (Sprint 11 retro pattern) | PASS — no `= ANY(:ids)` pattern in Sprint 16 attendance/timesheet repos |
| SQL injection — parameterised queries throughout | PASS — no string concatenation into SQL found in Sprint 14 or 16 changes |
| Sprint 14 proration reconciliation logic in run build | PASS — existing strategy values read safely via `client_meta[code].get("proration_strategy")` |

---

## Low Findings (Accepted / Deferred)

| # | Severity | Finding | Decision |
|---|---|---|---|
| L1 | Low | No file size cap on timesheet upload (`POST /workspaces/{wid}/timesheet/upload`) — large Excel files load fully into memory | Accepted for now; add `MAX_UPLOAD_BYTES = 10 MB` guard before Client B scales to more than 5 concurrent uploads |
| L2 | Low | `python-multipart` unpinned in `requirements.txt` (installed at 0.0.28, safe) | Pin to `==0.0.28` in next dependency update pass |
| L3 | Low | No DB CHECK constraint on `proration_strategy` column (API-level guard added by SEC-S5) | Add CHECK constraint in a future hardening migration |

---

## Pre-existing Pattern (Not a Regression)

`str(e)` in HTTP 400 responses exists at 9 other locations in `workspace.py` (lines 85, 172, 324, 416, 934, 1032, 1057, 1082, 1178) and throughout `payroll.py`. These were present before Sprint 14/16 and are not regressions from these sprints. Should be addressed globally in a dedicated hardening pass — log raw exception server-side, return generic string to client.

---

## Summary

| Finding | Severity | Sprint | Status |
|---|---|---|---|
| SEC-S5 — `proration_strategy` no enum validation | Medium | 14 | Fixed |
| SEC-S6 — Missing `max_length` on attendance code schema fields | Medium | 16 | Fixed |
| SEC-S7 — `str(exc)` leaks DB constraint names in attendance create/patch | Medium | 16 | Fixed |
| L1 — No file size cap on timesheet upload | Low | 16 | Deferred |
| L2 — `python-multipart` unpinned | Low | 16 | Deferred |
| L3 — No DB CHECK on `proration_strategy` | Low | 14 | Deferred |

All medium findings resolved. No critical or high findings. Safe to proceed to Client B staging.
