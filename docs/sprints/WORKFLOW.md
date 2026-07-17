# Sprint Workflow

**Static, cross-sprint, reusable.** This file defines the transition, parallel, skip, and rework rules that operate over `STAGE-REGISTRY.md`. It does not restate stage-specific detail (purpose, entry conditions, dependencies, parallel compatibility, mandatory status) — that lives only in `STAGE-REGISTRY.md`, per D2. This file states the general rules; the registry states the per-stage specifics those rules operate on.

Modeled on `docs/audit-program/WORKFLOW.md`'s stage-lifecycle section and the non-linear execution model approved in `docs/diagnostics/2026-07-11-sprint-workflow-icm-diagnostic.md` §7.

---

## Why non-linear

Stages are skipped (`security` when no routes changed), run out of order (a design question surfaced during implementation can send work back to `architecture`), and run concurrently (`verification` and `security` both start once `implementation` lands, without waiting on each other). This workflow models sprint state as a **graph** — an active stage *set*, not a single "current stage" scalar — because that is how the work actually happens, not because non-linearity is a goal in itself.

## Stage status values

Every stage in a sprint's `state.md` carries exactly one of these statuses:

| Status | Meaning |
|---|---|
| `not-started` | Registered in the sprint but no entry condition has been evaluated yet |
| `eligible` | Entry conditions and dependencies are satisfied; not yet activated |
| `active` | Currently being worked |
| `blocked` | Cannot proceed — `waiting_for` names the unmet dependency |
| `complete` | Completion criteria met, evidence recorded |
| `skipped` | Deliberately not run this sprint — reversible; may be activated later if conditions change |
| `not-applicable` | Structurally does not apply to this sprint's type — not merely deferred, and not reversible without a scope change |
| `needs-rework` | Was `complete`, reopened by a recorded human decision; downstream dependents revert to `blocked` |

`skipped` vs. `not-applicable` is a real distinction, not a style choice. A `skipped` stage remains a candidate for later activation if new evidence changes the picture (e.g. implementation turns out to touch a status enum after all, so `arch-council` — previously thought not-applicable — must be re-evaluated). `not-applicable` means the stage's precondition structurally cannot occur this sprint and does not need re-evaluating unless the sprint's scope itself changes.

**Update `state.md` in the same turn the work finishes, not later.** The turn that completes a stage's substantive work (writing the code, running the review, producing the evidence) must also write that stage's terminal status into `state.md` — do not defer this as bookkeeping to "do later." A stage left at `eligible`/`active`/`not-started` after its work is actually done is invisible to every downstream dependency check and to `retro`'s Sprint Workspace Close Gate, which will then have to catch and correct it retroactively (`dev-levy-rule-pct` sprint, 2026-07-17 — `implementation` and `verification` were both found stale this way).

## Eligibility rule

A stage becomes `eligible` the moment every stage ID in its `depends_on` list is `complete`, `skipped`, or `not-applicable` — **never** on `active` or `blocked`. This is the only eligibility rule; there is no separate "soft" eligibility.

**Default routing when no decision is recorded is always `blocked`, never silently `not-applicable`.** A stage does not become `not-applicable` by omission — it requires an explicit decision (see Skip and not-applicable rules, below) with a `decision_ref` that resolves in `decisions.md`. Absence of a decision leaves a stage `blocked`, which is visible and inspectable, rather than silently skipped.

## Parallel stage rules

- A stage may declare `may_run_with: [<stage-id>, ...]` in its sprint's `state.md` **only if** that pairing appears in that stage's `Parallel compatibility` column in `STAGE-REGISTRY.md`. A sprint cannot invent a parallel pairing the registry doesn't allow.
- Per the registry as currently drafted: `verification` and `security` may run concurrently. `implementation` and `audit` must never run concurrently.
- Parallel stages write evidence to isolated subfolders — `evidence/<stage>/` — so two stages running at once never overwrite each other's artefacts.
- A parallel stage still needs its own dependencies satisfied independently; `may_run_with` only says two eligible/active stages don't block each other — it does not mean they share entry conditions.

## Skip and not-applicable rules

Every `skipped` or `not-applicable` entry in a sprint's `state.md` **must** carry, at minimum:

```yaml
status: skipped            # or not-applicable
reason: <one sentence, specific>
decision_owner: <name>
decision_ref: DEC-<sprint>-<seq>   # must resolve to an entry in decisions.md
date: YYYY-MM-DD
compensating_control: <optional — what covers the risk instead, if anything>
```

`STAGE-REGISTRY.md`'s `Mandatory status` column governs whether skipping is even a legal move:

- A **mandatory** stage (e.g. `arch-council` when its entry condition holds) cannot be marked `skipped` — only `not-applicable`, and only if the entry condition genuinely does not hold, with a `decision_ref`.
- A **conditional** stage (e.g. `verification`, `security`, `audit`, `architecture` — each conditional on a specific trigger in the registry) may be `skipped` when its trigger doesn't apply, or marked `not-applicable` if the trigger structurally cannot occur — the reason is mandatory either way; no empty reasons.
- There are currently no stages registered as `optional` in `STAGE-REGISTRY.md`; if one is added later, an `optional` stage may be `skipped` freely, same reason requirement.

## Rework loop rules

- A `complete` stage may be reopened to `needs-rework` only via a recorded decision in `decisions.md` — never silently.
- The moment a stage moves to `needs-rework`, every stage whose `depends_on` includes it automatically reverts to `blocked` in `state.md` — this is a mechanical consequence of the eligibility rule above, not a separate rule to remember or apply by hand.
- Prior evidence is never deleted. A second pass writes to `evidence/<stage>/attempt-2/`; `state.md` records `attempt: 2` so it's visible which pass produced the artefact currently governing the stage's `complete` status.
- Rework does not restart the whole sprint — only the reopened stage and its dependents change status. Independent stages (e.g. `retro`, if it hasn't started yet) are unaffected.

## Recording HITL decisions

`<sprint-id>/decisions.md` is an append-only log — one entry per human decision, in the order they were made:

```yaml
- id: DEC-<sprint>-<seq>
  date: YYYY-MM-DD
  decision_owner: <name>
  stage: <stage-id>
  decision_type: skip | not-applicable | activate | allow-parallel | rework | block
  reason: <specific, one sentence minimum>
  reference: <conversation date/context, or a linked artefact>
```

Every `decision_ref` cited anywhere in a sprint's `state.md` must resolve to an `id` here. A reason with no matching `decisions.md` entry is a lint failure (`scripts/lint_sprint_state.py`, once introduced), not a valid state — this is what makes gate outcomes durable: an `arch-council` verdict, for instance, becomes a `decisions.md` entry, not a chat message that evaporates when the session ends.

## Sprint completion

A sprint is done when every activated stage in its `state.md` is `complete`, `skipped`, or `not-applicable` — not when some fixed final stage number is reached. `retro` checks this explicitly before allowing sprint close (see `STAGE-REGISTRY.md`'s `retro` entry): no stage may be left `active` or `blocked` at close.

## Separation of concerns

| Concern | Lives in | Reused across sprints? |
|---|---|---|
| Reusable skill instructions (how to run a stage, what to check) | `~/.claude/skills/*/SKILL.md` — unchanged by this workflow | Yes |
| Stage metadata (purpose/inputs/outputs/dependencies/mandatory-ness) | `docs/sprints/STAGE-REGISTRY.md` | Yes |
| Transition/parallel/skip/rework rules | `docs/sprints/WORKFLOW.md` (this file) | Yes |
| Which sprint(s) are active | `docs/sprints/CURRENT.md` | Yes (points at whichever sprint is current) |
| Sprint-specific context (goal, scope, AC) | `docs/sprints/<id>/CONTEXT.md` | No — one per sprint |
| Current execution state | `docs/sprints/<id>/state.md` | No — one per sprint, mutated in place |
| Human decisions | `docs/sprints/<id>/decisions.md` | No — append-only per sprint |
| Generated evidence | `docs/sprints/<id>/evidence/` | No — per sprint, per stage, per attempt |

Skill logic stays in `~/.claude/skills/` exactly where it is today — this workflow does not ask any sprint file to restate a checklist. `CONTEXT.md` / `state.md` / `decisions.md` hold only sprint-instance data; `STAGE-REGISTRY.md` / `WORKFLOW.md` (this file) hold only the rules, once.
