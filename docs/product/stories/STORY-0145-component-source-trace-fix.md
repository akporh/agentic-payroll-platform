# `STORY-0145` — AUD-1/Q1: `component_source` field added to `fixed_amount` trace on fallback

**Origin code(s):** `PT-A4-31` · `PT-Q-01` · `AUD-1/Q1`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-1` — Payroll calculation trace auditability
**Classification:** `operational story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll auditor / operator verifying a stored calculation result after the fact, without needing to re-query live salary-component configuration.

## Problem addressed

The `fixed_amount` calculation method's fallback logic derives an amount from a named salary component when the configured `amount` is `0` (`components.get(component_source, ...)`), but the trace entry recorded alongside that derivation did not name which component the value came from. `component_trace_jsonb` is the durable, persisted record an auditor reads later — "amount alone is not evidence; amount + source is evidence" (this repository's auditor-skill standing rule). Without the source name in the trace, the derivation path was invisible from stored data alone.

## Delivered behaviour

The `fixed_amount` branch of `backend/domain/payroll/rule_evaluator.py` now adds a `"component_source"` key to both the `"applied"` and `"not_applied"` trace dicts: the actual source-component name when the fallback fires, `null` when it does not (never omitted). No other trace field or the derivation math itself changed.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track Q — Audit Observations, item Q1 / `AUD-1` (raised Sprint 10, status was 🔜 until this ICM sprint closed it 2026-07-12).

## Implementation evidence

- `backend/domain/payroll/rule_evaluator.py`, `fixed_amount` branch (lines ~412–465) — `fallback_fired` capture, `component_source_used` derivation, `"component_source"` key added to both trace dicts.
- `tests/test_rule_evaluator.py`, class `TestFixedAmount` — 4 new tests: `test_component_source_recorded_when_fallback_fires`, `test_component_source_null_when_fallback_does_not_fire`, `test_component_source_null_when_not_configured`, `test_component_source_present_on_not_applied_branch`.
- Commit: `a8ffc76` — "Add component_source to fixed_amount trace entries (AUD-1 / Q1)".
- Full detail: `docs/sprints/aud-q1-trace-source/evidence/implementation/component_source_trace_fix.md`.

## Test / review evidence

- `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md` — audit verdict: AUD-1/Q1 CLOSED, all 3 acceptance criteria verified from code and test evidence.
- `docs/test-reports/2026-07-12-aud-q1-trace-source.md` — LIVE taxonomy test report; `python -m pytest tests/test_rule_evaluator.py -v -k "FixedAmount"` → 7 passed; full suite `python -m pytest` → 306 passed, 1 pre-existing intentional skip, 0 failed.
- `docs/sprints/aud-q1-trace-source/retrospective.md` — sprint-close retro, product-fix verdict PASS, 0 regressions.

## Decision references

- `DEC-aud-q1-trace-source-01` through `DEC-aud-q1-trace-source-05` (`docs/sprints/aud-q1-trace-source/decisions.md`) — architecture and arch-council `not-applicable`, security `not-applicable`, verification `not-applicable`, implementation `activate` (plan-approval gate).
- `D-015` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4A pilot.

## Dependencies

None. This is a self-contained additive trace-field change inside one existing rule branch; no migration, no other story's completion is a precondition.

## Delivery sprint(s)

Raised Sprint 10 (as `AUD-1`/`Q1`, part of the broader `STORY-0067` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A4-13`) fallback-fix item — see `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` line 186). Delivered in ICM sprint workspace `aud-q1-trace-source` (2026-07-12), the first sprint to use the current `docs/sprints/<sprint-id>/state.md`/`decisions.md`/`evidence/` structure.

## Delivery history

- 2026-07-12 — ICM sprint `aud-q1-trace-source` — `component_source` field added to `fixed_amount` trace (commit `a8ffc76`); audited and tested complete same day; sprint retro closed 2026-07-13.
- 2026-07-15 — Phase 4A pilot (`docs/programmes/product-traceability/`) — story migrated into `docs/product/` as one of the two authorised pilot items (D-015).

## Unresolved questions

The discovery document (`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`) records this same delivered item under two other provisional IDs: `STORY-0067` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A4-13`) (the broader Sprint 10 `fixed_amount` fallback fix that originally raised AUD-1/Q1, before it was closed) and `STORY-0145` (was `PT-Q-01`) (the Track Q cross-cutting audit-observations table entry). `STORY-0145` (was `PT-A4-31`) is used here as the stable story ID because it is the entry that specifically and only describes this ICM-sprint-delivered fix; the mapping between the three provisional IDs is not itself a decision this pilot is authorised to make (D-007 fixes discovery-document IDs as the migration source, not a deduplication scheme) — a future migration pass should decide, with human input, whether `STORY-0067` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A4-13`)/`STORY-0145` (was `PT-Q-01`) should be retired as duplicates of `STORY-0145` (was `PT-A4-31`) or kept as distinct historical markers.
