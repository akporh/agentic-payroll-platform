# Local Setup Guide

Step-by-step instructions for standing up the Agentic Payroll Platform locally from scratch.

---

## Prerequisites

| Tool | Minimum version | Notes |
|------|----------------|-------|
| Python | 3.10+ | Uses `match`/`case` and `dataclasses` |
| PostgreSQL | 14+ | Must be running before migrations |
| Node.js | 18+ | For the Vite/React frontend |
| npm | 9+ | Comes with Node 18 |

---

## 1. Clone and install dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

---

## 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in the values:

```dotenv
DATABASE_URL=postgresql://payroll_user:dev_password@localhost:5432/payroll
DB_PASSWORD=dev_password_change_me

# Generate a Fernet key (run once, paste result below)
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=<paste generated key>

# Any random string (used for HMAC signatures)
SECRET_KEY=<paste a random string>

ENVIRONMENT=development
API_PORT=8000
```

**Creating the PostgreSQL database:**

```bash
psql -U postgres -c "CREATE USER payroll_user WITH PASSWORD 'dev_password_change_me';"
psql -U postgres -c "CREATE DATABASE payroll OWNER payroll_user;"
```

---

## 3. Run database migrations

```bash
alembic upgrade head
```

This creates all tables, enums, constraints, and seeds default data (component metadata, proration strategies, etc.).

Verify the migrations applied:

```bash
alembic current
```

---

## 4. Start the backend

```bash
uvicorn backend.api.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.

- Interactive docs (Swagger): `http://localhost:8000/docs`
- Alternative docs (Redoc): `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/api/v1/health`

---

## 5. Start the frontend

```bash
cd frontend && npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API calls to port 8000.

---

## 6. Seed a workspace for development

The platform is workspace-scoped. You need at least one workspace with employees, salary definitions, and a statutory rule before you can run payroll.

### Option A — Use the admin UI (recommended for first-time setup)

1. Open `http://localhost:8000/admin/onboarding` in your browser
2. Upload the onboarding JSON via the UI — this creates the workspace, employees, salary definitions, grades, designations, pay cycle, and component metadata in one shot

A sample onboarding JSON is at `attached_assets/` or in the project data directory.

### Option B — JSON API

```bash
# Preview the onboarding (dry-run, no writes)
curl -X POST http://localhost:8000/api/v1/onboarding/preview \
  -H "Content-Type: application/json" \
  -d @data/sample_onboarding.json

# Commit (writes to DB)
curl -X POST http://localhost:8000/api/v1/onboarding/commit \
  -H "Content-Type: application/json" \
  -d @data/sample_onboarding.json
```

### After onboarding: note your workspace_id

```bash
curl http://localhost:8000/api/v1/workspaces
# Returns [{workspace_id, name, status, ...}]
```

---

## 7. Load grades and employee contracts (if not in onboarding JSON)

```bash
# Load grade definitions from a JSON file
python backend/scripts/load_grades.py <workspace_id> data/grades.json

# Assign employees to grades and salary definitions
python backend/scripts/load_employee_contracts.py <workspace_id> data/contracts.json
```

---

## 8. Activate the workspace

Payroll can only be run when a workspace is in `LIVE` status.

```bash
# Transition the workspace to LIVE
curl -X POST "http://localhost:8000/api/v1/{workspace_id}/transition" \
  -H "Content-Type: application/json" \
  -d '{"to_status": "LIVE"}'
```

---

## 9. Seed payroll inputs (optional — for testing rules)

Payroll inputs are per-period event data (overtime days, absent days, bonuses, etc.) that the rule evaluator consumes before the payroll engine runs.

```bash
# Seeds input rows for up to 5 active employees in a workspace
python scripts/seed_payroll_inputs.py
python scripts/seed_payroll_inputs.py --workspace-id <uuid>
```

---

## 10. Run your first payroll

### Via the frontend

Navigate to `Workspaces → [your workspace] → Payroll → Run Payroll`.

### Via the API

```bash
# 1. Create a payroll run for a period
curl -X POST "http://localhost:8000/api/v1/{workspace_id}/payroll/run" \
  -H "Content-Type: application/json" \
  -d '{
    "period_start": "2026-03-01",
    "period_end":   "2026-03-31",
    "run_type":     "REGULAR"
  }'
# Returns {run_id, status: "DRAFT", ...}

# 2. List runs
curl "http://localhost:8000/api/v1/{workspace_id}/payroll/runs"

# 3. Execute the run
curl -X POST "http://localhost:8000/api/v1/{workspace_id}/payroll/run" \
  -H "Content-Type: application/json" \
  -d '{"payroll_run_id": "<run_id>"}'

# 4. Check results
curl "http://localhost:8000/api/v1/{workspace_id}/payroll/runs/{run_id}/results"

# 5. Reconciliation summary
curl "http://localhost:8000/api/v1/{workspace_id}/payroll/runs/{run_id}/reconciliation"
```

---

## 11. Simulate payroll (no writes — for debugging)

Run the payroll engine for a single employee and print the full calculation trace without writing anything to the database:

```bash
# Uses first active employee in first workspace by default
python backend/scripts/simulate_payroll.py

# Specific employee
python backend/scripts/simulate_payroll.py --employee-number EMP001

# Specific workspace + period
python backend/scripts/simulate_payroll.py \
  --workspace-id <uuid> \
  --employee-number EMP001 \
  --period-start 2026-03-01 \
  --period-end   2026-03-31
```

For a step-through view showing each component's calculation in order:

```bash
python scripts/simulate_stepthrough.py
```

---

## 12. Run the test suite

```bash
# All unit tests (no DB required — runs in ~0.1s)
pytest tests/test_pension.py tests/test_nhf.py tests/test_period_context.py \
       tests/test_rule_evaluator.py tests/test_sequential_executor.py \
       tests/test_calculation_scenarios.py tests/test_paye.py -v

# Full suite (requires PostgreSQL running with migrations applied)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=backend --cov-report=term-missing
```

**Unit tests (no DB needed):**
`test_pension`, `test_nhf`, `test_period_context`, `test_rule_evaluator`,
`test_sequential_executor`, `test_calculation_scenarios`, `test_paye`,
`test_payroll_calculator`, `test_audit_events`, `test_status`, `test_state_machine`,
`test_salary`, `test_result_builder`

**E2E tests (require live DB):**
`test_payroll_pipeline_e2e`, `test_payroll_partial_run_e2e`,
`test_payroll_reconciliation_e2e`, `test_payroll_retry`, `test_workspace_integration`

---

## Payroll run lifecycle

```
DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED → PAID
                           ↑
                      PARTIAL (some employees failed — retry available)
```

A run must reach `CALCULATED` before it can be approved. `APPROVED` → `LOCKED` is
irreversible. Only `LOCKED` runs can be marked `PAID`.

---

## Key API endpoints at a glance

| Purpose | Method | Path |
|---------|--------|------|
| List workspaces | GET | `/api/v1/workspaces` |
| Workspace info | GET | `/api/v1/workspace/info?workspace_id=<id>` |
| List employees | GET | `/api/v1/{workspace_id}/employees` |
| Salary definitions | GET | `/api/v1/{workspace_id}/salary-definitions` |
| Create payroll run | POST | `/api/v1/{workspace_id}/payroll/run` |
| List payroll runs | GET | `/api/v1/{workspace_id}/payroll/runs` |
| Run results | GET | `/api/v1/{workspace_id}/payroll/runs/{run_id}/results` |
| Retry failed run | POST | `/api/v1/payroll/run/{run_id}/retry` |
| Payroll inputs | GET/POST | `/api/v1/{workspace_id}/payroll/inputs` |
| Bulk upload inputs | POST | `/api/v1/{workspace_id}/payroll/inputs/bulk` |
| Component metadata | GET | `/api/v1/{workspace_id}/component-metadata` |

Full interactive docs at `http://localhost:8000/docs` once the server is running.
