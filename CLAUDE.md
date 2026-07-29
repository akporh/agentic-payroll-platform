# Agentic Payroll Platform — Project Rules

Read the global `~/.claude/CLAUDE.md` first. This file adds project-specific context on top.

---

## Commercial & scope documents

The engagement's scope line and commercial position live outside this repo. Read them before any conversation about what is "done", what Phase 1 includes, or what Sandy is entitled to.

| Document | Location | What it settles |
|---|---|---|
| Progress & Value Report (23 Jul 2026) | `Clients/Sandy/_DELIVERABLES/Reports/Sandy_progress_value_report_2026-07-23.docx` | **The definition-of-done.** Section 7 lists the six Phase 1 completion items; section 6 is the honest maturity table. |
| Fee Proposal — Phase 1 | `Clients/Sandy/_DELIVERABLES/Proposals/Sandy_fee_proposal_phase1_v1.docx` | £12,500 proposed fee, payment terms, IP retention, responsibilities. Unsigned. |
| Subsequent Development Proposal | `Clients/Sandy/_DELIVERABLES/Proposals/Sandy_subsequent_development_proposal_v1.docx` | Gated Phase 2–5 roadmap. Approve-in-principle only; no phase authorised. |
| Fee model (internal) | `02_Finance_Accounting/Sandy - Fee Model/Sandy_fee_model_2026-07-23.xlsx` | **Internal only — never send.** Holds discount scenarios and closure-risk modelling. |

Live status is tracked in `_CONTROL/dashboard/src/data/register.ts` under `sandy-mvp` (Phase 1 delivery) and `sandy-commercial` (fee, IP, DPA).

**Phase 1 boundary:** upstream data prep and downstream bank/tax/remittance work stay manual. The platform calculates, evidences, and supports approval. The manual process remains the system of record until a controlled parallel run says otherwise. Nothing built-but-untested may be described as production-ready.

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
| `employee_contract.end_date` | Inclusive last paid day — the payroll engine prorates to this date (`active_to = min(period_end, end_date)`). Must never be set to "last physical day worked" if different from the last paid day. Garden leave, notice buyout, and suspension-before-exit scenarios are NOT yet modelled; in those cases `end_date` must be set to the last date the employer pays salary, not the last date the employee is physically present. A separate `termination_reason` field is deferred to a future sprint. |
| `employee.status = 'INACTIVE'` + live contract | Valid HR state (suspension, maternity leave, etc.). The employee is excluded from payroll runs by the engine (`e.status = 'ACTIVE'` guard). This is intentional — payroll ineligibility is a consequence of INACTIVE status, not a data error. The UI surfaces an AlertBanner warning when enrolled INACTIVE employees have a live contract, so the operator is aware they will not appear in the next run. Do NOT add a hard PATCH guard that rejects this state. |
| `payroll_rule.is_active` (Sprint A) | Means "not withdrawn," never "currently in effect." Any query resolving "the rate for a given date" must always pair with `effective_from <= <date>` (ordered `effective_from DESC`) — `is_active` alone is never sufficient to pick a single applicable row, and multiple rows can legitimately be `is_active=true` at once (a back-dated correction can coexist with a still-future-dated active row). Resolution must always be date-driven — there is no valid "current period" shortcut that skips the date check, even for the run's own period. This was the root cause of two separate bugs in the same sprint (a display bug and a calculation-path bug) that both stemmed from treating `is_active` as if it meant "current." |

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

## Test Harness (2026-07-12)

The suite is fully green (306 passed, 1 intentional Phase-2 skip) and enforced automatically. Do not close any sprint with a red suite.

- **Run:** `python -m pytest -q` (needs Postgres at `DATABASE_URL`; ~10 s).
- **Pre-push gate:** `.githooks/pre-push` runs pytest + `tsc --noEmit` before every push (`core.hooksPath` is set to `.githooks`). Emergency bypass: `--no-verify`.
- **CI:** `.github/workflows/tests.yml` runs on push/PR to uat/main against a **fresh Postgres built from `alembic upgrade head`** — tests must not depend on dev-DB state. The local dev DB is confirmed drifted from migration truth (registry activation flips, missing constraints); CI is the arbiter.
- **Fixture rules for new e2e tests:** declare registry activation via `tests/registry_state.py` (pin/restore in finally); statutory `effective_from` must be later than every migration seed (latest: 2026-05-01; e2e family uses 2026-05-10..21 — pick an unused date, they collide on a UNIQUE constraint); direct `INSERT INTO employee` must include `employee_number`.
- **Standing rule:** every bug fix ships with a regression test named for the invariant it protects.
- Progress/history: `docs/test-reports/test-harness/test-harness-checklist.md`.

---

## Sprint State

- Sprints 1–21: closed
- Sprint 22: closed (EMP-BULK-1, EMP-BULK-2, EMP-BULK-3)
- Sprints 24–28: closed (Employee Lifecycle UX, Smart Upload, Upload Error Visibility)
- Sprint PAY-TAX-1: closed (NG PAYE bands corrected to NTA 2025)
- Sprint RULE-VER-1: closed (payroll rule versioning + auto-publish, 2026-06-21)

---

## Key Files to Read Before Planning

- `backend/domain/payroll/sequential_executor.py` — core calculation engine
- `backend/api/routes/payroll.py` — main API surface
- `backend/application/payroll_run_service.py` — run orchestration
- `backend/infra/repositories/reconciliation_repo.py` — reconciliation persistence

---

## Automated Delivery Workflow

Follow the global sprint sequence in `~/.claude/CLAUDE.md`'s "Sprint Workflow" section (steps 1–17) for every sprint in this repository. Stage applicability, entry conditions, dependencies, and completion criteria for the auto-invoked review/audit/test gates are authoritative in `docs/sprints/STAGE-REGISTRY.md` and `docs/sprints/WORKFLOW.md` (per D2, `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`) — not restated here. If this file and the registry ever appear to disagree on a stage the registry models, the registry governs; fix the discrepancy in one place rather than maintaining two versions.

### Frontend sub-steps (not modeled as independent registry stages)

Per `STAGE-REGISTRY.md`'s "Not modeled as a registry stage" note, `/ux-designer`, `/ui-designer`, and `/frontend-designer` are real, invoked steps folded into the `architecture`/`implementation` stages' conditions rather than given their own registry rows. This repository's concrete trigger, kept here since the registry only states it abstractly:

- When a sprint plan includes any file under `frontend/src/`, invoke `/ux-designer` before plan mode, then `/ui-designer` and `/frontend-designer` after implementation — do not wait to be asked.

### Hook-Enforced Guards (fires automatically on every file save)

These are enforced via `~/.claude/settings.json` PostToolUse hooks — they fire on every Edit/Write:

| Trigger | What fires |
|---|---|
| Edit/Write `migrations/versions/*.py` | Duplicate revision-ID check — warns if any IDs clash |
| Edit/Write `backend/api/routes/*` | Reminder to run `/security` before closing the sprint track |
| Edit/Write `frontend/src/**` | Reminder to run `cd frontend && npx tsc --noEmit` |
| Edit/Write `requirements.txt` | Reminder to verify new packages are importable |
| Bash `git commit*` | Reminder to push to GitHub — shows current branch name |
