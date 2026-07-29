# `STORY-0077` — SEC-S5 — `shift_type` / `state_of_tax` / `skill_level` enum and length guards

**Origin code(s):** `PT-S-05` · `SEC-S5`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

engineer; payroll operator

## Problem addressed

The three employee fields added in Sprint 11 accepted arbitrary strings, so an out-of-range value could reach the engine — and an oversized one could produce a database truncation error whose message leaks the column name.

## Delivered behaviour

Allowlist enum validation and length guards on `shift_type`, `state_of_tax` and `skill_level` at the API boundary.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S5.

## Implementation evidence

Pydantic schema validation on the employee create/update schemas.

## Test / review evidence

`docs/security/2026-05-02-sprint-11-security-review.md`, `docs/test-reports/2026-05-02-sprint-11.md`.

## Decision references

Instance of the standing API rule in `CLAUDE.md`: a free-text field mapped to `VARCHAR(N)` must carry `max_length=N` in its Pydantic schema, or an oversized value leaks the column name in the DB error.

## Dependencies

`STORY-0071` — the schema fields being guarded.

## Delivery sprint(s)

Sprint 11.

## Delivery history

- Sprint 11 — delivered alongside the schema fields themselves.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
