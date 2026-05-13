# Sprint 16 — Timesheet Layer Implementation

**Track:** O (Timesheet / Variable-Pay Clients) — closes NEW-GAP1 / O6  
**Priority:** P1 — compliance and client delivery obligation; Client B cannot run payroll on the platform without this  
**Effort:** XL+ (7 stories, 5 migrations, 3 new service files, 2 new model files, frontend)  
**Arch-council:** ✅ APPROVED (2026-05-12) — 10 binding decisions (AC-1 through AC-10) + 2 critical fixes (C1, C2) + 4 high-priority pre-conditions (H1–H4) — all resolved in Sprint 15  
**Attendance config revision:** ✅ APPROVED (2026-05-13) — two-table split, template versioning, onboarding flow, `resolve_hours()` spec — all resolved in Sprint 15 revision  
**Plan files:**  
- `~/.claude/plans/splendid-gliding-sun.md` — Sprint 15 original arch-council decisions  
- `~/.claude/plans/from-the-plan-users-michaelemedo-claude-sleepy-dream.md` — attendance config architecture revision v2

---

## Problem

Client B (and future timesheet-based clients) run variable-pay payrolls driven by daily attendance data. The platform currently only supports the period-input-file route (`payroll_input` rows uploaded via Excel). To onboard timesheet clients the platform needs a translation layer that reads raw daily attendance grids, derives OT hours and proration factors using workspace-configured rules, and writes canonical `payroll_input` rows for the existing executor to process unchanged.

No new pay-instruction abstraction is required. `payroll_input` IS the pay instruction model. What is missing is the normalisation step that produces it from timesheets.

Three-layer architecture:

```
[Client HR Timesheet — raw daily attendance grid]
        ↓
[Translation Layer — TimesheetDerivationService]   ← BUILD THIS
        ↓
[payroll_input table — Pay Instruction Model]      ← UNCHANGED
        ↓
[Payroll Engine / Sequential Executor]             ← UNCHANGED
```

---

## User Stories

### TM-1: Workspace timesheet configuration

```
As a platform admin,
I want to configure a workspace as timesheet-enabled or input-file-only,
So that operators for timesheet-based clients see a timesheet upload flow,
while operators for salary-only clients continue using the period input file.
```

### TM-2: Timesheet upload

```
As an HR operator for a timesheet-enabled workspace,
I want to upload the monthly timesheet Excel file,
So that daily attendance data is captured in the system for the pay period.
```

### TM-3: Timesheet derivation pipeline

```
As the system,
I want to derive OT hours, proration factor, and shift days from raw attendance data,
So that these values can flow into payroll without manual calculation.
```

### TM-4: Manual OT override

```
As an HR operator,
I want to enter manual OT adjustments on top of auto-derived OT hours,
So that I can correct errors without re-uploading the entire timesheet.
```

### TM-5: Timesheet-to-pay-instruction flow

```
As the system,
I want to convert derived timesheet aggregates into pay instructions (payroll inputs),
So that the executor can process OT and prorated salary components without change.
```

### TM-6: Timesheet audit trail

```
As an auditor,
I want to see the derivation inputs and outputs for each employee for each period,
So that I can verify OT calculations and proration without accessing the raw spreadsheet.
```

### TM-7: Attendance code and policy workspace configuration

```
As an HR operator for a timesheet-enabled workspace,
I want to view and configure the attendance codes and their pay policies for my workspace,
So that the derivation service correctly interprets daily attendance data for my client's
specific leave and shift rules.
```

---

## Acceptance Criteria

### TM-1 — Workspace timesheet configuration

**TM-1-AC-1 — Config gate**
**Given** a `workspace_payroll_config` row exists for the workspace  
**When** `timesheet_enabled = TRUE`  
**Then** the operator sees a timesheet upload flow; input-file upload is not presented

**TM-1-AC-2 — Default is FALSE**
**Given** a new workspace  
**When** `workspace_payroll_config` is created  
**Then** `timesheet_enabled` defaults to `FALSE`; no timesheet routes are exposed

**TM-1-AC-3 — Non-timesheet workspace rejects upload**
**Given** `timesheet_enabled = FALSE`  
**When** a timesheet upload is attempted  
**Then** the API returns `400` with a clear user-facing error

**TM-1-AC-4 — In-flight runs unaffected**
**Given** a run in `SUBMITTED` or later status  
**When** `timesheet_enabled` is toggled  
**Then** the in-flight run is not affected; existing `payroll_input` rows are not changed

**TM-1-AC-5 — Readiness gate**
**Given** `timesheet_enabled = TRUE`  
**When** any employee's `timesheet_entry.derivation_status ≠ 'APPROVED'`  
**Then** `payroll_readiness_service` blocks `link_inputs_to_run` with a readable error listing which employees are not approved (C2)

**TM-1-AC-6 — Attendance codes seeded on first enable**
**Given** a workspace where `timesheet_enabled` is being set to `TRUE` for the first time  
**When** the toggle is saved  
**Then** platform attendance code templates (v1) are seeded into `attendance_code_config` and `attendance_policy_config` for this workspace; `workspace.attendance_template_version` is set to the current platform template version; if template rows already exist for the workspace they are not overwritten (`ON CONFLICT DO NOTHING`)

**TM-1-AC-7 — Template version warning**
**Given** a timesheet-enabled workspace  
**When** the workspace's `attendance_template_version` is behind the current platform template version  
**Then** the WorkspaceConfig UI shows a non-blocking warning: "New attendance codes are available — review Attendance Configuration to add them"

---

### TM-2 — Timesheet upload

**TM-2-AC-1 — Raw grid only accepted**
**Given** a timesheet Excel file  
**When** it is uploaded  
**Then** the parser extracts raw daily cells only; pre-aggregated formula columns are silently ignored

**TM-2-AC-2 — Employee matching**
**Given** a row in the uploaded file  
**When** the parser reads the employee identifier column (`employee_number`)  
**Then** it is matched against `employee.employee_number` exactly; fuzzy matching is not performed; unmatched employees → row-level rejection in upload response

**TM-2-AC-3 — Unknown attendance codes rejected at row level**
**Given** a cell containing a code not present in `attendance_code_config` for the workspace  
**When** the upload is processed  
**Then** the row is rejected with cell reference (e.g. `D14: unknown code 'XYZ'`); valid rows in the same upload are still stored

**TM-2-AC-3b — Code exists but policy not configured — warning at upload**
**Given** a cell containing a code that exists in `attendance_code_config` but has no corresponding `attendance_policy_config` row  
**When** the upload is processed  
**Then** the row is stored as `derivation_status = 'PENDING'`; the upload response includes a warning per affected employee: "code X has no policy configured — derivation will fail until resolved"; the operator must configure the policy via Attendance Configuration before derivation can run

**TM-2-AC-3c — Inactive code — warning at upload**
**Given** a cell containing a code where `attendance_code_config.is_active = FALSE`  
**When** the upload is processed  
**Then** a warning is included in the upload response per cell reference: "code X is inactive — contact your admin to re-enable it"; the row is stored at `PENDING`

**TM-2-AC-4 — Employee with no salary definition**
**Given** an employee row in the upload where no salary definition is found for that employee  
**When** the upload is processed  
**Then** the row is flagged in the upload response as a warning: "employee_number X: no salary definition found — derivation cannot complete until resolved"; the row is stored as `derivation_status = 'PENDING'`; derivation cannot be triggered for that employee until the salary definition is configured

**TM-2-AC-5 — PH column headers validated**
**Given** PH-flagged column headers in the uploaded file  
**When** the upload is processed  
**Then** each flagged date is validated against the workspace public holiday config; mismatches → warning in upload response (not rejection)

**TM-2-AC-6 — Duplicate upload replaces timesheet rows only**
**Given** a prior upload exists for the same `(workspace_id, period)`  
**When** a new upload is submitted  
**Then** previous `timesheet_entry` rows for the period are replaced; `payroll_input` rows are NOT touched (those are written on approval, per AC-4)

**TM-2-AC-7 — Upload response**
**When** any upload completes  
**Then** the response includes: employees found, rows accepted, rows rejected (with per-row error detail), warnings (policy gaps, inactive codes, PH mismatches)

**TM-2-AC-8 — Upload sets derivation status**
**When** an employee's rows are accepted  
**Then** `timesheet_entry.derivation_status = 'PENDING'`

---

### TM-3 — Timesheet derivation pipeline

**TM-3-AC-1 — Pure domain function**
**Given** raw attendance grid dict, attendance codes dict (semantic), attendance policies dict (pay interpretation), OT trigger rule config, PH date set, rate code map, shift type, employee contract window, and `hours_per_day` as `Decimal`  
**When** `timesheet_derivation.py` domain function is called  
**Then** it returns a list of `payroll_input` dicts and a `DerivationSummary` struct without any DB access; all numeric operations use `Decimal`, not `float`

**TM-3-AC-2 — Active window for mid-period hires**
**Given** `contract_start > period_start` (mid-period hire) or `contract_end < period_end` (termination)  
**When** derivation runs  
**Then** `expected_working_days` and `expected_hours` are computed over the employee's active window:  
`max(period_start, contract_start)` → `min(period_end, contract_end)`  
NOT over the full period (H1)

**TM-3-AC-3 — PH hours excluded from accumulation**
**Given** a day flagged as a public holiday  
**When** derivation processes the attendance grid  
**Then** hours on PH days are excluded from `total_hours_accumulated` and routed directly to the OT3 rate code bucket via the workspace `PH_DAY` trigger rule

**TM-3-AC-4 — Leave hours count toward OT threshold**
**Given** an employee with any paid leave code (L, SLA, SLD, SLN, P, M, C) in their grid  
**When** derivation runs  
**Then** those hours are included in `total_hours_accumulated` on equal footing with actual work hours — driven by `attendance_policy_config.counts_towards_ot_threshold = TRUE` for those codes, not hardcoded code lists

**TM-3-AC-5 — Three-step cap formula (mandatory)**
**When** derivation computes base-pay hours  
**Then** the three-step derivation is applied exactly:
```
step 1:  total_hours_accumulated = actual_hours + paid_hours_accumulator
         [paid_hours_accumulator = sum of hours for codes where counts_as_paid = TRUE]
         [does NOT include PH hours — those are in OT3 bucket]
step 2:  excess_OT1_hours = MAX(0, total_hours_accumulated − expected_hours)
step 3:  total_hours_paid = total_hours_accumulated − excess_OT1_hours
         [= MIN(accumulated, expected_hours); always ≤ expected_hours]
         proration_factor = total_hours_paid / expected_hours  [always ≤ 1.0; Decimal]
```
Rationale: base salary is paid for up to `expected_hours` only. Hours above that are compensated as OT at the applicable multiplier. Uncapped `total_hours_accumulated` in the proration numerator inflates all salary components — verified to produce ~₦10–13K overpayment per employee per period on Client B test data.

**TM-3-AC-6 — Full-period employee proration factor = 1.0**
**Given** an employee who works a complete period with no absences  
**When** derivation runs  
**Then** `proration_factor = Decimal('1.0')`; no reduction is applied to salary components

**TM-3-AC-7 — `resolve_hours()` definition**

`resolve_hours(cell, policy, hours_per_day: Decimal) → Decimal`:

| Cell value | Policy state | Result |
|------------|-------------|--------|
| Numeric (e.g. `8`) | — | `Decimal(str(cell))` — face value |
| Leave code | `hours_equivalent` set | `Decimal(str(hours_equivalent))` — fixed hours |
| Leave code | `unit_fraction` set | `unit_fraction × hours_per_day`, quantized to 2dp |
| Leave code | both NULL | `Decimal('0')` — zero hours (valid for unpaid zero-hours codes) |
| Leave code | no policy row | `UnknownAttendanceCode` raised — never reached (prefetch validates) |
| None / blank | — | `Decimal('0')` |

**Worked example — Client B, 4-SHIFT employee (`hours_per_day = Decimal('12')`):**

| Cell | Policy | Result |
|------|--------|--------|
| `8` | WORK code (numeric) | `Decimal('8')` |
| `L` | `unit_fraction = 1.0` | `1.0 × 12 = Decimal('12.00')` |
| `SLA` | `hours_equivalent = 6.5` | `Decimal('6.50')` |
| `SLD` | `hours_equivalent = 8` | `Decimal('8.00')` |
| `SLN` | `hours_equivalent = 11` | `Decimal('11.00')` |
| `P` | `hours_equivalent = 8` | `Decimal('8.00')` |

**TM-3-AC-8 — OT classification precedence (H3)**

Day classification — `classify_day(date, shift_type, ph_date_set) → DayType`:

```python
def classify_day(date, shift_type, ph_date_set):
    # Precedence: PUBLIC_HOLIDAY > SATURDAY (DAY shift only) > WEEKDAY
    if date in ph_date_set:
        return DayType.PUBLIC_HOLIDAY
    if date.weekday() == 5:  # Saturday
        if shift_type == 'DAY':
            return DayType.SATURDAY_DAY_SHIFT  # → OT2 bucket
        else:
            # Rotating shifts: Saturday accumulates toward OT1 threshold
            return DayType.WEEKDAY
    return DayType.WEEKDAY
```

Per-day derivation loop — all accumulators are `Decimal`, loop is policy-driven (no hardcoded code lists):

```python
actual_hours = Decimal('0')
paid_hours_accumulator = Decimal('0')
shift_days_worked = 0
ot_buckets: dict[str, Decimal] = defaultdict(Decimal)

for day in active_window_days:
    day_type = classify_day(day, shift_type, ph_date_set)
    cell = attendance_grid.get(day)

    if day_type == DayType.PUBLIC_HOLIDAY:
        ot_buckets[OT3_rate_code] += resolve_hours(cell, attendance_policies.get(cell), hours_per_day)
        continue
    if day_type == DayType.SATURDAY_DAY_SHIFT:
        ot_buckets[OT2_rate_code] += resolve_hours(cell, attendance_policies.get(cell), hours_per_day)
        continue
    if cell is None or cell == '':
        continue
    if is_numeric(cell):
        actual_hours += Decimal(str(cell))
        shift_days_worked += 1
    else:
        policy = attendance_policies[cell]   # KeyError impossible — prefetch validated all codes
        hours = resolve_hours(cell, policy, hours_per_day)
        if policy['counts_as_paid']:
            paid_hours_accumulator += hours
        if policy['eligible_for_shift_allowance']:
            shift_days_worked += 1
```

Phase 2 (post-accumulation):
```python
total_hours_accumulated = actual_hours + paid_hours_accumulator
excess_OT1 = max(Decimal('0'), total_hours_accumulated - expected_hours)
total_hours_paid = total_hours_accumulated - excess_OT1
proration_factor = (total_hours_paid / expected_hours).quantize(Decimal('0.0001'))

if excess_OT1 > 0:
    ot_buckets[OT1_rate_code] += excess_OT1
```

Rate codes resolved from workspace `ot_trigger_config` — NOT hardcoded. Client B's OT1/OT2/OT3 map to platform codes OT001/OT002/OT003.

**TM-3-AC-9 — Prefetch validation before derivation loop**
**Given** the orchestrator service has loaded all policy rows from DB  
**When** derivation is triggered for an employee  
**Then** the service validates ALL codes in the employee's attendance grid have a policy row AND any non-WORK code has at least one of `hours_equivalent` or `unit_fraction` set; if any code fails this check → `derivation_status = 'FAILED'` with a message listing the failing codes; no `payroll_input` rows are written for that employee

**TM-3-AC-10 — OT output rows**
**When** derivation completes  
**Then** one `payroll_input` dict is produced per OT rate code with hours > 0:  
`{source: 'TIMESHEET', input_category: 'EARNING', rate_code: <from registry>, quantity: <Decimal hours>}`

**TM-3-AC-11 — Shift allowance row**
**When** derivation completes  
**Then** one `payroll_input` dict is produced:  
`{source: 'TIMESHEET', input_code: 'shift_days_worked', input_category: 'EARNING', quantity: shift_days_worked}`  
*(AC-8: existing `ot_multiplier` handler on `basic_daily` rate code computes the allowance; no executor changes)*

**TM-3-AC-12 — `shift_type IS NULL` is a hard error**
**Given** an employee with `shift_type IS NULL`  
**When** derivation is triggered  
**Then** `derivation_status = 'FAILED'`; reason stored: "shift_type is not configured — update the employee record"; no silent fallback

**TM-3-AC-13 — S.DAY treated as DAY unless overridden**
**Given** an employee with `shift_type = 'S.DAY'`  
**When** no workspace config override is found for S.DAY  
**Then** S.DAY is treated as DAY (8h/day, 0% shift allowance); the derivation response includes a warning listing S.DAY employees with no override configured

**TM-3-AC-14 — FAILED status is observable**
**Given** a derivation that fails (policy gap, shift_type NULL, hours not configured, etc.)  
**When** the operator views the Timesheet Status UI  
**Then** `derivation_status = 'FAILED'` is shown with the stored reason; the operator knows exactly what to fix before re-triggering derivation

**TM-3-AC-15 — Policy snapshot written at derivation time**
**When** derivation completes successfully for an employee  
**Then** `timesheet_entry.policy_snapshot_jsonb` is written with the exact policy values used for each code:  
`{code: {counts_as_paid, counts_towards_ot_threshold, hours_equivalent, unit_fraction}}` per code  
This snapshot is immutable once written; subsequent operator changes to `attendance_policy_config` do not retroactively alter it

**TM-3-AC-16 — Derivation status transitions**
**When** derivation runs  
**Then** status transitions follow: `PENDING → DERIVED` (success) or `PENDING → FAILED` (error); `APPROVED` is set only by the approval step (TM-5), not by derivation; `FAILED` employees must be corrected and re-derived before approval is possible

**TM-3-AC-17 — Re-derivation scope**
**When** a timesheet is re-uploaded and re-derived for a period where `payroll_input` rows already exist  
**Then** only rows with `source = 'TIMESHEET' AND payroll_run_id IS NULL` are deleted before re-insertion; `MANUAL_OT` and `INPUT_FILE` rows for the same employee/period are untouched (M1, AC-6)

**TM-3-AC-18 — Client B three-employee worked example**
**Given** the Client B test period (Jan 21 – Feb 20, 4-SHIFT, `expected_days = 19`, `expected_hours = 152h`, PH = Thu 29 Jan)  
**When** derivation runs for all three employees in `docs/data/Client B/test sample timesheet-with result.xlsx`  
**Then** each employee's gross pay matches the client spreadsheet exactly (verified 2026-05-12)

---

### TM-4 — Manual OT override

**TM-4-AC-1 — Stored separately from auto-derived OT**
**Given** a manual OT override entry  
**When** it is written  
**Then** it is stored as `source = 'MANUAL_OT'`; both auto-derived (`TIMESHEET`) and manual rows are visible in the audit trail

**TM-4-AC-2 — Positive and negative overrides accepted**
**Given** an operator entering a manual override  
**When** the quantity is negative (correction)  
**Then** it is stored and applied; net effective hours cannot go below zero at the run level

**TM-4-AC-3 — Locked after APPROVED**
**Given** a payroll run that has reached `APPROVED` status  
**When** a manual override entry is attempted  
**Then** the API returns `409`; the override is not stored

**TM-4-AC-4 — Re-derivation does not delete MANUAL_OT rows**
**Given** an existing `MANUAL_OT` row for an employee/period  
**When** the timesheet is re-derived for that period  
**Then** the `MANUAL_OT` row is untouched; only `TIMESHEET` rows are replaced (AC-6)

---

### TM-5 — Timesheet-to-pay-instruction flow

**TM-5-AC-1 — Atomic approval write**
**When** the operator approves a timesheet period  
**Then** all employees' `payroll_input` rows are written in a single DB transaction; partial states cannot exist (AC-4); `timesheet_entry.policy_snapshot_jsonb` is included in the data written at this point

**TM-5-AC-2 — Approval sets status**
**When** the atomic write commits  
**Then** `timesheet_entry.derivation_status = 'APPROVED'`; `APPROVED` is immutable once the run is `SUBMITTED`

**TM-5-AC-3 — source carried through load and retry paths**
**When** `load_inputs_for_run()` and both retry paths in `payroll_retry_service.py` (lines 504, 806) execute  
**Then** the `source` column is included in the returned rows so executor and audit trail can distinguish provenance (M2)

**TM-5-AC-4 — Executor hire proration suppressed for timesheet employees**
**Given** an employee whose `payroll_input` rows carry `source = 'TIMESHEET'`  
**When** the executor runs  
**Then** `contract_start = None / contract_end = None` is passed; the executor's hire-date proration block is suppressed; derivation service is the sole proration mechanism (AC-5)

**TM-5-AC-5 — `expected_hours` resolved per employee**
**Given** a workspace with mixed shift types (e.g. DAY 8h/day and 4-SHIFT 12h/day)  
**When** `expected_hours` is computed for each employee  
**Then** it is derived from `shift_type → hours_per_day_by_shift_type` config in `workspace_payroll_config` as `Decimal` — not a single workspace scalar applied to all employees (C1)

**TM-5-AC-6 — Unique index updated**
**Given** a `TIMESHEET` row and a `MANUAL` row both with `(workspace_id, emp_id, OT001, 2026-05-15)`  
**When** both are written  
**Then** no unique constraint violation occurs; `uq_payroll_input_unclaimed` now includes `source` in its column set (H2)

**TM-5-AC-7 — Readiness gate blocks incomplete derivation**
**Given** any employee for the workspace/period with `derivation_status ≠ 'APPROVED'`  
**When** `link_inputs_to_run()` is called  
**Then** `payroll_readiness_service` blocks it with a readable error listing the non-approved employees (C2, AC-9)

**TM-5-AC-8 — State machine sequence enforced**
Timesheet approval → run `SUBMITTED` → run `APPROVED` → run `PAID`.  
A run cannot reach `SUBMITTED` unless all employees' timesheet derivation is `APPROVED`.

---

### TM-6 — Timesheet audit trail

**TM-6-AC-1 — Per-employee derivation summary queryable**
**Given** a completed derivation  
**When** the audit trail API is queried  
**Then** the response includes: `expected_hours`, `actual_hours`, `paid_hours_accumulator`, `excess_OT1_hours`, `total_hours_paid`, `proration_factor`, OT hours breakdown per rate code

**TM-6-AC-2 — Auto-derived vs manual OT separated**
**Given** both `TIMESHEET` and `MANUAL_OT` rows exist for an employee  
**When** the audit trail is viewed  
**Then** both are shown with their `source` label; they are not summed together silently

**TM-6-AC-3 — Per-day attendance codes retrievable**
**Given** a stored `timesheet_entry`  
**When** the audit trail is queried  
**Then** the daily attendance grid (date → code or hours) is accessible; aggregates alone are not sufficient

**TM-6-AC-4 — PH calendar recorded**
**Given** a derivation that applied a PH calendar  
**When** the audit trail is queried  
**Then** the specific PH dates active during derivation are stored alongside the result (not just the workspace PH config ID)

**TM-6-AC-5 — Policy snapshot queryable**
**Given** a completed derivation  
**When** the audit trail is queried  
**Then** `policy_snapshot_jsonb` is returned, showing exactly which `counts_as_paid`, `hours_equivalent`, and `unit_fraction` values were used for each attendance code at derivation time — independent of any subsequent operator changes to `attendance_policy_config`

---

### TM-7 — Attendance code and policy workspace configuration

**TM-7-AC-1 — Platform codes visible after workspace is timesheet-enabled**
**Given** a workspace that has just been timesheet-enabled (TM-1-AC-6)  
**When** the operator opens Attendance Configuration  
**Then** all v1 platform template codes (L, SLA, SLD, SLN, P, M, C) are listed with their seeded default policy values; no manual entry is required to start with the standard set

**TM-7-AC-2 — Policy values visible for each code**
**Given** a timesheet-enabled workspace  
**When** the operator views the Attendance Configuration list  
**Then** each code shows: `client_code`, `description`, `category`, `is_active`, `counts_as_paid`, `counts_towards_ot_threshold`, `hours_equivalent`, `unit_fraction`, `eligible_for_shift_allowance`, and any configuration warnings (orphan, hours not set)

**TM-7-AC-3 — Operator can update a policy**
**Given** an existing attendance code with a configured policy  
**When** the operator changes `hours_equivalent`, `unit_fraction`, `counts_as_paid`, `counts_towards_ot_threshold`, or `eligible_for_shift_allowance`  
**Then** the `attendance_policy_config` row is updated; `updated_at` is refreshed; the change is visible immediately; the change does NOT retroactively alter existing `policy_snapshot_jsonb` on already-derived timesheets

**TM-7-AC-4 — category is immutable**
**Given** an existing attendance code  
**When** the operator attempts to change `category` via the API  
**Then** the API returns `400`: "attendance code category is immutable after creation — disable this code and create a new one if the category is wrong"

**TM-7-AC-5 — Operator can add a workspace-specific code**
**Given** a code not yet in the workspace  
**When** the operator creates a new code supplying both code/semantic fields and policy fields in the same request  
**Then** both `attendance_code_config` and `attendance_policy_config` rows are created atomically; creating a code without policy fields is rejected `400`: "policy fields are required when creating an attendance code"

**TM-7-AC-6 — Operator can disable a code**
**Given** an active attendance code  
**When** the operator sets `is_active = FALSE`  
**Then** subsequent uploads containing that code receive a per-cell warning (TM-2-AC-3c); existing `timesheet_entry` rows referencing it are unaffected; re-enabling is possible; the code cannot be deleted if any `timesheet_entry` row references it

**TM-7-AC-7 — Orphaned codes flagged in UI**
**Given** a code in `attendance_code_config` with no corresponding `attendance_policy_config` row  
**When** the operator views Attendance Configuration  
**Then** the code is shown with a "Policy not configured" warning badge; the operator cannot trigger derivation while orphaned codes exist in the workspace configuration

**TM-7-AC-8 — Hours-not-configured warning**
**Given** a non-WORK code (category = LEAVE / OT / SHIFT) with both `hours_equivalent = NULL` and `unit_fraction = NULL`  
**When** the operator views Attendance Configuration  
**Then** the code is shown with a "Hours not configured — derivation will fail for this code" warning badge; this does not block upload but will cause `FAILED` derivation status

**TM-7-AC-9 — Invalid policy combination rejected**
**Given** an operator attempting to set `counts_as_paid = FALSE` and `counts_towards_ot_threshold = TRUE` on the same code  
**When** the request is submitted  
**Then** the API returns `400`: "unpaid hours cannot count toward the OT threshold — this combination is not permitted"

**TM-7-AC-10 — Workspace ownership enforced**
**Given** any request to the attendance code or policy endpoints  
**When** the `workspace_id` in the JWT does not match the `wid` path parameter  
**Then** the API returns `403`; no DB operation is performed

**TM-7-AC-11 — Default values for standard codes**  
Platform template v1 seeds the following defaults. Operators may override any field except `category`:

| Code | Category | counts_as_paid | counts_towards_ot | hours_equivalent | unit_fraction |
|------|----------|----------------|-------------------|-----------------|---------------|
| L    | LEAVE    | TRUE           | TRUE              | NULL            | 1.0           |
| SLA  | LEAVE    | TRUE           | TRUE              | 6.50            | NULL          |
| SLD  | LEAVE    | TRUE           | TRUE              | 8.00            | NULL          |
| SLN  | LEAVE    | TRUE           | TRUE              | 11.00           | NULL          |
| P    | LEAVE    | TRUE           | TRUE              | 8.00            | NULL          |
| M    | LEAVE    | TRUE           | TRUE              | 8.00            | NULL          |
| C    | LEAVE    | TRUE           | TRUE              | 8.00            | NULL          |

Numeric cells are WORK-category and have no code row — they always use face value via `is_numeric()` check.

---

## `derivation_status` Enum — All Values

| Value | Meaning | Set by |
|-------|---------|--------|
| `PENDING` | Uploaded; derivation not yet run | Upload |
| `DERIVED` | Derivation complete; awaiting approval | Derivation service (success) |
| `APPROVED` | Approved; `payroll_input` rows written | Approval step (TM-5) |
| `FAILED` | Derivation failed; reason stored | Derivation service (error) |

Re-upload replaces `timesheet_entry` rows entirely, resetting to `PENDING`. There are no stale `DERIVED` rows — old rows are deleted and new `PENDING` rows inserted on re-upload.

---

## Canonical Timesheet Upload Format (AC-10)

Version: `1.0`  
This schema is version-controlled here. The Sprint 16 upload parser must validate against it before derivation.

### Sheet structure

| Section | Columns | Notes |
|---------|---------|-------|
| Employee identifier | 1 column: `employee_number` | Exact match against `employee.employee_number`; no fuzzy matching |
| Shift type | 1 column: `shift_type` | Must match `employee.shift_type` in DB; mismatch → warning |
| Daily attendance grid | One column per calendar day in period | Column header format: `YYYY-MM-DD`; PH days flagged with `*` suffix e.g. `2026-01-29*` |
| Pre-aggregated columns | Any columns after the daily grid | Ignored by parser; may be present (client Excel formulas) |

### Attendance codes — workspace-configurable

Attendance codes and their pay interpretation are stored in two workspace-scoped tables: `attendance_code_config` (semantic registry) and `attendance_policy_config` (pay interpretation). Platform template v1 seeds standard codes into every timesheet-enabled workspace at setup time. Operators configure or override policies via Attendance Configuration (TM-7).

The table below documents the v1 default codes:

| Code | Category | Meaning | Default hours |
|------|----------|---------|---------------|
| Numeric | WORK | Hours worked | Face value (`is_numeric()`) |
| `L` | LEAVE | Annual Leave (paid) | `unit_fraction = 1.0` × `hours_per_day` for shift type |
| `SLA` | LEAVE | Sick Leave — Partial day | 6.5h (`hours_equivalent`) |
| `SLD` | LEAVE | Sick Leave — Full day | 8h (`hours_equivalent`) |
| `SLN` | LEAVE | Sick Leave — Night | 11h (`hours_equivalent`) |
| `P` | LEAVE | Paternity Leave | 8h (`hours_equivalent`) |
| `M` | LEAVE | Maternity Leave | 8h (`hours_equivalent`) |
| `C` | LEAVE | Compassionate Leave | 8h (`hours_equivalent`) |
| Blank | — | Non-working day (not tracked) | 0h — not an error |

Any code not in `attendance_code_config` for the workspace → row-level rejection with cell reference.

### Validation rules

1. `employee_number` column must be present and non-empty for every row
2. Unknown attendance codes → row rejection with cell reference (e.g. `D14: unknown code 'XYZ'`)
3. Known code with no policy row → warning in response; row stored at `PENDING`
4. Known code with `is_active = FALSE` → warning in response; row stored at `PENDING`
5. PH column header dates validated against workspace PH config → warning if mismatch (not rejection)
6. Numeric values must be `≥ 0` and `≤ 24` → rejection if out of range
7. Duplicate `employee_number` in same upload → rejection with row reference
8. `shift_type IS NULL` for any employee → row rejection; operator must fix employee record and re-upload (OQ-3)
9. No salary definition found for employee → warning in response; row stored at `PENDING`; operator decides next action (OQ-4)

---

## Out of Scope

| Item | Reason |
|------|--------|
| Executor changes for new OT/pay types | Derivation service produces `payroll_input` rows in the existing format; executor is unchanged |
| New pay-instruction table | `payroll_input` IS the canonical model (AC-1) |
| Attendance policy configuration via onboarding file | Excel "Attendance Policies" sheet and JSON `attendance_policies` section are deferred to a future sprint; post-onboarding configuration via TM-7 covers Sprint 16 |
| Template drift propagation admin endpoint | Admin `POST /admin/attendance-templates/propagate` is deferred; UI warning (TM-1-AC-7) covers the Sprint 16 case |
| Retroactive re-derivation for approved runs | Runs are immutable once `APPROVED`; operators must correct via a new run |
| 3-SHIFT shift type allowance % | Not confirmed for any current employee (OQ-2); treated as DAY until a workspace config entry is added |
| Fuzzy employee matching in upload | Exact `employee_number` match only; operator corrects upstream data if mismatch |
| Real-time timesheet entry (per-day UI) | Upload-based batch model; per-day entry is a future enhancement |

---

## Business Risk

| | |
|---|---|
| **Cost of NOT doing** | Client B is running payroll in a manual spreadsheet. Every period, OT calculations are done by hand with no audit trail. Platform cannot onboard any timesheet-based client without this layer. |
| **Cost of doing wrong** | Incorrect `proration_factor` (uncapped formula) inflates all salary components by ₦10–13K per OT worker per period. PAYE, pension, and NHF are computed on the inflated gross, compounding the error downstream. The executor produces `SUCCESS` with no indication anything is wrong. |
| **Blocked by this** | Client B live payroll on platform. Any other variable-pay client onboarding. |

---

## Implementation Notes (from arch-council + plan)

### Critical pre-conditions (must be done before timesheet routes are live)

**C1 — `expected_hours` per-employee fix**  
Location: `backend/api/routes/payroll.py` line 594 — `expected_hours = expected_working_days * 8`  
Fix: resolve per-employee from `shift_type → hours_per_day_by_shift_type` config in `workspace_payroll_config` as `Decimal`; pass into `emp_context` before `_run_sequential` is called. This is a live production bug for any mixed-shift workspace running `ot_multiplier` rules today.

**C2 — Timesheet completeness gate in `payroll_readiness_service.py`**  
Add check: if workspace is timesheet-enabled, all employees for the period must have `timesheet_entry.derivation_status = 'APPROVED'` before `link_inputs_to_run` is permitted. Returns readable error listing non-approved employees.

### Files to touch (confirmed post-arch-council + attendance config revision)

| File | Change | Decision |
|------|--------|----------|
| `backend/infra/db/models/attendance.py` | **NEW** — `AttendanceCodeConfig` + `AttendancePolicyConfig` SQLAlchemy models | Attendance revision |
| `backend/infra/db/models/platform_templates.py` | **NEW** — `PlatformAttendanceCodeTemplate` + `PlatformAttendancePolicyTemplate` + `PlatformAttendanceTemplateVersion` | Attendance revision |
| `backend/infra/db/models/timesheet.py` | **NEW** — `TimesheetEntry` model with `derivation_status` state machine + `policy_snapshot_jsonb` | AC-4, AC-9, TM-3-AC-15 |
| `backend/infra/repositories/attendance_config_repo.py` | **NEW** — load both tables for derivation; `WHERE workspace_id = :wid` on every query | Attendance revision |
| `backend/infra/repositories/timesheet_repo.py` | **NEW** — CRUD + scoped delete | M1, AC-6 |
| `backend/infra/repositories/payroll_input_repo.py` | Scoped delete: `WHERE source = 'TIMESHEET' AND payroll_run_id IS NULL` | M1, AC-6 |
| `backend/infra/repositories/workspace_config_repo.py` | Add `timesheet_enabled` to upsert fn + `_DEFAULTS`; update all call sites | AC-2, M3 |
| `backend/infra/repositories/` (load_inputs_for_run + retry) | Extend `load_inputs_for_run()` + retry paths (lines 504, 806) to return `source` | M2 |
| `backend/domain/payroll/timesheet_derivation.py` | **NEW** — pure domain fn; two-dict interface; `resolve_hours()`; all `Decimal`; no infra imports | AC-3, TM-3-AC-7 |
| `backend/application/timesheet_derivation_service.py` | **NEW** — orchestrator; prefetch + orphan check; atomic write; policy snapshot | AC-3, AC-4, TM-3-AC-9 |
| `backend/application/payroll_readiness_service.py` | Add timesheet completeness gate before `link_inputs_to_run` | C2, AC-9 |
| `backend/api/routes/payroll.py` | Timesheet upload endpoint; derivation trigger; approval endpoint; fix `expected_hours` to per-employee | C1, AC-10 |
| `backend/api/routes/workspace.py` | Attendance code + policy CRUD endpoints; `category` immutability guard; JWT workspace ownership check | TM-7 |
| `backend/domain/payroll/sequential_executor.py` | Suppress hire-date proration for `source='TIMESHEET'`; consume per-employee `expected_hours` as `Decimal` | AC-5, C1 |
| `migrations/versions/` | 5 migrations — see below | All |
| `frontend/src/pages/` | TimesheetUpload page; WorkspaceConfig timesheet toggle + template version warning; AttendanceConfiguration page | AC-2, AC-10, TM-7 |
| `frontend/src/api/payroll.ts` | Timesheet upload + derivation + approval API calls; attendance config CRUD | AC-4, AC-9, TM-7 |

### Migration list (5 migrations, ordered)

| Migration | Content | Constraints |
|-----------|---------|-------------|
| **MIG-A** | `timesheet_entry` table + `derivation_status` enum (`PENDING`, `DERIVED`, `APPROVED`, `FAILED`) + `policy_snapshot_jsonb JSONB` | Enum guard; ADD COLUMN guard; working downgrade |
| **MIG-B** | `workspace_payroll_config.timesheet_enabled BOOLEAN NOT NULL DEFAULT FALSE` + `workspace.attendance_template_version VARCHAR(10)` | ADD COLUMN guard; upsert fn + `_DEFAULTS` + all call sites; migration before code deploy |
| **MIG-C** | Update `uq_payroll_input_unclaimed` to include `source` | **Standalone migration file** — `AUTOCOMMIT` isolation required; `CREATE INDEX CONCURRENTLY` cannot run inside a transaction |
| **MIG-D** | `platform_attendance_template_version` + `platform_attendance_code_template` + `platform_attendance_policy_template` tables + v1 seed data | FK ordering: version table → code template → policy template |
| **MIG-E** | `attendance_code_config` + `attendance_policy_config` + composite index on policy table | `attendance_code_config` before `attendance_policy_config` (FK dependency); CHECK constraints as specified; ADD COLUMN guard |

Migration ordering: MIG-D before MIG-E. MIG-B before code deploy. MIG-C is standalone.  
Duplicate revision ID check before writing any migration: `grep -h "^revision" migrations/versions/*.py | sort | uniq -d`

### Domain layer constraints

- `timesheet_derivation.py` must NEVER import from `backend/infra/`
- Rate codes resolved from workspace `ot_trigger_config` dict — not hardcoded
- Attendance code behaviour resolved from `attendance_policies` dict — not hardcoded code lists
- All hours, rates, fractions use `Decimal` — no `float` anywhere in the derivation domain
- `classify_day()` stub at `rule_evaluator.py` lines 725–749 exists but has zero callers — do NOT use it from the domain layer; implement inline in `timesheet_derivation.py` per AC-3

---

## Open Questions — Resolved

| # | Question | Resolution |
|---|----------|------------|
| OQ-1 | What employee identifier appears in the timesheet Excel? | `employee_number` — exact match against `employee.employee_number` |
| OQ-2 | Does the 3-SHIFT type exist for any current employee? | Not confirmed; treated as DAY until workspace config entry added (out of scope) |
| OQ-3 | Employees with `shift_type = NULL`? | Hard row rejection in upload response; operator must fix employee record and re-upload |
| OQ-4 | Employee with no salary definition? | Warning in upload response; row stored at `PENDING`; operator decides |
| OQ-5 | Is Maternity (M) same hours as Paternity (P)? | Yes — both 8h (`hours_equivalent = 8.00` in v1 template) |
| OQ-6 | Are platform template codes workspace-specific or global? | Platform-wide defaults — all timesheet-enabled workspaces receive v1 codes; Client B uses defaults unchanged |
| OQ-7 | What are the defaults for `counts_as_paid` and `counts_towards_ot_threshold`? | Both `NOT NULL DEFAULT TRUE`; always set for any seeded code; the risk field is `hours_equivalent`/`unit_fraction` which can be NULL for leave codes — derivation fails (FAILED status) if both are NULL for a non-WORK code |
| OQ-8 | What happens at runtime if a policy field is not configured? | `counts_as_paid`/`counts_towards_ot_threshold` always have values (NOT NULL). For `hours_equivalent`/`unit_fraction`: at upload → warning in response; at derivation prefetch → FAILED status with code list; in UI → "Hours not configured" badge on that code |
