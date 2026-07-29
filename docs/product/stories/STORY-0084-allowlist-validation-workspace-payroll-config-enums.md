# `STORY-0084` — SEC-S2 — allowlist validation for `workspace_payroll_config` enums

**Origin code(s):** `PT-S-02` · `SEC-S2`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; bureau setup admin

## Problem addressed

Workspace payroll configuration enum fields accepted values outside their intended set, so a workspace could be configured into a state the engine has no handler for.

## Delivered behaviour

Allowlist validation on the `workspace_payroll_config` enum fields at the API boundary.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S2; `docs/stories/sprint-13-track-m3-m5-track-s-security.md`.

## Implementation evidence

Pydantic schema allowlists on the workspace-payroll-config update schema.

## Test / review evidence

None dedicated — covered within the Sprint 13 security track scope.

## Decision references

None.

## Dependencies

`STORY-0060` — the configuration surface being validated.

## Delivery sprint(s)

Sprint 13 (Track S).

## Delivery history

- Sprint 13 — delivered.
- Sprint 14 — the same treatment applied to `proration_strategy`, incompletely (`STORY-0087`).
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report isolates the Track S items in this sprint.
