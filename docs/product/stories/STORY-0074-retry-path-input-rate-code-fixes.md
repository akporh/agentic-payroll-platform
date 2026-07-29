# `STORY-0074` — Retry-path input and rate-code fixes

**Origin code(s):** `PT-A4-20`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-23` — Run retry & recovery
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator

## Problem addressed

The retry path diverged from the original run path in how it resolved inputs and rate codes, so a retry could produce a different figure from the run it was repeating.

## Delivered behaviour

Input and rate-code resolution on the retry path is aligned with the primary execution path.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O / Sprint 11.

## Implementation evidence

`backend/application/payroll_retry_service.py`.

## Test / review evidence

`docs/audit/2026-05-02-sprint-11-audit-review.md` — audit-reviewed; `docs/test-reports/2026-05-02-sprint-11.md`.

## Decision references

None beyond routine execution.

## Dependencies

None.

## Delivery sprint(s)

Sprint 11.

## Delivery history

- Sprint 11 — delivered and audit-reviewed.
- 2026-07-04 — a further retry-service divergence (missing date cap and `DISTINCT ON`) was found and fixed under `STORY-0135`.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

Retry-path divergence from the primary path has now been found twice, in Sprint 11 and Sprint A. No structural guarantee of parity between the two paths is recorded.
