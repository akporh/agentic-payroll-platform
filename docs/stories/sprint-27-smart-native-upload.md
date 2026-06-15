# Sprint 27 — Smart Native Upload

## Overview

Sandy's clients send payroll data in their own Excel formats — non-standard column headers, metadata rows above the data, multi-block layouts. The current system requires operators to use a fixed template, meaning client files must be manually reformatted every cycle. This sprint adds three smart upload paths that accept client files as-is, auto-detect column headers, let the operator verify the mapping, then submit to the existing backend endpoints unchanged.

No backend changes required for any story in this sprint.

---

## Story 1 — EMP-NATIVE-1: Smart Employee Upload

**Priority:** P2 · Operator Productivity

```
As Sandy (payroll operator),
I want to upload a client's existing employee spreadsheet in their own format,
So that I can register new employees without reformatting every client's file first.
```

### Acceptance Criteria

**File parsing**
- When I drop an `.xlsx` or `.xls` file, the system scans rows 1–15 and scores each row by how many cells match known field aliases
- If ≥ 3 required fields are matched, the header row is auto-selected and parsing proceeds without interruption
- If fewer than 3 fields are matched, I see a **row-picker**: a preview of the first 15 rows with a *"Use this as the header row"* action — parsing runs from the selected row downward
- The detected or selected header row is shown in the mapping preview so I can verify it
- Merged cells in the header row are forward-filled before alias matching — blank cells in a merge inherit the left-most cell value

**Column mapping**
- I see a **mapping preview** grouped as: *Needs attention* (expanded) · *Matched* (collapsed) · *Excluded* (collapsed)
- Auto-matched columns show a green tick; unresolved columns show a dropdown to select the target field or exclude
- If a required field (`employee_id`, `first_name`, `last_name`) cannot be auto-matched, I must resolve it before confirming
- `contract_end` absent from the file: silently omitted (valid)

**Data preview & submission**
- I see a data preview table of the rows to be created before confirming
- Duplicate `employee_id` values within the file: flagged per-row, blocked until resolved
- Entirely blank rows: silently skipped
- The confirm button is labelled *"Register N employees"*
- On confirm → employees created via existing `workspaceApi.createEmployee()` parallel calls → success/error summary
- `grade` maps to `imported_grade_label`; `designation` maps to `imported_designation_label`; `salary_definition_code`, `grade_code`, `designation_code` always `null` (Sprint 22 contract)

**Failure states**
- No row scores any alias matches after row-picker: error — *"Could not detect employee columns. Use the Template upload instead."*
- File is not `.xlsx` / `.xls`: rejected at drop with a clear format message

**Out of scope:** CSV support · multi-sheet detection (always reads Sheet 1) · saving column mappings · payroll fields

### Field Alias Map

| Target field | Recognised header names |
|---|---|
| `employee_id` | ID NUMBER · STAFF ID · EMPLOYEE ID · EMPLOYEE NO · EMPLOYEE NUMBER |
| `first_name` | FIRST NAME · FIRSTNAME · FORENAME |
| `last_name` | SURNAME · LAST NAME · FAMILY NAME |
| `grade` | CATEGORY · GRADE · STEP · GRADE CODE |
| `designation` | DESIGNATION · JOB TITLE · ROLE · POSITION |
| `tin` | TAX IDENTIFICATION · TIN · TAX ID |
| `rsa` | PENSION PIN · RSA PIN · RSA |
| `bank` | BANK · BANK NAME |
| `account_number` | ACCOUNT NO · ACCOUNT NUMBER · ACCT NO |
| `contract_start` | DATE EMPLOYED · START DATE · EMPLOYMENT DATE · JOINING DATE |
| `contract_end` | END DATE · CONTRACT END · EXIT DATE · TERMINATION DATE |

---

## Story 2 — INP-NATIVE-1: Smart Period Inputs Upload

**Priority:** P2 · Operator Productivity

```
As Sandy (payroll operator),
I want to upload a client's monthly inputs spreadsheet in their own format,
So that I don't manually reformat overtime, shift, and allowance data every month.
```

**Context:** Parser-only change. The upload UI, preview table, validation, and `POST /bulk` submission are all reused unchanged from `NativeUploadFlow`. The new code covers column header detection, deduplication, and long-format row emission.

### Acceptance Criteria

**File parsing — header detection**
- When I drop the file, the system scans rows 1–15 scoring each row by how many cells match the pattern `THE MONTH OF {MONTH} {YEAR} {INPUT TYPE KEYWORD}`
- If ≥ 2 input columns are confidently detected, the header row is auto-selected
- If fewer than 2 are detected, I see the **row-picker** before mapping proceeds
- The selected header row is shown above the preview table
- Merged cells in the header row are forward-filled before parsing

**File parsing — column extraction**
- For each column header matching the period/keyword pattern, the parser extracts:
  - **Period** — month name + year → normalised to `YYYY-MM-01`
  - **Rate** — the `@N{amount}` portion of the header (e.g. `@N1000.00`) → used to compute quantity; stripped before keyword matching
  - **Input type keyword** → fuzzy-matched to workspace `input_code` using Levenshtein distance ≤ 2 (tokens ≥ 4 chars), enabling typo-tolerant matching (e.g. "WEEKDEND" → "WEEKEND", "WEEKENE" → "WEEKEND")
- Sub-types are treated as distinct — "SPECIAL OVERTIME" and "OVERTIME" map to different input codes if both exist in the workspace
- **Duplicate column deduplication**: files commonly have a main input block followed by a reporting/calculation block with the same headers. The parser tracks `{period, input_code}` pairs — the first occurrence of each pair is mapped; subsequent occurrences are auto-excluded. The operator can reassign them from the Excluded section if needed.
- Only the first employee identifier column is mapped; additional identifier columns are auto-excluded

**Row emission — long format**
- For each data row, the parser reads `employee_no` from the first matched identifier column
- For each active (non-excluded) input column, if the cell value is non-blank, non-zero, and not `-`: emit one row `{ employee_number, input_code, quantity, reference_date }`
- **Quantity = cell value ÷ `@rate` from the column header** — the cell contains the amount earned; the header rate is the per-unit value configured in the payroll rule (e.g. cell = ₦20,000, rate = ₦1,000/day → quantity = 20)
- If no `@rate` is present in the header, the raw cell value is used as quantity (fallback)
- Blank, `0`, and `-` cells are silently skipped — no zero-quantity rows emitted
- Emitted rows feed directly into the existing preview table and `POST /bulk` submission — no intermediate format

**Column mapping panel**
- After parsing, I see a **column mapping panel**: each detected input column shows the raw header text (which includes period and rate) alongside the proposed `input_code`
- Multiple columns may map to the same `input_code` — the dropdown shows all workspace codes regardless of what other columns have claimed (`allowDuplicateTargets` mode)
- I can override any auto-matched `input_code` from a dropdown of all valid workspace codes
- I can exclude a column; excluded columns do not emit rows
- Unresolved columns (no auto-match found) block the Continue button until resolved or excluded
- Required: the employee identifier column must be mapped before continuing

**Validation & submission**
- Employee numbers with no enrolled match: flagged in preview, do not block the rest
- If the file spans multiple periods, all periods are parsed and emitted in a single operation
- Confirm button labelled *"Add N input rows"* where N is the parsed row count
- On confirm → existing `POST /{workspaceId}/payroll/inputs/bulk` → existing success/error summary

**Failure states**
- No input columns mapped (all excluded or none found): error — *"Could not detect input columns. Use the Template upload instead."*
- File is not `.xlsx` / `.xls`: rejected at drop

**Out of scope:** Wide-format template redesign (deferred) · CSV · saving column mappings · salary or statutory fields

---

## Story 3 — PAY-RECON-1: Payroll Reconciliation Upload

**Priority:** P2 · Operator Productivity

```
As Sandy (payroll operator),
I want to upload a client's old system payroll output for a given period
and compare it against the new system's results,
So that I can verify the new system is calculating correctly without
manually cross-referencing two spreadsheets.
```

**Context:** The new system stores `net_pay`, `gross_pay`, and a full `component_trace_jsonb` per employee result. The old system's file contains a superset of columns — the comparison covers only the intersection (fields that exist in both). This is not a data import — nothing is written to the database.

### Acceptance Criteria

**Entry point**
- The reconciliation upload is accessible from a completed payroll run (status APPROVED or later) via a *"Reconcile with old system"* button on the Results tab
- Opens a SlideOver containing the two-step reconciliation flow

**File parsing — same smart parser mechanics as EMP-NATIVE-1**
- System scans rows 1–15, auto-detects header row by alias scoring
- Row-picker fallback if confidence is low
- Merged cells forward-filled before parsing
- Parser identifies: an employee identifier column + all numeric value columns

**Column mapping**
- After parsing, I see a **column mapping panel**: each detected numeric column → proposed new system field
- Only fields available in the new system's results for this run are offered as mapping targets
- I can override any auto-matched mapping or uncheck a column to exclude it
- Columns with no new system equivalent are excluded by default
- I must map at least one value column before proceeding

**Comparison output — wide format**
- After confirming the mapping, the SlideOver transitions to a **comparison table**
- One row per employee; for each mapped field: three sub-columns — *Old · New · Diff*
- A **Status** column shows: `MISMATCH` (any field differs) · `MATCH` (all match) · `NEW ONLY` · `OLD ONLY`
- Filter chips: **All · Mismatch (N) · Match (N) · Unmatched (N)** — default view: Mismatch
- Diff cell: ▲/▼ prefix + value; zero diff shown as `—`; ▼ = red, ▲ = amber, `—` = muted
- Columns are dynamic — generated from the operator's confirmed field mappings

**Download**
- A *"Download"* button exports the full wide-format comparison as `.xlsx` via `XLSX.utils.json_to_sheet`
- Download includes all status values including MATCH rows (for audit purposes)

**Nothing is written**
- No payroll data, employee records, or inputs are created or modified
- The uploaded file is parsed in-memory only — not stored

**Failure states**
- No employee identifier column detected after row-picker: error — *"Could not detect an employee identifier column."*
- No numeric columns detected: error — *"No comparable value columns found in this file."*
- Run has no completed results: error — *"This run has no results to compare against."*
- File is not `.xlsx` / `.xls`: rejected at drop

**Out of scope:** Comparing multiple runs · storing reconciliation results · automated mismatch resolution · CSV

### Field Alias Map (Reconciliation)

| Target field | Recognised header names |
|---|---|
| `employee_id` | ID NUMBER · STAFF ID · EMPLOYEE NO · EMPLOYEE NUMBER |
| `net_pay` | NET SALARY · NET PAY · NET · TAKE HOME |
| `gross_pay` | STAFF GROSS · GROSS SALARY · GROSS PAY · GROSS |
| `paye` | PAYE · TAX · INCOME TAX |
| `pension_employee` | PENSION (EMPLOYEE) · PENSION EMPLOYEE · EMPLOYEE PENSION |
| `development_levy` | DEVELOPMENT LEVY · DEV LEVY |
| `nhf` | NHF · NATIONAL HOUSING FUND |
| `basic_salary` | BASIC SALARY · BASIC · BASIC PAY |
| `housing` | HOUSING ALLOWANCE · HOUSING |
| `transport` | TRANSPORT ALLOWANCE · TRANSPORT |

---

## Story 4 — INP-MULTI-1: Multi-row Period Input Entry

**Priority:** P2 · Operator Productivity

```
As Sandy (payroll operator),
I want to add multiple input lines for the same employee in a single operation,
So that I don't have to reopen the panel for every overtime, shift, and
allowance entry for the same person.
```

**Context:** Enhancement to the existing "Add Payroll Input" SlideOver on the
Period Inputs page. The edit flow (modifying one existing input) is unchanged.
No backend changes — submits N parallel calls to the existing single-create
endpoint `POST /{workspaceId}/payroll/inputs`.

### Acceptance Criteria

**Multi-row entry**
- The "Add Payroll Input" SlideOver shows an **Employee** selector at the top (full-width), then a **line-item table** below with columns: Input Code · Qty · For Period · remove (×)
- On open, one blank row is pre-populated
- The employee selector applies to all rows; the row table is dimmed with an info banner until an employee is selected
- "+ Add another input" adds a new row; the new row inherits the period value from the previous row
- The × remove button appears only when ≥ 2 rows exist; the last row cannot be removed
- The submit button is labelled *"Add N inputs"* where N is the count of valid (non-empty code) rows
- Submit button is disabled when no employee is selected or no rows have an input code

**Validation**
- On submit, rows with no input code are flagged inline with a red ring; valid rows are submitted
- Rows where qty is required by the input code but is blank are flagged inline
- If all rows fail validation, submission is blocked with a message *"Fix the errors above"*

**Submission & result**
- Valid rows are submitted in parallel via the existing `payrollInputApi.create()` (one call per row, using `employee_id`)
- Rows that succeed show a ✓ inline; rows that fail show the error message inline
- If all rows succeed: panel closes, toast *"N inputs added to payroll inbox"*
- If some rows fail: panel stays open showing inline errors; succeeded rows are locked (cannot re-submit)

**Edit mode unchanged**
- Editing an existing input still uses the current single-field form (employee + code shown as read-only text, qty + period editable)

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Pattern | Line-item entry (anchor + rows) | Operator mental model is "everything for this person" — same as invoice entry |
| Employee position | Full-width above row table | Single anchor makes it clear all rows share this employee; reduces visual noise |
| Period inheritance | New row copies period from previous row | Most inputs for the same employee share the same month; saves keystrokes |
| Submission | Parallel single-create calls | Reuses existing API; `employee_id` already available from select; no bulk-endpoint mismatch |
| Partial success | Inline row-level status, panel stays open | Operator must see exactly which rows failed without losing the succeeded context |
| Raw inputs in rows | `<input>` / `<select>` styled to DS tokens | DS `NumberInput`/`DateInput` are block elements with label markup; break table-cell layout |
| Edit mode | Unchanged single-field form | Different context (patching one existing record); line-item pattern adds no value |

See also: `docs/design/ui-decisions.md` → "Multi-row data entry"

---

## Story 5 — EMP-REG-5-FIX: Enrollment slide-over pre-population after group upload

**Priority:** P1 · Operator Productivity (blocks enrollment UX post-upload)
**Fixes:** EMP-REG-5 (Sprint 23 — Auto-suggest enrollment by grade group)

```
As Sandy (payroll operator),
I want the enrollment slide-over to pre-fill grade, designation, and salary
definition from the values the system already detected during upload,
So that I do not have to re-enter information the system already knows.
```

**Context:** EMP-REG-5 delivered the group suggestion panel correctly. The matching logic that feeds the slide-over used `toUpperCase()` only. Import files routinely have spaces where configured codes use underscores (`"General Manager"` vs `"GENERAL_MANAGER"`). The match failed silently — all slide-over fields opened blank. The native upload path introduced in this sprint (EMP-NATIVE-1) made this worse: it stored grades as raw strings, guaranteeing a mismatch for any multi-word grade.

### Acceptance Criteria

**Normalised matching — spaces, hyphens, case**

Given `imported_grade_label = "General Manager"` and a configured grade code of `"GENERAL_MANAGER"`,
When the Awaiting Enrollment section loads,
Then the group is matched — normalisation rule: trim → UPPER → spaces and hyphens → `_`.

Given `imported_grade_label = "step_1"` and salary def code `"STEP_1"`,
Then the salary def match is found (generalises EMP-REG-5 D-ARCH-6 case-only rule).

**"Enroll N" button (salary def matched) — existing behaviour unchanged**

Given I click "Enroll N" on a fully-matched group,
Then direct enroll proceeds as before — no slide-over required.

**"Select →" button pre-fills grade and designation**

Given I click "Select →" on a group where no salary def is matched,
Then BulkEnrollSlideOver opens with:
- `salary_definition_code` empty — operator must choose,
- `grade` pre-filled with the matched configured code when a normalised match exists,
- `designation` pre-filled with the matched configured code when a normalised match exists,
- If no configured code matches the imported label, the field shows the label marked `(from import)` — operator can confirm or override.

**Individual "Enroll →" pre-fills all fields**

Given I expand a group and click "Enroll →" on a single employee,
Then EnrollSlideOver opens with:
- `grade` pre-filled (normalised match of `imported_grade_label` against configured codes),
- `designation` pre-filled (normalised match of `imported_designation_label` against configured codes),
- `salary_definition_code` auto-matched from the resolved grade and designation where possible.

**Native upload normalises on ingest**

Given I upload a client file via the native path (EMP-NATIVE-1) with grade `"Senior Officer"`,
Then `imported_grade_label` is stored as `"SENIOR_OFFICER"`,
And the group suggestion panel and slide-over matching treat it identically to template-upload behaviour.

**No regressions on existing exact-match cases**

Given `imported_grade_label = "STEP_1"` and salary def code `"STEP_1"` (already an exact match),
Then behaviour is identical to before this fix — direct-enroll path unaffected.

### Out of Scope

- Fuzzy prefix matching (`STEP_1B → STEP_1`) — deferred. A wrong salary def suggestion causes wrong payroll calculations; exact normalised match only.
- Auto-enrolling without user confirmation — the one-click confirm is an intentional checkpoint before a payroll-consequential action.

### Business Risk

| | |
|---|---|
| **Cost of NOT doing this** | Every post-upload enrollment requires manual re-entry of grade/designation/salary def — defeating the group suggestion panel built in EMP-REG-5. Blocks Sandy UAT on the native upload flow. |
| **Cost of doing it wrong** | A false normalisation match (e.g. treating different grades as the same) would assign wrong salary def → wrong payroll calculations. Fix uses exact normalised match only — no prefix or fuzzy logic. |

### Implementation Notes

All changes in `frontend/src/pages/Employees.tsx`:
- `normalizeCode` helper added at module level: `s.trim().toUpperCase().replace(/[\s-]+/g, '_')`
- Applied in: `autoMatchSalaryDef`, `EnrollSlideOver` useEffect, `suggestedGroups` (grade, designation, salary def matching)
- `parseNativeRows`: normalises grade/designation on ingest
- "Select →" handler: falls back to `rawGradeLabel`/`rawDesigLabel` when no configured code matches
- `BulkEnrollSlideOver` dropdowns: injects `(from import)` option when preset value is not a configured code

---

## Shared Architecture

All three stories use a common `NativeUploadFlow` component and shared parsing utilities in `nativeExcelParser.ts`. See plan file for full implementation detail.

**New files:**
- `frontend/src/utils/nativeExcelParser.ts`
- `frontend/src/components/shared/ColumnMappingPanel.tsx`
- `frontend/src/components/shared/NativeUploadFlow.tsx`

**Modified files:**
- `frontend/src/pages/Employees.tsx` — add native upload mode to UploadSlideOver
- `frontend/src/pages/PayrollInputsBulkUpload.tsx` — add native upload mode
- `frontend/src/pages/PayrollResults.tsx` — add reconciliation SlideOver to Results tab

No backend changes. No migrations.
