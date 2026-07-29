# `STORY-0157` — “Percentage of basic” earning rule configurable via UI (RULE-PCT-1)

**Origin code(s):** `RULE-PCT-1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-18` — Core calculation & component execution
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin

## Problem addressed

Operators could not configure a “percentage of basic” earning rule from the UI. The engine already supported it via `percentage_of_sum` — the gap was UI-only. Separately, the rule form's `PERCENTAGE_OF_GROSS` option emitted an invalid calculation-method string that the DB CHECK constraint rejected outright.

## Delivered behaviour

The rule form offers percentage-of-basic configuration for earnings, emitting a calculation method the engine and the CHECK constraint both accept. The invalid `PERCENTAGE_OF_GROSS` method string is corrected.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/sprints/dev-levy-rule-pct/CONTEXT.md` — Story 2, RULE-PCT-1 (P2).

## Implementation evidence

`frontend/src/pages/WorkspaceConfig.tsx` (`buildDefinition` payload shape); engine support pre-existed via `percentage_of_sum`.

## Test / review evidence

`docs/test-reports/2026-07-16-dev-levy-rule-pct.md` — 327 passed / 1 intentional skip / 0 failed; verdict **PASS**. The SlideOver UI is verified by CODE REVIEW; the API/DB behaviour it drives, including the exact `buildDefinition` payload, is LIVE-verified.

## Decision references

`docs/sprints/dev-levy-rule-pct/decisions.md` DEC-01–DEC-10. Percentage-of-basic is scoped to **earnings only**.

## Dependencies

None.

## Delivery sprint(s)

ICM sprint `dev-levy-rule-pct`, closed 2026-07-16.

## Delivery history

- 2026-07-16 — delivered and verified; `docs/test-reports/2026-07-16-dev-levy-rule-pct.md` PASS.
- 2026-07-28 — captured into `docs/product/` under D-026 (absent from the discovery inventory, which has a 2026-07-15 horizon).
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

None.
