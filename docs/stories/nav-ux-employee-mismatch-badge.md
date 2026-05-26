# Nav UX — Inputs Order + Employee Mismatch Badge
**Written in retrospective — 2026-05-26**
**Implemented:** same session, no sprint planning precursor

---

## Story 1 — Sidebar nav order reflects workflow sequence

**As a** payroll operator,
**I want** the Inputs item to appear above the Runs item in the sidebar,
**So that** the nav reads in the same order I work — I enter data before I run payroll.

### Acceptance Criteria

- **Given** I am inside any workspace, **when** I look at the Payroll section of the sidebar, **then** "Inputs" is the first item and "Runs" is the second.
- **Given** I click "Inputs", **when** the page loads, **then** the Inputs nav item is highlighted (active state), not Runs.
- **Given** I click "Runs", **when** the page loads, **then** the Runs nav item is highlighted.
- Both items remain independently routable — the order change does not affect which URL each item navigates to.

### Out of Scope
- Renaming either nav item
- Changing the icon associated with either item
- Any reordering of other sidebar sections (People, Settings)

### Business Risk / Impact
- **Cost of not doing:** Operators mentally model payroll as a sequence: collect inputs → run → approve. A nav that shows Run before Input subtly implies the wrong order, increasing training friction and operator errors.
- **Cost of doing it wrong:** Low — this is a display-only reorder with no data consequence.

### Priority
**P3** — operator productivity / UX polish. No system is broken without it, but it removes a small daily friction point.

### Open Questions
None. Change is unambiguous and non-breaking.

---

## Story 2 — Sidebar shows employee mismatch count without navigating away

**As a** payroll operator preparing to run payroll,
**I want** to see a count of employees with incomplete contracts directly on the Employees nav item,
**So that** I know there is a data quality problem I need to fix before attempting a run — without having to visit the Employees page to discover it.

### Acceptance Criteria

**Happy path — mismatches present:**
- **Given** one or more active employees are missing a grade or designation, **when** I view any page within the workspace, **then** an amber badge appears on the "Employees" sidebar item showing the count (e.g. `3`).
- The count matches exactly the number shown in the AlertBanner on the Employees page.
- **Given** the count is greater than 99, **when** the badge renders, **then** it displays `99+` (not a truncated or overflowing number).

**Happy path — no mismatches:**
- **Given** all active employees have both grade and designation assigned, **when** I view the sidebar, **then** no badge appears on the Employees item.

**Collapsed sidebar:**
- **Given** the sidebar is collapsed to icon-only mode, **when** I hover over the Employees icon, **then** the tooltip reads `"Employees (N unmatched)"` if mismatches exist, or `"Employees"` if none.
- The badge pill is NOT visible in collapsed mode (the tooltip carries the information instead, to avoid overflow in the 64 px column).

**Employee resolved:**
- **Given** a badge is showing, **when** I navigate to Employees, assign the missing grade/designation and save, **then** the badge count decrements (or disappears if the last mismatch is resolved) on the next page load.

**No workspace selected:**
- **Given** I am on the Bureau Dashboard (no workspace context), **then** no badge is rendered.

**API failure:**
- **Given** the employee fetch in the layout silently fails, **then** the badge simply does not appear — no error is shown to the user, no crash, no blocked navigation.

### Out of Scope
- Real-time / WebSocket badge updates (badge refreshes on workspace navigation, not on a polling interval)
- Mismatch badges on other nav items (e.g. Configuration, Inputs)
- A breakdown of which employees are unmatched inside a tooltip or popover
- Colour choices other than amber (amber = warning, consistent with the AlertBanner on the Employees page)
- A badge on the "Runs" item for runs in a bad state

### Business Risk / Impact
- **Cost of not doing:** Operators discover unmatched employees only when a run fails or they happen to visit the Employees page. A payroll run that excludes employees silently is a compliance and trust risk — someone gets paid ₦0 with no clear warning upstream.
- **Cost of doing it wrong:** If the badge count diverges from the Employees page banner count, operators lose trust in the indicator and ignore it. The filter logic must be identical in both places — verified in this session.
- **Who is blocked:** Any operator who runs payroll without realising employees are unmatched will produce an incomplete run.

### Priority
**P2** — operator productivity with a compliance edge. Prevents silent incomplete payroll runs without requiring a process change.

### Open Questions
1. Should the badge refresh automatically when the operator resolves a mismatch on the Employees page without navigating away? Currently it refreshes only on workspace navigation (workspaceId dependency). Could add a context-level invalidation event — deferred, not blocking.
2. Should the badge persist across sub-pages (Results, Reconciliation, Run detail) or only on the main workspace pages? Currently always visible — may be distracting when the operator is deep in a run audit. Deferred.
