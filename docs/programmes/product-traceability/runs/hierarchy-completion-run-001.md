# Run record — `hierarchy-completion-run-001` (Phase 3B)

**Programme:** `product-traceability`
**Phase:** 3B — `hierarchy completion`
**Authorised by:** D-022 (2026-07-28, direct human chat instruction)
**Status:** in progress — Stage 0 complete; Stage 1 next
**Allowed paths:** `docs/product/`, `docs/programmes/product-traceability/`

---

## Why this phase exists

On 2026-07-28 the human reviewed the 21 stories migrated by Phases 4A (D-015) and 4B (D-016) and could not answer basic questions from the artefacts: where a story came from, what its identifier means, which stories a feature contains, or why a migrated story lost the acceptance criteria its source story had.

Six problems were identified and each verified against the artefacts before any work began:

| # | Problem | Verified against | Cause |
|---|---|---|---|
| P1 | Provenance one-way — story files link *to* their source, but nothing links source → migrated story, and no coverage view exists | `PT-A1-22`'s "Source reference" section vs. `docs/stories/sprint-17-employee-crud.md` | `POLICY.md` forbids modifying `docs/stories/**`; no inverse index was ever built |
| P2 | Migrated stories carry no acceptance criteria | `docs/stories/sprint-17-employee-crud.md` EMP-B2 has `### Acceptance Criteria`; `PT-A1-22` has none; `stories/TEMPLATE.md` has no such field | D-009's pointer-only rule — **contradicted by `POLICY.md`'s own boundary, "Story records own story definition and authoritative acceptance criteria"**, which never named *which* story records |
| P3 | `PT-A1-22` encodes the programme name (`PT`), a roadmap capability area (`A1`) and a position in a one-off retro inventory (`22`); the decode is written nowhere in `docs/product/` | Discovery document §3.1 table; `STORY-REGISTRY.md` schema note | `STORY-REGISTRY.md` flagged re-keying as a pending human decision — **it was never made, so the provisional scheme became permanent by default** |
| P4 | `FEATURES.md` shows `story_count: 9` but never *which* nine | `FEATURES.md` schema and `FEAT-3` row | Model A (D-008) holds relationships as ID columns; no inverse view was built |
| P5 | Story files show bare `OUT-3`/`CAP-3`/`FEAT-4`. Separately, live `OUT-1/2/3` **are** the discovery document's `OUT-3/OUT-4/OUT-2` — the same identifiers meaning different things across documents that cite each other | `PT-A1-22` header block; `OUTCOMES.md` preamble | D-016 applied its ID+name convention to the three registries but not to the story files |
| P6 | **Root cause** — the hierarchy was built bottom-up, each batch inventing only the rows needed to hold its own stories | `OUT-3`/`CAP-3`/`FEAT-3`/`4`/`5` all created by the A1+A2 batch | Discovery §7–8 explicitly deferred the feature layer until the model was approved; Phase 4A/4B proceeded without it, and no phase went back to produce it |

P6 is the root cause; P4 and P5 are its symptoms. The discovery document had itself warned against exactly this: performing the story-to-feature mapping "before the hierarchy model itself is approved would risk building the mapping around an unapproved structure, which is exactly the kind of scope expansion `POLICY.md` prohibits."

---

## Stage 0 — governance update (complete, 2026-07-28)

Executed **before** any analysis, deliberately. `POLICY.md`'s autonomy mode is phase-scoped — the executor "may not execute a later phase" and "may not expand the authorised file scope beyond what `PHASES.md` grants the active phase" — so a phase authorising this work had to exist before the work started. Producing the analysis first and back-filling the governance afterwards would have reproduced precisely the pattern that caused P6.

### Decisions recorded (`decisions.md`)

| ID | Decision |
|---|---|
| D-017 | Halt migration; complete and approve the hierarchy top-down first |
| D-018 | Acceptance criteria — pointer-only for retro-migrated stories, native for forward-authored stories; resolves the `POLICY.md`/D-009 contradiction |
| D-019 | Meaning-free durable story IDs `STORY-<nnnn>` + allocation rules |
| D-020 | Re-key the 21 migrated stories now; one-time recorded exception to "never renumbered" |
| D-021 | Defer `docs/ROADMAP.md` relabelling until after the traceability layer exists |
| D-022 | Authorise Phase 3B and the governance amendments it requires |

### Files changed

| File | Change |
|---|---|
| `decisions.md` | D-017–D-022 appended; closing provenance paragraph updated |
| `POLICY.md` | (a) acceptance-criteria source-of-truth boundary restated with the retro/forward split and an explicit amendment note; (b) **story identifier scheme** and **the complete outcome/capability/feature set** added to "Human approval required for"; (c) re-keying without a recorded decision added to "Executor may not"; (d) the "may not create the final `docs/product/` structure" prohibition struck through as superseded by D-014, retained as history |
| `PHASES.md` | Phase 3B defined in full (purpose, P1–P6 table, allowed/forbidden paths, inputs, per-stage outputs, reference-path convention, validations, human gate, executor/critic responsibilities); authorisation-state table added to the header, superseding the stale "Only `discovery` is authorised"; Phase 2 annotated as **partial** approval; cross-phase note extended to explain why a phase was added rather than Phase 4's scope stretched |
| `PROGRAMME.md` | `current phase` corrected from the long-stale `discovery` to `hierarchy completion`; scope exclusions corrected; Phase 3B added to the intended-phases list; the D-018 acceptance-criteria split carried into the objective's source-of-truth questions |
| `state.md` | Current phase, rationale, human-gate status, blocked decisions, and next permitted action all rewritten for Phase 3B |
| `phase-inputs.yaml` | `current_phase` → `hierarchy-completion-phase-3b` with per-stage write scopes and the human gate; prior Phase 4B block retained under `previous_phase_*`; D-017–D-022 added; `story_id_scheme` and `reference_path_convention` blocks added |

### Notable governance findings

Three pre-existing inconsistencies were found and corrected rather than left in place:

1. **`POLICY.md`'s acceptance-criteria boundary genuinely contradicted D-009.** This was not a deliberate trade-off that a reviewer had misread — the wording never named which story records it meant. It is the direct cause of P2's surprise, and is now stated explicitly.
2. **The story identifier scheme was absent from "Human approval required for."** That gap is precisely how the discovery document's *provisional* IDs became permanent without anyone deciding they should be. Both the ID scheme and the populated hierarchy are now explicit human gates.
3. **`PROGRAMME.md`'s `current phase` still read `discovery`** — never advanced across Phases 2, 3, 4A and 4B. `state.md` and `phase-inputs.yaml` carried the accurate position throughout, so nothing downstream relied on the stale value.

### Validation

- `git status --short` — only the six programme-control files above modified. No forbidden path touched: nothing under `docs/product/`, `docs/stories/`, `docs/ROADMAP.md`, `backend/`, `frontend/`, `migrations/`.
- `git diff --check` — clean.
- Phase 2's own historical record was **not** retro-edited; its partial scope is recorded as an added note alongside it.

---

## Stage 1 — hierarchy proposal (complete, 2026-07-28)

Output: `hierarchy-proposal.md`. **No file under `docs/product/` was written.**

Defined top-down across the whole inventory: **5 outcomes, 12 capabilities, 41 features, 148 story IDs allocated.**

| Layer | Result |
|---|---|
| Outcomes | 3 live retained unchanged; `OUT-4` (Accurate, compliant statutory payroll calculation) and `OUT-5` (AI-assisted payroll operations) added. The `OUT-1/2/3` collision with the discovery document is resolved by keeping live numbering and retiring the discovery numbering to a permanent decode table. |
| Capabilities | `CAP-1` and `CAP-2` proposed for **rename** (IDs unchanged) — both were named identically to their parent outcome, having been created to hold one pilot story each. `CAP-3` narrowed; `CAP-4`–`CAP-12` added. |
| Features | 41 across 11 populated capabilities — the layer that had never been defined. Live `FEAT-1`–`FEAT-5` retained by ID, two re-scoped. |
| Stories | All 148 allocated `STORY-<nnnn>` in chronological delivery order per D-019, each carrying its origin code(s). |

### Findings

1. **Both outstanding duplicate-ID mappings resolved.** `PT-A4-31`/`PT-Q-01` → `STORY-0138`; `PT-A4-32`/`PT-S-07` → `STORY-0139`. Each is one story carrying two origin codes. These had been open since the Phase 4A pilot.
2. **Coverage is now measurable, and lopsided.** The Execution Engine (`CAP-6`, 27 stories) has **zero** migrated coverage; Onboarding and Employee Lifecycle hold 19 of the 21. This is a direct artefact of the batch-selection rule, and is the clearest demonstration of why P6 mattered.
3. **Two sprints appear to be missing from the discovery inventory** — Sprint PAY-TAX-1 and Sprint 25 both have `docs/ROADMAP.md` sections but no `PT-*` item. Recorded as OQ-2/OQ-3; a discovery-phase gap, not a hierarchy defect.
4. **Item-count discrepancy.** The discovery document states 148; summing its tables and removing the nine documented duplicates and grouping rows yields 149. Recorded as OQ-1, unresolved — deliberately not fudged.
5. **No `EPIC-*` delivery rows proposed** — sprint/track membership is already per-story in `sprint_refs`. Recorded as OQ-7 so the non-adoption is a visible choice rather than an omission.

Eight open questions (OQ-1…OQ-8) are recorded in §8 of the proposal. Three are findings; five need a human ruling.

## Stage 2 — visual sign-off artefact (complete, 2026-07-28)

Published as a self-contained interactive page: the full tree expandable outcome → capability → feature → story, **every feature listing its member stories by name** (the P4 fix, demonstrated rather than asserted), per-feature and per-capability migrated-coverage bars, confidence encoded as an ordinal ramp rather than a good/bad semantic scale, migrated/not-migrated filters, search across titles and both old and new IDs, and the eight open questions inline.

**Phase halts here.** Stage 3 is blocked pending the human's sign-off.

## Human gate — passed 2026-07-28 (D-023)

The hierarchy was approved as a whole at outcome, capability, feature and story level. All eight open questions were ruled on; five were approved as proposed, and three were findings the human directed action on. Two of those — Sprint 25 and Sprint PAY-TAX-1 — were resolved as **capture the missing work** (D-024) rather than as hierarchy defects.

## Stage 3 — apply (complete, 2026-07-28)

### What was written

| File | Change |
|---|---|
| `OUTCOMES.md` | Full set of 5. `OUT-4`/`OUT-5` added; the discovery-document ID collision resolved with a permanent decode table at the top of the file. |
| `CAPABILITIES.md` | Full set of 12. `CAP-1`/`CAP-2` renamed (IDs unchanged); `CAP-3` narrowed; `CAP-4`–`CAP-12` added; the `EPIC-*` non-adoption recorded in prose so it reads as a choice. |
| `FEATURES.md` | All 41. **`stories` column added** listing member story IDs — the P4 fix — plus `migrated`/`allocated` counts so the gap between them is legible as the migration backlog. |
| `STORY-REGISTRY.md` | 21 rows re-keyed; `origin_code` and `ac_owner` columns added. Scope note added distinguishing it from `ID-ALLOCATION.md`. |
| `ID-ALLOCATION.md` | **New.** All 155 items with reserved IDs, feature assignments, confidence and migrated state — the coverage map. |
| `SOURCE-INDEX.md` | **New.** Reverse lookup by legacy code, source file and evidence file — the P1 fix, built *without* touching `docs/stories/`, which `POLICY.md` forbids. |
| `stories/*.md` | 21 files renamed to `STORY-<nnnn>-<slug>.md`; headers rewritten with `Origin code(s)`, ID **and name** for every parent, and an explicit acceptance-criteria ownership statement. |
| `stories/TEMPLATE.md` | `Origin code(s)` and `Acceptance criteria` sections added, with the retro/forward split spelled out; amendment rationale recorded. |
| `README.md` | Rewritten: which file answers what, the ID scheme and its rationale, allocation rules, the acceptance-criteria split, and the reference-path convention. |
| `validate_registry.py` | Extended — see below. |

### Validator: five new checks

`python3 docs/product/validate_registry.py` → **PASS** (79 content rows).

1. `origin_code` present on every story row.
2. `FEATURES.md`'s `stories` column round-trips against `STORY-REGISTRY.md`'s `feature_id`, **both directions**, and matches the `migrated` count.
3. No live `PT-*` identifier survives outside a declared origin code, an amendment-history section, or a mapping statement that names the replacement.
4. **Link existence** — every `../…` or `docs/…` reference resolves on disk. This is what makes relocating `docs/product/` a loud one-pass fix rather than slow rot.
5. Every migrated story appears in `SOURCE-INDEX.md`.

A column-index bug was also fixed: inserting `origin_code` at position 1 shifted `feature_id` from index 2 to 3, which the existing name-matching checks would otherwise have read from the wrong column.

### Finding: the re-key left dangling cross-references

The header rewrite changed each story's own identifier but not the references stories make **to each other** — `STORY-0102` still said "Depends on `PT-A1-21`". 27 distinct legacy codes across 16 files were pointing at retired identifiers.

**The validator caught this, not review.** Check 3 exists precisely because a re-key is exactly the kind of change that updates the obvious surface and misses the cross-references. Fixed by rewriting each reference to its new ID with the old one retained in parentheses; targets that are allocated-but-unmigrated keep their legacy code with a pointer to `ID-ALLOCATION.md`, because inventing a link to a record that does not exist would be worse than an honest one.

### Validation

- `python3 docs/product/validate_registry.py` — PASS.
- `git diff --check` — clean.
- `git status --short docs/stories/ docs/ROADMAP.md backend/ frontend/ migrations/` — **empty**. No forbidden path touched; history remains a read-only input.
- `grep -rn PT-A1-22 docs/product/` returns the origin-code cell, the allocation row, the source index and two documentation mentions — never a live reference.
- Story files renamed with `git mv`, so history follows the rename.

### Still open

- **OQ-1 (148 vs 149)** — ruled "proceed" (D-023). Now moot in its original form: the allocation is 155 by construction, and each ID is individually accounted for in `ID-ALLOCATION.md`. Any residual discrepancy surfaces when the remaining 134 story files are created in Phase 4.
- Phase 4 migration of those 134 items — **not authorised**.

## Critic

See `critic-review-phase-3b-hierarchy-completion.md`.

## Stage 3 — apply

*Blocked* until the human signs off the Stage 2 artefact.
