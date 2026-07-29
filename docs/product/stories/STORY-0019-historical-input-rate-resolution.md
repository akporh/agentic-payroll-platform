# `STORY-0019` — Historical input-rate resolution with fallback flagging in `rule_trace` (P2-7)

**Origin code(s):** `PT-A4-06` · `P2-7`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-22` — Rule resolution & versioning behaviour
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor; payroll operator

## Problem addressed

A run for a past period must use the rate in force then, not the current one — and when it cannot, that substitution must be visible rather than silent.

## Delivered behaviour

Input rates resolve historically, and where a fallback is used the `rule_trace` records `resolution_source` and a warning.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): “Resolve historical input rates with fallback flagging in rule_trace ✅ (P2-7)”.

## Implementation evidence

`backend/domain/payroll/rule_evaluator.py`; cross-period prefetch in `backend/api/routes/payroll.py`.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

None recorded at the time.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as P2-7.
- 2026-07-04 — Sprint A found the cross-period prefetch fell back silently for legacy workspaces; fixed under `STORY-0134`.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

The `_rule_trace` produced by `apply_payroll_rules` is discarded unconditionally in the legacy executor path — Track N's N1, still open. Where that path is used, this story's fallback flagging is not persisted.
