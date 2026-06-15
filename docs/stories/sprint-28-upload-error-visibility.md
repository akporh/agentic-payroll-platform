# Sprint 28 — Upload Error Visibility + Duplicate Skip

**Sprint date:** 2026-06-13
**Sprint goal:** Make upload failures visible, portable, and non-blocking across all upload flows. Make re-uploads idempotent for period inputs.

---

## Background

Two problems surfaced during UAT of the Sprint 27 native upload work:

1. When a bulk upload partially fails, the error information disappears when the user closes the panel or navigates away. The user has to re-upload the spreadsheet just to find out what went wrong.
2. Period inputs bulk upload was treating duplicate rows (same employee + code + period) as hard errors, forcing the user to manually delete existing inputs before re-uploading. The employee upload already treats duplicates as skips — period inputs should behave the same way.

---

## Story 1 — UPLOAD-ERR-1: Consistent upload error visibility

**Priority:** P1 · Operator Experience

```
As Sandy (payroll operator),
When a bulk upload partially or fully fails,
I want to see exactly which rows failed and why,
And be able to save that information before I close the panel,
So that I can fix my spreadsheet and re-upload without losing my place.
```

### What changed

**Visual pattern — three-layer error state (all upload flows)**

Every upload error state now renders three distinct visual layers:

| Layer | Purpose | Visual |
|---|---|---|
| 1 — Status | What happened | `AlertBanner` (warning/success) with counts: "12 added, 3 failed" |
| 2 — Download prompt | Why to act now | Amber box: "Download before you close" + outlined amber download button with row count |
| 3 — Detail | Reference for each failure | Scrollable red-tinted table: Reference column + Reason column |

The amber box copy is explicitly non-blocking:
> "X rows weren't uploaded. Save a copy now — fix them in your spreadsheet and re-upload whenever you're ready."

This makes clear the user is free to continue; the download is to preserve context, not a gate.

**Flows covered**

| Flow | File | Before | After |
|---|---|---|---|
| Period inputs — native upload | `NativeUploadFlow.tsx` (done state) | Generic warning banner, no per-row detail | Three-layer pattern; `submitNativeInputRows` now returns `details[]` |
| Period inputs — template upload | `PayrollInputsBulkUpload.tsx` (result section) | Truncated AlertBanner (first 3 errors + "+N more") | Three-layer pattern with row number + error table |
| Employees — native upload | `NativeUploadFlow.tsx` (done state) | Per-employee error table already existed | Download button added; banner text updated to "already exist — skipped" |
| Employees — template upload | `EmployeeUpload.tsx` | AlertBanner truncated to 5 errors | Full scrollable list (all errors) + amber download block |

**Download format**

CSV file with columns: `Reference, Name, Error` (native flows) or `Row, Error` (template flows). Opens directly in Excel. File is generated client-side — nothing sent to the server.

### Acceptance Criteria

- [ ] Upload with 0 failures: success AlertBanner only; no amber block; "Done" button
- [ ] Upload with partial failures: warning AlertBanner + amber "Download before you close" block + error table
- [ ] Upload with all failures: error AlertBanner + amber block + error table
- [ ] "Download error report (N rows/errors)" button downloads a CSV containing all failures
- [ ] CSV opens in Excel with correct columns and all rows visible
- [ ] Closing the panel after downloading: user has the CSV; information is not lost
- [ ] Error table is scrollable; all rows visible (no truncation or "+N more" cap)
- [ ] Skip count (if any) surfaces as info AlertBanner: "X already exist — skipped"
- [ ] Amber block copy does not imply the user is blocked from continuing

### Files changed

- `frontend/src/components/shared/NativeUploadFlow.tsx` — `SubmitResult` interface adds `skippedCount?`; done state redesigned with three-layer pattern; `downloadErrorsCsv` utility added
- `frontend/src/pages/PayrollInputsBulkUpload.tsx` — `submitNativeInputRows` returns `details[]` + `skippedCount`; template result section redesigned
- `frontend/src/components/employees/EmployeeUpload.tsx` — parse error display redesigned

---

## Story 2 — UPLOAD-SKIP-1: Skip duplicate period inputs (idempotent re-upload)

**Priority:** P1 · Operator Experience

```
As Sandy (payroll operator),
When I re-upload a period inputs file that contains rows already in the system,
I want those rows to be silently skipped (not rejected as errors),
So that re-uploading is safe and I don't have to manually delete existing inputs first.
```

### What changed

**Backend `POST /{workspace_id}/payroll/inputs/bulk`**

`IntegrityError` (duplicate `employee_id + input_code + reference_date`) previously appended a verbose error to the response. Now it increments a `skipped` counter.

| Before | After |
|---|---|
| `errors: [{ row: N, detail: "Duplicate: input_code '...' already exists. Delete the existing input..." }]` | `skipped: N` (no error entry) |
| Re-upload fails with N errors | Re-upload is idempotent — created + skipped, 0 errors |

Response shape updated: `{ created: int, skipped: int, errors: [...] }` — `skipped` was absent before.

This matches the existing employee bulk behaviour: `POST /employees` returns 409 for existing `employee_number`, which the frontend maps to `status: 'skipped'` — not an error.

**Frontend**

Both the native path (`submitNativeInputRows`) and the template path (`handleSubmit`) now read `res.skipped` from the API response and surface it as:
- Message string: "12 added, 3 already exist — skipped"
- Info AlertBanner in the done state (native path via `NativeUploadFlow`)

### Acceptance Criteria

- [ ] Upload file with 10 rows where 3 already exist: `created=7, skipped=3, errors=[]`
- [ ] Native upload done state: success/info banner — "7 added, 3 already exist — skipped"; no amber download block
- [ ] Template upload result: same message; "View in Inbox →" action present
- [ ] Upload where all rows already exist: `created=0, skipped=N, errors=[]`; success/info banner; no error table
- [ ] Duplicate detection is per `(employee_id, input_code, reference_date)` — same employee + different period is NOT a duplicate

### Files changed

- `backend/api/routes/payroll_input.py` — `IntegrityError` handler: `errors.append(...)` → `skipped += 1`; return value adds `skipped` key
- `frontend/src/pages/PayrollInputsBulkUpload.tsx` — result type, `handleSubmit`, `submitNativeInputRows` all updated

---

## Architecture Notes

**`SubmitResult` interface** (`NativeUploadFlow.tsx`):
```ts
interface SubmitResult {
  success: boolean;
  message: string;
  details?: SubmitResultDetail[];  // per-row failed/skipped/created entries
  skippedCount?: number;           // for flows where API returns bulk skip count only
}
```

`skippedCount` is additive with `details`-derived skipped count — both paths are summed in the done state. This handles the period inputs case (bulk skip count from API) and the employee case (per-row skipped details from parallel calls) without divergence.

**`downloadErrorsCsv` utility** is a module-level function in `NativeUploadFlow.tsx`:
```ts
function downloadErrorsCsv(filename, headers, rows): void
```
Creates a Blob URL, triggers download, revokes immediately. No server round-trip. Not extracted to a shared utility — three similar usages across three files is not enough to justify the abstraction.
