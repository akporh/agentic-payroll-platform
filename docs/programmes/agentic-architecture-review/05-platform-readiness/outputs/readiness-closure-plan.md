# Stage 05 Output: Readiness Closure Plan

For each blocker in `platform-blocker-register.md`, the minimum remediation and closure evidence required — not an implementation, per this stage's explicit scope.

## Critical

| Blocker | Minimum remediation | Closure evidence required |
|---|---|---|
| No authentication | `operator` table, JWT issuance route, `get_current_operator` FastAPI dependency wired into every route | Every route rejects an unauthenticated request; a committed test asserting this for a representative sample of routes; `workspace_id` never accepted from request body once this lands |
| Event/notification/exception foundation absent | Transactional outbox, 4 named new events (reconciliation MISMATCH, employee ENROLLED, employee STATUS CHANGED, payroll input SUBMITTED), event consumer worker, `workspace_notification` table, exception data model | Each event type has a committed test proving it's emitted on the triggering state change; consumer processes an event end-to-end in a test; exception record can be created/owned/resolved/closed in a test |
| Reconciliation workspace scoping | `workspace_id` column + backfill on `payroll_reconciliation`; repo functions filter by it; the three "workspace-scoped" routes actually enforce the parameter they already accept | A committed regression test asserting a cross-workspace request against `run_id` from another workspace is rejected (403/404), not silently succeeding |
| Statutory-rule change management | Application-level write path for `statutory_rule`/`tax_band`, pre-emptive duplicate validation, approval record, preview/impact-analysis mechanism | Each of the four sub-capabilities has a committed test; a duplicate `(country_code, effective_from)` attempt produces a clear application-level error before hitting the DB constraint |

## High

| Blocker | Minimum remediation | Closure evidence required |
|---|---|---|
| `salary_definition` in-progress edit-lock | Extend the DB trigger's `WHERE` clause to the full in-progress status range, or extend the application-layer check to cover every write path with a committed test | A test proving an edit attempt during `DRAFT`/`CALCULATING`/`LOCKED` (not just `PAID`) is rejected |
| D-ARCH-1 dead branches / status drift | Replace the hardcoded status list with a reference to the canonical `PayrollRunStatus` enum or an explicit derived subset | A test asserting the lock check's allowlist can never silently diverge from the enum again (e.g. a test that iterates the enum and checks the lock-check's coverage) |
| C12 required before C11 | Sequence C12's build ahead of or alongside C11 | C12's four sub-capabilities (above) closed before C11 is scoped for delivery |
| C14 required before C13 | Build C14's dry-run endpoint (lower cost than feared, reusing `run_sequential_payroll`) | A committed dry-run endpoint test, exercised against a proposed (unconfirmed) import |

## Medium

| Blocker | Minimum remediation | Closure evidence required |
|---|---|---|
| `component_trace_jsonb` data-access-layer null-guard | Add a null-check directly in `payroll_result_repo.py`/`payroll_retry_service.py`, independent of the HTTP-layer fix | A unit test at the repository layer confirming null-trace behavior without going through the HTTP route |
| `load_inputs_for_run` no workspace check | Add a `workspace_id` parameter and filter, or document/enforce that only pre-validated callers may invoke it | A test proving the function rejects or ignores rows from another workspace if called with a mismatched id |
| `workspace_info()` arbitrary selection | Require an explicit workspace identifier parameter; audit existing non-tool callers for correctness | A test proving the function cannot return data for an unspecified/wrong workspace |

## Sequencing implication (not a roadmap — a readiness dependency chain)

The critical blockers are not independent — closing C1 (auth) is a literal prerequisite for meaningfully closing C2, C8's tool-layer defence-in-depth, and the audit-attribution gap. This mirrors and reinforces Stage 04's own prioritisation signal (C1 → C2 → ...), now grounded in a committed-code re-verification rather than a general architectural preference.

## What this stage explicitly does not do

Per its own constraints: this plan names required evidence, not implementation. No code, migration, or test was written or modified as part of producing this plan.
