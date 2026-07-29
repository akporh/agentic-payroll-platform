# `STORY-0110` — AlertBanner with CTA and nav badge when enrollment is not yet possible

**Origin code(s):** `PT-A1-30` · `EMP-UX-5`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-8` — Enrollment & payroll readiness
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

payroll operator

## Problem addressed

An operator who had uploaded employees but had no salary structure yet found the enroll action simply inert, with nothing explaining why or what to do next.

## Delivered behaviour

An `info` AlertBanner with a "Set up salary structure →" call to action when no salary definitions exist, and a navigation badge showing the not-enrolled count, taking priority over the unmatched count.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint 24, item EMP-UX-5.

## Implementation evidence

`frontend/src/pages/Employees.tsx` alert banner; sidebar badge count logic.

## Test / review evidence

None dedicated — Sprint 24 has no separate test report; the roadmap records the items ✅.

## Decision references

Sprint 26's retro later recorded that this badge's count logic had an OR-versus-sum defect, and that state-variable partitions must be audited — see `STORY-0122`.

## Dependencies

`STORY-0130` — the workspace-activation CTA coverage this complements.

## Delivery sprint(s)

Sprint 24.

## Delivery history

- Sprint 24 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for Sprint 24; confidence is `strongly inferred` from the roadmap.
