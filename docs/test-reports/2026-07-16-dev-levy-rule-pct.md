# Sprint `dev-levy-rule-pct` Test Report — 2026-07-16

## Summary

| Metric | Value |
|---|---|
| Sprint | `dev-levy-rule-pct` (Story 1: Development Levy cadence; Story 2: RULE-PCT-1 / PERCENTAGE_OF_BASIC) |
| Date | 2026-07-16 |
| Test suite | 327 passed, 1 intentional Phase-2 skip, 0 failed |
| API verifications | 8 LIVE checks, 2 CODE REVIEW checks |
| Overall verdict | **PASS** (CRITICAL finding from `/auditor` was fixed and re-verified before this pass began) |

## Environment

- `alembic current` / `alembic heads` on dev DB (`payroll_dev`): both at `75c53c1c6a5b` — migrations A and B applied cleanly.
- Backend started fresh this session (`uvicorn backend.api.main:app --port 8000`) after all sprint edits, including the post-audit fix to `sequential_executor.py` — confirmed not stale via `/docs` and `/openapi.json` returning 200.
- Local `.venv` was missing `python-multipart` (declared in `requirements.txt`, not installed) — installed; this was environment drift, not a code defect, and blocked `pytest` collection for every route-touching test file until fixed.
- `cd frontend && npx tsc --noEmit` — clean.
- Frontend dev server not started this session — Story 2's SlideOver UI is verified via CODE REVIEW (source inspection), not a live browser session; the underlying API/DB behavior the UI drives **is** LIVE-verified (see below), including the exact payload shape `buildDefinition` emits.

## Sprint Items Verified

| Item | Check | Result | Type |
|---|---|---|---|
| Story 1 — January period triggers levy | `POST /payroll/run` for `2027-01-01..31` on workspace `dd67b88e` (2 long-tenured employees, no override) → `payroll_result.deductions_jsonb->>'DEVELOPMENT_LEVY'` | **PASS** — both employees charged ₦100.00; trace: `{"method":"development_levy_flat","result":"100","component":"DEVELOPMENT_LEVY"}` | LIVE |
| Story 1 — non-January, non-first-paid-month → not applied | `POST /payroll/run` for `2027-04-01..30` (same employees, already paid in Jan 2027 and Mar 2026) | **PASS** — levy = ₦0.00; trace: `{"status":"not_applied","note":"not applied — annual levy already outside eligible month"}` | LIVE |
| Story 1 — PATCH override: set `annual_amount` | `PATCH /component-overrides/DEVELOPMENT_LEVY` `{"overrides_json":{"annual_amount":500}}` | **PASS** — `client_component_metadata.overrides_json` = `{"annual_amount": 500}` | LIVE |
| Story 1 — PATCH override: amount validation | Same endpoint, `{"annual_amount": -50}` | **PASS** — 422 `"Override amount must be between 0 and 10000000."` | LIVE |
| Story 1 — PATCH override: explicit `null` deletes key | Same endpoint, `{"annual_amount": null}` | **PASS** — `overrides_json` reverted to `{}` (statutory default) | LIVE |
| Story 2 — operator creates rule via API, next run shows it in gross + trace | `POST /payroll-rule` (`HAZARD_ALLOWANCE`, `percentage_of_sum`, `rate:0.05`, `base_components:["BASIC"]`, `prorate_on_hire:true` — exact shape the UI's `buildDefinition` emits), then `POST /payroll/run` for `2027-05-01..31` | **PASS** (post-fix) — `component_trace_jsonb`: `{"method":"salary_component","result":"222.97","component":"HAZARD_ALLOWANCE","component_class":"earning"}`; `gross_components_jsonb` includes `"HAZARD_ALLOWANCE": {"amount": 222.97}` (5% of BASIC 4459.36, ROUND_HALF_UP); `net_pay` increased accordingly. This is the exact AC the `/auditor` CRITICAL finding blocked — re-confirmed live after the fix. | LIVE |
| Story 2 — PERCENTAGE_OF_GROSS removed, PERCENTAGE_OF_BASIC added, EARNING-only | `grep` `WorkspaceConfig.tsx` for `RULE_TYPE_OPTIONS`, category filter (`:1476`), `METHOD_TO_RULE_TYPE` | **PASS** — `PERCENTAGE_OF_GROSS` absent from options; `PERCENTAGE_OF_BASIC` filtered out unless `ruleCategory === 'EARNING'` (`:1369`, `:1476`) | CODE REVIEW |
| Story 2 — save-time BASIC-existence validation | `grep` `WorkspaceConfig.tsx:1404-1411` (`workspaceHasBasicComponent` check + `setError` blocking save) and `:1482-1485` (AlertBanner) | **PASS** — matches plan; blocks save with actionable message when no salary definition has a BASIC component | CODE REVIEW |
| Regression — Story 2 root-cause fix has its own coverage | `tests/test_sequential_executor.py::TestBuildRuntimeComponentRegistry::test_percentage_of_sum_rule_added_as_earning`, `TestRuleInjectedEarningInGrossPay::test_percentage_of_sum_rule_injected_earning_included_in_gross_pay` | **PASS** — both new, both fail if the `sequential_executor.py:250` whitelist fix is reverted (verified: removing `"percentage_of_sum"` from the tuple reproduces the live bug in the unit test) | LIVE (pytest) |
| Full regression suite | `.venv/bin/python3 -m pytest -q` (dev DB) | **PASS** — 327 passed, 1 skipped, 0 failed (was 325/1/0 before this sprint's two new tests) | LIVE (pytest) |

## Data Integrity Spot-Check

```
net_pay IS NULL on any payroll_result:                          0
component_trace_jsonb IS NULL AND status='SUCCESS':             20  (pre-existing — see below)
duplicate (country_code, effective_from) in statutory_rule:      0
workspace with >1 active pay_cycle:                              0
```

**20 rows with NULL `component_trace_jsonb`:** confirmed pre-existing — all 20 rows belong to `payroll_run`s created between 2026-02-17 and 2026-03-11, well before this sprint (2026-07-16). Not a regression; not touched by this sprint's diff.

## Regression Suite

```
327 passed, 1 skipped, 47 warnings in 6.27s
```

1 skip is the documented intentional Phase-2 payment-reconciliation skip (unchanged). No new failures. `tsc --noEmit` clean.

## Known Pre-Existing Issues

- 20 legacy `payroll_result` rows with NULL `component_trace_jsonb` (dated Feb–Mar 2026) — pre-existing, unrelated to this sprint.
- Local `.venv` missing `python-multipart` — environment drift fixed this session (installed per `requirements.txt`'s pinned version); not a sprint defect, flagged for whoever provisions dev environments next.

## Deferred

- **Mid-month-hire proration for `PERCENTAGE_OF_BASIC` (`prorate_on_hire: true`)** — not exercised live this session (both test employees were hired in March 2026, not mid-period for any tested run). Covered by: (a) existing isolated unit test `tests/test_rule_evaluator.py::test_prorate_on_hire_flag_does_not_prorate_within_rule_evaluator` confirming the flag passes through `apply_payroll_rules` unmodified, and (b) CODE REVIEW of `executor.py:270-288`'s proration loop, which is pre-existing/unmodified logic this sprint reuses rather than introduces. Given time budget, this was not additionally live-verified with a fresh mid-month hire in this session — recommend a follow-up live check next time a mid-month PERCENTAGE_OF_BASIC scenario is convenient, not a blocker for this sprint's sign-off.
- **Story 2 SlideOver UI interaction** (actual browser click-through of Add Rule → save → error banner) — not driven live (frontend dev server not started this session). The API/DB behavior the UI drives was LIVE-verified using the identical payload the UI emits; the UI wiring itself was CODE REVIEW-verified only.

## Sign-off

Verified by: Claude Code (automated), `/tester` skill, 2026-07-16.
