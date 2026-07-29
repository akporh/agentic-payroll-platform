# `STORY-0063` — `ot_code` → `rate_code` normalisation

**Origin code(s):** `PT-A1-46` · `WI-02`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-7` — Public holiday & rate-code configuration
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; bureau setup admin

## Problem addressed

Two names for the same concept — `ot_code` in some paths, `rate_code` in others — meant a rule written against one name could fail to resolve against the registry keyed by the other.

## Delivered behaviour

The naming is normalised to `rate_code` throughout, so rules and the registry agree on one key.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` WI-02.

## Implementation evidence

Rule-definition and rate-resolution paths; onboarding parsing.

## Test / review evidence

`docs/test-reports/2026-05-01-sprint-10.md`

## Decision references

None.

## Dependencies

`STORY-0036` — the registry this normalises against.

## Delivery sprint(s)

Sprint 10.

## Delivery history

- Sprint 10 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
