# `STORY-0125` — Smart period-inputs upload — header parsing, `@rate` derivation, dedup

**Origin code(s):** `PT-A3-14` · `INP-NATIVE-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-14` — Bulk input upload & reconciliation intake
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

The same native-file problem as employee upload, for the monthly variable inputs — plus inputs frequently carry a rate inline (`OT@1500`) that had to be split out by hand.

## Delivered behaviour

Period-inputs upload with header parsing, derivation of the rate from `@rate` notation, and deduplication against inputs already staged for the period.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-27-smart-native-upload.md`, item INP-NATIVE-1.

## Implementation evidence

`frontend/src/` period-inputs upload parsing; bulk input creation path.

## Test / review evidence

`docs/test-reports/2026-06-15-sprint-27-28.md`

## Decision references

None.

## Dependencies

`STORY-0017` — the bulk input upload path this supersedes; `STORY-0128` — the idempotency behaviour of its dedup.

## Delivery sprint(s)

Sprint 27.

## Delivery history

- Sprint 27 — delivered.
- Sprint 28 — the dedup path's silent-skip behaviour surfaced to the operator (`STORY-0128`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
