# Security Review — `sec-s7-timesheet-upload-guard` — 2026-07-13

**Reviewer:** Claude Code (`/security` skill)
**Scope:** commit `be337aa` — `backend/api/routes/payroll.py`, `frontend/src/pages/TimesheetUpload.tsx`

---

## Findings

### Closed this sprint

**SEC-S7 — no file size cap on timesheet upload.** Closed. `MAX_TIMESHEET_UPLOAD_BYTES` (10 MB) enforced via a bounded `await file.read(MAX_TIMESHEET_UPLOAD_BYTES + 1)` before `openpyxl.load_workbook` ever runs — matches this skill's own File Upload Security checklist item #7 exactly ("an explicit byte limit before the file is read into memory"). Confirmed live: an 11 MB file returns 413 before reaching the derivation service.

### Checked, no issue

- **`str(e)` / exception-string leakage:** none. The 413 response is a hardcoded generic string, not `str(e)`.
- **Float for money:** N/A — no monetary value in this diff.
- **Secrets:** none introduced.
- **New dependencies:** none.
- **Frontend XSS / injection:** the advisory check is a pure numeric comparison (`file.size`); the toast message is a static string, not user-controlled input reflected into markup.

### Observation (not a new finding of this sprint — pre-existing, flagged for the backlog)

**No content-type / malformed-file validation on timesheet upload.** Confirmed live this session: a small, non-Excel file passes the (now-fixed) size guard and reaches `timesheet_derivation_service.upload_timesheet`, which raises an unhandled `zipfile.BadZipFile`, surfaced to the client as a raw HTTP 500 with no message. This is the second half of this skill's own File Upload Security checklist item #7 ("content-type validation... at minimum, check the extension or catch parser exceptions and return a 400") — pre-existing, not introduced by this diff, and explicitly out of SEC-S7's scope (SEC-S7 is a size cap; this is a content-type/parse-error guard). Recommend logging this as a new Track S item at the next `/roadmap` sync — a raw 500 with no message is itself a minor `str(e)`-adjacent smell (unhandled-exception detail could leak in some configurations, even though nothing leaked in this local run).

## Compensating controls for the `architecture` skip (D-VP-02)

Per this sprint's `decisions.md` (`DEC-sec-s7-timesheet-upload-guard-01`), the `architecture` stage was skipped on the question of where the max-size constant should live, with this security review and the backend test suite named as compensating controls. Confirmed here: the backend guard is fully independent of the frontend constant (proven by the LIVE `curl` checks in `evidence/verification/live_run.md`, which never touch frontend code), so a future divergence between the two constants can only make the frontend's pre-check stricter or looser than the backend — it cannot weaken backend enforcement.

## Verdict

PASS. SEC-S7 closed correctly, no new risk introduced, one pre-existing adjacent gap flagged as a follow-up backlog item (not a blocker for this sprint).
