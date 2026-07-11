# Sprint Workflow — ICM Diagnostic

**Date:** 2026-07-11
**Scope:** Repository diagnostic, read-only — no application code, migrations, or workflow files were modified in the course of this inspection.
**Question:** Is the sprint workflow (`/roadmap` → `/pm` → `/architect` → `/arch-council` → plan mode → implementation → `/verify`/`/security` → `/auditor`/`/tester` → `/retro` → push) implemented as an Interpretable Context Methodology (ICM) workspace, or does it only appear as one because it's a disciplined sequence of slash commands?

---

## 1. Executive conclusion

> **Sequential workflow, not ICM-structured**

The workflow is a well-disciplined *sequence of skill invocations*, not a workspace. Every stage's instructions live in one shared, always-loaded prompt (three stacked `CLAUDE.md` files plus whichever `SKILL.md` is active) rather than in a stage-scoped folder the stage reads on entry. There is no folder boundary per stage, no `CONTEXT.md` contract, and — critically — no single directory that answers "what sprint is active, what stage is it in, what was approved" by itself. That answer currently lives across three places that don't reference each other: `docs/ROADMAP.md` (backlog state), `~/.claude/plans/*.md` (plan artefacts, outside the repo, unlinked from anything), and a per-project auto-memory index (`handoff_note.md`) that is itself a duplicate of a second, stale, in-repo memory folder.

Tellingly, two *other* workspaces in this same repository — `docs/agentic-architecture-review/` and `docs/audit-program/`, both freshly created — already implement the exact pattern this diagnostic is checking for: numbered stage folders, a `CONTEXT.md` contract per stage, a `findings.md`/`decisions.md` handoff, a single `*-state.md` tracker, and an explicit gate rule ("a stage may not begin until the prior stage's gate has been explicitly passed"). The sprint workflow that ships product code has none of this. The capability to build ICM structure clearly exists in this environment; it was simply never applied to the workflow that matters most.

---

## 2. Current context map

| Stage | Command | Governing source | Inputs | Outputs | Gate | State location | Hidden dependencies |
|---|---|---|---|---|---|---|---|
| **Roadmap** | `/roadmap` | SKILL.md `roadmap` | `docs/ROADMAP.md` | Terminal text only | None | `docs/ROADMAP.md` (self-admittedly can go stale) | Skill tells the model to trust ROADMAP.md, but also says "may be stale" and to defer to `/brief` — no automatic check |
| **PM** | `/pm` | SKILL.md `pm` | Conversation only | Story text in chat; sometimes a file under `docs/stories/` | None enforced by tooling | No dedicated file — story creation is a human/model judgment call each time | Memory feedback file requires PM to "read existing stories" first — a rule that lives in memory, not in the skill itself |
| **Architect** | `/architect` | SKILL.md `architect` (218 lines, mostly retro-derived checklists) | Conversation, plan draft | Design decisions in chat | None | None — decisions only persist if manually copied into a plan file or memory | Most of the file's checking power is 15 sprint-specific "retro" addenda appended over time — undiscoverable without reading the whole file top to bottom |
| **Arch-council** | `/arch-council` | SKILL.md + two persona files | `~/.claude/agents/senior-architect.md`, `principal-reviewer.md`, `docs/architecture/extraction-signals.md` | Verdict text in chat (APPROVED / NEEDS REVISION / …) | **Human**, informal | Extraction-signals.md is updated; the council verdict itself is **not written anywhere** | Persona files live in `~/.claude/agents/` — user-home, not repo — so a fresh clone of the repo cannot reconstruct who "the architect" is |
| **Plan mode** | `EnterPlanMode` / `ExitPlanMode` | Harness built-in | Everything discussed so far | `~/.claude/plans/<random-name>.md` | **Human** approval via ExitPlanMode prompt | `~/.claude/plans/` — **outside the git repo**, randomly named, not linked from ROADMAP or any story file | Nothing in the repo points to the plan file that was approved. Approval is a UI event, not a record. |
| **Implementation** | direct edits | 3 stacked `CLAUDE.md` files + PostToolUse hooks | Approved plan (from memory of the conversation) | Code diff | None besides the hooks firing reminders | Git history | Hooks are configured in `~/.claude/settings.json`, a user-level file — not visible from the repo itself |
| **Verify / Security** | `/verify`, `/security` | Global `verify` skill (bootstraps a project-local one if absent — **none exists yet**); `security` SKILL.md | Running app, changed routes | Findings in chat; security review sometimes written to `docs/security/YYYY-MM-DD-*.md` | None enforced | `docs/security/` exists but is written inconsistently — only 3 dated files across 30+ sprints | The project has no project-scoped `verify` skill despite the global one expecting to bootstrap one — first invocation would silently create it ad hoc |
| **Audit / Test** | `/auditor`, `/tester` | SKILL.md per skill | Running app, sprint AC | `docs/audit/`, `docs/test-reports/YYYY-MM-DD-sprint-N.md` | Tester's own PASS/FAIL taxonomy (LIVE vs STATIC vs CODE REVIEW) | Consistently written — **the one stage with a real, disciplined artefact convention** | None major — this is the strongest link in the chain |
| **Retro / Push** | `/retro` | SKILL.md `retro` | `git log`, `MEMORY.md`, plan file "if it still exists" | Edits to SKILL.md files, memory files, sometimes CLAUDE.md | "With user confirmation" | Diffuse — spread across skill files, memory files, and CLAUDE.md with no single retro log | Retro step itself notes the plan file "if it still exists" — an acknowledgment that plan-file persistence is already known to be unreliable |

---

## 3. Authority map

| Instruction source | Scope | Loaded by | Authority | Conflicts | Recommendation |
|---|---|---|---|---|---|
| `~/.claude/CLAUDE.md` | All projects | Always, automatically | governing | None found | Retain as-is |
| `.../2.OnAiR/CLAUDE.md` | All onAiR work | Always, automatically | governing | None found | Retain |
| `.../Sandy/CLAUDE.md` | Sandy client | Always, automatically | workflow-level | None found | Retain |
| `.../agentic-payroll-platform/CLAUDE.md` | This codebase | Always, automatically | workflow-level | Duplicates the global "Sprint Sequence" almost verbatim — same 17 steps restated with local auto-invoke triggers layered on | Consolidate: reference the global sequence, hold only auto-invoke triggers + data-contract table |
| `~/.claude/skills/*/SKILL.md` (9 files) | One stage each | On explicit invocation only | stage-level | `architect` and `arch-council` overlap heavily — both claim data-contract review | Keep, but split architect's 15 appended retro sections into a separate "lessons" reference |
| `~/.claude/agents/senior-architect.md`, `principal-reviewer.md` | arch-council only | Spawned by arch-council skill | stage-level | User-home scoped — not visible to anyone cloning the repo | Relocate persona definitions (or a copy) into the repo if verdicts must be reproducible by another operator |
| `docs/ROADMAP.md` | Backlog state | Manually, by `/roadmap` | task-specific | Roadmap skill itself documents known staleness risk | Retain, but wire the "post-sprint accuracy check" into a script instead of a manual grep list |
| `~/.claude/plans/*.md` | One plan each | Manually, must know exact filename | generated | Not referenced from anywhere in the repo once written | Copy the approved plan into `docs/planning/` or `docs/stories/` at ExitPlanMode time so it survives outside harness-local state |
| `.claude/memory/project_sprint13_m3_arch_decisions.md` (repo-committed) | Appears project-wide | Nothing — orphaned | **stale** | **Directly conflicts** with the real, current memory store below — same-looking path, one file, frozen at Sprint 13 | Deprecate / delete; dead weight that could mislead a future session or tool that globs `.claude/memory/` |
| `~/.claude/projects/.../memory/*.md` (75 files, MEMORY.md index) | This project, cross-session | Auto-loaded at session start | task-specific | Same nominal purpose as the file above, different location, no cross-link | This is the real, live store — keep, but resolve the name collision with the dead in-repo folder |
| `docs/security/`, `docs/audit/`, `docs/test-reports/`, `docs/retro-reports/` | Per-sprint evidence | Manually, written inconsistently | reference-only | Coverage is uneven — test-reports has 20+ files, security has 3, retro-reports has 1 | Make one of these mandatory-on-close (test-reports already functions this way) and apply the same discipline elsewhere |
| `~/.claude/settings.json` hooks | All Sandy work, user-level | Fires automatically on Edit/Write/Bash | governing (mechanical) | None — the one deterministic, always-on part of the system | Retain; this is the model for what stage gates should look like everywhere else |

---

## 4. Context provenance map

| Rule | Origin |
|---|---|
| 17-step sprint sequence, arch-council gate triggers, memory rules | **Repository file** — both CLAUDE.md layers, duplicated |
| Per-stage checklists (input validation, migration safety, trace completeness…) | **Repository file** — `~/.claude/skills/*/SKILL.md`, user-home but versioned by Claude Code tooling conventions |
| "is_active means not-withdrawn, always pair with effective_from" and 14 other data-contract invariants | **Repository file** — CLAUDE.md "Known Data Contract Rules" table (the single best piece of ICM-shaped state in the whole workflow) |
| Duplicate revision-ID check, str(e) reminder, tsc reminder, push reminder | **Hook** — `~/.claude/settings.json` PostToolUse/PreToolUse, mechanical and reliable |
| "PM must read docs/stories/ before generating stories"; "no blind implementation without a sprint"; "confirm scope before plan mode" | **Agent memory** only — not restated anywhere in CLAUDE.md or the pm/architect skill files. If auto-memory ever fails to load, this rule is gone with no fallback. |
| Which persona plays "Senior Architect" / "Principal Engineer" in arch-council | **Slash command** pointing at `~/.claude/agents/*.md` — user-home, unversioned relative to the repo |
| Whether a given roadmap item is actually done | **Unknown source** — the roadmap skill itself says to distrust the file and re-derive from grep; there is no authoritative record, only a re-derivation procedure |
| What the currently active sprint even is | **Conversation history** only. No file in the repo names "the current sprint." ROADMAP.md lists closed sprints; nothing marks one *open*. |
| Whether an arch-council verdict was APPROVED / NEEDS REVISION for a specific design | **Conversation history** only — printed to chat, never written to a file |
| Fix commits / retro lessons ("re-verify the fix touches the reported bug", etc.) | **Skill file**, correctly promoted from memory into `architect/SKILL.md` — this is the one place the loop from "caught late" to "written into governing instructions" visibly closes |

---

## 5. Fresh-session reconstruction test

Could a brand-new Casper session answer these from the repo alone?

| Question | Answer |
|---|---|
| What sprint is active? | **No** — ROADMAP.md lists sprint history but has no "current sprint" marker. Answerable only via the auto-memory handoff note, which is outside the repo and can be stale or absent. |
| Which stage is active? | **No** — no file records "we are between arch-council and implementation." Only conversation history or an unwritten mental model carries this. |
| What has been approved? | **No** — plan-mode approval is a UI click, never persisted. Arch-council verdicts print to chat and vanish. The data-contract rules table in CLAUDE.md is the one exception: real, durable, repo-visible approvals. |
| What must be read? | **Partially** — CLAUDE.md's "Key Files to Read Before Planning" is a good static list, but nothing tells a fresh session which of the 30+ story files, 20+ test reports, or 3 security reviews are relevant to the item currently in flight. |
| What output is expected? | **Partially** — test-reports and stories have a clear naming/file convention a new session could infer and follow. Plans, arch-council verdicts, and PM stories do not. |
| What cannot be changed? | **Yes** — the "Known Data Contract Rules" and "API Route Rules" tables in CLAUDE.md are exactly this: durable, explicit, repo-visible constraints. The strongest part of the whole system. |
| What is the next allowed stage? | **No** — there is no stage-lifecycle concept at all (contrast with `docs/audit-program/WORKFLOW.md`'s explicit `not-started → in-progress → blocked → complete` lifecycle, which exists a few directories away in the same repo for a different workflow). |

---

## 6. Gap register

| ID | Gap | Evidence | Consequence | Severity | Recommended correction |
|---|---|---|---|---|---|
| G1 | No file names the currently active sprint or stage | `docs/ROADMAP.md` has no "current" marker; no `docs/sprints/<active>/` folder exists | A fresh session cannot self-orient; must reconstruct state from conversation or hope the memory handoff note is current | High | Add one file, `docs/sprints/CURRENT.md`, updated at each stage transition |
| G2 | Plan-mode output lives outside the repo and is never linked to | `~/.claude/plans/*.md` — randomly named, home-directory scoped | Approved plans cannot be audited later, cannot be diffed against implementation, invisible to any other tool or teammate | High | Copy the approved plan into `docs/planning/<sprint>.md` at ExitPlanMode time, referenced from the story file |
| G3 | arch-council verdicts are never written to a file | arch-council SKILL.md Step 4 ("Synthesise and Present") outputs only to chat | The one mandatory data-contract gate produces no durable evidence that it ran, or what it concluded — undermines the "RC5 lesson" the gate exists to prevent | High | Write the Council Summary to `docs/architecture/decisions/<date>-<topic>.md` as a mandatory last step |
| G4 | Two divergent memory stores with the same nominal purpose | `.claude/memory/` (1 stale file, committed to git) vs `~/.claude/projects/.../memory/` (75 files, live) | A future contributor or tool that reads the committed `.claude/memory/` folder gets a Sprint-13 snapshot presented as current | Medium | Delete the stale committed folder or clearly mark it archived; document the real store is user-home scoped |
| G5 | Project CLAUDE.md restates the global sprint sequence almost verbatim instead of referencing it | Compare "Sprint Workflow" in `~/.claude/CLAUDE.md` to "Automated Delivery Workflow" in the project file — same 17 steps, duplicated | Any future edit to the global sequence silently diverges from the project copy unless both are remembered and updated together | Medium | Project file should hold only local deltas (auto-invoke triggers, hook table) and link to the global sequence |
| G6 | Uneven evidence discipline across stages | `docs/test-reports/` has 20+ dated files; `docs/security/` has 3; `docs/retro-reports/` has 1; audit has 2 | Tester's stage is the only one that reliably leaves a trail — security, audit, and retro findings are largely reconstructable only from memory or chat | Medium | Apply the tester skill's "always write the file, even on failure" rule to security, auditor, and retro identically |
| G7 | Architect's checklist is 218 lines of accreted, undated retro addenda with no index | `~/.claude/skills/architect/SKILL.md` — 15+ sprint-specific sections appended chronologically | A check added in a Sprint 7 retro is discoverable only by reading the entire file; nothing signals which checks are "core" vs. situational | Medium | Split into a short core checklist plus a separate, searchable lessons file the skill links to by keyword |
| G8 | No project-scoped `verify` skill exists yet, despite the global skill assuming one | Global `verify` skill description: "bootstraps this repo's project verify skill if none exists yet" — none found under any expected path | First invocation silently creates ad hoc process instead of following a pre-agreed, reviewed procedure | Low | Bootstrap it deliberately once, in a reviewed session, rather than letting the first real verify pass improvise it |
| G9 | Two sibling workspaces in the same repo already solve this problem correctly, unreferenced by the sprint workflow | `docs/agentic-architecture-review/WORKFLOW.md`, `docs/audit-program/WORKFLOW.md` | Working ICM pattern exists a few directories away and is not being reused — proof the fix is cheap, not proof the gap is minor | Low (opportunity) | Lift the stage-folder + `CONTEXT.md` + state-tracker pattern from these two workspaces directly into a minimal sprint-workspace structure (see §7) |

---

## ICM criteria scoring (0–3 each)

| Criterion | Score | Notes |
|---|---|---|
| A — Visible stage structure | 1/3 | No stage folders. `docs/` subfolders exist per artefact type (stories, test-reports), not per stage. |
| B — Stage contracts | 1/3 | SKILL.md files are contracts for the *skill*, not the sprint stage — no per-sprint `CONTEXT.md`. |
| C — Context isolation | 1/3 | Every stage runs inside the same shared 3-layer CLAUDE.md + full conversation history. |
| D — Explicit handoffs | 2/3 | Test reports and stories hand off cleanly; plans and arch-council verdicts do not persist at all. |
| E — Filesystem state | 1/3 | No file answers "what stage, what's approved" without chat or memory. |
| F — Authority hierarchy | 2/3 | Global → project → local CLAUDE.md is a real, consistent hierarchy; undermined by duplication (G5) and the orphaned memory folder (G4). |
| G — Resumability | 1/3 | Depends entirely on the auto-memory handoff note being current and undamaged — a single point of failure, not a repo guarantee. |
| H — Human control | 2/3 | Gates are real (ExitPlanMode, arch-council, retro confirmation) but their outcomes aren't recorded — the gate fires, the record doesn't. |
| I — Mechanical vs. reasoning work | 3/3 | PostToolUse/PreToolUse hooks genuinely enforce migration-ID checks, push reminders, and tsc reminders deterministically. Best-scoring criterion. |
| J — Traceability | 1/3 | A roadmap item can be traced to a story and a test report by filename convention, but not through architecture, plan, or security/audit review — those links exist only in a human's memory of the sprint. |

**Total: 15/30** — informal-to-partial across the board, with one deterministic bright spot (I) and one structural strength worth preserving (F's hierarchy, once G4/G5 are cleaned up).

---

## 7. Recommended target structure — REVISED (non-linear execution model)

> **⚠ PROPOSAL — requires human approval before any repository change.** This section replaces the original Section 7 (the four-file, single-current-stage model first proposed 2026-07-11). Nothing in this section has been implemented; `docs/sprints/` does not yet exist.

### 7.0 Revision note

The original recommendation modeled sprint state as a single scalar: `current sprint → current stage`. That shape is wrong for how this workflow actually runs — stages are skipped (`/security` when no routes changed), run out of order (a design question can send work back to `/architect` mid-implementation), and run concurrently (`/verify` and `/security` both start once implementation lands, without waiting on each other). ICM does not require a fixed pipeline; it requires that state, gates, and decisions be *explicit and inspectable*, however the graph actually branches. `docs/audit-program/` already proves this in miniature — its per-stage `blocked` status with a named blocking issue, and its rule that "an explicit `_core/human-decisions.md` entry authorizes proceeding early," are graph-routing primitives, not sequence primitives, even though its 13 stages happen to run mostly in order. The revised model generalizes that same primitive (named status + recorded reason + dependency check) to the sprint workflow, where branching is the norm rather than the exception.

The corrected shape:

```text
current sprint
    → active stage set        (not one stage — several may be eligible/active/blocked at once)
    → dependency graph        (STAGE-REGISTRY.md — static, reusable across all sprints)
    → gates                   (WORKFLOW.md — static routing/transition rules)
    → recorded routing decisions   (decisions.md — dynamic, one log per sprint)
    → completion and evidence state (state.md — dynamic, one record per sprint)
```

### 7.1 Revised filesystem structure

```text
docs/sprints/
├── CURRENT.md              # which sprint workspace(s) are active — nothing more
├── WORKFLOW.md              # static: transition/parallel/skip/rework rules — reusable across sprints
├── STAGE-REGISTRY.md        # static: one row per stage — purpose, inputs, outputs, dependencies
└── <sprint-id>/
    ├── CONTEXT.md            # this sprint's goal, in-scope stories, out-of-scope, AC
    ├── state.md              # authoritative, current status of every activated stage
    ├── decisions.md          # append-only HITL decision log for this sprint
    ├── plan.md                # copied from ~/.claude/plans/ at approval (conditional — only if planning ran)
    ├── architecture.md        # only if /architect or /arch-council ran
    ├── verification.md        # only if /verify ran
    ├── audit.md                # only if /auditor ran
    ├── retrospective.md       # only if /retro ran
    └── evidence/                # raw artefacts (test output, security findings, trace excerpts)
        └── <stage>/[attempt-N/]
```

No file above is mandatory for every sprint. **`STAGE-REGISTRY.md` declares which artefacts a given activated stage requires** (§7.3) — a one-line bugfix sprint that skips `/architect` never gets an `architecture.md`, and that absence is not an error, it's the recorded consequence of a skip decision in `decisions.md`.

### 7.2 Stage-state model

`<sprint-id>/state.md` is the authoritative execution-state record. Every stage carries one of these statuses:

| Status | Meaning |
|---|---|
| `not-started` | Registered in the sprint but no entry condition has been evaluated yet |
| `eligible` | Entry conditions and dependencies are satisfied; not yet activated |
| `active` | Currently being worked |
| `blocked` | Cannot proceed — `waiting_for` names the unmet dependency |
| `complete` | Completion criteria met, evidence recorded |
| `skipped` | Deliberately not run this sprint — reversible, may be activated later if conditions change |
| `not-applicable` | Structurally does not apply to this sprint's type — not merely deferred |
| `needs-rework` | Was `complete`, reopened by a human decision; downstream dependents revert to `blocked` |

Example:

```yaml
sprint: sprint-31
status: active

stages:
  roadmap:
    status: complete

  architecture:
    status: skipped
    reason: isolated low-risk change, single file, no data contract touched
    decision_ref: DEC-031-01

  implementation:
    status: active
    depends_on: [approved-plan]

  verification:
    status: active
    may_run_with: [implementation]

  security:
    status: not-applicable
    reason: no API route or input-handling surface changed
    decision_ref: DEC-031-02

  audit:
    status: blocked
    waiting_for: [implementation, verification]
```

`skipped` vs. `not-applicable` is a real distinction, not a style choice: a `skipped` stage remains a candidate for later activation if new evidence changes the picture (e.g. implementation turns out to touch a status enum after all); `not-applicable` means the stage's precondition structurally cannot occur this sprint (e.g. `/security` for a migration-only sprint with zero routes touched) and does not need re-evaluating unless the sprint's scope itself changes.

### 7.3 Routing and dependency model

Two files carry the *static* rules — written once, reused by every sprint — and one file carries the *dynamic* record for one sprint:

- **`STAGE-REGISTRY.md`** (static, cross-sprint) — one row per stage:

  | Field | Meaning |
  |---|---|
  | Stage ID | Stable identifier (`roadmap`, `pm`, `architecture`, `arch-council`, `implementation`, `verification`, `security`, `audit`, `test`, `retro`) |
  | Purpose | What the stage achieves |
  | Mandatory status | `mandatory` \| `conditional` \| `optional` |
  | Entry conditions | What must be true before the stage becomes `eligible` |
  | Inputs | Required artefacts (from this or a prior stage) |
  | Outputs | Required artefacts this stage must produce to reach `complete` |
  | Dependencies | Stage IDs or decision types required first |
  | Parallel compatibility | Stage IDs it may run alongside |
  | Skip conditions | The circumstances under which a human may mark it `skipped` or `not-applicable` |
  | Completion criteria | Evidence required to close |
  | Human gate | Required decision type, if any |

  This is the same content CLAUDE.md's auto-invoke table already states informally (e.g. "`/security` — any sprint that adds or modifies API routes") — `STAGE-REGISTRY.md` makes the *entry condition* the authoritative, machine-checkable version of that sentence, rather than duplicating the rule. CLAUDE.md keeps ownership of *why*; the registry states *when, formally*.

- **`WORKFLOW.md`** (static, cross-sprint) — the transition rules that operate over the registry: which stage combinations are allowed concurrently, which dependency types unblock a stage (`complete` only, or `complete`/`skipped`/`not-applicable` all count), and the default routing when a decision isn't recorded (default is always `blocked`, never silently `not-applicable`).

- **`<sprint-id>/state.md`** (dynamic, per-sprint) — declares the actual `depends_on` / `may_run_with` / `waiting_for` values for *this instance*, which must be a subset of what `STAGE-REGISTRY.md` permits. A stage becomes `eligible` the moment every ID in its `depends_on` list is `complete`, `skipped`, or `not-applicable` — never on `active` or `blocked`.

### 7.4 Parallel stage rules

- A stage may declare `may_run_with: [<stage-id>, ...]` in `state.md` only if that pairing appears in the stage's `Parallel compatibility` column in `STAGE-REGISTRY.md` — the sprint cannot invent a parallel pairing the registry doesn't allow (e.g. `implementation` and `audit` must never run concurrently; `verification` and `security` may).
- Parallel stages write evidence to isolated subfolders — `evidence/<stage>/` — so two stages running at once never overwrite each other's artefacts.
- A parallel stage still needs its own dependencies satisfied independently; `may_run_with` only says two eligible/active stages don't block each other, not that they share entry conditions.

### 7.5 Skip and not-applicable rules

Every `skipped` or `not-applicable` entry in `state.md` **must** carry, at minimum:

```yaml
status: skipped            # or not-applicable
reason: <one sentence, specific>
decision_owner: <name>
decision_ref: DEC-<sprint>-<seq>   # must resolve to an entry in decisions.md
date: YYYY-MM-DD
compensating_control: <optional — what covers the risk instead>
```

`STAGE-REGISTRY.md`'s `Mandatory status` column governs whether skipping is even a legal move: a `mandatory` stage (e.g. `arch-council` when a data contract is touched) cannot be marked `skipped` — only `not-applicable`, and only if its entry condition genuinely doesn't hold, with a decision reference. A `conditional` or `optional` stage (e.g. `/ux-designer` on a backend-only sprint) may be `skipped` freely, but the reason is still mandatory — no empty reasons.

### 7.6 Rework loop rules

- A `complete` stage may be reopened to `needs-rework` only via a recorded decision (`decisions.md`) — never silently.
- The moment a stage moves to `needs-rework`, every stage whose `depends_on` includes it automatically reverts to `blocked` in `state.md` — this is a mechanical consequence of §7.3's eligibility rule, not a separate rule to remember.
- Prior evidence is never deleted. A second pass writes to `evidence/<stage>/attempt-2/`; `state.md` records `attempt: 2` so it's visible which pass produced the artefact currently governing the stage's `complete` status.
- Rework does not restart the whole sprint — only the reopened stage and its dependents change status; independent stages (e.g. `/retro`, if it hasn't started) are unaffected.

### 7.7 Recording HITL decisions

`<sprint-id>/decisions.md` is an append-only log — one entry per human decision, in the order they were made:

```yaml
- id: DEC-031-02
  date: 2026-07-14
  decision_owner: Michael Emedo
  stage: security
  decision_type: not-applicable   # skip | not-applicable | activate | allow-parallel | rework | block
  reason: No API route or input-handling surface changed this sprint — migration-only.
  reference: conversation 2026-07-14, or a linked artefact
```

Every `decision_ref` anywhere in `state.md` must resolve to an `id` here — a reason with no matching decision entry is a lint failure, not a valid state. This is what makes gate outcomes durable (closing gap G3 and G7 from the original diagnostic): the arch-council verdict a mandatory gate produces becomes a `decisions.md` entry, not a chat message that evaporates when the session ends.

### 7.8 Separation of concerns (design principle 8)

| Concern | Lives in | Reused across sprints? |
|---|---|---|
| Reusable skill instructions (how to run `/architect`, what to check) | `~/.claude/skills/*/SKILL.md` — unchanged | Yes |
| Stage metadata (inputs/outputs/dependencies/mandatory-ness) | `docs/sprints/STAGE-REGISTRY.md` | Yes |
| Transition/parallel/skip/rework rules | `docs/sprints/WORKFLOW.md` | Yes |
| Sprint-specific context (goal, scope, AC) | `docs/sprints/<id>/CONTEXT.md` | No — one per sprint |
| Current execution state | `docs/sprints/<id>/state.md` | No — one per sprint, mutated in place |
| Human decisions | `docs/sprints/<id>/decisions.md` | No — append-only per sprint |
| Generated evidence | `docs/sprints/<id>/evidence/` | No — per sprint, per stage, per attempt |

Skill logic stays in `~/.claude/skills/` exactly where it is today — this revision does not ask any sprint file to restate a checklist. `CONTEXT.md`/`state.md`/`decisions.md` hold only sprint-instance data; `STAGE-REGISTRY.md`/`WORKFLOW.md` hold only the rules, once.

---

## 8. Migration plan — REVISED

**Proposal only — not to be implemented until approved.** Replaces the original Section 8 migration plan, which assumed the linear model.

| Action | Item |
|---|---|
| Retain | Three-layer CLAUDE.md hierarchy; SKILL.md per stage (unchanged — registry references them, doesn't replace them); PostToolUse/PreToolUse hooks; test-reports naming convention; "Known Data Contract Rules" table |
| Relocate | Plan-mode output (`~/.claude/plans/` → `docs/sprints/<id>/plan.md` at approval time, conditional on planning having run) |
| Make explicit (new) | `docs/sprints/STAGE-REGISTRY.md` (formalizes CLAUDE.md's auto-invoke table into entry conditions); `docs/sprints/WORKFLOW.md` (routing/parallel/skip/rework rules); `<id>/state.md` (graph status, not scalar "current stage"); `<id>/decisions.md` (durable HITL log — closes G3's arch-council-verdict gap directly) |
| Consolidate | Project CLAUDE.md's restated 17-step sequence → reference the global one, keep only local auto-invoke deltas (these deltas become `STAGE-REGISTRY.md` entry conditions instead of prose); architect skill's 15 retro addenda → core checklist + linked lessons file |
| Deprecate | The committed, stale `.claude/memory/` folder (1 file, frozen at Sprint 13) — superseded by the real auto-memory store; the original linear `docs/sprints/CURRENT.md` design (single "active stage" line) — replaced by the `active_sprints` list + per-sprint `state.md` graph |
| Automate | Roadmap's "post-sprint accuracy check" → a script; a lint step that checks every `decision_ref` in every `state.md` resolves to a `decisions.md` entry (mechanical enforcement of §7.7, in the spirit of criterion I which already scores 3/3 for hooks) |
| Do not change | The underlying calculation/domain rules, hook logic, or skill content itself; do not build a workflow engine — Markdown + YAML only, per constraint |

### 8.1 Comparison — original vs. revised recommendation

| Current recommendation | Revised recommendation |
|---|---|
| Current sprint + current stage | Current sprint + active stage set |
| Sequential stage progression | Dependency-based routing (`depends_on` / `may_run_with` / `waiting_for`) |
| One stage at a time | Parallel stages allowed, gated by registry-declared compatibility |
| Implicit skipping | Explicit skip decision, recorded with owner/reason/reference, distinguished from not-applicable |
| Linear completion | Graph completion — a sprint is done when every activated stage is `complete`, `skipped`, or `not-applicable`, not when stage N+1 begins |

---

*This revision addresses the drop-file request `docs/diagnostics/2026-07-11-prompt-revise-sprint-workflow-icm-target-model.md`. It revises the proposal document only — `docs/sprints/` has not been created, and no other repository or application file has been changed.*

*Companion visual report (original diagnostic content, styled): rendered as a Claude Artifact during the diagnostic session.*
