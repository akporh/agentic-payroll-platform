# Pilot Sprint Test Report — `aud-q1-trace-source` — 2026-07-12

## Summary
| Metric | Value |
|---|---|
| Sprint | `aud-q1-trace-source` (ICM sprint-workflow pilot, Changeset 5) |
| Date | 2026-07-12 |
| Test suite | 306 passed, 1 skipped (pre-existing, unrelated), 0 failed |
| Focused checks | 4 new + 3 pre-existing `TestFixedAmount` assertions |
| Overall verdict | PASS |

## Environment

Backend-only, migration-free, non-API change (`backend/domain/payroll/rule_evaluator.py`, a pure domain function) — no Alembic migration, no route file, no frontend file touched. `verification` and `security` stages are `not-applicable` for this pilot (confirmed in `state.md`/`decisions.md`) — Steps 1–3 of the standard workflow (env check, migration integrity, API verification) do not apply and are not run.

## Sprint Items Verified

| AC (from `CONTEXT.md`) | Check | Result |
|---|---|---|
| AC #1 — fallback fires → trace records source component name | `test_component_source_recorded_when_fallback_fires`: amount=0, component_source="BASIC", BASIC=50000 → `components["DERIVED_BONUS"] == 50000`, `trace[0]["component_source"] == "BASIC"` | **PASS** `LIVE` |
| AC #2 — fallback doesn't fire → key present with `null`, never omitted | `test_component_source_null_when_fallback_does_not_fire` (nonzero configured amount), `test_component_source_null_when_not_configured` (no `component_source` on rule), `test_component_source_present_on_not_applied_branch` (`not_applied` branch) | **PASS** `LIVE` (3 tests) |
| AC #3 — all other trace fields and derivation logic unchanged | Pre-existing `test_applied_when_condition_met`, `test_not_applied_when_condition_not_met`, `test_no_condition_always_applied` continue to pass unmodified | **PASS** `LIVE` |

```
$ python -m pytest tests/test_rule_evaluator.py -v -k "FixedAmount"
7 passed in 0.11s
```

## Regression Suite

```
$ python -m pytest
306 passed, 1 skipped, 48 warnings in 182.51s
```

Zero failures. No new skips — the 1 skip is the pre-existing, intentional Phase-2 payment-reconciliation skip (`tests/test_payroll_reconciliation.py:347`), unrelated to this change (confirmed unchanged from the 2026-07-11 test-harness baseline report).

## Data Integrity Spot-Check

Not applicable — this change is a pure in-memory trace-field addition with no DB write path and no migration. No DB-level spot-check has anything new to verify.

## Known Pre-Existing Issues

None new. The suite's single skip pre-dates this sprint (see `docs/test-harness-checklist.md` / `docs/test-reports/2026-07-11-test-harness-baseline.md`).

## Deferred

- `docs/ROADMAP.md` Track Q's Q1/AUD-1 status marker (🔜 → ✅) is not updated here — that is the `roadmap` stage's responsibility on next sync, not `test`'s. `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md` records the closure for that purpose.
- No live DB simulation (`scripts/simulate_payroll_components.py`) run against a real workspace — the plan's verification step allows a targeted pytest as the live check in place of a DB simulation, and the pytest run above directly exercises the production `apply_payroll_rules` function (not a mock), which satisfies the LIVE bar.

## Sign-off
Verified by: Claude Code (automated, `/tester` skill)
