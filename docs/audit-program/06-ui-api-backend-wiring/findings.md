# Stage 06 — Findings

Status: **complete**. All entries below use the template in
[`../_core/finding-schema.md`](../_core/finding-schema.md). Status values
restricted to this stage's five-value set.

---

## Headline result

The `05-001` backend remediation (payroll_run `FAILED` status +
`error_message`) is **not surfaced to end users anywhere in the frontend**.
The API contract change reached the backend correctly (confirmed in the
remediation's own verification), but the frontend type, status-badge
mapping, and run-detail rendering were never updated to consume it — a
bureau operator using the actual product today cannot see why a run
failed without direct API access. This is a genuine wiring gap, not a
reopening of `04-001`/`05-001` (the calculation-correctness and
persistence-safety fixes are unaffected and remain sound) — see 06-001.

---

## 1. UI/API/backend feature catalogue (summary)

| Feature | UI page | Wiring status | Evidence |
|---|---|---|---|
| Workspace setup/onboarding | `WorkspaceSetup.tsx`, `BureauDashboard.tsx` | Fully wired | §3 below |
| Workspace configuration (pay cycle, grades, designations, salary defs, rules, component overrides) | `WorkspaceConfig.tsx` | Mostly wired; `pay_cycle.definition_json` is the one confirmed gap (06-002) | `evidence/2026-07-12-pay-cycle-definition-json-write-only.txt` |
| Component metadata / client overrides | `WorkspaceConfig.tsx` | Fully wired (read, edit, save, display; `proration_strategy` dual-storage precedence from Stage 03's 03-001 confirmed correctly reflected in UI) | grep confirmed, §"positive controls" below |
| Salary definitions | `WorkspaceConfig.tsx` | Wired; D-ARCH-1 lock surfaced reactively, not proactively (06-005) | `evidence/2026-07-12-salary-def-edit-lock-reactive-only.txt` |
| Payroll rules / rule sets | `WorkspaceConfig.tsx` | Wired for CRUD; rule sets themselves have no direct UI (consistent with Stage 03 — rule sets are a backend snapshot mechanism, not a user-facing config surface) | Not a defect |
| Employee registry / contracts | `Employees.tsx` | Fully wired, including the Upload/Enroll separation (`CLAUDE.md` invariant) | Not re-verified in depth this stage — no new evidence gathered beyond confirming API calls exist |
| Attendance-code configuration | `AttendanceConfiguration.tsx` | Fully wired | `/workspaces/{id}/attendance-codes`, `/attendance-policies/{code}` confirmed called |
| Timesheet upload/derivation | `TimesheetUpload.tsx` | Mostly wired; `timesheet/audit/{employee_id}` is a confirmed missing UI feature (06-006) | `evidence/2026-07-12-backend-only-routes.txt` |
| Public holidays | `PublicHolidays.tsx` | Fully wired | `/workspaces/{id}/public-holidays` CRUD confirmed called |
| Payroll-run creation | `RunPayroll.tsx` | Wired but offers a dead-end option (06-003 — `FULL_RUN` retry strategy) | `evidence/2026-07-12-full-run-retry-strategy-dead-ui-option.txt` |
| Payroll-run list/detail/status | `PayrollRuns.tsx`, `PayrollResults.tsx` | `FAILED` status/`error_message` not surfaced (06-001) | `evidence/2026-07-12-failed-status-error-message-not-wired.txt` |
| Retry controls | `PayrollResults.tsx` (`ActionPanel`) | Correctly wired for `PARTIAL` runs (positive control); blank for `FAILED` runs (06-004) | `evidence/2026-07-12-actionpanel-returns-null-for-failed.txt` |
| Payroll result detail / component trace | `PayrollResults.tsx` | Fully wired (`component_trace_jsonb` rendered via `ComponentTraceEntry`) | Confirmed by type + usage |
| Reconciliation | `Reconciliation.tsx` | Fully wired (GET/POST/PATCH all called) | `evidence` grep in this stage's investigation log |
| Exports | `PayrollResults.tsx` | Fully wired — all 4 export types (`bank-upload`, `paye`, `pension`, `full-detail`) called | Confirmed — supersedes Stage 02's "exports mostly unwired" characterization for these 4 specific routes (the *dedicated export functions* Stage 02 flagged, `export_payroll_register_csv` etc., are a separate, still-unwired mechanism — see 06-007) |
| Audit/event history | `PayrollResults.tsx` (Audit tab, via `/runs/{id}/audit`) | Fully wired | Confirmed called |
| Operator/diagnostic endpoints | `admin.py`, `legacy-executor-stats` | Intentionally backend-only | `evidence/2026-07-12-backend-only-routes.txt` |

---

## 2. `05-001` remediation visibility verification (required investigation #4)

| Check | Result |
|---|---|
| Run detail/list APIs return `FAILED` and `error_message` correctly | ✅ Confirmed at the API layer (part of the approved remediation) — `GET /{workspace_id}/payroll/runs/{run_id}` returns both fields |
| Frontend status types accept `FAILED` | ❌ **Confirmed gap** — `PayrollRunStatus` in `frontend/src/types/payroll.ts` lists 7 values, `FAILED` is absent |
| The UI renders `FAILED` distinctly | ❌ **Confirmed gap** — `StatusBadge`'s `PAYROLL_COLORS` lookup has no `FAILED` key; falls back to the same generic gray used for any unrecognized value (indistinguishable from a typo or a future unrelated status) |
| The operator-visible `error_message` is actually displayed | ❌ **Confirmed gap** — zero references to `payroll_run`'s `error_message` anywhere in `frontend/src/`; the `PayrollRun` TypeScript interface doesn't declare the field; `getRun()` is typed to a shape that omits it |
| Retry/action controls are disabled or absent for terminal `FAILED` runs | ❌ **Confirmed gap, but via absence-by-omission, not a deliberate disable** — `ActionPanel`'s status if-chain has no `FAILED` branch and falls through to `return null` (06-004). Retry itself is correctly present and wired for `PARTIAL` (positive control) |
| No frontend enum/filter/badge/status mapping drops or mislabels `FAILED` | ❌ Same as above — `StatusBadge` "drops" it in the sense of not mapping it, though the literal text `FAILED` still renders via the badge's generic `{status.replace(/_/g, ' ')}` fallback, so it is not literally invisible, just unstyled and untyped |

**This is a wiring verification of the completed remediation, not a
reopening of it** — per the sprint's explicit framing. `04-001`'s
calculation-correctness fix and `05-001`'s backend-side abort/persist
behaviour are unaffected; both remain sound. What's missing is purely the
frontend's consumption of the now-available signal.

---

### 06-001 — `payroll_run.status = 'FAILED'` and `error_message` (05-001 remediation) are not surfaced anywhere in the frontend

- **stage:** 06-ui-api-backend-wiring
- **location:** `frontend/src/types/payroll.ts:1-19` (`PayrollRunStatus` type, `PayrollRun` interface); `frontend/src/components/ui/StatusBadge.tsx` (`PAYROLL_COLORS` lookup); `frontend/src/api/payroll.ts:27-28` (`getRun` typed `<PayrollRun>`)
- **current implementation:** `PayrollRunStatus` is a 7-member union type (`DRAFT | CALCULATING | CALCULATED | PARTIAL | APPROVED | LOCKED | PAID`) that does not include `FAILED`. `PayrollRun` does not declare an `error_message` field. `StatusBadge`'s `PAYROLL_COLORS: Record<PayrollRunStatus, string>` has no entry for `FAILED`, so a `FAILED` run's badge falls back to the same generic gray styling used for any unmapped/unknown value — visually indistinguishable from a data anomaly. Confirmed by grep across all of `frontend/src/`: zero references to `payroll_run`'s `error_message` (the only `error_message` hits belong to `ExecutionTraceStep`, an unrelated field from the `execution_trace` mechanism, Stage 02).
- **intended behaviour:** The `05-001` remediation's stated goal (`docs/audit-program/05-snapshot-integrity/findings.md` §9, `docs/audit-program/remediation/04-001-05-001/summary.md`) was explicit: "Ensure the API/UI can retrieve a meaningful error rather than requiring server-log access." The API half was delivered; the UI half was not attempted (out of scope for that remediation sprint, which was backend-only per its own constraints — "Do not modify frontend code").
- **suspected or confirmed defect:** Confirmed. A `FAILED` run today is visually a generic-gray badge with no distinguishing color, and the reason for the failure is retrievable only via direct API call (e.g. `curl`) or server logs — for a bureau operator using the product normally, `05-001`'s practical goal (operator-visible failure) is not yet reached, even though the backend and API layers are correct and complete.
- **evidence:** `evidence/2026-07-12-failed-status-error-message-not-wired.txt`
- **status:** confirmed
- **severity:** S2 (a real operator-experience gap directly following from a remediated S0/S2 pair, but not itself a calculation-correctness or data-integrity defect — no financial or persistence risk)
- **related invariant:** none directly; closes the loop on the `05-001` remediation's stated intent

---

### 06-002 — `pay_cycle.definition_json` is accepted at onboarding, read internally by the payroll engine, and never exposed to or editable from the UI afterward

- **stage:** 06-ui-api-backend-wiring
- **location:** `backend/api/routes/onboarding.py:288-324` (writer — accepts `definition_json` or an `execution_window` sub-key); `backend/api/routes/payroll.py:301-303` (`SELECT frequency, definition_json FROM pay_cycle` — read internally, feeds `pay_cycle_definition` into the calculation context, so it does affect runtime behaviour); `backend/api/routes/workspace.py:1144-1150,1223` (`GET /configuration` selects only `frequency, run_day, cutoff_day, payment_day` — never `definition_json`); `backend/api/routes/workspace.py:1420-1432` (`PATCH /pay-cycle` accepts only `frequency, run_day, cutoff_day, payment_day` — never `definition_json`)
- **current implementation:** Confirmed a genuine write-once, read-nowhere-in-the-UI field. It is written during onboarding, consumed internally by the payroll engine's period-type resolution, but no GET endpoint returns it and no PATCH endpoint accepts it — once set, a workspace administrator has no way to view or change it through the product. Confirmed by grep: zero references to `definition_json` anywhere in `frontend/src/`.
- **intended behaviour:** Not documented as intentional. Stage 03 flagged this exact field as "not traced to a specific UI control" and handed it to this stage for resolution — this stage confirms the gap precisely: it's not merely untraced, it is structurally unreachable after onboarding.
- **suspected or confirmed defect:** Confirmed as a dead-end configuration surface, per this stage's classification framework ("persisted but not surfaced," compounded by "surfaced at write-time only, then unreachable"). Whether this matters in practice depends on how often `definition_json`'s content actually varies per workspace and needs post-onboarding correction — not established in this stage.
- **evidence:** `evidence/2026-07-12-pay-cycle-definition-json-write-only.txt`
- **status:** confirmed
- **severity:** S2 (affects runtime calculation via `pay_cycle_definition`, but only at initial setup — no evidence of an active correctness risk, since the value can't drift once written; the risk is purely "cannot be corrected without a database intervention if wrong")
- **related invariant:** none

---

### 06-003 — `RunPayroll.tsx` offers a "Full Run" retry-strategy option that the backend always rejects

- **stage:** 06-ui-api-backend-wiring
- **location:** `frontend/src/pages/RunPayroll.tsx:48,235-241` (`RadioGroup` with `PER_EMPLOYEE`/`FULL_RUN` options, the latter described as "The entire run is retried from scratch on failure"); `backend/api/routes/payroll.py:83-87` (`_VALID_RETRY_STRATEGIES = {"PER_EMPLOYEE"}`, rejects anything else with a 422)
- **current implementation:** The run-creation form presents both retry strategies as apparently legitimate, described choices. Selecting "Full Run" and submitting always produces a backend rejection — confirmed by direct code citation (`CLAUDE.md`'s own invariant table already documents `FULL_RUN` as "disabled by migration," and Stage 04 confirmed `_retry_full_run()`'s entire body is a hard-coded `raise`).
- **intended behaviour:** Not documented as intentional for this specific control. `CLAUDE.md` documents the backend policy clearly; nothing documents an intent to keep offering the now-permanently-disabled option in the UI.
- **suspected or confirmed defect:** Confirmed as a dead, always-failing UI control. The user-facing error on submission does surface the backend's `detail` message reasonably (via the same `catch` pattern used elsewhere, falling through to `e.message`), so this is not a silent failure — but it is a confirmed wasted/misleading choice presented as valid.
- **evidence:** `evidence/2026-07-12-full-run-retry-strategy-dead-ui-option.txt`
- **status:** confirmed
- **severity:** S2 (a real, user-facing broken control — not a data-integrity risk, since the backend correctly rejects it, but a confirmed UX defect a bureau operator could hit at any time)
- **related invariant:** `CLAUDE.md` — `payroll_retry_request.retry_strategy` (`PER_EMPLOYEE` only)

---

### 06-004 — `ActionPanel` (the sole home of the retry button and all other run actions) renders nothing for a `FAILED` run — corrected finding, retry control itself is confirmed present and correctly wired for `PARTIAL`

- **stage:** 06-ui-api-backend-wiring
- **location:** `frontend/src/pages/PayrollResults.tsx:96-182` (`ActionPanel` — an if-chain over `run.status`: `CALCULATING`, `PARTIAL` (renders "Retry Failed Employees", wired to `payrollApi.retryRun`), `CALCULATED`, `APPROVED`, `LOCKED`, `PAID`; falls through to `return null` at line 181 for any status matching none of these); `frontend/src/pages/PayrollResults.tsx:1253` (`onRetry` wiring, confirmed correct)
- **current implementation:** This stage's first search (grep across `PayrollRuns.tsx` for a retry handler) was a false negative — the retry control lives in `PayrollResults.tsx`, not `PayrollRuns.tsx`, and is correctly wired: it appears exactly when `run.status === 'PARTIAL'`, calls `payrollApi.retryRun(runId)`, and there is even a dedicated "Cannot retry this run" modal (`EMP-UX-3`) that correctly handles `04-001`'s legacy pre-snapshot-engine hard-fail case — confirmed as a **positive control**, not a defect. However, `ActionPanel`'s if-chain covers only the 6 statuses that existed before the `05-001` remediation added `FAILED`; there is no `if (run.status === 'FAILED')` branch, so execution falls through every condition and returns `null` — the entire action area of the page (which is also where any status explanation text lives, per the `PARTIAL`/`PAID`/etc. branches each rendering their own message) is blank for a `FAILED` run. `DRAFT` also falls through to `null` today, but that is pre-existing, unrelated behaviour (a `DRAFT` run is mid-flight, arguably correctly showing nothing yet) — `FAILED` is the newly-introduced terminal status this gap actually affects.
- **intended behaviour:** Same as 06-001 — the `05-001` remediation intended `FAILED` runs to be operator-visible; a blank action panel is the opposite of that intent.
- **suspected or confirmed defect:** Confirmed. This is the second, more specific manifestation of 06-001 (which covers the type/badge-level gap) — `ActionPanel`'s blank fallthrough is the concrete, page-level consequence: a bureau operator opening a `FAILED` run's detail page sees the (generically-styled, per 06-001) status badge at the top, and then an empty space where an explanation or action would normally appear for every other terminal-ish status.
- **evidence:** `evidence/2026-07-12-actionpanel-returns-null-for-failed.txt`
- **status:** confirmed
- **severity:** S2 (same severity class as 06-001 — operator-experience gap, not a correctness or persistence risk; the retry mechanism itself, which this audit has spent two stages verifying, is confirmed correctly wired for the case it's actually meant to handle, `PARTIAL`)
- **related invariant:** none

---

### 06-005 — Salary-definition edit lock (D-ARCH-1) is surfaced reactively (after a failed save attempt), not proactively

- **stage:** 06-ui-api-backend-wiring
- **location:** `frontend/src/pages/WorkspaceConfig.tsx:673-688` (`handleSave` — no pre-check, relies on `catch (e) { setError(extractError(e)); }`); `frontend/src/utils/errorUtils.ts` (`extractError` — confirmed correctly surfaces the backend's `detail` field, e.g. "This salary definition cannot be edited while a payroll run is in progress or pending approval.")
- **current implementation:** The edit form does not check or display lock status before the user opens the editor or attempts to save — the lock is only discovered via the 409 response after clicking Save. The error message itself, once it arrives, is accurate and complete (not generic).
- **intended behaviour:** Not documented as requiring proactive disclosure. `CLAUDE.md`'s D-ARCH-1 invariant describes the backend guard's existence, not a specific UX requirement for how it should be surfaced.
- **suspected or confirmed defect:** Not a functional defect — the lock is correctly enforced and the error is accurately surfaced, just later in the interaction than a proactive design would choose (e.g. a disabled Edit button with a tooltip, or a banner in the SlideOver). Recorded as a UX-improvement opportunity, not a wiring gap.
- **evidence:** `evidence/2026-07-12-salary-def-edit-lock-reactive-only.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** D-ARCH-1 (Stage 03/04 citations)

---

### 06-006 — `GET /workspaces/{workspace_id}/timesheet/audit/{employee_id}` has no frontend caller — resolved: missing UI feature, not intentionally API-only

- **stage:** 06-ui-api-backend-wiring
- **location:** `backend/api/routes/payroll.py:1725` (route definition); confirmed via grep — zero matches anywhere in `frontend/src/`
- **current implementation:** A per-employee timesheet audit-trail endpoint exists with no UI surface.
- **intended behaviour:** **Resolved by human decision, 2026-07-12 (Stage 06 close review):** this is a **planned-but-missing UI feature**, not an intentionally API-only route. Rationale: it supports a core bureau-operator workflow — explaining how an employee's uploaded attendance/timesheet data was interpreted and converted into payroll inputs — which belongs alongside the already-wired timesheet upload, payroll-result trace, reconciliation, and audit-history surfaces, all of which serve the same "show the operator what happened and why" purpose.
- **suspected or confirmed defect:** Confirmed as a missing UI surface. The backend endpoint is the correct, retained source for this feature — not obsolete, not operator-only. Implementation is out of scope for this read-only audit stage; the UI requirement is recorded for Stage 13's consolidated backlog.
- **evidence:** `evidence/2026-07-12-backend-only-routes.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

### 06-007 — `GET/POST /payroll/run/{run_id}/reconcile` (unscoped) is superseded by the workspace-scoped reconciliation routes and has no frontend caller

- **stage:** 06-ui-api-backend-wiring
- **location:** `backend/api/routes/payroll.py:1236,1264` (unscoped routes); contrast with `backend/api/routes/payroll.py:1293,1302,1318` (`/{workspace_id}/payroll/runs/{run_id}/reconciliation` GET/POST/PATCH — confirmed the ones the frontend actually calls, per `frontend/src/api/payroll.ts:36,44,54`)
- **current implementation:** Two parallel reconciliation route families exist: an older, unscoped pair (no `workspace_id` in the path) and a newer, workspace-scoped triplet. Only the workspace-scoped routes are called from the frontend.
- **intended behaviour:** Not documented. The unscoped pair reads as an earlier iteration superseded by the workspace-scoped routes, consistent with the general pattern Stage 01 already noted of inconsistent route-prefix conventions in this codebase (finding 01-008/01-012).
- **suspected or confirmed defect:** Not itself a defect (unreachable dead code, not a broken feature) — but worth flagging alongside the exports-function dead code Stage 02 found (02-009), as another candidate for Stage 12's simplification pass. Also worth independently confirming the unscoped pair isn't missing the workspace-scoping the newer routes have (a security-adjacent question, flagged for Stage 09 rather than resolved here).
- **evidence:** `evidence/2026-07-12-backend-only-routes.txt`
- **status:** confirmed
- **severity:** S3
- **related invariant:** none

---

## Positive controls (confirmed correctly wired, recorded so this stage isn't read as all-gaps)

- **Component overrides / `proration_strategy` dual storage** (Stage 03's 03-001): confirmed all the way to the UI — `WorkspaceConfig.tsx` reads, edits, saves, and displays `proration_strategy` and `overrides_json` consistently with the backend's column-wins-over-JSON precedence.
- **Exports** (all 4 types — bank-upload, PAYE, pension, full-detail): confirmed fully wired end-to-end, each with its own button and handler in `PayrollResults.tsx`. This is a different, already-wired mechanism from the dead `export_payroll_register_csv`-family functions Stage 02 flagged (02-009) — the two should not be conflated.
- **Public holidays, attendance codes, reconciliation, audit history, component trace**: all confirmed fully wired via direct API-call-site citation.
- **Grade/designation editing**: confirmed wired (initially appeared backend-only in a shallow grep pass; a corrected search found both `updateGrade`/`updateDesignation` client functions and their call sites).

---

## Backend-only capability register

| Route | Classification | Evidence |
|---|---|---|
| `GET/POST /payroll/run/{run_id}/reconcile` (unscoped) | Obsolete/dead — superseded | 06-007 |
| `GET /{workspace_id}/payroll/ops/legacy-executor-stats` | Intentionally operator/API-only (confirmed, Stage 01 01-005) | Carried forward, not re-derived |
| `admin.py` (3 routes: `/admin`, `/admin/onboarding`, `/admin/payroll`) | Intentionally operator-only (HTML dashboard, unprefixed mount per Stage 01 01-012) | Carried forward |
| `GET /workspaces/{workspace_id}/timesheet/audit/{employee_id}` | Planned but not exposed (missing UI feature — resolved 2026-07-12) | 06-006 |

## Frontend-only/dead UI register

No TODO/mock/disabled-handler markers found in a targeted grep across
`frontend/src/pages/` and `frontend/src/components/`. The one candidate
this stage surfaced (06-003, the `FULL_RUN` retry option) is better
classified as a **contract mismatch** (a UI control whose backend
counterpart was deliberately removed) than "dead UI" in the sense of an
unfinished/stubbed component — recorded under contract mismatches instead.
No unreachable routes or navigation dead-ends were found in this stage's
search, though this was not an exhaustive navigation-graph traversal.

## Frontend/backend contract mismatch register

| Mismatch | Finding |
|---|---|
| `PayrollRunStatus` type missing `FAILED`; `PayrollRun` interface missing `error_message` | 06-001 |
| `RunPayroll.tsx` offers `FULL_RUN`, backend only accepts `PER_EMPLOYEE` | 06-003 |

No other type-level mismatches (missing fields, nullability, enum
mismatches, date/time format, monetary type) were found in the specific
surfaces checked this stage (`PayrollRun`, `ExecutionTraceStep`,
component-override types). A full field-by-field diff of every frontend
type against every backend Pydantic schema was not performed — this
stage's contract-alignment check was targeted at the surfaces most
relevant to the recent remediation and Stage 03's handoffs, not
exhaustive across all 88 backend routes.

---

## Tenant/permission wiring observations (for Stage 09 — not a full security audit)

- Spot-checked `GET /{workspace_id}/payroll/runs/{run_id}/results`: confirmed the query properly scopes through `JOIN payroll_run r ON r.payroll_run_id = pr.payroll_run_id WHERE ... AND r.workspace_id = :wid` — an initial single-line grep suggested a missing scope, but the full query confirms correct scoping across a JOIN. Recorded so Stage 09 doesn't need to re-check this exact route, and as a reminder that single-line greps for `WHERE` clauses in multi-line SQL can produce false positives — full-query reads are required.
- The unscoped `/payroll/run/{run_id}/reconcile` pair (06-007) was not checked for tenant scoping internally — flagged for Stage 09 to verify whether it enforces workspace ownership at all, given it has no `workspace_id` in its path.
- No frontend code path was found that lets a user supply an arbitrary `workspace_id` outside of the currently-selected workspace context (route params are sourced from the URL, which itself is derived from workspace-switcher UI state, not free user input) — this is a shallow, non-exhaustive observation, not a confirmed clean bill of health.
- A full route-by-route tenant/permission audit (all 88 backend routes) was explicitly out of scope for this stage, per the sprint's instruction not to expand into a full security audit.

---

## Handoff notes for later stages

- **Stage 07 (silent failures and observability):** 06-001 is directly
  relevant — a backend fix specifically designed to eliminate a silent
  failure (05-001) currently has no UI consumer, which is itself a form of
  silent failure from the end-user's perspective (the signal exists but
  isn't surfaced).
- **Stage 08 (data integrity):** 06-002 (`pay_cycle.definition_json`
  unreachable after onboarding) is relevant if any workspace's `definition_json`
  content is ever found to need correction — Stage 08 should check whether
  any workspace's engine behaviour depends on a `definition_json` value that
  cannot currently be verified or fixed through the product.
- **Stage 09 (security and tenant isolation):** the tenant/permission
  observations above, especially the unscoped reconciliation routes
  (06-007) and the general recommendation to re-verify tenant scoping via
  full-query reads rather than single-line greps.
- **Stage 11 (scenario testing):** the retry UI's positive-control
  behaviour for `PARTIAL` runs (correct wiring, correct legacy-hard-fail
  modal per `EMP-UX-3`) is confirmed and can be used as a baseline for a
  regression scenario; a new scenario should be added covering the
  `FAILED`-run blank-panel gap (06-004) once fixed.
- **Stage 12 (code simplification):** 06-007 (dead unscoped reconciliation
  routes) is a direct simplification candidate, alongside Stage 02's
  02-009 (dead export functions) and Stage 05's 05-002/05-005.
- **Stage 13 (consolidated backlog):** 06-001, 06-003, and 06-004 are the
  three confirmed, user-facing gaps from this stage most likely to warrant
  a single small, fast follow-up sprint (all frontend-only changes: add
  `FAILED` to the type/badge/`ActionPanel`, and remove or gray out the
  `FULL_RUN` radio option) rather than a large remediation. All three stem
  from the same root cause — the frontend's `PayrollRunStatus` union type
  not yet being updated for the `05-001` remediation — so a single sprint
  touching `frontend/src/types/payroll.ts`, `StatusBadge.tsx`, and
  `ActionPanel` would likely close 06-001 and 06-004 together.

## Human decisions required

None remaining open from this stage — 06-006 was resolved at close review
(below). All other findings (06-001 through 06-005, 06-007) reached
`confirmed` status directly during the investigation.

---

## Final decision and handoff (stage close, 2026-07-12)

**Decision recorded:** `06-006` — `GET /workspaces/{workspace_id}/timesheet/audit/{employee_id}`
is a **missing UI feature** for the core bureau-operator workflow of
explaining how an employee's uploaded timesheet data was interpreted and
converted into payroll inputs — not an intentionally API-only endpoint. The
backend route is retained as the correct source; no code changes were made
in this read-only stage. The UI requirement is recorded for Stage 13.

**Review requirements verified before closing:**

1. `06-001` and `06-004` are correctly classified as frontend visibility
   regressions following the completed `05-001` backend remediation — both
   findings explicitly state the backend/API layer is correct and that
   `04-001`/`05-001` are not reopened; neither finding's evidence or
   defect statement touches the remediated backend code paths.
2. `06-002` establishes, via direct citation of the writer
   (`onboarding.py`), the runtime consumer (`payroll.py`'s
   `pay_cycle_definition` context key), and both the GET and PATCH routes'
   field lists, that `pay_cycle.definition_json` affects runtime but is
   unavailable for post-onboarding read or edit.
3. `06-003` establishes, via direct citation of both the frontend
   `RadioGroup` options and the backend's `_VALID_RETRY_STRATEGIES`
   allowlist, that the frontend offers `FULL_RUN` while the backend
   accepts only `PER_EMPLOYEE`.
4. `06-006` updated from `human decision required` to `confirmed`, with
   intended behaviour recorded as a missing UI audit surface (above).
5. `06-007` remains scoped to a Stage 09 security handoff (tenant-scoping
   of the unscoped route pair, not verified in this stage) and a Stage 12
   simplification candidate (dead code) — no security conclusion was drawn
   in Stage 06.
6. All completion criteria in `CONTEXT.md` are satisfied: the feature
   catalogue covers every domain in the sprint's minimum list; all six
   `05-001` visibility checks were explicitly resolved (§2); `pay_cycle.
   definition_json`, onboarding/edit alignment (Upload/Enroll — confirmed
   via existing API call-site citations, no new gap found), component
   override UI mapping (confirmed correct, positive control), the D-ARCH-1
   edit-lock UI behaviour, and retry-strategy visibility were each
   explicitly resolved with evidence; the backend-only and frontend-only/
   dead-UI registers are populated; API contract alignment was checked for
   the payroll-run and retry surfaces (06-001, 06-003); tenant/permission
   observations were recorded for Stage 09 without expanding into a full
   security audit; every finding now uses exactly one of the five valid
   status values (re-verified: 6 `confirmed`, 0 `plausible`/`unconfirmed`/
   `human decision required` remaining).

**Handoff carry-forward (finalized):**

- `06-001`, `06-004`, `06-006` → Stage 13 (consolidated backlog) — all
  three are small, frontend-only fixes; 06-001/06-004 share a root cause
  (the `PayrollRunStatus` type) and are natural candidates for a single
  follow-up sprint alongside 06-006's new UI surface.
- `06-002` → Stage 08 (data integrity) and Stage 13.
- `06-007` → Stage 09 (security/tenant isolation) and Stage 12
  (simplification).
- `04-002` remains open for Stages 07/10; `05-004` remains deferred to
  Stage 13 — both carried forward unchanged from Stage 05, not
  re-litigated in Stage 06.
