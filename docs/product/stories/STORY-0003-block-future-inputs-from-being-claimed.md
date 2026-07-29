# `STORY-0003` — Block future-dated inputs from being claimed by a run

**Origin code(s):** `PT-A3-03`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator; auditor

## Problem addressed

An input dated after the period being run must not be paid in that period — doing so pays for work not yet performed and misstates the period's cost.

## Delivered behaviour

The claiming path excludes inputs whose target period is later than the run's period, so a future-dated input stays staged until its own period is run.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A3 — Pay Events, Sprint 0 foundation line items.

## Implementation evidence

`backend/application/` input-claiming path (`link_inputs_to_run`). Cited from the roadmap.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

None.

## Dependencies

`STORY-0004` — enforced inside the canonical claiming path.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as part of the foundation input-capture surface.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
