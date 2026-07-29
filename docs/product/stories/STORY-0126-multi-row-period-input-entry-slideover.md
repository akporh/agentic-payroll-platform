# `STORY-0126` — Multi-row period input entry slide-over

**Origin code(s):** `PT-A3-15` · `INP-MULTI-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Entering a handful of inputs by hand — too few to justify a file — meant repeating a single-input form once per row.

## Delivered behaviour

A slide-over allowing several period inputs to be entered and submitted together.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-27-smart-native-upload.md`, item INP-MULTI-1.

## Implementation evidence

`frontend/src/` multi-row input slide-over.

## Test / review evidence

`docs/test-reports/2026-06-15-sprint-27-28.md`

## Decision references

The design-system rule recorded outside this programme applies to this surface: never use design-system `NumberInput`/`TextInput` inside table cells — use a raw input styled consistently, with an `aria-label`.

## Dependencies

`STORY-0016` — the per-input negative-quantity guard each row is subject to.

## Delivery sprint(s)

Sprint 27.

## Delivery history

- Sprint 27 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
