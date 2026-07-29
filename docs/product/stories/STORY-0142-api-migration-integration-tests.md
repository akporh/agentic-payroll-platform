# `STORY-0142` — API / migration integration tests with workspace-isolation assertions

**Origin code(s):** `PT-A7-13`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; auditor

## Problem addressed

Workspace isolation and migration reversibility were both stated rules with nothing enforcing them — exactly the two properties whose failure is silent and expensive.

## Delivered behaviour

Integration tests across the API surface and migrations, including workspace-isolation assertions and an upgrade/downgrade smoke test.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-32-api-migration-tests.md`.

## Implementation evidence

`tests/` API and migration integration modules.

## Test / review evidence

Verified by the suite itself; baseline recorded in `docs/test-reports/test-harness/test-harness-checklist.md`.

## Decision references

Enforces two standing rules from `CLAUDE.md`: workspace scoping at the query level, and every migration upgrade having a working downgrade.

## Dependencies

`STORY-0139` — the fixture scaffold.

## Delivery sprint(s)

Sprint 32.

## Delivery history

- Sprint 32 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
