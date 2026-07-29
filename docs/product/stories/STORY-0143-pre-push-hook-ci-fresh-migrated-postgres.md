# `STORY-0143` — Pre-push hook and CI workflow enforcing the full suite against a fresh-migrated Postgres

**Origin code(s):** `PT-X-03`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-38` — CI/CD pipeline & branch protection
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

engineer

## Problem addressed

A suite that only runs when someone remembers to run it, against a developer database that has drifted from migration truth, proves very little.

## Delivered behaviour

A `.githooks/pre-push` hook running pytest and `tsc --noEmit` before every push, and a CI workflow running the suite on push/PR to `uat` and `main` against a **fresh Postgres built from `alembic upgrade head`**.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`CLAUDE.md` Test Harness section, citing `.githooks/pre-push` and `.github/workflows/tests.yml` directly.

## Implementation evidence

`.githooks/pre-push`; `.github/workflows/tests.yml`; `core.hooksPath` set to `.githooks`.

## Test / review evidence

`docs/test-reports/test-harness/test-harness-checklist.md` — the suite is green and enforced automatically.

## Decision references

Records the arbitration rule that matters most here: the local dev database is confirmed drifted from migration truth (registry activation flips, missing constraints), so **CI is the arbiter** and tests must not depend on dev-DB state.

## Dependencies

`STORY-0138` — the CI gate this gave a real suite to run; `STORY-0140` — the baseline being enforced.

## Delivery sprint(s)

Test harness workstream (2026-07-12).

## Delivery history

- Sprint 29 — CI gate and branch protection (`STORY-0138`).
- 2026-07-12 — pre-push hook and fresh-migrated CI workflow delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
