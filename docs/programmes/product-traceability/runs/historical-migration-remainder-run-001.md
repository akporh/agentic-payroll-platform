# Run record — Phase 4D `historical migration` (remainder, all 103 items)

**Run ID:** `historical-migration-remainder-run-001`
**Phase:** 4D — `historical migration` (remainder)
**Authorised by:** D-027, 2026-07-29, direct human chat instruction — *"product traceability programme: proceed with migrating all other capabilities no need to process in batch"*
**Date:** 2026-07-29
**Outcome:** complete — **157 of 157 items migrated (100%)**. Phase 4 is closed.

---

## What this run did

Migrated every one of the 103 items that held a reserved identifier and a feature assignment in `../../../product/ID-ALLOCATION.md` and nothing else, taking coverage from 54/157 (34%) to **157/157**.

Unlike Phases 4A (2 items), 4B (19) and 4C (33), this run was **not decomposed into capability-shaped batches** — D-027 retires that pattern explicitly. The batching existed to prove the mechanism at increasing scale; that proof was complete after 4C, and further batch authorisations would only have prolonged the period during which the registry under-reported the platform.

## Sequence

Governance first, execution second — the sequence fixed by Phase 3B and required by `../POLICY.md`'s phase-scoped autonomy.

1. **Stage 0 — governance.** D-027 recorded in `../decisions.md`; Phase 4D defined in `../PHASES.md` with its own allowed paths, required outputs, validations and executor/critic responsibilities; the authorisation-state table updated; Phase 4's historical "not authorised as a whole" status marked superseded rather than overwritten.
2. **Stage 1 — evidence pass.** `../../../diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` §3.1–3.11 read for every remaining item's actor, problem, delivered behaviour, source and confidence; the evidence directories (`docs/stories/`, `docs/test-reports/`, `docs/audit/`, `docs/security/`, `docs/retro-reports/`) enumerated so that no story could cite a file that does not exist.
3. **Stage 2 — write.** 103 story files written to `../../../product/stories/` against `TEMPLATE.md`; 103 rows added to `STORY-REGISTRY.md` and the table rebuilt in ID order.
4. **Stage 3 — reconcile.** `FEATURES.md` `stories`/`migrated` recomputed from the registry for all 41 features; `ID-ALLOCATION.md` flipped 103 rows `○` → `●` and its coverage tables rewritten; `SOURCE-INDEX.md` extended with a legacy-code table and an evidence-file table for the batch; `README.md` status rewritten.
5. **Stage 4 — validate.** See below.

## Outputs

- **103 new story files** under `docs/product/stories/`
- **`STORY-REGISTRY.md`** — 54 → **157 rows**, rebuilt in ID order; the "this is not the full inventory" note replaced with its opposite
- **`FEATURES.md`** — `stories` and `migrated` updated on every feature; `migrated` now equals `allocated` on all 41 rows
- **`ID-ALLOCATION.md`** — all 157 rows marked `●`; coverage tables rewritten to 157/157; a coverage-history table added
- **`SOURCE-INDEX.md`** — 103 legacy-code rows and 32 evidence-file rows added; header rewritten to state full coverage
- **`README.md`** — status section rewritten; guidance added on what an absent story now means and on how completeness decays
- **`../decisions.md`** — D-027
- **`../PHASES.md`** — Phase 4D section; authorisation-state table
- **`../state.md`**, **`../phase-inputs.yaml`** — advanced
- **`../critic-review-phase-4d-remainder.md`**
- this run record

## Composition of the batch

| | Count |
|---|---|
| `confirmed` | 33 |
| `strongly inferred` | 53 |
| `tentative` | 12 |
| `backlog` (recorded as `requires human classification`, `status: backlog`) | 5 |
| **Total** | **103** |

Confidence was carried verbatim from `ID-ALLOCATION.md` and verified row-for-row after writing. **No item was upgraded on migration.** The registry-wide totals after the batch are 68 `confirmed`, 66 `strongly inferred`, 17 `tentative`, 6 `requires human classification`; 150 `delivered`, 6 `backlog`, 1 `in-flight`.

By capability: `CAP-5` 18, `CAP-4` 15, `CAP-3` 14, `CAP-9` 11, `CAP-1` 10, `CAP-7` 9, `CAP-10` 9, `CAP-2` 7, `CAP-8` 7, `CAP-11` 3.

## Judgements made in the run, recorded rather than buried

**1. `STORY-0148` is the only `in-flight` story in the registry.** The `agentic-architecture-review` programme is genuinely incomplete — Stage 13 is open at `awaiting-human-decision`, with DP-2 and DP-9 unrecorded. It was migrated as `in-flight`, not `delivered`, and its record says explicitly that no Phase 2 implementation is authorised until the review closes. Rounding it up would have been the easier and wronger choice.

**2. Three items are contradictions carried forward, not resolved.**
- `STORY-0057` (Gate 4) — `docs/ROADMAP.md` says ✅; the gate's own story file says implementation pending. Migrated `tentative` with both sources cited and an explicit instruction not to treat it as evidence of delivery. This is D-012/DP-06 and stays open.
- `STORY-0103` (Employees.tsx split-action rework) — Sprint 17's test report marks browser UAT **BLOCKED**.
- `STORY-0105` (timesheet LATERAL join) — multi-contract verification **BLOCKED** for want of test data; the fix is applied but unverified.

Resolving any of these requires evidence this programme is not permitted to create.

**3. Two items delivered nothing, and say so.** `STORY-0062` (WI-01 OT multiplier seeds) and `STORY-0112` (Q8-FIX `proration_strategy`) were both closed by establishing that no change was needed. Their *Delivered behaviour* sections open with "**No code shipped.**" A no-code close is a legitimate outcome; presenting it as a delivery would not be.

**4. `STORY-0055` and `STORY-0054` describe the same delivery.** Gate 6 and Track J closed together, and the discovery inventory carried both a `PT-UI-06` and a `PT-A1-18` code for it. Both records are kept — the Track UI and capability-area registers are independently navigable — and the overlap is stated inside `STORY-0055` rather than resolved by deleting a record and breaking one of the two lookups.

**5. Backlog items follow the `STORY-0151` precedent exactly.** `status: backlog`, `confidence: requires human classification`, `ac_owner: source`, and the registry title suffixed "— NOT DELIVERED". Their *Delivered behaviour* sections begin "**Not delivered.**" `STORY-0150`, `0152`, `0153`, `0154`, `0155`.

**6. Every cited `docs/*.md` path was checked against disk.** Where a sprint has no test report — Sprint 0, Sprints 1–6, Sprint 24, Sprint B-UI, Sprint 25 — the record says so in the *Test / review evidence* section rather than citing a plausible-looking file that does not exist. The validator's link-existence check independently confirms this for every backticked path.

## Defects found and fixed during the run

1. **Five dangling `PT-*` references in new story prose.** Sentences of the form "`PT-Q-04` is the Track Q register's duplicate of this item and resolves here" name a legacy code without naming the story it resolves to, which is precisely the dangling-reference shape the validator's legacy-identifier sweep exists to catch. Caught by `validate_registry.py`, not by reading. Reworded to name the story ID explicitly in all five (`STORY-0075`, `0097`, `0104`, `0111`, `0112`).
2. **Backlog-item schema drift, caught before writing.** The first draft assigned backlog items `confidence: confirmed` and `ac_owner: hierarchy`. Checking `STORY-0151` — the one backlog item already migrated — showed the established treatment is `requires human classification` / `source` / "— NOT DELIVERED". Corrected to match rather than establishing a second convention for the same case.

## Validation

| Check | Result |
|---|---|
| `python3 docs/product/validate_registry.py` | **PASS** — 215 content rows checked |
| `git diff --check` | clean |
| Story files present | 157 + `TEMPLATE.md` |
| `STORY-REGISTRY.md` rows | 157, no duplicate ID |
| `ID-ALLOCATION.md` `○` remaining | 0 |
| Confidence matches `ID-ALLOCATION.md` row-for-row | 157/157, no upgrades |
| Feature assignment matches `ID-ALLOCATION.md` row-for-row | 157/157 |
| Story-file header vs registry row (status + confidence) | 157/157 identical |
| `FEATURES.md` `migrated` == `allocated` | all 41 rows |
| Every backticked `docs/`/`../` path exists on disk | enforced by the validator's link check |
| Identifiers renumbered, reused or invented | **none** |
| Forbidden paths modified | **0** |

`git status --short` shows changes confined to `docs/product/` and `docs/programmes/product-traceability/`. The other entries in the working tree (`CLAUDE.md`, two `.mmd` files under `docs/Buisness Specs & Designs (Drifted)/`, and the untracked Phase 3B/4C outputs) predate this run and were not touched by it.

## What is now true that was not

`STORY-REGISTRY.md` and `ID-ALLOCATION.md` return the same number. Until this run, a story's absence from the registry meant either "not yet migrated" or "no such work exists", and nothing distinguished the two. It now means the second — which is the property the programme was commissioned to produce and the first point at which the traceability layer can be used as evidence rather than as a partial index.

## What can still make it wrong

One thing, and it is known: the discovery inventory has a **2026-07-15 horizon** (D-026). Three sprints have already been found missing from it — Sprint 25 and PAY-TAX-1 by method gap (D-024), `dev-levy-rule-pct` by recency (D-026). Any sprint closing after that date registers here only if someone captures it by hand at migration time. **Completeness now decays with every sprint that closes until Phase 5 wires traceability into sprint closure.** Phase 5 is not authorised, and it is now the only phase left.
