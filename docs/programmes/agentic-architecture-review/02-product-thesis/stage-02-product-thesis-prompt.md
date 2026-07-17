# Stage 02 — Product Thesis Review Prompt

Begin Stage 02 only:

`docs/programmes/agentic-architecture-review/02-product-thesis/`

## Objective

Evaluate whether the proposed product boundary is sound:

> AI supports judgement, investigation, interpretation and coordination, while deterministic platform services remain responsible for payroll calculations, statutory rules, authoritative state transitions and financial record mutation.

This stage must determine where AI is justified, where conventional automation is safer, and where the proposed direction is unclear or unsound.

Do not review the individual agent portfolio in detail yet. That belongs to Stage 03.

## Before starting

Read:

- `CLAUDE.md`
- `docs/programmes/agentic-architecture-review/README.md`
- `docs/programmes/agentic-architecture-review/WORKFLOW.md`
- `docs/programmes/agentic-architecture-review/review-state.md`
- all files under `docs/programmes/agentic-architecture-review/_core/`
- `docs/programmes/agentic-architecture-review/_inputs/source-register.md`
- `docs/programmes/agentic-architecture-review/01-current-operating-model/findings.md`
- all Stage 01 outputs, especially:
  - `outputs/current-operating-model-summary.md`
- the current agent-layer architecture document
- current code where needed to verify architectural claims

Confirm:

- Stage 01 is approved and complete
- Stage 02 is eligible to begin
- no later stage is already in progress

Update:

- Stage 02 status to `in-progress`
- `review-state.md` next action to “Complete Stage 02 product-thesis assessment”

## Required investigation

### 1. Reconstruct the intended product thesis

Identify what the current architecture proposes AI should do and should not do.

Separate:

- explicitly stated design principles
- implied assumptions
- current implementation
- future intent
- unresolved product decisions

Do not treat the architecture document as proof of implementation.

### 2. Classify capability types

For every meaningful capability proposed or implied in the architecture, classify it as:

- deterministic software
- rules engine
- workflow automation
- analytics or anomaly detection
- retrieval and explanation
- probabilistic AI assistance
- bounded agentic workflow
- autonomous agent
- capability that should not be built

For each classification, explain:

- why that category fits
- whether an LLM is necessary
- whether a simpler approach would be safer
- what evidence or uncertainty remains

### 3. Test the deterministic/AI boundary

Assess whether AI is correctly excluded from:

- payroll calculations
- statutory-rule execution
- tax-band selection
- component ordering
- rounding
- eligibility enforcement
- run-state transitions
- locking
- payment-related actions
- authoritative data mutation
- final compliance decisions

Assess whether AI is potentially appropriate for:

- explanation
- investigation
- ambiguity resolution
- evidence assembly
- exception triage
- recommendation
- drafting
- natural-language interaction
- interpretation of unstructured inputs
- coordination across workflows

Identify any areas where the current boundary is:

- sound
- too permissive
- too restrictive
- ambiguous
- internally inconsistent

### 4. Test whether “agentic” is actually required

For each proposed problem area, determine whether the best intervention is:

- better product UX
- validation
- deterministic automation
- workflow orchestration
- rules
- analytics
- anomaly detection
- search and retrieval
- AI assistance
- bounded agency
- no new capability

Explicitly identify any cases where the architecture appears to use “agent” terminology for ordinary workflow automation.

### 5. Evaluate dependence on platform trustworthiness

Use Stage 01 findings to assess whether the proposed thesis depends on foundations that are not yet sufficiently reliable.

At minimum consider:

- parallel configuration entry points
- silent employee exclusion
- sequential versus legacy executor divergence
- snapshot completeness
- retry behaviour
- reconciliation scoping
- audit coverage
- frontend/backend mismatches
- statutory-rule representation
- incomplete historical reproducibility

Do not perform the full readiness review reserved for Stage 05.

Only identify where these facts materially affect the validity of the product thesis.

### 6. Define non-negotiable product principles

Recommend a concise set of principles governing future product decisions.

At minimum test whether the following should be retained:

1. Payroll calculations remain deterministic.
2. The LLM is never the source of truth.
3. Agents use controlled tools rather than database access.
4. Generated explanations must link to evidence.
5. High-risk mutations require structured approval.
6. Agent memory must not become a shadow system of record.
7. Historical payroll outcomes must remain reproducible.
8. Chat is an interface, not the product strategy.
9. AI should not be used where deterministic software is sufficient.
10. Autonomy must be earned through measured performance.

For each principle classify it as:

- retain
- revise
- remove
- add

## Required outputs

Create:

- `outputs/product-thesis-assessment.md`
- `outputs/capability-classification-matrix.md`
- `outputs/deterministic-ai-boundary.md`
- `outputs/non-negotiable-product-principles.md`
- `outputs/stage-03-handoff.md`

Update:

- `findings.md`
- `decisions.md`
- `review-state.md`

## Required finding structure

For each finding record:

- finding ID
- statement
- current implementation
- intended design
- observed gap or ambiguity
- consequence
- evidence
- confidence
- severity
- recommendation
- required human decision
- downstream stage dependency

Keep confirmed, draft and parked findings separate.

## Constraints

- Read-only review.
- Do not modify production code.
- Do not design the final target architecture.
- Do not fully assess individual agents.
- Do not create the roadmap.
- Do not assume AI is required.
- Do not equate conversational UI with agentic capability.
- Do not describe ordinary automation as autonomous.
- Do not make legal conclusions.
- Record compliance questions for Stage 06.
- Record platform-readiness dependencies for Stage 05.
- Record unresolved product choices in `decisions.md`.
- Do not begin Stage 03.
- Do not commit or push.

## Completion criteria

Stage 02 is ready for review only when:

- the intended product thesis has been reconstructed
- all material capability types have been classified
- the deterministic/AI boundary has been assessed
- unnecessary uses of AI have been identified
- ambiguous or unsafe boundaries have been documented
- Stage 01 findings affecting the thesis have been incorporated
- non-negotiable product principles have been proposed
- unresolved human decisions have been recorded
- Stage 03 receives a clear handoff
- every confirmed finding meets the evidence standard

At completion:

1. Mark Stage 02 `awaiting-review`, not `complete`.
2. Do not begin Stage 03.
3. Report:
   - outputs created
   - confirmed findings by severity
   - draft or unconfirmed observations
   - capabilities where AI appears justified
   - capabilities better handled deterministically
   - unsafe or ambiguous boundaries
   - human decisions required
   - Stage 03 handoff
   - `git status --short`

Do not commit or push.
