# `STORY-0017` — Bulk upload payroll inputs with a duplicate guard

**Origin code(s):** `PT-A3-05` · `P3-3`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-5` — Pay Events & Inputs
**Feature:** `FEAT-14` — Bulk input upload & reconciliation intake
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

Entering a month's variable inputs one at a time is impractical for a bureau, and re-uploading a corrected file must not double the inputs already loaded.

## Delivered behaviour

Bulk upload of payroll inputs from a file, with a duplicate guard so a re-uploaded row does not create a second input.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A3, item P3-3.

## Implementation evidence

Bulk input upload route and repository dedup path.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Sprint 27 — replaced by the smart period-inputs upload (`STORY-0125`).
- Sprint 28 — the dedup path's silent-skip behaviour made visible to the operator (`STORY-0128`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
