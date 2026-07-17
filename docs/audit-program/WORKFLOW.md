# Audit Workflow

Governs how stages in `docs/audit-program/` are opened, executed, closed, and
escalated. Subordinate to `CLAUDE.md`, which remains the governing repository
instruction source.

## Stage lifecycle

`not-created` → `not-started` → `in-progress` → `blocked` → `complete`

- **not-created** — stage folder does not exist yet.
- **not-started** — folder and `CONTEXT.md` exist; work has not begun.
- **in-progress** — evidence is being gathered and logged.
- **blocked** — a required input is missing, or a finding needs a
  `_core/human-decisions.md` entry before the stage can proceed.
- **complete** — the stage's completion criteria (defined in its
  `CONTEXT.md`) are met.

Every transition is recorded in [`audit-state.md`](audit-state.md).

## Read-only enforcement

All 13 stages are read-only against `backend/`, `frontend/`, and
`migrations/` — **including Stage 10 (execution-trace remediation)**. Stage
10 produces a remediation *design* (root cause, proposed fix, affected call
sites) as a finding, not a code change. No stage in this audit programme
edits application code.

Production-code remediation for any finding — including execution-trace
gaps — begins only after Stage 13 produces an approved backlog, and happens
outside this workspace, as an ordinary sprint under `CLAUDE.md`'s sprint
workflow (`/pm` scoping → plan mode → `/arch-council` if a data contract is
touched → implementation → `/security` / `/auditor` as applicable).

## Gate criteria

A stage may not open until:

1. Its declared **Inputs** (in its `CONTEXT.md`) exist and are readable.
2. The prior stage it depends on (if any) has reached `complete`, or an
   explicit `_core/human-decisions.md` entry authorizes proceeding early.

Example: Stage 04 (retry parity) depends on Stage 02's executor-path
baseline — it needs to know which executor path (`sequential_executor.py`
vs. the legacy fallback in `executor.py`) a given run took before comparing
original vs. retry output.

## Escalation

- Any finding logged at severity **S0 — Critical** is entered into
  `_core/human-decisions.md` immediately — it is not held until Stage 13.
- Any finding whose evidence cannot be obtained without touching
  `backend/`, `frontend/`, or `migrations/` is logged as `blocked` with the
  specific blocker named, and referred to `_core/human-decisions.md`.

## Rollup to the consolidated backlog

`13-consolidated-backlog/backlog.md` is a mechanical rollup of every
`findings.md` (and `10-execution-trace-remediation/remediation-log.md`,
read as a findings source) across stages 01–12, ordered by
`_core/severity-model.md`. Stage 13 does not re-analyze or re-derive
findings — it aggregates and prioritizes what earlier stages already
logged and evidenced.
