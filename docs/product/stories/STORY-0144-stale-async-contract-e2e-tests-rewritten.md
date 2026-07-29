# `STORY-0144` — Four stale async-contract e2e tests rewritten for backgrounded execution

**Origin code(s):** `PT-A7-14` · `TF-3`–`TF-7`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

engineer

## Problem addressed

Four end-to-end tests asserted against a synchronous execution contract that no longer existed — payroll execution had moved to a background task, so the tests were failing for a reason that had nothing to do with the behaviour they were meant to protect.

## Delivered behaviour

The four tests are rewritten to match backgrounded execution, restoring a green suite without weakening what they assert.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Known Test Failures table, which cites commit `2a069d6` directly.

## Implementation evidence

`tests/` — the four rewritten e2e modules. Commit `2a069d6`.

## Test / review evidence

`docs/test-reports/test-harness/test-harness-checklist.md`.

## Decision references

The lesson recorded in the PAY-TAX-1 retro is the general form of this: a sprint that backgrounds a task breaks every test asserting on the HTTP response body, and that breakage is a contract change, not a flake.

## Dependencies

`STORY-0140` — the baseline these failures were measured against.

## Delivery sprint(s)

Test harness workstream (2026-07-12).

## Delivery history

- 2026-07-12 — delivered; the Known Test Failures table cleared.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
