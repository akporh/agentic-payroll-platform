# `STORY-0108` — Payroll Inputs issues badge

**Origin code(s):** `PT-A1-27` · `EMP-UX-4`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Inputs with problems — unmatched employees, invalid codes — were only visible once the operator opened the Payroll Inputs page, so they were routinely discovered at run time instead.

## Delivered behaviour

A badge on the Payroll Inputs navigation entry showing the count of inputs with issues.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-17-employee-ux.md`, item EMP-UX-4.

## Implementation evidence

`frontend/src/` sidebar badge and its count query.

## Test / review evidence

`docs/test-reports/2026-05-27-sprint-17-full.md`

## Decision references

Reassigned to `FEAT-17` under D-024 so that navigation badges sit together rather than splitting across the employee-page feature.

## Dependencies

`STORY-0098` — the navigation this badges.

## Delivery sprint(s)

Sprint 17.

## Delivery history

- Sprint 17 — delivered showing issue inputs only.
- Sprint 25 (2026-06-10) — corrected to show total pending inputs, not just issue inputs (`STORY-0114`), and to update live on mutations (`STORY-0113`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None remaining — both defects in this badge's behaviour were closed in Sprint 25.
