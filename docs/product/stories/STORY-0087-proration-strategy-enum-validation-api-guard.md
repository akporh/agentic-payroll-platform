# `STORY-0087` — SEC-S6 — `proration_strategy` enum validation at the API, DB constraint still open

**Origin code(s):** `PT-S-06` · `SEC-S6`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `tentative`

## Actor

engineer; bureau setup admin

## Problem addressed

`proration_strategy` — introduced by the Sprint 14 configurable-proration work — accepted values outside its intended set, so a workspace could be configured to a proration strategy the engine does not implement.

## Delivered behaviour

An API-level allowlist guard on `proration_strategy`. **The matching database constraint was not added and remains open.**

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S6 — the table records the DB constraint as still pending (⬜).

## Implementation evidence

Pydantic allowlist on the proration-strategy field; no migration.

## Test / review evidence

`docs/security/2026-05-13-sprint-14-16-security-review.md`.

## Decision references

None.

## Dependencies

`STORY-0086` — the configurable proration work that introduced the field.

## Delivery sprint(s)

Sprint 14 (Track S).

## Delivery history

- Sprint 14 — API guard delivered; DB constraint deliberately not shipped.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**Partially delivered, and recorded as such.** The API allowlist is the only enforcement; a write path that bypasses the route can still store an invalid strategy. Confidence is `tentative` for that reason. This is the same shape of exposure that `payroll_run.run_type` carries and that `CLAUDE.md` records as a standing hazard — an API allowlist without a DB CHECK.
