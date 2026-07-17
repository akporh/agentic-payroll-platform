# Casper Prompt — Begin Stage 06: UI/API/Backend Wiring

Begin Stage 06 — UI/API/Backend Wiring.

## First: verify the handoff

Read:

- `CLAUDE.md`
- `docs/audit-program/README.md`
- `docs/audit-program/WORKFLOW.md`
- `docs/audit-program/audit-state.md`
- all files in `docs/audit-program/_core/`
- `docs/audit-program/03-configuration-integrity/findings.md`
- `docs/audit-program/04-original-run-retry-parity/findings.md`
- `docs/audit-program/05-snapshot-integrity/findings.md`
- `docs/audit-program/remediation/04-001-05-001/summary.md`
- `docs/audit-program/remediation/04-001-05-001/verification.md`

Confirm:

- Stages 01–05 are complete.
- The immediate remediation sprint for `04-001 + 05-001` is complete and approved.
- Stage 06 is unblocked.
- `04-001` and `05-001` are remediated and must not be reopened unless new evidence demonstrates a regression.
- `04-002` remains open for Stages 07/10.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is the governing instruction source.
- `docs/wrapper-command/` is reference-only and non-authoritative.
- Stage 06 is a read-only audit stage.

## Create Stage 06

Create:

```text
docs/audit-program/06-ui-api-backend-wiring/
├── CONTEXT.md
├── findings.md
└── evidence/
```

Populate `CONTEXT.md` before beginning the investigation.

Update `docs/audit-program/audit-state.md`:

- mark Stage 06 `in-progress`
- set opened date to today
- set next action to execute the Stage 06 UI/API/backend wiring audit
- preserve all prior completed-stage and remediation records

## Objective

Establish an evidence-backed wiring map from user-visible UI controls through frontend state, API requests, backend routes/services, persistence, runtime consumers, and returned UI state.

The stage must determine whether features are:

- fully wired end to end
- frontend-only
- API-only
- backend-only
- persisted but not surfaced
- surfaced but not persisted
- saved successfully but ignored at runtime
- returned by APIs but never rendered
- rendered from stale or different fields than those updated
- unreachable because routes, navigation, permissions, or feature flags do not expose them

Do not infer functionality from the existence of a component, route, schema, table, or handler. Verify the complete path.

## Required investigation

### 1. Build the UI/API/backend feature catalogue

Inventory all significant payroll product surfaces, including at minimum:

- workspace setup and onboarding
- workspace configuration
- pay-cycle configuration
- component metadata and client overrides
- salary definitions
- payroll rules and rule sets
- employee registry and employment/contract setup
- attendance-code configuration
- timesheet upload and derivation
- public holidays
- payroll-run creation
- payroll-run list/detail/status display
- retry controls and error display
- payroll result detail and component trace
- reconciliation
- exports and reports
- audit/event history
- operator/diagnostic endpoints
- any backend feature identified in earlier stages as not exposed in the UI

For each feature, record:

- UI page/component
- navigation/route entry point
- user action/control
- frontend state field
- request payload field
- API method and route
- request schema
- route/service/repository chain
- persistence target
- runtime consumer
- API response field
- UI read/display field
- permission/tenant checks
- error handling
- loading/success/failure feedback
- wiring status
- evidence

### 2. Trace every configurable field both directions

For every editable configuration field, verify:

```text
UI control
→ frontend state
→ request payload
→ API schema
→ backend validation
→ service/repository write
→ database field
→ subsequent read API
→ frontend hydration
→ rendered value
→ payroll/runtime consumer
```

Check especially for:

- mismatched field names
- JSON vs dedicated-column drift
- camelCase/snake_case conversion gaps
- omitted optional fields
- defaults applied differently in frontend and backend
- edits writing a different representation from the one runtime reads
- successful API responses masking no-op writes
- API reads that return a different source than the update route modifies

### 3. Revisit known Stage 03 handoffs

Investigate specifically:

- `pay_cycle.definition_json` — identify every UI control that maps to it, or confirm that parts of it are backend-only/unexposed
- any onboarding field written during initial setup but unavailable or inconsistently editable later
- component override fields and their exact UI/API/runtime mapping
- salary-definition editing and the D-ARCH-1 edit lock's user-visible behaviour
- retry strategy visibility and whether users can understand which retry behaviour a run supports

### 4. Verify remediation visibility

Confirm the `05-001` remediation is fully surfaced:

- run detail/list APIs return `FAILED` and `error_message` correctly
- frontend status types accept `FAILED`
- the UI renders `FAILED` distinctly
- the operator-visible `error_message` is actually displayed
- retry/action controls are disabled or absent for terminal `FAILED` runs
- no frontend enum, filter, badge, or status mapping drops or mislabels `FAILED`

This is a wiring verification of the completed remediation, not a reopening of the backend fix.

### 5. Identify backend-only capabilities

Search for backend routes/services with no confirmed frontend caller, including but not limited to:

- timesheet functionality
- reconciliation correction/resolution actions
- trace/detail endpoints
- export endpoints
- diagnostic/ops endpoints
- configuration endpoints
- employee/contract lifecycle actions

For each backend-only capability, classify it as:

- intentionally operator/API-only
- planned but not exposed
- obsolete/dead
- unintentionally missing from UI
- indeterminate, requiring human decision

### 6. Identify frontend-only or dead UI

Search for:

- controls whose handlers are empty, mocked, TODO, disabled, or local-state-only
- components/routes not reachable from navigation
- API calls to missing/obsolete routes
- pages rendering placeholder data
- forms that submit only part of their state
- displayed values never refreshed after save
- stale feature flags or conditional rendering that permanently hides implemented features

### 7. API contract alignment

Compare frontend request/response types with backend Pydantic schemas and actual route responses.

Identify:

- missing fields
- extra ignored fields
- incompatible nullability
- enum mismatches
- date/time format mismatches
- monetary value type mismatches
- response-shape drift
- pagination/filter/sort mismatches
- error-response assumptions that do not match backend behaviour

Use actual code paths and, where safe, controlled API calls against non-production state.

### 8. Tenant and permission wiring

For each major UI/API flow, verify:

- workspace/account ID is supplied from the correct authenticated context
- frontend cannot accidentally call cross-workspace resources
- backend validates tenant ownership independently of UI state
- UI visibility does not substitute for backend authorization
- operator-only routes are not exposed to ordinary workspace users without checks

Record security-relevant findings for Stage 09 without expanding this stage into a full security audit.

### 9. Error and status propagation

Trace representative failures end to end:

- validation error
- not found
- conflict/locked configuration
- payroll run `FAILED`
- retry hard-fail for legacy snapshot
- background calculation failure
- permission failure

Verify whether the UI displays a useful, accurate message or collapses errors into generic failure/toast behaviour.

### 10. Controlled verification

Where feasible, use controlled non-production checks to verify:

- saved values round-trip correctly
- UI payload matches API expectations
- updated values are consumed by the runtime path
- `FAILED` run status and `error_message` are visible
- unavailable actions are correctly disabled

Do not modify production/shared data. Any test data must be self-cleaning and leave zero residue.

## Required outputs

At minimum, produce:

1. UI/API/backend feature catalogue
2. Field-level write/read/runtime matrix
3. Frontend/backend contract mismatch register
4. Backend-only capability register
5. Frontend-only/dead UI register
6. Navigation and reachability map
7. Error/status propagation matrix
8. `FAILED` remediation visibility verification
9. Tenant/permission wiring observations for Stage 09
10. Configuration round-trip findings
11. Findings using `_core/finding-schema.md`
12. Evidence under the Stage 06 `evidence/` folder
13. Handoff notes for Stages 07, 08, 09, 11, 12, and 13

## Finding rules

Keep separate:

- current implementation
- intended behaviour
- suspected or confirmed defect

Use one valid status per finding:

- confirmed
- plausible
- unconfirmed
- rejected
- human decision required

A backend-only feature is not automatically a defect. Confirm whether it is intentionally API/operator-only before classifying it.

A UI control is not considered wired merely because an API call exists; verify persistence, read-back, rendering, and runtime consumption.

## Constraints

- Read-only audit stage.
- Do not modify frontend code.
- Do not modify backend code.
- Do not modify migrations.
- Do not modify tests or scripts.
- Do not implement missing wiring.
- Do not start Stage 07.
- Do not reopen remediated findings `04-001` or `05-001` without new regression evidence.
- Do not expand into a full security audit; record security handoffs for Stage 09.

## Completion and publication

When complete:

1. Check every Stage 06 completion criterion.
2. Leave Stage 06 `in-progress`, awaiting human review.
3. Commit and push only Stage 06 audit documentation and evidence to `uat`.
4. Return only:

```text
Stage: 06 — UI/API/backend wiring
Status: in-progress, awaiting review
Primary file: docs/audit-program/06-ui-api-backend-wiring/findings.md
Audit state: docs/audit-program/audit-state.md
Commit: <SHA>

Important decisions required:
- <decision 1 or none>
- <decision 2 or none>

Headline gaps:
- Backend-only: <count>
- Frontend-only/dead UI: <count>
- Contract mismatches: <count>
- Remediation visibility regressions: <count>
```
