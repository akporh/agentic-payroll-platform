# `STORY-0088` — Workspace timesheet configuration + attendance code seeding (TM-1, Sprint 16)

**Origin code(s):** `PT-A1-42` · `TM-1`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-5` — Attendance & timesheet configuration
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Platform admin configuring whether a workspace uses timesheet-based attendance capture or the existing period input file.

## Problem addressed

The platform had no way to distinguish timesheet-based clients from salary-only/input-file clients, and no mechanism to seed a workspace's attendance-code configuration before timesheet processing could begin.

## Delivered behaviour

A `workspace_payroll_config.timesheet_enabled` flag (default `FALSE`) gates whether an operator sees a timesheet upload flow or the existing input-file path; a non-timesheet workspace's upload attempt is rejected with HTTP 400. Toggling `timesheet_enabled` does not affect any in-flight run or existing `payroll_input` rows. When `timesheet_enabled` is TRUE, `payroll_readiness_service` blocks `link_inputs_to_run` if any employee's `timesheet_entry.derivation_status ≠ 'APPROVED'`, listing the non-approved employees by name (this is the C2 readiness gate). The first time a workspace is enabled, platform attendance-code templates (v1) are seeded into `attendance_code_config`/`attendance_policy_config` via `ON CONFLICT DO NOTHING` (idempotent, does not overwrite existing rows), and `workspace.attendance_template_version` is set to the current platform template version; `WorkspaceConfig.tsx` shows a non-blocking warning when a workspace's template version is behind the current platform version.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track O item O6 (Sprint 16 implementation of the timesheet/attendance layer, NEW-GAP1); full requirement and acceptance criteria (TM-1-AC-1 through TM-1-AC-7) in `docs/stories/sprint-16-timesheet-layer.md`, "TM-1: Workspace timesheet configuration."

## Implementation evidence

- `backend/infra/repositories/workspace_config_repo.py:21` — `"timesheet_enabled": False` in `_DEFAULTS`.
- `backend/api/routes/payroll.py:1485-1488` — `_require_timesheet_enabled()` returning HTTP 400 when disabled.
- `backend/domain/payroll/payroll_readiness_service.py:112-126` — the C2 timesheet-completeness gate.
- Attendance-code template seeding wired in `backend/api/routes/workspace.py`'s PUT payroll-config handler (`ON CONFLICT DO NOTHING`), and the template-version warning in `frontend/src/pages/WorkspaceConfig.tsx`.
- Commit `1dd340a` ("feat: sprint 16 — timesheet derivation layer (TM-1 through TM-7, C1, C2)", 2026-05-13).

## Test / review evidence

- `docs/test-reports/2026-05-13-sprint-16.md` — TM-1 checks: AC-2 (default FALSE) PASS, AC-3 (400 when disabled) PASS, AC-5 (C2 readiness gate) PASS, AC-6 (template seeding, `ON CONFLICT DO NOTHING`) PASS (code-level), AC-7 (template version warning) PASS (code-level). Report's overall verdict: "PASS (code-level); runtime deferred to staging" — 22/22 code-level checks passed; live-DB/runtime verification was explicitly deferred, not executed, in this report.

## Decision references

- Sprint 15 design sprint arch-council decisions AC-1–AC-10, C1, C2 (`docs/ROADMAP.md` Track O item O6: "Sprint 15 design sprint (arch-council locked AC-1–AC-10, C1, C2)").
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None upstream in this batch. It is a documented precondition for `STORY-0089` (was `PT-A1-41`) (attendance code + policy CRUD, which reads/writes the `attendance_code_config`/`attendance_policy_config` rows this story seeds).

## Delivery sprint(s)

Sprint 16 (Track O item O6 implementation, design locked in Sprint 15), delivered 2026-05-13 (commit `1dd340a`).

## Delivery history

- 2026-05-13 — Sprint 16 — workspace timesheet-enable flag, upload gate, C2 readiness gate, and first-enable attendance-template seeding delivered (commit `1dd340a`); 22/22 code-level checks PASS per `docs/test-reports/2026-05-13-sprint-16.md`; runtime/live-DB verification explicitly deferred to staging in the same report.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The Sprint 16 test report's own verdict is explicit that runtime/live-DB verification was deferred, not executed — all 22 checks are "code-level" (static inspection), not live API/DB exercises. This is a genuine, stated limitation of the cited evidence, carried forward rather than upgraded.
