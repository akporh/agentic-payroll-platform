# UI Gap Audit — All Sprints

**Date:** 2026-05-14
**Scope:** Sprint 0 through Sprint 16
**Definition:** A feature is UI-accessible only if an operator can discover it, configure or trigger it, and observe its effect — all without DB or API access.

**UI Status values:**
- `not wired` — no UI entry point exists
- `partial` — UI exists but does not cover all operator needs
- `complete` — fully operator-accessible from the UI

---

## Domain: Workspace Setup

### CARD 1 — View Applicable Statutory Rules
```
Domain:          Workspace Setup
Sprint:          Sprint 0
Feature:         View applicable statutory rules
Outcome:         Operator discovers which statutory rules and tax bands apply to their workspace country
Rationale:       Compliance verification; operator must understand tax/pension/levy obligations before first payroll run
UI status:       not wired
Gap description: No GET endpoint for statutory_rule rows; no UI surface to display them. Story exists in user story map (Step 1.3) but marked "Backend-only / Not wired"
API available:   None — no GET /{wid}/statutory-rules endpoint exists
Existing page:   WorkspaceSetup.tsx (could add a Rule Review step) or new Settings → Statutory Rules page
Data the UI must show:   country_code, effective_from, version, paye_band list (lower_limit, upper_limit, rate), pension_employee_rate, nhf_rate
Actions the UI must support: Read-only view; filter by effective_from date; compare versions
SC codes:        SC-TMP-1, SC-GUA-6, SC-DAT-2
Dependencies:    None — read-only view; GET endpoint needed first
```

### CARD 2 — Statutory Rule Management (Bureau Admin)
```
Domain:          Workspace Setup
Sprint:          Deferred (Phase 3)
Feature:         Publish new statutory rule versions with effective dates
Outcome:         Bureau admin updates PAYE bands, NHF or pension rates when statutory rates change annually
Rationale:       PAYE/NHF/pension rates change; bureau needs UI to publish new versions without direct DB access
UI status:       not wired
Gap description: No POST /statutory-rule or versioning UI exists. Only available via raw DB insert or migration script.
API available:   None
Existing page:   New page — StatutoryRules.tsx (admin-only) or Settings → Statutory Rules
Data the UI must show:   country_code, effective_from, version, paye_bands table, pension_rate, nhf_rate, life_insurance_rate
Actions the UI must support: View active rule; view version history; publish new rule with effective_from; soft-delete old version
SC codes:        SC-TMP-1, SC-TMP-3, SC-DAT-2
Dependencies:    Card 1 (view) must exist first
```

### CARD 3 — Update Pay Cycle Post-Setup
```
Domain:          Workspace Setup
Sprint:          Sprint 7 (Track J-37)
Feature:         Update pay cycle after initial onboarding
Outcome:         Operator modifies frequency, run day, or cutoff without re-running full onboarding
Rationale:       Pay schedules change seasonally or by client request; re-onboarding is destructive
UI status:       complete ✅
Gap description: PATCH /{wid}/pay-cycle endpoint (Track J-37) and WorkspaceConfig.tsx EditPayCycle SlideOver both wired (Gate 6).
API available:   ✅ PATCH /{wid}/pay-cycle
Existing page:   ✅ WorkspaceConfig.tsx — EditPayCycle SlideOver
Data the UI must show:   frequency, run_day, cutoff_day, payment_day
Actions the UI must support: Edit and save; validation gate if active runs exist
SC codes:        SC-DAT-1, SC-GUA-6
Dependencies:    None
```

---

## Domain: Workforce Config

### CARD 4 — Add/Edit Grades Post-Onboarding
```
Domain:          Workforce Config
Sprint:          Sprint 7 (Track J-38)
Feature:         Add grade / designation post-onboarding via UI
Outcome:         Operator adds a new salary grade without re-running onboarding
Rationale:       Org structure evolves; new grades may be added mid-year
UI status:       complete ✅
Gap description: POST /{wid}/grade + PATCH /{wid}/grade/{code} endpoints wired; WorkspaceConfig.tsx AddGrade and EditGrade SlideOvers present (Gate 6)
API available:   ✅ POST /{wid}/grade + PATCH /{wid}/grade/{code}
Existing page:   ✅ WorkspaceConfig.tsx
SC codes:        SC-GUA-6
Dependencies:    None
```

### CARD 5 — Edit Salary Definition Components Post-Onboarding
```
Domain:          Workforce Config
Sprint:          Sprint 7 (Track J-39)
Feature:         Edit salary definition components via UI
Outcome:         Operator adjusts BASIC, HOUSING, TRANSPORT amounts without deleting and recreating
Rationale:       Salary structures need fine-tuning post-onboarding; deletion + re-creation is risky
UI status:       complete ✅
Gap description: PATCH /{wid}/salary-definition/{id} endpoint (Track J-39) with edit-lock on PAID runs; WorkspaceConfig.tsx EditSalaryDef SlideOver (Gate 6)
API available:   ✅ PATCH /{wid}/salary-definition/{id}
Existing page:   ✅ WorkspaceConfig.tsx — EditSalaryDef SlideOver
SC codes:        SC-GUA-5, SC-GUA-6
Dependencies:    None
```

### CARD 6 — Toggle Payroll Rule Active/Inactive Post-Onboarding
```
Domain:          Workforce Config
Sprint:          Sprint 7 (Track J-40)
Feature:         Toggle payroll rule active/inactive via UI
Outcome:         Operator disables an earning/deduction rule without deletion
Rationale:       Business rules change; non-destructive enable/disable needed
UI status:       complete ✅
Gap description: PATCH /{wid}/payroll-rule/{id} endpoint (Track J-40); WorkspaceConfig.tsx EditPayrollRule SlideOver (Gate 6)
API available:   ✅ PATCH /{wid}/payroll-rule/{id} + DELETE /{wid}/payroll-rule/{id}
Existing page:   ✅ WorkspaceConfig.tsx — EditPayrollRule SlideOver
SC codes:        SC-GUA-6, SC-ENG-1
Dependencies:    None
```

### CARD 7 — Edit/Toggle Statutory Component Override
```
Domain:          Workforce Config
Sprint:          Sprint 7 (Track J-41)
Feature:         Edit/toggle statutory component override via UI
Outcome:         Operator suppresses statutory deductions or adjusts proration strategy per component
Rationale:       Some workspaces exempt from certain deductions; proration varies by employee category
UI status:       complete ✅
Gap description: PATCH /{wid}/component-override/{code} endpoint (Track J-41); WorkspaceConfig.tsx EditComponentOverride SlideOver (Gate 6); hard reject on statutory_deduction class per D-ARCH-2
API available:   ✅ PATCH /{wid}/component-override/{code}
Existing page:   ✅ WorkspaceConfig.tsx — EditComponentOverride SlideOver
SC codes:        SC-GUA-6, SC-ENG-1
Dependencies:    None
```

### CARD 8 — Define Payroll Rules via Interactive Form
```
Domain:          Workforce Config
Sprint:          Sprint 7 (Track J-36)
Feature:         Define payroll rules via guided form (not raw JSON textarea)
Outcome:         Operator creates earning/deduction rules without pasting raw JSON
Rationale:       Reduces errors; improves discoverability; lowers barrier to entry
UI status:       complete ✅
Gap description: POST /{wid}/payroll-rule + PATCH /{wid}/payroll-rule endpoints; WorkspaceConfig.tsx EditPayrollRule SlideOver has guided form
API available:   ✅ POST /{wid}/payroll-rule + PATCH /{wid}/payroll-rule
Existing page:   ✅ WorkspaceConfig.tsx — EditPayrollRule SlideOver
SC codes:        SC-GUA-6, SC-ENG-1
Dependencies:    None
```

---

## Domain: Pay Events

### CARD 9 — Bulk Payroll Input Upload with Deduplication Guard
```
Domain:          Pay Events
Sprint:          Sprint 1 (partial gap — G11)
Feature:         Bulk upload inputs via Excel with deduplication guard
Outcome:         Operator uploads 500+ input rows at once without accidental duplication
Rationale:       Re-uploading the same file twice currently doubles quantities (G11); a deduplication guard is needed
UI status:       partial
Gap description: PayrollInputsBulkUpload.tsx and POST /{wid}/payroll/inputs/bulk are wired. BUT: no unique constraint on (workspace_id, employee_id, input_code, reference_date); re-submission silently doubles inputs.
API available:   ✅ POST /{wid}/payroll/inputs/bulk (missing dedup guard)
Existing page:   ✅ PayrollInputsBulkUpload.tsx
Data the UI must show:   File drop zone; template download; result summary (rows inserted, errors)
Actions the UI must support: Upload Excel; show per-row errors; retry failed rows
SC codes:        SC-GUA-6, SC-FAIL-1
Dependencies:    Migration to add unique constraint on inputs table
```

---

## Domain: Payroll Execution

### CARD 10 — View Execution Timeline
```
Domain:          Payroll Execution
Sprint:          Sprint 1 (data captured; UI not built)
Feature:         View step-by-step execution log for a payroll run
Outcome:         Operator sees execution sequence and step durations for debugging and audit
Rationale:       Slow runs or errors need diagnosis; timeline shows which steps took time
UI status:       partial
Gap description: GET /{wid}/payroll/runs/{runId}/timeline endpoint exists; execution_trace table populated. BUT: No UI page renders it. No "View Timeline" button in PayrollRuns.tsx or PayrollResults.tsx.
API available:   ✅ GET /{wid}/payroll/runs/{runId}/timeline
Existing page:   PayrollResults.tsx (add collapsible "Execution Timeline" tab)
Data the UI must show:   Ordered list: step_name, step_type, duration_ms, timestamp, status, notes
Actions the UI must support: Read-only; sortable by timestamp; collapse/expand
SC codes:        SC-AUD-1, SC-GUA-6
Dependencies:    None (UI-only addition; data already captured)
```

### CARD 11 — Retry Failed Employees + Recalculate Run Totals
```
Domain:          Payroll Execution
Sprint:          Sprint 1 (partial gap — G1)
Feature:         Retry failed employees; run totals updated after retry
Outcome:         Operator re-executes failed employees; run totals reflect the corrected results
Rationale:       PARTIAL runs leave stale run totals; reconciliation and exports use incorrect figures (G1)
UI status:       partial
Gap description: POST /payroll/retry endpoint and "Retry" button in PayrollResults.tsx are wired. BUT: G1 — after retry, payroll_run totals (total_gross_pay, total_deductions, total_net_pay) are not recalculated. Downstream reconciliation uses stale figures.
API available:   ✅ POST /payroll/retry (but totals not recalculated)
Existing page:   ✅ PayrollResults.tsx — "Retry" button present; FAILED rows highlighted
Data the UI must show:   FAILED employee rows; retry button; post-retry result summary; updated run totals
Actions the UI must support: Trigger retry; show result count (before/after); hide retry button once no FAILED remain
SC codes:        SC-RET-1, SC-RET-2, SC-RET-3, SC-RET-4
Dependencies:    ⬜ G1 fix — backend must recalculate payroll_run totals after retry
```

### CARD 12 — Submit Reconciliation with Run State Guard
```
Domain:          Payroll Execution
Sprint:          Sprint 0 (partial gaps — G4, G5)
Feature:         Submit reconciliation with state guard; duplicate returns 409
Outcome:         Finance operator records actual payment total safely; duplicate submissions are rejected cleanly
Rationale:       Reconciliation submitted before LOCKED produces unreliable MATCHED/MISMATCH (G4); second POST crashes with 500 (G5)
UI status:       partial
Gap description: Reconciliation.tsx and POST /{wid}/payroll/runs/{runId}/reconciliation are wired. BUT: G4 — no run state guard (accepts DRAFT, CALCULATING, PARTIAL). G5 — duplicate submission returns 500, not 409. Expected total may also be stale (G1 dependency).
API available:   ✅ POST /{wid}/payroll/runs/{runId}/reconciliation + PATCH (resolve)
Existing page:   ✅ Reconciliation.tsx — form present; state handling incomplete
Data the UI must show:   Expected total (from run); actual amount (form input); variance; reconciliation status (MATCHED/MISMATCH/RESOLVED); resolution notes
Actions the UI must support: Submit (only if LOCKED/PAID); resolve MISMATCH; read-only view if MATCHED/RESOLVED
SC codes:        SC-GUA-4, SC-FAIL-2, SC-GUA-6
Dependencies:    ⬜ G4 fix — state guard (LOCKED or PAID only); ⬜ G5 fix — 409 on duplicate; ⬜ G1 fix (for accurate expected total)
```

---

## Domain: Governance & Approval

### CARD 13 — Approve Payroll Run
```
Domain:          Governance & Approval
Sprint:          Sprint 1
Feature:         Approve payroll run (CALCULATED → APPROVED)
Outcome:         Finance authoriser formally approves calculated payroll before locking
Rationale:       Separation of duties; only reviewed runs advance to locked state
UI status:       complete ✅
API available:   ✅ POST /payroll/approve
Existing page:   ✅ PayrollResults.tsx — "Approve" button (conditional on CALCULATED status)
SC codes:        SC-AUD-1, SC-DAT-4, SC-GUA-6
Dependencies:    None
```

### CARD 14 — Lock Payroll Run
```
Domain:          Governance & Approval
Sprint:          Sprint 1
Feature:         Lock payroll run (APPROVED → LOCKED)
Outcome:         Payroll enters read-only state; no results can be modified; ready for disbursement
Rationale:       Immutability gate; ensures no changes between approval and payment
UI status:       complete ✅
API available:   ✅ POST /payroll/lock
Existing page:   ✅ PayrollResults.tsx — "Lock" button (conditional on APPROVED status)
SC codes:        SC-GUA-2, SC-AUD-1, SC-DAT-4
Dependencies:    None
```

### CARD 15 — Mark Run as Paid
```
Domain:          Governance & Approval
Sprint:          Sprint 1 (partial)
Feature:         Mark run as PAID (LOCKED → PAID)
Outcome:         Finance records that payroll has been disbursed; run enters immutable terminal state
Rationale:       Audit trail; confirms disbursement completion; prevents accidental re-payment
UI status:       partial
Gap description: POST /payroll/mark-paid and PayrollResults.tsx "Mark as Paid" button are wired. BUT: No disbursement file is generated on transition; no external trigger. The PAID flag is set but actual payment workflow is not automated.
API available:   ✅ POST /payroll/mark-paid
Existing page:   ✅ PayrollResults.tsx — button present
Data the UI must show:   Mark as Paid button (conditional on LOCKED); confirmation; disbursement summary
Actions the UI must support: Trigger PAID transition; show success; link to reconciliation and export downloads
SC codes:        SC-GUA-5, SC-DAT-4, SC-AUD-1
Dependencies:    None for PAID flag; bank export (Card 16) is the companion action
```

### CARD 16 — Real User Identity in Audit Log (X-Performed-By Header)
```
Domain:          Governance & Approval
Sprint:          Sprint 7 (Track I #35 — partial)
Feature:         Capture real user identity on all approval/lock/retry actions
Outcome:         Audit trail shows actual user who approved/locked/retried — not default placeholder
Rationale:       Accountability; compliance; separation of duties evidence requires real actor names
UI status:       partial
Gap description: Backend routes accept X-Performed-By header on approve/lock/retry (defaults to "admin@internal" if absent). BUT: Frontend action buttons (PayrollResults.tsx, RunPayroll.tsx) do not send the header. All actions logged as "admin@internal".
API available:   ✅ Backend routes accept X-Performed-By header
Existing page:   ✅ All pages with approve/lock/retry actions (PayrollResults.tsx, RunPayroll.tsx)
Data the UI must show:   Logged actor name in audit trail view
Actions the UI must support: Frontend fetches user identity from auth context and injects X-Performed-By header on every action
SC codes:        SC-AUD-1, SC-INT-2
Dependencies:    Auth context / session management must expose current user
```

---

## Domain: Disbursement & Reconciliation

### CARD 17 — Export Net Pay for Bank Upload
```
Domain:          Disbursement & Reconciliation
Sprint:          Sprint 1 (complete)
Feature:         Generate CSV of employee net pay for bank disbursement
Outcome:         Finance downloads CSV with [employee_number, account_number, net_pay, bank_code]
Rationale:       Automates payment file; reduces manual error risk
UI status:       complete ✅
API available:   ✅ GET /{wid}/payroll/runs/{runId}/export/bank-upload
Existing page:   ✅ PayrollResults.tsx — export button present (conditional on LOCKED/PAID)
SC codes:        SC-GUA-3, SC-GUA-6
Dependencies:    None
```

### CARD 18 — Export PAYE Remittance Schedule
```
Domain:          Disbursement & Reconciliation
Sprint:          Sprint 1 (complete)
Feature:         Generate statutory PAYE return for tax authority
Outcome:         Operator downloads [employee_name, tin, paye_amount, pension_contribution] for tax filing
Rationale:       Statutory compliance; tax return filing
UI status:       complete ✅
API available:   ✅ GET /{wid}/payroll/runs/{runId}/export/paye-remittance
Existing page:   ✅ PayrollResults.tsx — export button present
SC codes:        SC-GUA-3, SC-GUA-6
Dependencies:    None
```

### CARD 19 — Export Pension Contribution Schedule
```
Domain:          Disbursement & Reconciliation
Sprint:          Sprint 1 (complete)
Feature:         Generate pension contribution report for administrator
Outcome:         Operator downloads [employee_name, employee_number, employee_contribution, employer_contribution]
Rationale:       Pension fund reconciliation; statutory reporting
UI status:       complete ✅
API available:   ✅ GET /{wid}/payroll/runs/{runId}/export/pension-contributions
Existing page:   ✅ PayrollResults.tsx — export button present
SC codes:        SC-GUA-3, SC-GUA-6
Dependencies:    None
```

### CARD 20 — Export Full Payroll Register
```
Domain:          Disbursement & Reconciliation
Sprint:          Sprint 1 (complete)
Feature:         Generate complete payroll register for audit and record
Outcome:         Operator downloads full register with [employee, gross, components, deductions, net]
Rationale:       Complete audit trail; statutory record; bank reconciliation reference
UI status:       complete ✅
API available:   ✅ GET /{wid}/payroll/runs/{runId}/export/full-detail
Existing page:   ✅ PayrollResults.tsx — export button present
SC codes:        SC-GUA-3, SC-GUA-6
Dependencies:    None
```

---

## Domain: Audit & Traceability

### CARD 21 — View Calculation Snapshot (Structured Renderer)
```
Domain:          Audit & Traceability
Sprint:          Sprint 0 (data captured; UI not built)
Feature:         Inspect the frozen rules context snapshot for a run
Outcome:         Auditor views the exact statutory rates, tax bands, and rule set items active when a run executed
Rationale:       Full reproducibility and auditability; resolves disputes over which rate was applied
UI status:       partial
Gap description: payroll_run.rules_context_snapshot (v2 JSONB) is captured. GET /{wid}/payroll/runs/{runId} returns it as raw JSON. No UI parses or renders it — data is inaccessible to a non-technical operator.
API available:   ✅ GET /{wid}/payroll/runs/{runId} (returns rules_context_snapshot raw JSONB)
Existing page:   PayrollResults.tsx (add collapsible "Rule Snapshot" tab)
Data the UI must show:   Statutory rule (version, effective_from, paye_bands, pension_rate, nhf_rate); rule_set items; historical rule sets used
Actions the UI must support: Read-only; tree view or expandable sections; search by component code
SC codes:        SC-AUD-3, SC-TMP-2, SC-TMP-3
Dependencies:    None (UI-only; data already stored)
```

### CARD 22 — View Component-Level Calculation Trace
```
Domain:          Audit & Traceability
Sprint:          Sprint 2 (partial — G12)
Feature:         View per-employee, per-component calculation breakdown with method and rate applied
Outcome:         Operator sees [component_code, method, rate_basis, amount] for each component per employee
Rationale:       Debugging; compliance verification; resolves employee disputes over pay components
UI status:       partial
Gap description: Sequential executor populates component_trace_jsonb; PayrollResults.tsx has per-employee expandable trace rows. BUT: G12 — legacy executor path produces NULL component_trace_jsonb; some employees have no trace. Track N-1 (merge _rule_trace + rate_basis) not yet scheduled.
API available:   ✅ GET /{wid}/payroll/runs/{runId}/results (returns component_trace_jsonb)
Existing page:   ✅ PayrollResults.tsx — per-employee trace expansion present (incomplete for legacy path)
Data the UI must show:   component_code, calculation_method, rate_basis, amount, resolution_source, warning (if any)
Actions the UI must support: Expand/collapse per employee; view full trace; search by component; highlight warnings
SC codes:        SC-AUD-2, SC-AUD-1, SC-GUA-3
Dependencies:    ⬜ G12 fix — legacy executor must populate component_trace_jsonb
```

### CARD 23 — Replay a Run Using Frozen Snapshot
```
Domain:          Audit & Traceability
Sprint:          Deferred (Phase 3)
Feature:         Re-derive payroll results using frozen snapshot without hitting live DB
Outcome:         Operator reproduces exact historical results for audit verification
Rationale:       Full auditability; resolves disputes over historical payment correctness without dependency on current rates
UI status:       not wired
Gap description: Snapshot v2 contains all required data. No replay endpoint or UI exists. Deferred to Phase 3 per ROADMAP.
API available:   None — no POST /payroll/replay endpoint
Existing page:   New feature — "Replay" button in PayrollResults.tsx or new ReplayRun.tsx
Data the UI must show:   Original run details; replay confirmation; result diff; discrepancy warnings
Actions the UI must support: Trigger replay; show side-by-side before/after results; flag discrepancies
SC codes:        SC-AUD-3, SC-RET-2
Dependencies:    Replay service (backend); data available in snapshot
```

---

## Domain: Timesheet & Attendance

### CARD 24 — Workspace Timesheet Configuration
```
Domain:          Timesheet & Attendance
Sprint:          Sprint 16 (TM-1)
Feature:         Configure workspace as timesheet-enabled or input-file-only
Outcome:         Operator toggles timesheet mode; attendance codes seeded automatically
Rationale:       Different clients use different input modes (daily attendance vs. period salary file)
UI status:       partial
Gap description: WorkspacePayrollConfig.timesheet_enabled + PUT /{wid}/payroll-config are wired (TM-1); WorkspaceConfig.tsx includes toggle. Needs verification that frontend sends timesheet_enabled flag correctly; template version warning not yet implemented.
API available:   ✅ GET /{wid}/payroll-config + PUT /{wid}/payroll-config
Existing page:   ✅ WorkspaceConfig.tsx — PayrollBehaviour section
Data the UI must show:   timesheet_enabled toggle; attendance template version; seeded attendance codes list
Actions the UI must support: Toggle timesheet_enabled; confirm seeding; view template version and available upgrades
SC codes:        SC-GUA-6, SC-TST-3
Dependencies:    None
```

### CARD 25 — Timesheet Upload for Daily Attendance
```
Domain:          Timesheet & Attendance
Sprint:          Sprint 16 (TM-2)
Feature:         Upload monthly timesheet Excel file with daily attendance grid
Outcome:         HR operator uploads raw attendance data; system normalises to daily entries
Rationale:       Timesheet clients input via attendance grids, not manual input files
UI status:       complete ✅
API available:   ✅ POST /{wid}/payroll/derive-timesheet
Existing page:   ✅ TimesheetUpload.tsx
SC codes:        SC-GUA-6, SC-INT-2
Dependencies:    None
```

### CARD 26 — Timesheet Derivation Review
```
Domain:          Timesheet & Attendance
Sprint:          Sprint 16 (TM-3)
Feature:         Review derived OT hours, proration factor, and shift days before approving
Outcome:         HR operator confirms derived values are correct before they become payroll inputs
Rationale:       Automation errors (wrong code mapping, shift misclassification) must be catchable before run
UI status:       complete ✅
API available:   ✅ POST /{wid}/payroll/derive-timesheet (returns derivation summary)
Existing page:   ✅ TimesheetUpload.tsx — derivation review step after upload
SC codes:        SC-AUD-2, SC-AUD-3
Dependencies:    None
```

### CARD 27 — Manual OT Adjustment
```
Domain:          Timesheet & Attendance
Sprint:          Sprint 16 (TM-4)
Feature:         HR operator enters manual OT adjustments on top of auto-derived OT hours
Outcome:         Post-upload corrections applied before run claims inputs — no full re-upload needed
Rationale:       System derivation errors or edge cases need a correction path
UI status:       complete ✅
API available:   ✅ PATCH /{wid}/payroll/timesheet-entry/{entryId}
Existing page:   ✅ AttendanceConfiguration.tsx — adjustment forms present
SC codes:        SC-AUD-2, SC-GUA-6
Dependencies:    None
```

### CARD 28 — Attendance Code and Policy Configuration
```
Domain:          Timesheet & Attendance
Sprint:          Sprint 16 (TM-7)
Feature:         View and configure attendance codes and their pay policies
Outcome:         HR operator customises which attendance codes are recognised and how they affect pay
Rationale:       Different clients have different leave/shift/absence policies
UI status:       complete ✅
API available:   ✅ GET /{wid}/attendance-codes + POST /{wid}/attendance-code + PATCH /{wid}/attendance-code
Existing page:   ✅ AttendanceConfiguration.tsx — full CRUD
SC codes:        SC-GUA-6, SC-TST-3
Dependencies:    None
```

---

## Domain: Rate Codes & Components

### CARD 29 — Rate Code Registry
```
Domain:          Rate Codes & Components
Sprint:          Sprint 7 (PH-7, Track F-25 / Sprint 8 Gate 5)
Feature:         View and manage rate codes (multipliers for OT/shift pay)
Outcome:         Operator sees platform codes and can add workspace-specific codes
Rationale:       Transparency into OT/shift multipliers; extensibility for client-specific rates
UI status:       complete ✅
API available:   ✅ GET /{wid}/rate-codes + POST /{wid}/rate-code + DELETE /{wid}/rate-code
Existing page:   ✅ RateCodes.tsx — full CRUD page (Gate 5, Sprint 8)
SC codes:        SC-GUA-6
Dependencies:    None
```

---

## Summary by Domain

| Domain | Not Wired | Partial | Complete | Total |
|--------|-----------|---------|----------|-------|
| Workspace Setup | 2 | 0 | 1 | 3 |
| Workforce Config | 0 | 0 | 5 | 5 |
| Pay Events | 0 | 1 | 0 | 1 |
| Payroll Execution | 0 | 3 | 0 | 3 |
| Governance & Approval | 0 | 2 | 2 | 4 |
| Disbursement & Reconciliation | 0 | 0 | 4 | 4 |
| Audit & Traceability | 1 | 2 | 0 | 3 |
| Timesheet & Attendance | 0 | 1 | 4 | 5 |
| Rate Codes & Components | 0 | 0 | 1 | 1 |
| **TOTAL** | **3** | **9** | **17** | **29** |

---

## Prioritised Build Order

### Priority 1 — Blocking Daily Operations

| # | Gap | Effort | Backend fix? | Depends |
|---|-----|--------|-------------|---------|
| 1 | G4: Reconciliation state guard (LOCKED/PAID only) | XS | Yes | None |
| 2 | G5: Duplicate reconciliation → 409 not 500 | XS | Yes | None |
| 3 | G1: Retry recalculates run totals | S | Yes | None |
| 4 | Card 21: View calculation snapshot (structured renderer) | M | UI only | None |
| 5 | Card 22: Component trace — fix legacy executor G12 gap | M | Yes | None |

### Priority 2 — Configuration / Setup

| # | Gap | Effort | Backend fix? | Depends |
|---|-----|--------|-------------|---------|
| 6 | Card 1: View applicable statutory rules (read-only GET) | S | Yes (endpoint) | None |
| 7 | Card 16: X-Performed-By header from frontend | S | UI only | Auth context |
| 8 | Card 9: Bulk input deduplication guard | S | Yes (migration) | None |
| 9 | Card 24: Timesheet config — verify frontend flag | XS | UI only | None |

### Priority 3 — Observability / Reporting

| # | Gap | Effort | Backend fix? | Depends |
|---|-----|--------|-------------|---------|
| 10 | Card 10: View execution timeline | S | UI only | None |
| 11 | Card 15: Mark as Paid — surface companion export | S | UI only | Bank export (Card 17) |
| 12 | Card 11: Retry — surface updated run totals in UI | XS | UI only | G1 fix |

### Priority 4 — Deferred (Phase 3)

| # | Gap | Effort | Notes |
|---|-----|--------|-------|
| 13 | Card 23: Replay run using frozen snapshot | L | Data captured; replay service not built |
| 14 | Card 2: Statutory rule management (publish new versions) | L | Admin-only; not blocking operator workflow |

---

*Built from Sprint 0 through Sprint 16. Update this document after each sprint that introduces or completes a UI-accessible feature. Reference SC codes in feature acceptance criteria.*
