# `STORY-0100` — Navigation reorder plus employee-mismatch badge

**Origin code(s):** `PT-A1-29`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Employees whose uploaded data did not match a payroll setup record were only discoverable by opening the Employees page, so a mismatch could sit unnoticed until it broke a run.

## Delivered behaviour

Navigation reordered, with a badge on the employees entry surfacing the count of mismatched employees.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/nav-ux-employee-mismatch-badge.md`.

## Implementation evidence

`frontend/src/` navigation component and badge count query.

## Test / review evidence

`docs/test-reports/2026-05-26-nav-ux.md`.

## Decision references

The story file explicitly defers open questions about the badge's refresh scope — those were later closed by Sprint 25's real-time badge work (`STORY-0113`).

## Dependencies

`STORY-0098` — the navigation structure this reorders.

## Delivery sprint(s)

2026-05-26 retrospective delivery increment.

## Delivery history

- 2026-05-26 — delivered, with refresh-scope questions deferred.
- Sprint 25 (2026-06-10) — refresh scope closed; badge updates live on mutations (`STORY-0113`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None remaining — the deferred refresh-scope question was closed by `STORY-0113`.
