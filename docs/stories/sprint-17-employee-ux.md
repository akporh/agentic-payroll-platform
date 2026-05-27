# Sprint 17: Employee UX — Workflow Corrections

**Delivery increment:** UX corrections to Employees.tsx — identified during employee refactor journey audit  
**Must ship with:** Sprint 17 Track B (sprint-17-employee-crud.md)  
**Note:** Deactivation UX (dedicated flow + input warning) is Sprint 20 — see sprint-20-hr-readiness-phase3.md EMP-UX-2

---

## Scope Boundary

**IN scope:**
- Split the conflated "Edit" action into two separate, correctly-scoped row actions
- Mid-period hire warning in Add Employee SlideOver
- Payroll Inputs attention badge (nav + page banner)

**OUT of scope:**
- Deactivation SlideOver and input warning (Sprint 20 EMP-P3-2 / EMP-UX-2)
- Contract history panel showing multiple past rows (Sprint 20 EMP-P3-1)
- "Final period" badge on payroll results (Sprint 20 EMP-P3-2)
- Any backend changes beyond the new `GET /payroll/inputs/issues` endpoint for EMP-UX-4

---

## EMP-UX-1 · Split employee row actions — Edit Details vs Change Grade/Salary

**Priority:** P1 — Data integrity prerequisite for Sprint 17 append-only contract model

**As a** workspace administrator,  
**I want** distinct, clearly labelled row actions for editing an employee's details and changing their grade or salary,  
**So that** I cannot accidentally trigger a contract change when I only intend to fix a name or status.

### Current state (the problem)

The existing `EditSlideOver` (`Employees.tsx:116–161`) contains grade, designation, and contract end date in one form. After the Sprint 17 append-only contract model, changing grade creates a new contract row — an irreversible operation. It must not share a form with editing a name.

### Acceptance Criteria

**Row action layout**

**Given** any active employee row,  
**When** rendered,  
**Then** the actions column shows two distinct buttons:
- **"Edit"** — opens `EditEmployeeSlideOver` (name and status only)
- **"Change Grade / Salary"** — opens `ChangeContractSlideOver` (new contract)

The existing single "Edit" button that opens the conflated form is removed.

**Edit SlideOver — correct scope**

**Given** the operator clicks "Edit",  
**When** the SlideOver opens,  
**Then** it contains only: `full_name` and `status` (ACTIVE / INACTIVE).  
**And** grade, designation, and contract end date are not present.  
**And** it saves via `PATCH /{wid}/employees/{eid}` — no contract row is touched.

**Change Grade / Salary SlideOver**

**Given** the operator clicks "Change Grade / Salary",  
**When** the SlideOver opens,  
**Then** it contains: new `salary_definition_id` (searchable dropdown), `start_date` (required), `change_reason` (required).  
**And** an info note reads: *"This will close the current contract and open a new one from the selected start date."*  
**And** on save: `POST /{wid}/employees/{eid}/contracts` is called.  
**And** on success: the table row updates to show the new salary definition.

**Given** the save returns a 409 (active run exists),  
**Then** an `AlertBanner variant="error"` inside the SlideOver displays: *"A payroll run is in progress. Contract changes are locked until the run completes."*

**Given** the save returns a 422 (backdating violation),  
**Then** an `AlertBanner variant="error"` displays: *"New start date must be after the current contract start date."*

**Ended employees**

**Given** a row in the "Ended" section,  
**When** rendered,  
**Then** only "Edit" is shown — no "Change Grade / Salary" for ended employees.

**View Contracts action**

**Given** any active employee row,  
**When** the actions are rendered,  
**Then** a "View Contracts" link is also present (alongside Edit and Change Grade/Salary).  
In Sprint 17, clicking it opens a read-only panel showing the current contract only (salary definition name, start date, "Current").  
Full history across multiple rows is Sprint 20.

### Out of Scope
- "Deactivate" action (Sprint 20)
- Overflow / "⋯ More" menu (Sprint 20 adds Deactivate at that point)

### Business Risk
- **Not done:** Operator opens "Edit", inadvertently changes grade and saves — creates a new contract row under the Sprint 17 model. No confirmation, no undo. Financial and audit error.

### Open Questions
- None.

---

## EMP-UX-3 · Mid-period hire warning in Add Employee

**Priority:** P2 — Operator clarity (prevents support queries about missing payroll results)

**As a** workspace administrator,  
**I want** a clear inline warning when I add an employee whose start date falls within the current open pay period,  
**So that** I am not surprised when that employee does not appear in the current run.

### Acceptance Criteria

**Warning trigger**

**Given** the Add Employee SlideOver is open,  
**When** the operator enters a `contract_start` date where `period_start ≤ contract_start ≤ period_end` for the current open period,  
**Then** an info `AlertBanner` appears immediately below the start date field:  
*"This start date falls within the current pay period ({period label}). This employee will appear in payroll from the next period onwards."*

**Given** `contract_start` is before the current period start (backdated hire),  
**Then** no warning — backdated hires are included normally.

**Given** `contract_start` is after the current period end (future hire),  
**Then** no warning — expected not to appear yet.

**Given** no active pay cycle is configured for the workspace,  
**Then** no warning — guard only active when a period is determinable.

**Save behaviour**

**Given** the warning is visible,  
**When** the operator clicks "Add Employee",  
**Then** the employee saves normally — warning is informational, not a blocker.

### Implementation note
Current period dates are derivable from `workspace.pay_cycle` already in `WorkspaceContext`. No new API call needed — pure frontend calculation.

### Out of Scope
- Blocking mid-period hires
- Prorating the new hire for the partial period (separate sprint)

### Business Risk
- **Not done:** Operator expects a same-period result, finds none, raises a support query. A single info banner eliminates the confusion.

### Open Questions
- None.

---

## EMP-UX-4 · Payroll Inputs attention badge

**Priority:** P2 — Operator awareness (prevents silent run failures and unprocessed inputs)

**As a** payroll operator,  
**I want** a badge on the Payroll Inputs nav item when inputs require attention,  
**So that** I notice and resolve issues before triggering a run rather than discovering them in a failed result.

### What "requires attention" means

| Condition | Risk if unresolved |
|-----------|-------------------|
| Deactivated employee has inputs in the current period | Employee excluded from run; inputs permanently unprocessed (underpaid bonus, unrecovered deduction) |
| Unmatched employee has inputs (missing grade or salary definition) | Run will fail for this employee; result row marked FAILED |

**Note on duplicates:** The backend rejects duplicate inputs at write time — they cannot persist as a queryable badge condition.

### Acceptance Criteria

**Badge — navigation**

**Given** the current open period has attention-required inputs,  
**When** any workspace page loads,  
**Then** the "Inputs" nav item shows a numeric badge with the total count of affected input rows.

**Given** all inputs are clean,  
**Then** no badge appears.

**Given** no open pay period exists,  
**Then** no badge appears.

**Backend endpoint**

New: `GET /workspaces/{id}/payroll/inputs/issues`

Response:
```json
{
  "total": 3,
  "deactivated_with_inputs": 1,
  "unmatched_with_inputs": 2,
  "period_label": "May 2026"
}
```

Scoped to the current open period. Returns `{"total": 0, ...}` when clean.

Query logic (workspace-scoped throughout):
- **Deactivated:** `payroll_input` rows for employees whose `contract_end < period_start`
- **Unmatched:** `payroll_input` rows for employees missing `grade` or `salary_definition_id`

**Frontend wiring — `MainLayout.tsx`**

Follows the existing `unmatchedEmployeeCount` pattern exactly:
- `MainLayout` calls `GET /payroll/inputs/issues` on workspace load
- Passes `inputIssueCount={data.total}` through `Layout` → `WorkspaceSidebar`
- `WorkspaceSidebar` adds `inputIssueCount` prop — "Inputs" nav item gets `badge: inputIssueCount || undefined`

Reuses existing badge rendering at `Navigation.tsx:286–291`. No new component needed.

**Inline alert on Inputs page**

**Given** issues exist and the operator navigates to Payroll Inputs,  
**When** the page loads,  
**Then** an amber `AlertBanner` appears at the top:  
*"3 inputs require attention before running payroll: 1 deactivated employee, 2 employees missing grade or salary definition."*  
With link: *"Review employees →"* navigating to the Employees page.

**Given** no issues exist,  
**Then** no banner.

**Badge refresh:** Updates on next page load or navigation — no real-time push needed.

### Out of Scope
- Real-time badge updates without navigation
- Resolving issues from the Inputs page (operator goes to Employees)
- Duplicate input detection (prevented at write time)

### Business Risk
- **Not done:** Operator runs payroll with deactivated employee inputs — they are silently excluded, money is not paid, correction run required.
- **Done wrong:** Over-broad badge scope causes alert fatigue. Intentionally narrow — only conditions that directly cause run failure or lost money.

### Open Questions
- None.
