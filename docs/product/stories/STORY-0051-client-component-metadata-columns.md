# `STORY-0051` — `client_component_metadata` add `is_active` + `proration_strategy` (Track J blocker)

**Origin code(s):** `PT-A1-15`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Not directly user-facing — this is the schema foundation the Track J post-onboarding configuration UI (`STORY-0050` (was `PT-A1-11`), statutory override edit/toggle) is built on.

## Problem addressed

`client_component_metadata` had no per-workspace `is_active`/`proration_strategy` columns to override. Track J's WC-10/WC-11 stories (edit/add statutory component overrides) could not be built without this migration landing first — `docs/ROADMAP.md` explicitly flags it as "BLOCKER — must land first" for the whole Track J batch (D-ARCH-4).

## Delivered behaviour

Migration `f9a0b1c2d3e4` adds `is_active BOOLEAN NOT NULL DEFAULT TRUE` and `proration_strategy VARCHAR(50)` columns to `client_component_metadata`, with a matching downgrade that drops both columns (in reverse order). This unblocked the WC-10/WC-11 frontend and API work in the same Track J delivery batch.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 36 ("Migration: add `is_active` + `proration_strategy` to `client_component_metadata` | Onboarding (A1) | WC-10/D-ARCH-4 | **BLOCKER — must land first**").

## Implementation evidence

- `migrations/versions/f9a0b1c2d3e4_add_component_override_columns.py` — confirmed by direct inspection during this migration pass: `revision = "f9a0b1c2d3e4"`, `down_revision = "f7a8b9c0d1e2"`; `ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE`, `ADD COLUMN proration_strategy VARCHAR(50)`; downgrade drops `proration_strategy` then `is_active`.
- Commit `db17ef9` (2026-04-22) — `git log --all --oneline` on this migration file isolates this single commit as the one that introduced it.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — Data Integrity Spot-Check table: "updated_at on 6 target tables | 6/6 | PASS — client_component_metadata added by migration 26b848abab55" (a related, subsequent migration adding `updated_at` to the same table, confirming the table and its new columns were live and being exercised at test time). WC-10/WC-11's own PASS verdicts in the same report (see `STORY-0050` (was `PT-A1-11`)) directly exercise these two columns via the PATCH/upsert endpoints.

## Decision references

- D-ARCH-4 (`docs/stories/track-j-workspace-config-management.md`) — "Migration first (BLOCKER): `client_component_metadata` needs `is_active` + `proration_strategy` columns."
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None upstream. This is itself a blocking dependency **for** `STORY-0050` (was `PT-A1-11`) (WC-10/11 edit/toggle UI) and `STORY-0053` (was `PT-A1-17`) (extended `/configuration` GET) — both read/write the columns this migration adds.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-22 — Track J — `client_component_metadata.is_active`/`proration_strategy` columns added via migration `f9a0b1c2d3e4` (commit `db17ef9`), unblocking WC-10/WC-11.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

None.
