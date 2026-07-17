# Sprint Test Report — `sec-s7-timesheet-upload-guard` — 2026-07-13

## Summary
| Metric | Value |
|---|---|
| Sprint | `sec-s7-timesheet-upload-guard` (ICM follow-up validation pilot, Candidate A) |
| Date | 2026-07-13 |
| Test suite | 308 passed, 1 skipped (pre-existing, unrelated), 0 failed |
| API verifications | 2 LIVE HTTP checks (413 boundary, in-limit pass-through) |
| Overall verdict | PASS |

## Environment

- Backend started fresh after this sprint's code (`be337aa`) was committed. `GET /api/v1/health` → 200.
- Frontend `npx tsc --noEmit` clean; `npm run dev` served the page with no compile error.
- No migration in this sprint — nothing to check via `alembic`.

## Sprint Items Verified

| AC (from `CONTEXT.md`) | Check | Result |
|---|---|---|
| 1. Oversized upload → 413, generic message, before parsing | Live `curl`: 11 MB file → HTTP 413, `"File too large — max 10 MB per upload."` | **PASS** `LIVE` |
| 2. In-limit upload unchanged | `test_within_limit_upload_reaches_derivation_service` (unit) + live `curl` confirming a small file reaches the derivation service (crashes downstream on unrelated pre-existing gap, proving pass-through) | **PASS** `LIVE` |
| 3. Frontend toast for oversized (pre-flight + fallback) | Code review of `handleUpload`'s pre-check and `catch` block; `tsc --noEmit` clean | **PASS** `CODE REVIEW` — no browser automation available this session for an actual click-through; not claimed as LIVE |
| 4. Frontend constant advisory-only, backend independent | Backend test suite (`tests/test_timesheet_upload_size_guard.py`) and both live `curl` checks exercise the guard with zero frontend code in the path | **PASS** `LIVE` |

## Regression Suite

```
$ python -m pytest
308 passed, 1 skipped, 48 warnings in 6.76s
```

306 pre-existing + 2 new (`test_timesheet_upload_size_guard.py`). Zero failures, zero new skips. The 1 skip is the pre-existing, intentional Phase-2 reconciliation skip.

## Data Integrity Spot-Check

Not applicable — no migration, no DB schema change, no monetary/calculation data touched.

## Known Pre-Existing Issues

- **No content-type/malformed-file validation on the timesheet upload endpoint** — confirmed live during this sprint's own verification pass (a small non-Excel file crashes with an unhandled `zipfile.BadZipFile`, surfaced as a raw 500). Pre-dates this sprint; not a regression. Flagged in `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` as a recommended new Track S backlog item, out of this sprint's scope.

## Deferred

- An actual browser click-through of the frontend toast (file selection → toast render) — this environment has no browser-automation tooling. The equivalent backend behavior (the authoritative half) is fully LIVE-verified; the frontend piece is verified by code + successful compile only.

## Sign-off
Verified by: Claude Code (automated, `/tester` skill)
