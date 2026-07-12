# Stage 03 — Agent Portfolio Review Prompt

Begin Stage 03 only:

`docs/agentic-architecture-review/03-agent-portfolio/`

## Objective

Review the proposed agent and tool portfolio in detail and determine which capabilities should be:

- retained
- revised
- merged
- split
- deferred
- blocked pending prerequisites
- rejected
- reclassified as deterministic platform work rather than agent work

The output must define a coherent portfolio of payroll capabilities, not merely critique the labels in the existing architecture document.

Do not design the final target architecture or roadmap in this stage.

## Before starting

Read:

- `CLAUDE.md`
- `docs/agentic-architecture-review/README.md`
- `docs/agentic-architecture-review/WORKFLOW.md`
- `docs/agentic-architecture-review/review-state.md`
- all files under `docs/agentic-architecture-review/_core/`
- `docs/agentic-architecture-review/_inputs/source-register.md`
- all Stage 01 findings and outputs
- all Stage 02 findings, decisions and outputs
- especially:
  - `02-product-thesis/outputs/stage-03-handoff.md`
  - `02-product-thesis/outputs/capability-classification-matrix.md`
  - `02-product-thesis/outputs/deterministic-ai-boundary.md`
  - `02-product-thesis/outputs/non-negotiable-product-principles.md`
- the current `docs/architecture/agent-layer-architecture.html`
- current code only where needed to verify whether a proposed agent/tool can be grounded in existing platform capabilities

Confirm:

- Stage 02 is complete
- Stage 03 is eligible to begin
- no later stage is in progress
- D-02-01 through D-02-04 are binding and must not be re-litigated

Then:

- update Stage 03 status to `in-progress`
- populate Stage 03 `CONTEXT.md` with the final scope, questions, explicit exclusions, inputs and completion criteria
- update `review-state.md` next action to “Complete Stage 03 agent portfolio review”

## Binding decisions inherited from Stage 02

Apply these as gates, not discussion points:

1. The source architecture document remains unapproved and under revision.
2. `get_reconciliation` and any tool touching `payroll_reconciliation` are blocked until repository-level workspace scoping is fixed; tool-layer enforcement is additionally mandatory.
3. Historical payroll explanation, reconciliation investigation and trace investigation are blocked until F-01-27, F-01-29 and F-01-38 are resolved.
4. Statutory-rule change management is a separate deterministic capability. Y1 may detect, compare and propose only; it may not author, execute or deploy migrations.

## Portfolio scope

Review all proposed tracks and capabilities, including:

- Track P — identity/authentication foundations
- Track V — event, tool and notification foundations
- Track W — operator chat modes
- Track X — preparation, reconciliation, trace and proactive workflows
- Track Y — compliance monitoring and onboarding assistance
- structured confirmation and pending actions
- tool definitions supporting those capabilities
- any agent-like capability implied elsewhere in the architecture or product documents

Where useful, review at capability level rather than accepting the existing track grouping.

## Required assessment for every capability

For each proposed capability record:

- capability name
- current track and label
- target user
- user problem
- desired outcome
- trigger
- required authoritative data
- required tools
- current-state versus historical-state dependency
- deterministic detection or computation required
- LLM role, if any
- permitted reads
- permitted writes
- prohibited actions
- human decision or approval required
- evidence shown to the operator
- failure modes
- platform prerequisites
- compliance/control prerequisites
- evaluation requirement
- measurable product outcome
- portfolio decision:
  - keep
  - revise
  - merge
  - split
  - defer
  - block
  - reject
  - reclassify as deterministic platform capability
- rationale and confidence

Do not treat the architecture document's existing agent names as fixed product boundaries.

## Required investigations

### 1. Agent boundaries and overlap

Assess overlap between:

- Navigation Guide and State Explainer
- State Explainer and Trace Agent
- Action Planner and Prep Agent
- Prep Agent and deterministic readiness validation
- Reconciliation Investigation and deterministic reconciliation diagnostics
- Trace Agent and the existing run-results/timeline UI
- Compliance Monitoring and statutory-rule administration
- Onboarding Agent and deterministic import validation/mapping UI

Determine whether any agents should instead be:

- modes of one operator assistant
- deterministic services surfaced through structured UI
- event-triggered workflows without an LLM
- analytics services with optional narration
- independent bounded agents

### 2. Deterministic versus probabilistic responsibility

Apply Stage 02 Principle 9 actively.

At minimum:

- Prep checks for missing timesheets, missing salary definitions and contract expiry must remain deterministic.
- Input anomaly detection should be deterministic/statistical first; the LLM may narrate or prioritise results.
- Reconciliation causal diff must be deterministic when eventually unblocked.
- Trace explanation may only use values already present in structured trace data.
- State explanation must retrieve individual facts rather than invent a reason.

Flag every capability where the current architecture risks asking an LLM to perform deterministic computation.

### 3. Track W launch boundary

Define a safe initial Track W portfolio limited to current-state assistance.

Explicitly separate:

- current-state navigation and explanation — eligible for consideration
- historical payroll-outcome explanation — blocked by D-02-03

For each allowed Track W mode, identify the exact facts and tools required to answer safely.

Define refusal or limitation behaviour when:

- facts are missing
- the requested answer requires historical reconstruction
- the employee/run is outside the user's workspace
- the tool result is ambiguous
- the relevant trace is null

### 4. Track X portfolio

Review each Track X capability independently.

For Prep:

- split deterministic readiness checks from optional AI narration/prioritisation
- assess whether an “agent” is needed at all or whether this is primarily a readiness service plus notification/work queue

For Reconciliation and Trace:

- classify them as blocked under D-02-03
- document their future design constraints without treating them as launch-ready
- ensure `get_reconciliation` remains separately blocked under D-02-02

For proactive/event-triggered behaviour:

- distinguish event automation from agent reasoning
- specify where an LLM adds value after the deterministic trigger fires

For write-capable behaviour:

- do not fully design the confirmation protocol
- record required Stage 08 specification questions, including expiry, conflicts, idempotency and state-transition invalidation

### 5. Track Y portfolio

For Compliance Monitoring:

- retain only detection, evidence comparison, impact summary and proposal drafting
- prohibit migration authoring/execution/deployment
- separate statutory-rule change management into its own deterministic capability
- identify external-source trust, freshness and provenance dependencies for Stages 06 and 08

For Onboarding Assistance:

- assess where AI is useful for ambiguous spreadsheet/header interpretation
- retain deterministic schema validation, tenant validation, rule validation and dry-run verification outside the LLM
- flag the dry-run mechanism as requiring Stage 08 definition
- determine whether mapping assistance, configuration proposal and parallel-run explanation should be one capability or separate bounded steps

### 6. Tool portfolio

Review every proposed tool contract.

For each tool determine:

- whether it should exist
- whether it is read-only or mutating
- workspace-scoping requirement
- source-of-truth table/service
- whether it returns facts, conclusions or both
- whether conclusions should instead be computed deterministically before returning
- maximum data exposure
- PII handling
- error/refusal behaviour
- required audit record
- blocked prerequisites

Require independent workspace ownership enforcement for every tool.

Do not assume repository functions are already correctly scoped.

### 7. UX/product surface

For each retained capability determine whether the primary experience should be:

- chat
- structured dashboard
- readiness panel
- exception queue
- notification
- investigation workspace
- comparison view
- approval panel
- configuration-mapping workspace
- evidence drawer

Chat should not be selected by default.

### 8. Portfolio coherence

Assess whether the proposed portfolio forms a coherent operating model across:

- preparation
- exception detection
- investigation
- explanation
- decision support
- onboarding
- compliance

Identify missing handoffs, duplicated responsibility and capabilities with no clear owner or destination.

Do not perform Stage 04 outcome discovery in full. Record newly noticed outcome opportunities as handoff items rather than expanding this stage indefinitely.

## Required outputs

Create at minimum:

- `outputs/agent-portfolio-assessment.md`
- `outputs/agent-capability-matrix.md`
- `outputs/tool-portfolio-matrix.md`
- `outputs/portfolio-boundary-map.md`
- `outputs/blocked-and-deferred-register.md`
- `outputs/stage-04-handoff.md`
- `outputs/stage-05-handoff.md`
- `outputs/stage-06-handoff.md`
- `outputs/stage-08-handoff.md`

Update:

- `findings.md`
- `decisions.md`
- `CONTEXT.md`
- `_inputs/source-register.md` where new sources are used
- `review-state.md`

## Required portfolio conclusion

Produce a concise recommended portfolio showing:

- capabilities retained as AI assistance
- capabilities converted to deterministic services/workflows
- capabilities merged or split
- capabilities blocked by platform prerequisites
- capabilities deferred
- capabilities rejected
- revised names where the current labels are misleading

Do not produce an implementation roadmap yet.

## Finding discipline

For every finding keep separate:

- current implementation
- proposed design
- observed overlap, gap or misclassification
- consequence
- evidence
- confidence
- recommendation
- required human decision
- downstream dependency

Keep confirmed, draft and parked/rejected findings separate.

Do not create artificial human decisions where the evidence and inherited principles already resolve the issue.

## Constraints

- Read-only review.
- Do not modify production code.
- Do not begin Stage 04.
- Do not design the final target architecture.
- Do not create the approved roadmap.
- Do not re-open Stage 02 decisions.
- Do not classify infrastructure engineering as AI capability merely because agents depend on it.
- Do not rely on an LLM for arithmetic, eligibility, state transitions, workspace ownership, reconciliation diffing or trace-derived numbers.
- Do not make legal conclusions.
- Record compliance questions for Stage 06.
- Record technical architecture questions for Stage 08.
- Do not commit or push.

## Completion criteria

Stage 03 is ready for review only when:

- every proposed agent/capability has a portfolio disposition
- every proposed tool has been assessed
- overlaps and misleading boundaries have been resolved or explicitly raised for decision
- deterministic responsibilities are separated from LLM responsibilities
- blocked capabilities reflect D-02-02 and D-02-03 correctly
- Y1 reflects D-02-04 correctly
- Track W has a clearly bounded current-state launch scope
- UX surface recommendations exist for retained capabilities
- platform, compliance and technical dependencies are handed to the correct later stages
- newly identified outcome opportunities are handed to Stage 04
- every confirmed finding meets the evidence standard

At completion:

1. Mark Stage 03 `awaiting-review`, not `complete`.
2. Do not begin Stage 04.
3. Report:
   - outputs created
   - confirmed findings by severity
   - recommended portfolio dispositions
   - capabilities retained as genuinely AI-assisted
   - capabilities reclassified as deterministic
   - merged, split, blocked, deferred or rejected capabilities
   - tool-level blockers
   - human decisions required
   - downstream handoffs
   - completion-criteria status
   - `git status --short`

Do not commit or push.