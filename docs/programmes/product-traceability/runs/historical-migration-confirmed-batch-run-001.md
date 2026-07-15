# Run Record — `historical-migration-confirmed-batch-run-001`

**Phase:** 4B — bounded confirmed-story batch migration (Phase 4 `historical migration`, one-capability-area batch scope only)
**Date:** 2026-07-15
**Authorising prompt:** `docs/diagnostics/2026-07-15-prompt-authorise-phase-4b-confirmed-capability-batch.md`
**Authorising decision:** D-016 (`docs/programmes/product-traceability/decisions.md`)

---

## Start state

- Phase 4A pilot complete: `docs/product/` contained `OUT-1`/`OUT-2`, `CAP-1`/`CAP-2`, `FEAT-1`/`FEAT-2`, and story rows/files for `PT-A4-31`/`PT-A4-32` (13 total content rows across the four registries).
- Phase 4 as a whole: not authorised beyond the Phase 4A pilot.
- Pre-existing, unrelated uncommitted working-tree state at run start (left untouched by this run): `docs/ROADMAP.md` (modified), `docs/test-harness-checklist.md` (deleted), `docs/test-reports/test-harness/` (untracked), `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md` (untracked). None of these paths were read from or written to by this run.

## Authorisation decision

D-016 was recorded in `decisions.md` (see that file) authorising a bounded Phase 4B batch: every `confirmed`-confidence story from exactly one capability area, selected per the authorising prompt's batch-selection rule, plus a human-readable parent-name schema amendment. Phase 4 as a whole remains unauthorised.

## Schema amendment and rationale

Per the authorising prompt's "Mandatory human-readable registry amendment" section, `CAPABILITIES.md`, `FEATURES.md`, and `STORY-REGISTRY.md` each gained one new display-only column:
- `CAPABILITIES.md`: `outcome_name` (after `outcome_id`).
- `FEATURES.md`: `capability_name` (after `capability_id`).
- `STORY-REGISTRY.md`: `feature_name` (after `feature_id`).

IDs remain the sole authoritative reference for identity and relationships; names are a display convenience only. `validate_registry.py` was extended (see "Validator changes" below) to reject any row whose displayed name has drifted from its parent's actual current name, or is missing, and to reject duplicate IDs within a single registry and ambiguous story-file prefix matches. `docs/product/README.md` was updated to state this convention explicitly. The two existing Phase 4A rows (`CAP-1`/`CAP-2`, `FEAT-1`/`FEAT-2`, `PT-A4-31`/`PT-A4-32`) were updated in the same change to carry the new display columns, so they remain valid under the amended schema rather than becoming legacy exceptions.

## Batch-selection rationale

Per the authorising prompt's preference order (an area with 10–20 confirmed items, preferred over any other option), confirmed-item counts were tallied directly from the discovery document (`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`), Section 3, per capability area:

| Capability area | Confirmed items (discovery doc) | Notes |
|---|---|---|
| **A1+A2 — Onboarding & Workforce Setup** | **19** | Selected — within the 10–20 band, no subsetting judgement call needed. |
| A4 — Execution | 13 | 2 of the 13 (`PT-A4-31`, `PT-A4-32`) are already migrated under Phase 4A; would require either accepting overlap or subsetting to 11 — a less clean fit than A1+A2's 19. |
| A5 — Governance | 2 | Below the 10–20 band. |
| A6 — Disbursement | 3 | Below the 10–20 band. |
| A7–A10 — Correctness/Temporal/Snapshot/Audit | 6 | Below the 10–20 band. |
| Track S — Security | 2 (excluding `PT-S-07`, already migrated as `PT-A4-32`) | Below the 10–20 band. |
| Track Q — Audit Observations | 1 net new (excluding duplicates of already-migrated/A4/A7 items) | Below the 10–20 band. |
| Track UI — Design System | 4 | Below the 10–20 band. |
| Cross-cutting (X), Programme-level (M) | 1, 4 | Below the 10–20 band; also thin, cross-cutting groupings the authorising prompt's "do not select unrelated items merely to hit a target" would have discouraged treating as one coherent area anyway. |

**A1+A2 selected** under preference-order rule 1. 19 confirmed candidate items were found; all 19 were included (see "Executor findings" — zero excluded after direct inspection, though several were migrated with a disclosed evidence caveat rather than being excluded — see below). Two nominally-partial items in the same discovery-document section, `PT-A1-23` and `PT-A1-24`, were excluded from candidacy at the outset because the discovery document itself does not classify them as cleanly `confirmed` (`PT-A1-23` is `tentative`; `PT-A1-24` is "confirmed for B0a; tentative for B0b" — a mixed classification, not a clean `confirmed`).

**Expected outcomes/capabilities/features to create:** one new outcome (`OUT-3`, reusing the discovery document's proposed OUT-2 framing — "Operationally usable payroll administration"), one new durable capability (`CAP-3`, corresponding to ROADMAP capability area A1+A2), three new features grouping the 19 items by genuine product intent (not sprint/delivery-order): `FEAT-3` "Post-onboarding configuration management" (Track J, 9 items), `FEAT-4` "Employee lifecycle management" (8 items), `FEAT-5` "Attendance & timesheet configuration" (2 items). **Expected story count:** 19.

## Included and excluded story IDs

**Included (19, all migrated):** `PT-A1-07`, `PT-A1-08`, `PT-A1-09`, `PT-A1-10`, `PT-A1-11`, `PT-A1-15`, `PT-A1-16`, `PT-A1-17`, `PT-A1-18` (→ `FEAT-3`); `PT-A1-19`, `PT-A1-20`, `PT-A1-21`, `PT-A1-22`, `PT-A1-25`, `PT-A1-28`, `PT-A1-38`, `PT-A1-39` (→ `FEAT-4`); `PT-A1-41`, `PT-A1-42` (→ `FEAT-5`).

**Excluded from candidacy (not part of the 19, not migrated):** `PT-A1-23` (discovery-document confidence: `tentative` — browser UAT BLOCKED for the whole item), `PT-A1-24` (mixed `confirmed`/`tentative` — B0a confirmed but B0b tentative; excluded as a whole rather than partially migrated, since this batch only migrates cleanly `confirmed` items), `PT-A1-45` (`tentative` — "seeds already correct; no migration needed," not a shipped fix), and every other A1+A2 item the discovery document itself classifies as `strongly inferred`, `tentative`, or `requires human classification` (`PT-A1-01`–`06`, `12`–`14`, `26`–`27`, `29`–`37`, `40`, `43`–`47`).

**Zero items excluded after direct inspection during migration** — see "Executor findings" for items whose evidence was found weaker than the discovery document's blanket label implied, all of which were migrated with the discrepancy disclosed rather than excluded, per the authorising prompt's instruction that this is a valid outcome distinct from silent downgrade-and-migrate.

## Files inspected and changed

**Inspected (read-only):** `docs/programmes/product-traceability/{PROGRAMME.md,POLICY.md,PHASES.md,state.md,decisions.md,phase-inputs.yaml,exceptions.md,critic-review-phase-4a-pilot.md,runs/historical-migration-pilot-run-001.md}`; `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` (Section 3.1 primarily); all files under `docs/product/` (pre-batch state); `docs/ROADMAP.md` (read-only — Track J / Gate 6 / Sprint 11 / Sprint 17 / Sprint 16 sections, and the Gate 6 completion note); `docs/stories/track-j-workspace-config-management.md` and other cited `docs/stories/*.md` files; `docs/test-reports/2026-04-21-track-j.md` and other cited dated test reports; git history (`git log`/`git show`) to isolate commit references; current `backend/`/`frontend/src/` source for several items where a dedicated test report was thin or contradictory (read-only — no production file was modified).

**Changed (all inside the authorised `docs/product/` / `docs/programmes/product-traceability/` scope):**
- `docs/product/OUTCOMES.md` — `+OUT-3`; `+outcome_name` column on all rows.
- `docs/product/CAPABILITIES.md` — `+CAP-3`; `+outcome_name` column on all rows.
- `docs/product/FEATURES.md` — `+FEAT-3/4/5`; `+capability_name` column on all rows.
- `docs/product/STORY-REGISTRY.md` — `+19` rows; `+feature_name` column on all rows.
- `docs/product/stories/PT-A1-{07,08,09,10,11,15,16,17,18,19,20,21,22,25,28,38,39,41,42}-*.md` — 19 new story files.
- `docs/product/README.md` — status section (both batches now recorded) and validation-mechanism section (name/duplicate/ambiguity checks) updated.
- `docs/product/validate_registry.py` — extended per "Validator changes" below.
- `docs/programmes/product-traceability/decisions.md` — D-016 appended.
- `docs/programmes/product-traceability/PHASES.md` — Phase 4 section updated to record both Phase 4A and Phase 4B.
- `docs/programmes/product-traceability/state.md` — current phase, executor/critic status, human-gate status, completed outputs, blocked/outstanding decisions, next permitted action all updated.
- `docs/programmes/product-traceability/phase-inputs.yaml` — pilot+batch run IDs, current phase, migrated story IDs (this batch and cumulative), batch outputs recorded.
- `docs/programmes/product-traceability/exceptions.md` — Phase 4B section appended.
- `docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md` (this file).
- `docs/programmes/product-traceability/critic-review-phase-4b-confirmed-batch.md` (written after critic review — see below).

## Hierarchy rows created and reused

**Created:** `OUT-3` (Operationally usable payroll administration); `CAP-3` (Onboarding & Workforce Setup, durable, serves `OUT-3`); `FEAT-3` (Post-onboarding configuration management, serves `CAP-3`, 9 stories); `FEAT-4` (Employee lifecycle management, serves `CAP-3`, 8 stories); `FEAT-5` (Attendance & timesheet configuration, serves `CAP-3`, 2 stories).

**Reused:** none of `OUT-1`/`OUT-2`, `CAP-1`/`CAP-2`, `FEAT-1`/`FEAT-2` — this batch's stories serve a genuinely different outcome/capability than Phase 4A's audit-trace and upload-security stories, so no cross-batch reuse was appropriate. Within the batch itself, all 19 stories reuse the single new `CAP-3` (one durable capability, three features) rather than creating a capability per story or per sprint — Track J's 9 items in particular span several literal Track-J sub-items (WC-1 through WC-11) but represent one coherent product-intent area (post-onboarding configuration), not 9 separate capabilities.

## Validator changes

`validate_registry.py` was extended, as explicitly authorised by D-016, to:
1. Reject duplicate IDs within any single registry (new `check_duplicate_ids` helper, run against all four registries).
2. Enforce that every `outcome_name`/`capability_name`/`feature_name` display field is present and exactly matches its referenced parent's current authoritative `name` — reject if missing or mismatched.
3. Reject an ambiguous story-file-to-story-ID match: a story_id matching more than one file, or a file stem matching more than one story_id (previously the script only checked "does at least one match exist," not "is the match unique").
Existing Phase 4A validation behaviour (story/file prefix matching, capability→outcome and feature→capability existence checks) was preserved, not weakened, per the authorising prompt's explicit instruction.

## Validation and reconciliation results

```
$ python3 docs/product/validate_registry.py
PASS — docs/product/ registries are internally consistent (32 total content row(s) checked).

$ git diff --check
(no output — clean, exit 0)

$ git status --short
 M docs/ROADMAP.md                                              <- pre-existing, unrelated, untouched by this run
 M docs/product/CAPABILITIES.md
 M docs/product/FEATURES.md
 M docs/product/OUTCOMES.md
 M docs/product/README.md
 M docs/product/STORY-REGISTRY.md
 M docs/product/validate_registry.py
 M docs/programmes/product-traceability/PHASES.md
 M docs/programmes/product-traceability/decisions.md
 M docs/programmes/product-traceability/exceptions.md
 M docs/programmes/product-traceability/phase-inputs.yaml
 M docs/programmes/product-traceability/state.md
 D docs/test-harness-checklist.md                                <- pre-existing, unrelated, untouched by this run
?? docs/product/stories/PT-A1-*.md (19 files)
?? docs/test-reports/test-harness/                                <- pre-existing, unrelated, untouched by this run
?? docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md    <- pre-existing, unrelated, untouched by this run
```

**Reconciliation (per the authorising prompt's required proof list):**
- Every selected item appears exactly once in `STORY-REGISTRY.md`: confirmed — `grep -c "^| \`PT-" STORY-REGISTRY.md` = 21 (2 Phase 4A + 19 Phase 4B), no duplicates (validator's duplicate-ID check passes).
- Every selected item has exactly one story file: confirmed — 21 non-template files in `stories/`, validator's ambiguous-prefix check passes.
- Every story resolves to valid feature, capability, and outcome IDs: confirmed by validator (all 19 `feature_id`s exist in `FEATURES.md`; `FEAT-3/4/5`'s `capability_id` = `CAP-3` exists in `CAPABILITIES.md`; `CAP-3`'s `outcome_id` = `OUT-3` exists in `OUTCOMES.md`).
- Every displayed parent name matches its authoritative parent registry: confirmed by validator's name-matching check (0 errors reported).
- No excluded item was migrated: confirmed by direct comparison of the 19 migrated IDs against the "Included and excluded" list above — `PT-A1-23`, `PT-A1-24`, `PT-A1-45`, and every strongly-inferred/tentative/requires-human-classification A1+A2 item are absent from `STORY-REGISTRY.md`.
- The two Phase 4A stories remain valid after the schema amendment: confirmed — `PT-A4-31`/`PT-A4-32` rows carry the new `feature_name` column correctly, `CAP-1`/`CAP-2` carry `outcome_name` correctly, `FEAT-1`/`FEAT-2` carry `capability_name` correctly; validator's name-matching check covers these rows too and passes.
- Migrated count equals selected count: 19 selected, 19 migrated, 0 excluded post-selection.

## Executor findings

All findings from the delegated research/drafting pass (independently spot-checked in this session — see below) plus this session's own direct verification:
- Confirmed all 19 story files exist with the exact required filenames (`<story-id>-<slug>.md`) and all 19 registry rows exist, via direct `find`/`grep`.
- Independently re-verified two of the most significant evidence caveats raised by the drafting pass: `PT-A1-09`'s WC-6 GAP claim (`docs/test-reports/2026-04-21-track-j.md` lines 34/81 — confirmed the GAP language is real and verbatim as cited) and commit `db17ef9` (`git show --stat` — confirmed date 2026-04-22, message matches the WorkspaceConfig overhaul claim) and commit `0a2702d` (confirmed date 2026-07-05, message matches the Withdraw-action supersession claim exactly as described in `PT-A1-10`'s story file).
- No item's evidence was found to fail outright (no fabricated commit SHA, no cited file that does not exist, no claim directly contradicted by code that isn't also disclosed in the story file itself) — the five items flagged in `exceptions.md`'s Phase 4B section were judged, on direct inspection, to still meet a genuine `confirmed` bar because the underlying delivered capability is demonstrably present in the current codebase; the gap in each case is in the freshness/completeness of the dated review trail, not in whether the thing was actually built.
- All 19 stories carry non-placeholder, evidenced content in every required field (Actor, Problem addressed, Delivered behaviour, Source reference, Implementation evidence, Test/review evidence, Decision references, Dependencies, Delivery sprint(s), Delivery history, Unresolved questions) — spot-checked across a sample spanning all three features.
- No forbidden path was modified (confirmed by `git status --short` above); no pre-existing unrelated working-tree change was touched.

## Critic verdict

See `critic-review-phase-4b-confirmed-batch.md`, produced by an independent read-only critic pass after all executor artefacts above existed. The critic was specifically asked to assess whether the five evidence-caveat items disclosed above were correctly migrated-with-disclosure versus should have been excluded.

## Amendments made after criticism

Verdict: `approve-with-amendments` (see `critic-review-phase-4b-confirmed-batch.md` for full detail). One required amendment, explicitly waived from re-review by the critic as a disclosure-text-only addition:

- Added an "Overlap disclosure" paragraph to `docs/product/stories/PT-A1-25-split-edit-change-grade-salary.md`'s Unresolved questions section, recording that `PT-A1-25` and the excluded `PT-A1-23` both describe the same Sprint 17 Track B3 delivery increment and rest on the identical evidence base (`docs/test-reports/2026-05-27-sprint-17-full.md`'s B3 section), with the discovery document giving them different confidence labels without reconciling the overlap. This does not change `PT-A1-25`'s migration status — its own EMP-UX-1 acceptance criteria are independently code-level verified — but surfaces the classification overlap explicitly for a future migration pass, rather than leaving it implicit in only the shared "browser UAT BLOCKED" caveat that was already disclosed.
- Re-ran `python3 docs/product/validate_registry.py` after the fix: `PASS — docs/product/ registries are internally consistent (32 total content row(s) checked).` — unaffected, as expected (a prose-only addition to a story file's Unresolved questions section does not touch any registry row or the validator's checks).

No other amendment was required. The critic independently re-verified all 5 disclosed evidence-caveat items (`PT-A1-09`, `PT-A1-10`, `PT-A1-25`, `PT-A1-28`/`PT-A1-38`/`PT-A1-39`, `PT-A1-41`/`PT-A1-42`) by reading cited test reports and running the cited `git show` commands, and confirmed "migrate with disclosure" (rather than exclude) was the right call in every case — the underlying delivered capability is genuinely present in the codebase in each instance.

## Commit SHA(s)

`8a9d357` — "docs: migrate confirmed product stories batch", pushed to `origin/uat`. Only the 32 authorised files under `docs/product/` and `docs/programmes/product-traceability/` were staged and committed; the pre-existing unrelated working-tree changes (`docs/ROADMAP.md`, `docs/test-harness-checklist.md`, `docs/test-reports/test-harness/`, `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md`) were left uncommitted, exactly as found at run start.

## Outstanding items

- Whether the five evidence-caveat items (`PT-A1-09`, `PT-A1-10`, `PT-A1-25`, `PT-A1-28`/`PT-A1-38`/`PT-A1-39`, `PT-A1-41`/`PT-A1-42`) should eventually get a dedicated re-verification pass (e.g. a small follow-up `/tester` or `/auditor` pass outside this programme) rather than resting indefinitely on this migration's own direct-inspection judgement call.
- Whether `PT-A1-23`/`PT-A1-24`/`PT-A1-45` (excluded from this batch as not cleanly confirmed) should be revisited in a future batch once their evidence gaps are closed by ordinary delivery work — not a decision for this programme to make unilaterally.
- The two pre-existing open follow-up investigations (PH_OT `is_pensionable`, D-010/DP-04; Gate 4 status contradiction, D-012/DP-06) remain open and unaffected by this batch — neither `PT-A1-02` (the PH_OT item) nor `PT-UI-04` (Gate 4) was part of this confirmed-only A1+A2 batch (both are lower-confidence than `confirmed` in the discovery document).
- Whether any further Phase 4 batch (another capability area, or the strongly-inferred tier) should be authorised — a human decision, not proposed here.

## Next permitted action

Human review of this batch's quality (registry rows, story files, the five disclosed evidence caveats, critic verdict), and explicit authorisation of any further Phase 4 migration batch scope only, if and when desired. No further story may be migrated, and full Phase 4 must not begin, without a further explicit human decision.
