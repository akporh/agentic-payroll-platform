# `STORY-0132` — Payroll rule versioning — `effective_from`, auto-publish, UNIQUE constraint

**Origin code(s):** `PT-A5-07` · `RULE-VER-1` · `RULE-VER-2` · `RULE-VER-3`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-7` — Governance & Run State Machine
**Feature:** `FEAT-31` — Statutory & payroll rule versioning
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin; auditor

## Problem addressed

A payroll rule could be edited in place, which silently changed how already-run periods would recalculate. Rules needed the same effective-dating discipline that statutory rules had held since `STORY-0026`.

## Delivered behaviour

Payroll rules carry `effective_from`, a new version auto-publishes, and a UNIQUE constraint prevents two versions of the same rule sharing an effective date.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Sprint RULE-VER-1 (RULE-VER-1/2/3).

## Implementation evidence

`payroll_rule.effective_from` and its UNIQUE constraint in `migrations/versions/`; rule versioning in the rule service; rule versioning UI.

## Test / review evidence

`docs/test-reports/2026-06-21-payroll-rule-versioning.md`.

## Decision references

This sprint's retro recorded four binding lessons: the service flush/commit boundary, the need for a UNIQUE dedup step before adding the constraint, `extra='forbid'` on the Pydantic schemas, and a copy audit whenever a feature is removed from the UI.

## Dependencies

`STORY-0014` — the rule form this versions; `STORY-0026` — the same discipline on statutory rules.

## Delivery sprint(s)

Sprint RULE-VER-1 (2026-06-21).

## Delivery history

- Sprint RULE-VER-1 — delivered.
- Sprint B-UI — the misleading Activate/Deactivate toggle replaced by a one-way withdraw (`STORY-0136`) and its stale copy cleaned up (`STORY-0137`).
- Sprint A (2026-07-04) — three defects in how the engine *resolves* these versions found and fixed (`STORY-0133`, `STORY-0134`, `STORY-0135`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None for the versioning mechanism itself. Sprint A later established that `is_active` on a versioned rule means "not withdrawn", never "currently in effect" — see `STORY-0135`.
