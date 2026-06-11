# Sprint 26 — Employee Registration & Status Management
**Stories: EMP-REG-1, EMP-STATUS-1, EMP-BADGE-1, EMP-EDIT-1, EMP-ICONS-1, EMP-ENROLL-AUTODEF-1, EMP-PAYROLL-ACTIONS-1**

---

## EMP-REG-1 — Grade and Designation on single Add Employee form

**As** a payroll operator,
**I want** to select a grade and designation when registering a new employee,
**So that** the employee's HR classification is captured at point of entry rather than requiring a separate step.

### Acceptance Criteria

- Given the Register Employee slide-over is open, two optional dropdowns appear: "Grade" and "Designation", populated from the workspace's active grades and designations
- When I select a grade and/or designation and submit, the employee is created with those values linked
- When I leave both blank and submit, the employee is created with grade and designation null (no regression)
- The "Salary Definition" field does NOT appear — it remains enrolment-only
- If the grades/designations list fails to load, dropdowns show empty with a placeholder and the form remains submittable

**Out of scope:** Salary definition, automatic enrolment, any payroll-calculation field.

**Priority:** P2

---

## EMP-STATUS-1 — Disable / Enable employees awaiting enrolment

**As** a payroll operator,
**I want** to mark an awaiting-enrolment employee as Inactive (and re-activate them),
**So that** I can park employees who are registered but not yet ready for payroll without cluttering the enrolment queue.

### Acceptance Criteria

- Given an employee with status=ACTIVE and is_enrolled=false appears in the not-enrolled list
- When I click "Park" on their row, the employee status is set to INACTIVE and they move out of the active not-enrolled accordion
- A "Parked" card section appears below the not-enrolled accordion showing all parked employees
- When I click "Re-activate →" for a parked employee, their status returns to ACTIVE and they reappear in the not-enrolled queue
- The action is confirmed immediately with a toast
- If the PATCH call fails, a toast error is shown and the row status does not change in the UI

**Edge cases:**
- An already-enrolled employee does NOT have this control (out of scope)
- Action scoped to workspace (backend enforces this)

**Out of scope:** Disabling enrolled employees, bulk status toggle, audit log for status change.

**Priority:** P2

---

## EMP-BADGE-1 — Exclude INACTIVE employees from not-enrolled nav badge

**As** a payroll operator,
**I want** the "Employees" nav badge to reflect only active employees awaiting enrolment,
**So that** the badge accurately represents actionable work, not parked records.

### Acceptance Criteria

- Given employee A is ACTIVE and not enrolled → counted in badge
- Given employee B is INACTIVE and not enrolled → NOT counted in badge
- Badge updates immediately when an employee is parked or re-activated (no reload required)
- Badge goes to zero / disappears when all not-enrolled employees are enrolled or parked

**Dependency:** EMP-STATUS-1 (badge fix without park capability has no effect).

**Priority:** P2 — ship with EMP-STATUS-1.

---

## EMP-EDIT-1 — Edit registered (not-enrolled) employees

**As** a payroll operator,
**I want** to edit an employee's name or status from the not-enrolled list,
**So that** I can correct mistakes made during registration without navigating elsewhere.

### Acceptance Criteria

- Given an employee row is expanded in the not-enrolled accordion
- When I click the edit icon, EditSlideOver opens pre-filled with that employee's name and status
- When I save, the employee's name/status is updated and the list refreshes
- The edit icon has tooltip "Edit employee" and uses IconBtn
- Salary definition, grade (from enrolment), and designation (from enrolment) are NOT editable here

**Priority:** P2

---

## EMP-ICONS-1 — Icon-based row actions in EmployeeTable

**As** a payroll operator,
**I want** action buttons in employee tables to use icons with tooltips rather than text labels,
**So that** tables are more compact and scannable at a glance.

### Acceptance Criteria

- All action buttons in EmployeeTable use IconBtn with a `title` tooltip and `aria-label`
- Edit → pencil icon (PencilIcon), tooltip "Edit"
- Change Grade / Salary → arrows icon (ArrowsRightLeftIcon), tooltip "Change Grade / Salary"
- View Contracts → document icon (DocumentTextIcon), tooltip "View Contracts"
- Enroll → user-plus icon (UserPlusIcon), tooltip "Enroll"
- Icons imported from `@heroicons/react/24/outline`
- Destructive/rare actions (Park, Terminate) retain text labels to prevent accidental clicks

**Out of scope:** Changes to payroll page icons.

**Priority:** P3 — polish; can be deferred if sprint is full.

---

## EMP-ENROLL-AUTODEF-1 — Auto-match salary definition from grade on enrolment

**As** a payroll operator,
**I want** the salary definition to be pre-selected automatically when the employee's grade is already known,
**So that** I don't have to manually look up and select the matching salary definition on every enrolment.

### Acceptance Criteria

- Given a single-employee enrolment (EnrollSlideOver) opens for an employee who has a grade set
- The salary definition field is pre-populated with the matching salary definition (same matching logic as grouped auto-suggest: DESIG_GRADE → GRADE_DESIG → DESIG → GRADE, case-insensitive)
- If no match is found, the field is empty and operator selects manually (no regression)
- Given the "Change Grade/Salary" slide-over is opened for an employee with a known grade
- When a grade is selected or pre-populated, the salary definition auto-matches and displays as read-only with label "Auto-matched from grade"
- If grade is changed, salary definition re-matches automatically
- If no match is found, salary definition field becomes editable

**Edge cases:**
- Multiple salary defs match same grade → pre-fill with first match, field remains editable
- No grades configured → no auto-match, behaviour unchanged

**Priority:** P2 — reduces a common manual step per enrolment. Backend fix ships with this story.

---

## EMP-PAYROLL-ACTIONS-1 — Restricted and simplified actions for enrolled employees

**As** a payroll operator,
**I want** the In Payroll employee rows to show only payroll-relevant actions, and for contract management (including activate/deactivate and end contract) to be accessible from the Contracts view,
**So that** it's clear what can be changed once an employee is enrolled, and all contract actions are in one place.

### Acceptance Criteria

**Row-level changes (EmployeeTable "active" variant):**
- "Edit" button is NOT shown (name/details not editable for enrolled employees)
- Two icon actions remain: Change Grade/Salary and View Contracts

**View Contracts slide-over — upgraded to management surface:**
- Shows status badge (ACTIVE / INACTIVE) and a contextual button: "Deactivate" when active, "Activate" when inactive
- Clicking Activate/Deactivate calls PATCH employee with new status; success = toast + slide-over state updates
- Shows "End Contract" button (only if contract has no end date set)
- Clicking "End Contract" reveals a date field inline (no modal) labelled "Contract End Date" with a "Confirm" button
- Confirming sets contract_end on the current contract and dispatches employees-changed
- Contract history list remains visible below the management actions

**Out of scope:** Editing employee name, TIN, RSA, bank details for enrolled employees. Reactivating a terminated contract. Bulk actions.

**Priority:** P2

---

## Delivery order

| # | Story | Depends on |
|---|---|---|
| 1 | EMP-REG-1 | — |
| 2 | EMP-EDIT-1 | — |
| 3 | EMP-ICONS-1 | — |
| 4 | EMP-STATUS-1 | — |
| 5 | EMP-BADGE-1 | EMP-STATUS-1 |
| 6 | EMP-ENROLL-AUTODEF-1 | — |
| 7 | EMP-PAYROLL-ACTIONS-1 | — |
