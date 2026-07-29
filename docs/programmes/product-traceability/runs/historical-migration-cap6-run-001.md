# Run record — `historical-migration-cap6-run-001` (Phase 4C)

**Programme:** `product-traceability` · **Phase:** 4C — `CAP-6` Execution Engine batch
**Authorised by:** D-025 (31 items), extended to 33 by D-026 · **Date:** 2026-07-28
**Status:** complete · **Allowed paths:** `docs/product/`, `docs/programmes/product-traceability/`

---

## Scope

Every item allocated to `CAP-6` Execution Engine — the platform's core reason to exist, and the capability that had **zero** migrated coverage after Phases 4A/4B.

| Feature | Items |
|---|---|
| `FEAT-18` Core calculation & component execution | 4 |
| `FEAT-19` Statutory deduction correctness | 9 |
| `FEAT-20` Proration & period handling | 2 |
| `FEAT-21` Overtime, shift & public-holiday pay | 5 |
| `FEAT-22` Rule resolution & versioning behaviour | 4 |
| `FEAT-23` Run retry & recovery | 4 |
| `FEAT-24` Engine defect remediation | 4 |
| `FEAT-25` Execution observability | 1 |
| **Total** | **33** |

Composition: 14 `confirmed`, 13 `strongly inferred`, 5 `tentative`, 1 `backlog`.

## Departure from the Phase 4B batch rule

D-016 selected `confirmed`-only items. **That rule was deliberately not carried forward** (D-025). Confirmed-only would have migrated 12 of 31 and left the Execution Engine partially covered — reproducing, inside one capability, the patchy-coverage problem Phase 3B existed to fix.

Confidence is carried **verbatim**. Nothing was upgraded. `POLICY.md` prohibits classifying an item `confirmed` without evidence; it does not prohibit recording an item at a lower confidence, and this batch does not weaken it. Where evidence is thin the gap is named in that story's own `Unresolved questions`.

## Finding: a third uninventoried sprint

Sprint `dev-levy-rule-pct` (2026-07-16) was found during evidence gathering and captured under D-026 as `STORY-0156` (DEV-LEVY-1) and `STORY-0157` (RULE-PCT-1).

**The cause differs from the previous two.** Sprint 25 and PAY-TAX-1 (D-024) were missed by the area-based sweep. This one was missed by **date**: the discovery pass ran 2026-07-15; the sprint closed 2026-07-16. Nothing was overlooked — the inventory simply has a horizon, and no mechanism existed to catch work delivered past it.

It is also among the best-evidenced work in the repository: a full ICM sprint workspace, a test report recording 327 passed / 1 intentional skip / 0 failed with 8 LIVE API checks, and an audit review whose CRITICAL finding was fixed and re-verified *before* the test pass began.

Allocated **forward** (D-019 rule 2) as `STORY-0156`/`0157`, not inserted chronologically — the seed pass is spent and D-019 rule 3 now binds absolutely.

**Standing implication:** the inventory has a 2026-07-15 horizon. Any sprint closing after it is invisible and must be captured by hand at migration time. Phase 5 (`sprint-workflow integration`) is the durable fix.

## Notable content decisions

Records were written from source evidence, not restated from the allocation table. Several capture things a summary would have lost:

- **`STORY-0156`** records the actual defect: the January 2026 reconciliation against Sandy's legacy system (run `e3bd910a`) showed **every one of 184 employees** short a ₦100 Development Levy. The handler existed at priority 430 but never fired, and would have computed ₦0 if it had. The dual OR'd cadence triggers and the December/January double-charge question are recorded as the deliberate design they are (DEC-04), not as a bug.
- **`STORY-0038`** keeps its `tentative` status and states why: ROADMAP marks PH-3 ✅ while its own notes column says `classify_day` "has no call site yet (dead code)". A function that exists but is never called is a materially different delivery state from "done". Carried from the discovery document's §14 risk list rather than quietly resolved.
- **`STORY-0020`** records a partial withdrawal: full-run retry is recorded as delivered, but `payroll_retry_request.retry_strategy` now permits `PER_EMPLOYEE` only, with `FULL_RUN` disabled by migration. The capability described is partly withdrawn, and the withdrawing change is not itself inventoried.
- **`STORY-0022`** notes that the architecture-review programme's finding F-07-01 identifies `get_run_timeline` — this story's own route — as one of five with decorative rather than enforced workspace scoping. A live security finding against a story recorded as delivered.
- **`STORY-0023`** / **`STORY-0034`** together show a recurring defect class: a statutory component silently resolving to ₦0 because of a key mismatch, fixed for NHF in Sprints 1–6 (SR9) and again for NHF, health and dev levy in Sprint 7 (FIX-2/FIX-3). Recorded because the pattern matters more than either instance.
- **`STORY-0151`** is migrated as `backlog`, **not delivered** — recorded so the Execution Engine's picture is complete and the item cannot be mistaken for a capability by omission.

## Files changed

| File | Change |
|---|---|
| `docs/product/stories/` | 33 new `STORY-<nnnn>-<slug>.md` records |
| `STORY-REGISTRY.md` | +33 rows; table rebuilt in ID order so the new rows interleave with the existing 21; scope note updated to 157/54 |
| `FEATURES.md` | `stories`/`migrated`/`allocated` updated for `FEAT-18`–`FEAT-25`; totals to 54/157 |
| `ID-ALLOCATION.md` | 31 rows marked migrated; new `dev-levy-rule-pct` section; header and coverage tables updated to 157 |
| `SOURCE-INDEX.md` | `CAP-6` section — legacy-code map (nine schemes), evidence-file map, and an explicit list of the ten items that have no dedicated evidence file |
| `decisions.md` | D-025, D-026 |
| `state.md` | current phase, executor/critic status, human-gate status, outputs, next action |

## Validation

- `python3 docs/product/validate_registry.py` — **PASS** (112 content rows).
- `git status --short docs/stories/ docs/ROADMAP.md backend/ frontend/ migrations/` — **empty**. No forbidden path touched.
- Story-file count = registry-row count = 54.
- `ID-ALLOCATION.md` migrated markers = 54.
- Every `CAP-6` story appears in `SOURCE-INDEX.md` (validator-enforced).

## Two mechanical defects caught during the run

1. **Registry column indices.** Inserting `origin_code` at index 1 in Phase 3B shifted `feature_id` from 2 to 3; the validator's name-matching checks were still reading the old positions. Fixed and commented so the coupling is visible.
2. **Malformed table cells.** A scripted marker substitution was off by one character and produced `| T || ● |` in 31 `ID-ALLOCATION.md` rows. Caught by inspection immediately after the run and repaired; no malformed cell survives.

Neither reached the final state, but both are recorded — scripted bulk edits over markdown tables are where this kind of damage hides.

## Still open

- Phase 4 as a whole: **not authorised.** 103 items remain allocated-only.
- `STORY-0038`'s dead-code ambiguity and `STORY-0020`'s partial withdrawal are recorded in their own records, not resolved.
