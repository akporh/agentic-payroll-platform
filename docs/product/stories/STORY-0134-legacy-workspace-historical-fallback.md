# `STORY-0134` — Legacy-workspace historical fallback in cross-period prefetch (SPRINT-A-2)

**Origin code(s):** `PT-A4-29` · `SPRINT-A-2`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-22` — Rule resolution & versioning behaviour
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; auditor

## Problem addressed

Where a workspace had never published a `rule_set`, the cross-period prefetch loop silently fell back to the **current** rate — producing a plausible-looking but wrong historical figure with no indication anything had been substituted.

## Delivered behaviour

When no `rule_set` has ever been published, resolution goes directly against `payroll_rule` rather than falling back to the current rate.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint A — SPRINT-A-2 (`payroll.py:519-599`).

## Implementation evidence

`backend/api/routes/payroll.py`. **No migration** — query-logic only.

## Test / review evidence

`docs/test-reports/2026-07-04-sprint-a-rule-versioning-integrity.md`.

## Decision references

Sprint A closed the correctness gap that had motivated the parked Sprint B lock/audit design — every live resolution call site is now date-driven.

## Dependencies

None.

## Delivery sprint(s)

Sprint A, 2026-07-04.

## Delivery history

- 2026-07-04 — delivered.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
