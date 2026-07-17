# Implementation Evidence — 10 MB timesheet-upload guard (SEC-S7)

**Stage:** implementation
**Date:** 2026-07-13
**Commits:** `be337aa` (product code + tests), `58ec4f8` (workspace creation, precedes this)

## Code change

- `backend/api/routes/payroll.py`: `MAX_TIMESHEET_UPLOAD_BYTES = 10 * 1024 * 1024` module constant; `await file.read(MAX_TIMESHEET_UPLOAD_BYTES + 1)` bounded read, `HTTPException(413, ...)` if the result exceeds the cap — before `timesheet_derivation_service.upload_timesheet` (and therefore `openpyxl.load_workbook`) ever runs.
- `frontend/src/pages/TimesheetUpload.tsx`: matching `MAX_TIMESHEET_UPLOAD_BYTES` constant (advisory only, documented as such in both locations' comments), a pre-flight `file.size` check in `handleUpload` that shows a toast and returns before the network call, and a fallback toast in the `catch` block keyed on the extracted error message containing "too large" — covers the case where the backend rejects a file the client-side check let through.

## Tests added

`tests/test_timesheet_upload_size_guard.py` (monkeypatched workspace-config + derivation service, no DB fixture):

- `test_oversized_upload_rejected_with_413` — a file one byte over the cap returns 413 with a "too large" message, and asserts the derivation service is never called.
- `test_within_limit_upload_reaches_derivation_service` — a 1 KB file reaches the derivation service unchanged (same byte length received).

## Verification run (LIVE)

```
$ python -m pytest tests/test_timesheet_upload_size_guard.py -v
2 passed in 0.79s

$ python -m pytest -q
308 passed, 1 skipped in 7.21s
```

Zero regressions — 306 pre-existing + 2 new, 0 failed, the 1 skip is the pre-existing intentional Phase-2 reconciliation skip.

```
$ cd frontend && npx tsc --noEmit
(no output — clean)
```

## Acceptance criteria — self-check

| AC (from CONTEXT.md) | Result |
|---|---|
| 1. Oversized upload → 413, generic message, before parsing | PASS — `test_oversized_upload_rejected_with_413` |
| 2. In-limit upload unchanged | PASS — `test_within_limit_upload_reaches_derivation_service` |
| 3. Frontend toast for oversized (pre-flight + fallback) | PASS — code review; live-run confirmation is `verification`'s job, not repeated here |
| 4. Frontend constant is advisory only, backend independent | PASS — the backend test suite above exercises the guard with zero frontend code in the call path |
