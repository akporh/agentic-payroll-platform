# `STORY-0058` — Export full payroll detail

**Origin code(s):** `PT-A6-07` · `S9-1` · `S9-2`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-33` — Payment & statutory exports
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; client finance contact

## Problem addressed

A completed run could be viewed in the application but not handed over — a bureau client needs the full per-employee detail as a file they can check and file.

## Delivered behaviour

An export of the full payroll detail for a run, per employee and per component.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-9-full-detail-export.md` (arch-council explicitly not required for this item).

## Implementation evidence

Full-detail export route and generator.

## Test / review evidence

None dedicated — Sprint 9 has no separate test report.

## Decision references

Recorded in the story file: arch-council review was assessed as not required.

## Dependencies

`STORY-0031` — the per-employee trace the detail is drawn from.

## Delivery sprint(s)

Sprint 9 (Client B).

## Delivery history

- Sprint 9 — delivered.
- Sprint 10 — the three statutory/bank exports followed (`STORY-0068`, `STORY-0069`, `STORY-0070`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 9.
