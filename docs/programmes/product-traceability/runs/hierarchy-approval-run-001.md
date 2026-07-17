# Run Record — hierarchy-approval-run-001

**Programme:** product-traceability
**Phase:** hierarchy approval (Phase 2)
**Date:** 2026-07-15
**Trigger:** `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`

## Start state

- Phase 1 (`discovery`) complete, per `runs/discovery-run-001.md`, critic verdict `approve-for-human-review`.
- `decisions.md` contained only D-001–D-006 (governance decisions from the bootstrap prompt).
- `decision-pack.md` contained DP-01–DP-07, all unresolved.
- `docs/product/` did not exist.
- Pre-existing, unrelated uncommitted working-tree changes present at run start (carried over from before the discovery phase and left untouched throughout it): `docs/ROADMAP.md` modification (pre-2026-07-12 Phase 1/2 numbering correction), `docs/test-harness-checklist.md` deletion, untracked `docs/test-reports/test-harness/`, untracked `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md`. All four remained untouched throughout this run as well.

## Human decisions received

Supplied verbatim in the triggering prompt:

| DP | Option | Summary |
|---|---|---|
| DP-01 | A | Retain 148-item granularity |
| DP-02 | A | Model A — flat registries |
| DP-03 | A | Adopt proposed source-of-truth rules as written |
| DP-04 | B | PH_OT `is_pensionable` still open; escalate outside programme |
| DP-05 | A | Classify 5 unresolved items as backlog/not-delivered |
| DP-06 | C | Investigate Gate 4 contradiction before trusting either source |
| DP-07 | A | Authorise and complete Phase 2 |

Recorded exactly, without reinterpretation, as D-007 through D-013 in `decisions.md`.

## Files changed

- `docs/programmes/product-traceability/decisions.md` — appended D-007–D-013.
- `docs/programmes/product-traceability/decision-pack.md` — each of DP-01–DP-07 annotated with a "**Resolved:**" line pointing to its binding decision; original questions, options, and executor recommendations preserved unmodified; a status banner added at the top of the file.
- `docs/programmes/product-traceability/PHASES.md` — Phase 1 marked complete; Phase 2 marked authorised-and-complete with executed allowed/forbidden paths and delivered outputs recorded; Phase 3 updated to reference `phase-3-inputs.md` and clarified as requiring its own explicit authorisation.
- `docs/programmes/product-traceability/phase-inputs.yaml` — `current_phase`/`current_phase_status` added; `recommended_next_phase_id` advanced to `structure-implementation`; `approved_decision_ids` extended to D-013; `unresolved_decision_ids` emptied (DP-01–DP-07 all resolved); new `follow_up_investigations_outside_programme` list added (PH_OT is_pensionable, Gate 4 contradiction); `proposed_allowed_paths_next_phase`/`proposed_outputs_next_phase` updated to the real Phase 3 scope; validation commands updated to match this prompt's required checks.
- `docs/programmes/product-traceability/exceptions.md` — Phase 2 section appended: no exception occurred.
- `docs/programmes/product-traceability/state.md` — rewritten to the true end-of-hierarchy-approval snapshot.
- `docs/programmes/product-traceability/phase-3-inputs.md` — new file; factual-only Phase 3 parameters (hierarchy, repository model, source-of-truth rules, proposed paths/outputs/validations); explicitly does not authorise Phase 3.
- `docs/programmes/product-traceability/runs/hierarchy-approval-run-001.md` — this file.
- `docs/programmes/product-traceability/critic-review-phase-2.md` — created by the independent critic (see below).

No file outside `docs/programmes/product-traceability/` was created or modified by this run.

## Validation commands and results

- `git status --short` — confirmed only files under `docs/programmes/product-traceability/` changed as new/modified by this run; the four pre-existing unrelated changes identified above were left untouched.
- `git diff --check` — clean.
- `find docs/programmes/product-traceability -maxdepth 2 -type f | sort` — lists exactly the files enumerated above (discovery-phase files plus this run's additions/edits).
- `test ! -e docs/product` — passes; `docs/product/` does not exist.
- Direct inspection: DP-01–DP-07 each appear exactly once as a resolved decision (D-007–D-013), with no duplicate or conflicting record. All control files (`PHASES.md`, `state.md`, `phase-inputs.yaml`) agree Phase 2 is complete and Phase 3 is not authorised. DP-04 and DP-06 remain visibly flagged as open follow-up investigations (in `decisions.md`, `decision-pack.md`, `phase-inputs.yaml`, and `state.md`) rather than being silently treated as resolved-and-closed.

## Executor summary

All seven decision-pack items were recorded exactly as supplied, with no reinterpretation or weakening. Phase 2 is closed accurately: the programme's control files agree on phase and gate status, the historical decision-pack trail remains visible (annotated, not erased), and Phase 3 was deliberately not authorised — `phase-3-inputs.md` supplies only factual preparation for a future, separate authorisation decision. `docs/product/` remains uncreated.

## Critic verdict

See `critic-review-phase-2.md` for the full independent critic review and verdict.

## Amendments made after criticism

None required. The critic's verdict was `approve` with no critical issues, guardrail gaps, decision-recording discrepancies, or required amendments — see `critic-review-phase-2.md` in full.

## Commit SHA(s)

`9f77532` — "docs: record product traceability hierarchy decisions", on branch `uat`. Scope: all of `docs/programmes/product-traceability/` (9 files changed). The pre-existing, unrelated uncommitted changes present throughout this run (`docs/ROADMAP.md` modification, `docs/test-harness-checklist.md` deletion, `docs/test-reports/test-harness/`, `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md`) were deliberately left unstaged and uncommitted — out of this programme's authorised scope.

## Outstanding follow-ups

- PH_OT `is_pensionable` deferral (D-010/DP-04) — open, owned outside this programme.
- Gate 4 status contradiction (D-012/DP-06) — open, owned outside this programme, requires targeted investigation.
- Phase 3 (`structure implementation`) authorisation — the operative next human gate for this programme itself.

## Next permitted action

**Human review and explicit authorisation of Phase 3 scope only.** Phase 3 must not begin, and `docs/product/` must not be created, without a further explicit human decision.
