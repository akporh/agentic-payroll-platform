# `STORY-0020` — Retry failed employees; full-run retry; retry recalculates totals (P0-2 / P1-1)

**Origin code(s):** `PT-A4-07` · `P0-2` · `P1-1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-23` — Run retry & recovery
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

A run where some employees failed had no recovery path short of re-running everything, and a partial retry that did not recalculate totals would leave the run internally inconsistent.

## Delivered behaviour

Failed employees can be retried from the UI; a full-run retry existed; a retry recalculates run totals rather than leaving stale figures.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Phase 1 — Sprints 1–6, Execution (A4): retry entries P0-2, P1-1.

## Implementation evidence

`backend/application/payroll_retry_service.py`.

## Test / review evidence

No dedicated report for Sprints 1–6.

## Decision references

`retry_strategy` is per-run on `payroll_run`, never on Workspace.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Later — `FULL_RUN` was disabled by migration; `PER_EMPLOYEE` is the only permitted strategy (`CLAUDE.md`).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

This story records full-run retry as delivered, but `payroll_retry_request.retry_strategy` now permits `PER_EMPLOYEE` **only**, with `FULL_RUN` disabled by migration. The capability described here is partly withdrawn; the withdrawing change is not itself inventoried.
