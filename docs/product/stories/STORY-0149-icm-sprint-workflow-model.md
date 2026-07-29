# `STORY-0149` — The ICM sprint-workflow model — `STAGE-REGISTRY.md` and `WORKFLOW.md`

**Origin code(s):** `PT-M-03`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-11` — Programme Governance & Assurance
**Feature:** `FEAT-41` — Sprint workflow model
**Classification:** `discovery or architecture item`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

programme owner; engineer

## Problem addressed

Sprint execution depended on remembering which review, audit, security and test gates applied — so gates were applied inconsistently and, in several recorded cases, late or not at all.

## Delivered behaviour

A modelled sprint workflow: a stage registry defining each stage's applicability, entry conditions, dependencies and completion criteria, and a workflow document defining how sprints move through them. It is the authority on gate mechanics; project instructions defer to it where they disagree.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/WORKFLOW.md`.

## Implementation evidence

Process artefact — the two control files plus the per-sprint workspaces under `docs/sprints/`.

## Test / review evidence

Validated across two pilot sprints, with five of six modelled scenarios proven on real data.

## Decision references

`CLAUDE.md` records that the registry governs where it and the project instructions appear to disagree, and that discrepancies are fixed in one place rather than maintained in two.

## Dependencies

None.

## Delivery sprint(s)

ICM sprint-workflow model — operating.

## Delivery history

- Operating and validated across two pilot sprints (`aud-q1-trace-source`, `sec-s7-timesheet-upload-guard`).
- 2026-07-16 — third sprint run under it (`dev-levy-rule-pct`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

One of six modelled scenarios remains unproven on real data. Integrating this traceability layer into sprint closure is Phase 5 of the product-traceability programme and is not yet authorised.
