# UI/UX Decisions Log

Running record of design decisions, component conventions, and interaction
patterns across all sprints. Read this at the start of any sprint with frontend
work. Add to it whenever a non-obvious choice is made.

---

## How to use this file

- **New pattern decided** → add an entry under the relevant section
- **Gotcha discovered** → add under Component Gotchas with sprint reference
- **Pattern overturned** → strike through the old entry, add the new one with reason

---

## Interaction Patterns

### SlideOver — single vs multi-step
SlideOvers are single-step panels. They do not have internal step navigation.
If a flow requires multiple steps, use a wizard modal (not yet implemented) or
break it into sequential SlideOvers. This keeps the panel lightweight and
scannable.
_Decided: Gate 3_

### Inline forms vs SlideOver
Primary record creation always opens a SlideOver, never an inline form row.
Inline editing (quantity, status) is acceptable for single-field changes
directly in a table cell.
_Decided: Gate 3 DD-3_

### Multi-row data entry (INP-MULTI-1, Sprint 27)
When an operator adds multiple records that share a common anchor field
(e.g. the same employee), use a **line-item entry** pattern inside a single
SlideOver:
- The anchor field (employee) sits above the row table as a standalone full-width select
- The row table uses raw `<input>` / `<select>` elements styled to DS tokens — NOT DS components inside cells (see Component Gotchas)
- Period auto-inherits from the previous row when a new row is added
- Submit button label reflects the count: "Add N inputs"
- Edit mode for a single existing record stays as a single-field form (different context)

_Decided: Sprint 27 · Pattern source: invoice line-item builders (Xero, QuickBooks)_

### Status-aware CTAs — READY vs incomplete-setup states
When a workspace is not yet LIVE, two fundamentally different states must be treated differently:

| Status | User mental model | Banner variant | Action |
|---|---|---|---|
| `READY` | "Setup is done, I just need to flip a switch" | `success` | "Activate Workspace →" — inline ConfirmDialog, no navigation |
| Pre-READY (DRAFT, STRUCTURE_DEFINED, etc.) | "I have more work to do" | `info` | "Continue Setup →" — navigate to /setup wizard |

Never use the same copy ("Continue Setup") for both — it misleads the READY operator into thinking their work is incomplete.
_Decided: Fix sprint 2026-06-13 (WS-ACTIVATE-2)_

### Activation CTAs — consistent pattern across surfaces
The READY → LIVE activation action appears on three pages (WorkspaceConfig, PayrollRuns, WorkspaceSetup). All three use the same ConfirmDialog → success/error AlertBanner flow:
- Button label: "Activate Workspace →"
- ConfirmDialog title: "Activate workspace?"
- ConfirmDialog body must state: "Configuration can still be edited at any time." — this is the key anxiety-reducer; without it operators hesitate
- ConfirmDialog confirm label: "Activate →" (not "Confirm" — name the outcome)
- Not destructive styling — activation is not a delete operation
- Post-activation: optimistic local state update; no page reload
_Decided: Fix sprint 2026-06-13 (WS-ACTIVATE-1/2/3)_

### Sub-component activation banners (ExistingConfigView pattern)
When a component receives workspace/status as a prop (cannot mutate it), use a local `activateSuccess` bool to switch between the pre-activation CTA banner and the post-activation confirmation banner. The prop status stays stale but the UI reflects the new state correctly. This avoids prop drilling or context coupling for a simple one-way transition.
_Decided: Fix sprint 2026-06-13 (WS-ACTIVATE-3)_

### Confirmation for destructive actions
Destructive actions (delete, deactivate) require a confirmation step. Use an
inline confirmation row expansion or a minimal AlertBanner with confirm/cancel
inline — not a separate modal, as modal-over-SlideOver creates z-index chaos.
_Decided: Sprint 8_

### Empty states
Every list/table view must have a purposeful empty state with:
- Icon (relevant to the content type)
- Heading ("No inputs yet")
- Specific CTA ("Add your first input")
Not: generic "No data found" text.
_Decided: Gate 3 DD-5_

---

## Visual / Layout Conventions

### Upload mode selector
When a page offers multiple upload paths (e.g. native file vs template), use a
2-column card grid selector above the content area. Selected card uses
`border-brand bg-blue-50` with a filled check circle top-right.
The mode selector stays visible even after a file is dropped so the operator
can switch without reloading.
_Decided: Sprint 27_

### Status badges
Always `color + text` — never color alone. Use `--radius-badge` (24px) for
pill shape. See `tokens.css` for the full semantic color set.
_Decided: Gate 3 DD-12_

### Disabled container blocks
When a section of a form is unavailable (e.g. row table before employee is
selected), apply `opacity-40 pointer-events-none` to the container AND show
an `AlertBanner variant="info"` above explaining why. Do not rely on disabled
styling alone — operators need to understand the dependency.
_Decided: Sprint 27 INP-MULTI-1_

---

## Component Gotchas

### DS inputs inside table cells — NEVER
`NumberInput`, `TextInput`, `DateInput` are full-width block components with
label markup baked in. Using them inside a `<td>` breaks the row height and
creates nested label/input nesting issues. Instead use raw `<input>` elements
with DS-consistent styling:
```
className="h-[var(--height-md)] w-full rounded-[var(--radius-input)]
  border border-gray-200 bg-white px-2.5 text-sm
  focus:outline-none focus:ring-1 focus:ring-brand"
```
Add `aria-label="..."` since there is no visible label.
_Discovered: Sprint 14 · Reinforced: Sprint 27_

### Full-width interactive elements inside padded Cards — NEVER
A `Card` component has internal padding. A full-width toggle header, accordion,
or collapsible section placed as a direct child creates a dead-click zone
around the perimeter. Use the CSS variable card pattern directly instead:
```tsx
<div style={{ borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)' }}
  className="overflow-hidden">
  <button className="w-full ...">...</button>
</div>
```
_Discovered: Sprint 25_

### Action link adjacent to next field label — NEVER
An inline link placed directly below a dropdown (e.g. "Bulk upload ↗") with no
gap reads as the label for the next input field. Always add `mb-4` (16px) below
the link so proximity clearly associates it with the field above.
_Discovered: Sprint 26_

### AlertBanner.description accepts ReactNode
`description` is typed as `ReactNode` — you can pass a `<span>` or list, not
just a plain string. Use this to inline links or formatted error lists.
_Discovered: Sprint 16_

### ProgressBar uses `percent` not `value/max`
The DS `ProgressBar` component takes a single `percent` prop (0–100).
It does not accept `value` and `max` separately.
_Discovered: Sprint 16_

### Card has optional `title` and `action` props
These render a standard card header. Using them keeps heading typography
consistent across cards without re-implementing the header pattern.
_Discovered: Sprint 16_

---

## Column Mapping Panel (native upload flows)

### Duplicate targets — per flow
The `ColumnMappingPanel` deduplicated targets by default (employee upload: each
system field maps to at most one client column). For **period inputs upload**,
pass `allowDuplicateTargets={true}` — multiple monthly columns legitimately
share the same `input_code`.
_Decided: Sprint 27_

### Auto-deduplication of repeated column blocks
Client files often contain a main input block and a reporting/calculation block
with the same headers. `buildInputMappings` deduplicates on `{period, input_code}`:
first occurrence wins, subsequent occurrences are auto-excluded. Operator can
reassign from the Excluded section if needed.
_Decided: Sprint 27_

---

## Data Entry Conventions

### Quantity = cell_value ÷ header_rate (period inputs)
In a native period inputs upload, the spreadsheet cell contains the amount
earned (e.g. ₦20,000). The column header encodes the per-unit rate via
`@N1000.00`. Quantity = cell ÷ rate. If no rate is in the header, the raw cell
value is used as a fallback.
_Decided: Sprint 27 (overturned original "cell = quantity" assumption)_

### Fuzzy token matching for column headers
Period input column headers use Levenshtein distance ≤ 2 (minimum token
length 4) for typo-tolerant matching. Shorter tokens require exact match to
prevent false positives. Threshold 2 handles real-world typos: "WEEKDEND" →
"WEEKEND", "WEEKENE" → "WEEKEND".
_Decided: Sprint 27_
