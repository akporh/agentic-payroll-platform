# `STORY-0135` — Date cap and `DISTINCT ON` on the legacy current-period rule loader (SPRINT-A-3)

**Origin code(s):** `PT-A4-30` · `SPRINT-A-3`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-22` — Rule resolution & versioning behaviour
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; auditor

## Problem addressed

The legacy current-period rule loader had no `effective_from <= period_end` ceiling and no `DISTINCT ON`. The retry-service copy had neither, making its rule selection **non-deterministic** — a retry could pick a different rule than the original run.

## Delivered behaviour

Both loaders apply a date cap and `DISTINCT ON`, making rule selection deterministic and bounded by the run's own period.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint A — SPRINT-A-3 (`payroll.py:394-401`, `payroll_retry_service.py:312-320`).

## Implementation evidence

`backend/api/routes/payroll.py`; `backend/application/payroll_retry_service.py`. **No migration**.

## Test / review evidence

`docs/test-reports/2026-07-04-sprint-a-rule-versioning-integrity.md`.

## Decision references

Underpins the standing rule in `CLAUDE.md`: `payroll_rule.is_active` means “not withdrawn”, never “currently in effect” — resolution must always be date-driven, and `is_active` alone is never sufficient to select a single row.

## Dependencies

None.

## Delivery sprint(s)

Sprint A, 2026-07-04.

## Delivery history

- 2026-07-04 — delivered; two separate bugs in the same sprint both traced to treating `is_active` as “current”.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
