# `STORY-0112` — `proration_strategy` frozen in the snapshot (Q8-FIX) — closed by confirming existing behaviour

**Origin code(s):** `PT-A7-08` · `Q8-FIX`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-26` — Period & rule snapshot integrity
**Classification:** `discovery or architecture item`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

auditor

## Problem addressed

Audit finding AUD-14-1 observed that `proration_strategy` was not captured in `rules_context_snapshot`, raising the possibility that a retry would reprorate against a strategy changed since the original run.

## Delivered behaviour

**No code shipped.** Investigation established that `proration_strategy` is already frozen in `client_component_metadata_snapshot` at run start, and that retry reads from the snapshot rather than the live table. The finding was closed on that basis.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-14-1 / Q8 — recorded as "✅ Sprint 24 (no-code close)", citing `backend/application/snapshot_service.py`.

## Implementation evidence

None — the existing `backend/application/snapshot_service.py` behaviour was the answer.

## Test / review evidence

None dedicated — the close is an evidence finding, not a change.

## Decision references

A no-code close recorded honestly as such rather than presented as a delivery. Same principle as `STORY-0062`.

## Dependencies

`STORY-0043` — the retry-from-snapshot discipline this confirms; `STORY-0086` — the configurable proration whose strategy is snapshotted.

## Delivery sprint(s)

Sprint 14 (found) / Sprint 24 (closed).

## Delivery history

- Sprint 14 — raised as audit finding AUD-14-1.
- Sprint 24 — closed with no code change, by confirming existing behaviour already satisfied the requirement.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None. `PT-Q-08` is the Track Q register's duplicate code for this same item, and resolves to `STORY-0112`.
