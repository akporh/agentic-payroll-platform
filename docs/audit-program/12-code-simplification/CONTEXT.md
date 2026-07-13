# Stage 12 — Code Simplification

**Status:** not started (see [`../audit-state.md`](../audit-state.md))

## Purpose

Identify code, schema, route, repository, migration, trace, and documentation structures that can be safely removed, consolidated, renamed, or made single-source without changing intended payroll behaviour.

This stage must distinguish between:

- dead code
- unreachable code
- superseded code
- duplicated implementations
- duplicated data extraction or transformation logic
- temporary compatibility code that is now permanent by accident
- unused schema columns or tables
- misleading names or comments
- defensive code that is still required
- security-sensitive code that must not be removed before replacement controls exist
- product features that appear unused but remain intentionally deferred

The objective is a bounded simplification backlog with dependency-aware deletion/consolidation plans. This is a read-only audit/design stage: do not perform the cleanup.

## Confirmed handoff state

- Stages 01–11 are complete.
- `04-001` and `05-001` are remediated and protected by passing regression tests.
- Stage 11 baseline: 306 passed, 1 skipped; no new distinct defect was found.
- Stage 09 authentication, membership, RBAC, and ownership controls remain unimplemented S0 production blockers. Do not simplify away temporary security evidence or guards before replacement controls exist.
- Stage 10 execution-trace remediation design is approved but unimplemented.
- `06-007` / `09-002`: legacy unscoped reconciliation routes are reachable, insecure, and superseded by workspace-scoped routes. They are prime removal candidates, but removal must be sequenced with callers/tests and the broader security package.
- `07-004`: stray module-scope `print()` in `backend/domain/rules/paye.py` is a confirmed S3 cleanup item.
- Stage 05 simplification handoffs remain open:
  - `05-002`: `employee_contract_snapshot.components_jsonb` is captured but unread;
  - `05-003`: snapshot/live extraction responsibilities are duplicated or ambiguous;
  - `05-005`: duplicated extraction logic across calculation paths.
- Stage 01 open architecture questions remain relevant:
  - duplicated repository structures (`backend/infra/repositories/` and `backend/infra/db/repositories/`);
  - legacy executor fallback when component metadata is empty;
  - reference-only `docs/wrapper-command/` must not be treated as authoritative runtime instruction.
- `05-004` snapshot immutability harmonisation belongs to Stage 13 and must not be mistaken for simple deletion.
- `03-004` statutory-component disablement remains an unresolved product-policy question; do not simplify away the mechanism or guard placeholder until Stage 13 decides policy.
- `CLAUDE.md` is authoritative.

## Required inputs

Read before investigation:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files under `docs/audit-program/_core/`
- Stage 01 findings and system inventory
- Stage 02 findings for execution and diagnostic paths
- Stage 03 findings for duplicated configuration representations
- Stage 05 findings, especially `05-002`, `05-003`, `05-005`
- Stage 06 findings, especially `06-007`
- Stage 07 findings, especially `07-004`
- Stage 08 findings for source-of-truth and immutability distinctions
- Stage 09 findings for security-sensitive legacy/admin routes
- Stage 10 findings for the approved trace taxonomy and migration design
- Stage 11 findings for current tests and coverage gaps

## Objective

Produce a simplification plan that answers:

1. Which code paths are provably unused or superseded?
2. Which duplicated implementations can be consolidated behind one canonical service/repository/helper?
3. Which schema fields are dead, write-only, or misleading?
4. Which routes can be removed without losing supported functionality?
5. Which compatibility/fallback paths are still required?
6. Which names, comments, and documentation contradict current behaviour?
7. Which cleanup items are independently safe versus blocked by security, trace, policy, or migration work?
8. What tests or evidence are required before deletion?

## Required investigation

### 1. Build the simplification candidate inventory

Search across backend, frontend, migrations, tests, scripts, and audit/reference documentation for:

- unused functions/classes/modules
- duplicate functions with materially identical logic
- unused imports and constants
- dead route handlers
- registered-but-no-caller routes
- frontend components/types with no route or consumer
- schema columns never read
- tables only written, never read
- migration compatibility branches that can no longer execute
- stale TODO/FIXME comments
- obsolete feature flags/fallbacks
- duplicate serialization or extraction helpers
- duplicate state/status mappings
- duplicate SQL/repository layers
- diagnostic scripts superseded by tests or newer scripts

For each candidate record:

- location
- current writers/callers/readers
- evidence of non-use or duplication
- behavioural/security dependency
- deletion/consolidation proposal
- tests required
- risk
- recommended stage/sprint

### 2. Repository-layer duplication (`01-002`)

Map both repository structures:

- `backend/infra/repositories/`
- `backend/infra/db/repositories/`

Determine:

- modules/classes/functions in each
- actual imports/callers
- ORM vs raw SQL responsibilities
- overlapping entities/operations
- transaction ownership
- whether one directory is legacy, experimental, or intentionally separate
- whether naming alone is misleading

Recommend one of:

- consolidate into one canonical repository layer;
- retain both with explicit bounded responsibilities and rename/document them;
- remove an unused layer;
- defer because active call graphs are too intertwined.

Do not make changes.

### 3. Legacy executor and fallback simplification (`01-004`)

Trace all paths into the legacy executor, including the empty-`component_metadata` fallback.

Determine:

- whether the fallback still runs in current data/tests
- whether it is required for legacy workspaces/runs
- whether an empty metadata set represents valid legacy state or invalid configuration
- whether the fallback masks configuration defects
- current metrics/diagnostic dependencies
- whether Stage 10 event taxonomy changes affect fallback monitoring

Produce options with consequences:

- retain with explicit contract and telemetry;
- hard-fail on empty metadata;
- migrate legacy configuration then remove;
- retain only for historical replay, not new runs.

If product intent remains genuinely ambiguous, preserve it as a human decision for Stage 13 rather than choosing silently.

### 4. Snapshot schema and extraction cleanup (`05-002`, `05-003`, `05-005`)

Investigate:

- `employee_contract_snapshot.components_jsonb`
- all writers/readers of employee contract, salary definition, component metadata, and client override snapshots
- duplicated extraction/building logic across original run, retry, snapshot service, executor, and persister
- fields captured but never consumed
- fields recomputed from live tables despite snapshot presence
- naming that implies stronger use than exists

For each item distinguish:

- safe dead-column removal
- future-use field required by an approved design
- duplication suitable for one shared helper/service
- behaviour difference that prevents consolidation
- cleanup blocked by historical-reproducibility or migration concerns

Do not remove snapshots or weaken immutability.

### 5. Legacy and superseded route cleanup (`06-007` / `09-002`)

Inspect all legacy/unscoped route pairs and compare them with current workspace-scoped routes.

At minimum cover:

- legacy reconciliation GET/POST routes
- unscoped retry/approve/lock/pay routes
- old aliases or duplicate endpoint families
- admin/operator HTML routes
- diagnostic/legacy-executor routes

For each route determine:

- registered/reachable
- frontend caller
- script/test caller
- external compatibility evidence
- current security risk
- canonical replacement
- removal prerequisites
- deprecation requirement

Do not recommend removing lifecycle routes solely because they are unscoped if no scoped replacement exists yet; those require security redesign, not simple deletion.

### 6. Trace and event-code literal consolidation

Using Stage 10’s approved design, inventory current free-text `ExecutionTracer.step()` names and repeated literals.

Design a simplification approach for future implementation:

- one canonical event-code enum/constants module
- human-readable labels separated from stable codes
- mapping for existing legacy step names
- removal of scattered string comparisons
- update path for `legacy_executor_fallback` statistics

Do not implement the Stage 10 design here.

### 7. Error/status/type duplication

Inspect duplicated representations of:

- payroll run statuses across database, backend enums, Pydantic models, frontend types, badges, and action panels
- component classes
- retry strategy values
- reconciliation statuses
- export types
- attendance codes
- event names

Identify drift-prone manual lists and recommend generated/shared-contract or central-constant approaches where feasible.

Keep language/runtime boundaries practical; do not recommend complex code generation without clear benefit.

### 8. Duplicate business-rule and extraction logic

Search for repeated implementations of:

- statutory snapshot extraction
- component metadata merge/override precedence
- employee/contract selection
- run-total recomputation
- error-to-HTTP translation
- workspace/run ownership checks
- export row construction
- audit/event creation
- retry/original calculation context construction

Determine whether duplicates are:

- identical and consolidatable
- intentionally different by lifecycle
- already drifting
- suitable for shared pure helper
- suitable for service-level abstraction
- too coupled to consolidate safely

### 9. Frontend dead code and contract drift

Review frontend routes/components/types for:

- no caller or no navigation entry
- backend feature no longer supported
- duplicate API client functions
- stale enum/status types
- obsolete action controls
- components that always return `null`
- unused legacy admin/debug UI

Do not classify intentionally deferred Stage 13 UI work as dead code.

### 10. Logging, debug, and diagnostics cleanup

Inventory:

- `print()` calls, including `07-004`
- debug-only logging in production paths
- duplicate logging of the same exception
- diagnostic endpoints/scripts superseded by tests
- stale developer comments
- one-off evidence scripts outside audit directories

Classify as:

- remove now
- replace with structured logging
- retain as operational diagnostic
- move to test/evidence tooling
- security-sensitive and blocked by auth/restriction work

### 11. Migration hygiene

Review migrations for:

- blanket exception swallowing
- duplicate compatibility guards
- dead downgrade branches
- repeated helper patterns
- migrations whose name/docstring no longer matches actual schema outcome
- multiple migrations implementing the same final constraint

Use `08-001` as the primary caution: simplification must never replace precise guards with broader exception suppression.

Recommend reusable migration conventions, not a rewrite of historical migrations unless required for correctness.

### 12. Documentation and instruction cleanup

Identify:

- stale architecture descriptions
- duplicated instructions
- contradictions with `CLAUDE.md`
- references to removed/renamed routes
- wrapper-command material that may confuse authority
- completed audit instructions that should remain historical versus active operational docs

Do not delete audit evidence/history. Propose archival or authority labels where appropriate.

### 13. Dependency-aware simplification sequencing

Classify every candidate as:

- **independently safe cleanup** — no behavioural change and covered by tests;
- **cleanup bundled with remediation** — best performed while fixing the related defect;
- **blocked by security architecture**;
- **blocked by Stage 10 trace implementation**;
- **blocked by product-policy decision**;
- **requires migration/data backfill**;
- **retain intentionally**.

### 14. Controlled verification

Use static call graphs, imports, route registration, test references, and safe read-only runtime checks.

Do not delete or rename code to see whether tests fail. Where usage cannot be proven, classify the candidate as uncertain and state the verification needed.

## Required outputs

At minimum produce:

1. Simplification candidate register
2. Repository-layer duplication map and recommendation
3. Legacy-executor/fallback options and decision requirement
4. Snapshot dead-field and extraction-consolidation assessment
5. Legacy/superseded route removal matrix
6. Trace literal/event-taxonomy consolidation plan
7. Backend/frontend enum and contract duplication register
8. Business-rule/helper duplication register
9. Frontend dead-code/contract-drift register
10. Logging/debug/diagnostic cleanup register
11. Migration hygiene register
12. Documentation authority/staleness register
13. Dependency-aware cleanup sequence
14. Positive-control register of apparently duplicate structures that are intentionally distinct
15. Findings using `_core/finding-schema.md`
16. Evidence under `docs/audit-program/12-code-simplification/evidence/`
17. Handoff to Stage 13

## Finding rules

Keep separate:

- proven dead or duplicated code
- likely cleanup candidate
- intentionally retained compatibility path
- unresolved product/architecture decision

Use exactly one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

Do not label code dead merely because the frontend has no caller; verify routes, scripts, tests, external compatibility, and historical replay needs.

Do not recommend removal of security-sensitive routes without identifying a secure replacement or explicit retirement plan.

Do not merge code paths whose similar logic has different transactional, snapshot, or lifecycle semantics.

## Constraints

- Read-only audit/design stage.
- Do not modify backend or frontend code.
- Do not modify migrations.
- Do not modify tests or scripts.
- Do not delete routes, columns, tables, docs, or evidence.
- Do not begin Stage 13.
- Do not reopen remediated `04-001` or `05-001` without regression evidence.
- Do not resolve `03-004` or the legacy-executor fallback policy without an explicit human decision.

## Completion criteria

Stage 12 is ready for human review only when:

- high-value backend/frontend/schema/documentation candidates are inventoried;
- repository-layer duplication has an evidence-backed recommendation;
- legacy executor/fallback has bounded options and any needed decision;
- Stage 05 dead-field/duplication handoffs are resolved into removal/consolidation/defer recommendations;
- `06-007` and other route candidates have caller/replacement/prerequisite analysis;
- every candidate has a dependency classification;
- no cleanup proposal weakens security, snapshot integrity, or historical reproducibility;
- Stage 13 handoff contains implementation-ready cleanup packages and acceptance checks;
- every finding uses a valid status and evidence reference.

## Publication

When the investigation is complete:

1. Create `findings.md` and evidence under this stage.
2. Update `docs/audit-program/audit-state.md`:
   - mark Stage 12 `in-progress`;
   - set opened date to today;
   - set next action to human review of Stage 12;
   - preserve all completed stages and remediation records.
3. Leave Stage 12 `in-progress, awaiting review`; do not self-close.
4. Commit and push only Stage 12 audit documentation/evidence and the audit-state update to `uat`.
5. Return only:

```text
Stage: 12 — Code simplification
Status: in-progress, awaiting review
Primary file: docs/audit-program/12-code-simplification/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision or none>

Headline simplification candidates:
- Independently safe cleanup: <count>
- Bundle with remediation: <count>
- Blocked by architecture/policy: <count>
- Retain intentionally: <count>
```
