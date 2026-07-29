# Write-Stage Proposal — moving story-record authorship from `retro` to `pm`

**Programme:** `product-traceability` · **Phase:** **Phase 7** `write-stage correction` · **Authorised by:** **D-031**
**Status:** **ADOPTED 2026-07-29.** Approved as written; OQ-1–OQ-5 all resolved in `decisions.md` § D-031 — full change (OQ-1), Out of scope + Priority added to the template (OQ-2), Business risk stays in `CONTEXT.md` (OQ-3), the five drifted `roadmap-split` records left as history (OQ-4), the backlog-with-evidence validator rule added (OQ-5). Phase 7 is recorded in `PHASES.md` with allowed paths named before any in-scope file was written. **Execution is a separate step and has not begun.**
**Date:** 2026-07-29 · **Adopted:** 2026-07-29

---

## 1. What this is, and why it exists

Phase 5 (D-029) wired traceability into the sprint workflow with a two-point split: `pm` allocates the `STORY-<nnnn>` when scope is agreed, `retro` writes the full registry row and story file at close.

That split puts **story authorship at the end of the sprint**. `pm` — the stage whose entire purpose is to scope the work and define done — writes its output into `docs/sprints/<id>/CONTEXT.md`, and `retro` later transcribes it into the durable record.

This proposal argues that the transcription step is unnecessary, that it has already caused measurable drift on every forward-authored story so far, and that it is an artefact of the retro-migration the programme was built to perform rather than a property of the steady state it produced.

Three rules held while writing this:

- **Nothing is asserted without evidence on disk.** Every claim below cites a file and can be re-checked.
- **The strongest objection is stated, not smoothed** — section 7.
- **No scope is smuggled.** Section 9 lists what this proposal deliberately does *not* change.

---

## 2. The defect

### 2.1 A forward-authored story's acceptance criteria exist twice

D-018 fixed acceptance-criteria ownership by origin:

- **Retro-migrated** — criteria stay in the frozen sprint story file; the product record links, never duplicates. Stated reason: *"the source is closed and frozen, so two copies would only drift."*
- **Forward-authored** — criteria live in the product record, authoritatively.

The forward case has the same two-copy problem, and it is worse, because both copies are live and editable:

| Copy | Written at | Written by |
|---|---|---|
| `docs/sprints/<id>/CONTEXT.md` | scope confirmation | `pm` |
| `docs/product/stories/STORY-<nnnn>-*.md` | sprint close | `retro` |

Nothing in `POLICY.md`, `WORKFLOW.md` or D-018 states which of the two is authoritative during the sprint. D-018's reasoning was applied to the retro case and never re-derived for the forward case.

### 2.2 It has already drifted — on 5 of 5 stories

`roadmap-split` (closed 2026-07-29) produced the first five forward-authored stories under this scheme. They are the only ones carrying `ac_owner: hierarchy`; the other 171 registry rows carry `ac_owner: source`.

Comparing `docs/sprints/roadmap-split/CONTEXT.md` against `docs/product/stories/`:

| Story | AC bullets in `CONTEXT.md` | AC bullets in record | Divergence |
|---|---|---|---|
| `STORY-0158` | 4 | **5** | Record adds the `S7`/`Q1` stale-marker criterion, learned during implementation. Also `python` → `python3`; "stays internally honest" → "stays honest". |
| `STORY-0159` | 4 | 4 | Substantive: *"the 20 open items"* became *"the open Phase 1 items"* — the count was dropped. |
| `STORY-0160` | 4 | 4 | Wording only. |
| `STORY-0161` | 3 | 3 | Wording only. |
| `STORY-0176` | 5 | **6** | Record splits and expands the never-blocks criterion into implementation specifics (`main()` returns 0; `set -e` cannot promote a warning). |

**All five differ. Two differ in criterion count. One dropped a quantified figure.**

`validate_registry.py` passes on all of them — correctly, since it checks story-file ↔ row correspondence, parent resolution, name drift, `origin_code` presence, `PT-*` leakage, path existence and `FEATURES.md` round-tripping. It has no notion of acceptance-criteria equivalence, and adding one would be the wrong fix.

### 2.3 Why the drift direction matters

In every case the **record is the better text** — it reflects what was actually built and what was learned. That is not reassuring; it is the diagnosis.

It means `CONTEXT.md`'s criteria were written once and abandoned, while the criteria of record were composed at close. So:

- The criteria that gated implementation and that `/tester` verified against were `CONTEXT.md`'s.
- The criteria the registry publishes, and attaches that test evidence to, are a later, different text.

A reader of `STORY-0158` sees five criteria and a passing test report, and reasonably concludes the report verified those five. It verified four, one of which was worded differently. The evidence link is not false, but it is not what it appears to be either.

---

## 3. Root cause

The hierarchy was built entirely by retro-migration: 157 stories created after the work was finished, in one pass. For a migrated story, intent and evidence genuinely arrive at the same instant — there is no earlier stage that could have written the intent, because the stage had already run, years of sprints ago.

Writing the whole record in one act was therefore correct for Phase 4. Phase 5 carried that shape into the steady state without re-deriving it for the forward case, where intent and evidence arrive months apart.

The artefacts are visible in the files themselves:

- **`stories/TEMPLATE.md`'s own header** records that it was amended *during the Phase 4A pilot migration* to add Outcome/Capability, decision references, dependencies and delivery history — *"the pilot's two stories could not be recorded to the letter of the migration rules without these fields."* The schema was shaped by migration need.
- **D-018** split ownership explicitly on retro-vs-forward. The programme knew the two cases behave differently; it fixed which *file* owns the criteria and never asked which *stage* writes the record.
- **`docs/product/README.md`** still describes the layer as *"a historical and current-state record, not a replacement planning surface."* That was true when written. `roadmap-split`'s `STORY-0160` then required every forward item in `docs/PLAN.md` to carry a `story_ref`, which makes the registry a planning surface in fact.

`WORKFLOW.md:100` gives the stated rationale: *"Allocating only at close would mean a sprint runs start to finish with nothing to reference; completing only at `pm` would mean inventing evidence that doesn't exist."*

The first half is right. The second half assumes the record must be written all at once. It need not be — see section 4.

---

## 4. Proposed change

### 4.1 Split the template by when each field becomes knowable

The template's nineteen fields divide cleanly:

| Known at `pm` — **intent** | Only knowable at `retro` — **evidence** |
|---|---|
| Origin code(s) | Implementation evidence |
| Outcome / Capability / Feature | Test / review evidence |
| Classification | Confidence |
| Actor | Delivery sprint(s) |
| Problem addressed | Delivery history *(append a line)* |
| Delivered behaviour *(as intended behaviour)* | |
| **Acceptance criteria** | |
| Source reference | |
| Decision references *(as known)* | |
| Dependencies | |
| Status: `backlog` | Status → `delivered` |
| Unresolved questions | |

**Proposal:** `pm` creates `docs/product/stories/STORY-<nnnn>-<slug>.md` with the left column populated and `status: backlog`, plus the `STORY-REGISTRY.md` row. `retro` populates the right column, flips status, appends the delivery-history line, and completes `SOURCE-INDEX.md` / `FEATURES.md`.

`retro` stops transcribing and starts completing.

### 4.2 `CONTEXT.md` keeps sprint scope, drops duplicated criteria

`POLICY.md`'s boundary — *"Sprint `CONTEXT.md` owns selected execution scope for that sprint"* — is unchanged and correct. `CONTEXT.md` continues to hold the goal, the in-scope story list, out-of-scope, and sprint-instance framing.

For each in-scope story it cites `STORY-<nnnn>` and its title, and **links** to the story record for criteria rather than restating them. One text, one owner, no transcription.

*(For retro-migrated stories nothing changes: `ac_owner: source`, the record links to the frozen sprint file, exactly as D-018 fixed.)*

### 4.3 Criteria that change mid-sprint become visible

Today a criterion learned during implementation appears silently in the record at close — `STORY-0158`'s fifth bullet and `STORY-0176`'s sixth arrived this way, and no reader can tell they were not agreed at scoping.

Under this proposal the criteria live in one file from the start, so a mid-sprint change is a visible edit to the story record and is recorded as a line in the sprint's `decisions.md` — matching the existing route for a scope increase (`roadmap-split` DEC-05 is the worked example). Criteria discovered during build are normal and often the most valuable output of a sprint; they should be legible as such, not arrive as a silent diff.

---

## 5. Why this is safe — the shape already exists

The obvious objection is that a story record created at `pm` sits in the permanent registry half-populated, and pollutes `ID-ALLOCATION.md`'s claim that *"an item absent from this table is an item no known evidence records."*

**That shape is already live, already validated, and already required.**

`STORY-0150` through `STORY-0155` are six `status: backlog` records carrying:

```
## Implementation evidence
None — not implemented.

## Test / review evidence
None — not implemented.
```

They pass `validate_registry.py`. They exist because **D-011 requires** scoped-but-undelivered work to hold an identifier and be visible rather than silently absent. `roadmap-split`'s `STORY-0160` then created ~14 more of them for open roadmap items, deliberately, as `status: backlog` / `confidence: requires human classification`.

So "a story record that exists before its evidence does" is not a new state this proposal introduces. It is the established, decided treatment of planned work — the proposal only makes it the state every story passes through, instead of a special case for work that was never scheduled.

No schema change is needed. No validator change is needed.

---

## 6. What stays with `retro`

This is not a proposal to move traceability out of `retro`. `retro` keeps:

- **Evidence refs** — implementation, test, audit, security — cited only as files that exist on disk.
- **`confidence`**, set from *this sprint's own* evidence, under the existing rule that a passing test report and completed audit records `confirmed`, never `strongly inferred`.
- **The status flip** to `delivered`, or the D-011 close-as-`backlog` for scoped work not delivered.
- **The append-only delivery-history line.**
- **The Close Gate** — `retro` still cannot reach `complete` while any `story_ref` is unresolved. This is what makes traceability a condition of closing rather than a habit, and this proposal does not touch it.

---

## 7. The strongest objection, stated fairly

**"`CONTEXT.md`'s criteria are working notes, not a publication. Drift between a working note and a durable record is expected and harmless — that is what the two files are for."**

This is a real position and it explains the observed data: in all five cases the record improved on the note, which is what you would want if the note is a draft.

Two responses:

1. **Nothing says it is a draft.** `POLICY.md` names `CONTEXT.md` the owner of "selected execution scope"; `roadmap-split/CONTEXT.md` is headed *"scope confirmed 2026-07-29 (DEC-01 through DEC-04, recorded before any in-scope file was touched)"* and is cited by Phase 6's PHASES.md entry as a **required input** establishing that four stories need a feature. It is treated as a decided artefact by other authorised documents, not as a scratch pad.
2. **Even granting it,** the objection concedes the substantive point: the criteria that gated the build were not the criteria of record. Whether `CONTEXT.md` is draft or decided, `/tester` verified one text and the registry publishes another with that verification attached. Calling the first a draft makes the evidence link weaker, not stronger.

A cheaper alternative — keep the current two-stage split and require `retro` to diff the two copies and report changes — would fix the visibility half of the problem and leave the duplication. It is a smaller change and worth considering if the proposal below is judged too large; it is recorded here as the fallback, not the recommendation.

---

## 8. Three secondary findings

Surfaced by the same review. All touch the same files; folded in here rather than filed separately.

### F-1 — `TEMPLATE.md` has no field for deliberate exclusions, priority, or business risk

Comparing `/pm`'s six output sections and the recurring headings across the 37 files in `docs/stories/` against the template, most map cleanly (`Open Questions` → `Unresolved questions`; `Dependency Map` → `Dependencies`; `Background`/`Goal`/`Problem` → `Problem addressed`; the `As a / I want / So that` narrative → `Actor` + `Problem addressed` + `Delivered behaviour`).

Three have no counterpart anywhere in the product layer — not in the template, not as a `STORY-REGISTRY.md` column:

- **Out of scope / scope boundary** — appears in 9 files across three heading variants (`Scope Boundary` ×5, `Out of Scope` ×2, `Explicitly Out of Scope` ×2). Without it a reader cannot distinguish *"not built because we ruled it out"* from *"not built because we missed it"* — a distinction the layer depends on, since its stated property is that a gap counts as evidence.
- **Priority (P0–P3)** — the strongest case. D-011 requires undelivered scope to close as `status: backlog`; the registry now holds ~20 such rows; `docs/PLAN.md` consumes them as the forward plan. A backlog story with no priority is unrankable, so priority is re-derived by hand on every planning pass. Note `roadmap-split`'s `CONTEXT.md` already writes `(P2)`/`(P3)` into its story headings — the field exists in practice and has nowhere to land.
- **Business risk / impact** — cost of not doing it, cost of doing it wrong. Weakest case of the three; arguably sprint-instance context that legitimately stays in `CONTEXT.md`. Recorded for a decision either way rather than left implicit.

*A partial fourth:* old story files carried `Architecture Notes` / `Implementation Notes` holding **rationale**. `Implementation evidence` holds paths and `Decision references` holds decision IDs; neither holds reasoning. Lower priority — `docs/sprints/<id>/decisions.md` covers it for new sprints.

### F-2 — `retro` is not told which schema to write

`~/.claude/skills/retro/SKILL.md` step 13 reads: *"write the full record… a row in `STORY-REGISTRY.md` and a file under `stories/`."* It never names `stories/TEMPLATE.md` and never names the `Actor` / `Problem addressed` / `Delivered behaviour` decomposition. The translation from `pm`'s `As a / I want / So that` narrative into the decomposed fields is left to the operator, unprompted, and `validate_registry.py` would not catch a record that pasted the narrative in whole.

This is largely dissolved by section 4 — if `pm` writes the record, `pm` is the stage that needs the pointer — but whichever stage owns it must cite the template by path.

### F-3 — `state.md` is stale

`docs/programmes/product-traceability/state.md` states *"All decisions to date received and recorded: D-001–D-029"* and *"Phase 5 … was the last defined phase."* D-030 authorised Phase 6, which `PHASES.md` carries. This is a **correction** under the steady-state provision — one line in the relevant sprint's `decisions.md`, no story, no phase. Named here so it is not lost; not part of this proposal's scope.

---

## 9. What this proposal does *not* change

- The `STORY-<nnnn>` scheme, allocation rules, or the never-renumber/never-reuse rule (D-019).
- The outcome / capability / feature set, or any story's feature assignment.
- `validate_registry.py`'s checks.
- D-018's treatment of **retro-migrated** stories — the pointer-only rule stands, untouched.
- The `retro` Close Gate, or any stage ordering, dependency or skip rule in `WORKFLOW.md`.
- Any of the 157 migrated story records. Nothing is retrofitted; this binds new sprints only, matching the D-029 precedent (*"This applies to new sprints only. Closed sprint workspaces are history and are not retrofitted."*).
- `docs/ROADMAP.md`, which stays frozen and forbidden to this programme.

---

## 10. Authorisation path

This is **structural change**, not an addition or a correction. `PHASES.md` § Steady state reserves *"changing what a registry column means"* to a new phase and a human decision; `POLICY.md` reserves *"source-of-truth changes (any change to the ownership model)"* to human approval, and closes with *"This boundary list may only be changed by explicit human approval recorded in `decisions.md`."* Section 4 changes which stage owns story-record authorship and amends D-018's forward-authored branch. Both gates apply.

Requested:

1. **D-031** in `decisions.md` — approve, amend or reject sections 4 and 8 (F-1 items individually).
2. **Phase 7 `write-stage correction`** in `PHASES.md`, with allowed paths named *before* any file is written, per the standing rule that authorisation is never back-filled. Expected scope: `docs/programmes/product-traceability/**`, `docs/product/stories/TEMPLATE.md`, `docs/product/README.md`, `docs/sprints/WORKFLOW.md` (§ Product traceability only), `docs/sprints/STAGE-REGISTRY.md` (`pm` and `retro` rows only).
3. **`POLICY.md` amendment** to the source-of-truth boundary list, recording which stage writes the forward-authored record.

### The skills problem

The behaviour change lands in `~/.claude/skills/pm/SKILL.md` and `~/.claude/skills/retro/SKILL.md`. `POLICY.md` forbids this programme from touching `~/.claude/**`, and `WORKFLOW.md:111` already records this as a known gap under D-029: *"the `/pm` and `/retro` skills … perform this work, and that path is outside this programme's authorised scope."*

The precedent is Phase 5's: the programme wrote the obligation into `WORKFLOW.md` and `STAGE-REGISTRY.md`, and the skill-side edits were **applied by the human and verified** (`state.md`, 2026-07-29). This proposal assumes the same handover and does not seek authority over `~/.claude/**`.

---

## 11. Open questions for the decision

| # | Question | Why it needs a human |
|---|---|---|
| OQ-1 | Adopt section 4, or the section 7 fallback (keep the split; require `retro` to diff and report)? | Trades correctness against size of change. |
| OQ-2 | Do **Out of scope** and **Priority** join `TEMPLATE.md`? (F-1) | Template shape is a governed structure. |
| OQ-3 | Does **Business risk** join it, or stay in `CONTEXT.md`? (F-1) | Genuinely arguable; I lean stay. |
| OQ-4 | Should the 5 `ac_owner: hierarchy` stories from `roadmap-split` be reconciled, or left as history? | §9 says no retrofit; these five are the only live drift, so an exception is defensible. I lean leave, and record the drift here as the evidence. |
| OQ-5 | Does a `pm`-written record need a validator rule that `status: backlog` + populated evidence fields is contradictory? | New failure mode this proposal creates; cheap to add, but adds a check the programme has so far kept minimal. |

**Unverified.** I have not traced whether `pm`'s declared `allowed-tools` and the Close Gate's unresolved-`story_ref` check behave correctly when the story record already exists at sprint open. That must be confirmed before Phase 7 is executed, not assumed.
