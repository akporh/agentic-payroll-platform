# Story: Employees Table — Sticky Actions Column + Toggle Dead Zone Fix
**Written in retrospective — 2026-06-09**
**Sprint 25a — implemented same session, no sprint planning precursor**

---

## Story — Action buttons are always reachable without horizontal scrolling

**As a** payroll bureau operator,
**I want** the "View Contracts" action button to always be visible on each employee row,
**So that** I can navigate to an employee's contracts without having to scroll right past wide
name/number columns that push the action off-screen on standard laptop viewports.

### Acceptance Criteria

**Happy path — action column always visible:**
- **Given** the Employees page is open at a 1024px-wide viewport with several employees listed,
  **when** I look at any row, **then** the action button column is visible on the right-hand
  side without horizontal scrolling.
- **Given** the table has a horizontal scroll on wide content, **when** I hover a row,
  **then** the sticky actions cell highlights consistently with the rest of the row (no
  colour mismatch between the scrolled columns and the pinned column).

**No regression:**
- All existing column data (name, number, status, grade, contract dates) remains accessible
  by scrolling horizontally — only the actions column is pinned.

### Out of Scope
- Responsive column hiding for very narrow viewports (not required for bureau desktop use)

### Implementation Summary

**Root cause:** The last table column (actions) was a standard `<td>` with no position
pinning — at 1024px the combined column widths pushed it off-screen.

**Fix:** CSS sticky column pinning on both header and body cells.
- `frontend/src/pages/Employees.tsx` — last `<th>` gets `sticky right-0 bg-gray-50` with a
  soft left-side box shadow `shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.06)]`.
- Each row `<tr>` gains a `group` class; the actions `<td>` gets
  `sticky right-0 bg-white group-hover:bg-slate-50 transition-colors` so the hover state
  matches the rest of the row regardless of scroll position.

### Business Risk / Impact
- **Cost of not doing:** Operator on a 13" laptop cannot see or click "View Contracts" without
  discovering horizontal scroll — a discoverability failure on a key navigation action.
- **Cost of doing it wrong:** Low — purely presentational, no data logic involved.

### Priority
**P2** — operator productivity / discoverability.
