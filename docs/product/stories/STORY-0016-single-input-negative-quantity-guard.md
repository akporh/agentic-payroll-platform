# `STORY-0016` — Single payroll input negative-quantity guard

**Origin code(s):** `PT-A3-04` · `INP10`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-12` — Payroll input capture & validation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

A negative quantity on a payroll input silently inverted the sign of an earning, producing a deduction where an addition was intended.

## Delivered behaviour

The single-input creation path rejects a negative quantity at the API boundary.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A3, item INP10 / P3-4.

## Implementation evidence

Input creation schema validation in `backend/api/routes/payroll.py`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Related standing guidance recorded outside this programme: DB constraint hard failures on input data are kept, never silently deduplicated or masked in the service layer.

## Dependencies

`STORY-0033` — the DB-level CHECK constraint that later backed this API guard.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — API-level guard delivered.
- Track A (Sprint 7) — backed by a `quantity >= 0` DB CHECK constraint (`STORY-0033`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
