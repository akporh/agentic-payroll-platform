# Casper Prompt — Record Product-Traceability Decisions and Close Phase 2

## Objective

Record the human decisions made for DP-01 through DP-07, complete the `hierarchy approval` phase, run an independent critic review of the decision recording, and stop at the Phase 3 human gate.

This prompt does **not** authorise creation of `docs/product/`, historical migration, production-code changes, sprint-workflow changes, or investigation/remediation of the two separately identified gaps.

## Authoritative human decisions

Record these decisions exactly:

- **DP-01 — Option A:** Retain the current 148-item story/feature-line granularity. Use one record per meaningful delivered product item; do not collapse to one item per sprint and do not split to one item per acceptance criterion.
- **DP-02 — Option A:** Use flat product registries and a flat `stories/` folder. Relationships between outcomes, capabilities, features, and stories will be maintained through stable IDs and metadata, not deeply nested folders.
- **DP-03 — Option A:** Adopt the proposed source-of-truth rules as written.
- **DP-04 — Option B:** Treat the `PH_OT is_pensionable` deferral as still open and escalate it as a potential compliance risk outside this programme.
- **DP-05 — Option A:** Classify all five unresolved items as backlog / not delivered unless newer evidence is provided.
- **DP-06 — Option C:** Run a targeted investigation to resolve the Gate 4 status contradiction before treating either source as authoritative.
- **DP-07 — Option A:** Authorise and complete Phase 2 (`hierarchy approval`) using the decisions above.

## Programme controls

Read and obey:

- `docs/programmes/product-traceability/PROGRAMME.md`
- `docs/programmes/product-traceability/POLICY.md`
- `docs/programmes/product-traceability/PHASES.md`
- `docs/programmes/product-traceability/state.md`
- `docs/programmes/product-traceability/decision-pack.md`
- `docs/programmes/product-traceability/critic-review.md`
- `docs/programmes/product-traceability/phase-inputs.yaml`
- `docs/programmes/product-traceability/decisions.md`

The human decisions in this prompt are authoritative and supersede the unresolved status of DP-01 through DP-07 in the current programme files.

## Allowed write scope

You may modify or create files only under:

```text
docs/programmes/product-traceability/
docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md
```

The prompt file itself should normally remain unchanged.

## Forbidden write scope

Do not modify or create anything under:

```text
docs/product/
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

All paths not expressly allowed are forbidden for writes.

## Executor tasks

### 1. Record the decisions

Update `docs/programmes/product-traceability/decisions.md` with explicit decision records for DP-01 through DP-07.

Each record must include:

- decision ID;
- selected option;
- exact decision;
- rationale, kept concise;
- date;
- effect on later phases;
- any follow-up work that remains outside this programme.

Do not reinterpret or weaken the decisions.

### 2. Close Phase 2 accurately

Update programme control files so they accurately show:

- Phase 1 `discovery`: complete;
- Phase 2 `hierarchy approval`: authorised and complete;
- Phase 3 `structure implementation`: not authorised;
- current human gate: approval of Phase 3 scope and controls;
- no `docs/product/` files have been created;
- DP-04 and DP-06 have follow-up investigations required outside the current phase.

Update at minimum, where necessary:

- `state.md`
- `PHASES.md`
- `phase-inputs.yaml`
- `decision-pack.md`
- `exceptions.md`

Do not erase the original questions or recommendations from `decision-pack.md`. Mark them resolved or add a clear resolution section so the historical decision trail remains visible.

### 3. Prepare Phase 3 decision inputs, not a free-form next prompt

Create or update a factual Phase 3 input section/file under `docs/programmes/product-traceability/` containing only:

- proposed Phase 3 ID: `structure-implementation`;
- approved hierarchy: `Outcome → Capability → Feature → Story`;
- approved repository model: flat registries plus flat `stories/` folder;
- approved source-of-truth rules;
- proposed allowed path: new `docs/product/` tree only;
- proposed outputs: empty hierarchy/registry scaffold, templates, and validation artefacts;
- proposed forbidden paths;
- proposed validation commands;
- unresolved Phase 3 authorisation decision.

Do not author a free-form continuation prompt and do not grant Phase 3 permission.

### 4. Create the Phase 2 run record

Create:

```text
docs/programmes/product-traceability/runs/hierarchy-approval-run-001.md
```

Include:

- start state;
- human decisions received;
- files changed;
- validation commands and results;
- executor summary;
- critic verdict;
- amendments made after criticism;
- commit SHA once available, or an honest pre-commit statement followed by an appended post-commit note if required;
- outstanding follow-ups;
- next permitted action.

## Independent critic gate

After the executor artefacts exist, run a separate read-only critic agent.

The critic must not edit executor files and must assess:

1. whether DP-01 through DP-07 were recorded exactly;
2. whether recommendations were kept distinct from approvals;
3. whether Phase 2 was closed without accidentally authorising Phase 3;
4. whether `docs/product/` remains uncreated;
5. whether source-of-truth rules match the approved proposal;
6. whether DP-04 and DP-06 remain visible as follow-up investigations rather than being silently treated as resolved;
7. whether control files agree on current phase and gate;
8. whether the allowed write scope was respected;
9. whether the Phase 3 inputs are factual-only and grant no permissions.

Write the critic result to:

```text
docs/programmes/product-traceability/critic-review-phase-2.md
```

Use this structure:

```text
Verdict:
approve / approve-with-amendments / reject

Critical issues:
...

Guardrail gaps:
...

Decision-recording discrepancies:
...

Required amendments:
...

Human decisions still required:
...
```

If amendments are required, the executor may apply only amendments within the allowed scope, after which the critic must re-review unless the requested amendment is purely mechanical and the critic explicitly states re-review is unnecessary.

## Validation

At minimum run:

```bash
git diff --check
git status --short
find docs/programmes/product-traceability -maxdepth 2 -type f | sort
test ! -e docs/product
```

Also verify mechanically or by direct inspection that:

- DP-01 through DP-07 each appear once as resolved decisions;
- all control files agree that Phase 2 is complete;
- Phase 3 remains unauthorised;
- no forbidden file was modified by this run;
- the critic reviewed the final executor state.

Pre-existing unrelated working-tree changes must be identified and left untouched.

## Commit and push

After the critic gate passes:

1. Commit only authorised files from this run.
2. Push to `origin/uat`.
3. Record the resulting commit SHA accurately in the run record or in a follow-up note if the run record itself was part of that commit.

Suggested commit message:

```text
docs: record product traceability hierarchy decisions
```

## Stop condition

Stop after Phase 2 is recorded and critic-approved.

Do not begin Phase 3.

## Final report

Report once, at the end:

```text
Product traceability Phase 2 complete

Decisions recorded:
DP-01 A
DP-02 A
DP-03 A
DP-04 B
DP-05 A
DP-06 C
DP-07 A

Critic verdict:
<verdict>

Current programme state:
Phase 2 complete; Phase 3 awaiting human authorisation

Files changed:
<paths>

Follow-up investigations:
- PH_OT is_pensionable
- Gate 4 completion contradiction

Commit SHA:
<sha>

Next permitted action:
Human review and explicit authorisation of Phase 3 scope only
```