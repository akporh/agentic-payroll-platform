# `STORY-0026` — Statutory rule `effective_from` UNIQUE constraint

**Origin code(s):** `PT-A5-05` · `G7`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-31` — Statutory & payroll rule versioning
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

auditor; payroll operator

## Problem addressed

Two statutory rules for the same country with the same effective date make the applicable rate ambiguous, and the engine's choice between them arbitrary.

## Delivered behaviour

A UNIQUE constraint on `statutory_rule (country_code, effective_from)` makes duplicate effective dates impossible.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A5, item G7.

## Implementation evidence

UNIQUE constraint on `statutory_rule (country_code, effective_from)` in `migrations/versions/`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Recorded as a standing data-contract invariant in `CLAUDE.md`: `statutory_rule (country_code, effective_from)` is UNIQUE — no duplicate effective dates.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Sprint RULE-VER-1 — the equivalent versioning discipline extended to `payroll_rule` (`STORY-0132`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. Migration-debt notes recorded outside this programme flag that this constraint's presence in the local dev database has drifted from migration truth; CI, which builds from `alembic upgrade head`, is the arbiter.
