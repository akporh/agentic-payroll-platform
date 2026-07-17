# `PT-A1-11` — WC-10/11: Statutory component override edit/toggle via UI

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-3` (see `../FEATURES.md`)
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator who needs to adjust a statutory component's (PAYE, Pension, NHF, etc.) proration strategy or active state for a specific workspace, or add an override for a platform component not yet configured for that workspace.

## Problem addressed

There was no UI for customising how a statutory deduction is calculated per workspace (proration strategy) or for adding a workspace-level override for a platform component that had not yet been configured — both required direct data manipulation.

## Delivered behaviour

`WorkspaceConfig.tsx` has an Edit action per component-override row (component name read-only, `is_active` toggle, `proration_strategy` select) and an "Add Override" SlideOver listing platform components not yet overridden for the workspace. Disabling a component surfaces an inline warning `AlertBanner`. Critically, the statutory-component guard is enforced server-side, not just in the UI: if `component_metadata.component_class = 'statutory_deduction'` for the workspace's country and the operator attempts `is_active = false`, the API hard-rejects with HTTP 422 ("cannot be disabled... statutory obligation under Nigerian law") — this is `PT-A1-16`, the backend half of the same WC-10 story. A country-scoped validation guard (D-ARCH-8) also rejects component codes that do not belong to the workspace's `country_code`.

## Source reference

`docs/ROADMAP.md` Track J item 41 (`WC-10/D-ARCH-2`); full acceptance criteria in `docs/stories/track-j-workspace-config-management.md`, sections "WC-10 — Edit / Toggle a Statutory Component Override" and "WC-11 — Add a Component Override for an Unconfigured Platform Component".

## Implementation evidence

- `docs/stories/track-j-workspace-config-management.md` — WC-10/WC-11 acceptance criteria (statutory hard-reject, country validation, unconfigured-component dropdown).
- `docs/ROADMAP.md` line 225: "Edit/toggle statutory component override via UI ✅ (WC-10/WC-11, Track J)".
- Commit `db17ef9` (2026-04-22) — Track J delivery commit; not independently isolated to a WC-10/11-only diff in this pass.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — WC-10 verified **PASS**/PASS ("D-ARCH-2 hard reject ✓, proration_strategy editable ✓"); WC-11 verified **PASS**/PASS ("New override created via PATCH upsert ✓, D-ARCH-8 country validation ✓").

## Decision references

- D-ARCH-2 (statutory hard-reject, no acknowledgment flag), D-ARCH-8 (component-code country validation) — `docs/stories/track-j-workspace-config-management.md`.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Depends on `PT-A1-15` (`client_component_metadata` `is_active`/`proration_strategy` migration) — explicitly called out in `docs/ROADMAP.md` Track J item 36 as "BLOCKER — must land first" for the whole Track J batch, and this story's fields (`is_active`, `proration_strategy` on `client_component_metadata`) are the direct columns that migration adds.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-21/22 — Track J — Edit/Add Component Override SlideOvers + PATCH upsert endpoint with D-ARCH-2/D-ARCH-8 guards delivered (commit `db17ef9`); verified PASS per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
