# Critic review — Phase 4D `historical migration` (remainder, 103 items)

**Reviewing:** `runs/historical-migration-remainder-run-001.md` and its outputs under `docs/product/`
**Authorisation under review:** D-027 (2026-07-29)
**Method:** independent, read-only. Registry, allocation table, feature counts and story-file headers re-derived from the files themselves rather than taken from the run record's claims.

## Verdict

**PASS**, with three non-blocking observations.

---

## Rubric

| # | Check | Result |
|---|---|---|
| 1 | All 103 authorised items migrated; none missed | **PASS** — `ID-ALLOCATION.md` holds 157 rows, all marked `●`; zero `○` remain |
| 2 | No item migrated that was not in the remainder | **PASS** — registry holds exactly 157 rows against 157 allocated |
| 3 | No identifier renumbered, reused or invented | **PASS** — the 157 registry IDs are exactly the 157 allocated IDs, set-equal |
| 4 | Confidence carried verbatim, no upgrades | **PASS** — re-derived from `ID-ALLOCATION.md` and compared row-for-row: 157/157 match |
| 5 | Feature assignment matches the approved allocation | **PASS** — 157/157 match |
| 6 | Story-file headers agree with their registry rows | **PASS** — status and confidence identical on all 157 |
| 7 | Backlog items not presented as delivered | **PASS** — all 6 carry `status: backlog`; the 5 new ones follow the `STORY-0151` precedent exactly |
| 8 | `origin_code` preserves every legacy code | **PASS** — every legacy token in `ID-ALLOCATION.md` appears in the corresponding registry row; no row has an empty `origin_code` |
| 9 | Every cited evidence path exists on disk | **PASS** — the validator's link-existence check covers every backticked `docs/`/`../` path; no `evidence_refs` cell is empty |
| 10 | `FEATURES.md` round-trip holds both directions | **PASS** — validator-enforced; `migrated` equals `allocated` on all 41 rows |
| 11 | `SOURCE-INDEX.md` reaches every story | **PASS** — validator-enforced; all 157 present |
| 12 | Coverage arithmetic reconciles across all three files | **PASS** — 157 in `ID-ALLOCATION.md`, 157 in `STORY-REGISTRY.md`, 157 summed across `FEATURES.md` |
| 13 | Write scope honoured; no forbidden path modified | **PASS** — changes confined to `docs/product/` and `docs/programmes/product-traceability/` |
| 14 | Governance recorded **before** execution | **PASS** — D-027 and the Phase 4D definition were written before the first story file |
| 15 | Validator passes | **PASS** — 215 content rows checked |

## What was tested independently rather than accepted

The run record claims confidence was carried verbatim. That is the claim most worth distrusting, because a batch this size makes a silent upgrade cheap and invisible. It was re-derived: the `C`/`S`/`T`/`B` marker was parsed out of `ID-ALLOCATION.md` for all 157 items, mapped to its registry vocabulary, and compared against both the registry row and the story file's own header. All three agree on all 157. The batch's own composition — 33 / 53 / 12 / 5 — reconciles to the remainder stated in D-027.

Equally worth distrusting: that a run migrating 103 items in one pass would quietly round up the awkward ones. It did not. The three items whose verification is incomplete or contradicted (`STORY-0057`, `STORY-0103`, `STORY-0105`) each carry `tentative` and an explicit instruction in their *Unresolved questions* section not to cite them as evidence of delivery. `STORY-0148` is the sole `in-flight` row in a 157-row registry, which is the correct treatment of a review programme whose Stage 13 is still open. The two no-code closes (`STORY-0062`, `STORY-0112`) both open their *Delivered behaviour* with "No code shipped."

## Observations — non-blocking

**O-1. Thirty-three of the 103 rest on `docs/ROADMAP.md` alone — a third of the batch.** Sprint 0, Sprints 1–6, Sprint 24, Sprint B-UI and the five backlog items have no dedicated test report; Phase 4C had already flagged ten such items, so the registry-wide total is now 43. Each affected record says so in its *Test / review evidence* section and carries `tentative` or `strongly inferred` accordingly, so nothing is overclaimed. But the registry as a whole now contains a larger single-sourced population than the Phase 4C batch flagged, and for an external audit the relevant number is that **17 items are `tentative` and 66 `strongly inferred` — 53% of the registry is not `confirmed`.** That is an accurate picture of the evidence, not a defect in this run; it is worth stating plainly because a complete-looking registry invites the assumption that completeness implies verification. It does not.

**O-2. `STORY-0054` and `STORY-0055` describe one delivery under two records.** The run record discloses this and gives a defensible reason — two independently navigable registers, both legacy codes preserved. It is nonetheless the one place in the hierarchy where the count of stories exceeds the count of distinct deliveries, and any future metric computed off row counts will be off by one here. Not worth restructuring now; worth knowing before anyone reports "157 delivered items" externally.

**O-3. The completeness claim has a dated shelf life, and the artefacts say so — once.** `README.md` and `ID-ALLOCATION.md` both record the 2026-07-15 horizon and that completeness decays until Phase 5. That disclosure is correctly placed. The risk it does not cover is behavioural: a reader who consults `STORY-REGISTRY.md` directly, three sprints from now, sees a table that looks authoritative and carries no staleness marker of its own. A dated "last reconciled against delivery" line in the registry header would close that gap cheaply. Recommendation only — outside this phase's authorised outputs.

## On the decision to stop batching

D-027 retires capability-shaped batching, and the run honours that without using it as licence to lower standards: the same template, the same validator, the same verbatim-confidence rule and the same evidence discipline applied to 103 items as to the 33 of Phase 4C. The two defects the run found and fixed — five dangling `PT-*` references and a backlog-schema drift caught against the `STORY-0151` precedent — are both the kind that batch review is supposed to catch, and both were caught. That is the strongest available evidence that dropping the batch boundaries did not drop the controls with them.

## Conclusion

Phase 4D is complete and Phase 4 is closed. Coverage is 157/157 with no identifier renumbered, no confidence upgraded, no backlog item presented as delivered, and no forbidden path touched. The three observations above are recorded for the human gate, not as conditions on this verdict.
