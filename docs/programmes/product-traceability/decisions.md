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

## D-017 — Halt migration; complete and approve the hierarchy top-down first

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction, review of the Phase 4A/4B batches)
**Decision:** Further historical migration is **halted**. Before any additional story is migrated, the product hierarchy — outcomes, capabilities and features — must be defined **as a whole, top-down, across the entire 148-item inventory**, and explicitly approved by the human as a single proposal.
**Rationale:** Phase 4A and Phase 4B each created only the hierarchy rows needed to place that batch's stories (`OUT-3`, `CAP-3`, `FEAT-3`/`4`/`5` exist because 19 A1+A2 stories needed a home). This is bottom-up accretion: feature boundaries are set by what a batch happened to contain rather than by product logic, coverage is unknowable, and there has never been a complete proposal for the human to approve. The discovery document anticipated exactly this — Sections 7 and 8 explicitly declined to define features or map stories "before the hierarchy model itself is approved… which is exactly the kind of scope expansion `POLICY.md` prohibits" — and Phase 4A/4B proceeded without that layer having been defined.
**Effect on later phases:** Introduces Phase 3B (`hierarchy completion`, authorised by D-022) between Phase 3 and any further Phase 4 batch. Full Phase 4 remains unauthorised and additionally now blocked behind Phase 3B's human gate.
**Follow-up outside this programme:** None.

## D-018 — Acceptance-criteria ownership: pointer-only for retro-migrated stories, native for forward-authored stories

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction)
**Decision:** A **retro-migrated** story record does not carry acceptance criteria; it summarises and links to the source story file, as D-009 established. A **forward-authored** story — one created in the product hierarchy from the point the PM writes it, with no pre-existing sprint story file to point at — carries its acceptance criteria **natively and authoritatively** in its own record.
**Rationale:** For already-delivered work the source story is closed and frozen, so the drift risk D-009 was avoiding is real while the benefit of duplication is low; re-typing acceptance criteria for up to 148 delivered stories is heavy work for little gain. For new work there is no prior file, so the hierarchy must own the criteria or they have no home.
**Contradiction resolved by this decision:** `POLICY.md`'s fixed source-of-truth boundaries state "Story records own story definition and authoritative acceptance criteria" without naming *which* story records, which reads as contradicting D-009's pointer-only rule. This ambiguity — not a deliberate trade-off — is why a reviewer reasonably expected migrated stories to carry acceptance criteria and found none. `POLICY.md` is amended under D-022 to state the retro/forward split explicitly rather than leaving the reading to the reader.
**Effect on later phases:** `stories/TEMPLATE.md` gains an acceptance-criteria section that is mandatory for forward-authored stories and explicitly "not applicable — see source" for retro-migrated ones. Phase 5 (sprint-workflow integration) inherits the forward rule.
**Follow-up outside this programme:** None.

## D-019 — Meaning-free durable story IDs (`STORY-<nnnn>`)

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction)
**Decision:** Story identifiers take the form `STORY-<nnnn>` and **encode nothing** — no programme name, no capability area, no feature, no sprint, no delivery date. Allocation rules:

1. Seed allocation runs in **chronological delivery order** across all 148 known inventory items, in a single pass at hierarchy sign-off.
2. Forward allocation is **strictly sequential** in the order stories enter the registry, regardless of date.
3. IDs are **never renumbered and never reused**. A late-discovered historical item takes a high number despite being early — this is correct; the delivery-date field carries the truth.
4. Every one of the 148 items receives an ID at sign-off whether or not it is migrated, so coverage is visible as "which IDs have a story file."
5. A later merge or split (human approval required per `POLICY.md`) **retires** an ID; it is never reused.
6. Every legacy code is preserved on the story in a mandatory `origin_code` field (e.g. `PT-A1-22`; `Sprint 17 B2`; `EMP-B2`).

**Rationale:** `PT-A1-22` encoded two temporary things — the programme's own name, and a position in a one-off retro inventory — neither of which survives the programme that created them. More fundamentally, `docs/product/README.md` already commits to "a story's ID never changes even if its feature assignment is later revised," so any identifier encoding a relationship eventually becomes a lie. The ID is a handle; readability comes from the title and the display-name columns, and chronology from the date fields, which are sortable. `STORY-REGISTRY.md` itself recorded that re-keying was a pending human decision — this decision makes it.
**Effect on later phases:** All forward stories use this scheme. The 21 already-migrated stories are re-keyed under D-020.
**Follow-up outside this programme:** None.

## D-020 — Re-key the 21 migrated stories now; one-time exception to "never renumbered"

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction)
**Decision:** The 21 stories migrated under D-015 and D-016 are re-keyed from their provisional `PT-*` identifiers to the `STORY-<nnnn>` scheme fixed in D-019, with every legacy code preserved in `origin_code`. This is an **explicit, recorded, one-time exception** to the "never reused, never renumbered" rule stated in the headers of `OUTCOMES.md`, `CAPABILITIES.md`, `FEATURES.md` and `STORY-REGISTRY.md`. That rule is restated as binding **from this decision forward**.
**Rationale:** The cost of re-keying scales with volume — 21 stories now versus up to 148 later. `STORY-REGISTRY.md`'s own schema note describes the `PT-*` IDs as provisional and flags re-keying as a decision the human had yet to make; that decision was never made, and the provisional scheme became permanent by default rather than by choice. Recording the exception explicitly is preferred to letting the "never renumbered" rule read as silently violated.
**Effect on later phases:** Executed in Phase 3B. `validate_registry.py` gains a check that no live `PT-*` identifier survives outside an `origin_code` field.
**Follow-up outside this programme:** None.

## D-021 — Defer `docs/ROADMAP.md` relabelling until after the traceability layer is established

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction)
**Decision:** The inconsistent labelling in `docs/ROADMAP.md` is acknowledged as a real problem and **deferred**. No relabelling is undertaken now, by this programme or otherwise. Old item codes are never rewritten; they are preserved as `origin_code` values on the corresponding stories.
**Rationale:** Three reasons. (1) `docs/ROADMAP.md` runs three different organising principles in sequence — capability area (Sprints 0–1b), Track (Phase 1 Priority Order), then Sprint with per-sprint Story Index (Sprint 14 onward) — and carries 25+ unrelated ID prefixes, some colliding (`B` denotes both Track B "Schema Foundations" and Sprint 17's Track B items; `P1`/`P2` serve as both item prefixes and phase names). (2) Relabelling now would break citations across four programmes simultaneously: `docs/product/`, `docs/audit-program/`, `docs/programmes/agentic-architecture-review/`, and every sprint story file and test report. (3) The root cause is that the roadmap serves two jobs — forward planning *and* historical record. This programme is building the layer that owns delivered history; once it does, the roadmap keeps only forward planning and one consistent scheme applies to new items alone, making a retrospective relabel largely unnecessary.
**Effect on later phases:** None within this programme. `POLICY.md` forbids this programme from modifying `docs/ROADMAP.md` in any case, so any future relabelling requires its own separate authorisation outside this programme.
**Follow-up outside this programme:** After the traceability layer is established, scope a separate piece of work to apply one consistent labelling scheme to *new* roadmap items and to retire the roadmap's historical-record role.

## D-022 — Authorise Phase 3B (`hierarchy completion`) and the governance amendments it requires

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction, plan approved this session)
**Decision:** A new phase, **Phase 3B — `hierarchy completion`**, is authorised, positioned as a peer of Phase 3 (`structure implementation`) and **before** any further Phase 4 batch. Write access is limited to `docs/product/` and `docs/programmes/product-traceability/`. Its purpose is to define the complete outcome/capability/feature hierarchy across the whole 148-item inventory, present it for human sign-off as a visual artefact, and — only after approval — apply it together with the re-key (D-020) and the readability fixes. **No story is migrated by this phase.**

This decision also authorises the following amendments, each a consequential change under `POLICY.md`'s own rule that changes to it require human approval:

- **`POLICY.md`** — (a) restate the acceptance-criteria source-of-truth boundary per D-018, naming which story records; (b) add **the story ID scheme** to "Human approval required for" — its absence is the gap that let provisional IDs become permanent without a decision; (c) mark the "may not create the final `docs/product/` structure" prohibition as superseded by Phase 3/D-014.
- **`PHASES.md`** — define Phase 3B; record that Phase 2's approval was **partial** (the model and terminology were approved; the feature layer was explicitly deferred and never defined). Phase 2's own record is not retro-edited to claim otherwise.
- **`PROGRAMME.md`** — correct the stale `current phase: discovery` and stale scope exclusions; carry the D-018 acceptance-criteria split into the source-of-truth model.

**Rationale:** Phase 4's stated purpose is to "populate **the approved structure**." Since the structure was never fully approved, this work is not Phase 4 and cannot legitimately run under Phase 4's authorisation. `POLICY.md`'s autonomy mode is phase-scoped — the executor "may not execute a later phase" and "may not expand the authorised file scope beyond what `PHASES.md` grants the active phase" — so the phase must exist before the work begins. Performing the analysis first and back-filling the governance afterwards would reproduce precisely the pattern that caused the problem this phase exists to fix.
**Effect on later phases:** Full Phase 4 remains unauthorised and is now additionally gated behind Phase 3B's human sign-off. Phase 3B's completion does **not** auto-authorise any migration batch.
**Follow-up outside this programme:** The roadmap relabelling deferred under D-021.

## D-023 — Hierarchy approved; OQ-1–OQ-8 resolved (Phase 3B Stage 2 gate passed)

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction, on review of the Stage 2 visual sign-off artefact)
**Decision:** The hierarchy proposed in `hierarchy-proposal.md` — **5 outcomes, 12 capabilities, 41 features** — is **approved as a whole**, at outcome, capability, feature and story level. Phase 3B's human gate is passed; Stage 3 is authorised to apply it.

Rulings on the eight open questions:

| OQ | Ruling |
|---|---|
| OQ-1 — 148 vs 149 item count | **Proceed.** The discrepancy surfaces itself in Stage 3 when each story file is created; do not block on it. |
| OQ-2 — Sprint PAY-TAX-1 missing | **Capture it.** The work is delivered; the gap is in the discovery inventory, not the platform. See D-024. |
| OQ-3 — Sprint 25 missing | **Capture it**, same as OQ-2. See D-024. |
| OQ-4 — Rename `CAP-1`/`CAP-2` | **Approved.** IDs unchanged; display names updated. |
| OQ-5 — Split A1+A2 into `CAP-3` + `CAP-4` | **Approved.** |
| OQ-6 — Keep `OUT-5`/`CAP-12` with zero stories | **Approved — keep.** They represent the agentic payroll work not yet done; naming them keeps that gap visible. |
| OQ-7 — No `EPIC-*` delivery rows | **Approved — non-adoption confirmed.** A capability already functions as an epic in this model, so a separate delivery layer would duplicate what `sprint_refs` and the capability layer already carry. |
| OQ-8 — Split `STORY-0104` (`PT-A1-24`) | **Approved — split**, on condition that both halves remain traceable to the original item. Both carry `PT-A1-24` as `origin_code`, distinguished by sub-item (B0a / B0b). The split is vindicated by the two halves landing in different features. |

**Rationale:** the proposal was reviewed as a whole against the visual artefact, with feature membership, coverage and provenance all inspectable. Every ruling above is the human's, not the executor's.
**Effect on later phases:** Stage 3 may proceed. Phase 4 (migration of the remaining items) remains separately unauthorised.
**Follow-up outside this programme:** None.

## D-024 — Capture six previously-uninventoried delivered items; re-seed the ID allocation

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction: the work "is there, it's implemented, we just need to capture it")
**Decision:** Six delivered items absent from the discovery inventory are added to the allocation, and `PT-A1-24` is split in two per OQ-8, taking the total from 148 to **155**:

| Origin | Item | Feature | Confidence |
|---|---|---|---|
| `BADGE-RT-1` | Payroll Inputs sidebar badge reflects live pending count via `window.dispatchEvent` | `FEAT-17` | confirmed |
| `BADGE-RT-2` | Badge shows total pending inputs, not just issue inputs | `FEAT-17` | confirmed |
| `EMP-TABLE-1` | Employees table UX: start/end dates visible, column alignment, inactive styling | `FEAT-11` | confirmed |
| `EMP-TABLE-2` | "No longer active" state surfaced; contract end date editable | `FEAT-11` | confirmed |
| `EMP-TABLE-3` | Register employee: contract start/end date fields in AddEmployeeSlideOver | `FEAT-4` | confirmed |
| `PAY-TAX-1` | NG PAYE bands corrected to NTA 2025 (migration `de1f2a3b4c5d`) | `FEAT-19` | confirmed |

**Evidence verified before classification** (per `POLICY.md`'s prohibition on classifying `confirmed` without direct evidence): all five Sprint 25 story files exist on disk (`docs/stories/sprint-25-badge-realtime-update.md`, `sprint-25a`, `sprint-25b`, `sprint-25c`, `sprint-25d`); `migrations/versions/de1f2a3b4c5d_fix_ng_paye_bands_nta_2025.py` and `tests/test_paye.py` both exist; both sprints are ✅ in `docs/ROADMAP.md` with named files-changed lists; `CLAUDE.md` records Sprint PAY-TAX-1 closed.

**Why they were missed — recorded so the method gap is not repeated:** the discovery pass inventoried **by capability area**, and both items sit exactly where an area-based sweep loses things.
- **Sprint 25** was collapsed into the Summary Matrix row "Sprints 24–26 — Employee Lifecycle UX | 14✅". Sprints 24 and 26 were expanded to line-item grain; the Sprint 25 block never was, so its five stories disappeared into an aggregate count.
- **Sprint PAY-TAX-1** is filed in the Summary Matrix under *Correctness & Audit* but is substantively an Execution/statutory item. The A4 sweep did not reach it (the matrix filed it under A7); the A7 sweep did not claim it (it is not an audit observation). It fell in the seam between two areas.

This is **not** a date cutoff — Sprint RULE-VER-1 (2026-06-21) was captured while PAY-TAX-1 (2026-06-20) was not. It is a method gap, and it is the strongest argument for maintaining a coverage map: an area-based sweep cannot see what sits between areas.

**Re-seed of the ID allocation:** because Stage 3 had not yet written any identifier to `docs/product/`, the chronological seed pass fixed by D-019 rule 1 is **re-run once** to place the seven new/split items in their correct chronological positions, rather than appending them out of order. This is the last moment at which that is free; after Stage 3 writes them, D-019 rule 3 (never renumber) binds absolutely. Notable shift: the item reviewed in conversation as `STORY-0104` becomes `STORY-0104`/`STORY-0105` (the B0a/B0b split), and everything from the old `STORY-0105` onward shifts by one or more places. The draft numbering in `hierarchy-proposal.md` §5 is superseded by `docs/product/ID-ALLOCATION.md`.

**Rationale:** capturing delivered work that the inventory missed is a correction, not a scope expansion — the alternative is a traceability layer that silently under-reports what was built. Re-seeding preserves the one property the chronological seed was chosen for.
**Effect on later phases:** Phase 4's migration set grows from 148 to 155 items; 134 remain unmigrated. The discovery document is **not** retro-edited — it remains an accurate record of what that pass found.
**Follow-up outside this programme:** None. If further uninventoried sprints surface, they are captured the same way and the count is corrected again.

## D-025 — Authorise Phase 4C: full `CAP-6` Execution Engine batch (31 items, all confidence levels)

**Date:** 2026-07-28
**Approved by:** Michael Emedo (direct chat instruction: start Phase 4, focused on the Execution Engine capability)
**Decision:** A bounded Phase 4C batch is authorised, and only this batch — **Phase 4 as a whole remains unauthorised.** The batch migrates **every item allocated to `CAP-6` Execution Engine** — all 31, across `FEAT-18` through `FEAT-25` — into `docs/product/`.

**Confidence is carried verbatim, not filtered.** The batch composition is 12 `confirmed`, 13 `strongly inferred`, 5 `tentative`, 1 `backlog`. No item may be upgraded; a `tentative` item is migrated *as* `tentative`, with its evidence gap stated in its own record.

**Departure from the Phase 4B batch rule, and why.** D-016's batch selected `confirmed`-only items. That rule is **not** carried forward here. Confirmed-only would have migrated 12 of 31 and left the Execution Engine partially covered — reproducing, inside a single capability, exactly the patchy-coverage problem that Phase 3B existed to fix. The `confidence` column exists precisely so that weakly-evidenced work can be recorded without overclaiming; using it is a better answer than omitting the work and leaving the registry silent about it. `POLICY.md`'s prohibition is on classifying an item `confirmed` **without evidence** — it does not prohibit recording an item at a lower confidence, and this batch does not weaken it.

**Known evidence weakness, accepted with eyes open:** five Sprint 0 items (`STORY-0004`, `0005`, `0006`, `0007`, and `STORY-0038`) rest on pre-sprint-tracking records with no dedicated test report. Each is migrated as `tentative` with the specific gap named in its `Unresolved questions` section. They are not to be cited as evidence of verified behaviour.

**Why `CAP-6` first:** it is the largest capability (31 items), had **zero** migrated coverage after Phases 4A/4B, and is the platform's core reason to exist — gross-to-net calculation, statutory deductions, proration, overtime and public-holiday pay, rule resolution and retry. Its zero-coverage state was surfaced by `ID-ALLOCATION.md` and is the clearest single illustration of what a batch-shaped hierarchy conceals.

**Rationale:** the hierarchy is now approved and stable (D-023), identifiers are allocated and permanent (D-019/D-020), and the coverage map makes the gap explicit. Migrating a whole capability — rather than a confidence slice of one — produces a capability that can be reasoned about as a unit.
**Effect on later phases:** on completion, coverage rises from 21/155 to 52/155. The remaining 103 items stay unauthorised; this batch's completion does **not** auto-authorise any further batch.
**Follow-up outside this programme:** None.

## D-026 — Capture the `dev-levy-rule-pct` sprint; extend the Phase 4C batch to 33

**Date:** 2026-07-28
**Approved by:** Michael Emedo (applying the D-024 standing approach — captured delivered work that the inventory missed)
**Decision:** Sprint `dev-levy-rule-pct` (2026-07-16) is captured as two stories, both Execution Engine work, and both are included in the Phase 4C batch — taking it from 31 items to **33**:

| New ID | Origin | Item | Feature | Confidence |
|---|---|---|---|---|
| `STORY-0156` | `DEV-LEVY-1` | Development Levy applied correctly — two independent OR'd cadence triggers, `annual_amount` override key | `FEAT-19` | confirmed |
| `STORY-0157` | `RULE-PCT-1` | "Percentage of basic" earning rule configurable via UI; invalid `PERCENTAGE_OF_GROSS` method string fixed | `FEAT-18` | confirmed |

**Why it was missed:** a date boundary, not a method gap this time. The discovery pass ran on **2026-07-15**; this sprint closed on **2026-07-16** — one day later. Nothing was overlooked; the inventory simply has a cut-off, and no mechanism existed to catch work delivered after it. This is the third uninventoried sprint found (with Sprint 25 and PAY-TAX-1 under D-024), and the first attributable to recency rather than to the area-based sweep.

**Evidence verified before classification:** `docs/sprints/dev-levy-rule-pct/` exists as a full ICM sprint workspace (`CONTEXT.md`, `plan.md`, `decisions.md`, `architecture.md`, `state.md`, `evidence/`); `docs/test-reports/2026-07-16-dev-levy-rule-pct.md` records **327 passed / 1 intentional skip / 0 failed**, 8 LIVE API checks, verdict PASS; `docs/audit/2026-07-16-dev-levy-rule-pct-audit-review.md` exists and its CRITICAL finding is recorded as fixed and re-verified before the test pass began. This is among the best-evidenced work in the repository.

**Forward allocation, not a re-seed.** `STORY-0156`/`0157` take the next free numbers under D-019 rule 2, **not** chronological positions. The seed pass is spent; D-019 rule 3 (never renumber) now binds absolutely, and a later-discovered item taking a high number is the expected and correct outcome. `sprint_refs` carries the true date.

**Standing implication:** the inventory has a 2026-07-15 horizon. Any sprint closing after that date is invisible to it and must be captured at migration time, as here. Phase 5 (`sprint-workflow integration`) is the durable fix — wiring traceability into sprint closure so new work registers itself rather than waiting to be rediscovered.
**Effect on later phases:** total allocation rises from 155 to 157; Phase 4C covers 33; on completion, coverage is 54/157.
**Follow-up outside this programme:** None.

## D-027 — Authorise Phase 4D: migrate every remaining allocated item (103), as one phase, not in batches

**Date:** 2026-07-29
**Approved by:** Michael Emedo (direct chat instruction: *"product traceability programme: proceed with migrating all other capabilities no need to process in batch"*)
**Decision:** **Phase 4 is now authorised in full**, and completed by a single phase — **Phase 4D** — which migrates **all 103 remaining allocated items** into `docs/product/`. On completion, coverage is **157 of 157 (100%)** and there is no migration backlog left.

**Explicit batching decision.** The instruction is that no further batch decomposition is required. Phases 4A (2), 4B (19) and 4C (33) each carried their own authorisation; this decision retires that pattern for the remainder rather than issuing six more capability-shaped authorisations. The batching existed to prove the mechanism at increasing scale — a 2-item pilot, a 19-item confirmed slice, a 33-item whole capability — and that proof is now complete: the hierarchy is approved and stable (D-023), identifiers are allocated and permanent (D-019/D-020), the coverage map is exhaustive (`../product/ID-ALLOCATION.md`), and the validator has caught real defects in each of the last two batches. Continuing to authorise batch-by-batch would buy nothing except a longer period during which the registry under-reports what the platform does.

**Scope — all six zero-coverage capabilities plus the partial remainder of four others:**

| Capability | Remaining | Capability | Remaining |
|---|---|---|---|
| `CAP-5` Pay Events & Inputs | 18 | `CAP-1` Correctness, Audit & Snapshot | 10 |
| `CAP-3` Onboarding & Workspace Setup | 14 | `CAP-4` Employee Lifecycle Management | 15 |
| `CAP-9` Design System & Navigation | 11 | `CAP-7` Governance & Run State Machine | 9 |
| `CAP-10` Delivery Infrastructure | 9 | `CAP-8` Disbursement & Exports | 7 |
| `CAP-2` Security & Compliance Hardening | 7 | `CAP-11` Programme Governance & Assurance | 3 |

`CAP-6` is already complete (33/33) and `CAP-12` Agent Layer has zero allocated items by design (D-023, OQ-6) — it stays empty and visible.

**Confidence is carried verbatim, per D-025 — the confirmed-only rule of D-016 stays retired.** The remainder is 33 `confirmed`, 53 `strongly inferred`, 12 `tentative` and 5 `backlog`. No item may be upgraded on migration; a `tentative` item is migrated *as* `tentative` with its evidence gap named in its own record.

**The five remaining `backlog` items are migrated with `status: backlog`, never `delivered`** (D-011): `STORY-0150`, `STORY-0152`, `STORY-0153`, `STORY-0154`, `STORY-0155`. A sixth, `STORY-0151`, was already migrated on the same terms under Phase 4C. Their reason for existing is that a reader must not be able to mistake them for delivered work by their absence.

**Two `tentative` items record a source contradiction rather than resolving it.** `STORY-0057` (Gate 4) — `docs/ROADMAP.md` marks it ✅ while `docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md` says implementation pending; this is D-012/DP-06's open item and is **not** closed by migrating it. `STORY-0103` (Employees.tsx split-action rework) and `STORY-0105` (timesheet LATERAL join) both carry **BLOCKED** browser/multi-contract verification in `docs/test-reports/2026-05-27-sprint-17-full.md`. Recording the contradiction accurately is the deliverable; resolving it is not this programme's work.

**Rationale:** the coverage map's whole point is that a partially-populated registry conceals gaps — that is what Phase 3B existed to fix at the hierarchy layer, and a 34%-migrated story layer reproduces it one level down. A registry that covers everything can be trusted to answer "is this recorded?" with silence meaning *no such work exists*, which is the property the programme was commissioned to produce.
**Effect on later phases:** Phase 4 closes entirely. Phase 5 (`sprint-workflow integration`) becomes the only remaining phase and the only defence against the 2026-07-15 horizon problem recorded in D-026 — with a complete backlog, every subsequently-missed sprint is now the *only* thing that can make the registry wrong.
**Follow-up outside this programme:** unchanged — PH_OT `is_pensionable` (D-010/DP-04, `STORY-0036`) and the Gate 4 status contradiction (D-012/DP-06, `STORY-0057`) remain open and are owned elsewhere.

## D-028 — Surface the two unflagged source contradictions in the registry title; open the steady-state authorisation gap

**Date:** 2026-07-29
**Approved by:** Michael Emedo (direct chat instruction, following a walkthrough of the three post-Phase-4D risks: registry completeness vs verification, the three contradiction items, and the decaying 2026-07-15 horizon)
**Decision:** The `title` of `STORY-0057` and `STORY-0103` is amended in `../product/STORY-REGISTRY.md`, `../product/ID-ALLOCATION.md` and their story files to carry the verification state inline. Scope is exactly these two titles. **No `status`, `confidence`, `evidence_refs` or story body is changed** — the underlying records are already correct.

| Story | Title before | Title after |
|---|---|---|
| `STORY-0057` | Gate 4 — Bureau / workspace-setup journey, 8 pages | Gate 4 bureau / workspace-setup journey, 8 pages — delivery CONTRADICTED |
| `STORY-0103` | `Employees.tsx` split-action rework — Edit / Change Grade / View Contracts | `Employees.tsx` split-action rework — browser UAT BLOCKED |

**The defect this fixes.** All three contradiction items (D-027) carry an explicit "do not cite this as evidence" warning *inside their story file*, and all three are `confidence: tentative`. But the surface most readers actually scan is the `STORY-REGISTRY.md` table, where the row reads `status: delivered` and the only counter-signal is one word in a column eight fields across. `STORY-0105` already solved this by putting `multi-contract verification BLOCKED` in its title; `STORY-0057` and `STORY-0103` did not. A reader skimming the table sees `delivered` and stops.

**This follows an existing precedent rather than inventing one — and closes a live divergence.** `ID-ALLOCATION.md` already titled `STORY-0103` *"Employees.tsx split-action rework — browser UAT BLOCKED"* while `STORY-REGISTRY.md` did not, so the two files disagreed on the same story's title. The wording adopted here is `ID-ALLOCATION.md`'s own, which makes them agree. `STORY-0057`'s flag is newly worded, following the shape `STORY-0105` and `STORY-0103` share: `<description> — <STATE>`. The leading `Gate 4 —` becomes `Gate 4 ` to avoid a second em-dash, matching `FEATURES.md`'s existing phrasing "Gate 4 bureau setup".

**What this does not do.** It does not resolve either contradiction. D-012/DP-06 (Gate 4) stays open and owned outside this programme; Sprint 17's BLOCKED verifications stay BLOCKED. Making a gap harder to miss is not the same as closing it, and this decision must never be cited as having closed one.

**Standing authorisation gap, opened not closed.** Phase 4 is closed (D-027) and Phase 5 is unauthorised, so at the moment this decision was taken **no phase authorised writing to `docs/product/` at all** — the programme has phase authorisations but no steady-state provision for correcting the layer it produced. This decision is a one-off narrow authorisation, not that provision. Defining the standing rule for post-migration maintenance of `docs/product/` belongs to Phase 5's scoping alongside the sprint-closure wiring; until then, every further edit needs its own decision.
**Effect on later phases:** none on scope. Adds one item to Phase 5's agenda: a steady-state maintenance authorisation for `docs/product/`.
**Follow-up outside this programme:** unchanged from D-027.

## D-029 — Authorise Phase 5 (`sprint-workflow integration`), with the exact allowed-path expansion

**Date:** 2026-07-29
**Approved by:** Michael Emedo (direct chat instruction, after a plain-language walkthrough of the scope and an explicit choice of "Option A — hand me the changes" for the skill files)
**Decision:** **Phase 5 is authorised.** This satisfies `PHASES.md`'s "human gate: **before**" requirement, which demands authorisation of *the exact allowed-path expansion* — not general approval of the phase. The list below is that expansion, and it is exhaustive.

**Allowed paths — write:**

| Path | Constraint |
|---|---|
| `docs/sprints/STAGE-REGISTRY.md` | **Amend only.** Lines added to the `Inputs`, `Outputs` and `Completion criteria` fields of the **`pm`** and **`retro`** rows. No new stage; no change to any stage's `Dependencies`, `Parallel compatibility`, `Mandatory status`, `Skip conditions`, `Entry conditions` or `Human gate`; no change to the 10-stage set or its ordering. |
| `docs/sprints/WORKFLOW.md` | **Amend only.** One new `## Product traceability` subsection, plus one row added to the "Separation of concerns" table. No change to the status values, transition rules, parallel rules, skip rules, rework rules or sprint-completion rule. |
| `docs/product/**` | Full write — the rows future sprints create, plus the steady-state maintenance provision D-028 identified as missing. |
| `docs/programmes/product-traceability/**` | Full write — phase record, decisions, critic review. |

**Allowed paths — read-only inputs:** `docs/sprints/CURRENT.md`, `docs/sprints/README.md`, and the three existing sprint workspaces (`aud-q1-trace-source/`, `sec-s7-timesheet-upload-guard/`, `dev-levy-rule-pct/`) as validation material.

**Forbidden paths:** `backend/`, `frontend/`, `migrations/`, `docs/ROADMAP.md`, `docs/stories/`, `docs/audit/`, `docs/audit-program/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/programmes/agentic-architecture-review/`, **`~/.claude/`** (see below), and `docs/sprints/<id>/**` for every existing sprint workspace — closed sprints are history and are **not** retrofitted with traceability links.

**`~/.claude/skills/` stays forbidden — deliberately, at the cost of one manual step.** The rules Phase 5 writes into `STAGE-REGISTRY.md` are *descriptions*; the work is performed by the `/pm` and `/retro` skills, which live outside this repository. Editing only the descriptions leaves a rule that nothing executes. The alternative — widening the boundary to the human's personal skill folder, which has been forbidden in every phase since bootstrap — was declined. **Phase 5 therefore emits the exact `SKILL.md` text as a proposal for the human to apply by hand, and the phase is not complete until they confirm they have.** Recorded here because it is a known, accepted gap between authorisation and effect, not an oversight.

**Two touchpoints, not one — a deliberate departure from `PHASES.md`'s stated output.** The phase definition anticipated "an additional field or step in the `retro` stage." That is insufficient on its own: at `retro` the evidence exists but the story has run the whole sprint with no identifier, and nothing earlier obliges anyone to create one. So the link is written in two places — **`pm`** allocates the `STORY-<nnnn>` when scope is agreed and evidence does not yet exist, and **`retro`** completes the row at close, when `evidence_refs`, `sprint_refs` and `confidence` finally do. `retro`'s existing Sprint Workspace Close Gate enforces it, which is what converts the obligation from a habit into a condition of closing.

**Why this fixes the decay and not just the symptom.** D-026 recorded the 2026-07-15 horizon and three sprints already past it; D-027 recorded that with the backlog at zero, a subsequently-missed sprint is now the *only* thing that can make the registry wrong. A sprint that cannot close without its row removes that failure mode at source rather than relying on periodic rediscovery. It also improves what enters the cabinet: `confidence` is set at close from the sprint's own test and audit evidence, so new items land as `confirmed` rather than joining the 45 rows whose sole evidence is `docs/ROADMAP.md`.

**Required validation:** run the amended fields against `dev-levy-rule-pct` — closed, fully evidenced, already migrated as `STORY-0156`/`STORY-0157` — as the synthetic case, confirming the new fields reproduce a known-good result. That workspace is read-only and is not modified. Plus `python3 docs/product/validate_registry.py` at PASS.
**Effect on later phases:** Phase 5 is the last defined phase. On its completion the programme moves to steady state and any further work needs a new phase, per the cross-phase note.
**Follow-up outside this programme:** unchanged from D-027, plus the manual `SKILL.md` application described above.

## D-030 — Authorise Phase 6 (`feature-42 addition`): add `FEAT-42` Product record & roadmap structure

**Date:** 2026-07-29
**Approved by:** Michael Emedo (`AskUserQuestion` answer, "Where do this sprint's four meta-stories live in the hierarchy?" → "Add FEAT-42 under CAP-11")
**Decision:** A new phase, **Phase 6 — `feature-42 addition`**, is authorised, adding exactly one feature row: `FEAT-42` — *Product record & roadmap structure* — under `CAP-11` Programme Governance & Assurance. Write access is limited to `docs/product/FEATURES.md` (amend only) and this programme's own folder. No outcome, capability, existing feature, ID scheme or column meaning changes, and no existing story's feature assignment moves.

**Rationale:** The `roadmap-split` sprint (authorised separately under its own `decisions.md` DEC-01, executing the follow-up deferred by D-021) has four in-scope stories about the structure of the product record itself. `CAP-11` is unambiguously the right capability, but its only two features are `FEAT-40` (independent review programmes — `audit-program`, `agentic-architecture-review`) and `FEAT-41` (the ICM sprint workflow model — `STAGE-REGISTRY.md`/`WORKFLOW.md`). Neither describes the roadmap and product-record structure, and this programme's own artefact was *excluded* from allocation under D-023's `PT-M-04` ruling rather than given a feature, so no precedent row exists to follow.

Two alternatives were put to the human and declined. Forcing the four stories into `FEAT-41` needs no governance at all but makes the tree assert something false about what `FEAT-41` contains — the small, compounding wrongness this programme was built to remove. Excluding the sprint from traceability entirely, on the `PT-M-04` precedent, was available but would need its own exemption from `retro`'s Close Gate, which hard-stops on an unresolved `story_ref`.

**Why a phase and not just a decision.** The steady-state provision (`PHASES.md`, added under D-029) names "adding or retiring an outcome, capability or feature" as structural change requiring **a new phase and a human decision in this file**. It states no size threshold. Adding one leaf feature under an existing capability is the smallest shape change available, and it is still a shape change; granting it an informal exemption would convert the rule into a matter of judgement on its second application. The phase is cheap. The precedent of skipping it is not.

**Effect on later phases:** None. Phase 6 is terminal and self-contained; on its completion the programme returns to the steady state defined after Phase 5. It does not reopen Phase 4, does not alter the ID scheme, and grants no authority over `docs/ROADMAP.md` — which stays forbidden to this programme, and is edited by the `roadmap-split` sprint under DEC-01/DEC-02 in that sprint's own record.

**Follow-up outside this programme:** Allocating `STORY-0158`–`0161` into `FEAT-42`, and creating backlog rows for the previously untraced open roadmap items, are **additions** — routine sprint work under the steady-state provision, carried by `roadmap-split`'s own record, not by this phase.

---

## D-031 — Authorise Phase 7 (`write-stage correction`): `pm` writes the forward-authored story record, `retro` completes it

**Date:** 2026-07-29
**Approved by:** Michael Emedo (direct human chat instruction, answering OQ-1–OQ-5 of `write-stage-proposal.md` in turn)
**Proposal:** `write-stage-proposal.md`, this folder. Approved as written, with all five open questions resolved — see below.

**Decision:** A new phase, **Phase 7 — `write-stage correction`**, is authorised. Authorship of a **forward-authored** story record moves from `retro` to `pm`. `pm` creates `docs/product/stories/STORY-<nnnn>-<slug>.md` and its `STORY-REGISTRY.md` row with the intent fields populated and `status: backlog`; `retro` populates the evidence fields, flips status, appends the delivery-history line, and completes `SOURCE-INDEX.md` and `FEATURES.md`. Sprint `CONTEXT.md` cites `STORY-<nnnn>` and links to the record for acceptance criteria rather than restating them.

This amends the **forward-authored** branch of D-018 only. D-018's retro-migrated branch — the product record links to the frozen sprint story file and never duplicates its criteria — is unchanged.

**Open questions as resolved:**

| OQ | Question | Resolution |
|---|---|---|
| OQ-1 | Full change, or the fallback (keep the split; require `retro` to diff and report)? | **Full change.** The fallback leaves the transcription step in place and fixes only its visibility. |
| OQ-2 | Do **Out of scope** and **Priority** join `TEMPLATE.md`? | **Yes, both.** |
| OQ-3 | Does **Business risk** join it? | **No** — it stays in sprint `CONTEXT.md`. It is sprint-instance context, not durable product intent. |
| OQ-4 | Reconcile the five already-drifted `roadmap-split` stories? | **No.** They are left as history and stand as the evidence for this decision. Retrofitting them would breach the proposal's own §9 no-retrofit rule on its first application. |
| OQ-5 | Add a validator rule that `status: backlog` with populated evidence fields is contradictory? | **Yes.** Minor; it guards the one new failure mode this phase creates. |

**Rationale.** The two-point split fixed by D-029 places story authorship at sprint close, so `pm` writes the story's intent into `docs/sprints/<id>/CONTEXT.md` and `retro` later transcribes it into the durable record. That transcription has drifted on **every forward-authored story produced to date** — all five from `roadmap-split`, the only rows carrying `ac_owner: hierarchy`. Two drifted in criterion count (`STORY-0158` 4→5, `STORY-0176` 5→6); `STORY-0159` dropped a quantified figure ("the 20 open items" → "the open Phase 1 items"). `validate_registry.py` passes all five, correctly — it has no notion of acceptance-criteria equivalence, and acquiring one would be the wrong fix.

The drift runs in the direction that diagnoses it: in every case the record is the *better* text, because it was composed at close and reflects what was learned. So the criteria that gated implementation and that `tester` verified against were `CONTEXT.md`'s, while the criteria the registry publishes — with that test evidence attached — are a later, different text. `STORY-0158` presents five criteria beside a passing test report; four were verified.

D-018 identified this exact hazard for retro-migrated stories ("two copies would only drift") and fixed it there. The forward case has the same hazard and is worse, because both copies are live and editable, and no document states which is authoritative during the sprint.

**Root cause: a migration workflow promoted to steady state.** All 157 stories were created by retro-migration, where intent and evidence arrive at the same instant and writing the record in one act is correct. Phase 5 carried that shape into the forward case, where they arrive months apart. The artefacts are on the record: `stories/TEMPLATE.md`'s header states it was amended during the Phase 4A pilot to add fields "the pilot's two stories could not be recorded [without]"; D-018 split ownership on retro-vs-forward yet asked only which *file* owns the criteria, never which *stage* writes the record; and `docs/product/README.md` still calls the layer "not a replacement planning surface", which `roadmap-split`'s `STORY-0160` made untrue by requiring a `story_ref` on every forward item in `docs/PLAN.md`.

**Why this needs no schema change.** A story record existing before its evidence is already the established treatment of planned work, not a state this phase introduces. `STORY-0150`–`0155` are six `status: backlog` records reading `Implementation evidence: None — not implemented.`; they pass validation, and D-011 *requires* the shape so undelivered scope holds an identifier rather than being silently absent. `STORY-0160` created ~14 more. This phase only makes it the state every story passes through.

**The objection, and why it was not taken.** That `CONTEXT.md` holds working notes, so drift from a durable record is expected and harmless — a position consistent with the observed data, since the record improved on the note in all five cases. Declined on two grounds. Nothing designates it a draft: `POLICY.md` names `CONTEXT.md` the owner of selected execution scope, `roadmap-split/CONTEXT.md` is headed "scope confirmed … recorded before any in-scope file was touched", and `PHASES.md`'s Phase 6 entry cites it as a **required input**. And granting the premise concedes the substance — whether draft or decided, one text was verified and another is published with that verification attached.

**Effect on later phases:** None. Phase 7 is terminal and self-contained; on completion the programme returns to the steady state defined after Phase 5. It does not reopen Phase 4, does not alter the ID scheme, does not move any story's feature assignment, and grants no authority over `docs/ROADMAP.md`. It binds **new sprints only** — no existing story record is retrofitted, matching the D-029 precedent.

**Consequential amendments authorised by this decision:** `POLICY.md`'s source-of-truth boundary list (which stage writes the forward-authored record); `stories/TEMPLATE.md` (write-stage note, plus the OQ-2 fields); `docs/product/README.md` § Acceptance criteria; `docs/sprints/WORKFLOW.md` § Product traceability; `docs/sprints/STAGE-REGISTRY.md` `pm` and `retro` rows; `validate_registry.py` (OQ-5 rule only).

**Follow-up outside this programme.** The behaviour change lands in `~/.claude/skills/pm/SKILL.md` and `~/.claude/skills/retro/SKILL.md`, which `POLICY.md` forbids this programme from touching and which `WORKFLOW.md` already records as a known gap under D-029. The Phase 5 precedent applies: the programme writes the obligation into `WORKFLOW.md`/`STAGE-REGISTRY.md`, and the skill-side edits are applied by the human and verified. This decision grants no authority over `~/.claude/**`.

**Also surfaced by the same review, not authorised here.** `state.md` records decisions as "D-001–D-029" and Phase 5 as "the last defined phase", both superseded by D-030/Phase 6. That is a **correction** under the steady-state provision — ordinary maintenance, recorded in the relevant sprint's `decisions.md`, needing no phase.

---

*Discovery-phase decisions: D-001–D-006 (governance). Hierarchy-approval-phase decisions: D-007–D-013 (DP-01–DP-07), recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`. Structure-implementation-phase decision: D-014, recorded 2026-07-15 via direct human chat instruction. Phase 4A pilot decision: D-015, recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-authorise-phase-4a-two-story-pilot-migration.md`. Phase 4B confirmed-batch decision: D-016, recorded 2026-07-15 per `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`. Hierarchy-completion decisions: D-017–D-022, recorded 2026-07-28 via direct human chat instruction following human review of the Phase 4A/4B batches. Phase 4 (historical migration) as a whole remains unauthorised, and is now additionally gated behind Phase 3B's human sign-off.*
