# `STORY-0127` — Payroll reconciliation upload — column mapping, comparison, mismatch filter

**Origin code(s):** `PT-A3-17` · `PAY-RECON-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-14` — Bulk input upload & reconciliation intake
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Reconciling what was actually paid against what the platform expected required comparing two files by eye.

## Delivered behaviour

Upload of an actuals file with column mapping, automatic comparison against the run's expected figures, and a filter isolating the mismatches.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-27-smart-native-upload.md`, item PAY-RECON-1.

## Implementation evidence

`frontend/src/` reconciliation upload and comparison view; reconciliation routes.

## Test / review evidence

`docs/test-reports/2026-06-15-sprint-27-28.md`

## Decision references

Bound by the reconciliation status invariants in `CLAUDE.md`: `MATCHED` means actual equals expected, always; a mismatch the operator closes becomes `RESOLVED` (`STORY-0028`).

## Dependencies

`STORY-0027` and `STORY-0028` — the reconciliation gating and correction path this feeds.

## Delivery sprint(s)

Sprint 27.

## Delivery history

- Sprint 27 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

A configurable reconciliation trigger and a pre-payment checks workflow were considered and deferred to a future sprint; that deferral is recorded outside this programme.
