# Sprint 32 — API Route & Migration Tests

## Goal
Add integration tests for the highest-risk API routes and a migration smoke test that runs upgrade + downgrade on a clean database. Requires the test harness from Sprint 30.

## Dependency
Sprint 30 (test harness) must be complete before this sprint starts.

---

## TEST-B1 — API Route Integration Tests · P1

**As the developer,**
**I want integration tests for key API routes,**
**So that route-level bugs (serialization errors, workspace scoping gaps, 500s) are caught before they reach production.**

### Acceptance Criteria
- Tests use `httpx.AsyncClient` with the FastAPI `app` and the test DB session from Sprint 30 fixtures
- Routes covered (minimum):
  - `POST /api/v1/payroll/run` — creates a run, returns run ID
  - `GET /api/v1/employees` — returns employees scoped to workspace (not another workspace's employees)
  - `POST /api/v1/inputs/bulk` — bulk upload succeeds; duplicate inputs are idempotent
  - `PATCH /api/v1/employees/{id}` — update succeeds; workspace scoping prevents cross-workspace update
- Each test asserts HTTP status code and key response fields
- Each test asserts workspace isolation (a request with workspace A credentials cannot access workspace B data)

### Out of Scope
- Full end-to-end payroll pipeline via API (covered by existing `test_payroll_pipeline_e2e.py`)
- Authentication flow tests (no auth layer yet)

---

## TEST-C1 — Migration Smoke Tests · P2

**As the developer,**
**I want CI to verify that every migration upgrades and downgrades cleanly,**
**So that broken migrations are caught before they run against the production database.**

### Acceptance Criteria
- CI job runs `alembic upgrade head` against a clean Postgres test DB (GitHub Actions `services.postgres`)
- CI job then runs `alembic downgrade base`
- Both complete without error
- Job fails and blocks merge if either step errors
- Test is idempotent — can run on any branch without leaving state behind

### Out of Scope
- Data migration correctness tests (schema shape only)
- Migration performance testing

---

## API-SEC-1 — Sanitise 409 Response on Duplicate Payroll Run · P1

**As an operator,**
**I want the API to return a clean error message when a duplicate payroll run is attempted,**
**So that internal DB constraint names and table structure are not exposed in the HTTP response.**

### Background
`POST /{workspace_id}/payroll/run` currently returns the raw PostgreSQL constraint violation message in the 409 detail when a run for the same period already exists:
```
"Duplicate payroll run detected (idempotency_key or period conflict): duplicate key value violates unique constraint \"uq_payroll_run_regular\"\nDETAIL:  Key (workspace_id, period_start, period_end)=(...) already exists."
```
This violates the standing route rule: *never return `str(e)` in an HTTP response* (CLAUDE.md).

### Acceptance Criteria
- `POST /{workspace_id}/payroll/run` returns `{"detail": "A payroll run already exists for this period."}` with status 409 when the period unique constraint fires
- No DB constraint name, table name, or column value appears in any API response
- The existing frontend 409 handler (`setError('A run for this period already exists — view it in the Runs list.')`) continues to work unchanged
- The fix is applied in `create_draft_payroll_run` (repo layer) or the route handler — whichever is closest to where the raw exception is caught

### Out of Scope
- Changes to the unique constraint itself
- Frontend changes

---

## DEFER-1 — Shared `dateUtils.ts` frontend utility · P2

**Identified during:** Sprint 33 `/simplify` pass (PayrollRule publish flow)

`getTomorrow()` and the `new Date().toISOString().slice(0, 10)` today-string pattern are duplicated across at least 5 files:
- `frontend/src/pages/WorkspaceConfig.tsx`
- `frontend/src/pages/RunPayroll.tsx`
- `frontend/src/pages/WorkspaceSetup.tsx`
- `frontend/src/pages/EmployeeUpload.tsx` (approx)
- `frontend/src/utils/nativeExcelParser.ts`

**Proposed fix:** Create `frontend/src/utils/dateUtils.ts` exporting `today()` and `tomorrow()`. Update all callers. Purely mechanical — no logic change.

---

## DEFER-2 — Shared `get_latest_rule_set` backend repo function · P2

**Identified during:** Sprint 33 `/simplify` pass (PayrollRule publish flow)

The query `SELECT rule_set_id, effective_from FROM rule_set WHERE workspace_id = :wid ORDER BY effective_from DESC, created_at DESC LIMIT 1` (with tiebreaking on `created_at`) exists in at least two places:
- `backend/api/routes/payroll.py` (lines ~355–362)
- `backend/api/routes/workspace.py` (inside the drift CTE)

**Proposed fix:** Extract into `backend/infra/repositories/rule_set_repo.py` as `get_latest_rule_set(db, workspace_id)`. Update both callers. The tiebreaking logic (`created_at DESC`) must not drift between callers — a shared function is the only safe guarantee.
