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

## D-007 (resolves DP-01) — Story-reconstruction granularity: retain current grain

**Selected option:** A
**Date:** 2026-07-15
**Approved by:** Michael Emedo (via `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`)
**Decision:** Retain the current 148-item story/feature-line granularity established in the discovery document. Use one record per meaningful delivered product item; do not collapse to one item per sprint, and do not split to one item per acceptance criterion.
**Rationale:** This grain already exists in the source material (`docs/ROADMAP.md`'s own Story Index / Track tables) and matches the granularity most sprints already report evidence against.
**Effect on later phases:** Fixes the item-count baseline (148) that Phase 4 (historical migration) will migrate against; no further granularity debate is open.
**Follow-up outside this programme:** None.

## D-008 (resolves DP-02) — Repository information architecture: Model A (flat registries)

**Selected option:** A
**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** Use flat product registries (`OUTCOMES.md`, `CAPABILITIES.md`, `FEATURES.md`, `STORY-REGISTRY.md`) plus a flat `stories/` folder. Relationships between outcomes, capabilities, features, and stories are maintained through stable IDs and metadata, not deeply nested folders. Model B (deeply nested outcome/capability/feature/story directories) is rejected.
**Rationale:** Matches the repository's existing flat-file convention (`docs/stories/`, `docs/test-reports/`, `docs/audit/`); gives stable story identifiers independent of feature reclassification; cheaper migration path; easier automated validation.
**Effect on later phases:** Fixes the target repository structure Phase 3 (structure implementation) will scaffold — see the Phase 3 factual inputs file. Phase 3 itself remains unauthorised by this decision alone.
**Follow-up outside this programme:** None.

## D-009 (resolves DP-03) — Source-of-truth rules adopted as written

**Selected option:** A
**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** Adopt the source-of-truth rules proposed in Section 10 of the discovery document (`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`) as written, with no amendment.
**Rationale:** The proposed rules are a direct extension of the fixed boundaries already approved in D-005, not a new invention; adopting them as written keeps the boundary consistent end-to-end.
**Effect on later phases:** These rules now govern how the product hierarchy, story records, sprint `CONTEXT.md`/`state.md`/`decisions.md`, and sprint evidence divide ownership for all subsequent phases — see the Phase 3 factual inputs file for the adopted text.
**Follow-up outside this programme:** None.

## D-010 (resolves DP-04) — PH_OT `is_pensionable` deferral: still open, escalate as compliance risk

**Selected option:** B
**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** The Sprint 7 `PH_OT is_pensionable` deferral (OQ1) is treated as still open. It is escalated as a potential statutory-compliance risk **outside this programme** — this programme does not investigate or resolve it; the decision only records that it remains unresolved and requires separate attention.
**Rationale:** No evidence was found in the discovery pass of this item being closed in any later sprint; given the possible real-money/compliance consequence (whether any client's PH overtime is contractually pensionable), it should not be quietly treated as settled or as a documentation-only loose end.
**Effect on later phases:** The historical migration phase (Phase 4, not yet authorised) must carry this item forward with its open/escalated status intact — it must not be migrated as if resolved.
**Follow-up outside this programme:** A separate sprint (outside `product-traceability`) must investigate whether any live client's PH overtime pay should in fact be pensionable, and close OQ1 with real evidence one way or the other.

## D-011 (resolves DP-05) — Five unresolved items: classify as backlog / not delivered

**Selected option:** A
**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** All five items flagged `requires human classification` in the discovery document (PT-A1-14 Client 3 shift allowance, PT-Q-02 period_type retry context, PT-Q-03 simulate-script Decimal conversion, PT-Q-07 approved_by actor identity, PT-S-08 python-multipart pin) are classified as backlog / not delivered, matching their `docs/ROADMAP.md` 🔜/⬜ status, unless newer evidence is supplied.
**Rationale:** No evidence surfaced during discovery indicates any of the five have been completed since ROADMAP.md was last updated; treating them as backlog is the accurate, non-inflated classification.
**Effect on later phases:** These five items are excluded from the Phase 4 "delivered stories" migration set; they remain visible only in the outcome/feature backlog view, per Section 14 of the discovery document.
**Follow-up outside this programme:** If any of the five is in fact already complete, the domain/delivery owner should supply the corroborating evidence so the classification can be corrected in a future programme pass — not assumed here.

## D-012 (resolves DP-06) — Gate 4 status contradiction: investigate before trusting either source

**Selected option:** C
**Date:** 2026-07-15
**Approved by:** Michael Emedo
**Decision:** Neither `docs/ROADMAP.md` (marks Gate 4 ✅) nor `docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md` (states "plan approved, implementation pending") is trusted as authoritative as-is. A targeted investigation (outside this programme) is required to determine Gate 4's actual completion status before either source is relied upon.
**Rationale:** The two sources directly contradict each other on whether 8 specific pages are built and wired; guessing in either direction risks either under- or over-stating delivered scope in the future product hierarchy.
**Effect on later phases:** PT-UI-04 remains `tentative` in the discovery document and must not be upgraded to `confirmed` in Phase 4 until this investigation closes.
**Follow-up outside this programme:** A short, targeted investigation (git history on both files plus a live check of the 8 pages listed in `docs/ROADMAP.md`'s "Gate 4 — Pages Remaining" table) should be scoped as ordinary delivery work, not as part of `product-traceability`.

## D-013 (resolves DP-07) — Authorise and complete Phase 2 (hierarchy approval)

**Selected option:** A
**Date:** 2026-07-15
**Approved by:** Michael Emedo (via `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`)
**Decision:** Phase 2 (`hierarchy approval`) is authorised and, with D-007 through D-012 above recorded, is complete. Phase 3 (`structure implementation`) is **not** authorised by this decision — it requires its own separate, explicit authorisation once its scope and controls (see the Phase 3 factual inputs file) have been reviewed.
**Rationale:** All seven decision-pack items (DP-01–DP-07) needed to close Phase 2 have now been recorded; no open question blocks calling Phase 2 complete. Phase 3 is a distinct, larger-scope decision (the only phase whose allowed paths would include a genuinely new directory tree, `docs/product/`) and is deliberately not bundled into this authorisation.
**Effect on later phases:** `PHASES.md` and `state.md` are updated to reflect discovery = complete, hierarchy approval = complete, structure implementation = not authorised. The next human gate is authorisation of Phase 3's scope and controls specifically.
**Follow-up outside this programme:** None — the next action is squarely within this programme (a future Phase 3 authorisation decision).

---

*Discovery-phase decisions: D-001–D-006 (governance). Hierarchy-approval-phase decisions: D-007–D-013 (DP-01–DP-07), recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`. No further decisions have been approved. Phase 3 (structure implementation) remains unauthorised — see `phase-3-inputs.md` for factual inputs only, not a permission grant.*
