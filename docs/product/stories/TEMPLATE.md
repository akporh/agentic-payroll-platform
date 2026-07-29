<!--
Template for one story record under docs/product/stories/.
Copy this file to <story-id>-<descriptive-slug>.md (e.g.
STORY-0145-component-source-trace-fix.md) — do not edit this template in place.
The slug exists so a filename alone identifies the story without opening it;
validate_registry.py matches a file to its registry row by story-ID prefix
(exact stem, or stem starting with "<story_id>-"), not by exact-stem equality.
Every field below is required; use "unknown" or "n/a" explicitly rather than leaving a field blank.
This template does not itself represent a delivered story — it is scaffolding only.

Amended during the Phase 4A pilot migration (2026-07-15, see
docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md):
added Outcome/Capability, Decision references, Dependencies, and Delivery history
sections. The original template only carried Feature/Classification/Status/
Confidence plus narrative evidence fields — it had no place to record the outcome
and capability a story rolls up to, no place for decision-ID traceability, no
explicit dependency field, and no append-only delivery-history mechanism distinct
from the single "Delivery sprint(s)" line. The pilot's two stories could not be
recorded to the letter of the migration rules without these fields, so this is
recorded here as a genuine schema defect, not scope creep — see the run record
and docs/programmes/product-traceability/critic-review-phase-4a-pilot.md.

Amended again 2026-07-28 (Phase 3B, D-018/D-019/D-023):
- Story IDs are now STORY-<nnnn> and encode nothing. Origin code(s) became a
  mandatory field so every legacy identifier the work was known by stays findable.
- Parent references now carry the ID *and* the name. Citing a bare "FEAT-4" forced
  a reader to open another file to learn what the story belonged to — the ID+name
  convention D-016 introduced for the registries had never been applied here.
- An Acceptance criteria section was added, with ownership differing by how the
  story came into existence (D-018). Its absence was a real gap: a reviewer
  reasonably expected migrated stories to carry the criteria their source had.

Amended again 2026-07-29 (Phase 7, D-031):
- WRITE STAGE. A forward-authored record is now created by `pm` at scope
  confirmation, not by `retro` at close. `pm` populates the intent fields and sets
  `status: backlog`; `retro` populates the evidence fields, flips the status and
  appends the delivery-history line. See the "Who writes what" table below.
  Previously `pm` wrote the criteria into the sprint's `CONTEXT.md` and `retro`
  transcribed them here — that transcription drifted on all five forward-authored
  stories produced under it, so the criteria `tester` verified and the criteria the
  registry published were not the same text.
- Out of scope and Priority sections added (D-031 OQ-2). Neither had anywhere to
  live: deliberate exclusions were invisible, so a reader could not tell work ruled
  out from work missed; and priority was being re-derived by hand on every planning
  pass across ~20 backlog rows, despite sprint CONTEXT.md files already writing
  "(P2)"/"(P3)" into story headings.
- Business risk was considered and deliberately NOT added (D-031 OQ-3) — it is
  sprint-instance context and stays in the sprint's CONTEXT.md.
-->

<!-- WHO WRITES WHAT (D-031) — guidance, not a story field. Delete when copying.

| Stage | Fields |
|---|---|
| `pm`, at scope confirmation | Origin code(s) · Outcome · Capability · Feature · Classification · Priority · Status (`backlog`) · Actor · Problem addressed · Delivered behaviour (as *intended* behaviour) · Acceptance criteria · Out of scope · Source reference · Decision references (as known) · Dependencies · Unresolved questions |
| `retro`, at sprint close | Implementation evidence · Test / review evidence · Confidence · Delivery sprint(s) · Delivery history (append one line) · Status → `delivered`, or `backlog` per D-011 if scoped and not delivered |

A retro-migrated record is written in one pass by whoever performs the migration;
the split above applies to forward-authored stories only.
-->

# `<story-id>` — `<title>`

**Origin code(s):** `<every legacy identifier this work has been known by — provisional PT ID, sprint item code, track code; "·"-separated. Write "None (authored here)" for a forward-authored story. Mandatory: never leave blank.>`
**Outcome:** `<outcome_id>` — `<outcome name>`
**Capability:** `<capability_id>` — `<capability name>`
**Feature:** `<feature_id>` — `<feature name>`
**Classification:** `<user-facing story | operational story | compliance story | platform capability | technical enabler | defect/remediation | discovery or architecture item>`
**Priority:** `<P0 system broken | P1 compliance or financial obligation | P2 operator productivity | P3 nice to have>`
**Status:** `<delivered | in-flight | backlog>`
**Confidence:** `<confirmed | strongly inferred | tentative | requires human classification>`

<!-- Parent names are display-only copies; the IDs are authoritative. A rename in
OUTCOMES/CAPABILITIES/FEATURES.md must update every copy in the same change —
validate_registry.py rejects a name that has drifted from its parent. -->

## Actor

`<Who this story serves — a role, not a person. e.g. "payroll operator", "bureau setup admin".>`

## Problem addressed

`<Plain-language description of the problem this story solves. Do not invent quantified benefits, original user intent, or business outcomes not supported by evidence.>`

## Delivered behaviour

`<What actually exists/works now, described plainly. If not yet delivered, describe the intended behaviour and mark status accordingly.>`

## Acceptance criteria

`<Ownership depends on how this story came into existence (D-018):`

`RETRO-MIGRATED (delivered before this hierarchy existed) — write:`
`"Owned by the source story file, not by this record — this is a retro-migrated story,`
`so its authoritative acceptance criteria stay where they were written and are not`
`duplicated here (D-018). Follow the Source reference below."`
`Do not copy the criteria across: the source is closed and frozen, and two copies drift.`

`FORWARD-AUTHORED (written here by the PM, no prior sprint story file) — the criteria`
`live HERE and are authoritative. Write them out in full as a checklist. There is no`
`other file to point at.>`

## Out of scope

`<What this story deliberately does NOT do, and — where it is not obvious — why.`
`Written by pm at scope confirmation (D-031). This exists so a reader can tell work`
`that was ruled out from work that was missed: without it, an absent behaviour is`
`indistinguishable from an oversight, and the layer's core property is that a gap`
`counts as evidence.`

`Record only exclusions a reader could plausibly expect to be included. Do not list`
`everything the story is not. For a retro-migrated story, write "Not recorded —`
`migrated before this field existed" rather than reconstructing it from memory.>`

## Source reference

`<The requirement, finding, or roadmap reference this story traces back to — e.g. a docs/ROADMAP.md line, an arch-council decision, an audit finding. Also add this story to ../SOURCE-INDEX.md so the reverse lookup works.>`

## Implementation evidence

`<Files, migrations, or code paths that implement this story. Cite specific paths, not "the codebase".>`
`<Implementation commit reference(s) — full or abbreviated SHA(s).>`

## Test / review evidence

`<Test report, audit report, or security review that verifies this story. Cite specific file paths.>`

## Decision references

`<Decision ID(s) relevant to this story — e.g. a sprint-workspace DEC-<sprint>-<n> HITL decision, or a programme-level D-<n> decision. State "None" explicitly if no decision is relevant beyond routine execution.>`

## Dependencies

`<Other story_id(s), migrations, or preconditions this story depends on. State "None" explicitly if there are no dependencies.>`

## Delivery sprint(s)

`<Sprint or track ID(s). If designed in one sprint and delivered in another, say so explicitly rather than collapsing to one reference.>`

## Delivery history

`<Append-only list — one line per sprint/contribution, oldest first, in the form "YYYY-MM-DD — <sprint/commit> — what changed". Never overwrite or remove a prior line; add a new line for each later contribution to this same story (e.g. a fix, a re-verification, a follow-up sprint).>`

## Unresolved questions

`<Anything left open about this story's scope, evidence, or classification. If none, write "None.">`
