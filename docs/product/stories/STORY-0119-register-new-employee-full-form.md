# `STORY-0119` — Register a new employee — full form

**Origin code(s):** `PT-A1-32` · `EMP-REG-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator; HR admin

## Problem addressed

Bulk upload was the only practical creation path, so registering a single new hire meant preparing a one-row spreadsheet.

## Delivered behaviour

A full registration form for creating one employee directly, covering the HR fields the upload path carries.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-26-employee-registration-status-management.md`, item EMP-REG-1.

## Implementation evidence

`frontend/src/` registration form; `createEmployee` client.

## Test / review evidence

`docs/test-reports/2026-06-11-sprint-26.md`

## Decision references

Consistent with the Upload/Enroll separation (`STORY-0109`) — registration sends HR data only.

## Dependencies

`STORY-0102` — the unified creation path this calls.

## Delivery sprint(s)

Sprint 26 (2026-06-11).

## Delivery history

- Sprint 26 — delivered.
- Sprint 25 had already added contract dates to this surface (`STORY-0117`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
