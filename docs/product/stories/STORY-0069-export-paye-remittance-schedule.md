# `STORY-0069` — Export PAYE remittance schedule

**Origin code(s):** `PT-A6-05` · `P1-4`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-33` — Payment & statutory exports
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; tax authority

## Problem addressed

PAYE remittance to the tax authority required assembling the schedule by hand from run results, with the compliance risk that carries.

## Delivered behaviour

An export of the PAYE remittance schedule for a run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A6, item P1-4 — ✅ Sprint 10.

## Implementation evidence

PAYE remittance export route and generator.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

None.

## Dependencies

`STORY-0007` — PAYE computed on taxable income, the figures this remits.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- Sprint PAY-TAX-1 (2026-06-20) — the underlying PAYE bands corrected to NTA 2025 (`STORY-0131`); schedules produced before that date reflect the superseded bands.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
