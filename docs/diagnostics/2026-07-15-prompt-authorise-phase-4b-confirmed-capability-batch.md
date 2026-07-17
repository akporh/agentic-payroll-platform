# Casper Prompt — Authorise and Run Product Traceability Phase 4B Confirmed-Story Batch

## Objective

Authorise and execute a bounded Phase 4B historical-migration batch for **confirmed stories only**, limited to **one capability area** and approximately **10–20 stories**.

This phase must also improve registry readability before scale migration by adding human-readable parent names alongside stable parent IDs.

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
- all files under `docs/product/`

The Phase 4A conventions remain authoritative unless this prompt explicitly changes them.

## Human authorisation

This prompt authorises:

- Phase 4B only;
- one capability-area batch only;
- confirmed stories only;
- approximately 10–20 stories, never more than 20;
- the human-readable registry schema amendment defined below;
- writes limited to `docs/product/` and approved programme-control files;
- an independent critic gate;
- stopping before any further migration batch.

It does not authorise the remainder of Phase 4.

## Mandatory human-readable registry amendment

Stable IDs remain the authoritative machine references. Human-readable names are required as display fields so a reviewer can understand each relationship without opening another registry.

Update the registry schemas and existing Phase 4A rows as follows.

### `CAPABILITIES.md`

Each capability row must contain at least:

```text
Capability ID | Capability name | Outcome ID | Outcome name | ...
```

### `FEATURES.md`

Each feature row must contain at least:

```text
Feature ID | Feature name | Capability ID | Capability name | ...
```

### `STORY-REGISTRY.md`

Each story row must contain at least:

```text
Story ID | Story title | Feature ID | Feature name | ...
```

Where useful and consistent with the current schema, the story registry may also display capability and outcome names, but this is optional. Do not duplicate long descriptions.

### Authority rule

- IDs are authoritative for identity and relationships.
- Names are human-readable display fields.
- A displayed parent name must exactly match the current name held in the authoritative parent registry.
- A parent rename must update all duplicated display-name fields in the same controlled change.
- Do not infer hierarchy from names; always resolve by ID.

### Validator requirements for names

Extend `docs/product/validate_registry.py` so it:

- confirms every capability's `Outcome ID` exists;
- confirms its displayed `Outcome name` exactly matches that outcome's authoritative name;
- confirms every feature's `Capability ID` exists;
- confirms its displayed `Capability name` exactly matches that capability's authoritative name;
- confirms every story's `Feature ID` exists;
- confirms its displayed `Feature name` exactly matches that feature's authoritative name;
- rejects missing display names;
- rejects stale or mismatched display names;
- preserves all existing Phase 4A validation behaviour.

Update `README.md` and relevant schema notes/templates so this ID-plus-name convention is explicit.

## Batch-selection rule

Select exactly one capability area using this preference order:

1. a capability area containing 10–20 confirmed items;
2. otherwise, the capability area closest to that range without exceeding 20;
3. otherwise, a coherent confirmed-only subset of no more than 20 items from one capability area.

Before migration, record:

- capability area selected;
- confirmed candidate items found;
- included items;
- excluded items and reasons;
- expected outcomes, capabilities, and features to create or reuse;
- expected story count.

Do not select unrelated items merely to hit a target.

## Mandatory exclusions

Exclude anything that is:

- strongly inferred;
- tentative;
- requires human classification;
- backlog or not delivered;
- related to the unresolved `PH_OT is_pensionable` question;
- the disputed Gate 4 item;
- contradicted or insufficiently supported during direct inspection;
- dependent on rewriting historical source files.

If direct inspection weakens a supposedly confirmed item, exclude and document it. Do not silently downgrade and migrate it.

## Allowed write scope

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

All other paths are forbidden for writes. Historical evidence is read-only.

## Migration requirements

For every migrated story:

1. Preserve its stable story ID.
2. Use a descriptive filename beginning with the full stable ID.
3. Add exactly one matching row to `STORY-REGISTRY.md`.
4. Create or reuse the correct outcome, capability, and feature rows.
5. Preserve `Outcome → Capability → Feature → Story`.
6. Record delivery status and evidence confidence separately.
7. Link to original evidence rather than duplicating historical acceptance criteria.
8. Record delivery history, including sprint/track and contribution.
9. Record decision references where applicable.
10. Record dependencies only when supported by evidence.
11. Do not invent actors, outcomes, dependencies, or dates.
12. Use product-owner-readable titles.
13. Populate both parent ID and parent display name in every applicable registry row.

## Stable filename rules

Use:

```text
<full-story-id>-<descriptive-slug>.md
```

The validator must:

- match by exact full story-ID prefix;
- reject duplicate registry IDs;
- reject duplicate story-file ID prefixes;
- reject ambiguous prefix matches;
- reject registry rows without files;
- reject files without registry rows;
- validate all hierarchy references;
- validate all duplicated parent display names;
- preserve compatibility with both Phase 4A stories.

Do not weaken validation to accommodate malformed records.

## Registry readability

Keep registries navigable using:

- stable deterministic sorting;
- concise titles and names;
- consistent status and confidence values;
- IDs and names shown together;
- optional grouping headings where they do not interfere with parsing.

Do not change hierarchy semantics or source-of-truth ownership.

## Reconciliation

Create a batch reconciliation record proving:

- every selected item appears exactly once in `STORY-REGISTRY.md`;
- every selected item has exactly one story file;
- every story resolves to valid feature, capability, and outcome IDs;
- every displayed parent name matches its authoritative parent registry;
- no excluded item was migrated;
- the two Phase 4A stories remain valid after the schema amendment;
- migrated count equals selected count.

## Programme-control updates

Update programme files to show:

- Phase 4A complete;
- Phase 4B authorised and complete if all gates pass;
- wider Phase 4 not authorised;
- current gate is approval of the next migration scope;
- exclusions and ambiguities remain visible;
- the human-readable registry amendment was adopted during Phase 4B;
- no claim that all confirmed stories are migrated unless true.

Record the authorisation as the next decision ID without renumbering earlier decisions.

## Run record

Create:

```text
docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md
```

Include:

- start state;
- authorisation decision;
- schema amendment and rationale;
- batch-selection rationale;
- selected capability area;
- included and excluded story IDs;
- files inspected and changed;
- hierarchy rows created and reused;
- validator changes;
- validation and reconciliation results;
- executor findings;
- critic verdict and amendments;
- commit SHA(s);
- outstanding items;
- next permitted action.

## Independent critic gate

Run a separate read-only critic after executor outputs exist.

The critic must assess:

1. one capability area only;
2. confirmed stories only;
3. mandatory exclusions respected;
4. no more than 20 migrated stories;
5. IDs, filenames, rows, hierarchy, evidence links, and display names agree;
6. every duplicated parent name exactly matches its authoritative parent name;
7. IDs remain authoritative and names are display-only;
8. no historical source was rewritten;
9. Phase 4A records still validate;
10. validator behaviour remains strict and rejects stale names and ambiguous prefixes;
11. programme state stops at the next human gate;
12. run record is complete and truthful;
13. allowed write scope was respected.

Write:

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

Hierarchy, name-display, or registry defects:
...

Guardrail gaps:
...

Required amendments:
...

Human decisions still required:
...
```

Re-review is required after amendments unless the critic explicitly waives it for a purely mechanical correction.

## Validation

At minimum run:

```bash
python3 docs/product/validate_registry.py
git diff --check
git status --short
```

Also confirm:

- selected count is 1–20;
- every selected story was confirmed before migration;
- no excluded confidence/status appears among new rows;
- every story filename begins with the full exact ID;
- no ambiguous prefix exists;
- every hierarchy ID resolves;
- every duplicated parent name matches the authoritative parent name;
- existing Phase 4A records still pass;
- no forbidden path changed.

Identify and leave untouched all pre-existing unrelated working-tree changes.

## Commit and push

After critic approval:

1. Commit only authorised files.
2. Push to `origin/uat`.
3. Record actual commit SHA(s), using a follow-up SHA-backfill commit only when necessary.

Suggested commit message:

```text
docs: migrate confirmed product stories batch
```

## Stop conditions

Stop and escalate if:

- no coherent confirmed-only batch can be formed;
- more than 20 stories are required for coherence;
- evidence contradicts discovery classification;
- the hierarchy cannot represent the batch without changing approved governance;
- parent names cannot be derived unambiguously from authoritative registries;
- a forbidden path would need modification;
- validator strictness would need weakening;
- the critic rejects the batch after permitted amendments.

## Final report

Report once at the end:

```text
Product traceability Phase 4B confirmed-story batch complete

Capability area:
<name/id>

Stories migrated:
<count and IDs>

Human-readable registry amendment:
<summary and validator result>

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
