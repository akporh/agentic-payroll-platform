# `STORY-0122` — Per-row payroll readiness badge

**Origin code(s):** `PT-A1-35` · `EMP-BADGE-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-8` — Enrollment & payroll readiness
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Whether a given employee was actually ready to be paid — enrolled, with a salary definition and a live contract — could only be established by opening their record one at a time.

## Delivered behaviour

A readiness badge on each employee row, showing at a glance which employees will and will not be picked up by the next run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, item EMP-BADGE-1.

## Implementation evidence

`frontend/src/pages/Employees.tsx` row badge; readiness service query.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

Sprint 26's retro recorded two lessons from this badge: its count logic had an OR-versus-sum defect, and state-variable partitions must be audited so a row cannot fall into two buckets or none.

## Dependencies

`STORY-0104` — the readiness service whose LATERAL join defect affected this badge's correctness for multi-contract employees.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- Sprint 26 retro — count-logic defect identified and recorded.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
