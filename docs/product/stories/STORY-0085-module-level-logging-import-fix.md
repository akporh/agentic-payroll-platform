# `STORY-0085` — SEC-S3 — module-level logging import fix

**Origin code(s):** `PT-S-03` · `SEC-S3`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer

## Problem addressed

A missing or misplaced logging import meant the server-side error logging that the other Track S fixes depend on could fail at the moment it was most needed.

## Delivered behaviour

The logging import is moved to module level so the logger is available on every code path in the module.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S3; `docs/stories/sprint-13-track-m3-m5-track-s-security.md`.

## Implementation evidence

Import placement in the affected route module.

## Test / review evidence

None dedicated — covered within the Sprint 13 security track scope.

## Decision references

None.

## Dependencies

None — but `STORY-0083` depends on this working.

## Delivery sprint(s)

Sprint 13 (Track S).

## Delivery history

- Sprint 13 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report isolates the Track S items in this sprint.
