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

## D-014 — Authorise Phase 3 (structure implementation), scope-limited

**Date:** 2026-07-15
**Approved by:** Michael Emedo (direct chat instruction: "Authorise Phase 3 with write access limited to docs/product/. Create the empty hierarchy scaffold, templates and validation mechanism. Do not modify historical files, migrate stories or begin Phase 4.")
**Decision:** Phase 3 (`structure implementation`) is authorised, with write access limited strictly to `docs/product/`. The authorised scope is: create the empty hierarchy scaffold (registries + `stories/` folder, per the Model A structure fixed in D-008), templates, and a validation mechanism. No historical file is to be modified. No story content is to be migrated into the registries or `stories/` folder — they are created empty of historical content. Phase 4 (`historical migration`) is explicitly not begun by this authorisation.
**Rationale:** This is a narrowly-scoped, explicit human authorisation matching exactly the Phase 3 definition already fixed in `PHASES.md` and the factual parameters already compiled in `phase-3-inputs.md` following D-008/D-009. No new judgement calls are introduced — this decision executes what was already proposed and reviewed, at the human's explicit direction.
**Effect on later phases:** Governs the write scope validated in `runs/structure-implementation-run-001.md`. Phase 4 (historical migration) still requires its own separate, explicit authorisation before any story content is migrated into the scaffold created under this decision.
**Follow-up outside this programme:** None — the two follow-up investigations from D-010/D-012 (PH_OT `is_pensionable`, Gate 4 contradiction) remain open and unaffected by this decision.

## D-015 — Authorise Phase 4A: bounded two-story pilot migration only

**Date:** 2026-07-15
**Approved by:** Michael Emedo (via `docs/diagnostics/2026-07-15-prompt-authorise-phase-4a-two-story-pilot-migration.md`)
**Decision:** A bounded pilot of Phase 4 (`historical migration`) is authorised, and only this pilot — **Phase 4 as a whole remains unauthorised.** The pilot migrates exactly two proven ICM sprint-workflow stories into the `docs/product/` hierarchy created in Phase 3:
- `aud-q1-trace-source` (Q1/AUD-1 — `component_source` field on `fixed_amount` trace entries)
- `sec-s7-timesheet-upload-guard` (SEC-S7 — 10 MB timesheet upload size guard)

No other historical item (of the 148 inventoried in the discovery document, or any other) may be migrated under this decision. The pilot exists to prove the product layer carries the intended ICM disciplines (stable IDs, source-of-truth ownership, explicit state, evidence links, decision traceability, dependency visibility, append-only history, human-gate discipline) on two already-closed, well-evidenced ICM sprints before any wider migration batch is considered.
**Rationale:** These two sprints are the only ones executed under the newer, more rigorous ICM sprint-workflow structure (`docs/sprints/<sprint>/state.md`/`decisions.md`/`evidence/`) with fully terminal per-stage status, closed audit/security/test/retro records, and unambiguous commit references — the strongest possible evidence base for a first migration pilot, deliberately chosen over any of the other 146 items (most of which rest on `docs/ROADMAP.md`'s narrative status plus a cross-check, not a dedicated per-stage evidence trail).
**Effect on later phases:** Governs `runs/historical-migration-pilot-run-001.md`. Successful pilot completion does **not** auto-authorise the remainder of Phase 4 — a separate, explicit human decision is required for any broader migration batch, per the pilot's own "human-gate discipline" governance check.
**Follow-up outside this programme:** None — the two follow-up investigations from D-010/D-012 (PH_OT `is_pensionable`, Gate 4 contradiction) remain open and unaffected by this decision.

## D-016 — Authorise Phase 4B: bounded confirmed-story batch (one capability area, ≤20 items), plus human-readable registry names

**Date:** 2026-07-15
**Approved by:** Michael Emedo (via `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`, delivered via the `/remote-control` session, then confirmed for execution in this session)
**Decision:** A bounded Phase 4B batch of Phase 4 (`historical migration`) is authorised, and only this batch — **Phase 4 as a whole remains unauthorised.** The batch migrates **confirmed-only** stories from **exactly one capability area**, selected per the authorising prompt's batch-selection rule (a capability area with 10–20 confirmed items, preferred over any other option): **capability area A1+A2 — Onboarding & Workforce Setup**, which contains exactly 19 confirmed items in the discovery document (within the 10–20 band, never exceeding 20). Strongly inferred, tentative, requires-human-classification, backlog, disputed, and unresolved-compliance items are explicitly excluded, as are the two items with internally mixed/contradictory confidence (`PT-A1-23`, `PT-A1-24` — see the run record's batch-selection log for why each was excluded even though nominally listed as at least partially confirmed).
This decision also authorises a schema amendment: `CAPABILITIES.md`, `FEATURES.md`, and `STORY-REGISTRY.md` gain human-readable parent-name display columns (`outcome_name`, `capability_name`, `feature_name` respectively) alongside their existing stable-ID columns, with `validate_registry.py` extended to strictly enforce that every displayed name exactly matches its authoritative parent's current name, and to reject duplicate registry IDs, duplicate story-file ID prefixes, and ambiguous prefix matches.
**Rationale:** A1+A2 is the only capability area whose confirmed-item count falls inside the authorised 10–20 range without any further subsetting judgement call — Execution (A4) has 13 confirmed items but two (`PT-A4-31`, `PT-A4-32`) are already migrated under Phase 4A's `CAP-1`/`CAP-2`, and other areas (A5, A6, A7–A10) have too few confirmed items (2, 3, and 6 respectively) to form a coherent standalone batch without reaching into adjacent areas, which the authorising prompt's batch-selection rule disallows ("do not select unrelated items merely to hit a target").
**Effect on later phases:** Governs `runs/historical-migration-confirmed-batch-run-001.md`. Successful batch completion does **not** auto-authorise the remainder of Phase 4 (the still-unmigrated confirmed items in other capability areas, nor any strongly-inferred/tentative item anywhere) — a separate, explicit human decision is required for any further migration batch, per the batch's own human-gate-discipline requirement (rubric point 11).
**Follow-up outside this programme:** None — the two follow-up investigations from D-010/D-012 (PH_OT `is_pensionable`, Gate 4 contradiction) remain open and unaffected by this decision; note that PH_OT `is_pensionable` (`PT-A1-02`) and Gate 4 (`PT-UI-04`) are in different capability areas / confidence levels and are not part of this A1+A2 confirmed-only batch regardless.

---

*Discovery-phase decisions: D-001–D-006 (governance). Hierarchy-approval-phase decisions: D-007–D-013 (DP-01–DP-07), recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`. Structure-implementation-phase decision: D-014, recorded 2026-07-15 via direct human chat instruction. Phase 4A pilot decision: D-015, recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-authorise-phase-4a-two-story-pilot-migration.md`. Phase 4B confirmed-batch decision: D-016, recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`. Phase 4 (historical migration) as a whole remains unauthorised.*
