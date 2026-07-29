# `STORY-0028` — Correct a MISMATCH — `RESOLVED` status and operator PATCH

**Origin code(s):** `PT-A6-03` · `RC5`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-8` — Disbursement & Exports
**Feature:** `FEAT-32` — Payroll reconciliation
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; auditor

## Problem addressed

A reconciliation that came back MISMATCH had no closure path — the operator could investigate and settle the difference in the real world but could not record that outcome against the run.

## Delivered behaviour

An operator may close a MISMATCH via PATCH, moving it to a distinct `RESOLVED` status. `RESOLVED` explicitly permits differing totals; `MATCHED` continues to mean actual equals expected, always.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A6, item RC5.

## Implementation evidence

`backend/infra/repositories/reconciliation_repo.py` status transitions; reconciliation PATCH route.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

**The single most-cited design lesson in this repository.** `CLAUDE.md` records both invariants: `MATCHED` means `actual_total == expected_total` always; `RESOLVED` means an operator closed a MISMATCH and totals may differ. Introducing a new status rather than widening `MATCHED`'s meaning is what the `/arch-council` gate exists to enforce — a widening would have been a silent data-contract break visible at design time.

## Dependencies

`STORY-0027` — the LOCKED/PAID gate this correction path sits behind.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as a new status, not as a widened `MATCHED`.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period; confidence stays `strongly inferred` despite this item's unusually good design record.
