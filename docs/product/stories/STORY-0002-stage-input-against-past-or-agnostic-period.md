# `STORY-0002` — Stage an input against a specific past month, or period-agnostically

**Origin code(s):** `PT-A3-02`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

Variable inputs frequently arrive late — an overtime claim for March surfaces in April. Without a way to target a past period, a late input could only be applied to the current one, putting the cost in the wrong month.

## Delivered behaviour

A staged input may name the specific past month it belongs to, or be left period-agnostic so the next run to claim it consumes it.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A3 — Pay Events, Sprint 0 foundation line items.

## Implementation evidence

`backend/api/routes/payroll.py` staged-input creation path; `payroll_input` period columns. Cited from the roadmap.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

None.

## Dependencies

`STORY-0004` — inputs are claimed at run time by the canonical claiming path.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as part of the foundation input-capture surface.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
