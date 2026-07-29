# `STORY-0141` — Financial-engine unit test suite — all six `calculation_method` values, Decimal-exact

**Origin code(s):** `PT-A7-12` · `TEST-A1`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; auditor

## Problem addressed

The calculation engine — the part of the platform whose errors are financial — had no unit-level coverage of its calculation methods.

## Delivered behaviour

A unit test suite covering all six live `calculation_method` values with Decimal-exact assertions rather than float comparison.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-31-financial-engine-tests.md` (TEST-A1).

## Implementation evidence

`tests/` financial engine test modules.

## Test / review evidence

Verified by the suite itself; baseline recorded in `docs/test-reports/test-harness/test-harness-checklist.md`.

## Decision references

Enforces the standing rule in `CLAUDE.md` that all monetary values use `Decimal`, never float. The six live methods are wider than the rule-type options the UI offers, which is recorded outside this programme.

## Dependencies

`STORY-0139` — the fixture scaffold.

## Delivery sprint(s)

Sprint 31.

## Delivery history

- Sprint 31 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
