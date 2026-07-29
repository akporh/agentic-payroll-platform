# `STORY-0043` — Retry context carries OT/PH keys from the snapshot (FIX-5)

**Origin code(s):** `PT-A7-10` · `FIX-5`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-26` — Period & rule snapshot integrity
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; auditor

## Problem addressed

A retry that rebuilt its period context from live configuration rather than the run's snapshot would recalculate an employee against different OT/PH inputs than the original run used — so the retry result would not be comparable to the run it was correcting.

## Delivered behaviour

The retry path builds its context from the run's stored snapshot, carrying the OT and PH keys forward, so a retried employee is calculated on the same basis as the original run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 7 Track A, item FIX-5.

## Implementation evidence

Retry context construction in the retry service; snapshot read rather than live-table read.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`

## Decision references

Same principle later re-confirmed by Q8-FIX (`STORY-0112`): `proration_strategy` is read from the snapshot, not the live table.

## Dependencies

`STORY-0034` — FIX-5 is one of the five Track A mandatory fixes; `STORY-0074` — later retry-path rate-code corrections.

## Delivery sprint(s)

Sprint 7 (Track A).

## Delivery history

- Sprint 7 (Track A) — delivered as FIX-5.
- Sprint 11 — further retry-path input/rate-code fixes (`STORY-0074`).
- Sprint A (2026-07-04) — retry-service parity with the date-capped rule loader (`STORY-0135`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
