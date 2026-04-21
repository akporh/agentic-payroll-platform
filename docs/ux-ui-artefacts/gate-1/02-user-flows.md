# Gate 1 — User Flow Diagrams

Format: Each flow uses a structured notation.
- Rectangles [ ] = screens/pages
- Diamonds < > = decision points
- Ovals ( ) = system actions
- Pipes | | = validation gates
- → = happy path
- ✗→ = error path

---

## Flow 1 — Chidi: Onboard a New Client Workspace

```
[Bureau Dashboard]
       |
       → Click "+ New Workspace"
       |
[Create Workspace Modal]
  Fields: Name, Country Code (NG), Currency (NGN)
       |
       → Submit
       |
  <country_code valid?> ──✗→ Error: "No statutory rules for this country. Contact admin."
       |
       → (System creates workspace, status = DRAFT)
       |
[Workspace Dashboard] ← status = DRAFT, progress banner shown
       |
       → Click "Complete Setup" banner (or Settings → Setup Wizard)
       |
[Workspace Setup — Step 1: Structure]
  Grades, Designations, Pay Cycle
       |
       → Next
       |
[Workspace Setup — Step 2: Compensation]
  Salary Definitions
       |
       → Next
       |
[Workspace Setup — Step 3: Rules]
  Payroll Rules, Component Overrides
       |
       → "Preview"
       |
  (System validates dry-run)
       |
  <errors?> ──✗→ [Preview Result — Errors]
                    Show per-field errors and warnings
                    → Fix → Re-preview (loop)
       |
       → "Commit"
       |
  (System atomically writes all data)
  (Workspace auto-advances: DRAFT → ... → READY)
       |
[Workspace Dashboard] ← status = READY
  Banner: "Setup complete. Ready to go live."
       |
       → Click "Go Live"
       |
  (System transitions workspace: READY → LIVE)
       |
[Workspace Dashboard] ← status = LIVE
  Full feature access unlocked
       |
       → Navigate back to Bureau Dashboard
       |
[Bureau Dashboard]
  Workspace now appears as LIVE with employee count
```

**Escape routes:**
- Cancel modal at any point → return to Bureau Dashboard
- Save progress mid-wizard → return later (if partial onboarding persists)
- Power-user path: Settings → JSON Onboarding → paste/upload raw payload

---

## Flow 2 — Ngozi: Update Employee Contract After Promotion

```
[Workspace Dashboard] or [Employees]
       |
       → Navigate to Employees
       |
[Employee List]
  Table: Name, Number, Status, Grade, Designation, Contract Start
  Search / filter controls
       |
       → Find employee → Click "Edit Contract"
       |
[Edit Contract Inline/Modal]
  Fields: Grade (dropdown from workspace grades), Designation (dropdown)
       |
       → Save
       |
  <grade/designation found?> ──✗→ Error: "Grade 'X' not found in this workspace"
       |
       → (System patches active contract)
       |
[Employee List] ← updated row reflected
  Success toast: "Contract updated"

  --- OR BULK PATH ---

[Employee List]
       |
       → Click "Bulk Update Contracts"
       |
[Bulk Update Modal]
  CSV upload (employee_number, contract_start, contract_end)
  OR paste table
       |
       → Submit
       |
  (System processes each row)
       |
[Bulk Update Result]
  "X employees updated"
  Not found: [list of employee_numbers not matched]
       |
       → Done → [Employee List]
```

---

## Flow 3 — Adaeze: Collect and Enter Variable Inputs

```
[Workspace Dashboard]
       |
       → Navigate to Inputs (sidebar)
       |
[Input Inbox]
  Table of unclaimed inputs
  Filter: by employee, by code, by date
       |
  <has inputs to add?> ─── No → Empty state: "No pending inputs yet"
       |
  Path A: Single entry
       |
       → "+ Add Input"
       |
[Add Input Form (inline/slide-over)]
  Employee: searchable picker
  Input Code: dropdown (from valid workspace codes)
  Quantity: number (>= 0, client-validated)
  Reference Period: optional date picker ("Applies to period — leave blank for current")
       |
       → Save
       |
  <validation> ──✗→ Inline field errors (invalid code, negative quantity)
       |
       → (Input created, unclaimed)
  [Input Inbox] ← new row appears, toast "Input added"

  Path B: Bulk upload
       |
       → "Bulk Upload" button
       |
[Bulk Upload Screen]
  Drop zone for CSV/Excel
  Template download link
  Column guide: employee_number | input_code | quantity | reference_date
       |
       → Upload file
       |
  (System processes all rows)
       |
[Upload Result]
  "X inputs created successfully"
  Errors table: Row | Employee Number | Reason
       |
  <errors?> ──✗→ Download error report → Fix → Re-upload
       |
       → Done → [Input Inbox]

  At any time:
       |
       → Find wrong input → Click delete (🗑)
       |
  <input claimed?> ──✗→ No delete control shown (input is locked to a run)
       |
       → Confirm delete → Input removed
```

---

## Flow 4 — Adaeze: Run Payroll and Handle Results

```
[Payroll Runs List]
       |
  <workspace LIVE?> ──No→ Banner: "Workspace is not live. Complete setup to run payroll."
                           → Link to Setup Wizard
       |
       → "+ New Run"
       |
[New Run Form]
  Period Start / Period End: date pickers (pre-filled with current month)
  Period Type: MONTHLY | FORTNIGHTLY | CUSTOM
  [if CUSTOM] → Working Days field appears (required)
  Run Type: REGULAR (default) | ADJUSTMENT
  [ADJUSTMENT] → Rule Set picker appears (optional)
       |
  <period already exists?> (UI checks list) → Warning: "A run for this period already exists"
       |
       → "Run Payroll"
       |
  (Loading state — may be slow, show progress)
       |
  <readiness failure 422?> ──✗→ [Error State]
                                  Structured list: "Salary definitions missing → [Fix]"
                                  Each error links to relevant settings screen
       |
  <period duplicate 409?> ──✗→ Toast: "A run for this period already exists"
                                 → Link to existing run
       |
       → (Run created, status = CALCULATING)
       |
[Payroll Runs List] ← new row appears, status = CALCULATING
  Auto-poll or manual refresh until status changes
       |
  <status = PARTIAL?> ──────────────────────────────┐
       |                                             |
  <status = CALCULATED?> ─── → (Adaeze's happy path) |
                                                     ↓
                                          [Run Results — PARTIAL view]
                                          Alert banner: "3 employees failed. Review and retry."
                                          Results table: FAILED rows highlighted in red
                                          → Click failed employee → expand trace
                                          → Identify root cause
                                          → Fix data (edit salary def / input / config)
                                          → "Retry Failed Employees"
                                          → (System reprocesses only FAILED employees)
                                          → loop until CALCULATED
       |
[Run Results — CALCULATED view]
  Summary: total gross, total deductions, total net, employee count
  Table: all employees, SUCCESS rows, no FAILED rows
  Action: "Approve Run" (primary button)
       |
       → "Approve Run"
       |
  (Status: CALCULATED → APPROVED)
  Audit log entry created
       |
  Toast: "Run approved. Notify finance team to lock and pay."
  [Results view] ← status badge now APPROVED, Approve button replaced by "Awaiting Lock"
```

---

## Flow 5 — Emeka: Approve, Lock, Reconcile, Pay

```
[Payroll Runs List]
  Filter: Status = CALCULATED | APPROVED | LOCKED
       |
       → Click run in CALCULATED state
       |
[Run Results — CALCULATED view]
  Review: period, totals, employee count
  Spot-check: expand individual employees
  Check: Audit Log tab → confirm who ran it and when
       |
       → "Approve Run"
       |
  (Status → APPROVED)
       |
  [Notify bank to initiate payment — happens outside system]
       |
  [Receive bank confirmation of payment amount — outside system]
       |
       → Return to run → "Lock Run"
       |
  Confirm dialog: "Lock this run? This will prevent any further changes."
  Buttons: "Cancel" | "Lock Run"
       |
       → Confirm
       |
  (Status → LOCKED)
  Export buttons appear: Bank Upload | PAYE | Pension
       |
  → "Download Bank Upload CSV"
  → (File downloads — employee_number, name, bank, account, net_pay)
       |
       → Click "Reconciliation" tab
       |
[Reconciliation — Awaiting Submission]
  Expected total: ₦ X,XXX,XXX.XX (from engine)
  Status: Not yet reconciled
  Form: "Actual payment received" [number input]
  Submit button: "Submit Reconciliation"
       |
       → Enter actual_payment → Submit
       |
  <actual == expected?> ──No→ [Reconciliation — MISMATCH]
       |                       Variance displayed prominently in red
       |                       "Actual: ₦ X — Expected: ₦ Y — Difference: -₦ Z"
       |                       Resolution form:
       |                         Notes (required): [textarea]
       |                         Resolved by (required): [text input — identity]
       |                       → "Mark as Resolved"
       |                       → (Status → RESOLVED)
       |
       → [Reconciliation — MATCHED or RESOLVED]
  Read-only confirmation view
       |
       → "Mark as Paid"
       |
  Confirmation dialog (IRREVERSIBLE WARNING):
  "⚠ This action cannot be undone.
   Marking this run as PAID permanently closes it.
   No further changes will be possible."
  Buttons: "Cancel" | "Mark as Paid" (red, destructive)
       |
       → Confirm
       |
  (Status → PAID — terminal)
  [Results view] ← full read-only, PAID badge, exports still available
```

---

## Flow 6 — Tunde: Download Statutory Reports

```
[Payroll Runs List]
  Filter: Status = LOCKED | PAID
  Search: by period
       |
       → Find run for the period
       |
[Run Results — LOCKED or PAID view]
  Export section visible:
  [↓ Bank Upload] [↓ PAYE Remittance] [↓ Pension Contributions]
       |
  <any FAILED employees?> → Warning banner: "X employees excluded from exports due to failed calculations"
       |
       → "Download PAYE Remittance"
  → CSV downloads: employee_number, name, TIN, gross_pay, paye_withheld, period
       |
       → "Download Pension Contributions"
  → CSV downloads: employee_number, name, RSA, basic_pay, pension_base, emp_contrib, er_contrib, period
       |
  [File saved to desktop — upload to FIRS / PFA portal outside system]
```

---

## Flow 7 — Chidi: Monitor Bureau Health

```
[Bureau Dashboard]
  Workspace list with health indicators:
  - LIVE, active employees, last run status
  - ⚠ Alert badges: PARTIAL, MISMATCH, CALCULATING > threshold
       |
  <alerts present?> → Alert section at top: "3 workspaces need attention"
       |
       → Click workspace with MISMATCH alert
       |
[Workspace Dashboard] ← MISMATCH banner shown
       |
       → Click "Payroll Runs"
       |
[Runs List] ← run with MISMATCH reconciliation highlighted
       |
       → Click run → Reconciliation tab
       |
  → Review mismatch, resolve or escalate
```

---

## Flow 8 — Chidi: Configure Public Holidays

```
[Settings → Public Holidays]
  Year selector (default: current year)
  List: National holidays (read-only) + Workspace holidays (editable)
       |
       → "+ Add Holiday"
       |
  Inline form: Date picker | Name input
       |
  <duplicate date?> ──✗→ Error: "A holiday already exists on this date"
       |
       → Save → Holiday added to list
       |
  Workspace holiday row shows: Name | Date | "Workspace" badge | 🗑 delete
  National holiday row shows: Name | Date | "National" badge | (no delete)
       |
  → Also: Settings → Payroll Config
       |
[Payroll Config]
  PH Mode: AUTOMATIC | FILE_BASED (radio buttons)
  PH Rate Code: dropdown from rate codes list
  Saturday PH: PH_TAKES_PRECEDENCE | DAY_OF_WEEK_TAKES_PRECEDENCE (radio + explanation)
  Sunday PH: same
  Leave overlap: LEAVE_ABSORBS_PH | PH_ADDITIVE (radio + explanation)
  Absence on PH: ABSENT_IS_DEDUCTIBLE | PH_EXCUSES_ABSENCE (radio + explanation)
  Effective from: date picker
       |
       → "Save Config"
       |
  (Config saved as a new versioned row)
  Toast: "Payroll config updated. Effective from [date]."
```

---

## Critical Path — Most Important Flow

**Adaeze's monthly payroll cycle (Flows 3 + 4 combined) is the highest-frequency, highest-stakes operation.** Every month-end, she runs this cycle 5–8 times across clients. Gate 3 implementation starts here.

The complete monthly cycle in steps:
1. Open workspace → check Input Inbox (S7)
2. Add/upload variable inputs (S7/S8)
3. Navigate to Runs (S9)
4. Click New Run → submit form (S10)
5. Wait for result → check for PARTIAL
6. Retry if needed → reach CALCULATED (S11)
7. Review results → Approve (S11)
8. Hand off to Emeka (context switch)

Total steps: 7 screens, 10–15 clicks on the happy path. This must be optimised ruthlessly.
