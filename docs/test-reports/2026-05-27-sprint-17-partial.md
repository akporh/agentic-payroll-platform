# Sprint 17 Test Report (Partial) — 2026-05-27

## Summary

| Metric | Value |
|---|---|
| Sprint | 17 (partial — B0a, B0b, B1 implemented; B2/B3/B4/Track A pending) |
| Date | 2026-05-27 |
| Test suite | 266 passed, 1 skipped, 0 new failures |
| Pre-existing failures excluded | 4 (TF-3 to TF-6, same root cause as Sprint 14) |
| API verifications | 11 manual checks across 4 new endpoints |
| Overall verdict | PASS (for implemented items) |

---

## Environment

- `alembic current`: `a2b3c4d5e6f7`, `ee5ff6aa7bb8` — two heads (pre-existing, not a Sprint 17 issue)
- `alembic heads`: `e4f5a6b7c8d9`
- Backend: started successfully on port 8000

---

## Sprint Items Verified

### B0a — LATERAL join fix in payroll_readiness_service.py

| Check | Result |
|---|---|
| readiness tests all pass (5/5) | PASS |
| `test_employee_missing_salary_definition_not_ready` passes | PASS |
| No regression in other 265 tests | PASS |

**Bug found and fixed during testing:** The initial B0a implementation used a pure LATERAL join with no date filter, which caused `test_employee_missing_salary_definition_not_ready` to fail. An employee with only an expired contract would no longer be flagged as not ready. Fix applied: added `AND (ec2.end_date IS NULL OR ec2.end_date >= CURRENT_DATE)` inside the LATERAL subquery so it picks the most-recent *currently valid or future* contract only. Employees with no valid contract still generate a readiness block.

### B0b — LATERAL join fix in timesheet_derivation_service.py

| Check | Result |
|---|---|
| Import check | PASS |
| No test regressions | PASS |
| BLOCKED: no test covers multi-contract employee in timesheet derivation | BLOCKED — needs B2+B3 deployed data |

### B1 — New employee CRUD (repo + routes)

| Check | Result |
|---|---|
| `GET /{wid}/employees/{eid}` — happy path returns employee with contract history | PASS |
| `GET /{wid}/employees/{eid}` — wrong workspace returns 404 | PASS |
| `PATCH /{wid}/employees/{eid}` — update full_name, verify persisted | PASS |
| `PATCH /{wid}/employees/{eid}` — restore original name | PASS |
| `PATCH /{wid}/employees/{eid}` — invalid status returns 422 with message | PASS |
| `POST /{wid}/employees/{eid}/contracts` — backdating guard returns 422 | PASS |
| `POST /{wid}/employees/{eid}/contracts` — invalid salary def returns 422 | PASS |
| `POST /{wid}/employees/{eid}/contracts` — happy path creates new contract | PASS |
| `POST /{wid}/employees/{eid}/contracts` — old contract end_date = new_start - 1 day (BLK-1) | PASS (end=2026-12-31 for start=2027-01-01) |
| `PATCH /{wid}/employee-contracts/{cid}` — happy path updates change_reason | PASS |
| `PATCH /{wid}/employee-contracts/{cid}` — wrong workspace returns 404 | PASS |
| `PATCH /{wid}/employee-contracts/{cid}` — invalid date format returns 422 | PASS |

**Bug found and fixed during testing:** `update_employee_contract` in `employee_repo.py` used `ec.change_reason` / `ec.end_date` in the SET clause of a `UPDATE ... FROM` query. PostgreSQL does not allow table alias prefixes in SET clauses. Fixed to use bare column names with fully-qualified table name in the WHERE clause.

**Route discovery:** `GET /{wid}/employees` and `POST /{wid}/employees` already existed in `workspace.py`. The new `employees.py` was stripped to only the 4 genuinely new endpoints. The duplicate `GET` and `POST` handlers were removed from `employees.py`.

**Effective_from validation added** to `workspace.py POST /{wid}/employees` as specified by the plan.

---

## Data Integrity Spot-Check

```
No null net_pay on CALCULATED runs: not checked (no payroll runs touched)
component_trace_jsonb populated: not checked (no payroll runs touched)
No duplicate statutory rules: not checked (no statutory data touched)
No multiple active pay cycles: not checked (no pay cycle data touched)
```

Sprint 17 B0/B1 touches only employee/employee_contract tables and readiness/timesheet service queries. No payroll run data was modified.

---

## Regression Suite

```
266 passed, 1 skipped (pre-existing), 38 warnings in 4.58s
```

Pre-existing failures (excluded from run):
- TF-3: `test_payroll_approval_and_lock_e2e` — NHF toggle in test fixture
- TF-4: `test_full_payroll_pipeline_e2e` — same root cause
- TF-5: `test_partial_payroll_run_e2e` — same root cause
- TF-6: `test_payroll_retry_e2e` — same root cause

All four confirmed pre-existing via ROADMAP.md Known Test Failures table. No new failures introduced by Sprint 17 work.

---

## Known Pre-Existing Issues

See ROADMAP.md Known Test Failures table (TF-3 to TF-6). Status unchanged from Sprint 14.

---

## Deferred

| Item | Reason |
|---|---|
| `/security` review | Not yet run — deferred to end of sprint once B2/B3/B4/Track A complete |
| `/auditor` review | Not yet run — no calculations or statutory rules touched by B0/B1 |
| B2 verification (onboarding inline SQL → repo) | Implementation pending |
| B3 verification (Employee management UI) | Implementation pending |
| B4 verification (temporal index migration) | Implementation pending |
| Track A verification (Attendance sidebar) | Implementation pending |
| D-ARCH-1 guard test (active run blocks contract change) | Needs a workspace with an active run in lock window |
| Multi-contract employee through full payroll run | Needs B2+data to produce multi-contract employees |

---

## Sign-off

Verified by: Claude Code (automated)
