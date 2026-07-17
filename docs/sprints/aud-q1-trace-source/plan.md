<!--
Copied verbatim from ~/.claude/plans/moonlit-percolating-llama.md immediately
after ExitPlanMode approval, per D5 (docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md).
The harness-owned original at that path is untouched — this is a durable
repository copy, not a move.
Approved: 2026-07-12.
-->

# Add `component_source` to `fixed_amount` trace entries (AUD-1 / Q1)

## Context

`docs/ROADMAP.md` Track Q — Audit Observations, item **Q1** (raised Sprint 10, still 🔜): when a `fixed_amount` rule's configured `amount` is `0` and a `component_source` is set, the engine derives the amount from the named salary component (`backend/domain/payroll/rule_evaluator.py:425-426`) — but the trace entry appended immediately after has no `component_source` key. An auditor reading `component_trace_jsonb` alone cannot tell where a derived `fixed_amount` value came from; per the auditor skill's own standing rule, "amount alone is not evidence; amount + source is evidence."

This is the pilot sprint (`docs/sprints/aud-q1-trace-source/`) for the non-linear ICM sprint-workflow implementation — a small, real, bounded fix chosen specifically to exercise the workflow mechanics (plan persistence, this changeset) without a large or contested surface area.

Scope, source item, and acceptance criteria are already agreed and recorded in `docs/sprints/aud-q1-trace-source/CONTEXT.md`. This plan implements exactly those three acceptance criteria — no more.

## Approach

Single-file change to `backend/domain/payroll/rule_evaluator.py`, inside the `fixed_amount` branch (currently lines 412-461).

1. Immediately after the existing fallback-derivation block (lines 421-426), capture whether the fallback actually fired, before `amount` is overwritten:

   ```python
   component_source = resolved_defn.get("component_source")
   fallback_fired = amount == Decimal("0") and bool(component_source)
   if fallback_fired:
       amount = components.get(component_source, Decimal("0"))
   component_source_used = component_source if fallback_fired else None
   ```

   (Replaces the existing `if amount == Decimal("0") and component_source:` block — same condition, same derivation, no behavior change to the derived `amount` value. `component_source_used` is the only new state.)

2. Add `"component_source": component_source_used` as a new key to **both** existing `trace.append({...})` dicts in this branch — the `"applied"` one (lines 431-445) and the `"not_applied"` one (lines 447-461). Using the same `component_source_used` variable in both branches means:
   - AC #1 (fallback fired → name recorded): satisfied in the `"applied"` branch, since `fallback_fired` only requires `amount == 0 and component_source` — independent of whether the rule's condition later evaluates true.
   - AC #2 (fallback didn't fire → key present with `null`): satisfied by construction — `component_source_used` is `None` whenever `fallback_fired` is `False`, and the key is always present (dict literal, not conditionally added).
   - AC #3 (no other field or the derivation logic itself changes): satisfied — every other key in both dicts is untouched, and the `amount` derivation math is identical to today, just captured in a named variable one line earlier.

No other `calculation_method` branch (`unit_multiplier`, `ot_multiplier`, `daily_rate_deduction`, `percentage_of_sum`, etc.) is touched. No migration — `component_trace_jsonb` is an existing freeform JSONB column; this adds a key to entries within it, not a schema change.

## Verification

- Run the existing payroll test suite's `fixed_amount` coverage (`grep -rln "fixed_amount" tests/`) to confirm no regression in `amount`/`result`/`status` values.
- Add/extend a test asserting: (a) a `fixed_amount` rule with `amount=0` and `component_source` set, where the named component has a nonzero value, produces a trace entry with `"component_source"` equal to that component's name; (b) a `fixed_amount` rule with a nonzero configured `amount` (no fallback) produces a trace entry with `"component_source": None`.
- Manually run a payroll simulation (`scripts/simulate_payroll_components.py` or a targeted pytest) and inspect the resulting `component_trace_jsonb` for a `fixed_amount` rule in both scenarios to confirm the field is present and correctly populated — this is the live check the pilot's `/tester` stage will perform later, not part of this plan-mode changeset.
