# Gate 3 — Adaeze's Payroll Operator Journey
## UX/UI Upgrade Stories (Retrospective)

**Status:** ✅ Shipped (April 2026) — 6 amendments pending implementation  
**Skills active:** `/ui-designer`, `/ux-designer`, `/pm`  
**Persona:** Adaeze — payroll operator, desktop, monthly rhythm, clearing a to-do list before month-end  
**Design decisions honoured:** DD-2, DD-3, DD-4, DD-5, DD-6, DD-7, DD-8, DD-12, DD-14, DD-15, DD-17, DD-18

---

## G3-UI-1 — Payroll Inputs Inbox

**Priority:** P2 — Operator productivity

> As **Adaeze (payroll operator)**,  
> I want to see all pending variable inputs queued for the next run — overtime, bonuses, deductions — in a single "inbox" view,  
> So that I can confirm everything is staged before I trigger the month-end run.

### Acceptance Criteria

- Given I navigate to Payroll Inputs: title "Payroll Inputs" + subtitle showing pending count ("X pending — will be claimed on next payroll run") or "No pending inputs for next run" when inbox is clear (DD-8)
- Given there are pending inputs: table shows Employee, Code, Category (EARNING/DEDUCTION/INFORMATION badge), Qty, Rate, Amount, For Period, Source columns
- Given I click "Add Input": SlideOver opens with Employee dropdown, Input Code dropdown grouped by category (EARNING/DEDUCTION/INFORMATION — DD-6), conditional fields (Qty for unit_multiplier, Amount for fixed_amount), and a month picker with hint "Leave blank for current run. Only set this for inputs from a prior month."
- Given I save a new input: panel closes, table refreshes, success toast appears
- Given I click the delete icon on a row: input removed immediately, success/error toast appears
- Given inbox is empty: EmptyState with "Add First Input" CTA — no blank table (DD-5)
- Given page load fails: AlertBanner variant="error"
- Given I delete the last input: table transitions smoothly to EmptyState

### Out of Scope
- Editing an existing input (delete and re-add)
- Filtering or searching inputs
- Bulk delete

---

## G3-UI-2 — Bulk Input Upload

**Priority:** P2 — Operator productivity

> As **Adaeze**,  
> I want to upload an Excel or CSV file with many period inputs at once,  
> So that I don't have to add high-volume items (e.g. 200 overtime records) one by one.

### Acceptance Criteria

- Given no file is selected: download template CTA is visible as the primary nudge (DD-5)
- Given I drag-and-drop or click to browse: FileDropZone enters processing state, then transitions to success (rows parsed) or error (validation failures)
- Given file parses cleanly: preview table shows all rows with "✓ OK" status column; Submit button enabled
- Given some rows have errors (unknown code, missing employee number): those rows highlighted in red with inline error; valid/invalid count shown as badges; only valid rows submitted
- Given I click Submit: success toast + AlertBanner summary showing created vs failed counts
- **[Amendment A]** Given submit succeeds with 0 errors: AlertBanner description includes "View in Inbox →" Link to `/workspaces/${workspaceId}/payroll/inputs`
- **[Amendment B]** Given all rows have errors (validCount === 0): hint below disabled Submit button reads "Fix the errors above before submitting."
- Given an unknown input code is encountered: error message instructs user to download the template to see valid codes

### Out of Scope
- Auto-correcting bad rows
- Multi-sheet Excel files

---

## G3-UI-3 — Payroll Runs List

**Priority:** P1 — Compliance (payroll must run on schedule)

> As **Adaeze**,  
> I want to see all payroll runs for this workspace with their current status,  
> So that I can track which runs are calculating, which need approval, and which are complete.

### Acceptance Criteria

- Given workspace is LIVE: "+ New Run" primary button enabled
- Given workspace is not LIVE: "+ New Run" disabled with tooltip; info AlertBanner directs to setup
- Given runs are loading: 5 skeleton rows shown (not spinner, not blank)
- Given runs exist: table shows Period, Pay Date, Status (StatusBadge — DD-12), Run ID (truncated), "View Results →" per row; clicking any row navigates to Results
- Given any run has status CALCULATING: page polls every 5s silently; when status transitions, toast appears ("Payroll run completed successfully" or "Run completed with some failures")
- **[Amendment C]** Given silent poll fails 3 consecutive times: AlertBanner shown "Auto-refresh paused — check your connection."; counter resets on success
- Given no runs exist and workspace is LIVE: EmptyState "No payroll runs yet" + "+ New Run" CTA (DD-5)
- Given no runs exist and workspace is not LIVE: EmptyState "Complete setup to unlock payroll runs" + "Continue Setup" CTA (DD-5)

### Out of Scope
- Deleting a run
- Filtering runs by date or status

---

## G3-UI-4 — New Payroll Run

**Priority:** P1 — Compliance

> As **Adaeze**,  
> I want to configure and submit a new payroll run for a specific period,  
> So that the system calculates results for all active employees.

### Acceptance Criteria

- Given workspace is not LIVE: AlertBanner warning shown; all form fields disabled; "Run Payroll" disabled
- Given workspace is LIVE: Period Start defaults to 1st of month, Period End defaults to today, Pay Date defaults to today
- Given I select Period Type "Custom": Working Days number input appears; disappears for MONTHLY or FORTNIGHTLY
- **[Amendment D]** Given period_start > period_end: client-side error "Period end must be after period start." blocks submit
- Given I submit successfully: button shows loading state; toast fires; navigate to Results page for new run
- **[Amendment E]** Given API returns 409: specific message "A run for this period already exists — view it in the Runs list." (not generic error)
- Given submit fails with other error: inline AlertBanner with message
- Given I click Cancel: return to Runs List

### Out of Scope
- Scheduling a future run
- Employee-level exclusions

---

## G3-UI-5 — Payroll Results & Run Detail

**Priority:** P0 — System correctness (financial output)

> As **Adaeze**,  
> I want to see the full results of a payroll run — summary totals, per-employee breakdown, reconciliation, and audit trail — in a single tabbed view,  
> So that I can verify correctness, take the next governance action (approve/lock/pay), and investigate any issues without navigating away.

### Acceptance Criteria

**Run header (always visible)**
- Run ID (truncated), period dates, pay date, StatusBadge (DD-12)
- Back link to Runs List

**DD-18: Polling**
- When status is CALCULATING: page polls every 5s; ActionPanel shows spinner + "Calculating payroll — refreshing automatically every 5 seconds…"
- When status transitions from CALCULATING: toast fires, UI updates

**Results tab**
- 4 SummaryCards: Employees, Gross Pay, Deductions, Net Pay (DD-1 / DAT-1)
- Status-driven single action (DD-3):
  - CALCULATING → spinner panel
  - PARTIAL → AlertBanner warning + "Retry Failed Employees" Btn
  - CALCULATED → "Approve Run" Btn primary
  - **[Amendment G]** APPROVED → "Run approved. Lock it when ready for payment processing." + "Lock Run" Btn primary (onLock was wired but Lock button was missing — now added)
  - LOCKED → "Mark as Paid" destructive Btn
  - PAID → green info panel "Run is PAID — no further actions available."
- "Mark as Paid" opens ConfirmDialog (DD-4): period, **[Fix F — already done]** net pay formatted with `formatNaira()`, "This action is irreversible." — red confirm button
- DownloadBtn row (bank upload / PAYE / pension) visible only when LOCKED or PAID
- PH warnings as AlertBanner variant="warning"
- Employee results DataTable; expanding a row shows ComponentTraceTable (DD-17: grid-template-rows, no flicker)

**Reconciliation tab (DD-7)**
- Expected total as prominent SummaryCard hero above all other content
- ReconciliationCard shows current status (AWAITING/MATCHED/MISMATCH/RESOLVED)
- When status allows: NumberInput (currency) for actual payment
- When MISMATCH: Textarea (notes) + TextInput (resolved_by) + "Mark as Resolved"

**Timeline tab** — PayrollTimeline component

**Audit Log tab** — TimelineTable with audit entries

### Out of Scope
- Editing employee results
- Exporting the audit log

---

## Amendment Summary

| Fix | File | Description | Status |
|-----|------|-------------|--------|
| A | PayrollInputsBulkUpload.tsx | Success banner: "View in Inbox →" link | 🔜 Pending |
| B | PayrollInputsBulkUpload.tsx | 0 valid rows: hint below disabled Submit | 🔜 Pending |
| C | PayrollRuns.tsx | Poll failure: AlertBanner after 3 retries | 🔜 Pending |
| D | RunPayroll.tsx | Client-side date validation | 🔜 Pending |
| E | RunPayroll.tsx | 409-specific error message | 🔜 Pending |
| F | PayrollResults.tsx | formatNaira() in ConfirmDialog | ✅ Already done |
| G | PayrollResults.tsx | APPROVED: copy fix + Lock Run Btn | 🔜 Pending |
