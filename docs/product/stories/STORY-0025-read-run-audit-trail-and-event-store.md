# `STORY-0025` — Read a run's audit trail and event-store history

**Origin code(s):** `PT-A5-04` · `P2-1`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-30` — Audit trail & actor attribution
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor; payroll operator

## Problem addressed

Audit events were being written but could not be read back, so the audit trail was unverifiable from the application.

## Delivered behaviour

Endpoints to read a run's `audit_log` entries and its `event_store` history.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5, item P2-1.

## Implementation evidence

Audit-trail read routes in `backend/api/routes/payroll.py`; `audit_log` and `event_store` tables.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

`STORY-0021` — retry writes to the same two tables.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. Actor identity on these entries remained incomplete — see `STORY-0041` and the still-open `STORY-0153`.
