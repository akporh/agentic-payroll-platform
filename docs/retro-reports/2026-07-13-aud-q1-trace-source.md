# Pilot Sprint Retro — `aud-q1-trace-source` — 2026-07-13

## Sprint Summary

**Goal:** Add a `component_source` field to the `fixed_amount` rule's trace entry in `backend/domain/payroll/rule_evaluator.py`, closing ROADMAP Track Q item Q1/AUD-1. This sprint doubled as the pilot workspace for the non-linear ICM sprint-workflow implementation (`docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`).

**Verdict — product fix:** PASS. All 3 acceptance criteria met (`docs/test-reports/2026-07-12-aud-q1-trace-source.md`), AUD-1/Q1 confirmed genuinely closed (`docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`), 0 regressions (306 passed / 1 pre-existing skip across the full suite). Sprint closed.

**Verdict — ICM workflow-mechanics validation:** PARTIAL. See the dedicated section below — 3 of the plan's 6 required test scenarios (§9) were not exercised by this particular pilot, and that gap is real, not a formality to wave through.

---

## Sprint Workspace Close Gate (this retro's own precondition)

- **Part A (decision-integrity):** `scripts/lint_sprint_state.py docs/sprints/aud-q1-trace-source` → PASS, 0 defects (10 stages, 5 decisions checked).
- **Part B (terminal-status):** every stage except `retro` itself is `complete` or `not-applicable` — `roadmap`/`pm`/`implementation`/`audit`/`test` complete; `architecture`/`arch-council`/`verification`/`security` not-applicable. `retro` was `eligible`, the expected precondition for this run. Gate passes; sprint may close.

---

## Issues Caught Late

None for this pilot's product commits (`a8ffc76`, `d9d35b1`) — `git log` shows no fix/revert/correct commit against either. Two real bugs were found and fixed in `scripts/lint_sprint_state.py` (Changeset 7) — see "What Went Well" below for why these don't count as "caught late."

| Issue | Stage Caught | Should Have Been Caught By | Skill Updated |
|-------|-------------|---------------------------|---------------|
| — | — | — | — |

## Skill Updates Made

| Skill | What Was Added |
|-------|---------------|
| `security/SKILL.md` | Sprint-workspace persistence pointer (Changeset 5) |
| `auditor/SKILL.md` | Sprint-workspace persistence pointer (Changeset 5) |
| `tester/SKILL.md` | Sprint-workspace persistence pointer (Changeset 5) |
| `retro/SKILL.md` | Decision-integrity check (Changeset 6) → extended to a full sprint-close gate with a terminal-status hard stop (Changeset 8, this sprint) |

## Standing Rules Added to CLAUDE.md

None this sprint — no project-wide rule change was warranted beyond what the ICM diagnostic plan already scopes to `docs/sprints/STAGE-REGISTRY.md`/`WORKFLOW.md` (repository) and the skill files above (user-home).

## What Went Well (Keep Doing)

1. **Fixture-first validation caught real bugs before they touched production data.** Changeset 7's own required sequence (prove the lint script against synthetic fixtures *before* trusting it against the live pilot) surfaced two genuine parser bugs — a missing block-style-list case (`waiting_for:` under a `- item` list) and a `CURRENT.md` line-filtering bug that broke auto-discovery — both caught and fixed during self-testing, before either bug ever ran against real sprint data. This is exactly what D8's "script-first, prove against fixtures" design was for; it worked as intended.
2. **Decision-log discipline held up under audit.** Changeset 6's live decision-integrity check found zero defects against 5 real decisions spanning 4 stages and 2 sessions — every `decision_ref` resolved, no duplicates, no orphaned or unknown-stage references. The append-only `decisions.md` convention did what it was designed to do.
3. **Keeping unrelated concurrent work out of these commits.** Every changeset in this pilot landed with `git status`/`git diff --stat` checked before staging, so none of the concurrent audit-program remediation's in-flight, uncommitted test-file changes were accidentally swept into these commits.

---

## ICM Workflow-Mechanics Validation — §9 Acceptance Audit

The implementation plan's §9 requires 6 specific scenarios to be exercised, with the explicit rule: **"The pilot is not considered complete until all six scenarios have been exercised."** This is a bar on the *workflow-mechanics validation*, separate from the bar on the *product fix* (which the pilot does meet). Auditing each scenario against this pilot's actual git history (not narrated intent) — verified via `git log --follow -- docs/sprints/aud-q1-trace-source/state.md` and per-commit diffs, not assumption:

| # | Scenario | Result | Evidence |
|---|---|---|---|
| 1 | One **skipped** stage, with a `decisions.md` entry | **NOT EXERCISED** | This pilot has zero `skipped` stages — its 4 conditional stages all resolved `not-applicable` instead. `skipped` vs. `not-applicable` (a real, load-bearing distinction per `WORKFLOW.md`) has never been exercised in a live sprint. |
| 2 | One **not-applicable** stage | **EXERCISED** | 4 stages (`architecture`, `arch-council`, `verification`, `security`), each with `reason`/`decision_owner`/`decision_ref`/`date`, committed across `ed65a30` and `aa3195b`. |
| 3 | **Two parallel stages**, evidence in separate `evidence/<stage>/` subfolders | **NOT EXERCISED** | No stage in this pilot ever declared `may_run_with` against another. `may_run_with` legality was proven mechanically (Changeset 7's `clean` fixture, `verification`/`security` pair), but never against this pilot's own real data — the pilot's `audit` and `test` stages ran sequentially, not concurrently. |
| 4 | One **rework loop** (`complete` → `needs-rework`, dependents auto-revert to `blocked`) | **NOT EXERCISED** | No stage in this pilot was ever reopened. The fix was correct on the first pass; there was no genuine defect to trigger rework. |
| 5 | One **unresolved dependency** (`blocked` → later `eligible`) | **EXERCISED, cleanly** | `retro` itself: `blocked` with `waiting_for: [test]` in `ed65a30`/`aa3195b` → `eligible` in `d9d35b1` once `test` reached `complete`. Verified via per-commit diff, not narration. |
| 6 | One **invalid `decision_ref`**, caught mechanically by the lint script | **EXERCISED (via fixture)** | `scripts/lint_sprint_state.fixtures/bad-decision-ref/` — exercised exactly as the plan itself permits: "a deliberately broken fixture (**not real pilot data**)." Real pilot data has never had an invalid `decision_ref` to catch. |

**Score: 3 of 6 (scenarios 2, 5, 6) genuinely exercised. 3 of 6 (scenarios 1, 3, 4) not exercised by this pilot.**

**Why:** this pilot was deliberately chosen (D1) to be small, bounded, single-file, and low-risk — which is exactly why it never needed a `skipped` stage (nothing was optional-and-declined), never had two stages ready to run concurrently (`audit` and `test` have a strict sequential dependency, not a parallel one), and never produced a genuine defect requiring rework (the fix was correct on the first attempt). These are not failures of execution — they are a structural consequence of picking a *small, low-risk* pilot, which was itself the explicit, approved design goal (D1(b), "exercise workflow mechanics independently of feature complexity"). But it means the workflow-mechanics validation these three scenarios exist to prove has genuinely not happened yet.

**Conclusion:** the **product sprint is complete**. The **ICM sprint-workflow pilot's own §9 acceptance bar is not fully met** — it is honestly PARTIAL, not complete, and should not be reported as fully validated. Closing this sprint does not require re-opening it to force scenarios 1/3/4 artificially (that would be fabricating workflow events for their own sake, which is exactly the kind of behavior `WORKFLOW.md`'s "never silently repair" principle exists to prevent applied to process itself). Instead, either:
- accept this as a documented, permanent limitation of *this* pilot and treat scenarios 1/3/4 as validated only when a future real sprint naturally needs a `skipped` stage, a parallel pair, or a rework loop; or
- deliberately scope a small follow-up validation pilot whose selection criteria specifically require at least one of the missing scenarios (e.g., a sprint with one clearly optional sub-task to `skip`, or two independent fixes that can genuinely run in parallel).

## Next Sprint Health Check

- [x] All skill updates committed (user-home files — no repo commit, by design, per D3)
- [x] Memory updated (`handoff_note.md`)
- [ ] CLAUDE.md reflects current invariants — deferred to Changeset 10 (CLAUDE.md consolidation), not part of this sprint's scope
- [x] `/arch-council` — not applicable this sprint (confirmed `not-applicable` in `state.md`, `decisions.md`)
- [x] **Git commit and push** — pilot workspace changes for this changeset committed and pushed to `origin/uat`

## Sign-off

Verified by: Claude Code (automated, `/retro` skill)
