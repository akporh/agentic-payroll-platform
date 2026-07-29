# Critic Review — Phase 4C (`CAP-6` Execution Engine batch)

**Programme:** `product-traceability` · **Run:** `historical-migration-cap6-run-001` · **Date:** 2026-07-28
**Reviewer:** independent critic pass, read-only · **Authorising decisions:** D-025, D-026

## Verdict

**PASS** — with three non-blocking observations.

---

## 1. Is the batch complete and correctly bounded?

**Confirmed**, reproduced independently:

| Assertion | Method | Result |
|---|---|---|
| Story files = registry rows | file count vs row count | 54 = 54 |
| Migrated markers reconcile | `ID-ALLOCATION.md` ● count | 54 |
| `CAP-6` composition | confidence tally over `FEAT-18`–`FEAT-25` rows | 14 confirmed · 13 strongly inferred · 5 tentative · 1 requires-human-classification = **33** |
| `FEATURES.md` totals | column sums | 54 migrated / 157 allocated |
| Validator | `validate_registry.py` | **PASS**, 112 rows |

The batch is exactly `CAP-6` — no item from another capability was swept in, and no `CAP-6` item was left behind. `FEAT-18` through `FEAT-25` all read `n/n`.

## 2. Was confidence carried verbatim, or quietly upgraded?

**Carried verbatim.** This was the batch's principal integrity risk, since D-025 deliberately abandoned the confirmed-only rule.

Spot-checked against the discovery inventory: `STORY-0004`, `0005`, `0006`, `0007` (Sprint 0) and `STORY-0038` (PH-3) are all still `tentative` in both the registry row and the story file. `STORY-0151` is `backlog` / `requires human classification` and its record says **"Not delivered"** in the Delivered behaviour section rather than describing a capability.

The five thin-evidence Sprint 0 items each carry an identical, explicit gap statement naming *why* they are tentative — pre-sprint tracking, no dedicated test report — and instructing that they not be cited as evidence of verified behaviour. That is the correct use of the confidence field: it records what is known, and says so.

## 3. Are the records substantive, or restated allocation rows?

**Substantive.** Sampled six at random and traced each claim to source:

- `STORY-0156` reproduces the actual defect from `docs/sprints/dev-levy-rule-pct/plan.md` — 184 employees, ₦100 each, run `e3bd910a`, handler present at priority 430 but never firing. It also records the DEC-04 design decision (dual OR'd triggers) *as a decision*, pre-empting a future reader mistaking the December/January double-charge for a bug.
- `STORY-0086` carries the sequencing detail that makes the story comprehensible — hire proration ran *before* `apply_payroll_rules`, corrupting the rate base for absence deductions — rather than the summary "configurable proration".
- `STORY-0135` names both call sites and records that the retry-service copy had *neither* the date cap nor `DISTINCT ON`, making rule selection non-deterministic.
- `STORY-0067` records that its own fix **opened** audit observation AUD-1/Q1, later closed by `STORY-0145`. That cross-link is real and correct.

Dependencies, decision references and delivery history are populated per record, not boilerplate.

## 4. Was the D-026 capture handled correctly?

**Yes**, and the cause is correctly diagnosed as different from the previous two captures. Sprint 25 and PAY-TAX-1 were missed by the area-based sweep; `dev-levy-rule-pct` was missed by **date** — the discovery pass ran 2026-07-15, the sprint closed 2026-07-16.

Evidence was verified before classification, per `POLICY.md`: the sprint workspace, test report (327 passed / 1 skip / 0 failed, 8 LIVE checks) and audit review all exist on disk. `confirmed` is justified.

Allocation is **forward** (`STORY-0156`/`0157`), not chronological — correct under D-019 rule 2, with rule 3 now binding absolutely. Re-seeding would have been a violation.

## 5. Was write scope honoured?

**Confirmed.** `git status --short` over `docs/stories/`, `docs/ROADMAP.md`, `backend/`, `frontend/`, `migrations/` returns **empty**. All changes fall inside the two D-025 allowed paths.

Note that this batch had more temptation than most: several records cite `docs/ROADMAP.md` line-level detail and `docs/sprints/dev-levy-rule-pct/` content. Both were read, neither was modified.

## 6. Do the records over-claim?

**No** — and in three places they actively under-claim where the evidence warrants it, which is the harder discipline:

- `STORY-0020` records that full-run retry is described as delivered but `FULL_RUN` was **later disabled by migration** — so the capability is partly withdrawn, and the withdrawing change is not itself inventoried. A record that simply said "delivered" would have been misleading.
- `STORY-0022` records that finding F-07-01 of the architecture-review programme identifies this story's own route (`get_run_timeline`) as having decorative rather than enforced workspace scoping — a live security finding against work recorded as delivered.
- `STORY-0038` refuses to resolve the `classify_day` dead-code ambiguity and states plainly that a function existing without a call site is a different delivery state from "done".

---

## Observations (non-blocking)

**O-1 — Two mechanical defects occurred mid-run and are disclosed.** A stale column index in the validator (a Phase 3B carry-over) and an off-by-one in a scripted table-cell substitution that malformed 31 rows. Both were caught and repaired before the final state; the run record discloses both rather than presenting a clean narrative. The pattern worth carrying forward: scripted bulk edits over markdown tables need a structural check after the edit, not just before.

**O-2 — Ten `CAP-6` records have no dedicated evidence file.** `SOURCE-INDEX.md` lists them explicitly rather than leaving the absence to be inferred. Their source is `docs/ROADMAP.md` alone. This is honest, but it means roughly a third of the Execution Engine's record rests on a single source — worth knowing before this capability's traceability is relied on for an external audit.

**O-3 — The recurring key-mismatch defect class is recorded but not addressed.** `STORY-0023` and `STORY-0034` (FIX-2/FIX-3) are the same failure — a statutory component silently resolving to ₦0 because of a key mismatch — occurring in different code paths a sprint apart. `STORY-0023`'s record raises the question of whether a structural guard exists and states that it is not established. That is the correct disposition for a traceability record, but the underlying question is a real engineering one and has no owner. It is not this programme's to resolve.

---

## Conclusion

Phase 4C's authorised scope is complete and correctly bounded. Confidence integrity held under a batch rule that permitted weakly-evidenced items — the harder test, and the one that mattered here.

**Coverage: 54 of 157 (34%).** `CAP-6` Execution Engine is complete at 33/33, from zero.

**Phase 4 as a whole remains unauthorised.** 103 items hold reserved identifiers and feature assignments and nothing more; this batch's completion grants nothing further.
