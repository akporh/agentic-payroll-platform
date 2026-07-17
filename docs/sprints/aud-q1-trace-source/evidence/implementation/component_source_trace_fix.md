# Implementation Evidence — `component_source` in `fixed_amount` trace (AUD-1 / Q1)

**Stage:** implementation
**Date:** 2026-07-12
**Plan:** `../../plan.md`

## Code change

`backend/domain/payroll/rule_evaluator.py`, `fixed_amount` branch (lines ~412–465):

- Captured `fallback_fired = amount == Decimal("0") and bool(component_source)` before `amount` is overwritten by the derivation.
- Introduced `component_source_used = component_source if fallback_fired else None`.
- Added `"component_source": component_source_used` as a new key to both the `"applied"` and `"not_applied"` trace dicts.
- No other key, and no change to the derivation math itself (`amount = components.get(component_source, Decimal("0"))` unchanged).

This matches `plan.md` exactly — no scope broadened to other `calculation_method` branches.

## Tests added

`tests/test_rule_evaluator.py`, class `TestFixedAmount`:

- `test_component_source_recorded_when_fallback_fires` — amount=0 + component_source="BASIC", BASIC=50000 → `components["DERIVED_BONUS"] == 50000` and `trace[0]["component_source"] == "BASIC"` (AC #1)
- `test_component_source_null_when_fallback_does_not_fire` — nonzero configured amount → `trace[0]["component_source"] is None` (AC #2)
- `test_component_source_null_when_not_configured` — no `component_source` on the rule at all → key present, `None` (AC #2)
- `test_component_source_present_on_not_applied_branch` — condition not met → `"component_source"` key present in the `not_applied` trace entry (AC #2, `not_applied` branch)

## Verification run (LIVE)

```
$ python -m pytest tests/test_rule_evaluator.py -v -k "FixedAmount"
7 passed in 0.07s
```

All 4 new tests pass; all 3 pre-existing `TestFixedAmount` tests continue to pass unmodified — confirms AC #3 (no change to `status`, `amount`, `result`, `note`, `rule_set_id`, `rule_effective_from`, `reference_date`, `rate_used`, `resolution_source`, `warning`, or the derivation logic itself).

Full regression suite:

```
$ python -m pytest
306 passed, 1 skipped in 182.51s
```

Zero failures, zero new skips. The 1 skip is the pre-existing, intentional Phase-2 reconciliation skip (`test_payroll_reconciliation.py:347`), unrelated to this change.

## Acceptance criteria — self-check

| AC | Result |
|---|---|
| 1. Fallback fires → trace records the source component name | PASS — `test_component_source_recorded_when_fallback_fires` |
| 2. Fallback doesn't fire → key present with `null`, never omitted | PASS — 3 tests covering nonzero-amount, no-component_source, and not_applied-branch cases |
| 3. All other trace fields and the derivation logic unchanged | PASS — pre-existing `TestFixedAmount` tests pass unmodified; diff shows no other key touched |

## Scope check

No other `calculation_method` branch touched (confirmed by diff — only the `fixed_amount` branch at lines ~412–465 changed). No migration. No change to `_period_context`, `sequential_executor.py`, or component-metadata resolution.
