# `STORY-0109` — Bulk upload / bulk enroll separation

**Origin code(s):** `PT-A1-40` · `EMP-BULK-1` · `EMP-BULK-2` · `EMP-BULK-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-10` — Bulk employee upload & import
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; HR admin

## Problem addressed

Uploading an employee and assigning them to payroll were conflated in one operation, so registering someone as an HR record forced a payroll setup decision at the same moment — often before the answer was known.

## Delivered behaviour

Two distinct operations. **Upload** registers the HR record and sends HR data only — name, employee number, TIN, RSA, bank, contract dates. **Enroll** assigns to payroll and sends `salary_definition_code`, `grade_code` and `designation_code`. During bulk upload `grade_code` is always null; the Excel grade column is informational only.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 22 (EMP-BULK-1/2/3); the separation is documented as a standing rule in `CLAUDE.md`.

## Implementation evidence

`frontend/src/` `createEmployee` / `enrollEmployee` / `bulkEnrollEmployees` clients and the bulk import handler; the corresponding backend routes.

## Test / review evidence

`docs/test-reports/2026-06-08-sprint-22.md`.

## Decision references

Recorded as a standing rule in `CLAUDE.md`'s Upload / Enroll Separation section — the two operations must not be re-conflated, and the raw Excel grade must never be forwarded to `createEmployee`. Sprint 22's retro added the further lessons that a bulk import must enumerate all fields including nulls, and that smart-filtering fields is still coupling.

## Dependencies

`STORY-0102` — the unified employee creation path both operations use.

## Delivery sprint(s)

Sprint 22.

## Delivery history

- Sprint 22 — delivered as EMP-BULK-1/2/3.
- Sprint 27 — smart upload built on the upload half (`STORY-0124`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
