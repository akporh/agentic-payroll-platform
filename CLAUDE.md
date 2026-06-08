# Agentic Payroll Platform — Project Rules

Read the global `~/.claude/CLAUDE.md` first. This file adds project-specific context on top.

---

## Domain Context

Nigerian payroll platform. Statutory deductions: PAYE (cumulative annual method), Pension (8% employee / 10% employer), NHF (2.5% of basic, key: `employee_rate`), Health Insurance (key: `employee_amount`), Development Levy (key: `amount`).

All monetary values use `Decimal`. All IDs are UUIDs. Workspace scoping is mandatory on every DB query.

---

## Architecture

| Layer | Location |
|-------|----------|
| API routes | `backend/api/routes/` |
| Application services | `backend/application/` |
| Domain logic (pure) | `backend/domain/payroll/` |
| Repositories (raw SQL) | `backend/infra/repositories/` |
| DB models | `backend/infra/db/models/` |
| Migrations | `migrations/versions/` |
| Frontend pages | `frontend/src/pages/` |
| Frontend API client | `frontend/src/api/payroll.ts` |
| Frontend types | `frontend/src/types/payroll.ts` |

Domain code must never import infrastructure. Routes must never contain business logic.

---

## Migration Conventions

- Revision ID format: 12 hex chars (e.g. `a1b2c3d4e5f6`)
- Check for duplicate revision IDs before writing a new migration (`grep -h "^revision" migrations/versions/*.py | sort | uniq -d`)
- Every upgrade must have a matching downgrade
- Every destructive step must be preceded by a fail-safe existence/duplicate check in a `DO $$ BEGIN ... END $$` block
- **ADD COLUMN guard**: wrap `ALTER TABLE ... ADD COLUMN` in `DO $$ BEGIN ... EXCEPTION WHEN duplicate_column THEN NULL; END $$` — the column may already exist from an earlier migration or manual change
- **`jsonb_typeof()` in CHECK constraints**: if the column type is `json` (not `jsonb`), always cast: `jsonb_typeof(col::jsonb)` — omitting the cast causes a type-mismatch error at migration apply time

---

## API Route Rules (Standing — Do Not Break)

- **Never return `str(e)` in an HTTP response.** All `except Exception as e` blocks in route files must log the raw exception server-side (`_log.error(...)`) and return a generic human-readable string to the client (`"Failed to update employee"` etc.). DB constraint violations expose table names, column names, and constraint names verbatim in `str(e)`. This has appeared in new routes in Sprint 10 and Sprint 17 — it is a standing prohibition.
- **Free-text fields mapped to VARCHAR(N) must have `max_length=N` in the Pydantic schema.** Without it, an oversized value hits a DB truncation error whose message leaks the column name. Applies to every `str | None` field that maps to a bounded column.

---

## Known Data Contract Rules (Do Not Break)

| Field | Invariant |
|-------|-----------|
| `payroll_reconciliation.status = 'MATCHED'` | actual_total == expected_total — always |
| `payroll_reconciliation.status = 'RESOLVED'` | operator closed a MISMATCH — totals may differ |
| `payroll_result.status = 'SUCCESS'` | net_pay and component_trace_jsonb are populated |
| `payroll_run.status = 'APPROVED'` | immutable — no employee results can be modified |
| `statutory_rule (country_code, effective_from)` | UNIQUE — no duplicate effective dates |
| `pay_cycle (workspace_id) WHERE is_active` | at most one active cycle per workspace |
| `component_class = 'non_taxable'` (Sprint 12 M1) | Excluded from GROSS_PAY and gross_components_jsonb; included in NET_PAY. Must NOT have `is_pensionable = True` in client_component_metadata. Cannot be injected via payroll rules (no NON_TAXABLE rule_type exists). gross_components_jsonb excludes non_taxable by design — correct legal treatment. |
| `component_class = 'paye_addition'` (Sprint 12 M2) | Used exclusively by PAYE_ONLY_ADDITIONS at priority 95. Not swept by sum_earnings, net_formula, or statutory_deduction aggregation. Only `_handle_taxable_income` reads it. |
| `payroll_input.input_category` | Allowed values: EARNING, DEDUCTION, STANDARD, PAYE_ONLY (all uppercase). PAYE_ONLY inputs enter TAXABLE_INCOME only — never GROSS_PAY or NET_PAY. Must use standard link_inputs_to_run claiming path so retry reproduces the same TAXABLE_INCOME. |
| `payroll_run.run_type` | Allowed values: REGULAR, ADJUSTMENT, CORRECTION. No DB CHECK constraint — API allowlist is the only enforcement. Do not add new values without a matching API allowlist update. |
| `payroll_retry_request.retry_strategy` | Allowed values: PER_EMPLOYEE only. FULL_RUN is disabled by migration. API allowlist must match the migration-disabled set. |

---

## Executor Paths

- **Sequential executor** (`sequential_executor.py`) — used when `component_metadata` is provided. Produces `component_trace_jsonb`. This is the production path.
- **Legacy executor** (`executor.py` fallback) — used when `component_metadata` is None. Does NOT produce `component_trace_jsonb`. Logs a deprecation warning. Migrate all callers.

---

## Upload / Enroll Separation (Sprint 22)

The employee lifecycle has two distinct operations — do not conflate them:

| Operation | Purpose | Fields sent to API |
|---|---|---|
| **Upload** (`createEmployee`) | Register employee as HR record | HR data only: name, employee_number, TIN, RSA, bank, contract dates |
| **Enroll** (`enrollEmployee`, `bulkEnrollEmployees`) | Assign to payroll | `salary_definition_code`, `grade_code`, `designation_code` |

During bulk upload (`handleImport`), `grade_code` is **always null** — never the raw Excel grade. Grade is a payroll setup field; it is assigned only via the Enroll flow. The Excel grade column is informational (used for salary def auto-matching and the mapping panel) but must not be forwarded to `createEmployee`.

---

## Sprint State

- Sprints 1–21: closed
- Sprint 22: closed (EMP-BULK-1, EMP-BULK-2, EMP-BULK-3)

---

## Key Files to Read Before Planning

- `backend/domain/payroll/sequential_executor.py` — core calculation engine
- `backend/api/routes/payroll.py` — main API surface
- `backend/application/payroll_run_service.py` — run orchestration
- `backend/infra/repositories/reconciliation_repo.py` — reconciliation persistence

---

## Automated Delivery Workflow

### Sprint Sequence (follow every sprint, in order)

1. `/roadmap` — orient: what's done, what's next, what's deferred
2. `/pm` — scope stories + write acceptance criteria before plan mode
3. `/ux-designer` — define flows and IA (frontend track only)
4. `/architect` — for any structural or cross-layer design work
5. Explicit user confirmation of scope
6. Plan mode — research, write plan file, get approval
7. `/arch-council` — mandatory before ExitPlanMode on any data contract risk
8. Implementation
9. `/simplify` — code quality pass on all changed files
10. `/verify` — run the app, observe live end-to-end behavior (API-to-frontend boundary touched only; skip for backend-only or migration-only sprints)
11. `/ui-designer` — visual design and polish review (frontend track only)
12. `/frontend-designer` — broader frontend review (frontend track only)
13. `/security` — any sprint that adds or modifies API routes (auto-invoked, see below)
14. `/auditor` — any sprint that touches calculations or statutory rules (auto-invoked, see below)
15. `/tester` — verification against acceptance criteria from step 2
16. `/retro` — update skill checklists
17. `/save-session` — safe exit

### Auto-Invoke Rules (Claude must invoke without being asked)

- At the start of every new sprint session, invoke `/roadmap` before asking the user what to work on.
- When the user says "let's scope sprint", "what's next", or "start sprint", invoke `/pm` immediately — do not summarise the backlog manually.
- When a sprint plan includes any file under `frontend/src/`, invoke `/ux-designer` before plan mode, then `/ui-designer` and `/frontend-designer` after implementation — do not wait to be asked.
- When a sprint plan includes any structural or cross-layer design, invoke `/architect` before plan mode — do not wait to be asked.
- When a sprint plan or implementation touches both `backend/api/routes/` and any file under `frontend/src/`, invoke `/verify` after `/simplify` — run the app and confirm end-to-end behavior before the review gates. Do not invoke for backend-only or migration-only sprints.
- When a sprint plan or implementation touches `backend/api/routes/`, invoke `/security` automatically after implementation — do not wait to be asked.
- When a sprint plan or implementation touches `sequential_executor.py`, `rule_evaluator.py`, `executor.py`, or any file under `migrations/versions/` that alters a statutory rule or calculation, invoke `/auditor` after `/security` — do not wait to be asked.
- When the user says "done", "sprint complete", or "close sprint", invoke `/retro` — do not skip.

### Hook-Enforced Guards (fires automatically on every file save)

These are enforced via `~/.claude/settings.json` PostToolUse hooks — they fire on every Edit/Write:

| Trigger | What fires |
|---|---|
| Edit/Write `migrations/versions/*.py` | Duplicate revision-ID check — warns if any IDs clash |
| Edit/Write `backend/api/routes/*` | Reminder to run `/security` before closing the sprint track |
| Edit/Write `frontend/src/**` | Reminder to run `cd frontend && npx tsc --noEmit` |
| Edit/Write `requirements.txt` | Reminder to verify new packages are importable |
| Bash `git commit*` | Reminder to push to GitHub — shows current branch name |
