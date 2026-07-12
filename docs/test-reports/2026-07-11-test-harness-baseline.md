# Test Harness Baseline — 2026-07-11

First formal baseline run of the full pytest suite, taken at the start of the
test-harness workstream (uat branch, commit 00a16f3).

## Summary

| Metric | Value |
|---|---|
| Total collected | 287 |
| Passed | 282 |
| Failed | 4 |
| Skipped | 1 |
| Runtime | ~9 s |

Suite composition: 41 test files under `tests/`, mix of pure-domain unit tests
(PAYE, pension, NHF, salary, proration, rule evaluator) and API-level
integration/e2e tests (pipeline, reconciliation, retry, lock/approval,
lifecycle, immutability).

## Failures — all one root cause (stale tests, not regressions)

All 4 failures assert `body["status"] == "success"` on the run-payroll HTTP
response. The endpoint was deliberately changed to background-task execution
(`backend/api/routes/payroll.py:852` — snapshot creation moved to a FastAPI
`BackgroundTasks` to avoid a ~25 s blocking response on Neon). It now returns
`{"status": "DRAFT", "payroll_run_id": ...}` immediately.

The captured engine traces in each failure show the calculation completing
correctly (gross/PAYE/net computed, results persisted, run reaches
CALCULATED) — the engine is not broken; the tests encode the old synchronous
response contract.

This is the known TF-7 failure class recorded in the Sprint PAY-TAX-1 retro:
"background-task sprints break HTTP response body test assertions."

| Test | File |
|---|---|
| test_payroll_approval_and_lock_e2e | tests/test_payroll_lock_and_approval.py |
| test_partial_payroll_run_e2e | tests/test_payroll_partial_run_e2e.py |
| test_full_payroll_pipeline_e2e | tests/test_payroll_pipeline_e2e.py |
| test_payroll_retry_e2e | tests/test_payroll_retry.py |

**Planned fix (triage task):** update the 4 e2e tests to poll the run-status
endpoint until the run leaves DRAFT/CALCULATING (with a timeout), then assert
on the persisted run state — matching the real async contract instead of the
retired synchronous one.

## Skipped — intentional

`tests/test_payroll_reconciliation.py:347` — payment reconciliation is a
Phase 2 feature (requires `payroll_payment_instruction` table and payment
generation). Skip is documented in the test itself. No action.

## Notable warnings (non-blocking)

- `LegacyAPIWarning`: `Query.get()` deprecated in SQLAlchemy 2.0 —
  `workspace_state_machine.py:23`, `workspace_repo.py:13,40`.
- Deprecated LIFE_INSURANCE rate×GROSS_PAY fallback fires in pipeline e2e
  (`sequential_executor.py:460`) — migration to `flat_amount` still pending.
- `starlette.formparsers` PendingDeprecationWarning (`python_multipart`).

## Baseline verdict

The suite is healthy: zero calculation-path failures. The only red is a stale
response-shape contract in 4 e2e tests. Once those are fixed the suite should
be fully green and ready to wire into CI.
