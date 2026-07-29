# `STORY-0068` — Export net pay for bank upload

**Origin code(s):** `PT-A6-04` · `P0-3`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-33` — Payment & statutory exports
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

Paying employees required transcribing net pay figures into the bank's upload format by hand — slow and the single most consequential place to make a transcription error.

## Delivered behaviour

An export of per-employee net pay in the format required for bank upload.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track H, item P0-3 — marked ✅ Sprint 10.

## Implementation evidence

Net-pay export route and generator.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

Consistent with the Phase 1 boundary recorded in `CLAUDE.md`: downstream bank and remittance work stays manual — the platform produces the file, it does not transmit it.

## Dependencies

`STORY-0031` — the per-employee results exported.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
