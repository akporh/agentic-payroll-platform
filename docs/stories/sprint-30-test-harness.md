# Sprint 30 — Test Harness Setup

## Goal
Establish the test infrastructure (fixtures, test database, configuration) that Sprint 31+ test suites will run inside. No feature tests written in this sprint — only the scaffold.

## Background
`pytest.ini` and a `tests/` directory already exist. Pure-Python unit tests for the calculator already run. This sprint adds the missing layer: a test database with lifecycle management and reusable fixtures so that API-level and migration-level tests can be written in subsequent sprints.

---

## HARN-1 — Test Database + Base Fixtures · P1

**As the developer,**
**I want a test database that spins up and tears down cleanly,**
**So that integration and migration tests can run in CI without affecting production data.**

### Acceptance Criteria
- `conftest.py` at repo root defines:
  - `db_engine` fixture — creates a test Postgres DB (or SQLite for speed), runs `alembic upgrade head`, tears down after session
  - `db_session` fixture — transaction-scoped, rolls back after each test
  - `workspace` fixture — a seeded test workspace
  - `employee` fixture — a seeded test employee linked to workspace
- `pytest tests/ -x` passes in CI with no manual setup
- No test touches the production `DATABASE_URL`
- `TEST_DATABASE_URL` env var controls the test DB connection (defaults to SQLite for local, Postgres for CI)

### Out of Scope
- Writing actual feature tests (Sprint 31+)
- Performance/load testing
- Test data factories (simple fixtures are enough for now)

---

## Notes
- SQLite is acceptable for unit/integration tests that don't use Postgres-specific features (jsonb, etc.)
- For migration smoke tests (Sprint 32), a real Postgres instance is required — GitHub Actions `services.postgres` block handles this in CI
