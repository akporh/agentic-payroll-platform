# `STORY-0089` — Attendance code + policy workspace configuration, CRUD + immutability (TM-7, Sprint 16)

**Origin code(s):** `PT-A1-41` · `TM-7`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-5` — Attendance & timesheet configuration
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

HR operator for a timesheet-enabled workspace configuring attendance codes and their pay policies to match a specific client's leave and shift rules.

## Problem addressed

The timesheet derivation service (`STORY-0088` (was `PT-A1-42`)) needed a way for each workspace to view, understand, and customise its attendance codes and policies (e.g. whether a code counts as paid, whether it counts toward OT threshold) — without this, derivation logic would be forced to hardcode one client's rules for all clients.

## Delivered behaviour

Workspace-scoped GET/POST/PATCH routes let an operator view seeded platform attendance codes, see each code's policy values, update a policy (subject to a `category`-is-immutable guard — the code's category cannot be changed after creation), add a workspace-specific code, and disable a code. A validation guard rejects an inconsistent policy combination (`counts_as_paid = FALSE AND counts_towards_ot_threshold = TRUE` → HTTP 400). Access is scoped to the requesting workspace via JWT ownership check. Codes whose configuration has drifted from the seeded template are flagged as orphaned in the UI, and a warning surfaces when a code's hours are not configured.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O item O6 (Sprint 16); full requirement and acceptance criteria (TM-7-AC-1 through TM-7-AC-11) in `docs/stories/sprint-16-timesheet-layer.md`, "TM-7: Attendance code and policy workspace configuration."

## Implementation evidence

- `backend/api/routes/workspace.py` — GET/POST attendance codes, PATCH code, PATCH policy routes, with category-immutability guard and workspace-ownership check.
- Commit `1dd340a` (2026-05-13) — same commit as `STORY-0088` (was `PT-A1-42`); TM-1 through TM-7 were delivered together in Sprint 16.

## Test / review evidence

- `docs/test-reports/2026-05-13-sprint-16.md` — TM-7 checks: "routes: GET/POST attendance codes, PATCH code, PATCH policy wired in `workspace.py` | PASS (code-level)"; "TM-7-AC-4 | `category` immutability guard present | PASS (code-level)"; "TM-7-AC-9 | `counts_as_paid = FALSE AND counts_towards_ot_threshold = TRUE` → HTTP 400 | PASS (code-level)"; "TM-7-AC-10 | JWT workspace ownership check | PASS (code-level)"; "TM-7-AC-11 | v1 template seed values in migration match spec table | PASS." Report's overall verdict: "PASS (code-level); runtime deferred to staging" — all TM-7 checks in the cited table are marked code-level (static inspection), with no live-DB/runtime exercise recorded for this item specifically.

## Decision references

- Sprint 15 design sprint arch-council decisions AC-1–AC-10, C1, C2 (shared with `STORY-0088` (was `PT-A1-42`)).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Depends on `STORY-0088` (was `PT-A1-42`) (workspace timesheet enablement and the first-enable attendance-template seeding) — TM-7's CRUD operates on the rows TM-1 seeds.

## Delivery sprint(s)

Sprint 16, delivered 2026-05-13 (commit `1dd340a`).

## Delivery history

- 2026-05-13 — Sprint 16 — attendance code + policy CRUD, category-immutability guard, and policy-consistency validation delivered (commit `1dd340a`); code-level checks PASS per `docs/test-reports/2026-05-13-sprint-16.md`; runtime/live-DB verification explicitly deferred to staging in the same report.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

As with `STORY-0088` (was `PT-A1-42`), every TM-7 check in the cited test report is explicitly labelled "code-level" — the report's own verdict states runtime verification was deferred to staging, not executed. This is a genuine, stated limitation carried forward rather than upgraded.
