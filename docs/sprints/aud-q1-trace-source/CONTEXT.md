# Pilot Sprint — `aud-q1-trace-source`

**Status:** scope agreed 2026-07-12 (this session — see decision trail below); implementation not yet started.
**Role:** ICM sprint-workflow pilot, per `docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md`, Changeset 2. This is a real, shippable fix — not a synthetic workflow exercise — deliberately chosen to be small and bounded so the workflow mechanics can be validated independently of feature complexity.

---

## Goal

Add a `component_source` field to the `fixed_amount` rule's trace entry in `backend/domain/payroll/rule_evaluator.py` so the derivation path is auditable directly from the stored `component_trace_jsonb`, without needing to re-read live DB state.

## Source item

`docs/ROADMAP.md`, Track Q — Audit Observations, item **Q1**:

> Add `"component_source"` field to `fixed_amount` trace entry when fallback fires — derivation path must be auditable — `backend/domain/payroll/rule_evaluator.py:327–338` — ref `AUD-1` — raised Sprint 10 — status 🔜

Confirmed still open by reading the live file (2026-07-12): the `fixed_amount` branch's fallback logic (lines 421–426) reads `component_source` and derives the amount from `components[component_source]` when the configured `amount` is zero, but the trace entry built immediately after (lines 428–443) has no `component_source` key — the derivation is invisible to anyone reading the trace alone. This matches the auditor skill's own standing rule: "amount alone is not evidence; amount + source is evidence."

## In-scope stories

- Q1 / AUD-1 only. No other Track Q item (Q2, Q3) is bundled into this pilot.

## Acceptance criteria

1. When a `fixed_amount` rule's configured `amount` is `0` and `component_source` is set (triggering the derive-from-named-salary-component fallback at `rule_evaluator.py:425–426`), the trace entry appended for that rule includes a `"component_source"` key naming the salary component the amount was derived from.
2. When the fallback does not fire (amount is nonzero, or no `component_source` is configured on the rule), the trace entry's `"component_source"` key is present with value `null` — never omitted. Presence-with-`null` vs. presence-with-a-name is the only signal; the key's absence never occurs for a `fixed_amount` trace entry.
3. All other `fixed_amount` trace fields (`status`, `amount`, `result`, `note`, `rule_set_id`, `rule_effective_from`, `reference_date`, `rate_used`, `resolution_source`, `warning`) and the derivation logic itself (lines 421–426) are unchanged — this is an additive trace field only, not a calculation change.

## Out of scope

- Any other `calculation_method`'s trace entry (`unit_multiplier`, `ot_multiplier`, `daily_rate_deduction`, `percentage_of_sum`, etc.) — only `fixed_amount` is touched.
- Q2 (persist `period_type` on `payroll_run`, requires a migration) and Q3 (simulate-script `Decimal` conversion) — separate ROADMAP items, deliberately not bundled into this pilot to keep it single-area and migration-free.
- Any change to `_period_context`, `sequential_executor.py`, or component-metadata resolution.
- The workflow mechanics themselves (Changesets 3+) — this sprint proves Changeset 2 only.

## Why this item fits the pilot constraints

| Constraint | How Q1 satisfies it |
|---|---|
| Bounded to one area | Single file, single rule branch (`fixed_amount`) |
| No migration / data-contract change | Additive key inside an already-freeform JSONB trace blob — no schema change |
| Clear acceptance criteria | Three testable, unambiguous criteria above |
| Exercises planning, implementation, verification, testing | `pm` (this scoping), `implementation` (the fix), `audit` (registry entry condition fires — `rule_evaluator.py` is touched), `test` (LIVE trace assertion) all genuinely activate; `architecture`, `arch-council`, `security`, `verification` genuinely resolve `not-applicable` rather than being artificially skipped — see `state.md` and `decisions.md` |
| Finishable within one short sprint | Estimated S (half day) — single function, no new tests infrastructure needed |
