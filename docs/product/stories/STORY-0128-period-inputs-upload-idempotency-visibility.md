# `STORY-0128` — Period-inputs bulk upload idempotency — `IntegrityError` no longer a silent skip

**Origin code(s):** `PT-A3-16` · `UPLOAD-SKIP-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-14` — Bulk input upload & reconciliation intake
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

A row that violated a uniqueness constraint on upload was caught and skipped silently, so an operator uploading 200 inputs could be told it succeeded while some rows were never created — and never learn which.

## Delivered behaviour

Skipped rows are surfaced to the operator rather than swallowed, so a partially-applied upload is visible at the moment it happens.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-28-upload-error-visibility.md`, item UPLOAD-SKIP-1.

## Implementation evidence

Bulk input upload exception handling and the upload result surface.

## Test / review evidence

`docs/test-reports/2026-06-15-sprint-27-28.md`

## Decision references

Sprint 27/28's retro recorded the binding narrowing this required: an `IntegrityError` catch must be narrowed to `UniqueViolation` specifically — a broad catch masks genuine data defects. The related standing rule recorded outside this programme is that DB constraint hard failures are kept, never silently deduplicated or masked in the service layer.

## Dependencies

`STORY-0125` — the smart upload whose dedup this makes visible; `STORY-0017` — the original dedup guard.

## Delivery sprint(s)

Sprint 28.

## Delivery history

- Sprints 1–6 — dedup guard introduced silently (`STORY-0017`).
- Sprint 28 — the silence removed.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
