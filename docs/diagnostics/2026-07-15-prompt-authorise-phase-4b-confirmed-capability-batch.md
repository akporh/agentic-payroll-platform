# Casper Prompt — Authorise and Run Product Traceability Phase 4B Confirmed-Story Batch

## Objective

Authorise and execute a bounded Phase 4B historical-migration batch for **confirmed stories only**, limited to **one capability area** and a target size of approximately **10–20 stories**.

This phase exists to prove the Phase 4A model at a larger but still controlled scale before any wider historical migration is authorised.

Do not migrate strongly inferred, tentative, requires-human-classification, backlog, disputed, or unresolved-compliance items.

## Governing inputs

Read and obey:

- `docs/programmes/product-traceability/PROGRAMME.md`
- `docs/programmes/product-traceability/POLICY.md`
- `docs/programmes/product-traceability/PHASES.md`
- `docs/programmes/product-traceability/state.md`
- `docs/programmes/product-traceability/decisions.md`
- `docs/programmes/product-traceability/phase-inputs.yaml`
- `docs/programmes/product-traceability/exceptions.md`
- `docs/programmes/product-traceability/critic-review-phase-4a-pilot.md`
- `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md`
- `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`
- `docs/product/README.md`
- `docs/product/OUTCOMES.md`
- `docs/product/CAPABILITIES.md`
- `docs/product/FEATURES.md`
- `docs/product/STORY-REGISTRY.md`
- `docs/product/stories/TEMPLATE.md`
- `docs/product/validate_registry.py`

The Phase 4A pilot conventions are authoritative unless this prompt explicitly changes them.

## Human authorisation

This prompt constitutes explicit human authorisation for:

- Phase 4B only;
- one capability-area batch only;
- confirmed stories only;
- approximately 10–20 stories;
- writes limited to the approved programme-control files and `docs/product/`;
- an independent critic gate;
- stopping before any further batch.

It does not authorise the remainder of Phase 4.

## Batch-selection rule

Select exactly one capability area from the discovery inventory using this order of preference:

1. a capability area containing between 10 and 20 `confirmed` items;
2. otherwise, the capability area closest to that range without exceeding 20;
3. otherwise, choose a coherent confirmed-only subset of no more than 20 items from one capability area.

Before migration, write a concise batch-selection record explaining:

- capability area selected;
- candidate confirmed items found;
- items included;
- items excluded and why;
- expected outcomes/capabilities/features to be created or reused;
- expected story count.

Do not select items merely to hit a numeric target. Preserve coherent product grouping.

## Mandatory exclusions

Exclude all items with any of these conditions:

- `strongly inferred`;
- `tentative`;
- `requires human classification`;
- backlog / not delivered;
- PH_OT `is_pensionable` unresolved item;
- Gate 4 disputed item;
- any contradictory or insufficient evidence discovered during execution;
- any story whose migration would require rewriting historical source files.

If an item initially appears confirmed but direct inspection materially weakens that confidence, exclude it and record the reason. Do not silently downgrade and migrate it within this batch.

## Allowed write scope

You may modify or create files only under:

```text
docs/product/
docs/programmes/product-traceability/
```

The saved prompt file may remain unchanged.

## Forbidden write scope

Do not modify or create files under:

```text
docs/ROADMAP.md
docs/stories/
docs/sprints/
docs/audit/
docs/audit-program/
docs/agentic-architecture-review/
docs/security/
docs/test-reports/
docs/retro-reports/
backend/
frontend/
migrations/
~/.claude/
```

All unlisted paths are forbidden for writes.

Historical evidence sources are read-only.

## Migration requirements

For every migrated story:

1. Preserve its stable story ID.
2. Use a descriptive filename beginning with the full stable ID.
3. Add exactly one corresponding row to `STORY-REGISTRY.md`.
4. Create or reuse the correct outcome, capability, and feature rows.
5. Preserve the approved hierarchy:

```text
Outcome → Capability → Feature → Story
```

6. Record both:
   - delivery status;
   - evidence confidence.
7. Link to the original authoritative evidence rather than duplicating historical acceptance criteria.
8. Record delivery history, including sprint/track and contribution.
9. Record decision references where applicable.
10. Record dependencies only where supported by evidence.
11. Do not invent actors, business outcomes, dependencies, or delivery dates.
12. Keep the story title understandable to a product owner, not only to an engineer.

## Stable filename and validator rules

Continue the Phase 4A convention:

```text
<full-story-id>-<descriptive-slug>.md
```

The validator must:

- match story files by exact full story-ID prefix;
- reject duplicate registry IDs;
- reject duplicate story-file ID prefixes;
- reject ambiguous prefix matches;
- reject registry rows without files;
- reject files without registry rows;
- validate outcome → capability → feature → story references;
- preserve compatibility with the two Phase 4A pilot stories.

Do not weaken validation to accommodate malformed records.

## Registry readability

After migration, check that the flat registries remain navigable.

Where necessary, improve schema-preserving presentation only, such as:

- deterministic sorting;
- grouping comments/headings by capability;
- concise titles;
- consistent evidence-confidence and status values.

Do not change approved source-of-truth ownership or hierarchy semantics.

## Reconciliation

Create a batch reconciliation record that proves:

- every selected item appears exactly once in `STORY-REGISTRY.md`;
- every selected item has exactly one story file;
- every story references valid feature, capability, and outcome IDs;
- no excluded item was migrated;
- the two Phase 4A stories remain unchanged except for strictly necessary validator-compatible mechanical amendments;
- migrated count matches selected count.

## Programme-control updates

Update programme-control files accurately to show:

- Phase 4A pilot complete;
- Phase 4B authorised and complete if all gates pass;
- wider Phase 4 still not authorised;
- current human gate is approval of the next migration scope only;
- all exclusions and newly discovered ambiguities remain visible;
- no claim that all confirmed stories have been migrated unless this batch genuinely completes them.

Record the human authorisation as the next decision ID in `decisions.md` without renumbering prior decisions.

## Run record

Create:

```text
docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md
```

Include:

- start state;
- authorisation decision;
- batch-selection rationale;
- selected capability area;
- included and excluded story IDs;
- files inspected;
- files changed;
- hierarchy rows created and reused;
- validator changes, if any;
- validation commands and results;
- reconciliation result;
- executor findings;
- critic verdict;
- amendments made after criticism;
- commit SHA(s);
- outstanding items;
- next permitted action.

## Independent critic gate

After executor outputs exist, run a separate read-only critic agent.

The critic must assess:

1. whether the batch is limited to one capability area;
2. whether every migrated story was `confirmed` before migration;
3. whether mandatory exclusions were respected;
4. whether the story count remains within the authorised maximum of 20;
5. whether IDs, filenames, rows, hierarchy references, and evidence links agree;
6. whether no historical source was rewritten;
7. whether no strongly inferred, tentative, disputed, backlog, or unresolved-compliance item slipped into the batch;
8. whether Phase 4A records remain valid;
9. whether validator behaviour is strict and unambiguous;
10. whether programme state stops at the next human gate;
11. whether the run record is complete and truthful;
12. whether the allowed write scope was respected.

Write the review to:

```text
docs/programmes/product-traceability/critic-review-phase-4b-confirmed-batch.md
```

Use:

```text
Verdict:
approve / approve-with-amendments / reject

Critical issues:
...

Evidence or classification discrepancies:
...

Hierarchy or registry defects:
...

Guardrail gaps:
...

Required amendments:
...

Human decisions still required:
...
```

If amendments are required, the executor may apply only in-scope amendments. Re-review is required unless the critic explicitly says a particular mechanical amendment does not require it.

## Validation commands

At minimum run:

```bash
python3 docs/product/validate_registry.py
git diff --check
git status --short
```

Also run targeted checks that confirm:

- selected story count is between 1 and 20;
- every selected story confidence is `confirmed`;
- no excluded confidence/status appears among newly migrated rows;
- every new story filename begins with the exact full story ID;
- no ambiguous filename prefix exists;
- every new story row resolves to one file;
- every new feature resolves to one capability;
- every new capability resolves to one outcome;
- existing Phase 4A story rows and files still validate;
- no forbidden path changed in this run.

Pre-existing unrelated working-tree changes must be identified and left untouched.

## Commit and push

After the critic gate passes:

1. Commit only authorised files.
2. Push to `origin/uat`.
3. Record the actual commit SHA(s) in the run record, using a follow-up commit only if required for honest SHA backfill.

Suggested commit message:

```text
docs: migrate confirmed product stories batch
```

## Stop conditions

Stop and escalate if:

- no coherent confirmed-only capability batch can be formed;
- more than 20 stories would be required to preserve the capability coherently;
- source evidence materially contradicts the discovery classification;
- the hierarchy model cannot represent the selected items without changing approved governance;
- a forbidden path would need modification;
- validator correctness would need to be weakened;
- the critic rejects the batch after permitted amendments.

## Final report

Report once, at the end:

```text
Product traceability Phase 4B confirmed-story batch complete

Capability area:
<name/id>

Stories migrated:
<count and IDs>

Hierarchy rows:
Outcomes: <created/reused counts>
Capabilities: <created/reused counts>
Features: <created/reused counts>
Stories: <new total and batch count>

Validator:
<result>

Reconciliation:
<result>

Critic verdict:
<verdict>

Files changed:
<paths>

Commit SHA(s):
<sha(s)>

Current programme state:
Phase 4B complete; wider migration not authorised

Next permitted action:
Human review and explicit authorisation of the next migration scope only
```
