# `STORY-0086` — Workspace-configurable hire and termination proration, strategy-aware (Sprint 14 P1)

**Origin code(s):** `PT-A4-26` · `P1`
**Outcome:** `OUT-4` — Accurate, compliant statutory payroll calculation
**Capability:** `CAP-6` — Execution Engine
**Feature:** `FEAT-20` — Proration & period handling
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

payroll operator; employee

## Problem addressed

Proration ignored the per-component `proration_strategy` each workspace had already configured (`work_days`, `calendar_days`, `fixed_30`). A sequencing bug also meant hire proration ran **before** `apply_payroll_rules`, corrupting the rate base used by absence deductions — so a mid-period hire's deductions were computed against an already-prorated salary.

## Delivered behaviour

`compute_hire_termination_factor` is strategy-aware; hire proration is re-ordered to run **after** `apply_payroll_rules`, fixing the `daily_rate_deduction` rate base; proration runs per component; structured per-component proration entries are written into `component_trace_jsonb`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track N (N2 partial); `docs/stories/sprint-14-hire-proration-configurable.md`.

## Implementation evidence

`backend/domain/payroll/` — `compute_hire_termination_factor` and the per-component proration loop.

## Test / review evidence

`docs/test-reports/2026-05-10-sprint-14.md`; `docs/retro-reports/2026-05-10-sprint-14.md` — the retro explicitly records a call-chain claim that had to be corrected before sign-off, i.e. genuinely verified rather than asserted.

## Decision references

Arch-council **APPROVED WITH CONDITIONS**, session 2026-05-05; all conditions resolved.

## Dependencies

None.

## Delivery sprint(s)

Sprint 14, delivered 2026-05-10.

## Delivery history

- 2026-05-10 — delivered; ordering fix resolves the `daily_rate_deduction` rate-base defect.
- 2026-07-28 — migrated into `docs/product/` in the Phase 4C `CAP-6` batch (D-025).

## Unresolved questions

`ot_multiplier` rate-base reconstruction (the remainder of Track N's N2) was explicitly left out of scope — self-prorating via input quantity, to be a separate story only if still needed. Track N's N1 (merging `_rule_trace` into `component_trace_jsonb`) remains open behind its own arch-council gate.
