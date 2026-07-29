# `STORY-0053` — Extend `/configuration` GET with IDs/is_active/proration_strategy

**Origin code(s):** `PT-A1-17`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Not directly user-facing — this is the read-side API contract the entire Track J `WorkspaceConfig.tsx` frontend (all WC-1→WC-11 SlideOvers) is built on.

## Problem addressed

The pre-Track-J `GET /{wid}/configuration` aggregate endpoint did not expose the row IDs, `is_active`, or `proration_strategy` fields the new edit/toggle SlideOvers needed to route their PATCH calls and pre-fill their forms.

## Delivered behaviour

`GET /{workspace_id}/configuration` (`backend/api/routes/workspace.py:1124`, `get_workspace_configuration`) now returns, among other sections: `salary_definitions` including `salary_definition_id` ("include ID for PATCH routing" — inline code comment); `payroll_rules` including `rule_id`, `is_active`, and `effective_from` for all versions (active and inactive); and component overrides including `is_active` and `proration_strategy` ("include is_active + proration_strategy columns (post-migration)" — inline code comment referencing the `STORY-0051` (was `PT-A1-15`) migration).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 42 ("Extend GET `/{wid}/configuration` — add IDs, is_active, proration_strategy | Onboarding (A1) | All WC | Needed by frontend").

## Implementation evidence

- `backend/api/routes/workspace.py:1124-1201` — `get_workspace_configuration`, confirmed present by direct inspection during this migration pass: `salary_definition_id` selected at line 1173, `pr.rule_id, ..., pr.is_active, ..., pr.effective_from` selected at lines 1182–1189, `component_code, overrides_json, is_active, proration_strategy` selected at line 1197 with the inline comment "post-migration."
- Commit `db17ef9` (2026-04-22) — Track J delivery commit; not independently isolated to a configuration-GET-only diff in this pass.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — all of WC-1, WC-2 through WC-5, WC-7, WC-8, WC-10, WC-11 verified PASS at the frontend layer, each of which depends on this endpoint returning the IDs/flags it pre-fills into its SlideOver; no standalone test item names the `/configuration` GET endpoint directly, so this is inferred from the dependent stories' PASS verdicts plus direct code inspection, not a dedicated `/configuration`-only test entry.

## Decision references

- None beyond the general Track J arch-council review.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Depends on `STORY-0051` (was `PT-A1-15`) (the `client_component_metadata.is_active`/`proration_strategy` migration) for the columns it now returns in the component-overrides section.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-22 — Track J — `/configuration` GET extended with salary-definition IDs, rule IDs/is_active/effective_from, and component-override is_active/proration_strategy (commit `db17ef9`); exercised indirectly via the PASS verdicts of every dependent WC-* frontend story in `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
