# `STORY-0004` — Claim variable inputs at run time; canonical component execution order

**Origin code(s):** `PT-A4-01`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-18` — Core calculation & component execution
**Classification:** `platform capability`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

payroll operator

## Problem addressed

Variable inputs staged against a period had to be pulled into the run deterministically, and components had to execute in a fixed order — an arbitrary order changes the answer, because later components read earlier ones' outputs.

## Delivered behaviour

Variable inputs are claimed at run start and bound to the run; components execute in a canonical order rather than dictionary or insertion order.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 0 — Foundation, Execution (A4): “Claim variable inputs at run time ✅”, “Execute in canonical component order ✅”.

## Implementation evidence

`backend/domain/payroll/sequential_executor.py` — the ordering is expressed as component priority; see the priority chain documented in `CLAUDE.md`.

## Test / review evidence

None dedicated. Sprint 0 predates the per-sprint test-report convention, which begins with `docs/test-reports/2026-04-14-sprint-7.md`.

## Decision references

None beyond routine execution.

## Dependencies

None.

## Delivery sprint(s)

Sprint 0 — Foundation (pre-sprint tracking).

## Delivery history

- Sprint 0 — foundation delivery; no dated record.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Delivered before per-sprint tracking existed. No dedicated test report covers it; confidence stays `tentative` per D-025 and must not be cited as evidence of verified behaviour without a fresh check against the engine.
