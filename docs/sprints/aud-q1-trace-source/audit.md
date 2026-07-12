# Audit — `aud-q1-trace-source`

**Stage:** audit
**Date:** 2026-07-12
**Existing output:** `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`

## Verdict

**AUD-1 / Q1: CLOSED.**

Verified from code (`rule_evaluator.py:421-465`) and test evidence (`tests/test_rule_evaluator.py::TestFixedAmount`, 4 new tests + 3 pre-existing, all passing; full suite 306 passed / 1 pre-existing skip / 0 failed) that:

1. The `component_source` key is present on both `fixed_amount` trace dicts (`applied`, `not_applied`).
2. When the fallback fires, the value equals the actual source component name used for derivation — exercised by a test asserting the specific name (`"BASIC"`), not just non-null.
3. When the fallback does not fire (nonzero amount, or no `component_source` configured), the key is present with `null` — never omitted — exercised by two separate tests covering both reasons the fallback can fail to fire.
4. No other trace field or the derivation logic itself changed — confirmed by the 3 pre-existing `TestFixedAmount` tests continuing to pass unmodified, and by diff inspection showing only the `fixed_amount` branch touched.

This satisfies the auditor skill's standing rule (Check #9): "amount alone is not evidence; amount + source is evidence" — the source is now present, correct, and machine-verifiable directly from `component_trace_jsonb`, without needing to re-read live salary-component configuration.

## Evidence referenced

- `evidence/implementation/component_source_trace_fix.md` (this sprint)
- `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md` (existing convention, full finding writeup)
- `tests/test_rule_evaluator.py::TestFixedAmount` (live pytest run, this session)

## State transition

`audit`: `blocked` → `active` → `complete` (this pass — see `state.md`).
