# `STORY-0146` — SEC-S7: 10 MB server-side timesheet upload size guard

**Origin code(s):** `PT-A4-32` · `PT-S-07` · `SEC-S7`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-2` — File upload security controls
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll bureau operator uploading a timesheet Excel file; and, defensively, the platform itself against an oversized or malicious upload.

## Problem addressed

`upload_timesheet` (`backend/api/routes/payroll.py`) read the entire uploaded file into memory and parsed it with `openpyxl.load_workbook` with no byte-size limit before parsing — an unbounded-size upload could exhaust server memory before any validation occurred (`docs/ROADMAP.md` Track S, item S7, ref SEC-S6 report, raised Sprint 16).

## Delivered behaviour

A module-level `MAX_TIMESHEET_UPLOAD_BYTES = 10 * 1024 * 1024` constant in `backend/api/routes/payroll.py`; the upload handler performs a bounded read (`file.read(MAX_TIMESHEET_UPLOAD_BYTES + 1)`) and raises `HTTPException(413, ...)` with a generic, non-leaking message before the derivation service (and therefore `openpyxl.load_workbook`) ever runs. `frontend/src/pages/TimesheetUpload.tsx` carries a matching advisory-only constant, a pre-flight client-side size check with a toast, and a fallback toast if the backend rejects a file the client-side check let through. The backend guard is authoritative; the frontend check is UX-only and cannot weaken backend enforcement — proven by the backend test suite exercising the guard with zero frontend code in the call path.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S — Security, item S7 (ref SEC-S6 report, raised Sprint 16, status was ⬜ until this ICM sprint closed it 2026-07-13).

## Implementation evidence

- `backend/api/routes/payroll.py` — `MAX_TIMESHEET_UPLOAD_BYTES` constant, bounded read, 413 guard ahead of `timesheet_derivation_service.upload_timesheet`.
- `frontend/src/pages/TimesheetUpload.tsx` — matching advisory constant, pre-flight `file.size` check + toast in `handleUpload`, fallback toast in the `catch` block.
- `tests/test_timesheet_upload_size_guard.py` — `test_oversized_upload_rejected_with_413`, `test_within_limit_upload_reaches_derivation_service`.
- Commits: `be337aa` ("SEC-S7: enforce 10 MB server-side limit on timesheet upload" — product code + tests), `58ec4f8` (sprint workspace creation, precedes it).
- Full detail: `docs/sprints/sec-s7-timesheet-upload-guard/evidence/implementation/size_guard.md`.

## Test / review evidence

- `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` — security review verdict PASS; SEC-S7 closed correctly per the security skill's File Upload Security checklist item #7; one pre-existing, unrelated Observation flagged separately (no content-type/malformed-file validation) and explicitly not bundled into this story's scope.
- `docs/sprints/sec-s7-timesheet-upload-guard/evidence/verification/live_run.md` — LIVE HTTP checks against a running backend: an 11 MB upload → 413 with the expected message; an in-limit file passes the size guard and reaches the derivation service.
- `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md` — all 4 acceptance criteria verified (3 LIVE, 1 CODE REVIEW — no browser automation available for the frontend toast click-through, labelled honestly rather than rounded up); full suite 308 passed (306 pre-existing + 2 new), 1 pre-existing skip, 0 failed; `cd frontend && npx tsc --noEmit` clean.
- `docs/sprints/sec-s7-timesheet-upload-guard/retrospective.md` — sprint-close retro, product-fix verdict PASS, 0 regressions.

## Decision references

- `DEC-sec-s7-timesheet-upload-guard-01` (`docs/sprints/sec-s7-timesheet-upload-guard/decisions.md`) — architecture stage `skipped` (not `not-applicable`): where the max-upload-size value should live is a genuine minor cross-layer question, deliberately deferred; backend constant ruled authoritative, frontend copy advisory-only, reversible if a third consumer of the value appears.
- `DEC-sec-s7-timesheet-upload-guard-02` — arch-council `not-applicable` (no data-contract/status/enum/migration/cross-workspace/shared-type surface touched).
- `DEC-sec-s7-timesheet-upload-guard-03` — audit `not-applicable` (no calculation path touched).
- `D-015` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4A pilot.

## Dependencies

None. Additive byte-size guard and advisory client-side check; no migration, no other story's completion is a precondition. (Not a dependency of this story, but a related open item: the security review's separately-flagged content-type/malformed-file validation Observation is explicitly out of scope here and is not tracked as a dependency.)

## Delivery sprint(s)

Raised Sprint 16 (as `S7`/`SEC-S7`/ref `SEC-S6`). Delivered in ICM sprint workspace `sec-s7-timesheet-upload-guard` (2026-07-13).

## Delivery history

- 2026-07-13 — ICM sprint `sec-s7-timesheet-upload-guard` — 10 MB server-side guard + frontend advisory check delivered (commits `58ec4f8`, `be337aa`); security-reviewed and tested complete same day; sprint retro closed 2026-07-13.
- 2026-07-15 — Phase 4A pilot (`docs/programmes/product-traceability/`) — story migrated into `docs/product/` as one of the two authorised pilot items (D-015).

## Unresolved questions

The discovery document (`docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`) also records this same delivered item under provisional ID `STORY-0146` (was `PT-S-07`) (the Track S cross-cutting security-register table entry, line 261) alongside `STORY-0146` (was `PT-A4-32`) (line 205, used here as the stable ID). As with `STORY-0145` (was `PT-A4-31`)/`STORY-0145` (was `PT-Q-01`), deciding whether `STORY-0146` (was `PT-S-07`) should be retired as a duplicate or kept as a distinct historical marker is outside this pilot's authorised scope. Separately, the security review's own Observation (no content-type/malformed-file validation on this endpoint, confirmed live via an unhandled `zipfile.BadZipFile` crash) was explicitly recommended as a new Track S backlog item, not bundled into this story — it is not yet represented anywhere in `docs/product/` and would need its own story record if and when it is scheduled.
