# Stage 01 — Findings

Status: **complete**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md).

---

### 01-001 — `backend/app/` is empty scaffolding, not in the documented architecture

- **stage:** 01-system-inventory
- **location:** `backend/app/` (contains only `.gitkeep`)
- **current implementation:** Directory exists with a single `.gitkeep` file and no Python modules.
- **intended behaviour:** `CLAUDE.md`'s Architecture table (API routes/application/domain/infra/migrations/frontend) does not list `backend/app/` at all.
- **suspected or confirmed defect:** No defect — it is inert scaffolding, not wired into any import path. Recorded for completeness of the inventory only.
- **evidence:** `evidence/2026-07-11-top-level-tree.txt` (directory present), `evidence/2026-07-11-empty-scaffold-dirs.txt` (contents confirmed as `.gitkeep` only; `CLAUDE.md` architecture table confirmed not to list it)
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-002 — Repository layer is split across two directories, one undocumented

- **stage:** 01-system-inventory
- **location:** `backend/infra/repositories/` (14 files) vs. `backend/infra/db/repositories/workspace_repo.py` (1 file)
- **current implementation:** `CLAUDE.md`'s architecture table lists a single repository location (`backend/infra/repositories/`, "raw SQL"). `backend/infra/db/repositories/workspace_repo.py` is a second, ORM-based (`db.query(...)`) repository file, imported exclusively by three onboarding-domain modules (`backend/domain/onboarding/hard_validator.py`, `onboarding_status.py`, `state_inference.py`). No other module in the codebase imports from `backend.infra.db.repositories`.
- **intended behaviour:** Not documented — `CLAUDE.md` does not describe a second repository location or a raw-SQL/ORM split.
- **suspected or confirmed defect:** Unconfirmed. This may be an intentional isolation of onboarding-status ORM checks from the raw-SQL repository layer, or it may be incomplete migration debt. No source states which.
- **evidence:** `evidence/2026-07-11-repository-layer.txt`
- **status:** plausible
- **severity:** S3
- **related invariant:** none

---

### 01-003 — `services/*` and `database/migrations/` are empty scaffolding

- **stage:** 01-system-inventory
- **location:** `services/payroll-engine/`, `services/api-gateway/`, `services/shared/`, `database/migrations/`
- **current implementation:** All four directories are empty (no files at all, not even `.gitkeep`). Confirmed via direct `ls -la`.
- **intended behaviour:** Not documented anywhere in `CLAUDE.md` or `docs/analysis/`.
- **suspected or confirmed defect:** No defect — not imported, not referenced, no runtime effect. Likely leftover scaffolding from an earlier services-split plan that was not pursued.
- **evidence:** `evidence/2026-07-11-empty-scaffold-dirs.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-004 — Legacy executor fallback can be triggered by an *empty* `component_metadata` list, not only an omitted one

- **stage:** 01-system-inventory
- **location:** `backend/api/routes/payroll.py:866` (`component_metadata = component_metadata or None`); `backend/domain/payroll/executor.py:108` (`if component_metadata:` → sequential path; else legacy path, line ~118 logs a deprecation warning)
- **current implementation:** The API route coerces an empty list (`[]`) — e.g. a workspace with zero rows in `component_metadata`/`client_component_metadata` — to `None` before passing it down. `executor.py`'s `if component_metadata:` check treats `None` and `[]` identically, so either condition routes execution through the legacy fallback path (no `component_trace_jsonb` produced), per `executor.py:108-122`.
- **intended behaviour:** `CLAUDE.md`'s "Executor Paths" section states the legacy path fires "when `component_metadata` is None" — it does not address the empty-list case, and no document states whether an empty list should be treated the same as an absent parameter, or should instead surface as a distinct error/onboarding-incomplete condition.
- **suspected or confirmed defect:** Unconfirmed whether this is intended. The mechanism itself is confirmed by direct code citation; whether "workspace has no component_metadata configured" *should* silently fall back to the legacy path (vs. hard-fail, since `CLAUDE.md` already directs "Migrate all callers" away from the legacy path) is an open question.
- **evidence:** `evidence/2026-07-11-executor-paths.txt`
- **status:** plausible
- **severity:** S1 (provisional — if the fallback is unintended, it's a silent-failure-class issue per the severity model; if intended, this is S3. Kept at S1 pending the human decision below.)
- **related invariant:** `CLAUDE.md` Executor Paths section

---

### 01-005 — Legacy executor fallback usage is already monitored, not an undiscovered condition

- **stage:** 01-system-inventory
- **location:** `backend/api/routes/payroll.py:1316-1327` (`GET /{workspace_id}/payroll/ops/legacy-executor-stats`); backed by `backend/infra/repositories/execution_trace_repo.py` (`get_legacy_executor_stats`)
- **current implementation:** A dedicated ops endpoint already exists that reports `total_runs`, `runs_with_legacy`, `pct_runs_affected`, and `total_legacy_events`, explicitly described in its docstring as tracking "migration progress away from the legacy executor."
- **intended behaviour:** Consistent with `CLAUDE.md`'s direction to migrate callers off the legacy path — this endpoint is the existing instrumentation for that migration.
- **suspected or confirmed defect:** None. Recorded so Stage 02 (execution trace baseline) starts from this existing instrumentation rather than re-discovering it.
- **evidence:** `evidence/2026-07-11-executor-paths.txt` (docstring), route citation above
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-006 — `scripts/` and `backend/scripts/` are both unimported by production app code but overlap in purpose; `backend/scripts/test_*.py` files are named like tests but excluded from the suite

- **stage:** 01-system-inventory
- **location:** `scripts/` (8 files) and `backend/scripts/` (10 files)
- **current implementation:** Neither directory is imported by any file under `backend/api/`, `backend/application/`, `backend/domain/`, or `backend/infra/` (confirmed by grep — zero matches). `pytest.ini` sets `testpaths = tests` and `norecursedirs = .venv backend/scripts` — so `backend/scripts/test_persist.py`, `test_execute_and_persist.py`, `test_run_batch_persist.py`, `test_export_netpay.py`, `test_export_paye.py`, `test_export_register.py` are explicitly excluded from pytest collection despite `test_*.py` naming. Purpose overlap: `scripts/simulate_payroll_components.py` / `simulate_stepthrough.py` vs. `backend/scripts/simulate_payroll.py` both simulate payroll execution outside the API.
- **intended behaviour:** Not documented — no file states which directory is canonical for diagnostics/simulation, or why the `test_*.py`-named files in `backend/scripts/` are deliberately excluded from CI rather than moved into `tests/` or renamed.
- **suspected or confirmed defect:** No correctness defect (neither path affects production runtime). The naming of `backend/scripts/test_*.py` is confirmed misleading — a reader could reasonably assume these run under CI when the config explicitly excludes them.
- **evidence:** `evidence/2026-07-11-scripts-inventory.txt`, `evidence/2026-07-11-tests-inventory.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-007 — A `.local_backup.py` file is tracked in git despite matching a `.gitignore` exclusion pattern, and its persistence logic uses stale field names

- **stage:** 01-system-inventory
- **location:** `scripts/run_first_payroll_emp001.local_backup.py`; `.gitignore:37` (`*.local_backup.py`)
- **current implementation:** `git ls-files` confirms the file is tracked. `.gitignore` contains a rule that would prevent *new* files matching `*.local_backup.py` from being added, implying the pattern is meant to keep such files out of version control — this one predates that rule or was force-added. A diff against the live `scripts/run_first_payroll_emp001.py` shows it references payroll-result fields (`payroll_result['gross_pay']`, `['total_deductions']`) that do not match the current live script's field names (`gross_components_jsonb`, `deductions_jsonb`, `calculations_snapshot_json`).
- **intended behaviour:** Not documented. No file marks this as an intentional retained reference copy.
- **suspected or confirmed defect:** No runtime defect — confirmed unimported, so it cannot be executed by anything else and cannot silently affect production. Its presence is a housekeeping artifact, not a functional one.
- **evidence:** `evidence/2026-07-11-scripts-inventory.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-008 — Inconsistent route path conventions within `backend/api/routes/workspace.py`

- **stage:** 01-system-inventory
- **location:** `backend/api/routes/workspace.py` — e.g. line 51 `POST /workspace` (singular, no id), line 98 `GET /workspaces` (plural, list), line 194 `GET /{workspace_id}/employees` (no `/workspace(s)` prefix at all), line 1696 `GET /workspaces/{workspace_id}/payroll-config` (plural + id prefix)
- **current implementation:** Three distinct prefix conventions coexist in the same route file: no prefix, singular `/workspace`, and plural `/workspaces`, confirmed by direct grep of all `@router.*` decorators in the file.
- **intended behaviour:** No document specifies a REST path convention for this API.
- **suspected or confirmed defect:** Unconfirmed whether this causes any actual collision or client confusion — no evidence of a broken route was gathered in this stage. Flagged as a wiring question for Stage 06 (UI/API/backend wiring), not resolved here. Superseded in scope by 01-012, which confirms the inconsistency persists at the full mounted path.
- **evidence:** `evidence/2026-07-11-config-entrypoints.txt`
- **status:** unconfirmed
- **severity:** S3
- **related invariant:** none

---

### 01-009 — Onboarding route cites "ARCHITECTURE_LOCK.md" by bare name while three differently-versioned files with that stem exist in a folder marked "(Drifted)"

- **stage:** 01-system-inventory
- **location:** `backend/api/routes/onboarding.py:8` (`Reference: ARCHITECTURE_LOCK.md — Onboarding Pipeline.`); `docs/Buisness Specs & Designs (Drifted)/ARCHITECTURE_LOCK.md`, `ARCHITECTURE_LOCK_V1_1.md`, `ARCHITECTURE_LOCK_PHASE1.md`
- **current implementation:** The code comment does not specify a path, and three files sharing that stem exist side by side in a folder whose own name marks its contents as drifted from current implementation.
- **intended behaviour:** Not determinable from the repository alone — unclear which (if any) of the three is the one the comment intends, or whether any of them still reflects current onboarding behaviour.
- **suspected or confirmed defect:** Not classified as a defect — recorded per `README.md`'s instruction to treat this folder as reference-only pending reverification, not as a current-truth source.
- **evidence:** citations above
- **status:** unconfirmed
- **severity:** S3
- **related invariant:** none

---

### 01-010 — Two similarly named UX documentation directories, one effectively empty

- **stage:** 01-system-inventory
- **location:** `docs/ux-design-brief/` (contains only `.DS_Store` — no actual content files) vs. `docs/ux-ui-design-brief/` (11 numbered files + `README.md`: entity map, API surface, business rules, actors, personas, journey maps, screen inventory, data sensitivity, state flows, integration touchpoints, drift log). A third, `docs/ux-ui-artefacts/`, is fully empty (no files at all, not even `.DS_Store`).
- **current implementation:** Confirmed via full-tree listing this session: `docs/ux-design-brief/` has no content, `docs/ux-ui-artefacts/` has no content, `docs/ux-ui-design-brief/` is the only one of the three with substantive files.
- **intended behaviour:** Not documented — no file states which directory name is canonical or why three near-identically-named directories exist.
- **suspected or confirmed defect:** Not a code defect. `docs/ux-ui-design-brief/` is confirmed the only populated one of the three, so for any future audit stage citing UX documentation, this is the one to reference — the other two are empty, not merely thin.
- **evidence:** `evidence/2026-07-11-docs-authority-full.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-011 — Concern-location table (from Stage 01 `CONTEXT.md`) re-verified against current code

- **stage:** 01-system-inventory
- **location:** see table below
- **current implementation:** Every row was re-checked this session by direct inspection (not by trusting `docs/analysis/` or the prior orientation report).
- **intended behaviour:** Matches `CLAUDE.md`'s architecture table and the Stage 01 `CONTEXT.md` table for every row except the two split/undocumented cases already logged as 01-002 (repository layer) and 01-006 (scripts).
- **suspected or confirmed defect:** None — this entry records confirmation, not a defect.
- **evidence:** `evidence/2026-07-11-top-level-tree.txt`, `evidence/2026-07-11-repository-layer.txt`, `evidence/2026-07-11-config-entrypoints.txt`, `evidence/2026-07-11-cross-check-remaining-rows.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

| Concern | Location | Result |
|---|---|---|
| Payroll calculation engine | `backend/domain/payroll/` (`executor.py`, `sequential_executor.py`, `batch_processor.py`, `run_executor.py`, `calculator.py`, `salary.py`, `salary_derivation.py`, `rule_evaluator.py`, `result_builder.py`) | confirmed accurate |
| Retry execution | `backend/application/payroll_retry_service.py` (818 lines; calls `execute_single_employee_payroll` at line 669) | confirmed accurate |
| Snapshot creation/consumption | `backend/application/snapshot_service.py`, `backend/domain/rules/snapshot.py` | confirmed accurate |
| Execution tracing | `backend/application/execution_tracer.py`, `trace_decorators.py`, `backend/infra/repositories/execution_trace_repo.py` | confirmed accurate |
| Diagnostic scripts | `scripts/` (8 files), `backend/scripts/` (10 files) | confirmed — overlapping, undeduplicated (see 01-006, 01-007) |
| Onboarding configuration | `backend/api/routes/onboarding.py`, `onboarding_validation.py`, `backend/domain/onboarding/` (`hard_validator.py`, `onboarding_status.py`, `state_inference.py`) | confirmed accurate |
| Workspace/payroll config UI | `frontend/src/pages/WorkspaceConfig.tsx`, `RateCodes.tsx`, `AttendanceConfiguration.tsx`, `PublicHolidays.tsx`, `WorkspaceSetup.tsx`, `Reconciliation.tsx` | confirmed present |
| API configuration routes | `backend/api/routes/workspace.py` (42 routes), `onboarding.py` (3), `admin.py` (3, HTML dashboard) | confirmed accurate, see 01-008 |
| DB models/migrations | `backend/infra/db/models/` (20 model files), `migrations/versions/` (99 migration files) | confirmed accurate |
| Reconciliation | `backend/application/reconciliation_service.py` (imports `backend.infra.repositories.reconciliation_repo`) | confirmed accurate |
| Tests | `tests/` (41 files); `pytest.ini` sets `testpaths = tests`, `norecursedirs = .venv backend/scripts` | confirmed — sole pytest-collected path |

---

### 01-012 — Route mount confirms sub-path prefix inconsistency is real, not resolved by the global mount; `admin` router is on a separate, unprefixed namespace

- **stage:** 01-system-inventory
- **location:** `backend/api/main.py:50,54-60`
- **current implementation:** Every router except `admin.router` is mounted with `prefix="/api/v1"` (`health`, `onboarding`, `onboarding_validation`, `payroll`, `payroll_input`, `workspace`, `employees`). `admin.router` is mounted with no prefix at all (`app.include_router(admin.router)`, line 50), so the HTML admin dashboard lives at `/admin`, entirely outside the `/api/v1` JSON API namespace. Because the sub-path inconsistency identified in finding 01-008 sits *inside* `workspace.py`'s own route strings, the shared `/api/v1` prefix does not resolve it — the live inconsistency is confirmed to persist at full-path resolution, e.g. `POST /api/v1/workspace` vs. `GET /api/v1/workspaces` vs. `GET /api/v1/{workspace_id}/employees` vs. `GET /api/v1/workspaces/{workspace_id}/payroll-config`.
- **intended behaviour:** Not documented.
- **suspected or confirmed defect:** No defect confirmed — FastAPI resolves all of these distinctly and no routing collision was found. Recorded as a confirmed structural fact, superseding 01-008's "unconfirmed" full-path characterization.
- **evidence:** `evidence/2026-07-11-config-entrypoints-full.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 01-013 — A second, agent-facing instruction set exists under `docs/wrapper-command/`, addressed to an agent named "Casper," separate from `CLAUDE.md`

- **stage:** 01-system-inventory
- **location:** `docs/wrapper-command/engineering-playbook.md`, `Query-codebase.md`, `run-architecture-check.md.txt`, `payroll-component-Integrity-and-period-input-alignment`
- **current implementation:** `engineering-playbook.md:5-9` states it "is used by: Engineers, Reviewers, AI agents (Casper)" and defines categories (Guarantees, Engine, Data Model) that changes "must be evaluated across." `Query-codebase.md` and `run-architecture-check.md.txt` are prompt templates instructing an agent to trace code paths end-to-end and apply "SYSTEM ARCHITECTURE MODE." `payroll-component-Integrity-and-period-input-alignment` (167 lines, no file extension) is framed as a "SYSTEM GUARD" the agent "MUST validate all reasoning against" concerning component/engine visibility and period-input alignment. None of these four files were surfaced in this audit programme's original repository orientation report.
- **intended behaviour:** Not stated anywhere how this instruction set relates to `CLAUDE.md`, whether it is still in active use, or whether "Casper" is a still-active tool in this project's workflow. A targeted check for overlap with `CLAUDE.md`'s specific invariants (`is_active`/`effective_from`, `MATCHED` reconciliation status, `component_class`) found no direct textual contradiction, but the check was not exhaustive across all 167+125 lines.
- **suspected or confirmed defect:** Unconfirmed whether this creates conflicting guidance for anyone (human or agent) working on this codebase, since its currency and authority relative to `CLAUDE.md` is unknown. Not a code defect — a documentation-authority question.
- **evidence:** `evidence/2026-07-11-wrapper-command-inspection.txt`
- **status:** plausible
- **severity:** S2 (elevated above the other documentation-authority findings because, unlike stale specs, this one explicitly instructs *agent reasoning* — if stale or contradictory, it could actively misdirect future AI-assisted work on this codebase, not just a human reader)
- **related invariant:** none directly confirmed; candidate overlap with `CLAUDE.md`'s Known Data Contract Rules table (`component_class`) noted but not verified

---

## Human-decision candidates raised (logged separately)

See [`../_core/human-decisions.md`](../_core/human-decisions.md) for the three open questions raised by 01-002, 01-004, and 01-013. All three remain **pending** — none are resolved here and none block Stage 01 completion, per `WORKFLOW.md`'s escalation rule.

## Handoff — where each open question is investigated next

| Open question | Finding(s) | Next investigated in |
|---|---|---|
| Does an empty `component_metadata` list silently and correctly fall through to the legacy executor, or should it hard-fail? | 01-004, 01-005 | **Stage 04 (original-run and retry parity)** — Stage 04 depends on this Stage 01 executor-path baseline to determine which path a given run/retry took; it is the natural point to also characterize how often the empty-list condition fires and whether original vs. retry ever diverge because of it. |
| Is the second, ORM-based repository directory (`backend/infra/db/repositories/workspace_repo.py`) intentional isolation or migration debt? | 01-002 | **Stage 12 (code simplification)** — this is a structural/consolidation question with no correctness impact identified in Stage 01; it belongs with the other duplication/simplification findings (e.g. 01-006, 01-007) rather than an earlier correctness-focused stage. |
| Is `docs/wrapper-command/` (the "Casper" agent-instruction set) still authoritative, and how does it relate to `CLAUDE.md`? | 01-013 | **A documentation-governance decision before Stage 02 opens** — this is not itself a code-behavior question any later stage's evidence-gathering would resolve; it requires a human decision on document ownership/currency. Recorded in `_core/human-decisions.md` as pending; Stage 02 does not depend on its resolution to begin, but the decision should be made before relying on `docs/wrapper-command/` as a citation source in any later stage. |
