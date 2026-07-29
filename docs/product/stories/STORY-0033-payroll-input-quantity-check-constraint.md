# `STORY-0033` — `quantity >= 0` DB CHECK constraint on `payroll_input`

**Origin code(s):** `PT-A3-06` · `INP10`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; auditor

## Problem addressed

The negative-quantity guard delivered in `STORY-0016` lived only at the API boundary, so any path that wrote a payroll input without going through that route could still store a sign-inverting quantity.

## Delivered behaviour

A database CHECK constraint enforces `quantity >= 0` on `payroll_input`, so the invariant holds regardless of the write path.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track A, item INP10.

## Implementation evidence

CHECK constraint on `payroll_input.quantity` in `migrations/versions/`.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`

## Decision references

Consistent with the standing rule recorded outside this programme: DB constraint hard failures on input data are kept, never silently deduplicated or masked in the service layer.

## Dependencies

`STORY-0016` — the API-level guard this backs.

## Delivery sprint(s)

Sprint 7 (Track A).

## Delivery history

- Sprints 1–6 — API-level guard delivered (`STORY-0016`).
- Sprint 7 (Track A) — backed by a DB CHECK constraint.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
