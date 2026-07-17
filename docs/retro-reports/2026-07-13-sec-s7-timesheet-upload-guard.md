# Sprint Retro — `sec-s7-timesheet-upload-guard` — 2026-07-13

## Sprint Summary

**Goal:** Enforce a 10 MB server-side limit on the timesheet-upload endpoint (Track S, item S7), with an advisory frontend pre-check and toast. Doubled as the follow-up ICM sprint-workflow validation pilot (Candidate A, per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md`), chosen specifically to exercise a genuinely `skipped` stage and truly parallel `verification`+`security` stages — the two scenarios `aud-q1-trace-source`'s own retro found unvalidated.

**Verdict — product fix:** PASS. All 4 acceptance criteria met (3 `LIVE`, 1 `CODE REVIEW` — no browser automation available for the frontend click-through, labeled honestly). 0 regressions (308 passed, 1 pre-existing skip). One pre-existing, unrelated Observation flagged (no content-type/malformed-file validation on the same endpoint) — recommended as a new Track S backlog item, not bundled into this sprint.

---

## Sprint Workspace Close Gate (this retro's own precondition)

- **Part A (decision-integrity):** `scripts/lint_sprint_state.py docs/sprints/sec-s7-timesheet-upload-guard` → PASS, 0 defects (10 stages, 3 decisions).
- **Part B (terminal-status):** every stage terminal except `retro` itself (`eligible`, the expected precondition). `architecture` is `skipped` (not `not-applicable`), `arch-council`/`audit` `not-applicable`, `implementation`/`verification`/`security`/`test` `complete`.

---

## Issues Caught Late

None in the product commits. Two process bugs were caught **live, by the lint script itself, during this sprint's own execution** — not after the fact:

1. After marking `implementation` complete (commit `a243998`), `test`'s `waiting_for` still named `implementation` even though it had just become terminal. `scripts/lint_sprint_state.py` flagged this as `E060` before the commit was made; fixed in the same commit. This is exactly the tool doing its job on a real (if small) live sprint, not just its own fixtures.
2. While building the synthetic `rework-loop` fixture, a `cp -r` into an already-existing target directory created a nested `evidence/evidence/` path in two of the three snapshots. Caught by inspection before committing, not by the lint script (the tool doesn't check evidence-path existence, which is by design — see its own documented limitations) — fixed before commit.

| Issue | Stage Caught | Should Have Been Caught By | Skill Updated |
|-------|-------------|---------------------------|---------------|
| `test.waiting_for` stale after `implementation` completed | Self (this session, before commit) | `scripts/lint_sprint_state.py` (worked as intended) | None — the tool already covers this; this is evidence the tool works, not a gap |
| Nested `evidence/evidence/` from `cp -r` into an existing dir | Self (inspection, before commit) | N/A — a shell-usage mistake, not a workflow-mechanics gap | None |

## Skill Updates Made

None this sprint — no skill file was touched. This sprint exercised the mechanisms Changesets 5–8 already built (sprint-workspace persistence in `security`/`auditor`/`tester`, the sprint-close gate in `retro`) rather than adding new ones.

## Standing Rules Added to CLAUDE.md

None. `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` recommends a new Track S backlog item (content-type validation) — a backlog addition, not a standing rule.

## What Went Well (Keep Doing)

1. **The dedicated "both active" commit worked exactly as designed.** `d69233f` shows `verification` and `security` both `active` with zero `evidence:` fields populated; `ff3dd4d` (later) shows both `complete` with independently-populated evidence. This is a clean, git-provable concurrency proof — the specific gap `aud-q1-trace-source`'s retro found in its own `audit`/`test` transitions (squashed into one commit, `eligible`/`active` never separately observed) does not recur here.
2. **The lint script caught a real, live mistake in a real sprint**, not just its own fixtures — the stale `test.waiting_for` after `implementation` completed. This is the tool doing exactly what Changeset 7 built it for.
3. **Scoping the sprint around the actual missing validation scenarios, rather than picking an arbitrary backlog item, produced a real, small, legitimate fix** — SEC-S7 is now closed, and the workflow validation happened as a side effect of real work, not a synthetic exercise wearing a real sprint's clothes.

---

## ICM Workflow-Mechanics Validation — Updated §9 Scoreboard

Combining this sprint with `aud-q1-trace-source`'s prior retro (`docs/retro-reports/2026-07-13-aud-q1-trace-source.md`):

| # | Scenario | Status (after `aud-q1-trace-source`) | Status (after this sprint) | Evidence |
|---|---|---|---|---|
| 1 | Skipped stage | Not validated | **✅ Validated** | `architecture`: `skipped` from the first commit (`58ec4f8`) through close, full `decisions.md` entry (`DEC-sec-s7-timesheet-upload-guard-01`), never re-evaluated as `not-applicable`. |
| 2 | Not-applicable stage | ✅ Validated | ✅ Still validated | `arch-council`/`audit` this sprint, in addition to the 4 stages in `aud-q1-trace-source`. |
| 3 | Two parallel stages | Not validated (fixture only) | **✅ Validated on real data** | `verification`+`security` both `active` in commit `d69233f`, before either had evidence — confirmed by direct `git log`/`git show` inspection, not narration. |
| 4 | Rework loop | Not validated | **Mechanically validated via synthetic fixture only** | `scripts/lint_sprint_state.fixtures/rework-loop/{before-rework,after-rework,after-fix}/` — lint PASS on all three snapshots in sequence. No genuine rework event arose in this sprint's real execution (everything passed cleanly first attempt), so the fixture path (explicitly anticipated by the discovery doc and approved as D-VP-04) was used instead of real product history. **This is the one scenario where the plan's original §9 wording did not explicitly sanction a fixture substitute the way it did for scenario 6** — reported honestly as fixture-only, not rounded up to "validated." |
| 5 | Unresolved dependency → eligible | ✅ Validated | ✅ Re-confirmed | `verification`/`security` both `blocked`→`eligible` in commit `a243998`. |
| 6 | Invalid `decision_ref` caught mechanically | ✅ Validated (fixture, plan-sanctioned) | ✅ Still validated | `bad-decision-ref` fixture (Changeset 7) — plan's own §9 wording explicitly permits a fixture here. |

**Cumulative score: 5 of 6 scenarios validated per the plan's own literal §9 bar** (scenarios 1, 2, 3, 5, 6). **Scenario 4 is mechanically proven but only on synthetic data** — the plan's original wording didn't pre-approve a fixture substitute for it the way it did for scenario 6, though this discovery's own D-VP-04 decision explicitly approved exactly that fallback for this specific effort. Whether that counts as "the pilot's own bar fully met" is a judgment call this report deliberately does not make on the user's behalf — it states the fact (5 real + 1 fixture-only, fixture-substitute pre-approved for this effort) and leaves the verdict open.

**No further validation-pilot work is recommended unless a genuine rework event is specifically desired on real data** — that would require deliberately picking a sprint likely to need correction, which conflicts with this project's own preference for small, low-risk pilots. The synthetic fixture is judged sufficient for this mechanic going forward, consistent with `WORKFLOW.md`'s and `scripts/lint_sprint_state.py`'s own fixture-first precedent (Changeset 7).

## Next Sprint Health Check

- [x] All skill updates committed — none this sprint (n/a)
- [ ] Memory updated — pending, next step after this report
- [x] CLAUDE.md reflects current invariants — no change needed this sprint
- [x] `/arch-council` — not applicable this sprint (confirmed in `state.md`/`decisions.md`)
- [x] **Git commit and push** — all sprint changes committed and pushed to `origin/uat`

## Sign-off

Verified by: Claude Code (automated, `/retro` skill)
