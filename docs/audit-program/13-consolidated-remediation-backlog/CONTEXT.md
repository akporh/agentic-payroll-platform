# Stage 13 — Consolidated Remediation Backlog

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Convert the completed Stage 01–12 audit into one authoritative, dependency-aware remediation backlog that can be implemented in safe, testable increments.

This is a backlog/design stage only. Do not implement remediation.

## Confirmed programme state

- Stages 01–12 are complete.
- `04-001` and `05-001` are remediated, reviewed, and regression-protected.
- Stage 11 baseline: 306 passed, 1 skipped.
- `09-000` remains the dominant S0 production blocker: no authentication, account membership, RBAC, or caller ownership exists.
- Application authentication and server-side authorization are mandatory before live/production-data use; network controls are defence in depth only.
- Approved tenancy model: one bureau account managing multiple client workspaces through explicit membership and RBAC, with future direct-client extensibility.
- Stage 10 trace-remediation design is approved and canonical.
- Stage 12 legacy-executor disposition is approved: retain temporarily with telemetry, inventory/migrate active configuration, then hard-fail/remove for new runs; replay-only compatibility only if a real requirement is proven.
- `04-004` remains rejected, no action.
- `05-003` remains intentionally retained.
- `CLAUDE.md` is authoritative.

## Required backlog domains

The canonical backlog must include:

1. Authentication, tenancy, RBAC, and route ownership.
2. Legacy route removal and admin/diagnostic protection.
3. Exception sanitization and export formula-injection protection.
4. Audit/event completeness.
5. Stage 10 trace/statutory-identity/excluded-component package.
6. Background-task terminal-failure handling.
7. Data-integrity corrections: `08-001`, `08-002`, `05-004`, `06-002`.
8. Statutory-component policy and enforcement.
9. Legacy-executor migration/removal programme.
10. Frontend/API contract repairs.
11. Stage 12 simplification package.
12. Permanent tests and CI controls embedded into each remediation item.

Every canonical item must define:

- source findings;
- severity and release gate;
- scope and non-scope;
- dependencies;
- migration/API/UI/operational impact;
- acceptance criteria;
- required automated tests;
- rollback;
- relative effort;
- recommended implementation package.

## Required sequencing

Preserve the following priority logic:

- Programme 0: keep `04-001`/`05-001` green.
- Programme 1: authentication, membership, RBAC, secure configuration.
- Programme 2: route ownership, secure lifecycle routes, reconciliation/timeline/stats, admin restriction, legacy route removal.
- Programme 3: error, export, and audit hardening.
- Programme 4: data-integrity corrections.
- Programme 5: execution trace and auditability.
- Programme 6: statutory policy and legacy-executor transition.
- Programme 7: frontend completeness and operator workflows.
- Programme 8: safe simplification and cleanup.

Security Programmes 1–2 must complete before live/production-data use. Independent lower-risk fixes may proceed in parallel where dependencies permit.

## Required crosswalk

Crosswalk every open, remediated, rejected, deferred, or intentionally retained Stage 01–12 item. Preserve all source IDs and consolidate duplicate mechanisms.

At minimum include:

- `01-002`, `01-004`
- `02-002`
- `03-004`
- `04-002`, `04-004`
- `05-002`, `05-003`, `05-004`, `05-005`
- `06-001` through `06-007`
- `07-001` through `07-005`
- `08-001`, `08-002`, `08-003`
- `09-000`, `09-001`, `09-002`, `09-004`, `09-005`, `09-006`, `09-007`, `09-008`
- Stage 10 approved package
- Stage 11 eight permanent-test recommendations
- Stage 12 frontend-status finding and cleanup candidates
- remediated: `04-001`, `05-001`
- rejected: `04-004`
- intentionally retained: `05-003` and Stage 12 retained items.

## Constraints

- Read-only backlog/design stage.
- No backend/frontend, migration, test, script, schema, or data changes.
- Do not begin remediation implementation.
- Do not reopen `04-001`/`05-001` without contradictory evidence.
- Do not reclassify `04-004` as open.
- Do not use local dev-data prevalence as production prevalence.
- Do not omit tests, rollback, dependencies, or release gates.

---

## Close-review instruction

Use this section after the Stage 13 backlog has been committed for human review.

### Final policy decisions

Approve all four recommendations:

#### D1 — Mandatory statutory-component disablement

**Decision: forbid disablement of mandatory statutory components.**

Implementation requirements:

- define mandatory statutory component codes/classes by jurisdiction;
- reject attempts to set them inactive through API, UI, onboarding, override, or direct supported configuration paths;
- retain eligibility/applicability rules for legitimate employee-level exemptions or zero liability;
- distinguish “not applicable under the statutory rule” from “disabled by configuration”;
- audit rejected configuration attempts where appropriate;
- preserve Stage 10 omitted-component visibility for non-mandatory components and for legacy evidence;
- add server-side, DB/configuration, and UI regression tests.

Rationale: mandatory legal obligations should be controlled by statutory applicability logic, not by a workspace-level off switch. A privileged disable option would create unnecessary compliance risk and make configuration authority responsible for overriding law. If a future jurisdiction has a genuine exemption, model that exemption explicitly in the statutory rule/eligibility layer rather than permitting blanket disablement.

#### D2 — `payroll_run` immutability lifecycle point

**Decision: financially relevant run totals and period fields become DB-immutable at `APPROVED`.**

Implementation requirements:

- align run-level immutability with the existing approved-run/result invariant;
- enumerate exact protected columns;
- permit only explicitly designed system transitions that do not alter approved financial facts;
- ensure lock, reconciliation, and payment consume the approved values without rewriting them;
- add direct SQL tests at `APPROVED`, `LOCKED`, and `PAID`;
- provide migration downgrade and rollback.

Rationale: allowing run totals or period identity to change after approval would make the approved result set and its run header inconsistent. `LOCKED` would be one lifecycle stage too late.

#### D3 — Legacy-executor observation window

**Decision: require zero new-run fallback firings across two consecutive full production payroll cycles after configuration migration is complete.**

The observation window starts only when:

- every active workspace has been inventoried;
- missing/invalid metadata has been repaired;
- fallback telemetry is live and reliable.

Any fallback firing resets the two-cycle count and requires investigation/classification. Dev-database percentages must not be used as cutover evidence.

#### D4 — Payroll operator/approver separation of duties

**Decision: soft separation with explicit audit flagging.**

- A user may hold both operator and approver roles.
- Same-person approval of a run they created or last retried is permitted but must be visibly flagged.
- Write a distinct audit/event record containing creator/retrier, approver, timestamps, and a `same_actor_approval` indicator.
- UI must display the warning before confirmation and in the run audit history.
- Reporting must allow these approvals to be filtered/reviewed.
- The role model must permit later upgrade to hard separation without redesign.

Rationale: this preserves a meaningful control and honest audit trail without making a small bureau unable to complete payroll when two separate people are unavailable.

### Backlog conclusions to preserve

Accept the Stage 13 backlog structure and prioritisation, subject to recording the decisions above:

- S0 security foundation and direct dependents remain the release-blocking programme.
- No live/production-data use before authentication, membership/RBAC, and mandatory ownership checks are implemented and tested.
- Stage 10’s schema/write-side trace work may ship independently, but tenant-safe trace access is not secure until auth/membership/RBAC exists.
- `07-001`, `09-008`, `08-001`, and zero-caller legacy reconciliation removal remain independently shippable early fixes where dependencies permit.
- Tests stay embedded within each remediation package rather than becoming a generic later task.
- `04-001` and `05-001` remain closed/remediated.
- `04-004` remains rejected.
- `05-003` and the Stage 12 retained items remain intentional retentions.

### Review requirements

Before closing Stage 13, verify that:

1. every Stage 01–12 finding has exactly one canonical disposition;
2. overlapping findings retain all source references without duplicate backlog items;
3. D1–D4 are reflected consistently in the backlog, dependency graph, release gates, tests, residual-risk statement, and completion criteria;
4. D1 does not remove legitimate statutory eligibility/exemption modelling;
5. D2 protects exact run-level financial/period fields at `APPROVED`;
6. D3 starts only after production configuration migration and reliable telemetry;
7. D4 creates an explicit audit signal rather than a silent same-person approval;
8. every S0/S1 item has implementation scope, tests, rollback, and release gate;
9. all eight Stage 11 permanent-test recommendations are embedded in their related items;
10. no implementation work or data change occurred in Stage 13.

### Close the audit programme

Update:

- `docs/audit-program/13-consolidated-remediation-backlog/findings.md`
  - change status to `complete`;
  - replace D1–D4 decision-required language with the approved decisions;
  - update affected backlog items, residual risk, and programme completion criteria;
  - add a final closure summary.
- `docs/audit-program/_core/human-decisions.md`
  - record D1–D4 as final decisions.
- `docs/audit-program/audit-state.md`
  - mark Stage 13 `complete`;
  - set the closed date to today;
  - state that the 13-stage audit programme is complete;
  - set the next action to implementation planning for Programme 1 — Authentication and tenancy foundation;
  - preserve all prior stage summaries, decisions, remediation records, rejected findings, and intentional retentions.

### Constraints during close review

- Do not modify application code, migrations, tests, scripts, schema, or data.
- Do not begin implementation.
- Do not create a separate close-review prompt file.

### Publish

Commit and push the Stage 13 closure documentation to `uat`.

Return only:

```text
Stage: 13 — Consolidated remediation backlog
Status: complete
Primary file: docs/audit-program/13-consolidated-remediation-backlog/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decisions:
- D1: mandatory statutory components cannot be disabled; exemptions are modeled through statutory applicability rules.
- D2: payroll_run financial totals and period fields become immutable at APPROVED.
- D3: legacy fallback removal requires two consecutive clean production payroll cycles after migration and telemetry readiness.
- D4: soft operator/approver separation with explicit same-actor audit flagging.

Audit programme:
- Stages 01–13 complete.
- Next action: implementation planning for Programme 1 — Authentication and tenancy foundation.
```
