# Sprint 16 — Timesheet Layer Implementation

**Track:** O (Timesheet / Variable-Pay Clients) — closes NEW-GAP1 / O6  
**Priority:** P1 — compliance and client delivery obligation; Client B cannot run payroll on the platform without this  
**Effort:** XL (6 stories, 4 migrations, 2 new service files, frontend)  
**Arch-council:** ✅ APPROVED (2026-05-12) — 10 binding decisions (AC-1 through AC-10) + 2 critical fixes (C1, C2) + 4 high-priority pre-conditions (H1–H4) — all resolved in Sprint 15  
**Plan file:** `~/.claude/plans/splendid-gliding-sun.md`

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

---

### TM-2 — Timesheet upload

**TM-2-AC-1 — Raw grid only accepted**
**Given** a timesheet Excel file  
**When** it is uploaded  
**Then** the parser extracts raw daily cells only; pre-aggregated formula columns are silently ignored

**TM-2-AC-2 — Employee matching**
**Given** a row in the uploaded file  
**When** the parser reads the employee identifier column  
**Then** it is matched against `employee.staff_id` exactly; fuzzy matching is not performed; unmatched employees → row-level rejection

**TM-2-AC-3 — Unknown attendance codes rejected at row level**
**Given** a cell containing a code not in the workspace attendance code config table  
**When** the upload is processed  
**Then** the row is rejected with cell reference (e.g. `D14: unknown code 'XYZ'`); valid rows in the same upload are still stored

**TM-2-AC-4 — PH column headers validated**
**Given** PH-flagged column headers in the uploaded file  
**When** the upload is processed  
**Then** each flagged date is validated against the workspace public holiday config; mismatches → warning in upload response (not rejection)

**TM-2-AC-5 — Duplicate upload replaces timesheet rows only**
**Given** a prior upload exists for the same `(workspace_id, period)`  
**When** a new upload is submitted  
**Then** previous `timesheet_entry` rows for the period are replaced; `payroll_input` rows are NOT touched (those are written on approval, per AC-4)

**TM-2-AC-6 — Upload response**
**When** any upload completes  
**Then** the response includes: employees found, rows accepted, rows rejected (with per-row error detail)

**TM-2-AC-7 — Upload sets derivation status**
**When** an employee's rows are accepted  
**Then** `timesheet_entry.derivation_status = 'PENDING'`

---

### TM-3 — Timesheet derivation pipeline

**TM-3-AC-1 — Pure domain function**
**Given** raw attendance grid dict, attendance code config, OT trigger rule config, PH date set, rate code map, shift type, and employee contract window  
**When** `timesheet_derivation.py` domain function is called  
**Then** it returns a list of `payroll_input` dicts and a `DerivationSummary` struct without any DB access

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
**Given** an employee with sick leave (SLA/SLD/SLN) or annual leave (L) or paternity/maternity (P/M/C) codes in their grid  
**When** derivation runs  
**Then** those hours are included in `total_hours_accumulated` on equal footing with actual work hours  
*(they contribute to whether the OT1 threshold is breached)*

**TM-3-AC-5 — Three-step cap formula (mandatory)**
**When** derivation computes base-pay hours  
**Then** the three-step derivation is applied exactly:
```
step 1:  total_hours_accumulated = actual_hours + sick_leave_hours + leave_hours + patmat_hours
         [does NOT include PH hours]
step 2:  excess_OT1_hours = MAX(0, total_hours_accumulated − expected_hours)
step 3:  total_hours_paid = total_hours_accumulated − excess_OT1_hours
         [= MIN(accumulated, expected_hours); always ≤ expected_hours]
         proration_factor = total_hours_paid / expected_hours  [always ≤ 1.0]
```
Rationale: base salary is paid for up to `expected_hours` only. Hours above that are compensated as OT at the applicable multiplier. Uncapped `total_hours_accumulated` in the proration numerator inflates all salary components — verified to produce ~₦10–13K overpayment per employee per period on Client B test data.

**TM-3-AC-6 — Full-period employee proration factor = 1.0**
**Given** an employee who works a complete period with no absences  
**When** derivation runs  
**Then** `proration_factor = 1.0`; no reduction is applied to salary components

**TM-3-AC-7 — OT classification precedence (H3 pseudocode)**

Day classification algorithm — `classify_day(date, shift_type, ph_date_set) → DayType`:

```python
def classify_day(date, shift_type, ph_date_set):
    # Precedence: PUBLIC_HOLIDAY > SATURDAY (DAY shift only) > WEEKDAY
    if date in ph_date_set:
        return DayType.PUBLIC_HOLIDAY
    if date.weekday() == 5:  # Saturday
        if shift_type == 'DAY':
            return DayType.SATURDAY_DAY_SHIFT  # → OT2 bucket
        else:
            # Rotating shifts (4-SHIFT, 2-SHIFT): Saturday is a normal
            # accumulation day — does NOT go to OT2; contributes to OT1 threshold
            return DayType.WEEKDAY
    return DayType.WEEKDAY
```

Per-day derivation loop — Phase 1 (iterates attendance grid by calendar day):
```python
for day in calendar_days_in_period:
    day_type = classify_day(day, employee.shift_type, ph_date_set)
    cell = attendance_grid.get(day)

    if day_type == DayType.PUBLIC_HOLIDAY:
        # Hours worked on PH → OT3 bucket directly; skip accumulation
        ot_buckets[OT3_rate_code] += resolve_hours(cell, attendance_code_config)
        continue

    if day_type == DayType.SATURDAY_DAY_SHIFT:
        # DAY shift Saturday hours → OT2 bucket directly; skip accumulation
        ot_buckets[OT2_rate_code] += resolve_hours(cell, attendance_code_config)
        continue

    # All other days (incl. Saturday for rotating shifts) — accumulate by code type
    if cell is None or cell == '':
        continue  # non-working day, not tracked
    if is_numeric(cell):
        actual_hours += float(cell)
        shift_days_worked += 1
    elif cell in sick_codes:           # SLA, SLD, SLN
        sick_leave_hours += attendance_code_config[cell]['hours_equivalent']
    elif cell in leave_codes:          # L
        annual_leave_hours += attendance_code_config[cell]['hours_equivalent']
    elif cell in patmat_codes:         # M, P, C
        patmat_hours += attendance_code_config[cell]['hours_equivalent']
    else:
        raise UnknownAttendanceCode(cell, day)
```

Phase 2 (post-accumulation — three-step formula + OT emission):
```python
total_hours_accumulated = actual_hours + sick_leave_hours + annual_leave_hours + patmat_hours
# PH hours already in ot_buckets[OT3_rate_code] — not included here

excess_OT1_hours = max(0, total_hours_accumulated - expected_hours)
total_hours_paid = total_hours_accumulated - excess_OT1_hours  # ≤ expected_hours always
proration_factor = total_hours_paid / expected_hours            # ≤ 1.0 always

if excess_OT1_hours > 0:
    ot_buckets[OT1_rate_code] += excess_OT1_hours  # via workspace EXCESS_HOURS trigger rule
```

Rate codes are resolved from workspace `ot_trigger_config`, NOT hardcoded. Client B's OT1/OT2/OT3 are their internal labels mapped at onboarding to platform codes OT001/OT002/OT003.

**TM-3-AC-8 — OT output rows**
**When** derivation completes  
**Then** one `payroll_input` dict is produced per OT rate code with hours > 0:  
`{source: 'TIMESHEET', input_category: 'EARNING', rate_code: <from registry>, quantity: <hours>}`

**TM-3-AC-9 — Shift allowance row**
**When** derivation completes  
**Then** one `payroll_input` dict is produced:  
`{source: 'TIMESHEET', input_code: 'shift_days_worked', input_category: 'EARNING', quantity: shift_days_worked}`  
*(AC-8: existing `ot_multiplier` handler on `basic_daily` rate code computes the allowance; no executor changes)*

**TM-3-AC-10 — `shift_type IS NULL` is a hard error**
**Given** an employee with `shift_type IS NULL`  
**When** derivation is triggered for that employee  
**Then** derivation is rejected with a hard error returned to the operator before any rows are written; no silent fallback

**TM-3-AC-11 — S.DAY treated as DAY unless overridden**
**Given** an employee with `shift_type = 'S.DAY'`  
**When** no workspace config override is found for S.DAY  
**Then** S.DAY is treated as DAY (8h/day, 0% shift allowance) and the operator receives a warning in the derivation response listing S.DAY employees with no override configured

**TM-3-AC-12 — Derivation status set**
**When** derivation completes for an employee  
**Then** `timesheet_entry.derivation_status = 'DERIVED'`

**TM-3-AC-13 — Re-derivation scope**
**When** a timesheet is re-uploaded and re-derived for a period where `payroll_input` rows already exist  
**Then** only rows with `source = 'TIMESHEET' AND payroll_run_id IS NULL` are deleted before re-insertion; `MANUAL_OT` and `INPUT_FILE` rows for the same employee/period are untouched (M1, AC-6)

**TM-3-AC-14 — Client B three-employee worked example**
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
**Then** all employees' `payroll_input` rows are written in a single DB transaction; partial states cannot exist (AC-4)

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
**Then** it is derived from `shift_type → hours_per_day_by_shift_type` config in `workspace_payroll_config` — not a single workspace scalar applied to all employees (C1)

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
**Then** the response includes: `expected_hours`, `actual_hours`, `sick_leave_hours`, `leave_hours`, `patmat_hours`, `excess_OT1_hours`, `total_hours_paid`, `proration_factor`, OT hours breakdown per rate code

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

---

## Canonical Timesheet Upload Format (AC-10)

Version: `1.0`  
This schema is version-controlled here. The Sprint 16 upload parser must validate against it before derivation.

### Sheet structure

| Section | Columns | Notes |
|---------|---------|-------|
| Employee identifier | 1 column: `staff_id` | Exact match against `employee.staff_id`; no fuzzy matching |
| Shift type | 1 column: `shift_type` | Must match `employee.shift_type` in DB; mismatch → warning |
| Daily attendance grid | One column per calendar day in period | Column header format: `YYYY-MM-DD`; PH days flagged with `*` suffix e.g. `2026-01-29*` |
| Pre-aggregated columns | Any columns after the daily grid | Ignored by parser; may be present (client Excel formulas) |

### Supported attendance codes (platform defaults — workspace config may override)

| Code | Meaning | Hours counted |
|------|---------|---------------|
| Numeric | Hours worked | Face value |
| `L` | Annual Leave (paid) | `hours_per_day` for shift type |
| `SLA` | Sick Leave — Partial day | 6.5h |
| `SLD` | Sick Leave — Full day | 8h |
| `SLN` | Sick Leave — Night | 11h |
| `P` | Paternity Leave | 8h |
| `M` | Maternity Leave | 8h |
| `C` | Compassionate Leave | 8h |
| Blank | Non-working day (not tracked) | 0h (not an error) |

Any code not in this table and not in the workspace attendance code config → row-level rejection with cell reference.

### Validation rules

1. `staff_id` column must be present and non-empty for every row
2. Unknown attendance codes → row rejection with cell reference (e.g. `D14: unknown code 'XYZ'`)
3. PH column header dates validated against workspace PH config → warning if mismatch (not rejection)
4. Numeric values must be `≥ 0` and `≤ 24` → rejection if out of range
5. Duplicate `staff_id` in same upload → rejection with row reference

---

## Out of Scope

| Item | Reason |
|------|--------|
| Executor changes for new OT/pay types | Derivation service produces `payroll_input` rows in the existing format; executor is unchanged |
| New pay-instruction table | `payroll_input` IS the canonical model (AC-1) |
| Global attendance code defaults (cross-workspace) | Workspace config table with `workspace_id IS NULL` partial index covers platform defaults (M4); cross-workspace management UI deferred |
| Retroactive re-derivation for approved runs | Runs are immutable once `APPROVED`; operators must correct via a new run |
| 3-SHIFT shift type allowance % | Not confirmed for any current employee (OQ-2); treated as DAY until a workspace config entry is added |
| Fuzzy employee matching in upload | Exact `staff_id` match only; operator corrects upstream data if mismatch |
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
Fix: resolve per-employee from `shift_type → hours_per_day_by_shift_type` config in `workspace_payroll_config`; pass into `emp_context` before `_run_sequential` is called. This is a live production bug for any mixed-shift workspace running `ot_multiplier` rules today.

**C2 — Timesheet completeness gate in `payroll_readiness_service.py`**  
Add check: if workspace is timesheet-enabled, all employees for the period must have `timesheet_entry.derivation_status = 'APPROVED'` before `link_inputs_to_run` is permitted. Returns readable error listing non-approved employees.

### Files to touch (confirmed post-arch-council)

| File | Change | Arch decision |
|------|--------|---------------|
| `backend/infra/db/models/` | New `TimesheetEntry` model with `derivation_status` state machine (`PENDING → DERIVED → APPROVED`) | AC-4, AC-9 |
| `backend/infra/repositories/timesheet_repo.py` | **NEW** — CRUD + scoped delete | M1, AC-6 |
| `backend/infra/repositories/payroll_input_repo.py` | Scoped delete: `WHERE source = 'TIMESHEET' AND payroll_run_id IS NULL` | M1, AC-6 |
| `backend/infra/repositories/workspace_config_repo.py` | Add `timesheet_enabled` to upsert fn + `_DEFAULTS`; update all call sites | AC-2, M3 |
| `backend/infra/repositories/` (load_inputs_for_run + retry) | Extend `load_inputs_for_run()` + retry paths (lines 504, 806) to return and propagate `source` | M2 |
| `backend/domain/payroll/timesheet_derivation.py` | **NEW** — pure function domain layer; no DB access; takes grid + config dicts → returns `payroll_input` dicts + `DerivationSummary` | AC-3 |
| `backend/application/timesheet_derivation_service.py` | **NEW** — orchestrator; loads config from DB, calls domain fn, writes rows atomically | AC-3, AC-4 |
| `backend/application/payroll_readiness_service.py` | Add timesheet completeness gate before `link_inputs_to_run` | C2, AC-9 |
| `backend/api/routes/payroll.py` | Timesheet upload endpoint; derivation trigger; approval endpoint; fix `expected_hours` to per-employee | C1, AC-10 |
| `backend/domain/payroll/sequential_executor.py` | Suppress hire-date proration for `source='TIMESHEET'` employees; consume per-employee `expected_hours` from `emp_context` | AC-5, C1 |
| `migrations/versions/` | (1) `timesheet_entry` table + `derivation_status` enum; (2) `workspace_payroll_config.timesheet_enabled`; (3) update `uq_payroll_input_unclaimed` to include `source`; (4) attendance code config table with UNIQUE constraint | AC-2, AC-4, H2, M4 |
| `frontend/src/pages/` | TimesheetUpload page; WorkspaceConfig timesheet toggle | AC-2, AC-10 |
| `frontend/src/api/payroll.ts` | Timesheet upload + derivation + approval API calls | AC-4, AC-9 |

### Migration constraints

- All four migrations must be written with ADD COLUMN guards and working downgrades
- `uq_payroll_input_unclaimed` update (H2): `CONCURRENTLY` drop + recreate with `source` included; avoid lock on `payroll_input`
- `derivation_status` enum: use `DO $$ BEGIN CREATE TYPE ... EXCEPTION WHEN duplicate_object THEN NULL; END $$` guard
- Revision IDs: check for duplicates before writing (`grep -h "^revision" migrations/versions/*.py | sort | uniq -d`)

### Domain layer constraints

- `timesheet_derivation.py` must NEVER import from `backend/infra/`
- Rate codes resolved from workspace `ot_trigger_config` dict passed in — not hardcoded
- Attendance code hours resolved from workspace attendance code config dict passed in — not hardcoded
- `classify_day()` stub at `rule_evaluator.py` lines 725–749 exists but has zero callers — do NOT use it from the domain layer; implement the classification inline in `timesheet_derivation.py` per AC-3

---

## Open Questions

| # | Question | When needed |
|---|----------|------------|
| OQ-1 | What employee identifier appears in the timesheet Excel? Does it match `employee.staff_id` exactly? | Before upload parser is written |
| OQ-2 | Does the 3-SHIFT type exist for any current employee? What is its allowance %? | Before derivation config for 3-SHIFT |
| OQ-3 | Are there employees with `shift_type = NULL` who appear in Client B timesheets? | Before go-live; AC-7 requires a hard error |
| OQ-4 | What happens if an employee appears in the timesheet but has no salary definition? Reject or warn? | Before upload validation is written |
| OQ-5 | Is Maternity (M) a distinct code from Paternity (P) in terms of paid hours or is it the same? | Before attendance code config table is seeded |
