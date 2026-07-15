# Stage 05: Platform Readiness — Context

## Status

awaiting-review (investigation complete 2026-07-13 — 12 confirmed findings, 0 draft, 0 parked; 0 human decisions required at this stage's gate (2 design questions forwarded to Stage 08/09); 15 outputs produced, all findings independently re-verified against current committed code, not inferred from prior stages. Not marked `complete` per this CONTEXT.md's own completion procedure — Stage 06 not started.)

## Objective

Assess whether the current payroll platform is technically and operationally ready to support the approved capability portfolio safely.

This stage must identify, verify and prioritise the platform prerequisites that must exist before each capability can be built or launched. It is a readiness assessment, not an implementation stage and not a re-review of the approved portfolio.

## Binding decisions inherited from prior stages

Do not re-litigate these decisions:

1. The deterministic/AI boundary approved in Stage 02 remains binding.
2. The approved 15-capability portfolio from Stage 03 is the reference portfolio.
3. `payroll_reconciliation` repository-level workspace scoping is a mandatory precondition for C8 and any reconciliation-reading tool.
4. Tool-layer workspace verification is required in addition to repository-level scoping.
5. F-01-27, F-01-29 and F-01-38 must close before C4 or C8 can launch.
6. C9 Trace Agent remains rejected as a standalone capability.
7. C11 remains detect/compare/propose only.
8. C12 statutory-rule change management is a separate deterministic platform capability.
9. C13 may not ship without C14 deterministic validation/dry-run as its hard safety gate.
10. D-04-01 approves layered C7 calibration: absolute thresholds first, period-on-period variance second, peer-pattern comparison deferred.
11. C7 must not ship without the exception-resolution workflow.

## Required inputs

Read:

- `CLAUDE.md`
- `docs/programmes/agentic-architecture-review/README.md`
- `docs/programmes/agentic-architecture-review/WORKFLOW.md`
- `docs/programmes/agentic-architecture-review/review-state.md`
- all files under `docs/programmes/agentic-architecture-review/_core/`
- all confirmed findings and outputs from Stages 01–04
- `03-agent-portfolio/outputs/agent-capability-matrix.md`
- `03-agent-portfolio/outputs/blocked-and-deferred-register.md`
- `03-agent-portfolio/outputs/stage-05-handoff.md`
- `04-outcome-discovery/outputs/outcome-prioritisation.md`
- `04-outcome-discovery/outputs/measurement-framework.md`
- `04-outcome-discovery/outputs/stage-05-handoff.md`
- the current agent-layer architecture document
- relevant backend, domain, repository, service, API, migration, frontend and test code needed to verify readiness claims

Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. Which approved capabilities are build-ready now?
2. Which capabilities are blocked by platform defects, missing infrastructure or incomplete guarantees?
3. Which preconditions are hard launch gates versus normal implementation work?
4. Are current data, snapshot, trace, reconciliation, audit, event and state-transition guarantees strong enough for the intended capabilities?
5. Where do frontend and backend behaviour diverge in ways that would mislead an agent or operator?
6. Are current repository and service boundaries safe enough to expose through tools?
7. What minimum remediation is required to unblock C4, C8, C11/C12, C13/C14 and the exception-resolution workflow?
8. What evidence would prove each prerequisite has actually closed?

## Required investigation

### 1. Capability-by-capability readiness assessment

For all 15 approved capabilities classify readiness as:

- ready
- ready with normal implementation work
- conditionally ready
- blocked
- deferred
- rejected

For each capability record:

- required platform services
- required data guarantees
- required security guarantees
- required control/audit guarantees
- current evidence
- readiness gaps
- blocker severity
- minimum closure evidence
- downstream stage owner

Do not redefine capability scope.

### 2. Reconciliation workspace isolation

Inspect all code paths touching `payroll_reconciliation`, including:

- repository reads and writes
- service calls
- API routes
- joins through payroll runs
- correction/resolution flows
- future tool-wrapper risk

Determine:

- exact current scoping behaviour
- whether a repository-level fix already exists on the reviewed commit
- whether all relevant paths derive workspace ownership safely
- the minimum code/test evidence required to close F-01-33
- the required defence-in-depth pattern for future tools

Treat this as a hard blocker, not an accepted risk.

### 3. Historical reproducibility closure

Reassess F-01-27, F-01-29 and F-01-38 in current code:

- mutable salary-definition or configuration state affecting historical explanation
- trace persistence/fallback ambiguity
- dead or incomplete status branches in the D-ARCH-1 guard

Also inspect any related snapshot, retry and lock semantics that could affect historical truth, including:

- salary-definition snapshots
- employee-contract snapshots
- component metadata/client override snapshots
- statutory-rule/tax-band snapshots
- retry snapshot-first behaviour
- current-date versus run-period reads
- post-calculation and post-lock mutation paths

For each item determine whether it is:

- closed
- partially closed
- still open
- superseded by a stronger mechanism

State the exact evidence required before C4/C8 can unblock.

### 4. Snapshot and retry integrity

Verify that:

- original runs and retries use the correct authoritative snapshot sources
- retry strategy cannot silently change the source of truth
- retry does not delete or overwrite successful historical evidence incorrectly
- legacy and sequential execution paths do not produce incompatible guarantees
- trace and totals remain consistent between original-run and retry paths

Do not modify the unrelated remediation work in the operator's working tree. Assess committed repository state and clearly label any uncommitted evidence separately if it is visible.

### 5. Event, notification and exception-workflow foundation — C2

Assess readiness for:

- transactional outbox/event delivery
- event completeness for material payroll lifecycle changes
- event consumption
- workspace notifications
- exception ownership/status/history
- idempotent creation and resolution
- stale-event or stale-notification handling
- multi-worker safety

Stage 04 established C2 as a prerequisite for the highest-priority exception-resolution outcome. Determine minimum viable platform closure, not final UI design.

### 6. Audit and operational-history coverage

Reassess F-01-40 and determine whether the platform records enough structured history for:

- recurring-error analysis
- control-completion evidence
- exception lifecycle reporting
- operator-action attribution
- configuration-change history
- compliance-change evidence

Separate:

- payroll-run state-transition audit
- domain-change audit
- agent/tool invocation audit
- exception-resolution audit

Identify the minimum audit expansion needed before downstream capabilities rely on historical operational reporting.

### 7. Onboarding instrumentation and dry-run prerequisites

Assess readiness for C13/C14, including:

- current upload/mapping persistence
- deterministic validation coverage
- dry-run execution feasibility
- whether dry-run can use the real sequential executor and snapshot path safely
- separation from production payroll-run state
- persistence of comparison results
- feasibility of persisting `ReconSlideOver` output currently discarded client-side
- instrumentation for mapping time, mapping error rate, parallel-run agreement and time-to-go-live

Do not fully design the dry-run mechanism; Stage 08 owns that. Determine platform prerequisites and feasible evidence sources.

### 8. Statutory-rule change-management readiness — C12

Assess the current statutory-rule model and maintenance path:

- migration-only changes
- effective dating
- overlapping or duplicate rules
- validation
- test coverage
- preview/impact analysis
- approval evidence
- rollback/correction
- auditability

Determine what deterministic platform capabilities must exist before C11 proposals can become actionable. Stage 06 owns compliance workflow design; Stage 05 owns technical readiness facts.

### 9. Tool-readiness baseline

For every proposed read-only or future write-capable tool assess:

- authoritative source
- workspace ownership enforcement
- current-state versus historical-state guarantee
- null/ambiguous-result behaviour
- pagination and result bounds
- PII exposure
- deterministic evidence returned
- repository/service functions safe to wrap

Do not write final tool contracts; Stage 08 owns them.

### 10. Frontend/backend alignment

Reassess confirmed mismatches that could create false operator or agent assumptions, including:

- retry options exposed in UI versus supported backend behaviour
- backend-only features not surfaced in UI
- configuration values written to one representation while calculation reads another
- readiness checks not surfaced before failure
- trace/reconciliation data present but inconsistently exposed

Classify each mismatch as:

- blocker
- launch-risk
- usability gap
- normal implementation work

## Required outputs

Create:

1. `outputs/capability-readiness-matrix.md`
2. `outputs/platform-blocker-register.md`
3. `outputs/reconciliation-scoping-assessment.md`
4. `outputs/historical-reproducibility-assessment.md`
5. `outputs/snapshot-retry-integrity-assessment.md`
6. `outputs/event-notification-readiness.md`
7. `outputs/audit-coverage-assessment.md`
8. `outputs/onboarding-platform-readiness.md`
9. `outputs/statutory-change-platform-readiness.md`
10. `outputs/tool-readiness-baseline.md`
11. `outputs/frontend-backend-alignment.md`
12. `outputs/readiness-closure-plan.md`
13. `outputs/stage-06-handoff.md`
14. `outputs/stage-07-handoff.md`
15. `outputs/stage-08-handoff.md`

Update:

- `findings.md`
- `decisions.md`
- `_inputs/source-register.md` where required
- `review-state.md`

## Finding discipline

For each finding record:

- finding ID
- affected capability/capabilities
- current implementation
- expected guarantee
- evidence
- gap
- consequence
- severity
- readiness classification
- minimum remediation
- closure evidence
- confidence
- required human decision
- downstream owner

Keep confirmed, draft and parked findings separate.

Do not mark a blocker closed merely because remediation code exists uncommitted in a working tree. Closure requires committed, reviewable evidence and relevant tests.

## Explicitly out of scope

- implementing fixes
- modifying production code, tests or migrations
- final security architecture
- detailed compliance workflow
- final tool contracts
- prompt or model design
- final dry-run design
- final confirmation-protocol design
- UI design
- commercial sequencing
- reopening Stage 02–04 decisions
- starting Stage 06

## Constraints

- Read-only review.
- Do not alter or include unrelated uncommitted remediation changes.
- Distinguish committed-state evidence from working-tree observations.
- Do not infer readiness from architecture documents alone; verify against code and tests.
- Do not treat passing unit tests as proof of an unstated guarantee.
- Do not reduce mandatory launch gates to documentation warnings.
- Do not commit or push unless explicitly instructed by the operator executing this context.

## Completion criteria

Stage 05 is ready for review only when:

- all 15 capabilities have a readiness classification
- every blocker has a named remediation and closure-evidence requirement
- reconciliation workspace scoping has a definitive status
- F-01-27, F-01-29 and F-01-38 have each been reassessed against current code
- snapshot and retry integrity have been evaluated end to end
- C2 readiness for exception workflows has been assessed
- audit coverage has been assessed against operational-reporting outcomes
- onboarding instrumentation and dry-run prerequisites have been assessed
- C12 technical prerequisites have been defined
- tool-readiness and frontend/backend alignment baselines are complete
- committed versus uncommitted evidence is clearly separated
- all human decisions are recorded
- Stage 06, 07 and 08 handoffs are complete

## Completion procedure

When work is finished:

1. Mark Stage 05 `awaiting-review`, not `complete`.
2. Do not begin Stage 06.
3. Report:
   - capability readiness summary
   - blockers by severity
   - preconditions closed, partially closed or still open
   - committed versus uncommitted evidence
   - human decisions required
   - Stage 06, 07 and 08 handoffs
   - `git status --short`

## Next action

**Human review of Stage 05 outputs; gate approval required before Stage 06.**