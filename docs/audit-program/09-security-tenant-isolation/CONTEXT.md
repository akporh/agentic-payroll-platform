# Stage 09 — Security and Tenant Isolation

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Determine whether authentication, authorization, tenant scoping, data exposure, privileged operations, and security-relevant error handling are consistently enforced across the payroll platform.

This stage must distinguish between:

- missing authentication
- missing authorization
- missing tenant scoping
- tenant scoping present only in the UI
- tenant scoping enforced in routes but not repositories/services
- schema-permitted cross-workspace relationships
- information disclosure through errors, logs, exports, traces, or diagnostics
- intentionally privileged operator/admin routes
- dead or superseded routes that retain security risk
- security controls that are correctly enforced end to end

The focus is application and data-access security for the current codebase. Do not perform destructive penetration testing or modify production/shared data.

## Confirmed handoff state

- Stages 01–08 are complete.
- `04-001` and `05-001` are remediated and must not be reopened without regression evidence.
- `07-001` is confirmed S1: 21 API-route sites return raw exception text via `str(e)`/`str(exc)` and require security classification.
- `06-007` is confirmed: an older unscoped reconciliation route pair has no frontend caller and is superseded by workspace-scoped routes; tenant enforcement was not verified.
- `03-004` / `08-003` remain open: statutory-deduction components can be disabled without a class-aware guard or omission signal. This stage should assess who can perform that action and whether tenant/role boundaries protect it; do not resolve the product-policy question.
- Stage 08 found no new cross-workspace referential defect in targeted spot checks, but did not perform a full route-by-route tenant audit.
- `04-002` and the minimal retry-trace design belong to Stage 10.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.
- Stage 09 is read-only: no backend, frontend, migration, test, script, or data changes.

## Required inputs

Read before investigation:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 01 findings, especially route-prefix, operator, and architecture observations
- Stage 03 findings, especially `03-004`
- Stage 06 findings, especially `06-007` and tenant/permission observations
- Stage 07 findings, especially `07-001`
- Stage 08 findings, especially `08-003` and referential/tenant spot checks
- completed remediation records for `04-001 + 05-001`

## Objective

Establish whether the platform can guarantee that:

1. every protected route requires the intended authentication context;
2. every workspace-scoped operation independently verifies tenant ownership server-side;
3. route, service, repository, and SQL layers do not trust client-supplied workspace or resource IDs without validation;
4. cross-workspace reads, writes, retries, exports, traces, reconciliation, and configuration changes are prevented;
5. privileged admin/operator capabilities are intentionally separated and protected;
6. error handling, logs, exports, and diagnostic endpoints do not disclose sensitive payroll, personal, schema, or infrastructure information;
7. security-relevant failures are logged and auditable without leaking secrets or personal data;
8. dead or legacy routes do not retain bypassable security surfaces.

## Required investigation

### 1. Build the route security catalogue

Inventory all backend routes and classify each by:

- route and HTTP method
- router/module
- intended user/role
- authentication dependency
- authorization dependency
- workspace/account identifier source
- resource ownership check
- service/repository call
- SQL tenant predicate
- response sensitivity
- frontend caller or operator-only classification
- security status
- evidence

Cover at minimum:

- workspace setup/configuration
- employees and contracts
- attendance/timesheets
- payroll inputs
- payroll-run creation/list/detail/results
- retry
- approval/lock/pay
- reconciliation
- exports
- audit and execution traces
- diagnostics/ops
- admin routes
- onboarding routes

### 2. Authentication architecture

Trace how identity enters the application and is propagated.

Determine:

- authentication mechanism in use
- token/session validation location
- current-user object contents
- how account/workspace membership is represented
- whether unauthenticated development bypasses exist
- whether route modules consistently apply authentication dependencies
- whether admin/operator routes use stronger checks
- whether frontend route protection is merely cosmetic or backed by server checks

Record missing or inconsistent authentication separately from tenant authorization.

### 3. Tenant-isolation audit

For every material workspace-scoped route, verify the full chain:

```text
request identity
→ account/workspace membership check
→ route resource lookup
→ service/repository call
→ SQL WHERE/JOIN tenant predicate
→ returned or modified rows
```

Check for insecure direct object reference patterns involving:

- workspace ID
- employee ID
- employee-contract ID
- salary-definition ID
- grade/designation ID
- payroll-run ID
- payroll-result ID
- payroll-input ID
- reconciliation ID
- rule-set/statutory-rule ID
- audit/trace identifiers

Do not accept a workspace ID in the path as proof of isolation. Verify the requested child resource belongs to that workspace.

### 4. Unscoped and legacy reconciliation routes (`06-007`)

Inspect:

- `GET /payroll/run/{run_id}/reconcile`
- `POST /payroll/run/{run_id}/reconcile`

Determine:

- whether authentication is required
- whether workspace ownership is derived and checked internally
- whether a user with one workspace can supply another workspace's `run_id`
- whether the route exposes or modifies reconciliation data cross-tenant
- whether it duplicates weaker logic than the workspace-scoped route family
- whether it is reachable through current router registration

Classify each route as:

- secure but obsolete
- insecure/tenant-bypass risk
- unreachable dead code
- indeterminate

Do not remove it; hand off removal to Stage 12/13.

### 5. Raw exception disclosure (`07-001`)

Review all 21 known `str(e)`/`str(exc)` response sites individually or by evidence-backed risk class.

For each site record:

- underlying operation
- likely exception classes
- whether raw DB/schema/constraint details can reach the client
- whether personal/payroll values may appear
- whether filesystem, host, SQL, or internal identifiers may appear
- HTTP status used
- whether the frontend renders the message verbatim
- risk classification

Group into:

- confirmed sensitive disclosure
- structurally capable of disclosure
- currently safe developer-authored exception only
- dead/unreachable

Preserve `07-001` as the systemic parent finding; create child findings only where a materially distinct risk warrants it.

### 6. Authorization for configuration and statutory controls

Verify who can modify:

- component metadata
- client component overrides
- `is_active`
- proration strategy
- salary definitions
- pay-cycle configuration
- payroll rules/rule sets
- attendance policies
- public holidays
- statutory-component enablement/disablement

For `03-004` / `08-003`, determine whether:

- ordinary workspace users can disable statutory deductions
- only privileged roles can do so
- role checks exist server-side
- changes are audited
- cross-workspace changes are prevented
- direct API calls bypass UI restrictions

Do not decide whether statutory components should be disableable; assess access control and accountability only.

### 7. Privileged lifecycle operations

Verify authorization for:

- creating payroll runs
- retrying runs
- approving
- locking
- marking paid
- reconciling
- resolving mismatches
- exporting payroll and bank files
- viewing audit logs and traces

Determine whether role distinctions exist and are enforced, or whether any authenticated workspace member can perform every operation.

Where intended roles are undocumented, record a human-decision requirement rather than inventing policy.

### 8. Admin, operator, and diagnostic surfaces

Inspect:

- `admin.py` routes
- onboarding/admin dashboards
- legacy executor stats
- diagnostic endpoints
- health/debug endpoints
- any scripts or routes exposing database state

Determine:

- authentication and authorization
- deployment reachability
- sensitive data returned
- tenant scoping
- whether routes are intended for internal networks only
- whether environment/configuration accidentally exposes them publicly

### 9. Export and report security

Verify tenant and authorization controls for all export routes, including:

- bank upload
- PAYE
- pension
- full detail
- any legacy export functions/routes

Assess:

- cross-workspace run ID access
- inclusion of unnecessary personal/payroll data
- filename/header information leakage
- formula/CSV injection risks from employee-controlled text fields
- content-type and download handling
- auditability of export actions

Do not generate or retain real sensitive exports.

### 10. Audit, trace, and error-data exposure

Inspect whether APIs/UI expose:

- stack traces
- SQL or constraint names
- internal filesystem paths
- raw input payloads
- salary values beyond the viewer's authorization
- personal identifiers
- secrets/tokens
- cross-workspace trace or audit rows

Review:

- `error_message`
- `component_trace_jsonb`
- `execution_trace`
- `audit_log`
- `event_store`
- reconciliation notes
- timesheet audit output

### 11. Logging and secret handling

Review configuration and code for:

- credentials or tokens committed to the repository
- secrets in environment examples or defaults
- database URLs in logs/errors
- personal/payroll data logged unnecessarily
- authentication tokens logged
- insecure debug logging
- `print()` of sensitive state
- overly permissive CORS or trusted-host configuration

Do not report secret values verbatim in findings. Redact and cite location/type only.

### 12. Cross-workspace relational consistency

Extend Stage 08's targeted checks where security impact exists.

Verify whether schemas or writes can create combinations such as:

- payroll result employee from workspace A attached to run in workspace B
- payroll input employee/workspace mismatch
- contract references to salary definition/grade/designation from another workspace
- reconciliation linked to mismatched workspace/run
- snapshot rows linked to the wrong employee/workspace

Distinguish:

- schema-permitted but no application path
- application-path reachable
- blocked by FK/constraint
- blocked only by route/service checks

### 13. Controlled non-production verification

Use controlled, self-cleaning checks only where static analysis is insufficient.

Candidate checks:

- call a workspace-scoped endpoint with a valid resource ID from another workspace
- call the unscoped reconciliation route using another workspace's run ID
- trigger representative raw exceptions and inspect sanitized/unsanitized responses
- attempt a statutory-component override across workspace boundaries
- access export, audit, and trace endpoints cross-workspace

Constraints:

- no destructive testing
- no brute force
- no credential attacks
- no production/shared data
- verify zero residue
- stop after proving or rejecting the specific hypothesis

## Required outputs

At minimum produce:

1. Route security catalogue
2. Authentication architecture summary
3. Tenant-isolation matrix by major domain
4. IDOR/resource-ownership register
5. `06-007` unscoped reconciliation security assessment
6. `07-001` 21-site disclosure-risk classification
7. Configuration/statutory-control authorization assessment
8. Privileged lifecycle-operation role matrix
9. Admin/operator/diagnostic exposure register
10. Export/report security assessment
11. Audit/trace/error-data exposure matrix
12. Logging, CORS, and secret-handling assessment
13. Cross-workspace relational-risk register
14. Positive-control register for correctly isolated routes
15. Findings using `_core/finding-schema.md`
16. Evidence under `docs/audit-program/09-security-tenant-isolation/evidence/`
17. Handoff notes for Stages 10, 11, 12, and 13

## Finding rules

Keep separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Use exactly one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not classify a route as insecure merely because `workspace_id` is absent from the path; verify internal ownership checks.

Do not classify UI role hiding as authorization unless the backend independently enforces it.

Do not include actual secret values, raw personal data, or exploit-ready sensitive payloads in audit documentation.

A dead route can still be a security defect if it is registered and reachable.

## Constraints

- Read-only audit stage.
- Do not modify backend or frontend code.
- Do not modify migrations.
- Do not modify tests or scripts.
- Do not rotate or expose secrets.
- Do not perform destructive penetration testing.
- Do not start Stage 10.
- Do not reopen remediated `04-001` or `05-001` without regression evidence.
- Do not resolve the `03-004` product-policy decision; assess authorization and auditability only.

## Completion criteria

Stage 09 is ready for human review only when:

- all material route families are security-classified or explicitly marked not investigated
- authentication and authorization mechanisms are mapped
- tenant ownership is verified at route/service/repository/SQL layers for high-value payroll operations
- `06-007` has a final security classification
- the 21 `07-001` sites are grouped by evidence-backed disclosure risk
- privileged lifecycle and configuration actions have a role/authorization assessment
- exports, audit, trace, and diagnostic surfaces are reviewed
- security-relevant cross-workspace relational risks are assessed
- every finding uses a valid status and evidence reference
- handoffs exist for Stages 10–13 as applicable

## Publication

When the investigation is complete:

1. Create `findings.md` and the `evidence/` directory under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 09 `in-progress`
   - set opened date to today
   - set next action to human review of Stage 09
   - preserve all completed stages and remediation records
3. Leave Stage 09 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 09 audit documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 09 — Security and tenant isolation
Status: in-progress, awaiting review
Primary file: docs/audit-program/09-security-tenant-isolation/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Headline security gaps:
- Confirmed tenant-isolation defects: <count>
- Authorization/role gaps: <count>
- Information-disclosure findings: <count>
- Insecure legacy/diagnostic routes: <count>
```
