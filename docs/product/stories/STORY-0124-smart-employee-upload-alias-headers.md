# `STORY-0124` — Smart employee upload — alias header detection and a mapping panel

**Origin code(s):** `PT-A1-37` · `EMP-NATIVE-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-10` — Bulk employee upload & import
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Every client's employee spreadsheet uses its own column names, so each upload required either reformatting the client's file or a bespoke template — friction at exactly the point a new client is onboarded.

## Delivered behaviour

Upload detects known header aliases automatically and presents a mapping panel where the operator confirms or corrects the column-to-field mapping, so a client's native file can be uploaded as-is.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-27-smart-native-upload.md`, item EMP-NATIVE-1.

## Implementation evidence

`frontend/src/` upload alias detection and mapping panel; bulk import handler.

## Test / review evidence

`docs/test-reports/2026-06-15-sprint-27-28.md`

## Decision references

Constrained by the Upload/Enroll separation in `CLAUDE.md`: the Excel grade column is informational — used for salary-definition auto-matching and the mapping panel — and must never be forwarded to `createEmployee`.

## Dependencies

`STORY-0109` — the upload/enroll separation this builds on.

## Delivery sprint(s)

Sprint 27.

## Delivery history

- Sprint 27 — delivered.
- Sprint 28 — upload error visibility improved across the upload surfaces (`STORY-0128`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
