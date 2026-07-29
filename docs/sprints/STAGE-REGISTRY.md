# Stage Registry

**Static, cross-sprint, reusable.** This is the authoritative source for stage applicability, entry conditions, dependencies, and completion criteria — per D2 (`docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`, approved 2026-07-12). CLAUDE.md's "Automated Delivery Workflow" section keeps the *why*; this registry states the *when*, formally and machine-checkably. No duplicate applicability rules should exist in prose elsewhere — if CLAUDE.md's auto-invoke table and this registry ever appear to disagree, this registry governs, and the discrepancy is a bug to fix here (or in CLAUDE.md, per Changeset 10), not a reason to maintain two versions.

Every entry below is drawn directly from this repository's `CLAUDE.md` (global `~/.claude/CLAUDE.md` Sprint Workflow section, project `CLAUDE.md` Automated Delivery Workflow section) and the corresponding `~/.claude/skills/*/SKILL.md` files. No new rule is invented here.

10 stage IDs, in typical (not enforced-sequential — see `WORKFLOW.md`) order: `roadmap`, `pm`, `architecture`, `arch-council`, `implementation`, `verification`, `security`, `audit`, `test`, `retro`.

---

## `roadmap`

| Field | Value |
|---|---|
| Purpose | Orient on what's done, what's next, what's deferred before any sprint work begins |
| Mandatory status | mandatory |
| Entry conditions | Start of a new sprint session, before the user is asked what to work on |
| Inputs | `docs/ROADMAP.md` |
| Outputs | Orientation summary presented to the user (no dedicated per-sprint file required) |
| Dependencies | None — first stage |
| Parallel compatibility | None |
| Skip conditions | None — always invoked at the start of a new sprint session |
| Completion criteria | Roadmap state presented to the user |
| Human gate | None |

## `pm`

| Field | Value |
|---|---|
| Purpose | Scope stories and write acceptance criteria |
| Mandatory status | mandatory |
| Entry conditions | User says "let's scope sprint," "what's next," or "start sprint" |
| Inputs | `docs/PLAN.md` (forward work) and `docs/ROADMAP.md` (frozen history); existing `docs/stories/` (must be read first, per standing project practice, before generating new stories); `docs/product/ID-ALLOCATION.md` (to find the next free story ID); `docs/product/stories/TEMPLATE.md` (the record schema to write) |
| Outputs | Story text and acceptance criteria (in chat); a reserved `STORY-<nnnn>` per in-scope story recorded in `docs/product/ID-ALLOCATION.md` and in this sprint's `CONTEXT.md` as `story_refs`; **and, per story, a `docs/product/stories/STORY-<nnnn>-<slug>.md` file plus `STORY-REGISTRY.md` row carrying the intent fields** — actor, problem, intended behaviour, acceptance criteria, out of scope, priority, parent IDs, dependencies, source and decision references — at `status: backlog`, `ac_owner: hierarchy`, no delivery evidence (D-031). `CONTEXT.md` links to that record for criteria rather than restating them |
| Dependencies | `roadmap` (complete) |
| Parallel compatibility | None |
| Skip conditions | None |
| Completion criteria | Stories + AC agreed; explicit human confirmation of sprint scope obtained before plan mode; every in-scope story carries an allocated `STORY-<nnnn>` **and a created story record at `status: backlog`**, with `python3 docs/product/validate_registry.py` at PASS (see `WORKFLOW.md` § Product traceability) |
| Human gate | Explicit scope confirmation — required before entering plan mode |

## `architecture`

| Field | Value |
|---|---|
| Purpose | Cross-layer architecture review for structural design decisions, before plan mode |
| Mandatory status | conditional |
| Entry conditions | The sprint plan includes any structural or cross-layer design |
| Inputs | Agreed stories/AC from `pm` |
| Outputs | Design decisions (recorded in the plan / chat) |
| Dependencies | `pm` (complete) |
| Parallel compatibility | None |
| Skip conditions | Sprint plan has no structural or cross-layer design component |
| Completion criteria | Design decisions reached, ready to inform plan mode |
| Human gate | None formal (informal review during planning) |

## `arch-council`

| Field | Value |
|---|---|
| Purpose | Two-stage architectural review (Senior Architect, then Principal Reviewer) before approving any plan with data-contract risk |
| Mandatory status | mandatory when applicable (see entry conditions) — not skippable when the trigger condition holds, only `not-applicable` when it genuinely does not |
| Entry conditions | The plan touches a `status`/`state`/enum field, a DB constraint on a financially-critical table, the meaning of an existing API response field, a destructive migration step, a cross-workspace endpoint, or a shared type/interface/service contract |
| Inputs | Draft plan |
| Outputs | Council verdict (APPROVED / NEEDS REVISION / etc.) |
| Dependencies | `architecture` (complete or not-applicable); draft plan prepared |
| Parallel compatibility | None — gates `ExitPlanMode`, must resolve before implementation starts |
| Skip conditions | Not applicable (not skippable): if none of the entry-condition triggers hold this sprint, mark `not-applicable`, never `skipped` |
| Completion criteria | Verdict reached before `ExitPlanMode` |
| Human gate | Plan approval (`ExitPlanMode`) follows the council verdict |

## `implementation`

| Field | Value |
|---|---|
| Purpose | Execute the approved plan |
| Mandatory status | mandatory |
| Entry conditions | Plan approved via `ExitPlanMode` |
| Inputs | Approved plan |
| Outputs | Code diff; `/simplify` pass applied to all changed files |
| Dependencies | Plan approved; `arch-council` (complete or not-applicable) |
| Parallel compatibility | None with `audit` (must never run concurrently with `audit`) |
| Skip conditions | None — always runs for any code change |
| Completion criteria | Code changes made; `/simplify` quality pass complete |
| Human gate | None formal |

## `verification`

| Field | Value |
|---|---|
| Purpose | Run the app and observe live end-to-end behavior |
| Mandatory status | conditional |
| Entry conditions | The sprint touches both `backend/api/routes/` and any file under `frontend/src/` |
| Inputs | Running app, changed routes/pages |
| Outputs | Live-run findings (chat; may cite `docs/test-reports/` where relevant) |
| Dependencies | `implementation` (complete) |
| Parallel compatibility | `security` |
| Skip conditions | Backend-only or migration-only sprints |
| Completion criteria | Live end-to-end behavior confirmed (a STATIC read of the diff does not satisfy this) |
| Human gate | None formal |

## `security`

| Field | Value |
|---|---|
| Purpose | Review all new/modified API routes |
| Mandatory status | conditional |
| Entry conditions | `backend/api/routes/` added or modified |
| Inputs | New/modified route code |
| Outputs | Security review findings; sometimes `docs/security/YYYY-MM-DD-*.md` |
| Dependencies | `implementation` (complete) |
| Parallel compatibility | `verification` |
| Skip conditions | `not-applicable` if no API route or input-handling surface changed this sprint |
| Completion criteria | Every new/modified route reviewed |
| Human gate | None formal |

## `audit`

| Field | Value |
|---|---|
| Purpose | Verify correctness of calculation/statutory-rule changes |
| Mandatory status | conditional |
| Entry conditions | `sequential_executor.py`, `rule_evaluator.py`, `executor.py`, or a migration under `migrations/versions/` that alters a statutory rule or calculation is touched |
| Inputs | Implementation diff, calculation/statutory logic |
| Outputs | Audit findings, `docs/audit/` |
| Dependencies | `implementation` (complete); `security` (complete or not-applicable) |
| Parallel compatibility | None — must never run concurrently with `implementation` |
| Skip conditions | `not-applicable` if no calculation/statutory code touched this sprint |
| Completion criteria | Audit findings recorded |
| Human gate | None formal |

## `test`

| Field | Value |
|---|---|
| Purpose | Verify the sprint against the acceptance criteria set in `pm` |
| Mandatory status | mandatory |
| Entry conditions | `implementation` complete |
| Inputs | Sprint AC (from `pm`), running app |
| Outputs | `docs/test-reports/YYYY-MM-DD-sprint-N.md`, using the LIVE / STATIC / CODE-REVIEW pass/fail taxonomy |
| Dependencies | `implementation` (complete); `verification`, `security`, `audit` (each complete or not-applicable, as relevant to the sprint) |
| Parallel compatibility | None declared |
| Skip conditions | None — always runs |
| Completion criteria | AC verified pass/fail, documented |
| Human gate | None formal; a FAIL result requires a human decision on rework (see `WORKFLOW.md` rework rules) |

## `retro`

| Field | Value |
|---|---|
| Purpose | Review what was caught late in the sprint; update skill checklists |
| Mandatory status | mandatory |
| Entry conditions | User says "done," "sprint complete," or "close sprint" |
| Inputs | `git log`, `MEMORY.md`, plan file (if it still exists); this sprint's `story_refs`, `state.md` and `evidence/` |
| Outputs | `SKILL.md` edits, memory file updates, occasionally `CLAUDE.md` edits; for every `story_ref`, the **completion** of the record `pm` created — `evidence_refs`, `sprint_refs` and `confidence` set from this sprint's own test/audit/security output, `status` flipped, one line appended to Delivery history, and `SOURCE-INDEX.md` + `FEATURES.md` extended (D-031). `retro` completes these records; it no longer creates them |
| Dependencies | `test` (complete); every other activated stage in this sprint's `state.md` at a terminal status (`complete` / `skipped` / `not-applicable`) — no stage may be left `active` or `blocked` when `retro` runs |
| Parallel compatibility | None |
| Skip conditions | None — always runs at sprint close |
| Completion criteria | Retro findings applied to skill files; `state.md` fully terminal; every `story_ref` **resolved — meaning its record carries this sprint's `evidence_refs`, `sprint_refs` and `confidence`, and a `status` no longer holding the `pm` placeholder `backlog` (or holding it deliberately, per D-011, with that stated in the record). File existence alone is not resolution (D-031)**; `python3 docs/product/validate_registry.py` at PASS (see `WORKFLOW.md` § Product traceability) |
| Human gate | "With user confirmation" (per CLAUDE.md's retro step) |

---

## Not modeled as a registry stage

Per CLAUDE.md's workflow, `/ux-designer`, `/ui-designer`, `/frontend-designer`, and `/simplify` are real, invoked steps — but they are not independent graph stages in this registry. `/ux-designer`/`/ui-designer`/`/frontend-designer` are frontend-track-conditional sub-steps folded into the `architecture`/`implementation` stages' entry/completion conditions where the sprint has a frontend component; `/simplify` is folded into `implementation`'s completion criteria (see above). "Git commit and push," the final workflow step, is the sprint-close action that follows `retro`, not a reviewable stage in its own right.
