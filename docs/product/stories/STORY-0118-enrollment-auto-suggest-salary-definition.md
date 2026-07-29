# `STORY-0118` — Enrollment slide-over auto-suggests a salary definition from the grade label

**Origin code(s):** `PT-A1-31` · `EMP-ENROLL-AUTODEF-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-8` — Enrollment & payroll readiness
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Enrolling an employee meant choosing a salary definition from a list by hand, when the grade already recorded against them usually determines it — repeated work with an easy mis-selection.

## Delivered behaviour

The enrollment slide-over auto-suggests the matching salary definition from the employee's grade label, leaving the operator to confirm rather than search.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, item EMP-ENROLL-AUTODEF-1.

## Implementation evidence

`frontend/src/` enrollment slide-over auto-match logic.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

The matching rule this depends on is recorded outside this programme: salary-definition codes are grade-only, not designation-plus-grade — the grade column in the onboarding workbook *is* the salary-definition code.

## Dependencies

`STORY-0129` — the pre-population normalisation fix on the same surface.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
