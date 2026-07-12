# Stage 06 — UI/API/Backend Wiring

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Build an evidence-backed wiring map from user-visible UI controls through
frontend state, API requests, backend routes/services, persistence, runtime
consumers, and returned UI state. Determine, per feature, whether it is
fully wired, frontend-only, API-only, backend-only, persisted-but-not-
surfaced, surfaced-but-not-persisted, saved-but-ignored, returned-but-not-
rendered, rendered-from-stale-fields, or unreachable.

## Confirmed handoff state (verified before starting)

- Stages 01–05 are complete.
- The immediate remediation sprint for `04-001` + `05-001` is complete and
  approved (`docs/audit-program/remediation/04-001-05-001/`). Both findings
  are remediated and are **not** reopened in this stage absent new
  regression evidence — Stage 06 verifies the remediation's UI *visibility*
  only (required investigation #4), not the backend fix itself.
- `04-002` remains open, passed to Stages 07/10.
- `05-004` remains deferred to Stage 13.
- `CLAUDE.md` is the governing instruction source; `docs/wrapper-command/`
  remains reference-only, non-authoritative.
- Read-only stage — no frontend, backend, migration, test, or script edits.

## Inputs

- Stage 03 findings — full configuration catalogue; specifically flags
  `pay_cycle.definition_json` as untraced to a specific UI control, and the
  Upload/Enroll separation and D-ARCH-1 edit-lock as UI-relevant invariants.
- Stage 04/05 findings — retry-strategy is a per-run column
  (`payroll_run.retry_strategy`, PER_EMPLOYEE only per `CLAUDE.md`); no UI
  surface for it was confirmed in prior stages.
- Remediation record — `05-001`'s exact API contract change: `GET
  /{workspace_id}/payroll/runs/{run_id}` now returns `error_message`;
  `PayrollRunStatus` gained `FAILED`. This stage verifies both reached the
  frontend.
- Frontend inventory (confirmed present, from direct listing):
  `frontend/src/pages/` — 15 pages; `frontend/src/api/` — 6 client modules;
  `frontend/src/types/` — 3 type-definition files.

## Process

Per the sprint's 10-point required investigation: build the feature
catalogue; trace configurable fields bidirectionally; revisit Stage 03's
`pay_cycle.definition_json`/onboarding/component-override/edit-lock/retry-
strategy handoffs; verify `05-001`'s frontend visibility explicitly;
identify backend-only capabilities; identify frontend-only/dead UI; check
API contract alignment (frontend types vs. backend Pydantic schemas);
record tenant/permission observations for Stage 09 without expanding into
a full security audit; trace representative error/status propagation;
controlled non-production verification only where it adds evidence beyond
static code tracing.

## Outputs

Per the sprint's 13-item list: feature catalogue, field-level matrix,
contract-mismatch register, backend-only register, frontend-only/dead-UI
register, navigation/reachability map, error/status propagation matrix,
`FAILED` remediation visibility verification, tenant/permission
observations, configuration round-trip findings, `findings.md`,
`evidence/`, handoff notes for Stages 07, 08, 09, 11, 12, 13.

## Prohibited actions

- No edits to frontend, backend, migrations, tests, or scripts.
- No implementation of missing wiring.
- Do not start Stage 07.
- Do not reopen `04-001`/`05-001` without new regression evidence.
- Do not expand into a full security audit — record Stage 09 handoffs only.

## Completion criteria

- Feature catalogue covers every domain in the sprint's minimum list, or
  explicitly marks a domain not-applicable with reason.
- `05-001` visibility explicitly verified against all six checks in
  required investigation #4.
- `pay_cycle.definition_json`, onboarding/edit alignment, component
  override UI mapping, salary-definition edit-lock UI behaviour, and
  retry-strategy visibility are each explicitly resolved with evidence.
- Backend-only and frontend-only/dead-UI registers populated with
  evidence-backed classification per entry.
- API contract alignment checked between frontend types and backend
  schemas for at least the payroll-run and retry surfaces.
- Tenant/permission observations recorded for Stage 09 handoff without
  scope creep into a full security audit.
- Every finding uses one of the five valid status values.
- Handoff notes exist for Stages 07, 08, 09, 11, 12, 13.
- `audit-state.md` left `in-progress` — this stage does not self-close.
