# Stage 02 — Execution Trace and Diagnostic-Script Baseline

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Establish the current, evidence-backed baseline for execution tracing,
diagnostic scripts, and step-through tooling — including where they diverge
from the production payroll system. This stage does not fix anything; it
maps what exists so Stage 04 (retry parity) and Stage 10 (execution-trace
remediation) have a verified foundation instead of re-deriving it.

## Inputs

- `CLAUDE.md` (root) — Executor Paths section, data-contract invariants.
- Stage 01 findings, specifically:
  - 01-004 / 01-005 — legacy executor fallback mechanism and existing
    ops-endpoint instrumentation (`/ops/legacy-executor-stats`).
  - 01-006 / 01-007 — `scripts/` vs `backend/scripts/` inventory, overlap,
    and the tracked `.local_backup.py` stale file.
  - Concern-location table (01-011) for tracer/repo file locations.
- Human decision on `docs/wrapper-command/` (finding 01-013): resolved
  2026-07-11 as **non-authoritative** — not cited in this stage.
- Current source:
  - `backend/application/execution_tracer.py`
  - `backend/application/trace_decorators.py`
  - `backend/infra/repositories/execution_trace_repo.py`
  - `backend/application/payroll_run_service.py`,
    `backend/application/payroll_retry_service.py`,
    `backend/application/payroll_run_persister.py`
  - `backend/domain/payroll/` (`executor.py`, `sequential_executor.py`,
    `batch_processor.py`, `run_executor.py`, `result_builder.py`,
    `calculator.py`, `salary.py`)
  - `scripts/`, `backend/scripts/`

## Process

1. Trace the production execution path: orchestration
   (`payroll_run_service.py`) → per-employee execution → sequential
   executor → handlers → result building → persistence. Record file:line
   for each handoff.
2. Identify every point the tracer/decorator is invoked, what step name it
   records, and whether the step is persisted to `execution_trace` or is
   console-only (Rich output, not persisted).
3. Inventory `scripts/` and `backend/scripts/` in full — for each script,
   record: does it call production services directly, does it reimplement
   calculation logic, does it use the sequential or legacy executor path,
   does it write to the DB, is it read-only, does it depend on stale
   fields/schemas.
4. Determine whether `component_trace_jsonb` (persisted by the sequential
   executor path per `CLAUDE.md`) and the `execution_trace` table (written
   by `ExecutionTracer`/`save_trace_step`) are the same trace system or two
   independent mechanisms with different scopes.
5. Compare trace behaviour across original run, full retry, partial retry,
   per-employee retry, and diagnostic scripts — which of these paths
   produce which trace artifacts.
6. Cross-reference fields/steps present in production vs. scripts in both
   directions.
7. Assess each script for safety as audit instrumentation (i.e. can it be
   run read-only against a copy of data without mutating production state
   or reimplementing possibly-stale logic).

## Outputs

- Production execution-flow map
- Execution-trace lifecycle map (creation → enrichment → persistence →
  exposure)
- Trace schema/field inventory
- Diagnostic-script catalogue (one row per script in `scripts/` and
  `backend/scripts/`)
- Script-to-production-service dependency map
- Original-run/retry/script trace comparison table
- List of stale, duplicated, or unsafe diagnostic scripts
- Retain/repair/replace/retire assessment per script
- `findings.md` entries per `_core/finding-schema.md`
- `evidence/` — code citations, read-only grep/inspection output

## Prohibited actions

- No edits to `backend/`, `frontend/`, `migrations/`, or existing scripts.
- No script execution against production data. Any controlled execution
  (per `_core/evidence-standard.md` evidence type 4) must run against a
  local/non-production DB and be recorded with command + result.
- Do not repair or replace any script — only assess.
- Do not infer script correctness from filename or docstring — verify by
  reading the actual logic.

## Completion criteria

- Production execution-flow map and execution-trace lifecycle map produced
  and cited to code.
- Every file in `scripts/` and `backend/scripts/` (18 files per Stage 01's
  01-006 count) appears in the diagnostic-script catalogue with a
  retain/repair/replace/retire recommendation.
- `component_trace_jsonb` vs. `execution_trace` table relationship
  explicitly determined (one system or two) with evidence.
- Original-run/retry/script trace comparison completed for at least:
  original run, per-employee retry (the only enabled retry strategy per
  `CLAUDE.md`'s `payroll_retry_request.retry_strategy` invariant), and one
  diagnostic script.
- All findings logged with evidence citations; any S0 finding escalated to
  `_core/human-decisions.md` immediately.
- `audit-state.md` updated to `complete` for Stage 02 (pending explicit
  user approval — this stage does not self-close).
