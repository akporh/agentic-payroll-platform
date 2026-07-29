# `STORY-0030` — `rule_set` `effective_from` UNIQUE; cross-period rule-set access

**Origin code(s):** `PT-A7-02` · `P2-6`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-26` — Period & rule snapshot integrity
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor

## Problem addressed

Recalculating or inspecting a past period requires reaching the rule set that was in force then, not the current one — and two rule sets sharing an effective date make that lookup ambiguous.

## Delivered behaviour

`rule_set.effective_from` is unique, and the engine can access a rule set for a period other than the current one.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability areas A7–A10, item P2-6.

## Implementation evidence

`rule_set` UNIQUE constraint; cross-period rule-set loader.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None at the time. Sprint A later established the binding rule that date-driven resolution is always required and `is_active` alone is never sufficient — see `STORY-0135`.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Sprint A (2026-07-04) — the cross-period prefetch and legacy loader on this foundation both found defective and fixed (`STORY-0134`, `STORY-0135`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
