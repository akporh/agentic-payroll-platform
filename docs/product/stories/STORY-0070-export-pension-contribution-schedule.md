# `STORY-0070` — Export pension contribution schedule

**Origin code(s):** `PT-A6-06` · `P1-5`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-33` — Payment & statutory exports
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; pension administrator

## Problem addressed

The pension schedule — employee and employer contributions per employee — had to be assembled manually for remittance to the PFA.

## Delivered behaviour

An export of the pension contribution schedule for a run, carrying both the 8% employee and 10% employer components.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A6, item P1-5 — ✅ Sprint 10.

## Implementation evidence

Pension schedule export route and generator.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

None.

## Dependencies

`STORY-0031` — the per-employee results exported.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
