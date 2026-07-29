# `STORY-0071` — Employee schema fields: shift_type, state_of_tax, skill_level (NEW-GAP4/13)

**Origin code(s):** `PT-A1-19` · `NEW-GAP4/13`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Bureau setup admin onboarding a workforce with different shift patterns, tax jurisdictions, and skill levels; indirectly, the payroll engine that routes overtime/PAYE/allowance calculations using these fields.

## Problem addressed

The employee record had no way to capture `shift_type` (gating OT2/shift-allowance routing), `state_of_tax` (tax jurisdiction), or `skill_level` — without these, Client B employees on 2-shift or 4-shift schedules received incorrect overtime calculations, and there was no structured field for jurisdiction-aware PAYE routing.

## Delivered behaviour

Migration `f1e2d3c4b5a6` adds `shift_type`, `state_of_tax`, and `skill_level` columns to `employee_contract`. A GET/PATCH API surface exposes and validates these fields, with onboarding-time validation and VARCHAR length guards. `shift_type` directly gates the D9 shift-gate logic in `rule_evaluator.py` (`ot_multiplier` rules with `basic_daily` base return ₦0 for `shift_type` in `(None, "DAY")` — see `STORY-0072` (was `PT-A1-20`)'s sibling item O3, out of this batch's scope but implemented in the same sprint).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O item O1 ("NEW-GAP4 + NEW-GAP13: Employee payroll-critical fields — `shift_type`, `state_of_tax`, `skill_level` columns; migration `f1e2d3c4b5a6`; API GET/PATCH wired; onboarding validation + length guards ✅ | Onboarding (A2) | NEW-GAP4/13 | Sprint 11"); full requirement in `docs/stories/sprint-11-track-o-employee-schema-shift-lta.md`, "O1 — Employee Payroll-Critical Fields."

## Implementation evidence

- `migrations/versions/f1e2d3c4b5a6_add_employee_contract_shift_fields.py` — confirmed by direct inspection during this migration pass.
- `docs/audit/2026-05-02-sprint-11-audit-review.md` — "O1 | `migrations/versions/f1e2d3c4b5a6` | shift_type/state_of_tax/skill_level added to `employee_contract`" (audit-review evidence table).
- `docs/ROADMAP.md` Track S item S5: "`shift_type`, `state_of_tax`, `skill_level` onboarding endpoint: enum allowlist validation + VARCHAR length guards added ✅ | Low | `backend/api/routes/onboarding.py` | SEC-S5 | Sprint 11 | ✅" — the security-hardening half of the same fields.
- Commit `7334a2f` ("feat: sprint 11 — Track O employee schema, shift allowance, grade percentage salary derivation", 2026-05-02) — this single commit is confirmed via `git log --all --oneline -S` on the migration filename as the one that introduced it.

## Test / review evidence

- `docs/audit/2026-05-02-sprint-11-audit-review.md` — the Sprint 11 audit review, which cross-references this migration directly as evidence for O1. The same audit raises two related, explicitly scoped-separately observations: AUD-4 (`shift_type` missing from `component_trace_jsonb` header — since resolved, per Track Q item Q4 ✅) and AUD-5 (`shift_type` re-read live on retry rather than from snapshot — deferred, per Track Q item Q4's "Full closure" note). Neither observation invalidates O1's own delivery; both concern downstream auditability of the field this story adds, not this story's own scope.

## Decision references

- Arch-council joint session for O1 (per `docs/stories/sprint-11-track-o-employee-schema-shift-lta.md`'s "Arch-council gate" section: "Joint arch-council for NEW-GAP4 + NEW-GAP13").
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None recorded as a precondition for this story itself. It is a documented **precondition for** `STORY-0072` (was `PT-A1-20`)'s sibling item O3 (shift gate in `rule_evaluator.py`, out of this batch) and for the deferred LTA anniversary trigger (O5, backlog, not part of this batch).

## Delivery sprint(s)

Sprint 11 (Track O), delivered 2026-05-02 (commit `7334a2f`).

## Delivery history

- 2026-05-02 — Sprint 11 — `employee_contract` gains `shift_type`/`state_of_tax`/`skill_level` via migration `f1e2d3c4b5a6`, with API GET/PATCH wiring and onboarding validation (commit `7334a2f`); audit-reviewed same sprint per `docs/audit/2026-05-02-sprint-11-audit-review.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None specific to this story. Related unresolved items (`PH_OT` `is_pensionable` deferral, tracked separately as `STORY-0036` — not yet migrated, see `../ID-ALLOCATION.md` (was `PT-A1-02`)/D-010) are out of this batch's scope and not carried here.
