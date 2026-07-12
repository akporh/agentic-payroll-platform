# Non-Linear ICM Sprint Workflow — Implementation Plan

**Date:** 2026-07-12
**Status:** PROPOSAL — no implementation has occurred. Nothing below has been created, and no existing file has been changed, as a result of this document.
**Scope:** Introduces `docs/sprints/` as repository-based state for the sprint workflow, per the non-linear target model approved in `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md` (Sections 7–8, revised 2026-07-11 per `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md`).
**Inputs read:** the two diagnostic documents above; `~/.claude/CLAUDE.md`, `.../2.OnAiR/CLAUDE.md`, `.../Sandy/CLAUDE.md`, this repo's `CLAUDE.md`; `~/.claude/skills/{roadmap,pm,architect,arch-council,security,auditor,tester,retro}/SKILL.md`; `~/.claude/settings.json` hooks; `~/.claude/agents/{senior-architect,principal-reviewer}.md`; `docs/audit-program/{WORKFLOW.md,audit-state.md}` and `docs/agentic-architecture-review/{WORKFLOW.md,review-state.md}` as the working precedent; the project auto-memory index and the stale committed `.claude/memory/` folder.

---

## 1. Executive summary

This plan introduces four static files (`docs/sprints/CURRENT.md`, `WORKFLOW.md`, `STAGE-REGISTRY.md`, and a shared linting convention) plus a per-sprint workspace, piloted on exactly one upcoming sprint rather than backfilled across sprint history. It does **not** touch the reusable skill files, the hooks, or CLAUDE.md's substantive rules — those stay exactly where they are; the new files formalize *when* those rules apply and *what happened* each time they were checked, which is the gap the diagnostic identified (G1–G3, G9).

The plan is deliberately front-loaded on the parts that are cheap to get wrong and expensive to unwind: the stage-registry vocabulary (what counts as a stage, what its legal statuses are) and the decision-recording convention (how a skip/rework/parallel call becomes a durable, lintable fact) are fixed in Changesets 1–2, before a single real sprint runs through them. Everything after that is additive — a sprint that doesn't need `architecture.md` never gets one, and no historical sprint is retrofitted.

The riskiest open question is not technical, it's behavioral: whether `state.md` and `decisions.md` actually get written *during* a live sprint, under time pressure, rather than reconstructed afterward from memory (the same failure mode that produced G1–G3 in the first place). Changeset 7 (mechanical linting) exists specifically to make that failure visible immediately rather than discovered three sprints later — this is treated as the load-bearing changeset, not a nice-to-have.

---

## 2. Assumptions

- The existing SKILL.md files, hooks, and CLAUDE.md hierarchy are correct and are **not** being redesigned here — this plan only adds the missing state layer around them.
- Exactly one sprint pilots the new structure. No historical sprint (1 through the current in-flight work) is backfilted into `docs/sprints/`.
- "Fresh-session resumability" means: a new Casper session, given only repository access (no chat history, no auto-memory), can answer every question in the diagnostic's §5 reconstruction test for the pilot sprint.
- `docs/audit-program/` and `docs/agentic-architecture-review/` remain independent workspaces with their own `WORKFLOW.md` — this plan does not merge them with `docs/sprints/`, only reuses their proven conventions (named stage status, `_core/human-decisions.md`-style append-only decision log, evidence-cites-findings discipline).
- No CI system currently runs in this repository (not confirmed — flagged as Decision D8). Linting is planned as a local script + hook first; CI is out of scope unless D8 resolves that way.
- The two prior diagnostic documents (`2026-07-11-sprint-workflow-icm-diagnostic.md` and its revision prompt) are treated as already-approved direction for the *target model*. This plan does not re-litigate that model — it plans the build only.

---

## 3. Decisions requiring human approval

| Decision ID | Decision required | Options | Recommendation | Consequence of deferral |
|---|---|---|---|---|
| D1 | Pilot sprint ID and scope | (a) the next scoped product sprint on the ROADMAP, whatever it turns out to be; (b) a deliberately small, low-risk sprint chosen specifically to exercise the new mechanics (e.g. a single-file bugfix) | **(b)** — a deliberately small pilot isolates workflow-mechanics failures from feature-scope failures; if the pilot sprint is itself large or contested, a stall in `docs/sprints/` gets blamed on the feature, not the mechanism | Without a chosen pilot, Changesets 2 and 8 cannot start; the static changesets (1, 3, 6, 7) can still land, but nothing exercises them |
| D2 | Authoritative source for stage applicability rules | (a) `STAGE-REGISTRY.md` becomes authoritative and CLAUDE.md's auto-invoke table is trimmed to a pointer; (b) CLAUDE.md's auto-invoke table stays authoritative in prose and the registry restates it in structured form (duplication) | **(a)** — matches the diagnostic's G5 finding (duplication between global and project CLAUDE.md already caused drift); one authoritative source per rule | If deferred, the registry is built as a restatement (option b) and silently drifts from CLAUDE.md on the next unrelated edit — same failure mode as G5, one level down |
| D3 | Whether `senior-architect.md` / `principal-reviewer.md` personas must be copied into the repo | (a) copy into `docs/sprints/_personas/` so verdicts are reproducible by another operator or a future session without `~/.claude` access; (b) leave in `~/.claude/agents/`, accept that arch-council is operator-machine-specific | **(b)** for this pilot — copying now is scope creep against "keep the solution minimal"; revisit only if a second operator or a cloud/remote agent needs to run `/arch-council` | If left in `~/.claude/agents/`, a cloud-executed sprint (e.g. via a scheduled routine) cannot run `/arch-council` at all — acceptable for now since no such routine exists yet, but must be re-decided before one is created |
| D4 | Whether global or project `CLAUDE.md` files are changed | (a) no changes — `docs/sprints/` is additive only; (b) trim the project CLAUDE.md's restated 17-step sequence to a pointer at the global one (closes G5) | **(b), but as its own tiny changeset (10), not bundled** — it's a real fix but touches a file every session loads, so it deserves isolated review | If deferred, G5's duplication risk remains unaddressed; no functional blocker to the pilot |
| D5 | Whether user-home plan files (`~/.claude/plans/*.md`) are copied or moved into `docs/sprints/<id>/plan.md` | (a) copied (original stays in `~/.claude/plans/` as harness state, repo gets a durable copy at ExitPlanMode); (b) moved (original deleted after copy) | **(a) copy, never move** — the harness's own plan-mode UI may still reference the original path; copying is strictly additive and reversible | If deferred, plans keep living only in `~/.claude/plans/`, and G2 (the diagnostic's highest-severity gap) stays open |
| D6 | Whether the stale committed `.claude/memory/` folder is deleted or archived | (a) delete outright (1 file, frozen at Sprint 13, superseded); (b) rename to `.claude/memory-archived-2026-07/` and keep for history | **(b)** — costs nothing, removes the name-collision risk (G4) immediately, and preserves the one historical file in case Sprint 13's arch decisions are referenced later | If deferred, the collision risk (a tool or session that globs `.claude/memory/` gets a Sprint-13 snapshot presented as current) persists indefinitely |
| D7 | Which commands must write mandatory artefacts (vs. best-effort) | (a) mandatory: `/arch-council` writes `decisions.md` + `architecture.md`; `/tester` writes `state.md` evidence entries (already does via `docs/test-reports/`, now also updates `state.md`); all others best-effort initially; (b) mandatory for all nine commands from day one | **(a)** — matches the diagnostic's own finding that `/tester` is already the most disciplined stage; extend mandatory-writing outward from the one place it already works, rather than mandating it everywhere at once | If deferred to (b) without a pilot, the least-mature commands (e.g. `/pm`, which currently has no dedicated output file at all) are the most likely to silently fail the mandate |
| D8 | Whether workflow-state linting runs as a hook, script, or CI check | (a) a `~/.claude/settings.json` PostToolUse hook, matching the existing migration-ID-duplicate check pattern; (b) a standalone script run manually before `/retro`; (c) CI (not currently configured in this repo) | **(b) for the pilot, promote to (a) once the check is proven** — a hook that misfires during the pilot is harder to debug and disable than a script; graduate to a hook only after the script has run clean on at least one full sprint | If deferred entirely (no lint), `decision_ref` orphans (a reason with no matching decision entry) are only caught by manual review, undermining Changeset 7's purpose |
| D9 | Whether more than one active sprint is supported in the first implementation | (a) single active sprint only — `CURRENT.md`'s `active_sprints` list has exactly one entry, enforced informally; (b) multiple concurrent sprints from day one | **(a)** — this repository's actual delivery pattern (per `docs/ROADMAP.md`) is one sprint at a time; building for concurrency now is speculative generality against "keep the solution minimal" | If (b) is chosen anyway, `evidence/` isolation and `state.md` schema need an extra `sprint_id` disambiguation field from the start — cheap now, expensive to retrofit, so this decision should be made explicitly even though (a) is recommended |

---

## 4. Exact target file inventory

### 4.1 New files — static, cross-sprint (created once, in Changeset 1)

| Path | Purpose |
|---|---|
| `docs/sprints/CURRENT.md` | Names the active sprint workspace(s) — nothing else. Per D9, exactly one entry under `active_sprints` for this implementation. |
| `docs/sprints/WORKFLOW.md` | Static transition/parallel/skip/rework rules — modeled on `docs/audit-program/WORKFLOW.md`'s stage-lifecycle section. |
| `docs/sprints/STAGE-REGISTRY.md` | One row per stage (`roadmap`, `pm`, `architecture`, `arch-council`, `implementation`, `verification`, `security`, `audit`, `test`, `retro`) — purpose, mandatory status, entry conditions, inputs, outputs, dependencies, parallel compatibility, skip conditions, completion criteria, human gate. Per D2, this becomes the authoritative source; CLAUDE.md's auto-invoke table is trimmed to point here (Changeset 10). |
| `docs/sprints/README.md` | One paragraph: what this folder is, links to the two diagnostic documents as design rationale, and to `docs/audit-program/` / `docs/agentic-architecture-review/` as the precedent this reuses. Prevents a fresh session from needing to rediscover the "why" from chat history. |

### 4.2 New files — per-sprint (created in Changeset 2, for the pilot sprint only)

| Path | Purpose | Mandatory or conditional? |
|---|---|---|
| `docs/sprints/<pilot-sprint-id>/CONTEXT.md` | Goal, in-scope stories, out-of-scope, acceptance criteria | Mandatory — created the moment `/pm` produces stories for the pilot |
| `docs/sprints/<pilot-sprint-id>/state.md` | Authoritative per-stage status (§7.2 of the diagnostic) | Mandatory |
| `docs/sprints/<pilot-sprint-id>/decisions.md` | Append-only HITL decision log | Mandatory |
| `docs/sprints/<pilot-sprint-id>/evidence/` | Raw artefacts, one subfolder per stage | Mandatory folder, contents conditional |
| `docs/sprints/<pilot-sprint-id>/plan.md` | Copy of the approved plan from `~/.claude/plans/` | Conditional — only if plan mode ran (per D5, always if it did) |
| `docs/sprints/<pilot-sprint-id>/architecture.md` | Arch-council Council Summary verdict | Conditional — only if `/architect` or `/arch-council` ran |
| `docs/sprints/<pilot-sprint-id>/verification.md` | `/verify` findings | Conditional |
| `docs/sprints/<pilot-sprint-id>/audit.md` | `/auditor` findings (in addition to, not instead of, `docs/audit/`) | Conditional |
| `docs/sprints/<pilot-sprint-id>/retrospective.md` | Pointer to the sprint's entry in `docs/retro-reports/` — not a duplicate | Mandatory (thin — see Changeset 8) |

### 4.3 Existing files/sources that must change

| Path | Change | Changeset |
|---|---|---|
| `~/.claude/skills/roadmap/SKILL.md` | Add one step: after presenting the roadmap, read `docs/sprints/CURRENT.md` and report the active sprint/stage-set alongside the backlog view | 3 |
| `~/.claude/skills/pm/SKILL.md` | Add: on story approval for the pilot sprint, create `docs/sprints/<id>/CONTEXT.md` from the agreed stories/AC | 3 |
| `~/.claude/skills/architect/SKILL.md` | No content change — the 15 retro addenda stay; only a pointer added: "if a sprint workspace exists under `docs/sprints/`, log decisions there per `STAGE-REGISTRY.md`" | 3 |
| `~/.claude/skills/arch-council/SKILL.md` | Step 4 ("Synthesise and Present") gains a mandatory final step: write the Council Summary to `docs/sprints/<id>/architecture.md` and append a `decisions.md` entry with the verdict | 4 |
| `~/.claude/skills/security/SKILL.md`, `auditor/SKILL.md`, `tester/SKILL.md` | Each gains one line: "if `docs/sprints/<id>/` exists, also update `state.md` for this stage and write findings to the corresponding `<stage>.md`" — existing `docs/security/`, `docs/audit/`, `docs/test-reports/` outputs are unchanged, this is additive | 5 |
| `~/.claude/skills/retro/SKILL.md` | Add: check every `state.md` entry for stages not yet `complete`/`skipped`/`not-applicable`; flag before allowing sprint close | 8 |
| `~/.claude/settings.json` | New PostToolUse hook (Edit/Write on `docs/sprints/*/state.md` or `decisions.md`) running the lint script from Changeset 7 — **only added after D8 resolves in favor of a hook**; until then, no settings.json change | 7 (conditional on D8) |
| `.../agentic-payroll-platform/CLAUDE.md` | Trim "Automated Delivery Workflow" section to reference the global sequence + point to `docs/sprints/STAGE-REGISTRY.md` for entry conditions, per D2/D4 | 10 |
| `.claude/memory/` (stale committed folder) | Rename or delete per D6 | 10 |

### 4.4 Explicitly not created

- No per-stage `CONTEXT.md` files inside `docs/sprints/<id>/` beyond the single sprint-level `CONTEXT.md` — the target model's stage-level detail lives in `STAGE-REGISTRY.md` (shared) plus `state.md` (per-sprint instance), not in per-stage folders. This repo's sprint workflow is not being restructured into 13 numbered stage folders like `docs/audit-program/` — that pattern fits a single long-running investigation; the sprint workflow runs many short sprints, so per-sprint (not per-stage) folders are the right grain.
- No workflow engine, no CI pipeline (unless D8 resolves to CI), no new slash commands.

---

## 5. Ordered changesets

| # | Changeset | Purpose | Files created | Files updated | Behaviour introduced | Dependencies | Validation | Rollback | Risk |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Shared static workflow definitions** | Establish the shared vocabulary before any sprint uses it | `docs/sprints/CURRENT.md`, `WORKFLOW.md`, `STAGE-REGISTRY.md`, `README.md` | — | None yet — these are reference documents, no command reads them until Changeset 3 | D2 (registry vs. CLAUDE.md authority) | Manual read-through by the user; confirm `STAGE-REGISTRY.md`'s 10 stages match `CLAUDE.md`'s auto-invoke table with no contradictions | Delete the four files — nothing else references them yet | Low |
| 2 | **Pilot sprint workspace creation** | Stand up one sprint's folder to prove the shape | `docs/sprints/<pilot-id>/CONTEXT.md`, `state.md` (all stages `not-started`), `decisions.md` (empty), `evidence/` | `docs/sprints/CURRENT.md` (add the pilot to `active_sprints`) | A sprint now has a physical home before any stage runs | 1, D1 (pilot chosen) | Confirm `state.md` validates against the schema in §7.2 of the diagnostic (manual check for the pilot; automated from Changeset 7 onward) | Remove the sprint folder, revert `CURRENT.md`'s `active_sprints` entry | Low |
| 3 | **Command and skill integration — roadmap/pm/architect** | Wire the first three stages to read/write the new structure | — | `roadmap/SKILL.md`, `pm/SKILL.md`, `architect/SKILL.md` (pointer only) | `/roadmap` now also reports active sprint/stage-set; `/pm` creates `CONTEXT.md` on story approval | 1, 2 | Run `/roadmap` and `/pm` live against the pilot sprint; confirm `CONTEXT.md` is created with the agreed AC and `/roadmap`'s output includes the pilot | Revert the three SKILL.md files to their pre-changeset version (git revert of this changeset's commit) | Low — additive instructions, no removed behaviour |
| 4 | **Plan and architecture verdict persistence** | Close G2 and G3 — the two highest-severity gaps from the original diagnostic | — | `arch-council/SKILL.md`; ExitPlanMode handling (documented convention, not a harness change — Claude copies the plan manually per the new instruction) | Approved plans and arch-council verdicts become durable, repo-visible files instead of chat-only or `~/.claude/plans/`-only | 1, 2, D3, D5 | Run a real `/arch-council` pass on the pilot; confirm `architecture.md` and a `decisions.md` entry are both written before the skill reports its verdict to chat | Revert `arch-council/SKILL.md`; delete any `architecture.md`/`plan.md` written during the pilot if the sprint is abandoned | Medium — this changeset modifies a mandatory gate's behaviour; a bug here could block `/arch-council` from completing |
| 5 | **Verification, audit and evidence persistence** | Extend the same discipline to `/verify`, `/security`, `/auditor`, `/tester` | — | `security/SKILL.md`, `auditor/SKILL.md`, `tester/SKILL.md` | Each writes to both its existing output location (`docs/security/`, `docs/audit/`, `docs/test-reports/`) and updates the pilot's `state.md` + writes to the corresponding conditional file | 1, 2, D7 | Run each skill live against the pilot; confirm existing outputs are unaffected (regression check) and the new `state.md` entries appear correctly | Revert the three SKILL.md files individually — each is independent, so partial rollback is safe | Low — purely additive to skills with an already-strong output habit (tester) or moderate habit (security, auditor) |
| 6 | **HITL decision recording** | Make `decisions.md` the single place every skip/not-applicable/rework/parallel-allow decision is logged | — | `retro/SKILL.md` (adds a decisions.md completeness check); no other skill changes beyond what Changesets 3–5 already added | Every human decision made during the pilot has an `id`, `date`, `decision_owner`, `stage`, `decision_type`, `reason`, `reference` — see diagnostic §7.7 schema | 2, 4, 5 | Manually audit the pilot's `decisions.md` at sprint close: does every `decision_ref` cited in `state.md` resolve to an entry here? (This becomes automatic in Changeset 7.) | No file removal needed — this changeset is process discipline, not new files | Low |
| 7 | **Mechanical validation / linting** | The load-bearing changeset — makes broken state visible immediately instead of discovered late | `scripts/lint_sprint_state.py` (or `.sh`) | `~/.claude/settings.json` **only if D8 resolves to (a) hook** | A script that: (a) parses every `state.md` under `docs/sprints/`, (b) confirms every `decision_ref` resolves to a `decisions.md` entry, (c) confirms every `depends_on`/`may_run_with` pairing is legal per `STAGE-REGISTRY.md`, (d) flags orphaned `skipped`/`not-applicable` entries missing a reason | 1, 2, 6, D8 | Run the script against the pilot's deliberately-seeded test scenarios (§9 below — one bad `decision_ref`, one illegal parallel pairing) and confirm it catches both | Delete the script; remove the hook entry from `settings.json` if added | Medium — a false-positive lint that blocks legitimate work is worse than no lint; must be validated against real bad input before being trusted, hence script-first (D8) rather than hook-first |
| 8 | **Pilot execution and retrospective** | Run one real sprint end-to-end through the new structure and close the loop | `docs/sprints/<pilot-id>/retrospective.md` (thin pointer) | `retro/SKILL.md` (state-completeness gate) | The pilot sprint closes; `/retro` explicitly checks `docs/sprints/<pilot-id>/state.md` for any stage not in a terminal status (`complete`/`skipped`/`not-applicable`) before allowing sprint close | 1–7 | The full §9 acceptance-criteria pass, executed against the real pilot, not a synthetic example | If the pilot fails badly enough to abandon: the sprint folder can be deleted and `CURRENT.md` reverted; the static files (Changeset 1) and skill changes (3–6) are kept regardless, since they're now proven independent of any one sprint's outcome | Medium — first real-world exercise of everything above; risk is schedule/process, not code |
| 9 | *(reserved — not used; retained to keep numbering stable if a changeset is later split)* | — | — | — | — | — | — | — |
| 10 | **CLAUDE.md consolidation and memory cleanup** (optional, per D4/D6) | Close G4 and G5 from the original diagnostic | — | `.../agentic-payroll-platform/CLAUDE.md`; `.claude/memory/` renamed or deleted | Project CLAUDE.md's "Automated Delivery Workflow" section becomes a pointer to the global sequence + `STAGE-REGISTRY.md`; the stale memory folder no longer collides with the real store | None — independent of the pilot, can run before, during, or after it | Diff CLAUDE.md before/after to confirm no substantive rule was dropped, only de-duplicated | `git revert` this changeset's commit | Low — mechanical text consolidation, but touches a file every session loads, so review carefully before merging |

**Recommended execution order:** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8, with Changeset 10 run independently whenever convenient (it has no dependency on the pilot's outcome). This groups "define the vocabulary" (1) before "create an instance of it" (2) before "teach the commands to use it" (3–6) before "make it self-checking" (7) before "prove it on a real sprint" (8) — each changeset's validation step depends only on changesets already merged, so the sequence can pause after any step without leaving the repo in a half-wired state.

---

## 6. Command / skill integration matrix

| Command | Reads from `docs/sprints/` | Writes to `docs/sprints/` | Existing output unaffected? | Changeset |
|---|---|---|---|---|
| `/roadmap` | `CURRENT.md` (to report active sprint/stage-set) | — | Yes — `docs/ROADMAP.md` behaviour unchanged | 3 |
| `/pm` | `STAGE-REGISTRY.md` (entry conditions for downstream stages, to inform scoping) | `<id>/CONTEXT.md` on story approval | Yes — `docs/stories/` file convention unchanged | 3 |
| `/architect` | `STAGE-REGISTRY.md`, `<id>/state.md` | `<id>/decisions.md` (if a design decision is made outside a formal arch-council run) | Yes — checklist content unchanged | 3 |
| `/arch-council` | `<id>/state.md`, `docs/architecture/extraction-signals.md` (unchanged) | `<id>/architecture.md` (mandatory), `<id>/decisions.md` (mandatory) | Yes | 4 |
| Plan mode (`EnterPlanMode`/`ExitPlanMode`) | — | `<id>/plan.md` (copied from `~/.claude/plans/` at approval, per D5) | Yes — `~/.claude/plans/` still the harness's own record | 4 |
| Implementation | `<id>/state.md` (to check `implementation` is `eligible`, i.e. plan approved) | `<id>/state.md` (mark `active`, later `complete`) | Yes — git history remains the code-level record | 4 |
| `/verify` | `<id>/state.md` | `<id>/verification.md`, `<id>/state.md` | Yes | 5 |
| `/security` | `<id>/state.md` (to check entry condition: routes changed) | `<id>/decisions.md` (if marked `not-applicable`), `<id>/state.md` | Yes — `docs/security/` convention unchanged | 5 |
| `/auditor` | `<id>/state.md` | `<id>/audit.md`, `<id>/state.md` | Yes — `docs/audit/` convention unchanged | 5 |
| `/tester` | `<id>/state.md` | `<id>/state.md` (existing `docs/test-reports/` file also still written) | Yes | 5 |
| `/retro` | Every stage's status in `<id>/state.md`; every entry in `<id>/decisions.md` | `<id>/retrospective.md` (pointer), gate check before allowing close | Yes — `docs/retro-reports/` convention unchanged | 6, 8 |

---

## 7. Validation plan

- **Per-changeset validation** is specified in the table in §5 and must pass before the next changeset merges — changesets are not batched into one review.
- **Schema validation**: the lint script from Changeset 7 is the mechanical backbone; it must be run against three synthetic fixtures *before* being trusted against the real pilot: (a) a `state.md` with a `decision_ref` that doesn't exist in `decisions.md` (must fail), (b) a `state.md` with a `may_run_with` pairing not present in `STAGE-REGISTRY.md`'s parallel-compatibility column (must fail), (c) a clean, fully-consistent `state.md` (must pass). These three fixtures are written as part of Changeset 7, not invented ad hoc during the pilot.
- **Live-run validation**: every skill change (Changesets 3–6) is validated by actually invoking the command against the pilot sprint and inspecting the resulting file — not by reading the SKILL.md diff and assuming it works, per this project's own `/tester` "LIVE vs. STATIC vs. CODE REVIEW" taxonomy. A SKILL.md edit that hasn't been exercised live is a STATIC check, not a PASS.
- **Regression validation**: every existing output convention (`docs/stories/`, `docs/security/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/`) must be confirmed unchanged after each relevant changeset — this plan is additive by design, and a regression here would mean a changeset accidentally replaced rather than extended an existing habit.

---

## 8. Rollback plan

- **Changesets 1, 2, 10**: pure file addition/rename — `git revert` of the changeset's commit is sufficient and safe at any point.
- **Changesets 3, 5, 6**: SKILL.md edits are additive instructions (new steps appended, nothing existing removed) — reverting the commit restores prior behaviour with no data loss, since the sprint-folder writes these changesets introduce are themselves new files, not modifications to existing ones.
- **Changeset 4** (arch-council): higher risk because it modifies a *mandatory* gate. Rollback plan: revert `arch-council/SKILL.md` to its pre-changeset version; any `architecture.md`/`plan.md` already written during the pilot are left in place as historical record (they cause no harm sitting unused) rather than deleted, unless the pilot itself is abandoned.
- **Changeset 7** (linting): if the script produces false positives that block real work, the immediate mitigation is to stop invoking it (it is a script, not a hook, until D8 says otherwise) — no repository state needs to change to "turn it off." If it was promoted to a hook, remove the hook entry from `~/.claude/settings.json` and keep the script available for manual, non-blocking use.
- **Changeset 8** (pilot execution): if the pilot sprint itself is abandoned for reasons unrelated to the workflow mechanics (e.g. the underlying feature is deprioritized), the sprint folder is deleted and `CURRENT.md`'s `active_sprints` entry is removed — the static changesets (1, 3–7) remain merged and are exercised again by the next pilot attempt, so a failed pilot does not require re-doing the foundational work.
- **General principle**: no changeset in this plan performs a destructive operation on an existing file except Changeset 10's optional deletion of the stale `.claude/memory/` folder — and D6 recommends rename over delete specifically so that step is reversible too.

---

## 9. Pilot acceptance criteria

A fresh Casper session, given repository access only (no chat history, no auto-memory loaded), must be able to answer each of the following from `docs/sprints/<pilot-id>/` and the static files alone:

| Question | Answered by |
|---|---|
| Which sprint is active? | `docs/sprints/CURRENT.md` |
| Which stages are active, blocked, complete, skipped, or not-applicable? | `<pilot-id>/state.md` |
| What has been approved? | `<pilot-id>/plan.md` (plan approval), `<pilot-id>/architecture.md` (arch-council verdict), `<pilot-id>/decisions.md` (every other HITL call) |
| What evidence exists? | `<pilot-id>/evidence/<stage>/` |
| What decisions were made and by whom? | `<pilot-id>/decisions.md` — every entry has `decision_owner` |
| What work may proceed in parallel? | `<pilot-id>/state.md`'s `may_run_with` fields, cross-checked against `STAGE-REGISTRY.md` |
| What is currently blocked? | `<pilot-id>/state.md` entries with `status: blocked` and their `waiting_for` field |
| What are the next permitted actions? | Any stage in `<pilot-id>/state.md` with `status: eligible`, per the dependency rule in the diagnostic's §7.3 |

### Required test scenarios (seeded deliberately, not left to chance)

The pilot sprint's scope must be chosen (per D1) or supplemented with a deliberate small exercise so that all six of the following actually occur and are observed, not merely described:

1. **One skipped stage** — e.g. `/ux-designer` skipped because the pilot is backend-only; `decisions.md` entry present with reason and owner.
2. **One not-applicable stage** — e.g. `/security` marked `not-applicable` if the pilot touches no API route; distinguished in `state.md` from the skipped stage above.
3. **Two parallel stages** — e.g. `/verify` and `/security` both `active` at once, evidence written to separate `evidence/<stage>/` subfolders without collision.
4. **One rework loop** — a `complete` stage (e.g. `implementation`) deliberately reopened to `needs-rework` via a recorded decision, and confirmation that its dependents (e.g. `verification`) automatically revert to `blocked`.
5. **One unresolved dependency** — a stage left `blocked` on purpose at some point during the pilot, with `waiting_for` correctly naming the unmet stage, later resolving to `eligible` once that stage completes.
6. **One invalid `decision_ref` caught mechanically** — a deliberately broken fixture (not real pilot data) run through the Changeset 7 lint script to confirm it fails loudly, per the §7 validation plan.

The pilot is not considered complete until all six scenarios have been exercised and every question in the table above can be answered correctly by a reviewer reading only the repository files for `<pilot-id>`.

---

## 10. Statement of no implementation

No file listed in this plan has been created. No skill file, hook, or CLAUDE.md file has been modified as a result of this plan. `docs/sprints/` does not exist in this repository as of 2026-07-12. This document is a plan only, requiring the decisions in §3 and overall approval before Changeset 1 may begin.
