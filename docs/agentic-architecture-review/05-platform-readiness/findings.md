# Stage 05: Platform Readiness — Findings

Schema per `CONTEXT.md`: finding ID / affected capability(ies) / current implementation / expected guarantee / evidence / gap / consequence / severity / readiness classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner. All findings below are re-verified directly against current committed code (git HEAD), not inferred from prior stages' point-in-time findings — per this stage's explicit constraint against inferring readiness from documents alone.

---

## Draft Findings

_None — every item investigated reached a confirmed, evidence-backed disposition._

---

## Confirmed Findings

### F-05-01: No authentication mechanism exists anywhere in the application
- **Affected capability(ies)**: C1 (itself), and transitively nearly all others
- **Current implementation**: zero routes have any auth dependency; `workspace_id` is a plain, caller-supplied, unauthenticated string throughout
- **Expected guarantee**: verified operator identity and workspace isolation, per the source architecture document's own stated Track P design
- **Evidence**: `outputs/event-notification-readiness.md`; independently corroborated by `docs/audit-program/09-security-tenant-isolation/findings.md` (09-000)
- **Gap**: total — this is not a partial implementation, it is entirely unbuilt
- **Consequence**: every workspace-scoping guarantee elsewhere in the codebase (correct or not) only holds against an honest caller
- **Severity**: Critical
- **Readiness classification**: blocked
- **Minimum remediation**: `operator` table, JWT issuance, `get_current_operator` dependency on every route
- **Closure evidence**: every route rejects an unauthenticated request, proven by committed tests
- **Confidence**: High
- **Required human decision**: none — this is a build-priority fact, not a judgment call
- **Downstream owner**: Stage 08 (build), Stage 07 (security review)

### F-05-02: Event/notification/exception-tracking foundation is entirely unbuilt
- **Affected capability(ies)**: C2, C3, C6's surfacing, C7 (now gated on this per D-04-01), the exception-resolution workflow (F-04-01)
- **Current implementation**: `event_store` is write-only with no consumer; no `workspace_notification` table; no exception/issue data model of any kind
- **Expected guarantee**: a reliable event stream and notification/exception-tracking layer, per the source document's Track V design and Stage 04's outcome definition
- **Evidence**: `outputs/event-notification-readiness.md`
- **Gap**: total
- **Consequence**: the highest-priority outcome Stage 04 identified (exception resolution) has no platform to build on at all
- **Severity**: Critical
- **Readiness classification**: blocked
- **Minimum remediation**: transactional outbox, 4 named new events, consumer worker, notification table, exception data model
- **Closure evidence**: each component has a committed, passing test demonstrating end-to-end event flow
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 08

### F-05-03: `payroll_reconciliation` workspace scoping remains open, and is worse than Stage 01 found
- **Affected capability(ies)**: C8, any `get_reconciliation` tool
- **Current implementation**: no `workspace_id` column; repo functions scope solely by `payroll_run_id`; three "workspace-scoped" routes accept but discard the `workspace_id` parameter they declare
- **Expected guarantee**: workspace isolation on every reconciliation read/write, per D-02-02
- **Evidence**: `outputs/reconciliation-scoping-assessment.md`; corroborated by `docs/audit-program/09-security-tenant-isolation/findings.md` (09-002, 09-004)
- **Gap**: full data-layer gap unchanged since Stage 01, plus a newly-identified API-surface issue (decorative scoping)
- **Consequence**: a false impression of isolation is arguably worse than an honest absence of it, since it could pass a superficial review
- **Severity**: Critical
- **Readiness classification**: blocked (D-02-02)
- **Minimum remediation**: `workspace_id` column + backfill, repo/service functions updated, the three routes fixed to enforce what they already accept
- **Closure evidence**: committed regression test proving cross-workspace access is rejected
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 05 (this stage's findings feed directly into remediation prioritisation), Stage 07

### F-05-04: Statutory-rule change-management capability (C12) is entirely unbuilt, with zero test coverage for the capability itself
- **Affected capability(ies)**: C12, transitively C11
- **Current implementation**: statutory rates are added exclusively via Alembic migrations; no admin route exists; 20+ tests use raw-SQL statutory_rule inserts as fixtures for unrelated payroll tests, none test the capability itself
- **Expected guarantee**: an application-level, human-approved change-management workflow, per D-02-04/F-02-12
- **Evidence**: `outputs/statutory-change-platform-readiness.md`; corroborated by `docs/audit-program/03-configuration-integrity/findings.md`
- **Gap**: total
- **Consequence**: C11 cannot function end-to-end regardless of how well it detects changes
- **Severity**: Critical
- **Readiness classification**: blocked
- **Minimum remediation**: application-level write path, duplicate validation, approval record, preview/impact analysis
- **Closure evidence**: each sub-capability has a committed test
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 06 (workflow), Stage 08 (mechanism)

### F-05-05: `salary_definition` in-progress edit-lock gap remains open, unchanged
- **Affected capability(ies)**: C4, C8
- **Current implementation**: DB trigger only fires at `PAID`; application-layer check covers only one route and a partial status range
- **Expected guarantee**: historical reproducibility of any run referencing a `salary_definition`, per D-02-03
- **Evidence**: `outputs/historical-reproducibility-assessment.md`
- **Gap**: unchanged since Stage 01 (F-01-27)
- **Consequence**: a run's calculated result could differ from what re-explaining it later would show, if the referenced `salary_definition` was edited in between
- **Severity**: High
- **Readiness classification**: blocked (D-02-03)
- **Minimum remediation**: extend DB trigger or application-layer check to the full in-progress range, with a regression test
- **Closure evidence**: test proving an edit attempt during DRAFT/CALCULATING/LOCKED is rejected
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 08

### F-05-06: D-ARCH-1 lock check's dead branches and status-vocabulary drift remain unchanged
- **Affected capability(ies)**: C4, C8 (indirectly, via the same reproducibility gate)
- **Current implementation**: lock check still allowlists `SUBMITTED`/`PROCESSING`, neither of which exist in the current `PayrollRunStatus` enum (which gained `FAILED` since Stage 01, unrelated to this gap); `LOCKED` is also absent from the guarded range
- **Expected guarantee**: the lock check's status vocabulary should track the canonical enum, never drift
- **Evidence**: `outputs/historical-reproducibility-assessment.md`
- **Gap**: unchanged since Stage 01 (F-01-38); confirmed the `FAILED`-status remediation (commit `68e9307`) did not touch this
- **Consequence**: two of five branches in a financially-relevant lock check are dead code; the guard may not cover its intended full range
- **Severity**: High
- **Readiness classification**: blocked (bundled with F-05-05 under D-02-03)
- **Minimum remediation**: reference the canonical enum instead of a hardcoded list; add `LOCKED` if intended
- **Closure evidence**: a test iterating the enum against the lock check's coverage
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 08

### F-05-07: `component_trace_jsonb` fallback-precedence ambiguity (F-01-29) is confirmed unreachable in production
- **Affected capability(ies)**: C5 (informationally — not currently at risk)
- **Current implementation**: `save_payroll_result`'s ambiguous fallback logic has no production caller; only `save_payroll_results_bulk` (unambiguous) is used in practice
- **Expected guarantee**: N/A — narrowing finding
- **Evidence**: `outputs/historical-reproducibility-assessment.md`
- **Gap**: code-hygiene only — an unreachable function with latent ambiguous logic
- **Consequence**: none currently active; would become live only if a future caller is added without resolving the ambiguity first
- **Severity**: Low (downgraded from Stage 01's framing, based on new evidence of unreachability)
- **Readiness classification**: not a blocker
- **Minimum remediation**: remove the dead function, or resolve the ambiguity if a future caller is planned
- **Closure evidence**: either removal confirmed, or a test for the resolved fallback behavior
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 08 (code hygiene, low priority)

### F-05-08: Genuine platform improvement confirmed — retry statutory-rule source is now snapshot-first and hard-fails
- **Affected capability(ies)**: retry integrity generally, indirectly supports C4/C8's eventual unblocking
- **Current implementation**: retry reads exclusively from `payroll_run.rules_context_snapshot["statutory_rule"]`, hard-fails for legacy/incomplete snapshots, never falls back to a live query
- **Expected guarantee**: retry must reproduce the original run's statutory context exactly
- **Evidence**: `outputs/snapshot-retry-integrity-assessment.md` — commit `68e9307`, regression-tested (`tests/test_payroll_retry_snapshot_first.py`)
- **Gap**: none — this is a closure, not a gap
- **Consequence**: a specific, previously-reproducible statutory-rule-divergence bug is now fixed and proven fixed
- **Severity**: Informational (positive finding)
- **Readiness classification**: N/A — this is progress evidence, not a blocker
- **Minimum remediation**: N/A
- **Closure evidence**: already closed — test exists and passes
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: none — recorded for completeness

### F-05-09: Dry-run mechanism (C14) has a lower implementation cost than previously assumed
- **Affected capability(ies)**: C13, C14
- **Current implementation**: no dry-run product feature exists, but the calculation engine's core functions are already pure/side-effect-free and proven reusable via an existing developer script
- **Expected guarantee**: a trustworthy dry run exercising real payroll logic before commit
- **Evidence**: `outputs/onboarding-platform-readiness.md`
- **Gap**: product-level (endpoint, UI, operational definition of "safely separated"), not engine-level
- **Consequence**: C14 is more tractable than the original architecture proposal's framing suggested
- **Severity**: Medium (readiness gap, but a favorable one)
- **Readiness classification**: ready with normal implementation work
- **Minimum remediation**: API endpoint + UI wrapping the existing pure-compute path
- **Closure evidence**: committed dry-run endpoint test against a proposed import
- **Confidence**: High
- **Required human decision**: what "safely separated from production state" means operationally (does a dry run create a `payroll_run` row?) — forwarded to Stage 08 as a design question, not a Stage 05 decision
- **Downstream owner**: Stage 08

### F-05-10: `component_trace_jsonb` null handling is fixed at the HTTP/UI layer — genuine progress with a residual data-access-layer gap
- **Affected capability(ies)**: C5
- **Current implementation**: `payroll.py:1129` coerces null to `[]`; `PayrollResults.tsx` has an explicit empty-state UI; but `payroll_result_repo.py`/`payroll_retry_service.py` have no null-guard at the data layer
- **Expected guarantee**: no consumer of trace data should encounter an unhandled null, at any layer
- **Evidence**: `outputs/tool-readiness-baseline.md`, `outputs/frontend-backend-alignment.md`
- **Gap**: narrow — only affects a hypothetical future tool reading `payroll_result` directly, bypassing the HTTP route
- **Consequence**: today's operators are protected; a future tool builder could reintroduce the original gap if they don't know to check
- **Severity**: Medium
- **Readiness classification**: conditionally ready (for C5)
- **Minimum remediation**: add the same null-guard at the repository layer
- **Closure evidence**: a repository-layer unit test for the null case
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 08

### F-05-11: Two previously-unidentified tool-wrapping risks found in this stage's dedicated tool-readiness pass
- **Affected capability(ies)**: any future tool layer (C3, C5, C11, etc.)
- **Current implementation**: `load_inputs_for_run(payroll_run_id)` has no workspace_id parameter (safe today only via upstream caller discipline); `workspace_info()` picks an arbitrary workspace with `LIMIT 1` and no scoping parameter at all
- **Expected guarantee**: every function a future tool might wrap should be safe to call directly, not merely safe for its current caller
- **Evidence**: `outputs/tool-readiness-baseline.md`
- **Gap**: newly identified — neither function was flagged in Stage 01's general workspace-scoping sweep, which asked a different question
- **Consequence**: confirms the value of the "independent tool-layer verification" principle (Stage 02 Principle 11) concretely, beyond the one previously-known reconciliation case
- **Severity**: Medium
- **Readiness classification**: not yet blocking (no tool exists), but must be fixed before either function is wrapped
- **Minimum remediation**: add workspace parameter/enforcement to `load_inputs_for_run`; require an explicit identifier for `workspace_info()`, audit its existing callers
- **Closure evidence**: tests proving both functions reject/ignore cross-workspace data
- **Confidence**: High
- **Required human decision**: none
- **Downstream owner**: Stage 07, Stage 08

### F-05-12: Frontend/backend mismatches largely unchanged, one narrowing
- **Affected capability(ies)**: operator-facing UI generally
- **Current implementation**: `FULL_RUN` retry option still selectable in `RunPayroll.tsx` despite DB/API rejection; `run_type` CORRECTION still API-only; `employee.status` still has no DB CHECK
- **Expected guarantee**: UI options should only present backend-supported paths
- **Evidence**: `outputs/frontend-backend-alignment.md`; corroborated by `docs/audit-program/06-ui-api-backend-wiring/findings.md` (06-003)
- **Gap**: unchanged for all three items
- **Consequence**: FULL_RUN remains a confirmed dead-end UI path (launch-risk); the other two are lower-severity usability/consistency gaps
- **Severity**: Medium (FULL_RUN), Low (the other two)
- **Readiness classification**: normal implementation work
- **Minimum remediation**: remove FULL_RUN from the UI, or restore backend support (a product decision outside this review's scope); expose CORRECTION in the UI dropdown if intended to be operator-reachable; add the DB CHECK constraint
- **Closure evidence**: UI no longer offers FULL_RUN; either CORRECTION appears in the UI or its API-only status is a deliberate, documented choice
- **Confidence**: High
- **Required human decision**: whether CORRECTION should remain API-only by design or be exposed in the UI — a product decision, forwarded to Stage 09/11, not resolved here
- **Downstream owner**: Stage 09

---

## Parked / Rejected

_None — every re-verification reached a confirmed disposition._

## Human decisions required (raised by this stage)

Consistent with the finding-discipline principle applied since Stage 03 ("do not create artificial human decisions where evidence and inherited principles already resolve the issue"), this stage found **no decision requiring adjudication at the Stage 05 gate itself**. The two candidate decisions surfaced (F-05-09's "what does dry-run separation mean operationally," F-05-12's "should CORRECTION be UI-exposed") are both forwarded as design/product questions to Stage 08/09/11 respectively — neither is a readiness-evidence question this stage needs the human reviewer to resolve before closing its own gate.

## Cross-references for later stages

- Stage 06 (Compliance & Controls): F-05-04, F-05-01/F-05-02 (attribution/audit dependency), F-05-03 (tenant-isolation compliance angle).
- Stage 07 (Security & Identity): F-05-01, F-05-03, F-05-11.
- Stage 08 (Technical Architecture): F-05-01, F-05-02, F-05-04, F-05-05, F-05-06, F-05-09, F-05-10, F-05-11.
- Stage 09 (Human Experience): F-05-12.
- Stage 11 (Commercial & Product Strategy): sequencing implications of F-05-01/F-05-02 being foundational blockers for the majority of the portfolio.
