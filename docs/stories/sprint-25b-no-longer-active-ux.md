# Story: Employees Page — "No Longer Active" Toggle Fix + Contract Ended / Deactivated Sub-Groups
**Written in retrospective — 2026-06-09**
**Sprint 25b — implemented same session, no sprint planning precursor**

---

## Story A — "No Longer Active" section collapses and expands reliably on click

**As a** payroll bureau operator,
**I want** clicking anywhere on the "No Longer Active" section header to reliably toggle
the section open or closed,
**So that** I can review ended and deactivated employees without fighting a non-responsive
UI element.

### Acceptance Criteria

**Happy path — full-width toggle:**
- **Given** the "No Longer Active" section is collapsed, **when** I click anywhere on the
  section header bar (including near the edges), **then** the section expands.
- **Given** the section is expanded, **when** I click the header bar again, **then** it
  collapses cleanly.
- The toggle arrow rotates 180° when open and returns to 0° when closed.

**No dead zones:**
- Clicking the very edge of the header card registers as a toggle — no dead zone around
  the perimeter.

### Implementation Summary

**Root cause:** The section was wrapped in `<Card padding="sm">` which applies `p-4` (16px)
padding around its children. The toggle `<button>` was a child of the card, so it only
spanned the inner padded area — clicks on the 16px border ring hit the Card's own padding
and were ignored.

**Fix:** Replaced `<Card>` with a padless `<div>` using CSS variable card styling directly:
```tsx
<div style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
  className="bg-white overflow-hidden">
  <button className="w-full px-4 py-3 flex items-center justify-between ...">
```
The `overflow-hidden` on the wrapper ensures the rounded corners clip the button's full-width
hover background correctly.

- `frontend/src/pages/Employees.tsx` — "No Longer Active" section header card replaced.

---

## Story B — Subtitle chips distinguish "contract ended" from "deactivated"

**As a** payroll bureau operator,
**I want** the Employees page subtitle to show separate "N contract ended" and "N deactivated"
counts as clickable chips,
**So that** I can immediately see how many employees are in each terminal state and jump
directly to that section with one click.

### Acceptance Criteria

**Happy path — two separate chips:**
- **Given** there are employees with ended contracts AND employees manually deactivated,
  **when** I view the Employees page subtitle, **then** I see two separate chips:
  `· N contract ended · N deactivated`.
- **Given** only one category is non-empty (e.g. no deactivated employees),
  **then** only the relevant chip appears — the other is hidden.

**Click behaviour — auto-expand and scroll:**
- **Given** the "No Longer Active" section is collapsed, **when** I click either chip,
  **then** the section expands AND the page scrolls to bring it into view.
- **Given** the section is already expanded, **when** I click a chip, **then** the page
  scrolls to the section (no unintended collapse).

### Implementation Summary

- `frontend/src/pages/Employees.tsx` — subtitle area: single "no longer active" chip
  replaced with two conditional `<button>` elements, each with `onClick` that calls
  `setShowEnded(true)` and `endedRef.current?.scrollIntoView(...)`.
- `ended` = employees where `is_ended === true`.
- `deactivated` = employees where `status === 'INACTIVE' && !is_ended`.
- Both sub-groups render inside the expanded "No Longer Active" section, separated by a
  divider.

### Business Risk / Impact
- **Cost of not doing:** Operator sees a single opaque count with no distinction between
  contract expiry (expected) and manual deactivation (deliberate HR action) — two very
  different operational states conflated in one chip.
- **Cost of doing it wrong:** Low — display-only change, no data mutation.

### Priority
**P2** — operator clarity.
