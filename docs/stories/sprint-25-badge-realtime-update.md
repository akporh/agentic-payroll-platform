# Story: Nav Badge Real-Time Update — employees-changed Event
**Written in retrospective — 2026-06-09**
**Sprint 25 — implemented same session, no sprint planning precursor**

---

## Story — Sidebar badge updates in real-time without a page refresh

**As a** payroll bureau operator,
**I want** the "not enrolled" badge on the Employees sidebar item to update immediately when
I enroll an employee,
**So that** I can see at a glance that my action worked and know how many employees remain
without having to refresh the page or navigate away.

### Acceptance Criteria

**Happy path — enrollment clears the badge:**
- **Given** the sidebar shows a badge (e.g. `12`) on the Employees item, **when** I enroll
  a group of employees via the 1-click enroll button, **then** the badge count decrements
  to reflect the remaining unenrolled employees within the same page session (no refresh).
- **Given** I enroll the last unenrolled employee, **when** the enrollment saves successfully,
  **then** the badge disappears from the sidebar without any page reload.

**All enrollment paths trigger the update:**
- Badge updates after: 1-click direct group enroll, bulk enroll via SlideOver, single employee
  enroll via EnrollSlideOver, bulk upload, add single employee, edit employee, change contract.
- No action that modifies the employee list leaves the badge stale.

**Upload path:**
- **Given** I upload a spreadsheet of 20 new employees, **when** the upload completes,
  **then** the badge increments to reflect the newly added unenrolled employees immediately.

**Workspace switch:**
- **Given** a badge is showing for workspace A, **when** I switch to workspace B, **then**
  the badge reflects workspace B's counts and no stale events from workspace A affect it.

**No regression — initial load:**
- **Given** I navigate to a workspace for the first time in a session, **when** the page
  loads, **then** the badge is already correct (initial fetch is unaffected).

### Out of Scope
- Polling or websocket-based badge updates (not required — badge updates driven by user
  actions only)
- Badge updates triggered by actions on other pages (e.g. PayrollResults) — those pages do
  not yet dispatch the event

### Implementation Summary

**Root cause:** `MainLayout.tsx` fetched the employee list once on mount (`useEffect([workspaceId])`).
`Employees.tsx` mutations refreshed local state but had no channel to signal the parent.

**Fix:** Custom window event `employees-changed`.
- `frontend/src/pages/Employees.tsx` — `loadEmployees()` dispatches
  `new CustomEvent('employees-changed')` after every successful employee list refresh.
- `frontend/src/components/layout/MainLayout.tsx` — a `useEffect` subscribes to the event
  and re-fetches the employee list, recomputing `notEnrolledEmployeeCount` which drives the badge.
- Listener is cleaned up on workspace change via the useEffect return function.

### Business Risk / Impact
- **Cost of not doing:** Operator enrolls 56 employees, badge still shows 56 — they think the
  action failed, attempt again, confusion and loss of trust in the UI.
- **Cost of doing it wrong:** Low — additive change, does not alter existing fetch logic. Worst
  failure mode: badge stays stale (not a data integrity risk).

### Priority
**P2** — operator productivity. Badge staleness after enrollment was actively misleading.
