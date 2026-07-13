# Verification Evidence — `sec-s7-timesheet-upload-guard`

**Stage:** verification
**Date:** 2026-07-13

## Environment

- Backend: `uvicorn backend.api.main:app --port 8000`, started fresh after this sprint's code was committed (`be337aa`). Health check: `GET /api/v1/health` → 200.
- Frontend: `npm run dev -- --port 5173` (Vite). Compiled and served cleanly (`GET /` → 200), confirming no runtime/compile error in the `TimesheetUpload.tsx` changes.
- Real workspace created directly via SQL for this check (`workspace_payroll_config.timesheet_enabled = true`), used only for the duration of this test, then deleted.

## Checks

`[PASS]` **Oversized upload rejected with 413** — `LIVE`
Given: an 11 MB binary file, a workspace with `timesheet_enabled=true`.
When: `POST /api/v1/workspaces/{id}/timesheet/upload` with that file.
Then: HTTP 413, `{"detail": "File too large — max 10 MB per upload."}`.
Got: exactly that — confirmed via `curl`, HTTP 413.

`[PASS]` **In-limit file passes the size guard** — `LIVE`
Given: a small (~210 byte) file, same workspace.
When: same endpoint.
Then: the size guard must not block it — request should proceed to the derivation service.
Got: HTTP 500, traceback confirms the request reached `timesheet_derivation_service.upload_timesheet` → `openpyxl.load_workbook` → `zipfile.BadZipFile: File is not a zip file`. This proves the size guard correctly let an in-limit file through; the 500 itself is a **pre-existing, unrelated gap** (no content-type/malformed-file validation in the derivation service) — not introduced by this sprint, out of this sprint's scope (SEC-S7 is a size cap, not a content-type guard), and flagged as an **Observation** in the security review below rather than silently fixed or silently ignored.

`[CODE REVIEW]` **Frontend advisory pre-check + toast**
Given: `handleUpload` in `TimesheetUpload.tsx`.
When: a file's `.size` exceeds `MAX_TIMESHEET_UPLOAD_BYTES` (10 MB).
Then: `toast.show('error', ...)` fires and the function returns before any network call.
Got: confirmed by reading the code (`frontend/src/pages/TimesheetUpload.tsx:69-75`) and by `tsc --noEmit` passing clean. **Not LIVE** — this environment has no browser-automation tooling to click a file input and observe a rendered toast; the click-through itself was not exercised. Labeled `CODE REVIEW`, not `PASS` via LIVE, per this project's own LIVE/STATIC/CODE-REVIEW taxonomy (a check not executed this session is never `PASS`-via-LIVE).

`[PASS]` **Frontend constant is advisory only, backend independent** — `LIVE` (via the backend HTTP checks above)
The two `LIVE` checks above call the backend directly with `curl`, with zero frontend code in the call path — proving the backend enforcement holds regardless of anything in the frontend.

## Evidence artefacts

- `/tmp/resp_oversized.json` (HTTP 413 body) — transient, not committed (contains no sensitive data, but per repo convention scratch files aren't checked in).
- Server log excerpt (traceback for the pre-existing zip-parsing gap) captured above.

## Summary

2 LIVE checks, 1 CODE REVIEW check (frontend click-through — no browser automation available this session), 1 LIVE check reusing the backend evidence. 0 BLOCKED. The authoritative half of this sprint's scope (backend enforcement) is fully LIVE-verified; the advisory half (frontend UX) is confirmed by code + compile, not by an actual rendered toast.
