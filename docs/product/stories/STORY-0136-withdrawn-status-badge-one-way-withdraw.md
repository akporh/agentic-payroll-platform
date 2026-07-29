# `STORY-0136` — WITHDRAWN status badge and a one-way withdraw action

**Origin code(s):** `PT-A5-08` · `B-UI-1` · `B-UI-2` · `B-UI-3`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-31` — Statutory & payroll rule versioning
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin

## Problem addressed

The rules UI still offered an Activate/Deactivate toggle after versioning shipped. That toggle was actively misleading: it implied a rule could be switched back on, when under versioning `is_active` means "not withdrawn" and withdrawal is not reversible.

## Delivered behaviour

The toggle is replaced by a one-way withdraw action and a WITHDRAWN status badge, so the UI states what the data model actually permits.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint B-UI (B-UI-1/2/3).

## Implementation evidence

`frontend/src/` payroll rules tab — status badge and withdraw action.

## Test / review evidence

None dedicated — the roadmap records B-UI-1/2/3 as ✅ complete.

## Decision references

The UI gate rule recorded outside this programme applies directly: **no Toggle-as-indicator** — a control that looks two-way must be two-way.

## Dependencies

`STORY-0132` — the versioning model whose semantics this surfaces correctly.

## Delivery sprint(s)

Sprint B-UI.

## Delivery history

- Sprint B-UI — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report for Sprint B-UI.
