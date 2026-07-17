# Stage 03 — Configuration Integrity

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Build an evidence-backed map of every payroll configuration from entry point
through validation, persistence, snapshotting, runtime consumption, and
user-visible effect. Determine where duplicate representations of the same
concept exist, which representation execution paths actually read, whether
UI/API/backend/engine stay aligned, and whether any configuration is a dead
end (accepted-but-unused, displayed-but-unsaved, saved-but-ignored).

## Governing sources (confirmed)

- `CLAUDE.md` (root) is the sole governing instruction source for this
  audit and for this codebase generally.
- `docs/wrapper-command/` is reference-only, non-authoritative (Stage 01
  finding 01-013, human decision resolved 2026-07-11).
- This stage is read-only against `backend/`, `frontend/`, `migrations/`,
  `scripts/`, and `tests/` — no code, config, or data is modified.

## Inputs

- `CLAUDE.md` — architecture table, Known Data Contract Rules table
  (`payroll_rule.is_active` date-resolution invariant is directly relevant
  here), Executor Paths section.
- Stage 01 findings (`01-system-inventory/findings.md`):
  - 01-002 — second ORM repository directory (`backend/infra/db/repositories/workspace_repo.py`), onboarding-only.
  - 01-004/01-005 — empty `component_metadata` list collapses to legacy fallback; existing `/ops/legacy-executor-stats` instrumentation.
  - 01-011 — confirmed file-location map for config UI, config API routes, DB models/migrations.
- Stage 02 findings (`02-execution-trace-baseline/findings.md`), all now
  directly load-bearing for this stage:
  - 02-001 — `execution_trace` and `component_trace_jsonb` are independent
    mechanisms; this stage must track which one (if either) reflects
    configuration resolution decisions.
  - 02-002 — per-employee retry writes zero `execution_trace` rows; this
    stage's original-run/retry consumption comparison inherits that gap —
    do not expect step-level trace evidence for retry-side configuration
    resolution.
  - 02-005/02-007/02-008 — several diagnostic/seed scripts are confirmed
    non-functional (broken imports/signatures); do not use them as
    evidence sources for "how configuration is consumed" without
    independently verifying they still run.
  - 02-006 — `simulate_payroll_components.py` reimplements config
    resolution rather than calling the production engine; not a reliable
    source for confirming precedence behaviour.
  - 02-009 — `gross_components_jsonb` shape drift between docstring/tests
    and production is a precedent for this stage's "duplicate/drifted
    representation" search — component metadata and client overrides are
    a similarly layered structure and warrant the same scrutiny.
  - 02-010 — no script touches `execution_trace`; controlled non-production
    runs invoked in this stage (if any) will not produce step-level trace
    evidence either.
- Executor-path baseline (from Stage 01/02): sequential executor
  (`sequential_executor.py`, driven by `component_metadata` +
  `client_component_metadata` overrides + `context`) is the production
  path; legacy fallback (`executor.py`) bypasses component metadata
  entirely and cannot be a configuration-consumption reference for
  metadata-driven config.

## Process

Follow the trace model specified in the sprint prompt for every
configuration catalogued:

```
Onboarding or UI → request schema → validation → application service
→ persistence → snapshot or live context → engine or handler
→ payroll result → execution trace → retry
```

1. Enumerate configuration domains: onboarding, workspace setup/config UI,
   payroll rules, statutory configuration, salary definitions, component
   metadata, client component overrides, rule sets/rule-set items, pay
   cycles, retry settings, attendance/timesheet configuration, public
   holidays, employee/contract configuration, reconciliation
   configuration, and any JSON/JSONB fields or DB columns duplicating the
   same concept.
2. For each, record entry point, validation, API/service, persistence
   location(s), default, precedence, original-run consumer, retry
   consumer, snapshot behaviour, UI visibility/editability, error/fallback
   behaviour, evidence, authority status.
3. Search explicitly for duplicate representations (JSON vs. column vs.
   rule-set item vs. hard-coded handler default vs. frontend default) and
   determine writers, readers, precedence, drift risk, conflict handling.
4. Compare consumption across original run / sequential executor / legacy
   fallback / per-employee retry (the only enabled retry strategy) /
   diagnostic scripts, reusing Stage 02's flow maps rather than
   re-deriving them.
5. Identify dead-end configuration in both directions (unused-but-stored,
   UI-only, backend-only).
6. Where safe, use read-only inspection to characterize conflict behaviour
   (e.g. platform metadata vs. client override, snapshot vs. live). No
   production data is modified; any controlled execution is read-only or
   against non-production state only, per `_core/evidence-standard.md`.

## Outputs

1. Configuration catalogue
2. Source-of-truth and precedence map
3. Configuration writer/reader matrix
4. Onboarding-to-runtime trace map
5. UI/API/backend/engine configuration coverage map
6. Duplicate-representation register
7. Dead or unused configuration register
8. Original-run/retry configuration-consumption comparison
9. Snapshot/live configuration boundary map
10. Silent-default and conflict-behaviour register
11. `findings.md` per `_core/finding-schema.md`
12. `evidence/` — code citations, grep/read output
13. Handoff notes for Stages 04, 05, 06, 07, 08, 12

## Prohibited actions

- No edits to `backend/`, `frontend/`, `migrations/`, `scripts/`, `tests/`.
- No repair of configuration wiring, no consolidation of duplicate
  storage — assessment only.
- No modification of production or shared test data.
- Do not start Stage 04 or later.
- Do not treat historical docs (`docs/analysis/`, `docs/audit/`,
  `docs/architecture/`, drifted specs) as current truth without code
  verification, per `_core/evidence-standard.md`.
- Do not infer runtime consumption merely because a field/schema/UI
  control exists — verify the actual read path.

## Completion criteria

- Configuration catalogue covers every domain listed in the sprint
  prompt's "Build the configuration catalogue" section, with the required
  fields populated (or explicitly marked "not determinable" with reason).
- Every duplicate representation found is registered with writers,
  readers, precedence, and drift/conflict assessment.
- Original-run vs. per-employee-retry consumption comparison completed for
  at least: component_metadata/client_component_metadata resolution,
  payroll_rule resolution (date-driven per `CLAUDE.md`'s `is_active`
  invariant), and one snapshot-vs-live boundary.
- All findings logged with evidence citations; classification
  (confirmed/plausible/unconfirmed/rejected/human-decision-required) per
  finding, per `_core/evidence-standard.md`.
- Handoff notes written for Stages 04, 05, 06, 07, 08, 12.
- `audit-state.md` left `in-progress` — this stage does not self-close.
