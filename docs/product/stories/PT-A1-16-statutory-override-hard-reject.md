# `PT-A1-16` — Statutory component hard reject on override PATCH (D-ARCH-2, WC-10)

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-3` (see `../FEATURES.md`)
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

The platform itself, acting as a compliance guard against a payroll operator (or a bug in the frontend) attempting to disable a statutory deduction.

## Problem addressed

Disabling a statutory component (PAYE, Pension, NHF) is a compliance-sensitive action under Nigerian law — it must never be possible to silently turn one off for a workspace, whether via a UI bug, a direct API call, or an operator misunderstanding a toggle. A frontend-only warning is not a sufficient control.

## Delivered behaviour

The component-override PATCH endpoint (`PT-A1-11`'s backend) enforces a server-side hard reject: if `component_metadata.component_class = 'statutory_deduction'` for the workspace's country and the request sets `is_active = false`, the API returns HTTP 422 with the message "[COMPONENT] cannot be disabled. It is a statutory obligation under Nigerian law." There is no acknowledgment flag or override path — this is an unconditional reject, by explicit arch-council decision (D-ARCH-2), enforced independently of whatever the frontend does or fails to do.

## Source reference

`docs/ROADMAP.md` Track J item 41 (`WC-10/D-ARCH-2`, "Statutory component hard reject on component-override PATCH | Onboarding (A1) | WC-10/D-ARCH-2 | 422 for statutory_deduction class").

## Implementation evidence

- `docs/stories/track-j-workspace-config-management.md` — D-ARCH-2 in the "Arch-Council Decisions Reference" table: "Statutory suppression: server-side 422 hard reject for `is_active=false` on `component_class='statutory_deduction'`. No acknowledgment flag."
- Commit `db17ef9` (2026-04-22) — Track J delivery commit; not independently isolated to a D-ARCH-2-only diff in this pass (the guard is implemented inside the same PATCH handler as WC-10/WC-11).

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — WC-10 verified **PASS**: "D-ARCH-2 hard reject ✓, proration_strategy editable ✓."

## Decision references

- D-ARCH-2 (`docs/stories/track-j-workspace-config-management.md`).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Shares its implementation with `PT-A1-11` (WC-10/11 edit/toggle UI) — this is the backend compliance-guard half of the same PATCH endpoint. Depends on `PT-A1-15`'s migration for the `is_active` column it is guarding.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-22 — Track J — server-side 422 hard reject for disabling statutory components delivered as part of the WC-10 PATCH endpoint (commit `db17ef9`); verified PASS per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
