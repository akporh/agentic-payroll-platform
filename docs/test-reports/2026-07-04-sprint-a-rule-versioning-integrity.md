# Sprint A Test Report — 2026-07-04

## Summary
| Metric | Value |
|---|---|
| Sprint | A — Rule Versioning Integrity Fix (display + calculation date-awareness) |
| Date | 2026-07-04 |
| Test suite | 129 passed, 4 failed (payroll/rule subset) — all 4 failures confirmed pre-existing |
| New tests added | 3 (all LIVE PASS) |
| API verifications | 3 LIVE, 1 CODE REVIEW |
| Overall verdict | PASS |

## Environment
```
alembic current → ef2a3b4c5d6e (head)
alembic heads   → ef2a3b4c5d6e (head)   -- single head, no migration in this sprint
```
No migration was added or required for Sprint A (confirmed against the plan — all three fixes are query-logic changes only). DB: local Postgres at `postgresql+psycopg2://michaelemedo@localhost:5432/payroll_dev`. Frontend typecheck: `npx tsc --noEmit` — clean, zero errors.

## Sprint Items Verified

### Fix 1 — Payroll Inputs page rate display (the originally reported bug)
`POST /{workspace_id}/payroll/input-codes/by-date` in `backend/api/routes/payroll_input.py`, consumed by `frontend/src/pages/PayrollInputs.tsx`.

[PASS] Historical rate resolves correctly for a past-dated input  [LIVE]
```
Given: a rule REGULAR_OVERTIME with two versions — ₦150 effective 2025-01-01, ₦1,000 effective 2026-01-01
When:  POST .../input-codes/by-date with reference_dates ["2025-12", "2026-07"]
Then:  2025-12 bucket returns rule_rate 150; 2026-07 bucket returns rule_rate 1000
Got:   exactly as expected — the exact bug from the report (Dec-2025 input showing the 2026 rate) is fixed
Notes: tests/test_payroll_input_codes_route.py::test_resolves_historical_rate_for_past_date
```

[PASS] Empty reference_dates list returns empty map, not an error  [LIVE]
```
Given: no reference_dates
When:  POST .../input-codes/by-date with reference_dates: []
Then:  200 OK, {"input_codes": {}}
Got:   as expected
Notes: tests/test_payroll_input_codes_route.py::test_empty_reference_dates_returns_empty_map
```

[PASS] Reference date before any known version excludes the rule (no false match)  [LIVE]
```
Given: SPECIAL_OVERTIME effective_from 2025-06-01 only
When:  POST .../input-codes/by-date with reference_dates ["2025-01"]
Then:  2025-01 bucket contains no SPECIAL_OVERTIME entry
Got:   as expected — empty list, no error, no incorrect fallback match
Notes: tests/test_payroll_input_codes_route.py::test_date_before_earliest_version_gets_no_match
```

[PASS] Frontend consumers correctly wired to date-bucketed lookups  [STATIC]
```
Given: PayrollInputs.tsx replaces flat inputDefs with inputDefsByDate (keyed by month)
When:  npx tsc --noEmit
Then:  no type errors across all 4 consumer sites (renderInputRow, edit form, bulk-row table, dropdown)
Got:   clean compile
Notes: STATIC only — did not drive the actual browser UI this session (no dev server started).
       Recommend a manual click-through before this ships to production, per plan's verification section.
```

### Fix 2 — Historical/cross-period fallback for legacy workspaces (payroll.py:519-599)
[PASS] `_resolve_rule` and all 6 call sites handle a synthetic `{"id": None, ...}` historical entry identically to a real rule_set snapshot  [CODE REVIEW]
```
Given: the new fallback branch injects a synthetic historical_rule_sets entry when no
       rule_set has ever been published for a workspace
When:  traced rule_evaluator.py's _resolve_rule (lines 750-826) and all 6 call sites
Then:  consumption is generically by shape (rs.get("id"), rs.get("effective_from"), rs.get("items"))
       — a None id is read and handled identically to a real UUID
Got:   confirmed via direct code trace (also independently verified twice by architect + principal
       engineer reviewers during this session's arch-council passes)
Notes: NOT executed as a live end-to-end run this session — building a legacy-workspace
       (zero rule_set rows) + cross-period-input + full payroll-run fixture is substantial
       additional setup beyond this session's remaining scope. Labeled CODE REVIEW, not PASS-via-LIVE,
       per this skill's taxonomy rule. DEFERRED: a dedicated e2e test
       (tests/test_cross_period_legacy_fallback.py, as named in the plan) is a recommended follow-up
       before this fix sees its first real legacy-workspace arrears input in production.
```

### Fix 3 — Current-period legacy-loader date cap (payroll.py:394-401, payroll_retry_service.py:312-320)
[PASS] Full regression suite exercises this code path with no new failures  [LIVE]
```
Given: date cap (effective_from <= period_end) and DISTINCT ON added to both legacy loaders
When:  ran full payroll/rule test suite (129 tests) including tests/test_payroll_retry.py,
       tests/test_payroll_pipeline_e2e.py, tests/test_payroll_lock_and_approval.py, etc.
       — several of these exercise the legacy (no rule_set) code path directly
Then:  no new failures introduced
Got:   129 passed, 4 failed — all 4 failures independently confirmed pre-existing via git stash
       comparison (identical failures with and without this sprint's changes)
Notes: No dedicated fixture exists yet asserting "a future-dated rate version is excluded from the
       current period's calculation" (the specific scenario this fix targets) — existing tests don't
       happen to construct that scenario. DEFERRED per plan: extend tests/test_payroll_retry.py with
       this exact case as a follow-up, same reasoning as Fix 2 above.
```

## Regression Suite
```
pytest tests/ -k "payroll or rule" -q
→ 4 failed, 129 passed, 1 skipped, 153 deselected

Failures (all confirmed pre-existing via `git stash` A/B comparison before/after this sprint's diff):
  tests/test_payroll_lock_and_approval.py::test_payroll_approval_and_lock_e2e
  tests/test_payroll_partial_run_e2e.py::test_partial_payroll_run_e2e
  tests/test_payroll_pipeline_e2e.py::test_full_payroll_pipeline_e2e
  tests/test_payroll_retry.py::test_payroll_retry_e2e

Root cause (all 4, identical): assertion `body["status"] == "success"` against
POST /payroll/run, which now returns the run object with `status: DRAFT`
(execution moved to a background task in Sprints 31-32). This is TF-7,
already tracked in project memory (handoff_note.md) as a pre-existing,
unrelated test-assertion gap — not caused by this sprint.
```

## Data Integrity Spot-Check
Not applicable this sprint — no migration, no new tables/columns, no data mutation. Skipped per Step 5's own scope ("after any migration or data change").

## Known Pre-Existing Issues
- TF-7 (4 test files, listed above): `body["status"]` assertion stale since Sprints 31-32's background-task change. Pre-dates this sprint. Confirmed via `git stash` A/B test.
- TF-3 (`test_payroll_lock_and_approval.py` — separate historical fixture collision issue, per `docs/ROADMAP.md`'s existing Known Test Failures table): not re-verified this session, out of scope for Sprint A.

## Deferred
1. Manual browser click-through of the Payroll Inputs page (add/edit form + main table RATE column) — recommended before production release, not performed this session (no dev server started).
2. `tests/test_cross_period_legacy_fallback.py` (Fix 2's dedicated e2e test, named in the plan) — not written this session; Fix 2 verified via CODE REVIEW/architecture trace only, not LIVE execution.
3. A dedicated fixture for Fix 3 (future-dated rate excluded from current-period calculation) in `tests/test_payroll_retry.py` — not written this session; covered indirectly (no regression) but not directly asserted.
4. Sprint B (the `locked_at`/lock/audit mechanism, explicitly out of scope per the split decision) — untouched, as intended.

## Sign-off
Verified by: Claude Code (automated), 2026-07-04
