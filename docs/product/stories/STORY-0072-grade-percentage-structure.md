# `STORY-0072` — Grade percentage structure (total_monthly/basic_pct/etc., NEW-GAP12)

**Origin code(s):** `PT-A1-20` · `NEW-GAP12`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-4` — Employee records & CRUD
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Bureau setup admin who wants to define a grade's total monthly salary once and have component amounts (basic/housing/transport/utility) derived automatically as percentages, rather than entering each component amount by hand.

## Problem addressed

Before this story, salary components had to be entered as absolute amounts per employee/salary-definition. There was no way to define a grade-level percentage structure (e.g. "basic = 60% of total_monthly") that the engine could derive amounts from — every grade change required manually recalculating every component.

## Delivered behaviour

Migration `a2b3c4d5e6f7` adds `total_monthly`, `basic_pct`, `housing_pct`, `transport_pct`, `utility_pct` columns to the `grade` table. A new pure function in `backend/domain/payroll/salary_derivation.py` computes each component as `total_monthly × pct`, with the grade-percentage structure winning over any conflicting component definition when `total_monthly` is non-null (arch-council decision D6), and residual rounding (round-half-up) absorbed into the largest component so the sum of derived components equals `total_monthly` exactly (decision D7).

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O item O2 ("NEW-GAP12: Grade percentage structure — `total_monthly`, `basic_pct`, `housing_pct`, `transport_pct`, `utility_pct` on `grade` table; migration `a2b3c4d5e6f7`; `salary_derivation.py` pure function; grade pct wins when `total_monthly` non-null (D6); round-half-up + residual (D7) ✅ | Onboarding (A2) | NEW-GAP12 | Sprint 11"); full requirement in `docs/stories/sprint-11-track-o-employee-schema-shift-lta.md`, story O2.

## Implementation evidence

- `migrations/versions/a2b3c4d5e6f7_add_grade_percentage_structure.py` — confirmed by direct inspection during this migration pass.
- `docs/audit/2026-05-02-sprint-11-audit-review.md` — "O2/D6 | `backend/domain/payroll/salary_derivation.py` (NEW) | Grade percentage salary derivation — `total_monthly × pct` per component; grade wins when `total_monthly` non-null" and "O2 | `migrations/versions/a2b3c4d5e6f7` | total_monthly/basic_pct/housing_pct/transport_pct/utility_pct added to `grade`".
- Commit `7334a2f` (2026-05-02) — isolated via `git log --all --oneline -S` on the migration filename.

## Test / review evidence

- `docs/audit/2026-05-02-sprint-11-audit-review.md` — Grade pct derivation checked directly: "Grade pct derivation — D7 residual absorbed | ✅ PASS | Largest component absorbs residual; sum of derived components equals `total_monthly` exactly."

## Decision references

- D6 (grade percentage structure wins when `total_monthly` non-null), D7 (round-half-up + residual absorption) — both recorded in `docs/ROADMAP.md`'s Track O item O2 and verified in the Sprint 11 audit review.
- Arch-council standalone session for O2 (`docs/stories/sprint-11-track-o-employee-schema-shift-lta.md`: "Standalone arch-council for NEW-GAP12. Changes how `salary_components` dict is populated at run time — every handler that reads BASIC is downstream.").
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. Additive columns + a new pure derivation function; no other story in this batch is a precondition.

## Delivery sprint(s)

Sprint 11 (Track O), delivered 2026-05-02 (commit `7334a2f`).

## Delivery history

- 2026-05-02 — Sprint 11 — `grade` percentage-structure columns + `salary_derivation.py` derivation function delivered (commit `7334a2f`); audit-verified same sprint (D7 residual-absorption check PASS) per `docs/audit/2026-05-02-sprint-11-audit-review.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
