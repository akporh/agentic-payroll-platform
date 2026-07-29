# `STORY-0139` — Test-fixture scaffold — `conftest.py`, db / workspace / employee fixtures

**Origin code(s):** `PT-X-02` · `HARN-1`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer

## Problem addressed

There was no shared way to stand up a database, a workspace and an employee for a test, so every test that needed them would have built its own — which is why almost none existed.

## Delivered behaviour

A `conftest.py` providing `db_engine`, `db_session`, workspace and employee fixtures.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-30-test-harness.md` (HARN-1) — which states explicitly that no feature tests were written this sprint, only the scaffold.

## Implementation evidence

`tests/conftest.py` and the fixture definitions.

## Test / review evidence

None — this item *is* test infrastructure; it is verified by the suites later built on it.

## Decision references

Fixture rules recorded in `CLAUDE.md` for anyone adding e2e tests: declare registry activation via `tests/registry_state.py` and restore it in a `finally`; statutory `effective_from` must be later than every migration seed and must not collide on the UNIQUE constraint; a direct `INSERT INTO employee` must include `employee_number`.

## Dependencies

None.

## Delivery sprint(s)

Sprint 30.

## Delivery history

- Sprint 30 — scaffold delivered, deliberately with no feature tests.
- Sprint 31 — financial-engine suite built on it (`STORY-0141`).
- Sprint 32 — API/migration suite built on it (`STORY-0142`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
