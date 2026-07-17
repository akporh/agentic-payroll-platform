# Stage 01 — System Inventory

**Status:** not-started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Build the audit's own baseline map of where each concern actually lives in
the current codebase, cross-checked against prior analysis rather than
assumed from it. This is the foundation every later stage cites instead of
re-deriving.

## Inputs

- `CLAUDE.md` (root) — architecture table, data-contract invariants,
  executor-paths note.
- `docs/analysis/0.1-capability-inventory.md`,
  `0.2-execution-flow.md`, `0.8 system-reality-report.md` — prior baseline,
  to be reverified, not copied.
- Current source tree: `backend/`, `frontend/src/`, `migrations/versions/`,
  `scripts/`, `backend/scripts/`, `tests/`, `uat/`.

## Process

1. Enumerate the current top-level structure and confirm it still matches
   the architecture table in `CLAUDE.md`; note any drift.
2. For each concern in the table below, confirm current file locations by
   direct inspection (`grep`/`find`/`ls`), not by trusting `docs/analysis/`.
3. Explicitly account for both diagnostic-script locations —
   `scripts/` and `backend/scripts/` — as two distinct, currently
   undeduplicated directories; note any file present in one but not the
   other, and any file that appears stale (e.g. a `.local_backup.py`).
4. Explicitly record the two executor paths in
   `backend/domain/payroll/`: the production path
   (`sequential_executor.py`, used when `component_metadata` is supplied)
   and the legacy fallback path (`executor.py`'s internal fallback, used
   when it is not) — this record is the input Stage 02 depends on.
5. Note any directory that is empty scaffolding (e.g. `services/`,
   `database/migrations/`) versus live code.
6. Log every discrepancy between this inventory and `docs/analysis/` /
   `CLAUDE.md` as a finding — do not silently correct the prior document.

| Concern | Prior claimed location (docs/analysis, CLAUDE.md) | To confirm |
|---|---|---|
| Payroll calculation engine | `backend/domain/payroll/` | Still accurate? |
| Retry execution | `backend/application/payroll_retry_service.py` | Still accurate? |
| Snapshot creation/consumption | `backend/application/snapshot_service.py`, `backend/domain/rules/snapshot.py` | Still accurate? |
| Execution tracing | `backend/application/execution_tracer.py`, `trace_decorators.py` | Still accurate? |
| Diagnostic scripts | `scripts/`, `backend/scripts/` | Overlap/duplication current state |
| Onboarding configuration | `backend/api/routes/onboarding*.py`, `backend/domain/onboarding/` | Still accurate? |
| Workspace/payroll config UI | `frontend/src/pages/WorkspaceConfig.tsx` etc. | Still accurate? |
| API configuration routes | `backend/api/routes/workspace.py`, `onboarding.py`, `admin.py` | Still accurate? |
| DB models/migrations | `backend/infra/db/models/`, `migrations/versions/` | Still accurate? |
| Reconciliation | `backend/application/reconciliation_service.py` | Still accurate? |
| Tests | `tests/` (root) | Still the only pytest-collected path? |

## Outputs

- `findings.md` — one entry per confirmed location, per discrepancy found,
  and per duplicate/stale item identified, using `_core/finding-schema.md`.
- `evidence/` — raw `grep`/`find`/`ls` output supporting each finding, per
  `_core/evidence-standard.md` naming convention.

## Prohibited actions

- No edits to `backend/`, `frontend/`, `migrations/`, or `tests/`.
- No deletion or renaming of any file, including the suspected stale
  `scripts/run_first_payroll_emp001.local_backup.py` — record it as a
  finding, do not remove it.
- No finding may be marked `confirmed` without a citation per
  `_core/evidence-standard.md`.

## Completion criteria

- Every row in the table above has a corresponding finding (confirmed
  accurate, or confirmed drifted, with evidence).
- The `scripts/` vs `backend/scripts/` overlap is explicitly characterized
  (which files exist in each, which appear duplicated or stale).
- The production-vs-legacy executor split is explicitly recorded with
  file:line citations, ready for Stage 02 to build on.
- `audit-state.md` updated to `complete` for Stage 01.
