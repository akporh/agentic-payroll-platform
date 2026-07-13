# ICM Follow-Up Validation-Pilot — Scope Discovery

**Date:** 2026-07-13
**Status:** DISCOVERY ONLY — no implementation, no new sprint workspace, no CURRENT.md change. Requires human approval before any of the actions this document proposes may begin.
**Predecessor:** `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md` (Changesets 1–8, 10 — all complete). Pilot: `docs/sprints/aud-q1-trace-source/` (closed, `state.md` status `complete`).

---

## 1. Current Validation Baseline

Per `docs/sprints/aud-q1-trace-source/retrospective.md` and `docs/retro-reports/2026-07-13-aud-q1-trace-source.md`, the plan's §9 acceptance test scored 3 of 6:

| # | Scenario | Status | Evidence |
|---|---|---|---|
| 1 | Skipped stage | **Not validated** | No `skipped` stage has ever existed in a real sprint under `docs/sprints/`. |
| 2 | Not-applicable stage | ✅ Validated | 4 stages (`architecture`, `arch-council`, `verification`, `security`) in `aud-q1-trace-source`. |
| 3 | Two parallel stages | **Not validated** | `may_run_with` legality proven only via the synthetic `clean` fixture (Changeset 7) — never against real sprint data. |
| 4 | Rework loop | **Not validated** | No stage has ever been reopened in a real sprint. |
| 5 | Unresolved dependency → eligible | ✅ Validated | `retro` itself: `blocked` (commits `ed65a30`/`aa3195b`) → `eligible` (commit `d9d35b1`). |
| 6 | Invalid `decision_ref` caught mechanically | ✅ Validated (via fixture) | `scripts/lint_sprint_state.fixtures/bad-decision-ref/` — per the plan's own permitted wording ("a deliberately broken fixture, not real pilot data"). |

This document scopes how to close scenarios 1, 3, and 4 without fabricating product history or introducing real defects to manufacture a rework event.

**Read for this discovery:** `docs/ROADMAP.md` (Track Q, Track S, Track UI, Phase 2 Track P), `docs/sprints/WORKFLOW.md`, `docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/aud-q1-trace-source/retrospective.md`, `docs/retro-reports/2026-07-13-aud-q1-trace-source.md`, `docs/security/` findings register, `docs/audit/` findings register.

---

## 2. Candidate Sprint Comparison

| Candidate | Real backlog ref | Touches route? | Touches frontend? | Verdict |
|---|---|---|---|---|
| **A — Timesheet upload file-size guard + companion frontend surfacing** | Track S, item S7 (`docs/ROADMAP.md:387`) | Yes — `backend/api/routes/payroll.py:1684-1688` | Yes — `frontend/src/pages/TimesheetUpload.tsx` (companion, scoped below) | **RECOMMENDED** — only candidate that naturally triggers both `verification` and `security` (registry-declared parallel pair), and carries a genuine minor design question for `architecture` to skip. |
| **B — Q3, simulate-script Decimal fix** | Track Q, item Q3 (`docs/ROADMAP.md:401`) | No | No | Ruled out. Single backend script file, same shape as the `aud-q1-trace-source` pilot — `verification`/`security`/`audit` would all resolve `not-applicable` exactly as before. A real, worthwhile fix, but contributes nothing new to this validation goal. |
| **C — `workspace.py` batch `str(e)` fix (8 violations)** | CLAUDE.md standing prohibition, confirmed live: `grep -c "str(e)" backend/api/routes/workspace.py` → 8 | Yes | No | Ruled out. Route-only, no frontend → `verification` stays `not-applicable`, no parallel pairing possible. Also unsuitable for the skip scenario: `security` is exactly the kind of correctness/safety check this discovery is told not to skip "merely to satisfy validation." |

Two backlog items were checked and found already stale/closed during this discovery, worth flagging to `/roadmap`:
- **S8** (pin `python-multipart`) — `requirements.txt:15` already reads `python-multipart==0.0.28`. Already resolved; ROADMAP still shows it open.
- **Q7** (`approved_by` actor identity) — `docs/ROADMAP.md:920,928` explicitly gates this behind Track P (Authentication/JWT identity, Phase 2) — "closes atomically" with `P5`. Not independently scopeable without contradicting that stated dependency; excluded as a candidate.

---

## 3. Candidate Detail

### Candidate A (recommended) — `sec-s7-timesheet-upload-guard`

- **Proposed sprint ID:** `sec-s7-timesheet-upload-guard`
- **Product scope:** Add a byte-size cap (10 MB, per the existing S7 recommendation) to the timesheet Excel upload endpoint before `openpyxl.load_workbook` parses the full buffer into memory. Companion frontend change: surface the resulting `413` with a specific, human-readable toast (reusing `TimesheetUpload.tsx`'s existing `useToast()`/`extractError()` pattern — no new UI component) instead of falling through to the generic upload-failure message.
- **Source backlog/audit reference:** Track S, item S7 (`docs/ROADMAP.md:387`) — "Add file size cap (10 MB) on timesheet upload — `openpyxl.load_workbook` loads entire file into memory; no current guard." Confirmed still open by reading `backend/api/routes/payroll.py:1684-1688` directly this session (no size check present).
- **Acceptance criteria:**
  1. Uploading a timesheet Excel file larger than 10 MB returns HTTP 413 with a generic, non-leaking message before the workbook is parsed.
  2. Uploading a file at or under 10 MB behaves exactly as today — no change to successful-path behavior.
  3. The frontend surfaces the 413 as a specific toast (e.g., "File too large — max 10 MB"), not the generic upload-failure fallback.
  4. No change to any other upload validation (content-type, sheet structure, row parsing).
- **Files likely to change:** `backend/api/routes/payroll.py` (guard before `await file.read()` / after, before `load_workbook`), `frontend/src/pages/TimesheetUpload.tsx` (catch-block branch for 413), one new focused backend test, one frontend behavior note (no new component per `ds_inputs_in_table_cells`-style DS constraints — this is a toast, not a form control).
- **Expected stage graph:** see §4.
- **Skipped-stage decision:** see §5.
- **Parallel-stage pairing:** `verification` + `security` — see §6.
- **Risks:** Low. Additive guard, no existing behavior changed for valid uploads. The only genuine judgment call is the skip decision itself (§5), which is deliberately conservative (correctness/security stages are never the skip candidate — only `architecture`, the one non-mandatory, no-formal-gate stage in the registry).
- **Estimated complexity:** XS (half day) — smaller than the `aud-q1-trace-source` pilot; the pilot touched one file, this touches two, both additive.
- **Recommendation:** Use this as the real sprint for scenarios 1 (skip) and 3 (parallel).

### Candidate B — Q3 (not recommended for this purpose)

- **Proposed sprint ID:** `aud-q3-simulate-decimal-fix` (if pursued on its own merits, separately from this validation effort)
- **Product scope:** Replace the raw `dict(b)` tax-band mapping in `scripts/simulate_payroll_components.py:508` with explicit `Decimal(str(...))` conversion, matching the production PAYE path.
- **Source backlog/audit reference:** Track Q, item Q3 / AUD-3 (`docs/ROADMAP.md:401`).
- **Acceptance criteria:** simulate script's tax-band values match production `calculate_paye_for_period`'s Decimal handling for at least one boundary-crossing salary.
- **Files likely to change:** `scripts/simulate_payroll_components.py` only.
- **Expected stage graph:** identical shape to `aud-q1-trace-source` — `architecture`/`arch-council`/`verification`/`security` all `not-applicable`, only `audit`(maybe)/`test` genuinely activate.
- **Skipped-stage decision:** none available — nothing here is conditionally applicable-but-deferred; it's cleanly not-applicable across the board.
- **Parallel-stage pairing:** none possible — single file, no route, no frontend.
- **Risks:** None beyond the fix itself. Zero risk of misuse for validation purposes, because it structurally cannot be misused for validation purposes — it just doesn't offer the graph shape needed.
- **Estimated complexity:** XS.
- **Recommendation:** Worth doing eventually as its own small Track Q closure, but explicitly not a candidate for this discovery's goal — including it only for comparison completeness, per the instruction to name real alternatives considered and ruled out.

### Candidate C — `workspace.py` `str(e)` batch fix (not recommended for this purpose)

- **Proposed sprint ID:** `sec-workspace-str-e-batch` (if pursued on its own merits)
- **Product scope:** Fix all 8 `str(e)` leaks in `backend/api/routes/workspace.py` (lines 93, 180, 663, 768, 1452, plus 3 more) per CLAUDE.md's standing API Route Rule.
- **Source backlog/audit reference:** CLAUDE.md "API Route Rules (Standing — Do Not Break)"; memory note `feedback_sprint_...` flags this as a known batch of standing-prohibition violations (referenced in the ICM handoff note's "Next Sprint Candidates" list, item 6).
- **Acceptance criteria:** none of the 8 sites return `str(e)`/`repr(e)` to the client; each logs the raw exception server-side and returns a generic message.
- **Files likely to change:** `backend/api/routes/workspace.py`, 8 focused regression tests (one per fixed site, or grouped by endpoint).
- **Expected stage graph:** `security` genuinely `active` (this is exactly what `/security` exists to catch) — `verification` `not-applicable` (no frontend file touched).
- **Skipped-stage decision:** **Explicitly none proposed.** `security` here is reviewing a real information-disclosure vector on a live route — this is precisely the "mandatory safety or correctness check" this discovery was told not to skip merely to manufacture a scenario.
- **Parallel-stage pairing:** none possible — no frontend change, so no `verification`/`security` pair.
- **Risks:** None to the validation effort (it's simply not usable for it); real risk if shipped is the existing information-disclosure exposure itself, unrelated to this discovery.
- **Estimated complexity:** S (multiple sites, same pattern, still small).
- **Recommendation:** A legitimate, independent backlog item — schedule it as its own sprint whenever convenient, but do not fold it into ICM validation.

---

## 4. Proposed Stage Graph — Candidate A (`sec-s7-timesheet-upload-guard`)

| Stage | Status (once implementation lands) | Rationale |
|---|---|---|
| `roadmap` | complete | Standard orientation step. |
| `pm` | complete | Scope + AC per §3 above, human-confirmed. |
| `architecture` | **`skipped`** | Genuine minor design question exists (see §5) — deliberately deferred, not structurally absent. |
| `arch-council` | not-applicable | No status/enum, DB constraint, API response-field meaning change, destructive migration, cross-workspace endpoint, or shared type/interface/service contract touched — a byte-size guard and a toast branch are neither. |
| `implementation` | complete | The guard + toast branch, plus focused tests. |
| `verification` | **active, `may_run_with: [security]`** | Entry condition holds: touches both `backend/api/routes/` and `frontend/src/`. |
| `security` | **active, `may_run_with: [verification]`** | Entry condition holds: `backend/api/routes/payroll.py` modified. |
| `audit` | not-applicable | Neither `sequential_executor.py`, `rule_evaluator.py`, `executor.py`, nor a calculation-altering migration is touched — this is upload validation, not a calculation path. |
| `test` | complete | Mandatory; AC verification per §3. |
| `retro` | complete | Closes the sprint; this is also where scenarios 1 and 3 get their final confirmation write-up. |

This graph is a **superset** of `aud-q1-trace-source`'s shape (which had zero `active`/`skipped` stages beyond the mandatory ones) — it adds exactly the two missing shapes (`skipped`, two genuinely `active`-together stages) without inventing anything the registry doesn't already support.

---

## 5. Skipped-Stage Decision Design

- **Stage:** `architecture`
- **Why applicable but deliberately skippable (not not-applicable):** the sprint plan does contain a small, real cross-layer question — where should the 10 MB max-upload-size value live? Options considered: (a) a single shared constant imported by both the FastAPI route and the React upload page (requires a shared-config mechanism this codebase does not yet have between `backend/` and `frontend/`), (b) duplicate the literal `10 * 1024 * 1024` in both places with a comment cross-referencing the other, (c) make it a workspace-configurable value (a real feature, out of scope for a bug-fix-sized sprint). This is a genuine, if minor, structural question — `architecture`'s entry condition ("sprint plan includes any structural or cross-layer design") legitimately holds.
- **Distinguishing from not-applicable:** `not-applicable` would mean no such question exists at all (as in `aud-q1-trace-source`, where the trace-field addition had zero design surface). Here the question is real; it is being deferred by explicit human judgment, not ruled structurally absent.
- **Required human decision:** the sprint's product owner/operator (Michael Emedo, consistent with every other `decisions.md` entry in this workstream) explicitly decides option (b) — duplicate the literal constant, with a comment in each location cross-referencing the other — is acceptable for a fix this size, and formally records that decision rather than silently proceeding.
- **Required `decisions.md` entry:**
  ```yaml
  - id: DEC-sec-s7-timesheet-upload-guard-01
    date: <execution date>
    decision_owner: Michael Emedo
    stage: architecture
    decision_type: skip
    reason: >
      A minor cross-layer question exists (where the 10 MB max-upload-size
      constant should live — shared config vs. duplicated literal vs.
      workspace-configurable). Judged too small to warrant a formal
      /architect review for a bug-fix-sized sprint; duplicating the
      literal with a cross-referencing comment is accepted for now.
    reference: <link to the actual sprint's CONTEXT.md / plan>
  ```
- **Compensating control:** the duplicated constant in each file carries an inline comment pointing at its counterpart ("keep in sync with backend/api/routes/payroll.py's MAX_TIMESHEET_UPLOAD_BYTES" and vice versa), and this decision is re-opened (via the existing `skipped` → re-evaluable-later semantics, per `WORKFLOW.md`) the moment a third consumer of this constant appears, or the value needs to become workspace-configurable.

---

## 6. Parallel-Execution Validation Design

- **Stage IDs:** `verification`, `security`.
- **Registry permission:** `docs/sprints/STAGE-REGISTRY.md` — `verification`'s "Parallel compatibility" row reads `` `security` ``; `security`'s row reads `` `verification` ``. Symmetric, explicit, already the only positive (non-"None") pairing in the real registry. Also the only pairing `scripts/lint_sprint_state.py` will accept per its `E050` check.
- **Common dependency that must become terminal first:** both stages declare `depends_on: [implementation]` only. Neither depends on the other. `implementation` must reach `complete` before either becomes `eligible`.
- **Why neither depends on the other:** `verification` is a live end-to-end behavioral check; `security` is a static/code-level review of the same diff. They read the same implementation output independently and produce independent findings — this is exactly the registry's own stated rationale (`STAGE-REGISTRY.md`'s `verification`/`security` rows list each other as their sole parallel-compatible partner, with no ordering implied).
- **Separate evidence outputs (no write collision):**
  - `docs/sprints/sec-s7-timesheet-upload-guard/evidence/verification/` — live-run findings (curl/HTTP transcript for the 413 path + a normal-size upload, screenshot or transcript of the frontend toast).
  - `docs/sprints/sec-s7-timesheet-upload-guard/evidence/security/` — the `/security` review findings for the new guard code (confirms no float used, no unbounded read before the check, generic error message per CLAUDE.md's `str(e)` rule).
  - Existing conventions (`docs/security/YYYY-MM-DD-*.md` if a narrative is produced) remain additionally written per the `security/SKILL.md` sprint-workspace-persistence integration from Changeset 5 — this is additive, not a replacement.
- **Proving concurrent activation from repository history (the specific gap Changeset 8's retro found — audit/test were squashed into one commit, never observed genuinely concurrent):**
  1. Commit `state.md` the moment **both** `verification` and `security` transition from `eligible` to `active` — **before** either stage's actual review work begins. This commit's diff will show both stages' `status: active` simultaneously, with no `evidence:` field yet populated.
  2. Do the live-run (`verification`) and the code review (`security`) as two independent passes in either order — order does not matter, since neither depends on the other.
  3. Commit `state.md` again once **both** reach `complete`, with their respective `evidence:` fields populated.
  4. The git history between these two commits is the durable proof: a single commit exists in which both stages are simultaneously `active`, and both stages' own `evidence:` references were written after that shared commit, not before — meaning neither could have silently completed before the other even started. This directly closes the gap the Changeset 8 retro flagged (`implementation`'s and `audit`'s real transitions were never separately committed) by making the "both active at once" commit boundary an explicit, deliberate step rather than an artifact of batching convenience.

---

## 7. Rework-Loop Fixture Design (synthetic — explicitly not real product history)

**This entire section describes synthetic workflow-mechanics evidence.** No production code is deliberately made defective to produce it. It extends `scripts/lint_sprint_state.fixtures/` (Changeset 7's proven pattern: self-contained `STAGE-REGISTRY.md`, decoupled from the real one) with a fourth fixture, `rework-loop/`, reusing the existing 7-stage fixture registry (`roadmap, pm, implementation, verification, security, audit, test`).

**Two fixture snapshots are proposed, both of which must pass `scripts/lint_sprint_state.py` in isolation** (this is a fixture with two valid *states*, analogous to how `clean/` proves one valid state — here we need to prove two, since rework is a transition):

- `rework-loop/before-rework/` — `implementation` is `complete` (with `evidence: evidence/implementation/attempt-1.md`), `audit` is `complete` (depends on `implementation`), `test` is `blocked` (`depends_on: [implementation, audit]`, but held deliberately `blocked` rather than advanced, to keep the fixture's "before" state simple and focused on the one transition being tested).
- `rework-loop/after-rework/` — same workspace, after the reopening:
  - `implementation`: `needs-rework` (was `complete`).
  - `decisions.md` gains a new entry: `decision_type: rework`, `stage: implementation`, with `reason`/`decision_owner`/`date` — this is the human authorization the reopening requires (per `WORKFLOW.md`: "A `complete` stage may be reopened to `needs-rework` only via a recorded decision in `decisions.md` — never silently").
  - `audit`: reverts to `blocked`, `depends_on: [implementation]`, `waiting_for: [implementation]` — the mechanical consequence `WORKFLOW.md` describes ("every stage whose `depends_on` includes it automatically reverts to `blocked`").
  - A third snapshot, `rework-loop/after-fix/`, shows the resolution: `implementation` back to `complete`, with `evidence: evidence/implementation/attempt-2.md` (per `WORKFLOW.md`'s "a second pass writes to `evidence/<stage>/attempt-2/`; `state.md` records `attempt: 2`"), and `audit` back to `eligible` (its dependency is terminal again).

**Required lint passes (per the instruction: "lint_sprint_state.py passes before and after the valid transitions"):**
1. `python scripts/lint_sprint_state.py scripts/lint_sprint_state.fixtures/rework-loop/before-rework` → PASS.
2. `python scripts/lint_sprint_state.py scripts/lint_sprint_state.fixtures/rework-loop/after-rework` → PASS (confirms `needs-rework` is a legal status, the `rework` decision resolves, `audit`'s `blocked`+`waiting_for: [implementation]` is legitimate since `implementation` is genuinely non-terminal again).
3. `python scripts/lint_sprint_state.py scripts/lint_sprint_state.fixtures/rework-loop/after-fix` → PASS (confirms `implementation` `complete` with `attempt: 2` evidence, `audit` `eligible` again).

**Why a fixture, not the real sprint:** per the instruction's own preference ("prefer a dedicated synthetic workspace... unless a genuine rework event arises naturally during the real product sprint"). Candidate A (§3) is deliberately small and low-risk — exactly the property that makes it unlikely to need genuine rework. If `/tester` or `/auditor` finds a real defect in Candidate A during its actual execution, that becomes the real rework event instead, and this fixture is not needed for scenario 4 (though it remains valuable as a permanent lint-fixture regardless, extending Changeset 7's coverage). This is decided at execution time, not now — this document proposes the fixture as the default path, not a forced one.

**Labeling requirement (per instruction):** every file under `rework-loop/` will carry the same fixture disclaimer used in the existing three (`clean/CONTEXT.md`, `bad-decision-ref/CONTEXT.md`, `illegal-parallel/CONTEXT.md`): *"Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py` [behavior]. Not a real sprint."* No claim of real product history will appear anywhere in this fixture.

---

## 8. Evidence and Commit Strategy

| Event | Commit boundary |
|---|---|
| Candidate A: `pm` scoping + `CONTEXT.md`/`state.md`/`decisions.md` creation | One commit, mirrors `aud-q1-trace-source`'s Changeset 2 pattern. |
| Candidate A: `architecture` skip decision recorded | Same commit as workspace creation, or its own — either is fine, but must land **before** implementation starts (the decision gates nothing structurally, but recording it late would look like a post-hoc rationalization). |
| Candidate A: `verification` + `security` both `eligible` → `active` | **Its own commit**, per §6 — this is the load-bearing commit that proves concurrent activation. Must not be batched with `implementation`'s own completion commit (the mistake flagged in the Changeset 8 retro). |
| Candidate A: `verification` + `security` both `active` → `complete` | Its own commit, evidence files included. |
| Candidate A: `test`, `retro`, sprint close | Follows the same pattern as `aud-q1-trace-source`'s Changeset 8. |
| Rework fixture: `scripts/lint_sprint_state.fixtures/rework-loop/{before-rework,after-rework,after-fix}/` | One commit, all three snapshots together (they are one proof, like Changeset 7's three original fixtures) — clearly labeled synthetic in every `CONTEXT.md`. |

All commits follow the discipline already established across Changesets 5–8: check `git status`/`git diff --stat` before staging, never sweep in concurrent unrelated work, fetch before push, merge cleanly if the remote has moved.

---

## 9. Acceptance Criteria (for the follow-up validation effort as a whole)

1. Candidate A's product fix (S7 file-size guard + frontend toast) ships with 0 regressions, per the same test-taxonomy discipline as `aud-q1-trace-source`.
2. `architecture` is recorded `skipped` (not `not-applicable`) with a complete `decisions.md` entry (`reason`, `decision_owner`, `decision_ref`, `date`) and a stated compensating control.
3. `verification` and `security` are both observed `active` within a single git-committed `state.md` snapshot, each with independently-populated `evidence:` paths, and `scripts/lint_sprint_state.py` accepts the `may_run_with` pairing without an `E050`.
4. The rework-loop fixture (or a genuine real rework event, if one arises) demonstrates: `complete` → `needs-rework` via a recorded decision, dependent stage reverting to `blocked` with a correct `waiting_for`, a second-attempt evidence write, and return to `complete` → dependent stage `eligible` again — with `scripts/lint_sprint_state.py` PASS on every valid snapshot in the sequence.
5. `docs/retro-reports/<date>-sec-s7-timesheet-upload-guard.md` scores all 6 of the plan's §9 scenarios and states plainly whether the ICM sprint-workflow pilot's own acceptance bar is now fully met — no rounding up, consistent with the `aud-q1-trace-source` retro's own standard.

---

## 10. Human Decisions Required Before Execution

1. **Approve Candidate A** as the real sprint (or select an alternative not surfaced by this discovery).
2. **Approve the `architecture` skip decision's substance** in §5 — specifically, that duplicating the max-upload-size literal (option b) is an acceptable resolution for a fix this size, since this is the actual engineering call this changeset's `decisions.md` entry will formally record, not a rubber-stamp.
3. **Approve the rework-loop fixture as the default path** for scenario 4 (§7), with the explicit understanding that a genuine defect found during Candidate A's real execution would supersede it.
4. **Confirm sprint ID** `sec-s7-timesheet-upload-guard` (or provide an alternative naming preference — `aud-q1-trace-source` set the `<area>-<item>-<short-description>` convention this follows).
5. **Confirm this document does not itself count as any scenario being validated** — per the instruction, no claim of validation is made anywhere above; §9's acceptance criteria describe what execution must still prove.

No file under `docs/sprints/` has been created or modified by this discovery. `docs/sprints/CURRENT.md` is unchanged. `docs/sprints/aud-q1-trace-source/` is unchanged. No user-home skill file has been modified. No production code has been modified.
