# `STORY-0041` — `X-Performed-By` header read on approve / lock / retry routes

**Origin code(s):** `PT-A5-06` · `P2-2`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-30` — Audit trail & actor attribution
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

auditor

## Problem addressed

Governance actions were recorded without an actor, so the audit trail could say a run was approved but not by whom.

## Delivered behaviour

The backend reads an `X-Performed-By` header on the approve, lock and retry routes and records it against the audit entry.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5, item P2-2 — marked ⚠️, not ✅.

## Implementation evidence

Header read in the approve/lock/retry handlers in `backend/api/routes/payroll.py`.

## Test / review evidence

`docs/test-reports/2026-04-14-sprint-7.md`

## Decision references

None.

## Dependencies

`STORY-0024` — the routes this attributes; `STORY-0025` — the audit trail it writes into.

## Delivery sprint(s)

Sprint 7.

## Delivery history

- Sprint 7 — backend half delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Genuinely incomplete, and recorded as such rather than rounded up.** The roadmap marks this ⚠️: the backend reads the header but the frontend does not send it. End-to-end actor attribution therefore does not work. Confidence is `tentative` for that reason. The related timesheet-transition actor-identity gap is separately tracked as the still-open `STORY-0153`.
