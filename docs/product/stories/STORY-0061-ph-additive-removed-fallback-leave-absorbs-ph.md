# `STORY-0061` — `PH_ADDITIVE` removed from the UI, backend falls back to `LEAVE_ABSORBS_PH`

**Origin code(s):** `PT-A1-44` · `WI-12`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

bureau setup admin

## Problem addressed

`PH_ADDITIVE` was offered as a selectable PH mode but its engine handling was not established, so an operator could configure a workspace into a mode the engine did not reliably implement.

## Delivered behaviour

`PH_ADDITIVE` is removed from the UI's options and the backend falls back to `LEAVE_ABSORBS_PH`, so no workspace can be left in the unverified mode.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` WI-12.

## Implementation evidence

PH-mode options in the workspace configuration UI; backend fallback in the PH handling path.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

The related standing UI rule recorded outside this programme: an enum fallback in a `useEffect` must use the domain default (`LEAVE_ABSORBS_PH`), never an empty string.

## Dependencies

`STORY-0035` — the PH engine whose mode set this narrows.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 7 — PH modes introduced including `PH_ADDITIVE`.
- Sprint 10 — `PH_ADDITIVE` withdrawn from the UI; backend fallback added.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

Whether `PH_ADDITIVE` was ever correctly handled by the engine was never confirmed — it was withdrawn rather than fixed. Project memory records the engine handling as unconfirmed and warns against relying on it.
