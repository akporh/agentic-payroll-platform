# `STORY-0012` — Component overrides update endpoint

**Origin code(s):** `PT-A1-04` · `P1-8`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

A workspace whose statutory or component rates differ from the platform default had no way to record that difference after onboarding.

## Delivered behaviour

An endpoint to update a workspace's component overrides — the mechanism later hard-gated for statutory components by `STORY-0052` and surfaced in the UI by `STORY-0050`.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability area A1, item P1-8.

## Implementation evidence

`backend/api/routes/` component override PATCH; `client_component_metadata` / `overrides_json`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

None at delivery time. A later standing hazard is recorded outside this record: `patch_component_override` destroys NHF/health/levy rates if `overrides_json` is absent from the payload.

## Dependencies

None.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- Track J — statutory components hard-rejected on this path (`STORY-0052`); UI added (`STORY-0050`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period.
