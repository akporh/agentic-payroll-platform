# `STORY-0001` — List valid/unclaimed input codes; delete a staged input; download the input template

**Origin code(s):** `PT-A3-01`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

An operator staging variable pay inputs had no way to see which input codes were valid for the workspace, which staged inputs were still unclaimed by a run, or to remove one entered in error — and no starting template to enter them from.

## Delivered behaviour

Endpoints and UI to list the workspace's valid input codes, list unclaimed (not yet consumed by a run) staged inputs, delete an individual staged input, and download an input template for offline entry.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A3 — Pay Events, Sprint 0 foundation line items.

## Implementation evidence

`backend/api/routes/payroll.py` input-code and staged-input routes; `backend/infra/repositories/` payroll input repository. Cited from the roadmap; individual files not independently re-verified in the discovery pass.

## Test / review evidence

None. No dedicated test report exists for Sprint 0.

## Decision references

None.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation.

## Delivery history

- Sprint 0 — delivered as part of the foundation input-capture surface.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Sprint 0 predates the per-sprint test-report convention, so there is no dedicated test report for this item. Its only source is `docs/ROADMAP.md`. Confidence is `tentative` for that reason and it must not be cited as evidence of verified behaviour.
