# `STORY-0013` — Active pay-cycle guard — at most one active cycle per workspace

**Origin code(s):** `PT-A1-05` · `PC4`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-6` — Client onboarding & workspace creation
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

Two simultaneously active pay cycles in one workspace make the question 'which period are we running?' ambiguous, and the engine has no principled way to choose.

## Delivered behaviour

At most one `pay_cycle` row per workspace may be active at a time; the constraint is enforced rather than merely assumed by the UI.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A1, item PC4.

## Implementation evidence

`pay_cycle` partial unique index on `(workspace_id) WHERE is_active`; guard in the pay-cycle service.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Recorded as a standing data-contract invariant in `CLAUDE.md`: `pay_cycle (workspace_id) WHERE is_active` — at most one active cycle per workspace.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Track J — post-setup update endpoint added on top of this guard (`STORY-0046`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
