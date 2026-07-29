# `STORY-0081` — Life insurance flat-amount handler (M4)

**Origin code(s):** `PT-A4-24` · `GAP-10-FIX` · `M4`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-19` — Statutory deduction correctness
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

employee

## Problem addressed

Life insurance was modelled as `rate × GROSS_PAY`, which scales a flat ₦2,000 premium with salary — wrong for every employee whose gross is not exactly the assumed base.

## Delivered behaviour

A flat-amount pattern seeds `employer_amount=2000` in `rules_jsonb`, with a DEPRECATION fallback retained for clients still on the rate-based shape.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track M, M4 — GAP-10.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py` — flat-amount handler with rate-based fallback.

## Test / review evidence

No dedicated Sprint 13 report; ROADMAP marks ✅.

## Decision references

None recorded beyond the Track M arch-council.

## Dependencies

None.

## Delivery sprint(s)

Sprint 13.

## Delivery history

- Sprint 13 — delivered with a deprecation fallback for rate-based clients.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The DEPRECATION fallback path's removal date is not recorded. Whether any workspace still uses the rate-based shape is not established here.
