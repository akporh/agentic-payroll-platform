# Verification — 04-001 + 05-001

## Focused tests

```
$ python -m pytest tests/test_payroll_retry_snapshot_first.py -v

tests/test_payroll_retry_snapshot_first.py::test_retry_uses_frozen_statutory_snapshot_not_intervening_live_rule PASSED
tests/test_payroll_retry_snapshot_first.py::test_retry_hard_fails_on_legacy_v1_statutory_snapshot PASSED
tests/test_payroll_retry_snapshot_first.py::test_v2_retry_issues_no_live_statutory_rule_or_tax_band_query PASSED
tests/test_payroll_retry_snapshot_first.py::test_snapshot_creation_failure_aborts_calculation_and_marks_run_failed PASSED
tests/test_payroll_retry_snapshot_first.py::test_successful_snapshot_creation_still_calculates_normally PASSED

5 passed, 5 warnings in 3.72s
```

Test-to-acceptance-criterion mapping:

| Test | Acceptance criterion |
|---|---|
| `test_v2_retry_issues_no_live_statutory_rule_or_tax_band_query` | 1 — a v2 retry never queries live statutory rule/tax-band data (verified via a `before_cursor_execute` SQL spy, not inference from output) |
| `test_retry_uses_frozen_statutory_snapshot_not_intervening_live_rule` | 2 — a retried employee uses the exact frozen statutory content from the original run |
| `test_retry_hard_fails_on_legacy_v1_statutory_snapshot` | 3 — a legacy/malformed statutory snapshot fails before result deletion, calculation, or persistence |
| `test_snapshot_creation_failure_aborts_calculation_and_marks_run_failed` | 4, 5 — snapshot-creation failure prevents calculation/persistence and is operator-visible via the API |
| `test_successful_snapshot_creation_still_calculates_normally` | (regression guard) — the normal path is unchanged |

## Broader regression

```
$ python -m pytest tests/ -q

291 passed, 1 skipped, 46 warnings in 10.60s
```

The one skip (`test_payroll_reconciliation.py:347`, "Payment reconciliation
is a Phase 2 feature") pre-dates this sprint and is unrelated.

Four pre-existing tests required updates to keep passing, all because they
asserted the *old* v1-snapshot shape (`rules_context_snapshot["payroll_rules"]`)
for workspaces whose only payroll rule lacked `effective_from` — a shape
that no longer occurs now that v2 statutory content is always frozen
(see summary.md, "blocking gap found and fixed"). None of these changes
altered what the tests were actually verifying (retry lifecycle, snapshot
immutability, full pipeline correctness) — only the specific shape
assertion for the snapshot's rule-set sub-object:

- `tests/test_payroll_retry.py` — added `effective_from` to the fixture's
  PENSION rule so it exercises a *v2, rule-set-backed* run, matching what
  real current onboarding produces when a workspace does configure a
  custom rule. (Its own retry-success assertions were otherwise
  unaffected — same expected `net_pay` values as before.)
- `tests/test_payroll_pipeline_e2e.py`, `tests/test_payroll_run_snapshot_immutable.py`
  — kept their PENSION rule without `effective_from` (representing a
  workspace with no published rule_set) and updated the assertion to the
  new, correct expectation: `snapshot_version == 2` and `rule_set is None`,
  instead of the old v1 `payroll_rules` list.
- `tests/test_status.py` — expected enum set extended to include `FAILED`.

## Stage 04 controlled reproduction, fixed-behaviour re-run

```
$ python docs/audit-program/04-original-run-retry-parity/evidence/statutory_divergence_controlled_test.py

...
[7] Employee B post-retry result: status=SUCCESS PAYE=36800.0 net_pay=331200.00
[7] Expected PAYE for Employee B if rule A (10%) had been used (matching Employee A's original-run rule): 36800.00
[7] Expected PAYE for Employee B if rule B (25%, the intervening insert) was used instead: 92000.00
[VERDICT] DIVERGENCE NOT REPRODUCED: Employee B's retried PAYE matches rule A (the original run's rule), contradicting the 03-002 hypothesis under this test design.

FINAL VERDICT: REJECTED

[CLEANUP] All test-scoped rows deleted ... Verified via reverse-FK-order DELETE.
```

The exact same script that reproduced the divergence in Stage 04 (verdict
`REPRODUCED`) now returns `REJECTED` — i.e. the divergence can no longer be
produced. Full output at
`docs/audit-program/04-original-run-retry-parity/evidence/2026-07-12-statutory-divergence-test-output.txt`
(overwritten by this re-run; the original `REPRODUCED` run is preserved in
Stage 04's `findings.md` as a quoted excerpt).

## Schema/migration impact

**Not none, as originally expected for the approved scope** — one
migration was required for 05-001 (`error_message` column +
`FAILED` status), documented in summary.md. 04-001 itself required no
schema change, confirming Stage 05 §8's sufficiency analysis. The
blocking-gap fix (v2/rule_set decoupling) required no schema change either
— it changed which in-memory branch `build_rules_context_snapshot` takes,
not the `rules_context_snapshot` column's type or the table structure.

Migration applied and verified against the local non-production
`payroll_dev` database:

```
$ alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade ef2a3b4c5d6e -> b8c9d0e1f2a3, ...
```

```
$ psql ... -c "\d payroll_run" | grep error_message
 error_message | text | | |
```

## Lifecycle behaviour chosen for snapshot creation failure

New terminal status `PayrollRunStatus.FAILED`, reachable only from `DRAFT`.
See summary.md, "Lifecycle design chosen," for the reasoning against reusing
an existing status.

**Recovery behaviour:** a `FAILED` run cannot be retried or restarted — it
never reached `CALCULATING`, so `retry_failed_payroll_employees()` (which
requires `PARTIAL`) correctly rejects it, and no code path transitions a run
out of `FAILED`. Per the sprint prompt's "implement only behaviour supported
by current lifecycle invariants," a **new correction run** is the only
supported recovery path once the underlying snapshot failure (e.g. a
transient DB issue) is resolved — consistent with how every other
irrecoverable run state in this system (pre-snapshot-engine legacy runs,
pre-v2 statutory snapshots) is handled. This was not implemented as new
behaviour; it falls out of `FAILED` simply not appearing in any
`ALLOWED_TRANSITIONS` value.

## Acceptance criteria results

| # | Criterion | Result |
|---|---|---|
| 1 | A v2 retry never queries live statutory rule/tax-band data | ✅ Verified by SQL spy test |
| 2 | A retried employee uses the exact frozen statutory content from the original run | ✅ Verified by controlled reproduction + dedicated regression test |
| 3 | A legacy or malformed statutory snapshot fails before result deletion, calculation, or persistence | ✅ Verified — FAILED row untouched, no new result, run status unchanged |
| 4 | Snapshot creation failure prevents calculation and result persistence | ✅ Verified — `execute_and_persist` not called, zero `payroll_result` rows |
| 5 | Snapshot creation failure is operator-visible outside server logs | ✅ Verified via `GET .../runs/{run_id}` returning `status: FAILED` + `error_message` |
| 6 | Existing snapshot immutability guarantees are preserved | ✅ `trg_run_snapshot_immutable` untouched; no new update-in-place snapshot writes; `test_payroll_run_snapshot_immutable.py` still passes |
| 7 | Focused and broader regression tests pass | ✅ 5/5 focused, 291/291 broader (1 unrelated pre-existing skip) |
| 8 | No production/shared data is modified | ✅ All controlled execution against local non-production `payroll_dev`; zero residue confirmed after every test run and the Stage 04 script re-run |
| 9 | Remediation documentation and audit-state handback are complete | ✅ This file + summary.md + `audit-state.md` update |

All nine acceptance criteria are satisfied.
