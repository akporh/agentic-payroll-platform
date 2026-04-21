# Gate 1 — Component Inventory

> Every reusable UI component needed across the 18 screens.
> Grouped by category. Gate 2 will produce the coded implementation of each.

---

## Navigation Components

### NAV-1 — Global Top Bar
**Used on:** All screens
**Slots:** Logo/brand | Workspace picker (dropdown) | User menu (dropdown) | Help icon
**States:** Default | Workspace context active | No workspace (bureau level)
**Notes:** Workspace picker shows "Bureau" when at bureau level. Switches to workspace name when inside a workspace. Backdrop blur on scroll.

### NAV-2 — Workspace Sidebar
**Used on:** All workspace-level screens
**Slots:** Workspace name + status badge | Nav sections (Payroll, People, Settings) | Nav items per section | Active state indicator
**States:** Collapsed (icon only, 64px) | Expanded (label + icon, 240px) | Mobile (drawer/overlay)
**Sections:**
- Payroll: Runs, Inputs
- People: Employees
- Settings: Config, Payroll Config, Holidays, Rate Codes
- Setup Wizard (conditional — only if not LIVE)

### NAV-3 — Breadcrumb
**Used on:** All screens below bureau level
**Format:** Bureau Name / Workspace Name / Section / [Detail]
**Behaviour:** Each crumb is a link. Last crumb is non-linked.

### NAV-4 — Tab Bar
**Used on:** Run Detail (Results | Reconciliation | Timeline | Audit Log)
**States:** Active tab (underline + weight) | Inactive tab | Disabled tab
**Notes:** Active tab state must be immediately obvious. No icon overload — tabs are text-only.

### NAV-5 — Onboarding Stepper
**Used on:** Workspace Setup (S3)
**Format:** Numbered steps with connecting line | Completed (filled circle + check) | Current (filled, animated) | Upcoming (outline)

---

## Status and State Components

### STS-1 — Status Badge
**Used on:** Bureau Dashboard, Runs List, Run Header, Employee List
**Variants:** 
- LIVE (green) | READY (blue) | DRAFT/incomplete (grey)
- CALCULATING (blue, pulse) | PARTIAL (amber) | CALCULATED (teal) | APPROVED (purple) | LOCKED (indigo) | PAID (green dark)
- MATCHED (green) | MISMATCH (red) | RESOLVED (neutral)
- ACTIVE employee (green dot) | INACTIVE (grey dot)
- SUCCESS result (green) | FAILED result (red)
**Size variants:** Small (inline in tables) | Default (cards/headers)

### STS-2 — Alert Banner
**Used on:** Bureau Dashboard, Runs List, Run Results (PARTIAL)
**Variants:** Warning (amber) | Error (red) | Info (blue) | Success (green)
**Slots:** Icon | Title | Description | Action link/button | Dismiss (optional)

### STS-3 — Progress Indicator (Onboarding)
**Used on:** Workspace Setup, Workspace Dashboard (incomplete workspaces)
**Format:** Linear progress bar with percentage | Label showing what's complete | What's missing

### STS-4 — Loading / Skeleton
**Used on:** All data tables and summary cards while fetching
**Format:** Shimmer skeleton rows matching the height and layout of the real content
**Never:** Spinners in the centre of a full page. Only spinners inside buttons.

---

## Data Display Components

### DAT-1 — Summary Cards (KPI Row)
**Used on:** Payroll Results header, Workspace Dashboard
**Slots:** Label | Value (large) | Sub-label (optional)
**Variants:** 4-up row (Results page) | 3-up row (Workspace Dashboard)
**Notes:** Monetary values right-aligned, formatted with ₦ and comma separators. Never show amounts when status is not SUCCESS.

### DAT-2 — Data Table
**Used on:** Runs List, Results table, Employee List, Input Inbox, Holiday List, Rate Code List, Audit Log
**Features:** Column headers (sortable where applicable) | Row hover state | Expandable rows | Sticky header on scroll | Empty state (see EMP-1) | Selection (for future bulk actions)
**Notes:** Text columns left-aligned. Monetary columns right-aligned. Status columns centre-aligned.

### DAT-3 — Expandable Row
**Used on:** Payroll Results (employee pay breakdown + component trace)
**Trigger:** Click row or chevron icon
**Content:** Sub-table of components (EARNINGS section | DEDUCTIONS section | Trace section)
**Animation:** Smooth expand, 200ms ease-out

### DAT-4 — Component Trace Row
**Used on:** Payroll Results expandable section
**Columns:** Component code | Method | Status (✓/✕) | Amount | Note | Warning (if present)
**States:** SUCCESS (normal) | FAILED (red text, error note) | No trace available (legacy path note)

### DAT-5 — Reconciliation Summary Card
**Used on:** Reconciliation screen
**Variants:** Awaiting (neutral) | MATCHED (green border) | MISMATCH (red border, variance prominent) | RESOLVED (neutral with resolution details)

### DAT-6 — Timeline / Audit Log Row
**Used on:** S16 (Timeline) and S17 (Audit Log)
**Columns:** Timestamp | Action/event | Actor | Details
**Notes:** Monospaced font for timestamps. Read-only, no interactive elements.

---

## Form Components

### FRM-1 — Text Input
**Used on:** All forms
**States:** Default | Focus (blue outline) | Filled | Error (red outline + message) | Disabled
**Notes:** Always has a visible label above. Placeholder text is supplementary only, never the label.

### FRM-2 — Number Input
**Used on:** Run form (working_days), Input form (quantity), Reconciliation form (actual_payment)
**Variants:** Plain number | Currency (₦ prefix)
**Validation:** Quantity must be ≥ 0 (client-side). Currency formats on blur.

### FRM-3 — Searchable Dropdown / Select
**Used on:** Employee picker, Input code picker, Grade picker, Rate code picker, Country picker
**Features:** Type to filter | Selected value shown | Clear button | Loading state for async data
**Notes:** Input code dropdown groups by category (EARNING, DEDUCTION, INFORMATION) with section headers.

### FRM-4 — Date Picker
**Used on:** Period dates, reference period, holiday date, effective_from fields
**Format:** Shows month/year label. Period pickers for payroll run pre-fill to current month.
**Month-only variant:** For reference_period field (shows "Mar 2026", not a specific day).

### FRM-5 — Radio Group
**Used on:** Period type, Run type, PH conflict rules, PH mode
**Behaviour:** One selection always active. Each option has a label and optional description.
**Notes:** PH conflict rule radio groups must include a plain-English description of what each choice means.

### FRM-6 — Toggle (Active/Inactive)
**Used on:** Component overrides (is_active), potentially Employee status
**States:** On (green) | Off (grey)
**Notes:** Changing a component override should not require saving the whole page — each toggle saves inline.

### FRM-7 — File Drop Zone
**Used on:** Bulk Input Upload (S8), JSON Onboarding (S4), Bulk Contract Update
**States:** Idle (dashed border) | Drag-over (filled border, colour change) | Processing | Success | Error

### FRM-8 — Textarea
**Used on:** Reconciliation resolution (notes field), JSON Onboarding editor
**States:** Default | Focus | Error | Disabled

---

## Action Components

### ACT-1 — Primary Button
**Used on:** Every screen — the single dominant action
**States:** Default | Hover | Active/Pressed | Loading (spinner replaces label) | Disabled
**Rules:** ONE per screen section. Never more than one primary button in the same visual region.

### ACT-2 — Secondary Button (Outline)
**Used on:** Cancel actions, secondary actions alongside primary
**States:** Same as primary
**Notes:** Always smaller visual weight than primary. Paired with primary on the right.

### ACT-3 — Destructive Button
**Used on:** Delete actions, Mark as Paid (irreversible)
**Colour:** Red
**Always paired with:** A confirmation dialog (CONF-1) before executing

### ACT-4 — Ghost / Text Button
**Used on:** Low-priority actions, navigation links within content (e.g. "View Inputs →")
**Notes:** No border, no background. Looks like a link but sized like a button for touch targets.

### ACT-5 — Icon Button
**Used on:** Delete row (🗑), expand/collapse row (▾), dismiss alert (✕)
**Rules:** Must have aria-label. 44×44px minimum touch target.

### ACT-6 — Download Button
**Used on:** CSV exports (Bank Upload, PAYE, Pension), error report download, template download
**Variant:** Shows ↓ icon + label. Disabled state when exports not available (status gating).
**On click:** Triggers direct file download (streaming response).

---

## Feedback Components

### FBK-1 — Toast Notification
**Used on:** All success/error responses to user actions
**Variants:** Success (green) | Error (red) | Warning (amber) | Info (blue)
**Position:** Bottom-right, stacks
**Duration:** 4s auto-dismiss (errors persist until dismissed manually)
**Notes:** Toast messages are short (1 sentence). Don't use for multi-part errors — use inline form validation instead.

### FBK-2 — Inline Field Error
**Used on:** All form fields on validation failure
**Format:** Red text below the field, with ✕ icon. Replaces helper text.
**Behaviour:** Appears on blur (not on every keystroke). Cleared on next valid input.

### FBK-3 — Confirmation Dialog (Modal)
**Used on:** Mark as Paid (irreversible), Lock Run, Delete operations
**Slots:** Title (what is happening) | Body (consequences) | Cancel button | Confirm button (destructive for irreversible)
**Rules:** Destructive confirms use red button. Both buttons are named specifically — never "OK" / "Cancel" alone.

### FBK-4 — Empty State
**Used on:** Every list/table screen when no data
**Slots:** Illustration/icon | Headline (what's empty) | Body (why and what to do) | CTA button
**Rules:** Never just "No data found". Always include an action.

---

## Layout Components

### LAY-1 — Page Shell
**Used on:** All workspace-level screens
**Structure:** Top bar | Sidebar | Main content area | (optional) Right panel/drawer

### LAY-2 — Content Header
**Used on:** All section pages
**Slots:** Page title | Sub-title/description | Primary action (top-right)

### LAY-3 — Slide-Over (Drawer)
**Used on:** Add Input form, Edit Employee contract
**Behaviour:** Slides in from right, overlays content (not full-page replace)
**Width:** 400–480px. Overlay darkens background.
**Close:** ✕ button, Escape key, clicking outside.

### LAY-4 — Modal (Centred)
**Used on:** Create Workspace, Confirmation dialogs
**Width:** 480px (forms) | 640px (content)
**Focus trap:** Tab cycles within modal only.

### LAY-5 — Split Panel
**Used on:** JSON Onboarding (editor | response)
**Layout:** 50/50 or 60/40 horizontal split.
