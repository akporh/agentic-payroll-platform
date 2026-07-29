# `STORY-0138` — Dead branch cleanup, CI gate on merge, branch protection on `main`

**Origin code(s):** `PT-X-01` · `PIPE-1` · `PIPE-2` · `PIPE-3`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-38` — CI/CD pipeline & branch protection
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer

## Problem addressed

Accumulated dead branches made the repository hard to reason about, and nothing prevented a merge to `main` that had not passed anything.

## Delivered behaviour

Dead branches removed, a CI gate required on merge, and branch protection applied to `main`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/stories/sprint-29-pipeline.md` (PIPE-1/2/3).

## Implementation evidence

`.github/workflows/` CI configuration; repository branch-protection settings.

## Test / review evidence

None dedicated — verified by the gate being in force.

## Decision references

None.

## Dependencies

None — `STORY-0143` later made the gate meaningful by giving it a real suite to run.

## Delivery sprint(s)

Sprint 29.

## Delivery history

- Sprint 29 — delivered.
- 2026-07-12 — the CI workflow rebuilt to run the full suite against a fresh-migrated Postgres (`STORY-0143`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
