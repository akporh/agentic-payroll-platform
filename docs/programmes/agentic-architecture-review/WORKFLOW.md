# Workflow

## Stage sequence

Stages run in strict numbered order. A stage is a unit of investigation, not delivery.

| # | Stage | Folder |
|---|---|---|
| 01 | Current Operating Model | `01-current-operating-model` |
| 02 | Product Thesis | `02-product-thesis` |
| 03 | Agent Portfolio | `03-agent-portfolio` |
| 04 | Outcome Discovery | `04-outcome-discovery` |
| 05 | Platform Readiness | `05-platform-readiness` |
| 06 | Compliance & Controls | `06-compliance-controls` |
| 07 | Security & Identity | `07-security-identity` |
| 08 | Technical Architecture | `08-technical-architecture` |
| 09 | Human Experience | `09-human-experience` |
| 10 | Evaluation & Assurance | `10-evaluation-assurance` |
| 11 | Commercial & Product Strategy | `11-commercial-product-strategy` |
| 12 | Target Direction | `12-target-direction` |
| 13 | Approved Roadmap | `13-approved-roadmap` |

Stages 01–11 are diagnostic. Stage 12 synthesises confirmed findings into target direction. Stage 13 produces the roadmap and always requires final human approval.

## Per-stage contents

Every stage folder contains:

- `CONTEXT.md` — populated execution contract
- `findings.md` — draft, confirmed and parked/rejected findings
- `decisions.md` — material human decisions made during the stage
- `evidence/` — captured evidence where needed
- `outputs/` — stage deliverables, handoffs and `critic-review.md`

Authoritative repository code, tests, migrations, git history and confirmed prior-stage findings may be cited directly. Evidence snapshots should be captured under `evidence/` when the source may change, the extract is needed for reproducibility, or the finding depends on a query/log rather than a stable repository location.

## Stage execution lifecycle

1. **eligible** — predecessor is closed and no blocking decision prevents opening.
2. **context-ready** — `CONTEXT.md` is fully populated and controller-validated.
3. **in-progress** — primary executor performs the investigation.
4. **awaiting-critic** — required outputs exist and the independent critic runs.
5. **revision-required** — critic returned `REVISE`; executor applies named corrections.
6. **awaiting-human-decision** — critic passed but a material decision blocks progression.
7. **closed** — critic passed, decisions are resolved or non-blocking/forwarded, state and handoffs are complete.

## Automatic stage progression

A stage may open automatically when:

- the prior stage is closed
- its context is populated from confirmed evidence and binding decisions
- no blocking human decision or stop condition exists

A stage may close automatically when:

- required outputs exist
- findings informing later work are confirmed, parked or rejected
- evidence meets `_core/EVIDENCE-STANDARD.md`
- current implementation, intended design and gap remain separated
- the critic returns `PASS`
- no blocking human decision remains
- handoffs and `review-state.md` are consistent

After automatic closure, the controller may populate and open the next stage without a human prompt.

## Human gating

Human approval is required only for:

- genuine material decisions classified under `POLICY.md`
- unresolved executor/critic disagreement
- changes to binding review/programme policy
- final Stage 13 roadmap approval
- Phase 2 or Phase 3 authorisation

Non-blocking questions are recorded in `decision-queue.md` and forwarded to the stage that owns them.

## Independent critic

Every stage from the adoption of D-003 onward must receive a separate critic review under `CRITIC.md`.

The critic returns `PASS`, `REVISE` or `STOP`. It reviews evidence and outputs, not merely the prompt. It cannot silently rewrite executor findings.

## Finding lifecycle

1. **Draft** — observation/hypothesis; not citable downstream.
2. **Confirmed** — meets evidence standard and is citable downstream.
3. **Parked / Rejected** — explicitly closed with a reason.

## Current implementation / intended design / gap separation

Every system-behaviour finding records separately:

- current implementation
- intended design
- identified gap

## Production code

This programme does not modify production code, configuration or data. Recommendations become future roadmap/build-order inputs for ICM sprint delivery.

## Next action

Read `review-state.md` and `decision-queue.md`, then execute the next eligible action under `RUNBOOK.md`.