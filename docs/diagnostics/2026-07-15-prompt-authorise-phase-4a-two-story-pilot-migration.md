# Casper Prompt — Authorise and Execute Product Traceability Phase 4A Pilot Migration

## Objective

Record explicit human authorisation for a bounded Phase 4A pilot, migrate exactly two proven ICM stories into the approved `docs/product/` hierarchy, run the product registry validator, run an independent critic review, and stop before any wider historical migration.

This prompt authorises **only** the two-story pilot described below. It does not authorise migration of the remaining reconstructed items.

## Human authorisation

The human has approved:

- Phase 4A — two-story pilot migration only.
- Pilot sprint/story sources:
  - `aud-q1-trace-source`
  - `sec-s7-timesheet-upload-guard`

Record this as a new decision in:

```text
docs/programmes/product-traceability/decisions.md
```

The decision must state clearly that Phase 4 as a whole is not yet authorised; only this bounded pilot is authorised.

## Governing inputs

Read and obey:

- `docs/programmes/product-traceability/PROGRAMME.md`
- `docs/programmes/product-traceability/POLICY.md`
- `docs/programmes/product-traceability/PHASES.md`
- `docs/programmes/product-traceability/state.md`
- `docs/programmes/product-traceability/decisions.md`
- `docs/product/README.md`
- `docs/product/OUTCOMES.md`
- `docs/product/CAPABILITIES.md`
- `docs/product/FEATURES.md`
- `docs/product/STORY-REGISTRY.md`
- `docs/product/stories/TEMPLATE.md`
- `docs/product/validate_registry.py`
- `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`

Use the two completed ICM sprint workspaces and their linked evidence as authoritative delivery evidence:

- `docs/sprints/aud-q1-trace-source/`
- `docs/sprints/sec-s7-timesheet-upload-guard/`

Also inspect their linked audit, verification, security, retrospective, implementation and commit evidence where referenced.

## Allowed write scope

You may modify or create files only under:

```text
docs/product/
docs/programmes/product-traceability/
```

## Forbidden write scope

Do not modify:

```text
docs/ROADMAP.md
docs/stories/
docs/sprints/
docs/audit/
docs/security/
docs/test-reports/
docs/retro-reports/
docs/audit-program/
docs/agentic-architecture-review/
backend/
frontend/
migrations/
~/.claude/
```

All paths not expressly allowed are forbidden for writes.

## Pilot migration rules

Migrate exactly two product story records, one corresponding to each authorised pilot.

Do not migrate any other historical item.

Each migrated story must include:

- stable story ID;
- concise title;
- classification;
- delivery status;
- evidence confidence;
- actor and problem addressed;
- delivered behaviour;
- outcome ID;
- capability ID;
- feature ID;
- source requirement references;
- sprint reference;
- delivery history;
- evidence links;
- implementation commit reference(s);
- decision references where applicable;
- dependencies, or an explicit empty value;
- unresolved questions, or an explicit none value.

Use the adopted source-of-truth rules in `docs/product/README.md`:

- summarise and link to original evidence;
- do not duplicate full historical acceptance criteria;
- do not rewrite historical sprint or story records;
- preserve stable IDs independently of future hierarchy reclassification.

## Hierarchy creation rules

Create only the minimum outcome, capability and feature rows required to place the two pilot stories coherently.

Avoid artificial over-fragmentation.

Where both stories genuinely share an outcome or capability, reuse the same ID. Where they represent materially different product intent, use separate IDs.

Do not create speculative hierarchy entries for future stories.

Every hierarchy choice must be supported by the story's actual product intent and evidence, not merely by its implementation file location.

## Registry and story-file updates

Update:

```text
docs/product/OUTCOMES.md
docs/product/CAPABILITIES.md
docs/product/FEATURES.md
docs/product/STORY-REGISTRY.md
```

Create exactly two story files under:

```text
docs/product/stories/
```

Do not edit `stories/TEMPLATE.md` unless the pilot proves a genuine schema defect. If a template change is necessary, record the reason explicitly in the run record and critic review.

## Product-governance checks

The pilot must prove that the product layer carries the intended ICM disciplines:

1. **Stable IDs** — all hierarchy and story IDs are unique and durable.
2. **Clear source-of-truth ownership** — product intent/status lives in `docs/product/`; execution state and detailed evidence remain in the original sprint/evidence files.
3. **Explicit state** — delivery status and evidence confidence are separate fields.
4. **Evidence links** — every delivered claim resolves to repository evidence.
5. **Decision traceability** — relevant decisions are linked by ID.
6. **Dependency visibility** — dependencies are explicit, including none.
7. **Append-only delivery history** — each story records the pilot sprint contribution without overwriting original history.
8. **Human-gate discipline** — successful pilot completion must not auto-authorise broader migration.

## Programme-control updates

Update programme control files so they accurately show:

- Phase 3 complete;
- Phase 4A pilot authorised and, when complete, completed;
- exactly two stories migrated;
- full Phase 4 historical migration not authorised;
- next gate is human review of pilot quality and explicit authorisation of any broader migration batch.

Update at minimum where necessary:

- `state.md`
- `PHASES.md`
- `decisions.md`
- `phase-inputs.yaml`
- `exceptions.md`

Preserve prior history; do not rewrite earlier phase records as though the pilot had already existed.

## Run record

Create:

```text
docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md
```

Include:

- start state;
- authorisation decision;
- source files inspected;
- hierarchy choices and rationale;
- files created/modified;
- validator output;
- executor findings;
- critic verdict;
- amendments made after criticism;
- commit SHA(s);
- outstanding questions;
- next permitted action.

## Independent critic gate

After executor artefacts exist, run a separate read-only critic agent.

The critic must assess:

1. exactly two stories were migrated;
2. no unrelated historical item was added;
3. hierarchy assignments reflect product intent rather than code structure;
4. IDs are unique and stable;
5. delivery status and evidence confidence are distinct and supported;
6. source-of-truth boundaries were preserved;
7. evidence and commit references resolve;
8. registry rows and story files agree;
9. the validator passes;
10. no forbidden historical or production file was modified;
11. programme controls do not authorise broader Phase 4 migration;
12. the pilot genuinely tests all eight product-governance disciplines listed above.

Write the critic review to:

```text
docs/programmes/product-traceability/critic-review-phase-4a-pilot.md
```

Use:

```text
Verdict:
approve / approve-with-amendments / reject

Critical issues:
...

Hierarchy issues:
...

Traceability gaps:
...

Guardrail gaps:
...

Required amendments:
...

Human decisions still required:
...
```

If amendments are required, the executor may apply only amendments within the authorised scope. Re-run validation and critic review unless the critic explicitly states a purely mechanical amendment needs no re-review.

## Required validation

Run at minimum:

```bash
python3 docs/product/validate_registry.py
git diff --check
git status --short
find docs/product -maxdepth 2 -type f | sort
```

Also verify:

- exactly two non-template story files exist;
- `STORY-REGISTRY.md` has exactly two content rows;
- all referenced outcome/capability/feature IDs exist;
- every story file has one matching registry row;
- every registry row has one matching story file;
- all evidence paths resolve;
- no forbidden path was modified by this run;
- pre-existing unrelated working-tree changes were left untouched.

## Commit and push

After the critic gate passes:

1. Commit only authorised pilot files.
2. Push to `origin/uat`.
3. Record the resulting commit SHA accurately in the run record or an explicit follow-up note.

Suggested commit message:

```text
docs: pilot product traceability migration with two ICM stories
```

## Stop condition

Stop after the two-story pilot is complete and critic-approved.

Do not migrate a third story.
Do not begin bulk migration.
Do not authorise a later batch.

## Final report

Report once at the end:

```text
Product traceability Phase 4A pilot complete

Stories migrated:
- <story ID> — aud-q1-trace-source
- <story ID> — sec-s7-timesheet-upload-guard

Hierarchy rows created:
Outcomes: <count>
Capabilities: <count>
Features: <count>
Stories: 2

Validator:
<result>

Critic verdict:
<verdict>

Files changed:
<paths>

Commit SHA:
<sha>

Current programme state:
Phase 4A pilot complete; wider Phase 4 migration not authorised

Next permitted action:
Human review of the pilot and explicit authorisation of the next migration scope only
```