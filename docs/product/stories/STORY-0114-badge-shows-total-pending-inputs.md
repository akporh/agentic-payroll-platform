# `STORY-0114` — Badge shows total pending inputs, not just issue inputs

**Origin code(s):** `BADGE-RT-2`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

The badge counted only inputs flagged with issues, so a period with a large number of perfectly valid but unclaimed inputs showed a badge of zero — implying there was nothing waiting when there was.

## Delivered behaviour

The badge counts all pending inputs, not only those with issues.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-25-badge-realtime-update.md`.

## Implementation evidence

`frontend/src/` badge count query predicate.

## Test / review evidence

None dedicated — see `STORY-0113`.

## Decision references

Captured under D-024.

## Dependencies

`STORY-0113` — delivered together as the same badge correction.

## Delivery sprint(s)

Sprint 25 (2026-06-10).

## Delivery history

- Sprint 25 — delivered alongside the live-update fix.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 25.
