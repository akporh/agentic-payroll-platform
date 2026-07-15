<!--
Template for one story record under docs/product/stories/.
Copy this file to <story-id>-<descriptive-slug>.md (e.g.
PT-A4-31-component-source-trace-fix.md) — do not edit this template in place.
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
-->

# `<story-id>` — `<title>`

**Outcome:** `<outcome_id>` (see `../OUTCOMES.md`)
**Capability:** `<capability_id>` (see `../CAPABILITIES.md`)
**Feature:** `<feature_id>` (see `../FEATURES.md`)
**Classification:** `<user-facing story | operational story | compliance story | platform capability | technical enabler | defect/remediation | discovery or architecture item>`
**Status:** `<delivered | in-flight | backlog>`
**Confidence:** `<confirmed | strongly inferred | tentative | requires human classification>`

## Actor

`<Who this story serves — a role, not a person. e.g. "payroll operator", "bureau setup admin".>`

## Problem addressed

`<Plain-language description of the problem this story solves. Do not invent quantified benefits, original user intent, or business outcomes not supported by evidence.>`

## Delivered behaviour

`<What actually exists/works now, described plainly. If not yet delivered, describe the intended behaviour and mark status accordingly.>`

## Source reference

`<The requirement, finding, or roadmap reference this story traces back to — e.g. a docs/ROADMAP.md line, an arch-council decision, an audit finding.>`

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
