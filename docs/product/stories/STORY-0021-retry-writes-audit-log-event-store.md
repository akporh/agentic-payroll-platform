# `STORY-0021` — Retry writes to `audit_log` and `event_store` (P2-3)

**Origin code(s):** `PT-A4-08` · `P2-3`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-23` — Run retry & recovery
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor

## Problem addressed

A retry changes payroll figures. If it left no audit record, the run's history would not explain how a value changed.

## Delivered behaviour

Retries write to both `audit_log` and `event_store`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): “Retry writes to audit_log and event_store ✅ (P2-3)”.

## Implementation evidence

`backend/application/payroll_retry_service.py`.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

None recorded at the time.

## Dependencies

Depends on `STORY-0020`.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered as P2-3.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Audit writes elsewhere in the platform are post-commit and fire-and-forget (finding F-06-02 of the architecture-review programme). Whether the retry path shares that weakness is not established here.
