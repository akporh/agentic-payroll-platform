# Skill Handover — Phase 7 (D-031)

**Programme:** `product-traceability` · **Phase:** 7 `write-stage correction` · **Authorised by:** D-031
**Status:** **APPLIED 2026-07-29 and verified.** All six edits are in place; the four checks below pass. Four residual defects were found in the applied text — see § Residual defects. These edits are outside the programme's authorised scope (`POLICY.md` forbids `~/.claude/**`) and were handed over for manual application, per the Phase 5 precedent.
**Date:** 2026-07-29

Until these are applied, `docs/sprints/WORKFLOW.md` and `STAGE-REGISTRY.md` describe the two-pass split and the skills still describe the old one. The workflow documents are authoritative; the skills are the thing lagging.

Two files, six edits. Line numbers are as of 2026-07-29 and will shift as you edit — match on the quoted text, not the number.

---

## `~/.claude/skills/pm/SKILL.md`

### Edit 1 — the traceability bullet (currently line 65)

**Find:**

> - **Allocate a product-traceability ID for every in-scope story** (per `docs/sprints/WORKFLOW.md` § Product traceability, D-029). Read `docs/product/ID-ALLOCATION.md`, take the next free `STORY-<nnnn>` for each story — strictly sequential, never renumbered, never reused — and record it in both `ID-ALLOCATION.md` and the sprint's `CONTEXT.md` under `story_refs`. Allocate the ID only; `evidence_refs`, `sprint_refs` and `confidence` do not exist yet and are written by `/retro` at close. A story later dropped from scope keeps its ID — the ID is retired, not recycled. Scope is not agreed until every in-scope story carries one.

**Replace with:**

> - **Write the product-traceability record for every in-scope story** (per `docs/sprints/WORKFLOW.md` § Product traceability, D-031). This is `pm`'s output, not `retro`'s — `retro` completes it, it does not create it.
>   1. Read `docs/product/ID-ALLOCATION.md` and take the next free `STORY-<nnnn>` per story — strictly sequential, never renumbered, never reused. Record it in `ID-ALLOCATION.md` and in the sprint's `CONTEXT.md` under `story_refs`.
>   2. Create `docs/product/stories/STORY-<nnnn>-<slug>.md` **from `docs/product/stories/TEMPLATE.md`** — copy the file, do not write the sections from memory. Populate the intent fields: Origin code(s) (`None (authored here)`), Outcome, Capability, Feature, Classification, **Priority**, Actor, Problem addressed, Delivered behaviour (as *intended* behaviour), **Acceptance criteria**, **Out of scope**, Source reference, Decision references, Dependencies, Unresolved questions. Set `Status: backlog`.
>   3. Add the `STORY-REGISTRY.md` row with `ac_owner: hierarchy`, `confidence: requires human classification`, and **no delivery evidence**. Citing the source the item came from (`docs/PLAN.md`) is correct; citing a test report is not — the validator rejects it (D-031, OQ-5).
>   4. Leave `evidence_refs`, `sprint_refs`, `confidence` and Delivery history for `/retro`. Those are the only fields that require evidence that does not exist yet.
>   5. Run `python3 docs/product/validate_registry.py`. It must PASS before scope is agreed.
>
>   **`CONTEXT.md` links, it does not restate.** Cite `STORY-<nnnn>` and its title under `story_refs`, and point at the story record for acceptance criteria. Do not write a second copy of the criteria into `CONTEXT.md` — that duplication is exactly what D-031 removed, after it drifted on all five forward-authored stories written under the old split.
>
>   A story later dropped from scope keeps its ID — the ID is retired, not recycled. Scope is not agreed until every in-scope story carries a created record.

### Edit 2 — the output-format sections (currently lines 22–47)

Sections 1–6 (`User Story`, `Acceptance Criteria`, `Out of Scope`, `Business Risk / Impact`, `Priority Framing`, `Open Questions`) stay as the thinking prompts they are. Add this note directly beneath the `## For Every Feature or Change` heading:

> **Where these land.** Sections 1, 2, 3, 5 and 6 are the *intent* fields of the story record and are written into `docs/product/stories/STORY-<nnnn>-<slug>.md` — see the Sprint Workspace Integration section below. The record's schema decomposes the narrative rather than storing the sentence: **As a** → `Actor`, **I want** → `Delivered behaviour`, **So that** → `Problem addressed`. Section 2 → `Acceptance criteria`, section 3 → `Out of scope`, section 5 → `Priority`, section 6 → `Unresolved questions`.
>
> **Section 4 (Business Risk / Impact) is the exception** — it stays in the sprint's `CONTEXT.md` and does not go into the story record (D-031, OQ-3). It is sprint-instance context, not durable product intent.

### Edit 3 — `allowed-tools` (line 4)

Currently `Read, Glob, Grep, Write, Edit` — already sufficient, **no change needed**. Noted only so it is not re-checked: `pm` can write to `docs/product/`. (Per prior finding, a `tools:`/`allowed-tools:` declaration in a SKILL.md is inert anyway and does not restrict the session.)

---

## `~/.claude/skills/retro/SKILL.md`

### Edit 4 — step 12 (currently line 54)

**Find:** `…that is a `/pm`-stage miss — report it and allocate the IDs now rather than letting the sprint close unrecorded.`

**Replace the trailing clause with:**

> …that is a `/pm`-stage miss — report it, then allocate the IDs **and create the story records** now rather than letting the sprint close unrecorded. Under D-031 the records should already exist from scope confirmation; if they do not, you are doing `pm`'s work as well as your own, and the retro should record that as a process finding rather than silently absorbing it.

### Edit 5 — step 13 (currently line 55) — the main change

**Find:**

> 13. **For every `story_ref`, write the full record** into `docs/product/`: a row in `STORY-REGISTRY.md` and a file under `stories/`, plus the `SOURCE-INDEX.md` entry and the `FEATURES.md` story list. Populate `evidence_refs` and `sprint_refs` from this sprint's actual test report, audit review and security review — cite only files that exist on disk.

**Replace with:**

> 13. **For every `story_ref`, complete the record `pm` created** (D-031 — you complete these, you do not create them). Open `docs/product/stories/STORY-<nnnn>-<slug>.md` and fill the evidence fields only: `Implementation evidence`, `Test / review evidence`, `Delivery sprint(s)`, and one appended line to `Delivery history`. Update the `STORY-REGISTRY.md` row's `evidence_refs` and `sprint_refs` from this sprint's actual test report, audit review and security review — cite only files that exist on disk. Add the `SOURCE-INDEX.md` entry and the `FEATURES.md` story list.
>
>     **Do not rewrite the intent fields.** Actor, problem, acceptance criteria, out of scope and priority were agreed at scope confirmation and are already there. If implementation revealed that a criterion was wrong or incomplete, **edit it and record the change as a line in the sprint's `decisions.md`** — the same route a scope increase takes. A criterion that first appears at close, having never been visible during the sprint, is the failure D-031 was written to stop: it means `tester` verified one text and the registry publishes another with that evidence attached.

### Edit 6 — step 17 (currently line 59)

**Find:**

> 17. **If any `story_ref` is unresolved or the validator fails, stop.** Report it; do not mark the sprint or `retro` complete. Same hard-stop semantics as Part B.

**Replace with:**

> 17. **If any `story_ref` is unresolved or the validator fails, stop.** Report it; do not mark the sprint or `retro` complete. Same hard-stop semantics as Part B.
>
>     **"Unresolved" means incomplete, not absent (D-031).** Before D-031 the story file did not exist until this stage created it, so "resolved" and "the file exists" were the same test. They no longer are — the file exists from scope confirmation onward, in an intentionally incomplete state. A `story_ref` is resolved only when its record carries this sprint's `evidence_refs`, `sprint_refs` and `confidence`, and a `status` that is no longer the placeholder `backlog` written at `pm` — **unless** the story was scoped and genuinely not delivered, which closes as `backlog` under D-011 with that stated explicitly in the record. Checking only that a file exists would pass a sprint whose every record still holds its `pm` placeholders.

---

## Verifying the handover

After applying, confirm:

1. `grep -n "D-031" ~/.claude/skills/pm/SKILL.md ~/.claude/skills/retro/SKILL.md` returns hits in both.
2. Neither file still instructs `retro` to *write* or *create* a story record — only to complete one.
3. `pm`'s bullet names `docs/product/stories/TEMPLATE.md` by path. The absence of that pointer was finding F-2 in `write-stage-proposal.md`: `retro` was told to write "a file under `stories/`" and never told which schema, so nothing stopped a record being written in the wrong shape.
4. Update `state.md` § Current phase — replace "**Not yet applied.**" with the applied date, matching how the Phase 5 handover was recorded.

## Residual defects (found at verification, 2026-07-29) — **all four applied**

All four are **corrections** under the steady-state provision — true-or-false, no behaviour change. They sit in `~/.claude/**`, which this programme may not edit; they were applied on the human's explicit instruction, 2026-07-29, and re-verified (stale phrases return zero matches; replacements present).

### R-1 — `retro/SKILL.md` line 52: stale attribution

Part C's header reads *"…`WORKFLOW.md` § Product traceability (D-029)."* That section is now governed by D-029 **and** D-031. Change to `(D-029, D-031)`. Minor, but a stale citation in the one gate that enforces traceability is the wrong place to leave one.

### R-2 — `retro/SKILL.md` line 54: stray ellipsis

Step 12 reads *"If it did, …that is a `/pm`-stage miss"*. The `…` is a paste artefact from this document's find/replace instruction, not intended text. Delete it.

### R-3 — `pm/SKILL.md`: "Allocation is advisory, not enforcement" now understates `pm`'s role

The bullet's substance is still correct — `retro`'s Close Gate remains the only hard control, and `check_traceability_drift.py` deliberately never blocks. But its framing ("Allocation is advisory"; "do not imply the ID allocation is itself a control") predates D-031, under which `pm` no longer merely allocates an ID: it writes the record, and its own completion criteria now require one per in-scope story with the validator at PASS.

Suggested: retitle to **"Enforcement still sits at close, not at `pm`"** and open with *"`pm` now writes the story record, but writing it is not a control: nothing forces `pm` to run at all."* The warning survives; the obsolete premise goes.

### R-4 — `pm/SKILL.md` final bullet: now contradicts the stage's completion criteria

*"If no matching workspace exists, scope the sprint exactly as before — this integration is additive, not a new requirement to gate story-writing on."*

True under D-029, when the integration only added an ID allocation. Under D-031 `STAGE-REGISTRY.md`'s `pm` row makes a created record a completion criterion, so the sentence now tells the reader the opposite of what the registry requires. The no-workspace case still needs an answer — suggested: *"If no matching workspace exists, scope the sprint as normal and still write the story records; they live in `docs/product/`, which does not depend on a sprint workspace existing."*

**R-3 and R-4 matter more than R-1/R-2.** They are not typos: both are live instructions that now point the wrong way, and a reader following either would skip the step D-031 exists to add.

## Next sprint is the real test

The first sprint to run under this will show whether the split holds. Two things to watch:

- Does `pm` actually produce a usable record before implementation starts, or does it stall waiting for detail that genuinely isn't knowable yet? If the latter, the honest fix is to name which field was premature — not to slide back to writing everything at close.
- Does `retro` respect the intent fields, or quietly rewrite them? Rewriting is the old failure in a new place. `/retro` should surface every criterion it changed.
