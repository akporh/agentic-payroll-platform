# State — Product Traceability Programme

*Last updated: 2026-07-15, end of historical-migration-confirmed-batch-run-001 (Phase 4B). Authoritative snapshot — see `runs/discovery-run-001.md`, `runs/hierarchy-approval-run-001.md`, `runs/structure-implementation-run-001.md`, `runs/historical-migration-pilot-run-001.md`, and `runs/historical-migration-confirmed-batch-run-001.md` for full run records.*

## Current phase

`historical migration` — **Phase 4A pilot** (D-015) and **Phase 4B confirmed-batch, capability area A1+A2** (D-016) both authorised and complete for their authorised scope. Phase 4 as a whole (every other capability area's confirmed items, and every strongly-inferred/tentative/requires-human-classification item anywhere) remains **not authorised**.

## Executor status

`complete` for discovery, hierarchy-approval, structure-implementation, the Phase 4A pilot, and the Phase 4B confirmed-batch. 21 stories total migrated into `docs/product/`: 2 from Phase 4A (`PT-A4-31`, `PT-A4-32`) and 19 from Phase 4B (`PT-A1-07/08/09/10/11/15/16/17/18/19/20/21/22/25/28/38/39/41/42`), with the minimum hierarchy rows to place them (`OUT-1/2/3`, `CAP-1/2/3`, `FEAT-1/2/3/4/5`). No other historical item touched.

## Critic status

`complete` for discovery, hierarchy-approval, structure-implementation, and Phase 4A pilot phases (see prior verdicts below). Phase 4B confirmed-batch critic verdict: see `critic-review-phase-4b-confirmed-batch.md`.

**Prior verdicts:** Discovery: `approve-for-human-review` (`critic-review.md`). Hierarchy approval: `approve` (`critic-review-phase-2.md`). Structure implementation: `approve-with-amendments` (`critic-review-phase-3.md`) — two mechanical amendments applied. Phase 4A pilot: `approve-with-amendments` (`critic-review-phase-4a-pilot.md`) — one mechanical amendment (stale file-path references after a mid-run rename) applied.

## Human-gate status

Discovery, hierarchy-approval, structure-implementation (D-014), Phase 4A pilot (D-015), and Phase 4B confirmed-batch (D-016) decisions: **received and recorded** (D-001–D-016). Full Phase 4 (historical migration of every remaining item) authorisation: **pending** — this is the current, unresolved human gate. Neither batch's completion auto-authorises it.

## Completed outputs

Discovery phase (`runs/discovery-run-001.md`): see that file's own listing.

Hierarchy-approval phase (`runs/hierarchy-approval-run-001.md`): see that file's own listing.

Structure-implementation phase (`runs/structure-implementation-run-001.md`): see that file's own listing (`docs/product/README.md`, empty registries, template, validation script).

Phase 4A pilot (`runs/historical-migration-pilot-run-001.md`):
- `docs/product/OUTCOMES.md` (`OUT-1`, `OUT-2`)
- `docs/product/CAPABILITIES.md` (`CAP-1`, `CAP-2`)
- `docs/product/FEATURES.md` (`FEAT-1`, `FEAT-2`)
- `docs/product/STORY-REGISTRY.md` (`PT-A4-31`, `PT-A4-32`)
- `docs/product/stories/PT-A4-31-component-source-trace-fix.md`, `docs/product/stories/PT-A4-32-timesheet-upload-size-guard.md`
- `docs/product/stories/TEMPLATE.md` (amended — 4 fields added: Outcome, Capability, Decision references, Dependencies, Delivery history — recorded as a genuine schema defect, see the run record)
- `docs/programmes/product-traceability/decisions.md` (D-015 appended)
- `docs/programmes/product-traceability/critic-review-phase-4a-pilot.md`
- `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md`

Phase 4B confirmed-batch (`runs/historical-migration-confirmed-batch-run-001.md`):
- `docs/product/OUTCOMES.md` — added `OUT-3` (Operationally usable payroll administration)
- `docs/product/CAPABILITIES.md` — added `CAP-3` (Onboarding & Workforce Setup); added `outcome_name` display column to all rows
- `docs/product/FEATURES.md` — added `FEAT-3`/`FEAT-4`/`FEAT-5`; added `capability_name` display column to all rows
- `docs/product/STORY-REGISTRY.md` — added 19 rows (`PT-A1-07/08/09/10/11/15/16/17/18/19/20/21/22/25/28/38/39/41/42`); added `feature_name` display column to all rows
- 19 new story files under `docs/product/stories/`
- `docs/product/README.md` — status and validation-mechanism sections updated for the batch and the human-readable-name convention
- `docs/product/validate_registry.py` — extended: name-matching enforcement, duplicate-ID rejection, ambiguous-prefix rejection
- `docs/programmes/product-traceability/decisions.md` (D-016 appended)
- `docs/programmes/product-traceability/PHASES.md` (Phase 4 section updated: both batches recorded, remainder not authorised)
- `docs/programmes/product-traceability/phase-inputs.yaml` (current phase advanced; batch outputs recorded)
- `docs/programmes/product-traceability/exceptions.md` (Phase 4B section appended)
- `docs/programmes/product-traceability/critic-review-phase-4b-confirmed-batch.md`
- `docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md`

**`docs/product/` now contains exactly 21 migrated stories** (2 from Phase 4A, 19 from Phase 4B) and the minimum hierarchy rows to place them — no other row from the 148-item discovery inventory has been migrated. **This is not a claim that all confirmed stories are migrated** — only capability area A1+A2's 19 confirmed items and the two Phase 4A pilot items have been; the other capability areas' confirmed items (e.g. 13 in A4 Execution, of which 2 are already covered by Phase 4A) remain unmigrated pending a further, separate authorisation.

## Blocked or outstanding decisions

- Full Phase 4 (`historical migration` of every remaining item) authorisation — not yet decided. No numbered DP item exists for it yet.
- Two follow-up investigations remain open, owned **outside** this programme: PH_OT `is_pensionable` deferral (D-010/DP-04, item `PT-A1-02` — not part of either migrated batch) and the Gate 4 status contradiction (D-012/DP-06, item `PT-UI-04` — not part of either migrated batch). Unaffected by either batch.
- Two duplicate-provisional-ID mappings surfaced by the Phase 4A pilot (`PT-A4-31`/`PT-Q-01`; `PT-A4-32`/`PT-S-07` — see each story file's "Unresolved questions") remain unresolved.
- Phase 4B surfaced several items whose evidence was weaker than the discovery document's blanket `confirmed` label implied but were migrated anyway on the strength of direct code inspection performed during the batch (most notably `PT-A1-09`'s add-flow, and `PT-A1-25`'s browser-UAT-blocked status shared with the excluded `PT-A1-23`) — see the run record and `critic-review-phase-4b-confirmed-batch.md` for the full list and the critic's assessment of whether migrating them anyway was justified.

## Next permitted action

**Human review of the Phase 4A and Phase 4B batch quality (registry rows, story files, critic verdicts), and explicit authorisation of any further Phase 4 migration batch scope only, if and when desired.** No executor action beyond recording is permitted. No further story may be migrated, and full Phase 4 must not begin, without a further explicit human decision.
