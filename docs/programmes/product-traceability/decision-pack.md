# Decision Pack — Product Traceability Programme, Discovery Phase

This pack contains only genuine human decisions arising from the discovery phase. It does not contain routine formatting or mechanical questions. Every recommendation here is a recommendation, not an approval — approval happens only by the human recording a decision in `decisions.md`.

**Status as of 2026-07-15 (Phase 2 closure):** All seven decisions below (DP-01–DP-07) have been made by the human and recorded as D-007 through D-013 in `decisions.md`, per `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md`. The original questions, options, and executor recommendations are preserved below **unmodified** so the historical decision trail remains visible — each is now annotated with a "**Resolved:**" line pointing to the binding decision. This file is retained as the historical record of what was asked and recommended; `decisions.md` is the authoritative record of what was decided.

---

## DP-01 — Story-reconstruction granularity

**Resolved:** Option A selected — see `decisions.md` D-007. Current 148-item granularity retained.

**Question:** Should the delivered-work inventory in the discovery document (`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`, Section 3) use the story/feature-line granularity it currently uses (148 items), or a coarser (one-per-sprint, ~35 items) or finer (one-per-acceptance-criterion, 400+ items) grain?

**Available options:**
- A. Keep current granularity (148 items, matching `docs/ROADMAP.md`'s existing Story Index / Track table rows).
- B. Coarsen to one item per sprint/track (~35 items).
- C. Finer-grain to one item per acceptance criterion (400+ items).

**Executor recommendation:** A. This grain already exists in the source material (ROADMAP's own tables), requires no invented boundaries, and matches the granularity most sprints already report evidence against (one test-report line often covers one story, not one sprint or one acceptance criterion).

**Supporting evidence:** Section 3 of the discovery document; `docs/ROADMAP.md`'s Story Index tables (e.g. Sprint 16, Sprint 17, Sprint 24–28) already itemise at this grain.

**Consequences of each option:**
- A: Registry stays large (148 rows) but each row is independently traceable to one piece of evidence; matches existing convention.
- B: Loses the ability to say "which specific stories in Sprint 16 are done" — defeats part of the programme's stated objective.
- C: Registry becomes unwieldy (400+ rows) and most rows would share identical evidence with their siblings, adding volume without adding traceable information.

**Default if deferred:** Option A stands as the working assumption for this document; a deferral does not block Phase 1 completion since it only affects Phase 4 (historical migration), which is not yet authorised.

**Blocks next phase?** No — blocks Phase 4 only, not Phase 2.

---

## DP-02 — Repository information architecture

**Resolved:** Option A selected — see `decisions.md` D-008. Model A (flat registries + flat `stories/` folder) adopted; Model B rejected.

**Question:** Which repository structure should the eventual `docs/product/` hierarchy use?

**Available options:**
- A. Model A — flat registries (`OUTCOMES.md`, `CAPABILITIES.md`, `FEATURES.md`, `STORY-REGISTRY.md`) plus a flat `stories/` folder.
- B. Model B — deeply nested `outcomes/<x>/capabilities/<y>/features/<z>/stories/<id>.md` folders.
- C. An alternative hybrid not enumerated in this pack.

**Executor recommendation:** A, per Section 9's evaluation table — matches the repository's existing flat-file conventions (`docs/stories/`, `docs/test-reports/`, `docs/audit/`), gives stable story identifiers independent of feature reclassification, and is the cheaper migration path.

**Supporting evidence:** Section 9 of the discovery document (full criterion-by-criterion comparison).

**Consequences of each option:**
- A: Easy validation, easy agent discovery, but requires disciplined registry-file maintenance (a table growing to 150+ rows needs to stay well-organised, e.g. by capability).
- B: Better visual grouping in a file browser, but first deeply-nested doc structure in the repo, higher migration cost, and reclassifying a story later means moving files and breaking existing references.
- C: Unscoped — would require a fresh evaluation pass before Phase 3 could begin.

**Default if deferred:** No structure is created until this is decided (Phase 3 is not authorised regardless).

**Blocks next phase?** Blocks Phase 3 (structure implementation). Does not block Phase 2 (hierarchy approval) — indeed Phase 2 exists specifically to make this decision.

---

## DP-03 — Source-of-truth rules for the product layer

**Resolved:** Option A selected — see `decisions.md` D-009. Proposed rules (Section 10 of the discovery document) adopted as written, no amendment.

**Question:** Should the proposed source-of-truth rules in Section 10 of the discovery document be adopted as written, amended, or rejected?

**Available options:**
- A. Adopt as written.
- B. Amend (specify which rule and how).
- C. Reject and request an alternative proposal.

**Executor recommendation:** A — the proposed rules are a direct extension of the fixed boundaries already approved in `decisions.md` D-005 (from the bootstrap prompt itself), not a new invention.

**Supporting evidence:** Section 10 of the discovery document; `decisions.md` D-005.

**Consequences of each option:**
- A: Product layer's boundary with sprint workflow and story files is clear from day one.
- B: Requires the human to specify the amendment precisely enough to avoid the same ambiguity resurfacing later.
- C: Phase 3 cannot begin until an alternative is proposed and approved.

**Default if deferred:** D-005's boundaries (already approved) remain in force; Section 10's extensions are not adopted.

**Blocks next phase?** No — blocks Phase 3, not Phase 2.

---

## DP-04 — PH_OT `is_pensionable` deferral (Sprint 7 open question OQ1)

**Resolved:** Option B selected — see `decisions.md` D-010. Still open; escalated as a potential statutory-compliance risk **outside this programme**. This programme does not investigate or resolve it. Follow-up investigation required (see D-010's "Follow-up outside this programme").

**Question:** Was the Sprint 7 deferral of `is_pensionable=true` on the `PH_OT` component-metadata row (pending "PH_OT handler ships atomically") ever resolved? If not, is this a live statutory-compliance gap requiring urgent attention outside this programme, or a documentation-only loose end?

**Available options:**
- A. Confirm resolved in a later sprint not surfaced by this discovery pass (cite the sprint).
- B. Confirm still open — escalate to the payroll domain owner as a compliance risk, tracked outside this programme.
- C. Confirm still open — but low/no real-world impact (e.g. no client currently uses PH overtime in a pensionable context) — track as backlog only.

**Executor recommendation:** None — this requires domain knowledge (whether any live client's PH overtime is contractually pensionable) that is outside repository evidence. Recommend B or C pending that check, not A, since no closing evidence was found in this pass.

**Supporting evidence:** `docs/ROADMAP.md` PH-7 row: "Seed component_metadata row for PH_OT with is_pensionable=true ⚠️ (PH-7/OQ1) — row seeded; is_pensionable flag intentionally deferred until PH_OT handler ships atomically." No later sprint story, test report, or audit report closing OQ1 was found.

**Consequences of each option:**
- A: No further action needed for this programme; discovery document should be corrected to reflect the closing evidence.
- B: A sprint should be scoped (outside this programme) to resolve it before any further PH/OT statutory feature work.
- C: Registry carries it as a known, accepted gap.

**Default if deferred:** Treated as an open compliance question, unresolved, in this programme's inventory — no automatic escalation happens on its own.

**Blocks next phase?** No — but recommended for priority attention regardless of this programme's phase sequencing, since it is a potential statutory-compliance gap, not merely a traceability gap.

---

## DP-05 — Resolve the 5 `requires human classification` items

**Resolved:** Option A selected — see `decisions.md` D-011. All 5 classified backlog / not delivered, unless newer evidence is supplied.

**Question:** Confirm the classification of the 5 items flagged `requires human classification` in Section 14 of the discovery document (PT-A1-14 Client 3 shift allowance, PT-Q-02 period_type retry context, PT-Q-03 simulate-script Decimal conversion, PT-Q-07 approved_by actor identity, PT-S-08 python-multipart pin).

**Available options:**
- A. Confirm all 5 as "not delivered / backlog" (matches their ROADMAP 🔜/⬜ status) — exclude from any future "delivered stories" registry view, retain only in the outcome/feature backlog view.
- B. Provide updated status for any of the 5 that have in fact been completed since the evidence was last reviewed.

**Executor recommendation:** A, pending B for any item the human knows to be more current than the reviewed evidence.

**Supporting evidence:** Section 14, items 4; `docs/ROADMAP.md` Track Q, Track S, Track A1 rows cited per item.

**Consequences of each option:**
- A: Registry accurately reflects these as open backlog, not delivered stories.
- B: Registry is corrected before Phase 4 migration, avoiding a later false start.

**Default if deferred:** Treated as open/backlog (option A) by default, since that matches the last-known repository evidence.

**Blocks next phase?** No — blocks Phase 4 accuracy only.

---

## DP-06 — Gate 4 status contradiction

**Resolved:** Option C selected — see `decisions.md` D-012. Neither source trusted as-is; a targeted investigation is required **outside this programme** before either is treated as authoritative. Follow-up investigation required (see D-012's "Follow-up outside this programme").

**Question:** `docs/ROADMAP.md` marks Track UI Gate 4 (Bureau/workspace-setup journey, 8 pages) as ✅ complete, but `docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md` states "🔜 Plan approved April 2026, implementation pending." Which is current?

**Available options:**
- A. Trust `docs/ROADMAP.md` (as this document provisionally did) — the story file is simply stale and should be corrected in a future sprint (not by this programme, which may not modify historical story files).
- B. Trust the story file — ROADMAP's ✅ is itself the stale marker and Gate 4 is not actually complete; escalate to confirm the 8 pages are genuinely built.
- C. Investigate via git history/live app check before either registry entry is trusted (outside this programme's read-only documentation scope).

**Executor recommendation:** C, if the human wants certainty before any future sprint relies on Gate 4 being "done"; A as the safe default for this programme's own inventory, since ROADMAP.md is the more consistently maintained live-status source across the whole repository.

**Supporting evidence:** Section 14, item 2 of the discovery document.

**Consequences of each option:**
- A: Discovery document's PT-UI-04 stays `tentative`; no further action from this programme.
- B: A "completed" UI gate might in fact be missing work — risk if a future sprint assumes those 8 pages exist and are wired.
- C: Resolves the ambiguity definitively but requires effort outside this programme's authorised (documentation-only) scope.

**Default if deferred:** PT-UI-04 remains `tentative` in the registry; no escalation happens automatically.

**Blocks next phase?** No.

---

## DP-07 — Authorise Phase 2 (hierarchy approval)

**Resolved:** Option A selected — see `decisions.md` D-013. Phase 2 authorised and complete. Phase 3 (structure implementation) is **not** authorised by this decision and requires its own separate authorisation.

**Question:** Should the programme proceed to Phase 2?

**Available options:**
- A. Authorise Phase 2 now.
- B. Request amendments to the discovery package first (see critic-review.md once produced).
- C. Do not proceed at this time.

**Executor recommendation:** None — per `POLICY.md`, "authorisation to begin the next phase" is exclusively a human decision; the executor does not recommend a course of action on its own continuation.

**Supporting evidence:** `POLICY.md` "Human approval required for" list; `decisions.md` D-006.

**Consequences of each option:**
- A: Phase 2 review begins — human works through DP-01 through DP-06 above.
- B: Executor applies only critic-requested amendments within discovery scope, then re-submits.
- C: Programme remains paused at Phase 1 indefinitely; no further work occurs.

**Default if deferred:** No phase begins. The programme remains at `state: awaiting human decision-pack approval` (see `state.md`).

**Blocks next phase?** This decision **is** the gate for Phase 2 — by definition it blocks it until answered.
