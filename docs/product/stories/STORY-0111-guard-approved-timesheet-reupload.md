# `STORY-0111` — Guard APPROVED timesheet re-upload (Q6-FIX)

**Origin code(s):** `PT-A7-07` · `Q6-FIX`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-27` — Audit-observation remediation
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

auditor; payroll operator

## Problem addressed

Re-uploading a timesheet overwrote entries that had already been APPROVED, with no guard — destroying the approved record that the payroll inputs were derived from. `CLAUDE.md` describes this as an evidence-destruction risk.

## Delivered behaviour

Approved timesheet IDs are prefetched before the upsert loop and rejected per employee, so an APPROVED entry cannot be overwritten by a re-upload.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q register, AUD-16-2 / Q6 — found Sprint 16, closed Sprint 24.

## Implementation evidence

`backend/application/timesheet_derivation_service.py` — approved-ID prefetch and per-employee rejection.

## Test / review evidence

None dedicated — Sprint 24 has no separate test report; the roadmap records the finding as Resolved with the implementing file named.

## Decision references

Closes Track Q audit finding AUD-16-2.

## Dependencies

`STORY-0090` — the upload path guarded; `STORY-0093` — the approval state being protected.

## Delivery sprint(s)

Sprint 16 (found) / Sprint 24 (closed).

## Delivery history

- Sprint 16 — raised as audit finding AUD-16-2.
- Sprint 24 — closed by the prefetch-and-reject guard.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None. `PT-Q-06` is the Track Q register's duplicate code for this same item, and resolves to `STORY-0111`.
