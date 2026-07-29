# `STORY-0046` — WC-1: Pay-cycle post-setup update endpoint

**Origin code(s):** `PT-A1-07` · `WC-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator who needs to correct pay-cycle scheduling fields (run day, cutoff day, payment day, frequency) after initial workspace onboarding.

## Problem addressed

Pay cycle fields were set once during onboarding and were immutable via the UI. An operator who discovered a wrong cutoff day or incorrect payment date had no fix other than a full Excel re-upload of the entire workspace configuration.

## Delivered behaviour

An "Edit Pay Cycle" SlideOver on `WorkspaceConfig.tsx` pre-fills the active pay cycle's current values and submits to a PATCH endpoint that updates the active `pay_cycle` row. The endpoint enforces two guards at the repository layer: an in-progress-run lock (409 if any run for the workspace is in `SUBMITTED | PROCESSING | CALCULATED | PARTIAL | APPROVED`, per the D-ARCH-1 lock window) and a mid-year frequency-change guard (409 if the operator tries to change `frequency` while a PAID run exists in the current calendar year, per D-ARCH-6). `run_day`, `cutoff_day`, `payment_day` are informational only (D-ARCH-7) — an in-SlideOver note says so, since the execution engine does not read them.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 37 (`WC-1`, ref D-ARCH-6/D-ARCH-7); full acceptance criteria in `docs/stories/track-j-workspace-config-management.md`, section "WC-1 — Edit Pay Cycle Settings".

## Implementation evidence

- `docs/stories/track-j-workspace-config-management.md` — WC-1 acceptance criteria (edit-lock, frequency-change guard, informational-fields note).
- `docs/ROADMAP.md` Track J table, item 37: "PATCH `/{wid}/pay-cycle` — update active pay cycle with run-state + frequency guards".
- Commit `db17ef9` ("feat: sprint 7/8 — design system, WorkspaceConfig overhaul, rate codes, migrations, and docs cleanup", 2026-04-22) — Track J delivery commit covering the whole WC-1→WC-11 batch; not independently isolated to a WC-1-only diff in this pass.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — Sprint Items Verified table: "WC-1 | Edit Pay Cycle | PASS | PASS | **PASS** | SlideOver pre-fills, saves, info note shown". The same report's Deferred section notes the D-ARCH-6 mid-year frequency guard specifically was "not smoke-tested (requires a PAID run in current year — test setup too complex for this session)" — the guard exists in code per the acceptance criteria and API check, but its live behaviour was not independently exercised at that pass.

## Decision references

- D-ARCH-1, D-ARCH-6, D-ARCH-7 (`docs/stories/track-j-workspace-config-management.md`, "Arch-Council Decisions Reference").
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None additional beyond the Track J migration blocker `STORY-0051` (was `PT-A1-15`) (`client_component_metadata` `is_active`/`proration_strategy` columns), which gates the whole Track J batch's ability to ship together, not this endpoint specifically (WC-1 touches `pay_cycle`, not `client_component_metadata`).

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track), delivered 2026-04-22 (commit `db17ef9`).

## Delivery history

- 2026-04-21/22 — Track J — Edit Pay Cycle SlideOver + PATCH endpoint with D-ARCH-1/D-ARCH-6/D-ARCH-7 guards delivered (commit `db17ef9`); code-level and live-API PASS same window per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The D-ARCH-6 mid-year frequency-change guard was verified to exist in code and API acceptance criteria but was explicitly not live-tested in the 2026-04-21 Track J test report (test setup complexity — requires a PAID run in the current year). No later test report was found re-verifying it live. This is carried forward as-is, not upgraded.
