# Audit Review — Pilot Sprint `aud-q1-trace-source` (Q1 / AUD-1)

**Date:** 2026-07-12
**Reviewer:** Claude Code (`/auditor` skill)
**Branch:** `uat`

---

## Scope

Single calculation-trace change introduced in this pilot:

| Ref | File | Change |
|-----|------|--------|
| Q1 / AUD-1 | `backend/domain/payroll/rule_evaluator.py` (`fixed_amount` branch, ~lines 412–465) | Added `"component_source"` key to both `fixed_amount` trace dicts (`applied` and `not_applied`) |

---

## Findings

### AUD-1 — `component_source` not recorded in `fixed_amount` trace entry

**Type:** Finding (raised Sprint 10, Track Q)
**Status:** Closed this sprint

**Location (before fix):** `backend/domain/payroll/rule_evaluator.py:421–443`

**Control Gap:** When a `fixed_amount` rule's configured `amount` was `0` and a `component_source` was set, the engine derived the amount from the named salary component — but the trace entry appended immediately after had no `component_source` key. The derivation path was invisible to anyone reading `component_trace_jsonb` alone; reconstructing it required re-reading live salary-component configuration, which may have since changed.

**Risk:** Per this skill's own standing rule (Check #9, "amount alone is not evidence; amount + source is evidence"), an auditor or automated compliance report could not verify *why* a `fixed_amount` component had a given value when it was fallback-derived, nor distinguish a fallback-derived amount from a directly-configured one.

**Evidence Required:** A structured `component_source` field in the trace entry, present (possibly `null`) on every `fixed_amount` trace entry — not just the ones where the fallback fires.

**Fix applied (verified in code, `rule_evaluator.py:421-465` current state):**
```python
fallback_fired = amount == Decimal("0") and bool(component_source)
if fallback_fired:
    amount = components.get(component_source, Decimal("0"))
component_source_used = component_source if fallback_fired else None
...
trace.append({..., "component_source": component_source_used})   # both applied and not_applied dicts
```

**Verification performed (not just "field exists"):**
- Grep confirms exactly one dynamic-source derivation exists in this branch (`component_source` for `fixed_amount`), and both trace dict literals now carry the key (`rule_evaluator.py:447`, `:464`).
- `tests/test_rule_evaluator.py::TestFixedAmount` — 4 new tests exercise the field, not just its presence:
  - fallback fires → key equals the source component name (`"BASIC"`), not merely non-null
  - fallback does not fire (nonzero amount) → key present, `None`
  - `component_source` not configured at all → key present, `None`
  - condition not met (`not_applied` branch) → key present
- Live run: `pytest tests/test_rule_evaluator.py -k FixedAmount` → 7/7 passed (3 pre-existing + 4 new).
- Full regression suite: 306 passed, 1 pre-existing skip, 0 failed — no other `calculation_method` branch or trace field altered.

**Conclusion:** AUD-1 is genuinely closed — the field exists, is correctly populated with the actual source name when the fallback fires, is `null` (present, not omitted) when it doesn't, and this behaviour is exercised by passing tests rather than asserted by inspection alone.

**Roadmap ref:** Q1 / AUD-1 (Track Q) — should be marked ✅ in `docs/ROADMAP.md` at next roadmap sync.

---

## Out of scope (confirmed, not re-litigated)

- Q2 (persist `period_type` on `payroll_run`) and Q3 (simulate-script `Decimal` conversion) — separate Track Q items, not touched.
- No other `calculation_method` branch (`unit_multiplier`, `ot_multiplier`, `daily_rate_deduction`, `percentage_of_sum`) modified.
- No migration; `component_trace_jsonb` is pre-existing freeform JSONB — additive key only.
