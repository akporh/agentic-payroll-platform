# Artefact 11 — Drift Log

> This log records every conflict found between existing documentation and the actual code,
> and every place where the code itself was ambiguous or incomplete.
> Entries are ordered by severity: Critical first, then Warnings, then Ambiguities.

---

## Critical — Conflicts or Gaps That Could Cause Design Errors

### DRIFT-1 — `personal_details_encrypted` Is Not Demonstrably Encrypted

**Claim in field name:** The column is called `personal_details_encrypted`, implying the values are encrypted.

**Observed in code:** The CSV export routes read bank details and statutory identifiers directly from the JSONB field using plain dictionary access — `biodata.get("BANK", "")`, `biodata.get("TIN", "")`, `biodata.get("RSA", "")`, `biodata.get("ACCOUNT_NUMBER", "")`. No decryption call is made.

**Implications:**
1. Either encryption is not implemented (the name is aspirational).
2. Or decryption is handled transparently at the PostgreSQL/ORM layer — but no such configuration is visible in the codebase.

**Design impact:** The UI/UX design brief for data handling must not assume these fields are protected. Until encryption is confirmed, treat all personal_details values as plaintext PII in transit and at rest.

---

### DRIFT-2 — No RBAC Is Implemented in the Backend

**Implication in documentation / design intent:** The actor list (Artefact 4) describes distinct roles with different access levels: Bureau Admin, Payroll Operator, Finance Authoriser, HR Admin.

**Observed in code:** Zero role checks in any route handler. No auth middleware is imported or applied in any route file. The `X-Performed-By` header is optional and defaults to `"admin@internal"`. Any caller who knows a `workspace_id` can perform any operation on that workspace — including Approve, Lock, Pay.

**Design impact:** The UI can enforce access visually (hide buttons, separate views by role), but the backend does not enforce it. Any RBAC the UI implements is bypassed by a direct API call. This must be flagged as a security gap if the platform is to be used in production by multiple people.

---

### DRIFT-3 — Reconciliation Endpoint: Two Different Route Patterns for Same Operation

**Issue:** There are two sets of reconciliation endpoints:
1. Legacy (no workspace scope): `POST /payroll/run/{run_id}/reconcile`, `GET /payroll/run/{run_id}/reconcile`
2. Workspace-scoped (current): `POST /{workspace_id}/payroll/runs/{run_id}/reconciliation`, `GET /{workspace_id}/payroll/runs/{run_id}/reconciliation`, `PATCH /{workspace_id}/payroll/runs/{run_id}/reconciliation`

**The frontend API client (`payroll.ts`) uses the workspace-scoped routes.** The legacy routes appear to still exist and could be called by external systems.

**The field names also differ:**
- Legacy: `actual_total` in request body
- Workspace-scoped: `actual_payment` in request body

**Design impact:** The UI must use the workspace-scoped routes. Document the legacy routes as deprecated. The UI should never send `actual_total` — it must send `actual_payment`.

---

### DRIFT-4 — `workspace/info` Is Not Workspace-Scoped

**Observed:** `GET /workspace/info` returns data for the **first workspace found** (`LIMIT 1`) — no workspace_id parameter. This is not a multi-tenant-safe endpoint.

**Design impact:** Do not use this endpoint for any functional UI screen. It may be a development/debugging endpoint. The Bureau Dashboard should use `GET /workspaces` instead.

---

## Warnings — Ambiguities That May Affect Design Decisions

### DRIFT-5 — Payroll Run Creation Is Synchronous or Asynchronous? Unknown.

**Issue:** The `POST /payroll/run` endpoint calls `execute_and_persist()` which runs the full calculation pipeline. The route does not return until the calculation completes. This means a run for 500 employees would block the HTTP response for potentially minutes.

**Not observed:** Any background task queue, async job system, or WebSocket notification.

**Design impact:** The frontend must either handle a long synchronous wait (show a loading spinner for the full duration) or implement polling. If polling, the run list endpoint (`GET /{workspace_id}/payroll/runs`) must return in-progress runs in CALCULATING status. Verify whether the run is actually created atomically before the calculation completes, or only after.

---

### DRIFT-6 — `DRAFT` Status in Payroll Run Is Never Created by the API

**Observed:** The PayrollRunStatus enum includes `DRAFT`, and the DB trigger references it. However, the `POST /payroll/run` route immediately moves to `CALCULATING` — there is no endpoint to create a run in DRAFT state for later submission.

**Design impact:** Do not design a "draft run" workflow in the UI — it is not supported. The run status immediately moves to CALCULATING on creation.

---

### DRIFT-7 — Workspace Status `account_id` Field Is in the Model but Not in API Responses

**Observed in model:** `workspace` table has an `account_id` column (FK).

**Observed in routes:** No endpoint returns `account_id`. The create, list, and detail routes omit it entirely.

**Design impact:** `account_id` may represent a higher-level account grouping (e.g. for multi-bureau deployments) but there is no UI-visible mechanism for it. Do not design any account-level grouping UI unless this is clarified.

---

### DRIFT-8 — `BureauDashboard.tsx` Content Unknown

**Issue:** The Bureau Dashboard page was listed in the file scan but its content was not read in full. The exact metrics and data it displays are therefore not known from code inspection.

**Design impact:** The Screen Inventory (S1) describes the expected purpose based on the route structure and domain context. Verify against the actual component when designing this screen.

---

### DRIFT-9 — Bulk Input Upload: No Server-Side Template Download Endpoint

**Issue:** The `PayrollInputsBulkUpload.tsx` screen exists, implying users can upload Excel files for bulk input. However, no endpoint was found that generates or serves a template file for users to download.

**Design impact:** Either the template is embedded in the frontend as a static file, or it is not provided — users may be expected to know the column format. Confirm and design accordingly. Consider adding a "Download Template" button backed by a static CSV asset.

---

### DRIFT-10 — `JsonOnboarding.tsx` vs Onboarding Stepper: Unclear Which Is Primary

**Issue:** Two distinct onboarding UI paths exist:
1. `WorkspaceSetup.tsx` — multi-step form wizard (implied to be the primary path).
2. `JsonOnboarding.tsx` — raw JSON editor.

**Not clear from code:** Whether these are alternative paths for the same user, or whether one is the bureau-internal path and the other is an external client path.

**Design impact:** The UX design must decide which is the primary onboarding flow and which is the fallback/power-user path. Presenting both equally would confuse new users.

---

### DRIFT-11 — `WorkspacePayrollConfig` and `RateCodes` Have No Dedicated Page

**Issue:** Both `WorkspacePayrollConfig` (PH rules) and `RateCodeRegistry` management endpoints exist, but no dedicated page file was found for them. They are likely embedded within `WorkspaceConfig.tsx` or similar.

**Design impact:** These are non-trivial configurations with significant payroll accuracy implications (wrong PH conflict rules → wrong pay). They deserve dedicated, clearly labelled UI sections — confirm they are not buried in an overflow tab.

---

### DRIFT-12 — Component Trace Format May Vary (Legacy vs Sequential Executor)

**Issue:** The `component_trace_jsonb` field is only populated when the sequential executor path is used (when `component_metadata` is present). Runs processed by the legacy executor do not produce `component_trace_jsonb`.

**Design impact:** The PayrollResults screen (`PayrollResults.tsx`) renders the component trace. It must gracefully handle runs where this field is null or empty — do not show a blank expandable row; show "No trace available (legacy calculation path)" or similar.

---

## Resolved — Documentation Conflicts That Are Not Bugs

### DRIFT-13 — `PENDING` Reconciliation Status Exists in the Enum but Is Never Created

**Observed:** The `ReconciliationStatus` in frontend types and the DB model includes `PENDING`. The reconciliation service only creates `MATCHED` or `MISMATCH` records — never `PENDING`.

**Verdict:** `PENDING` is a legacy placeholder from an earlier design. The current code never produces it. Design the UI to handle it defensively (show it as "Awaiting submission" if encountered), but do not design a workflow around it.

---

### DRIFT-14 — Sprint State in CLAUDE.md Says Sprint 6 Is "In Progress" but Git Log Shows Sprint 7 Complete

**Observed:** The project CLAUDE.md lists "Sprint 6: in progress". The git log shows a Sprint 7 commit as the most recent commit.

**Verdict:** CLAUDE.md is stale. Trust the git log — Sprint 7 is the current state. This does not affect the UI design brief since it is derived from the code, not the documentation.
