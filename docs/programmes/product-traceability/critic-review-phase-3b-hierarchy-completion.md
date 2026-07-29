# Critic Review — Phase 3B (`hierarchy completion`)

**Programme:** `product-traceability` · **Run:** `hierarchy-completion-run-001` · **Date:** 2026-07-28
**Reviewer:** independent critic pass, read-only, separate from the executor pass
**Rubric:** `PHASES.md` Phase 3B "Critic responsibilities" — seven checks.

## Verdict

**PASS** — with two non-blocking observations recorded below.

---

## Check 1 — Does the feature set cover all items, with no overlap and no orphan?

**Confirmed.** Reproduced independently rather than taking the run record's word:

| Assertion | Method | Result |
|---|---|---|
| 155 items allocated | count of content rows in `ID-ALLOCATION.md` | 155 |
| No duplicate identifier | unique-sort of the ID column | 155 distinct |
| No gap in the sequence | numeric sort, index comparison | contiguous `0001`–`0155` |
| `FEATURES.md` `allocated` column reconciles | column sum | 155 |
| `FEATURES.md` `migrated` column reconciles | column sum | 21 |
| Registry ↔ story files | row count vs file count | 21 = 21 |

Every item carries exactly one `feature_id`; the `allocated` sum matching the allocation-table row count means no item is double-counted across features and none is orphaned. `validate_registry.py` independently enforces the story↔feature round-trip in both directions, so an orphan or a mis-listing fails the build rather than resting on this review.

## Check 2 — Is the `OUT-1/2/3` collision genuinely resolved, or papered over?

**Genuinely resolved.** The resolution is not a silent renumbering — `OUTCOMES.md` carries a five-row decode table directly under the heading, stating which registry ID corresponds to which discovery-document ID and declaring the discovery numbering superseded. A reader who arrives holding the discovery document's `OUT-1` is told, in the first screen of the file, that it now means `OUT-4`.

The alternative — renumbering live rows to match the discovery document — was correctly rejected: those IDs are cited across 21 story files, and a second exception to "never renumbered" so soon after the first (D-020) would have hollowed out the rule.

## Check 3 — Is the ID allocation complete, unique, and does it preserve every legacy code?

**Confirmed**, with one strengthening observation.

Uniqueness and contiguity verified above. Legacy-code preservation is enforced structurally, not by convention: `origin_code` is a mandatory column, and `validate_registry.py` fails on an empty one. Spot-check — `grep -rn "PT-A1-22" docs/product/` returns the origin-code cell, the allocation row, the `SOURCE-INDEX.md` mapping and two documentation mentions; the identifier is findable from five directions.

The `PT-A1-24` split (D-023, OQ-8) is correctly traceable: both `STORY-0104` and `STORY-0105` carry `PT-A1-24` as an origin code, distinguished by sub-item. The split is substantively justified rather than cosmetic — the two halves land in different features (`FEAT-8` and `FEAT-13`), which is itself evidence the original item conflated two things.

**Observation C3-1 (non-blocking):** the six items captured under D-024 (`BADGE-RT-1/2`, `EMP-TABLE-1/2/3`, `PAY-TAX-1`) carry their sprint item codes as `origin_code` but have no `PT-*` code, because they never appeared in the discovery inventory. This is correct and self-documenting — the *absence* of a `PT-*` code is now the marker of an item the discovery pass missed. Worth preserving deliberately rather than back-filling synthetic PT codes.

## Check 4 — Was any story content migrated?

**No.** `STORY-REGISTRY.md` holds 21 rows, unchanged in number from the Phase 4A/4B batches; `docs/product/stories/` holds 21 files plus the template. No new story file was created. The 134 unmigrated items appear only in `ID-ALLOCATION.md`, which carries no story-file reference and is explicitly documented as an ID reserve and coverage map, not a registry.

The distinction is load-bearing and correctly implemented: `validate_registry.py` reads rows from `STORY-REGISTRY.md` only, so an allocated-but-unmigrated ID cannot silently acquire the status of a migrated one.

## Check 5 — Was write scope honoured?

**Confirmed.** `git status --short` restricted to `docs/stories/`, `docs/ROADMAP.md`, `backend/`, `frontend/`, `migrations/` returns **empty**. All modifications fall inside `docs/product/` and `docs/programmes/product-traceability/`, matching the D-022 allowed paths exactly.

Of particular note: the P1 fix (reverse provenance) was implemented as `SOURCE-INDEX.md` *inside* `docs/product/` rather than as back-references written into `docs/stories/`. The latter would have been the more obvious implementation and would have violated `POLICY.md`'s prohibition on modifying sprint history. The executor took the constrained path and documented why.

Story files were renamed with `git mv`, so rename history is preserved rather than presenting as delete-plus-add.

## Check 6 — Was the Stage 2 human gate respected?

**Confirmed.** The run record shows Stages 1 and 2 completing with no write to `docs/product/`, an explicit halt, and Stage 3 beginning only after D-023 was recorded. `state.md` carried "STOPPED AT THE HUMAN GATE" between the two. The eight open questions were presented as questions, with recommendations clearly marked as recommendations — no ruling was pre-empted, and the three that were findings rather than preferences were labelled as such.

## Check 7 — Are P1–P6 actually closed, or only asserted closed?

Each verified against the artefact rather than the claim:

| | Problem | Evidence it is closed |
|---|---|---|
| **P1** | No reverse provenance | `SOURCE-INDEX.md` exists with three lookup tables (legacy code, source file, evidence file); validator check 5 fails if a migrated story is absent from it |
| **P2** | No acceptance criteria, contradictory governance | Every story file carries an explicit `## Acceptance criteria` section stating ownership; `POLICY.md`'s boundary restated naming which records; `ac_owner` column added; `TEMPLATE.md` carries both branches |
| **P3** | Opaque IDs | `STORY-<nnnn>` encodes nothing; scheme and rationale documented in `README.md`; `origin_code` mandatory and validator-enforced |
| **P4** | Features show a count, not a list | `stories` column present on all 41 rows; validator enforces the round-trip both ways and against the `migrated` count |
| **P5** | Bare parent IDs; outcome-ID collision | All 21 story files name outcome, capability and feature in words; decode table in `OUTCOMES.md` |
| **P6** | Bottom-up hierarchy | Full tree defined and approved as one proposal (D-023) before any further migration; `ID-ALLOCATION.md` makes coverage measurable — 21/155, and the Execution Engine's 0/31 is now visible |

**P6 deserves specific comment.** The clearest evidence it is closed is that the artefact now surfaces an uncomfortable fact it previously concealed: the Execution Engine, the largest capability at 31 items and the platform's core purpose, has zero migrated coverage. A hierarchy built to flatter the work done so far would not have produced that number.

---

## Observations (non-blocking)

**O-1 — The dangling-reference finding was caught by tooling, not by review.** The re-key updated each story's own identifier but left 27 legacy codes in story *bodies* pointing at retired IDs. Validator check 3 caught it; a reading pass over 21 files plausibly would not have. This is the correct outcome and worth naming: for mechanical transformations, the check belongs in the validator, not the checklist. The same reasoning should apply to any future re-key or bulk rename.

**O-2 — Unmigrated cross-reference targets are honestly marked.** Where a story referenced an item that is allocated but not yet migrated, the executor retained the legacy code and annotated it with the reserved ID plus a pointer to `ID-ALLOCATION.md`, rather than rewriting it to a `STORY-` ID whose record does not exist. Fabricating a link to a non-existent record would have satisfied the validator while degrading the artefact. The judgement was correct.

---

## Scope hygiene

Files modified: 6 programme-control files, 4 registries, 2 new files in `docs/product/`, 21 renamed story files, `TEMPLATE.md`, `README.md`, `validate_registry.py`, 2 run/critic records. All within the D-022 allowed paths. Zero forbidden-path modifications. `git diff --check` clean.

## Conclusion

Phase 3B's authorised scope is complete and its human gate was respected. **Full Phase 4 remains unauthorised**, and Phase 3B's completion does not grant it — 134 items hold reserved identifiers and feature assignments and nothing more.
