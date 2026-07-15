# Decisions — Product Traceability Programme

This is the programme-level decision register. It records only actual approved decisions. Recommendations remain in `decision-pack.md` until a human approves them and they are moved here.

---

## D-001 — Adopt phase-level autonomy with an independent critic gate

**Date:** 2026-07-15
**Approved by:** Michael Emedo (via the bootstrap prompt `docs/diagnostics/2026-07-15-prompt-bootstrap-product-traceability-programme-with-critic.md`)
**Decision:** The executor may complete an entire authorised phase without requesting intermediate confirmation, but may not approve its own recommendations, write its own continuation prompt, or execute the next phase. An independent, read-only critic reviews the executor's outputs before human review.
**Effect:** Governs `POLICY.md` autonomy mode and the critic-gate requirement in this programme.

## D-002 — Executor/critic role separation

**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** The critic role must be independent from the executor role, read-only, and must review executor outputs against fixed programme policy and a fixed rubric. The critic does not edit executor artefacts and does not authorise execution of the next phase.
**Effect:** Implemented via `critic-review.md` and a separately-spawned reviewer with no access to executor reasoning beyond the artefacts themselves.

## D-003 — No free-form executor-authored continuation prompt

**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** The executor must not write a free-form next-run prompt, and `phase-inputs.yaml` must contain factual parameters only — no prose continuation prompt, no conversion of a recommendation into an approval.
**Effect:** Constrains the format and content of `phase-inputs.yaml` and the final report.

## D-004 — Human authority over consequential decisions

**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** The human remains the final approver for: hierarchy terminology and model, repository information architecture, source-of-truth changes, ambiguous story classification, merges/splits of historical stories, migration scope, any production-code or user-home-skill change, and authorisation to begin each subsequent phase.
**Effect:** Listed verbatim in `POLICY.md` under "Human approval required for."

## D-005 — Fixed source-of-truth boundaries

**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** Product hierarchy owns long-lived intent/relationships/status; story records own story definition and acceptance criteria; sprint `CONTEXT.md` owns selected execution scope; sprint `state.md` owns workflow-stage state; sprint `decisions.md` owns HITL routing/skip decisions; sprint evidence/stage outputs own delivery proof; completed sprint history is never rewritten to make the new model appear to have existed earlier.
**Effect:** Fixed in `PROGRAMME.md` and `POLICY.md` unless a future human decision changes it.

## D-006 — Discovery-only authorisation

**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** Of the five intended programme phases (discovery, hierarchy approval, structure implementation, historical migration, sprint-workflow integration), only `discovery` is authorised by this bootstrap. Phases 2–5 require a separate, explicit human decision recorded in this register before they may begin.
**Effect:** Governs `PHASES.md` phase statuses and `state.md`'s "next permitted action."

---

*No further decisions have been approved as of the end of the discovery-phase run recorded in `runs/discovery-run-001.md`. All discovery-phase recommendations remain in `decision-pack.md` pending human review.*
