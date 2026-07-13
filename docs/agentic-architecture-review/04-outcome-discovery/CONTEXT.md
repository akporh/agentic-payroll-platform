# Stage 04: Outcome Discovery — Context

## Status

complete (gate closed 2026-07-13, HD-GATE-04) — 8 confirmed findings, 0 draft, 0 parked; HD-04-1 resolved (D-04-01: layered C7 calibration approach). 11 outputs produced, 3 updated to reflect the decision. Stage 05 not started.

## Objective

Identify the highest-value payroll, operator, compliance and commercial outcomes the approved 15-capability portfolio should deliver.

Begin from user and business outcomes, not from agent names or implementation preferences. Determine whether each outcome is best achieved through product UX, deterministic automation, analytics, AI assistance, bounded agency, or no new capability.

This stage is evaluative and product-focused. It must not redesign the final target architecture or implementation mechanism.

## Binding decisions inherited from prior stages

Do not re-litigate these decisions:

1. The deterministic/AI boundary approved in Stage 02 remains binding.
2. The revised 15-capability portfolio in `03-agent-portfolio/outputs/agent-capability-matrix.md` is the approved reference portfolio.
3. C4 Historical Payroll Explanation remains blocked until F-01-27, F-01-29 and F-01-38 close.
4. C8 Reconciliation Investigation remains blocked until the reconciliation workspace-scoping and historical-reproducibility preconditions close.
5. C9 Trace Agent remains rejected as a standalone capability.
6. C11 Compliance Monitoring remains detect/compare/propose only.
7. C12 Statutory-Rule Change Management remains a separate deterministic platform/compliance capability.
8. C13 AI Onboarding Mapping may not ship without C14 deterministic validation/dry-run as its hard safety gate.
9. C1, C2, C6, C10, C12 and C14 remain deterministic platform/workflow capabilities, not agents.
10. AI must not replace deterministic detection, calculation, rule execution, state transition or authoritative mutation.

## Required inputs

Read:

- `CLAUDE.md`
- `docs/agentic-architecture-review/README.md`
- `docs/agentic-architecture-review/WORKFLOW.md`
- `docs/agentic-architecture-review/review-state.md`
- all files under `docs/agentic-architecture-review/_core/`
- `docs/agentic-architecture-review/01-current-operating-model/findings.md`
- `docs/agentic-architecture-review/01-current-operating-model/outputs/current-operating-model-summary.md`
- all Stage 02 outputs
- `docs/agentic-architecture-review/03-agent-portfolio/findings.md`
- `docs/agentic-architecture-review/03-agent-portfolio/outputs/agent-capability-matrix.md`
- `docs/agentic-architecture-review/03-agent-portfolio/outputs/portfolio-boundary-map.md`
- `docs/agentic-architecture-review/03-agent-portfolio/outputs/blocked-and-deferred-register.md`
- `docs/agentic-architecture-review/03-agent-portfolio/outputs/stage-04-handoff.md`
- the current agent-layer architecture document
- current code only where needed to verify that an outcome has a real current-state basis

Record any new source used in `_inputs/source-register.md`.

## Questions this stage must answer

1. What important user, operational, compliance and business outcomes should the platform pursue?
2. Which approved capabilities contribute to each outcome?
3. Which desired outcomes are missing from the current portfolio?
4. Which capabilities solve weakly-defined or low-value problems?
5. Which outcomes should be achieved deterministically rather than through AI?
6. What measurable evidence would show each outcome has been achieved?
7. What risks or harmful incentives could arise from the chosen metrics?
8. What platform or control prerequisites must exist before an outcome can be pursued safely?
9. Which outcomes should be prioritised, deferred, blocked or rejected?

## Required investigation

### 1. Map the payroll operating lifecycle to desired outcomes

Cover at minimum:

- workspace and client setup
- structural configuration
- employee registration and enrolment
- employment/contract configuration
- timesheet and payroll-input collection
- payroll readiness
- run creation and calculation
- exception handling
- reconciliation and investigation
- approval and assurance
- locking and payment preparation
- post-payroll support and explanation
- statutory-rule monitoring and maintenance
- new-client onboarding and parallel-run validation
- operational reporting and continuous improvement

For each lifecycle area identify:

- primary user
- current problem or friction
- desired outcome
- current evidence from Stages 01–03
- best intervention type
- contributing approved capability or capabilities
- platform prerequisite
- control/compliance prerequisite
- measurable outcome
- risk of false confidence or harmful incentives

### 2. Assess specific outcome areas

At minimum assess:

#### Payroll readiness

- prevent avoidable run failures
- surface missing timesheets, missing salary definitions and expiring contracts
- assign and resolve readiness exceptions
- reduce unresolved issues at payroll cutoff

#### Input anomaly detection — C7

- define the user outcome before defining thresholds
- identify what kinds of anomalies matter operationally
- distinguish absolute thresholds, period-on-period variance and peer-pattern comparison
- propose a calibration approach, not a final production algorithm
- define how false positives and false negatives should be measured
- define what happens after an anomaly is flagged

Any final statistical mechanism belongs to Stage 08. Any threshold requiring product-owner judgement must be recorded in `decisions.md`.

#### Exception resolution workflow

Define the desired outcome and handoff for:

- issue creation
- prioritisation
- ownership
- evidence
- recommended next action
- resolution
- verification
- closure

Do not design the final UX; Stage 09 owns interface design.

#### Operator assistance — C3

Define value and metrics for:

- navigation guidance
- current-state explanation
- action planning
- support deflection
- operator confidence
- correct refusal of historical questions

Avoid adoption metrics that reward unnecessary chat usage.

#### Trace explanation — C5

Define the operator outcome and evidence standard for explaining current-run component traces without invented values.

#### Compliance monitoring and change management — C11 → C12

Frame the complete outcome chain:

- detect possible external change
- verify source and effective date
- compare with current platform rules
- assess affected clients/runs
- prepare a proposal
- review and approve
- apply through the separate deterministic change-management mechanism
- test and evidence the result

Keep C11 and C12 separate capabilities while defining the end-to-end user outcome.

#### Onboarding — C13 → C14

Define outcomes for:

- interpreting legacy payroll files
- reducing manual mapping work
- surfacing ambiguous mappings
- validating proposed mappings deterministically
- running a trustworthy dry run
- measuring parallel-run confidence
- reducing time to client go-live

Establish measurable baseline needs where the repository does not currently contain quantified onboarding data.

#### Historical explanation and reconciliation investigation — C4/C8

Do not reopen their blockers. Define only the future user outcomes and launch evidence that would be required once Stage 05 closes the prerequisites.

### 3. Discover missing outcomes

Test whether the approved portfolio is missing valuable outcomes such as:

- pre-approval assurance packs
- material period-on-period movement explanation
- operator work queues and ownership
- recurring-error root-cause reporting
- payroll deadline-risk visibility
- control-completion evidence
- client profitability or operational-cost insight
- support-response drafting
- configuration-drift detection
- unresolved-input visibility

Do not add a capability merely because it is technically possible. Every proposed addition must have a clear user problem, value case, intervention type and measurable outcome.

### 4. Prioritise outcomes

Classify each outcome as:

- pursue now
- pursue after platform prerequisite
- defer
- reject
- research further

Assess using:

- user value
- payroll-risk reduction
- compliance value
- frequency of the problem
- measurable operational impact
- platform readiness
- implementation complexity
- learning value
- commercial differentiation

Do not create the final roadmap; Stage 13 owns roadmap approval.

## Required outputs

Create:

1. `outputs/product-opportunity-map.md`
2. `outputs/outcome-capability-matrix.md`
3. `outputs/outcome-prioritisation.md`
4. `outputs/measurement-framework.md`
5. `outputs/anomaly-detection-outcome-policy.md`
6. `outputs/exception-resolution-outcome.md`
7. `outputs/compliance-outcome-chain.md`
8. `outputs/onboarding-outcome-baseline.md`
9. `outputs/stage-05-handoff.md`
10. `outputs/stage-09-handoff.md`
11. `outputs/stage-11-handoff.md`

Update:

- `findings.md`
- `decisions.md`
- `_inputs/source-register.md` where required
- `review-state.md`

## Finding discipline

For each finding record:

- finding ID
- user or business problem
- current evidence
- desired outcome
- approved capability/capabilities involved
- best intervention type
- observed gap or overlap
- consequence
- metric or evidence of success
- risk or harmful incentive
- confidence
- recommendation
- required human decision
- downstream dependency

Keep confirmed, draft and parked findings separate.

Do not present inferred user needs as verified facts. Label evidence gaps and baseline-data gaps explicitly.

## Explicitly out of scope

- final target architecture
- detailed tool contracts
- prompt design
- model selection
- technical orchestration design
- final anomaly algorithm or production threshold
- detailed confirmation-protocol design
- detailed dry-run mechanism design
- final UI design
- production implementation
- reopening approved Stage 02 or Stage 03 decisions
- starting Stage 05

## Constraints

- Read-only review.
- Do not modify production code, tests, migrations or application documentation outside this review programme.
- Do not disturb or include unrelated uncommitted remediation changes in this stage.
- Do not assume every outcome requires AI.
- Do not reward agent usage as an outcome in itself.
- Do not treat blocked capabilities as launch-ready.
- Do not make legal conclusions; record compliance questions for Stage 06.
- Do not commit or push unless explicitly instructed by the operator executing this context.

## Completion criteria

Stage 04 is ready for review only when:

- the full payroll lifecycle has been mapped to desired outcomes
- every approved capability has an outcome rationale or an explicit reason it remains foundational/blocked/deferred
- missing outcome opportunities have been assessed
- C7 anomaly-detection outcome and calibration policy have been framed
- the exception-resolution outcome and handoff have been defined
- C11→C12 has an end-to-end outcome chain without merging the capabilities
- C13→C14 has measurable onboarding outcomes and identified baseline gaps
- C3 has value metrics that do not incentivise unnecessary chat usage
- success, safety and harmful-incentive metrics are defined
- outcome priorities and prerequisites are explicit
- all human decisions are recorded
- downstream handoffs are complete
- every confirmed finding meets the evidence standard

## Completion procedure

When the work is finished:

1. Mark Stage 04 `awaiting-review`, not `complete`.
2. Do not begin Stage 05.
3. Report:
   - outputs created
   - confirmed findings by severity/importance
   - new or revised outcome opportunities
   - outcomes better handled deterministically
   - baseline-data gaps
   - human decisions required
   - blocked/deferred outcomes
   - Stage 05, 09 and 11 handoffs
   - `git status --short`

## Next action

**Await approval to begin Stage 05 — Platform Readiness.**