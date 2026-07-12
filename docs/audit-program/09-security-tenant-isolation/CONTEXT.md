# Stage 09 — Security and Tenant Isolation

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Determine whether authentication, authorization, tenant scoping, privileged operations, error handling, exports, diagnostics, and data-access paths protect payroll and personal data consistently.

This is a read-only audit stage. Do not modify application code, migrations, tests, scripts, secrets, or data.

## Confirmed handoff state

- Stages 01–08 are complete.
- `04-001` and `05-001` remain remediated.
- `07-001` identified 21 raw-exception response sites.
- `06-007` identified legacy unscoped reconciliation routes.
- `03-004` / `08-003` remain an open product-policy question concerning whether statutory components may be disabled; Stage 09 assesses access control only.
- `04-002` and retry-trace design remain Stage 10 inputs.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is authoritative.

## Investigation scope

Stage 09 must assess:

1. authentication architecture and caller identity;
2. account/workspace membership and role representation;
3. tenant isolation at route, service, repository, and SQL levels;
4. run lifecycle operations: create, retry, approve, lock, pay, reconcile;
5. configuration and statutory-control authorization;
6. admin, operator, diagnostic, audit, trace, and export surfaces;
7. raw exception, log, CORS, secret, and personal-data exposure;
8. insecure legacy or decorative-scoping routes;
9. cross-workspace resource access and IDOR patterns;
10. positive controls where workspace ownership is correctly enforced.

## Required outputs

Maintain in `findings.md` and `evidence/`:

- route security catalogue;
- authentication and role-model assessment;
- tenant-isolation and IDOR register;
- `06-007` final classification;
- `07-001` disclosure-risk grouping;
- privileged-operation role matrix;
- admin/diagnostic exposure register;
- export and CSV-injection assessment;
- audit/trace/error exposure matrix;
- logging, CORS, and secret-handling assessment;
- positive controls;
- handoffs for Stages 10–13.

## Finding rules

Use one status only:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not treat a `workspace_id` path segment as tenant enforcement unless it reaches an ownership check and scoped query. Do not treat UI visibility as authorization. Do not record real secret values or personal data.

---

## Close-review instruction

Use this section after the initial Stage 09 findings have been committed and presented for human review.

### Human decisions

#### Decision 1 — application authentication

`09-000` is an **unrecognized S0 production blocker**, not an intentionally accepted network-only architecture.

- Application-level authentication and server-side authorization are mandatory before any live or production-data use.
- Network, VPN, reverse-proxy, firewall, or private-subnet controls may be retained as defence in depth, but they do not replace application identity, membership, and authorization checks.
- Development environments may support an explicit, disabled-by-default local bypass, but production must fail closed when authentication configuration is absent.

#### Decision 2 — tenancy and role model

The intended operating model is:

- one **bureau account** can manage multiple client **workspaces**;
- every user is authenticated and belongs to an account;
- access to workspaces is explicit through membership, not inferred from a caller-supplied UUID;
- the current product scope is bureau-operated, not direct client self-service;
- the model must remain extensible to workspace-scoped client users later without redesigning tenancy.

Minimum roles for backlog/design purposes:

1. **Platform administrator** — platform-wide operational administration; not an ordinary payroll user.
2. **Bureau administrator** — account/workspace membership, configuration, and user administration across permitted workspaces.
3. **Payroll operator** — employee/input maintenance, run creation, retry, reconciliation preparation, and exports for assigned workspaces.
4. **Payroll approver** — approve, lock, resolve reconciliation where permitted, and authorize payment-state transitions; separation from preparation should be supported.
5. **Read-only auditor/viewer** — results, traces, audit history, and reports without mutations.

A single person may hold multiple roles in the initial client deployment, but the system must enforce permissions as roles rather than hard-code a single-operator assumption.

Direct client-workspace users are out of the current MVP scope, but future membership must be constrainable to one or more explicit workspaces.

### Review conclusions to accept

- `09-000` remains confirmed S0: no application authentication or caller identity exists.
- `09-001` remains confirmed S0: unauthenticated `GET /workspaces` enumerates all tenants and enables downstream attacks.
- `09-002` remains confirmed S0: retry, approve, lock, pay, and legacy reconcile use global `run_id` without caller/workspace authorization.
- `09-004` remains confirmed S1: scoped reconciliation routes accept but discard `workspace_id`.
- `09-005` remains confirmed S1: timeline/trace accepts but discards `workspace_id`.
- `09-006` remains confirmed S1: legacy executor stats returns global cross-workspace data.
- `09-007` remains confirmed S1: predictable admin dashboards are unauthenticated; infrastructure reachability may affect exposure but not the code-level finding.
- `09-008` remains confirmed S2: employee-controlled text reaches CSV exports without spreadsheet-formula sanitization.
- `06-007` is finalized as insecure/tenant-bypass risk and remains a Stage 12 removal candidate after secure replacement paths exist.
- `07-001` remains S1: 10 of 21 sites are structurally capable of raw DB/schema disclosure; 11 currently catch controlled developer-authored exceptions.
- No committed secrets and correctly scoped employee/export guards remain positive controls.
- `03-004` remains an open product-policy decision. Stage 09 only confirms that currently anyone reaching the API can modify the control and that no role model or audit trail protects it.

### Required backlog/design handoff

Stage 13 must treat security remediation as a sequenced programme, not isolated route patches:

1. Introduce authentication and account/workspace membership.
2. Introduce centralized authorization dependencies/policies and the role model above.
3. Make workspace ownership checks mandatory for every child resource and lifecycle operation.
4. Replace or remove unscoped/decoratively scoped routes.
5. Restrict `/admin*` and diagnostics to platform-admin/operator roles and deployment controls.
6. Sanitize Group A raw exceptions and log full details server-side.
7. Add security audit events for privileged changes and lifecycle transitions.
8. Add CSV-injection protection.
9. Add regression scenarios for cross-workspace enumeration, reads, mutations, exports, and lifecycle transitions.

Do not authorize production/live-data use merely because individual tenant predicates exist on some routes. The platform remains unsafe until caller identity, membership, and authorization are enforced consistently.

### Close the stage

Update:

- `docs/audit-program/09-security-tenant-isolation/findings.md`
  - change status to `complete`;
  - resolve both human decisions using the decisions above;
  - preserve finding severities and evidence;
  - add the final operating-model and remediation-sequencing handoff.
- `docs/audit-program/_core/human-decisions.md`
  - mark the authentication-scope and tenancy/role-model questions resolved.
- `docs/audit-program/audit-state.md`
  - mark Stage 09 `complete` and set the closed date;
  - set next action to open Stage 10 — Execution-trace remediation design;
  - leave Stage 10 not started;
  - record `09-000`, `09-001`, and `09-002` as S0 production blockers for Stage 13;
  - carry `09-004`, `09-005`, `09-006`, `09-007`, and `07-001` to Stage 13;
  - carry `09-005` specifically into Stage 10's trace-route design;
  - carry `09-008` to Stages 11/13;
  - carry `06-007` to Stages 12/13;
  - preserve `03-004` as open and preserve all prior completed-stage/remediation records.

### Constraints during close review

- Do not implement authentication, authorization, route scoping, exception sanitization, CSV protection, or admin restrictions.
- Do not run destructive cross-tenant tests.
- Do not begin Stage 10.
- Do not create a separate close-review prompt file.

### Publish

Commit and push the Stage 09 closure documentation to `uat`.

Return only:

```text
Stage: 09 — Security and tenant isolation
Status: complete
Primary file: docs/audit-program/09-security-tenant-isolation/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Decisions:
- Application authentication and authorization are mandatory before any live/production-data use; network controls are defence in depth only.
- Intended model: authenticated bureau users, one bureau account managing multiple client workspaces, explicit membership and RBAC; direct client users deferred but supported by the tenancy design.

Next stage:
10 — Execution-trace remediation design
```
