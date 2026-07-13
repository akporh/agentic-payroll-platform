# Stage 13 — Consolidated Remediation Backlog

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Convert the completed Stage 01–12 audit programme into one authoritative, dependency-aware remediation backlog that can be implemented safely in sequenced sprints.

This stage must not merely restate findings. It must produce an execution plan that:

- deduplicates overlapping findings;
- preserves the exact evidence and decisions behind each item;
- separates production blockers from lower-risk hardening and cleanup;
- defines remediation packages with clear scope boundaries;
- sequences architecture, schema, backend, frontend, migration, observability, security, and test work;
- identifies which items may ship independently and which are blocked by prerequisites;
- carries every permanent-test recommendation into the acceptance criteria of its corresponding remediation item;
- defines release gates and rollback requirements;
- distinguishes immediate implementation from deferred policy/product decisions.

Stage 13 is a backlog/design stage only. Do not implement remediation in this stage.

## Confirmed programme state

- Stages 01–12 are complete.
- The `04-001 + 05-001` immediate remediation sprint is complete, reviewed, approved, and regression-protected. Do not reopen it without contradictory evidence.
- Full backend test baseline at Stage 11: **306 passed, 1 skipped**.
- No authentication, account membership, RBAC, or caller-ownership enforcement exists. Stage 09 classified this as an S0 production blocker.
- Application authentication and server-side authorization are mandatory before any live/production-data use. Network controls are defence in depth only.
- Approved tenancy model:
  - one bureau account manages multiple client workspaces;
  - explicit account/workspace membership;
  - minimum roles: platform administrator, bureau administrator, payroll operator, payroll approver, read-only auditor/viewer;
  - direct client users are deferred, but the design must remain extensible to them.
- Stage 10 execution-trace remediation design is approved and canonical.
- Stage 11 live execution strengthened the Stage 09 security evidence and confirmed there are no automated tenant/security regression tests.
- Stage 12 legacy-executor decision is final:
  - retain temporarily with telemetry;
  - inventory and migrate active workspace configuration;
  - prove zero new-run fallback use over an observation window;
  - hard-fail/remove the fallback for new runs;
  - preserve replay-only compatibility only if a real historical-replay requirement is proven.
- `03-004` remains the principal unresolved product-policy decision: whether statutory components may ever be disabled. Stage 13 must present and resolve or explicitly defer this decision.
- `04-004` remains rejected with no remediation required.
- `05-003` (`payroll_result.salary_inputs_snapshot`) is retained intentionally.
- `CLAUDE.md` is authoritative; `docs/wrapper-command/` is reference-only.

## Required inputs

Read before consolidation:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- findings and evidence from Stages 01–12
- `docs/audit-program/remediation/04-001-05-001/summary.md`
- `docs/audit-program/remediation/04-001-05-001/verification.md`
- all recorded human decisions

## Objective

Produce one backlog in which every open item has:

1. canonical ID and title;
2. source finding(s);
3. severity and production/release impact;
4. current evidence class;
5. exact scope;
6. explicit non-scope;
7. dependencies and blockers;
8. implementation sequence;
9. migration/API/UI/operational impact;
10. acceptance criteria;
11. required automated tests;
12. rollback/reversibility requirements;
13. release gate;
14. owner/discipline suggestion;
15. recommended sprint/package;
16. disposition: implement now, defer, retain, rejected, or policy decision.

## Consolidation principles

1. One defect mechanism should appear once in the canonical backlog, even if multiple stages observed it.
2. Preserve all source finding IDs as references.
3. Never downgrade severity merely because implementation is large.
4. Do not promote maintainability cleanup above production blockers.
5. Security controls must be complete enough to authorize the system, not cosmetic route changes.
6. Each remediation package must include its regression tests, not defer testing to a generic later task.
7. Schema changes must include upgrade, downgrade, pre-check/backfill, and verification plans.
8. Frontend fixes must follow backend contracts, not invent parallel status or role models.
9. Do not bundle unrelated items solely to reduce PR count.
10. Prefer small independently verifiable increments within a larger programme.

## Required backlog domains

### 1. Security and tenant-isolation programme — highest priority

Create a sequenced programme covering at least:

#### 1A. Authentication foundation (`09-000`)

Define:

- authentication mechanism and principal model;
- user/account identity tables or provider integration;
- token/session validation;
- backend `current_user` dependency;
- frontend login/session handling;
- unauthenticated response contract (`401`);
- removal of permissive production CORS defaults;
- secure configuration and secret handling.

#### 1B. Account/workspace membership and tenancy

Implement the approved bureau-account model:

- bureau account;
- users;
- account membership;
- workspace entitlement/membership;
- future-compatible direct-client membership;
- platform-administrator path that is explicit and audited.

#### 1C. RBAC

Define the minimum role matrix for:

- workspace discovery;
- employee/contract/configuration changes;
- payroll creation/retry;
- approval;
- lock;
- mark paid;
- reconciliation create/resolve;
- exports;
- traces/audit logs;
- admin/diagnostic access.

Where separation of duties is required but not yet documented, flag it as a policy decision rather than inventing it.

#### 1D. Mandatory ownership checks (`09-001`, `09-002`, `09-004`, `09-005`, `09-006`)

Specify one reusable authorization chain from route to query:

```text
authenticated principal
→ bureau account/role
→ workspace entitlement
→ parent resource ownership
→ child resource ownership
→ workspace-scoped repository query
```

Cover every route family, especially:

- `GET /workspaces`;
- retry/approve/lock/pay;
- reconciliation;
- timeline;
- legacy executor stats;
- exports;
- payroll results/inputs/audit routes.

Use non-disclosing `404` where the approved design requires resource concealment.

#### 1E. Route cleanup and admin restriction (`06-007`, `09-002`, `09-007`)

Separate:

- immediate removal of the zero-caller legacy reconciliation GET/POST pair after final external-integration verification;
- creation and rewiring of secure scoped lifecycle routes before retiring active unscoped routes;
- authentication/RBAC protection for admin dashboards;
- proper workspace filtering for legacy-executor stats.

#### 1F. Exception sanitization (`07-001`)

Specify remediation for all 21 sites:

- 10 broad exception sites: log internal detail, return generic safe error;
- 11 controlled `ValueError`/custom-exception sites: preserve developer-authored safe messages where appropriate;
- optional shared error-to-HTTP helper;
- no raw SQL/schema/constraint/stack details in responses;
- tests for representative Group A and Group B routes.

#### 1G. Audit/event completeness (`07-002` and security-sensitive actions)

Add consistent audit/event entries for:

- reconciliation create/resolve;
- retry completion and run transition per Stage 10 design;
- configuration changes, especially statutory-component enable/disable;
- platform-administrator access where applicable.

#### 1H. CSV formula-injection fix (`09-008`)

Define a reusable export-cell sanitizer for strings beginning with `=`, `+`, `-`, or `@`, applied to all relevant exports. Include exact automated tests derived from Stage 11’s synthetic proof.

#### 1I. Security regression suite

Attach permanent tests to each item. At minimum:

- unauthenticated access denied;
- workspace enumeration scoped;
- cross-workspace run/reconciliation/timeline access denied;
- lifecycle actions denied for wrong workspace/role;
- admin dashboards protected;
- legacy stats scoped;
- authorized read-only auditor access;
- platform admin access explicit/audited;
- direct-client extensibility at design level;
- raw exception sanitization;
- export formula sanitization.

### 2. Execution-trace and per-result auditability package

Use Stage 10 findings as the canonical implementation specification. Treat the following as one bounded package, with auth-dependent portions sequenced appropriately:

- `02-002` / `07-005`: minimal retry trace;
- `04-002`: per-result statutory identity;
- `08-003`: excluded-component visibility;
- `09-005`: tenant-safe timeline access;
- trace event-code consolidation from Stage 12.

Preserve the approved design:

- `execution_trace` additions: `workspace_id`, `event_code`, `operation_type`, `invocation_id`, `employee_id`, `actor_id`, `metadata_jsonb`, `error_class`;
- invocation/preflight, per-employee, and final retry events;
- additive-only event taxonomy;
- `payroll_result.statutory_rule_id` and `statutory_version` populated from frozen context;
- no live-table backfill for legacy results;
- component trace `outcome` states;
- one run-level excluded-component event per distinct component;
- timeline filters, grouping, deterministic ordering, and pagination;
- trace-write failure containment plus structured server log;
- auth dependency for production-safe timeline access.

Convert all 12 Stage 10 scenarios and Stage 11 dispositions into implementation acceptance tests.

### 3. Background-failure reliability (`07-003`)

Define a remediation package for the outer calculation background-task catch:

- persist terminal `FAILED` status where safe;
- populate safe `error_message`;
- create audit/event/trace signal;
- preserve already-committed per-employee outcomes if relevant;
- avoid overwriting a more specific terminal state;
- add an explicit fault-injection seam;
- add the permanent regression test specified by Stage 11.

Clarify interaction with the existing `05-001` snapshot-failure path so the two handlers do not conflict.

### 4. Data-integrity hardening

#### 4A. `employee_number` NOT NULL (`08-001`)

Define:

- production-data pre-check and null-row remediation policy;
- corrective migration;
- precise migration guards, never `EXCEPTION WHEN others`;
- verification that the column is truly NOT NULL;
- update to misleading historical migration documentation/reference;
- migration upgrade/downgrade test;
- schema regression test.

Do not assume the local 11/4,673 ratio represents production.

#### 4B. `payroll_run` immutability window (`08-002`)

Define DB-level protection for financially relevant run totals/period fields at the intended lifecycle point, likely `APPROVED` or `LOCKED` depending on the final invariant.

Specify:

- exact protected columns;
- allowed system-owned transitions;
- interaction with reconciliation/payment;
- migration/trigger design;
- direct SQL regression tests;
- rollback.

If approval-vs-lock policy requires a decision, make it explicit.

#### 4C. Snapshot immutability harmonisation (`05-004`)

Audit and define consistent DB immutability for:

- component metadata snapshots;
- client component metadata snapshots;
- employee contract snapshots;
- uncovered payroll-result fields;
- any Stage 10-added trace/identity fields where appropriate.

Do not weaken existing trigger protection.

#### 4D. Pay-cycle definition configurability (`06-002`)

Define the smallest safe remediation for `pay_cycle.definition_json`:

- expose current value in read APIs;
- allow validated post-onboarding updates where policy permits;
- make precedence with dedicated columns explicit;
- add UI support;
- preserve historical run snapshots;
- add consistency tests.

### 5. Statutory-component policy and control (`03-004` / `08-003`)

Present a bounded policy decision for human approval:

- **forbid disablement of mandatory statutory components**; or
- **allow disablement only through privileged, audited, explicitly justified controls**.

For either option define:

- which component classes/codes are mandatory by supported jurisdiction;
- server-side validation;
- RBAC requirement;
- audit/event entry;
- run-time guard;
- omitted-component trace per Stage 10;
- UI behavior;
- migration/configuration impact;
- tests.

Do not conflate visibility (`08-003`) with permission policy (`03-004`).

### 6. Legacy executor migration-and-removal programme (`01-004`)

Use the Stage 12 decision as binding.

Create phased backlog items for:

1. correct stale documentation/comment;
2. add stable fallback telemetry with workspace/run/country context;
3. inventory production/environment dependency;
4. classify each occurrence;
5. migrate/repair active workspace metadata;
6. observe zero fallback usage for new runs;
7. hard-fail new runs on empty metadata with actionable error;
8. remove default fallback path;
9. isolate replay-only compatibility only if a genuine requirement is proven.

Define the observation-window decision and evidence needed without inventing production figures.

### 7. Frontend/API contract repairs

At minimum include:

#### 7A. `FAILED` run support (`06-001`, `06-004`, Stage 12 status duplication)

- one canonical frontend `PayrollRunStatus` type;
- include `FAILED` and correct `DRAFT`/`PENDING` drift;
- badge styling;
- action panel/recovery guidance;
- error message display;
- API contract tests or generated/shared contract check.

#### 7B. Retry strategy UI (`06-003`)

- remove `FULL_RUN` as a selectable option while backend supports only `PER_EMPLOYEE`;
- prevent future drift through a single source or API-driven option list;
- add frontend test.

#### 7C. Timesheet audit UI (`06-006`)

- expose the existing backend timesheet-audit route in an operator workflow;
- define access control under the new RBAC model;
- add UI/API tests.

#### 7D. Salary-definition edit UX (`06-005`)

Keep as optional polish/no required remediation unless included opportunistically. Do not elevate it above confirmed defects.

### 8. Code simplification package

Create bounded low-risk cleanup items from Stage 12:

- rename/document ORM onboarding-readiness repository layer;
- remove dead `employee_contract_snapshot.components_jsonb` with migration;
- extract shared statutory-rate helper;
- remove stray `paye.py` print;
- rename/manual-label `backend/scripts/test_*.py` utilities;
- remove legacy unscoped reconciliation pair after external-integration check;
- correct stale comments/docstrings;
- centralize trace event-code constants when Stage 10 lands;
- optional shared error-to-HTTP helper with `07-001`.

For each item specify whether it is:

- independent quick win;
- bundled with a defect remediation;
- blocked by architecture;
- intentionally retained.

Preserve intentional retentions:

- `payroll_result.salary_inputs_snapshot`;
- differing retry/original context construction;
- operational load/simulation/backfill scripts;
- `docs/wrapper-command/` as reference-only history;
- `03-004` mechanism until policy resolution.

### 9. Test and CI programme

Integrate the eight Stage 11 permanent-test recommendations into the related backlog items, and additionally define programme-level checks:

- tenant/security test suite;
- migration upgrade/downgrade smoke test against scratch schema;
- schema invariant tests;
- lifecycle/immutability direct-DB tests;
- background-failure fault injection;
- Stage 10 retry trace/statutory identity tests;
- CSV export sanitization tests;
- frontend status/role/route tests;
- regression run of the complete current suite.

Do not create a generic “add tests later” task detached from remediation.

## Required prioritisation model

Classify each canonical backlog item by:

### Severity

- S0 production blocker
- S1 serious security/auditability risk
- S2 material integrity/operability risk
- S3 cleanup/polish

### Release gate

- must complete before any live/production-data use;
- must complete before first production payroll run;
- must complete before enabling a specific feature;
- post-launch hardening;
- optional cleanup.

### Effort

Use relative sizing only:

- XS
- S
- M
- L
- XL

Explain uncertainty and do not convert sizes into time estimates.

### Dependency

At minimum:

- independent;
- requires auth foundation;
- requires membership/RBAC;
- requires schema migration;
- requires policy decision;
- requires production-data inventory;
- requires Stage 10 trace schema;
- bundle with another item.

## Required sequencing

Produce a recommended multi-sprint sequence. At minimum evaluate this order:

### Programme 0 — Keep current remediation green

- preserve `04-001`/`05-001` tests;
- no regression during subsequent work.

### Programme 1 — Authentication and tenancy foundation

- auth;
- account/workspace membership;
- RBAC;
- secure CORS/configuration;
- current-user propagation.

### Programme 2 — Mandatory route ownership and security closure

- workspace enumeration;
- lifecycle operations;
- reconciliation/timeline/stats;
- admin restriction;
- legacy route removal;
- security tests.

### Programme 3 — Error/export/audit hardening

- exception sanitization;
- CSV sanitization;
- audit/event gaps.

### Programme 4 — Data-integrity corrections

- employee number;
- run immutability;
- snapshot immutability;
- pay-cycle configuration.

### Programme 5 — Execution trace and auditability

- schema/write-side components that can ship independently;
- auth-dependent timeline portion after Programmes 1–2;
- Stage 10 tests.

### Programme 6 — Statutory policy and legacy-executor transition

- resolve `03-004`;
- fallback telemetry/inventory/migration/removal.

### Programme 7 — Frontend completeness and operator workflows

- FAILED run support;
- retry option correction;
- timesheet audit UI;
- role-aware UI.

### Programme 8 — Simplification and cleanup

- safe cleanup items and documentation.

You may recommend a different ordering where evidence supports it, but explain all deviations.

## Required backlog artefacts

At minimum produce:

1. Executive remediation summary
2. Canonical finding-to-backlog crosswalk
3. Deduplicated backlog register
4. S0/S1 production-release gate
5. Security programme specification
6. Trace/auditability package specification
7. Data-integrity package specification
8. Statutory-policy decision pack
9. Legacy-executor transition plan
10. Frontend/API repair package
11. Simplification package
12. Test/CI acceptance matrix
13. Dependency graph
14. Recommended sprint sequence
15. Migration register
16. API/UI impact register
17. Rollback and operational-readiness register
18. Deferred/retained/rejected register
19. Residual-risk statement
20. Programme completion criteria
21. Evidence references back to Stages 01–12

## Finding crosswalk requirements

Explicitly include all open or disposition-relevant items, including at least:

- `01-002`, `01-004`
- `02-002`
- `03-004`
- `04-002`
- `05-002`, `05-003`, `05-004`, `05-005`
- `06-001`, `06-002`, `06-003`, `06-004`, `06-005`, `06-006`, `06-007`
- `07-001`, `07-002`, `07-003`, `07-004`, `07-005`
- `08-001`, `08-002`, `08-003`
- `09-000`, `09-001`, `09-002`, `09-004`, `09-005`, `09-006`, `09-007`, `09-008`
- Stage 10 approved package
- Stage 11 eight permanent-test recommendations
- Stage 12 frontend-status finding and cleanup candidates

Also list:

- remediated/closed: `04-001`, `05-001`;
- rejected/no action: `04-004`;
- intentionally retained: `05-003` and the Stage 12 retained items.

## Decision handling

Stage 13 must surface only genuine remaining human decisions. At minimum assess:

1. `03-004`: mandatory statutory-component disablement policy.
2. `08-002`: exact lifecycle point for payroll-run DB immutability if not already implied by invariant documentation.
3. Legacy-executor observation-window/cutover evidence threshold, if operational policy is not already defined.
4. Separation-of-duties details between payroll operator and approver, if required before RBAC implementation.

Provide bounded options and a recommended choice for each. Do not leave broad open-ended questions.

## Constraints

- Read-only backlog/design stage.
- Do not modify backend or frontend code.
- Do not modify migrations, tests, scripts, schema, or data.
- Do not begin remediation implementation.
- Do not reopen `04-001`/`05-001` without regression evidence.
- Do not reclassify `04-004` as open.
- Do not treat network restrictions as a substitute for application authorization.
- Do not use local dev-data prevalence as production prevalence.
- Do not omit tests, rollback, or release gates from implementation packages.

## Completion criteria

Stage 13 is ready for human review only when:

- every Stage 01–12 finding is crosswalked to implement/defer/retain/rejected/remediated;
- duplicate findings are consolidated without losing source references;
- all S0/S1 items have implementation-ready packages;
- release blockers are explicit;
- security remediation is sequenced before live/production use;
- Stage 10 design is converted into a bounded implementation package;
- all eight Stage 11 test recommendations are embedded in relevant acceptance criteria;
- the Stage 12 fallback decision is converted into a phased programme;
- genuine remaining decisions have bounded options and recommendations;
- every package has dependencies, tests, migration/API/UI impact, rollback, and release gate;
- residual risk and deferred scope are explicit;
- no application code or data has changed.

## Publication

When the investigation is complete:

1. Create `findings.md` and any supporting outputs/evidence under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 13 `in-progress`;
   - set opened date to today;
   - set next action to human review of Stage 13;
   - preserve all completed stages, decisions, and remediation records.
3. Leave Stage 13 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 13 documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 13 — Consolidated remediation backlog
Status: in-progress, awaiting review
Primary file: docs/audit-program/13-consolidated-remediation-backlog/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Backlog summary:
- S0 production blockers: <count>
- S1 serious risks: <count>
- S2 material risks: <count>
- S3 cleanup/polish: <count>
- Remediation programmes: <count>
- Independently shippable quick wins: <count>
```
