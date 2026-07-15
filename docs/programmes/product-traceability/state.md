# State — Product Traceability Programme

*Last updated: 2026-07-15, end of historical-migration-pilot-run-001 (Phase 4A). Authoritative snapshot — see `runs/discovery-run-001.md`, `runs/hierarchy-approval-run-001.md`, `runs/structure-implementation-run-001.md`, and `runs/historical-migration-pilot-run-001.md` for full run records.*

## Current phase

`historical migration` — **Phase 4A pilot only** authorised and complete (D-015). Phase 4 as a whole (the remaining ~146 discovery items) remains **not authorised**.

## Executor status

`complete` for discovery, hierarchy-approval, structure-implementation, and the Phase 4A pilot. Exactly two stories (`PT-A4-31`, `PT-A4-32`) migrated into `docs/product/`, with the minimum hierarchy rows needed to place them (`OUT-1`/`OUT-2`, `CAP-1`/`CAP-2`, `FEAT-1`/`FEAT-2`). No other historical item touched.

## Critic status

`complete` for discovery, hierarchy-approval, and structure-implementation phases (see prior verdicts below). Phase 4A pilot critic verdict: see `critic-review-phase-4a-pilot.md`.

**Prior verdicts:** Discovery: `approve-for-human-review` (`critic-review.md`). Hierarchy approval: `approve` (`critic-review-phase-2.md`). Structure implementation: `approve-with-amendments` (`critic-review-phase-3.md`) — two amendments required (this file was stale; the run record was missing) and applied; both were mechanical/documentation-only and did not touch `docs/product/` itself.

## Human-gate status

Discovery, hierarchy-approval, structure-implementation (D-014), and Phase 4A pilot (D-015) decisions: **received and recorded** (D-001–D-015). Full Phase 4 (historical migration of the remaining ~146 items) authorisation: **pending** — this is the current, unresolved human gate. Pilot completion does **not** auto-authorise it.

## Completed outputs

Discovery phase (`runs/discovery-run-001.md`): see that file's own listing.

Hierarchy-approval phase (`runs/hierarchy-approval-run-001.md`): see that file's own listing.

Structure-implementation phase (`runs/structure-implementation-run-001.md`): see that file's own listing (`docs/product/README.md`, empty registries, template, validation script).

Phase 4A pilot (`runs/historical-migration-pilot-run-001.md`):
- `docs/product/OUTCOMES.md` (2 content rows: `OUT-1`, `OUT-2`)
- `docs/product/CAPABILITIES.md` (2 content rows: `CAP-1`, `CAP-2`)
- `docs/product/FEATURES.md` (2 content rows: `FEAT-1`, `FEAT-2`)
- `docs/product/STORY-REGISTRY.md` (2 content rows: `PT-A4-31`, `PT-A4-32`)
- `docs/product/stories/PT-A4-31-component-source-trace-fix.md`, `docs/product/stories/PT-A4-32-timesheet-upload-size-guard.md`
- `docs/product/stories/TEMPLATE.md` (amended — 4 fields added: Outcome, Capability, Decision references, Dependencies, Delivery history — recorded as a genuine schema defect, see the run record)
- `docs/programmes/product-traceability/decisions.md` (D-015 appended)
- `docs/programmes/product-traceability/PHASES.md` (Phase 4 section updated: pilot authorised/active/complete-for-scope, remainder not authorised)
- `docs/programmes/product-traceability/phase-inputs.yaml` (current phase advanced; pilot outputs recorded)
- `docs/programmes/product-traceability/exceptions.md` (Phase 4A section appended — no exception)
- `docs/programmes/product-traceability/critic-review-phase-4a-pilot.md`
- `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md`

**`docs/product/` now contains exactly two migrated stories** and the minimum hierarchy rows to place them — no other row from the 148-item discovery inventory has been migrated.

## Blocked or outstanding decisions

- Full Phase 4 (`historical migration` of the remaining ~146 items) authorisation — not yet decided. No numbered DP item exists for it yet.
- Two follow-up investigations remain open, owned **outside** this programme: PH_OT `is_pensionable` deferral (D-010/DP-04) and the Gate 4 status contradiction (D-012/DP-06). Unaffected by this phase.
- Two duplicate-provisional-ID mappings surfaced by the pilot (`PT-A4-31`/`PT-Q-01`; `PT-A4-32`/`PT-S-07` — see each story file's "Unresolved questions") are not resolved by this pilot; a future migration pass should decide, with human input, whether to retire the duplicates or keep them as distinct historical markers.

## Next permitted action

**Human review of the Phase 4A pilot quality (registry rows, story files, critic verdict), and explicit authorisation of any broader Phase 4 migration batch scope only, if and when desired.** No executor action beyond recording is permitted. No further story may be migrated, and full Phase 4 must not begin, without a further explicit human decision.
