# Stage 05 — Snapshot Integrity

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Establish whether every snapshot used by payroll execution and retry is
complete, internally consistent, immutable where required, created at the
correct lifecycle point, consumed by the correct execution path, versioned/
identifiable enough for audit, and safe for legacy-run handling. Validate and
specify — but do not implement — the canonical snapshot-first fix for
finding 04-001 (confirmed S0 release blocker, Stage 04).

## Confirmed handoff state (verified before starting)

- Stage 04 is **complete**, closed 2026-07-12.
- `04-001` is a **confirmed S0 release blocker**: per-employee retry
  re-resolves the statutory rule/tax bands live instead of reading the
  frozen `rules_context_snapshot.statutory_rule`, reproduced by controlled
  non-production test.
- Decided fix direction (Stage 04 close): retry must consume frozen
  statutory content; legacy runs lacking it must hard-fail, never silently
  fall back to a live re-query.
- `CLAUDE.md` is the governing instruction source; `docs/wrapper-command/`
  remains reference-only, non-authoritative.
- This stage is read-only and produces findings plus a bounded remediation
  specification — no code changes.

## Inputs

- Stage 03 findings — full configuration catalogue, snapshot/live boundary
  map, finding 03-003 (`employee_contract_snapshot.components_jsonb`
  written, never read).
- Stage 04 findings — the reproduced 04-001 divergence and its evidence
  script/output; 04-002 (no persisted statutory-identity field); the
  execution-comparison and snapshot-source comparison tables (not
  re-derived here, extended where this stage's deeper focus requires it).
- Stage 02 findings — `execution_trace`/`component_trace_jsonb` mechanism
  split, relevant to the 04-002 observability recommendation.

## Process

1. Inventory every snapshot mechanism (12 minimum per the sprint prompt),
   recording purpose/writer/creation point/source/schema/version
   marker/consumer/immutability/validation/absent-behaviour/legacy
   compatibility/actual-consumption/evidence for each.
2. Field-by-field sufficiency analysis of
   `rules_context_snapshot["statutory_rule"]` (v2) against every value
   `payroll.py`'s live resolution extracts and every value
   `payroll_retry_service.py::_build_shared_context` currently re-derives
   live — classify each field present/missing/redundant/ambiguous.
3. Define the canonical snapshot-first retry contract: exact key/schema to
   read, exact live queries to remove, validation rules, hard-fail wording,
   legacy-run policy, migration/backfill safety, required audit data,
   required regression tests, acceptance criteria.
4. Classify legacy runs into tiers (v2-complete / partial-or-malformed v2 /
   v1 ID-only / pre-snapshot-engine / frozen-date-no-frozen-object) and
   define safe retry behaviour per tier — no tier may recommend a live-query
   fallback.
5. Revisit 03-003 and search for any other dead/unused/ambiguous/
   partially-immutable snapshot fields across the full inventory.
6. Trace snapshot creation timing and transaction boundaries for every
   snapshot mechanism — same-transaction vs. background-task, partial-
   failure behaviour, TOCTOU windows.
7. Build the immutability/mutation-control matrix from DB triggers,
   constraints, application guards, and retry's delete/reinsert pattern.
8. Recommend the minimum reliable design for statutory-identity
   observability (04-002), kept separate from the core 04-001 fix.
9. Any controlled verification reuses Stage 04's reproduction script/data
   as evidence where relevant; no new production-code execution beyond
   read-only inspection is required for this stage's specification work.

## Outputs

Per the sprint prompt's 14-item list: snapshot inventory/lifecycle map,
writer/consumer matrix, schema/version register, immutability/validation
matrix, transaction/timing assessment, legacy-run compatibility matrix,
dead/unused/ambiguous field register, statutory field-by-field sufficiency
analysis, canonical snapshot-first retry contract, bounded remediation
specification + acceptance criteria, 04-002 observability recommendation,
`findings.md`, `evidence/`, handoff notes for Stages 07, 08, 10, 11, 12 and
the immediate post-Stage-05 remediation sprint.

## Prohibited actions

- No edits to backend code, frontend code, migrations, scripts, or tests.
- Do not implement the 04-001 fix or start the remediation sprint.
- Do not start Stage 06.
- Do not downgrade or re-litigate 04-001's confirmed S0 status.
- Do not recommend live statutory re-resolution as a fallback for any
  legacy-run tier.

## Completion criteria

- Every snapshot mechanism in the minimum-12 list is inventoried with all
  required fields, or explicitly marked not-applicable with reason.
- The statutory field-by-field comparison (live resolution vs. frozen
  snapshot vs. retry requirements) is complete with every field classified.
- A canonical snapshot-first retry contract is produced with explicit
  hard-fail wording and no live-fallback recommendation for any tier.
- Legacy-run tiers are classified with a defined safe behaviour per tier.
- 03-003 is resolved to one of the sprint's five classifications with
  evidence.
- Immutability is assessed consistently across every snapshot table, not
  just the two already known to have DB triggers.
- 04-002 observability recommendation is produced, kept distinct from the
  04-001 fix.
- Every finding uses one of the five valid status values.
- Handoff notes exist for Stages 07, 08, 10, 11, 12, and the remediation
  sprint.
- `audit-state.md` left `in-progress` — this stage does not self-close;
  04-001's release-blocker status and remediation timing are preserved,
  not altered.
