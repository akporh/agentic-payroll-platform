# `STORY-0113` — Payroll Inputs sidebar badge reflects the live pending count on mutations

**Origin code(s):** `BADGE-RT-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-9` — Design System & Navigation
**Feature:** `FEAT-17` — Navigation & information architecture
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

The sidebar badge was computed once and not invalidated, so after the operator resolved an input the badge still showed the old count — training them to distrust it.

## Delivered behaviour

The badge count is invalidated and refetched on the mutations that change it, so it reflects the live pending count.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-25-badge-realtime-update.md`.

## Implementation evidence

`frontend/src/` sidebar badge query and its invalidation on input mutations.

## Test / review evidence

None dedicated — Sprint 25 has no separate test report; the story files record the changes with files-changed lists.

## Decision references

Captured under D-024 — Sprint 25 was absent from the discovery inventory because the roadmap collapsed it into an aggregate row.

## Dependencies

`STORY-0100` — the badge whose deferred refresh-scope question this closes; `STORY-0108` — the Payroll Inputs badge itself.

## Delivery sprint(s)

Sprint 25 (2026-06-10).

## Delivery history

- Sprint 17 — badge introduced (`STORY-0108`).
- 2026-05-26 — refresh scope explicitly deferred (`STORY-0100`).
- Sprint 25 — live update delivered, closing that deferral.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint 25; classification is `confirmed` on the strength of the five story files existing on disk with named files-changed lists.
