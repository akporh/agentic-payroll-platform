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
