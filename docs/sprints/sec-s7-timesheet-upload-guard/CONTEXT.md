# Sprint — `sec-s7-timesheet-upload-guard`

**Status:** scope approved 2026-07-13 (Validation-Pilot Scope Approval, decisions D-VP-01 through D-VP-06).
**Role:** Follow-up ICM sprint-workflow validation pilot, per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md`, Candidate A. A real, shippable security fix — not a synthetic workflow exercise — chosen specifically because it naturally activates a skipped `architecture` stage and genuinely parallel `verification`+`security` stages, closing the gap the `aud-q1-trace-source` retro found.

---

## Goal

Enforce a 10 MB server-side limit on the timesheet-upload endpoint, with a frontend advisory check and toast for early user feedback — the backend guard is authoritative; the frontend copy is UX-only.

## Source item

`docs/ROADMAP.md`, Track S — Security, item **S7**:

> Add file size cap (10 MB) on timesheet upload — `openpyxl.load_workbook` loads entire file into memory; no current guard — `backend/api/routes/payroll.py:1492` — ref SEC-S6 (report) — raised Sprint 16 — status ⬜

Confirmed still open by reading the live file (2026-07-13): `upload_timesheet` (now `backend/api/routes/payroll.py:1679-1692`) read the full request body via `await file.read()` with no byte limit before calling `timesheet_derivation_service.upload_timesheet`, which parses it with `openpyxl.load_workbook`.

## Approved product scope (D-VP-01, this session)

- Enforce a 10 MB server-side limit on the timesheet-upload endpoint.
- Add a frontend error toast for oversized uploads.
- The backend constant is authoritative; any frontend size check or constant is advisory UX only, and must never weaken backend enforcement.

## In-scope stories

- SEC-S7 only. No other Track S item bundled into this sprint.

## Acceptance criteria

1. Uploading a timesheet Excel file larger than 10 MB returns HTTP 413 with a generic, non-leaking message, before the workbook is parsed.
2. Uploading a file at or under 10 MB behaves exactly as today — no change to the successful-path response or the derivation service's inputs.
3. The frontend shows a specific toast for an oversized file — both pre-flight (client-side size check, before the network call) and as a fallback if the backend rejects a file the client-side check let through.
4. The frontend's size constant is advisory only: removing or misconfiguring it must not change what the backend accepts or rejects — verified by the backend test suite being independent of any frontend code path.

## Out of scope

- S8 (pin `python-multipart`) — confirmed already resolved this session (`requirements.txt:15` already reads `python-multipart==0.0.28`); ROADMAP is stale on this item, to be corrected at next `/roadmap` sync.
- Any other Track S/Track Q item.
- Making the 10 MB limit workspace-configurable (considered and explicitly deferred — see the `architecture` skip decision, `decisions.md`).
- A shared frontend/backend config mechanism for the size constant (same deferral).

## Why this item fits the validation-pilot constraints

| Constraint | How this item satisfies it |
|---|---|
| Genuinely activates `architecture` as `skipped`, not `not-applicable` | A real (if minor) cross-layer question exists — where should the max-size value live — deliberately deferred by human decision, not structurally absent. See `decisions.md`. |
| Genuinely activates `verification` + `security` in parallel | Touches both `backend/api/routes/payroll.py` (route) and `frontend/src/pages/TimesheetUpload.tsx` (frontend) — the only registry-declared parallel-compatible pair. |
| Small, real, low-risk | Additive guard + advisory client check; no existing successful-path behavior changed. |
| Does not require skipping a mandatory safety/correctness check | The stage being skipped (`architecture`) has no formal human gate and is explicitly the registry's least safety-critical stage — `security` and `test` are never candidates for skip here. |
