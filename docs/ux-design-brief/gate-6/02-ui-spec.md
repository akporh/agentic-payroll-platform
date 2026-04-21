# Gate 6 — UI Specification: Post-Onboarding Workspace Configuration Management

## Design System Constraints

All components from the existing design system: `ContentHeader`, `Card`, `Btn`, `StatusBadge`, `AlertBanner`, `SlideOver`, `ExpandableRow`, `Breadcrumb`, `IconBtn`. No new primitives needed.

- Spacing: 8pt grid (4 / 8 / 12 / 16 / 24 / 32px)
- Edit affordances: `variant="secondary" size="sm"` — present but subordinate to content
- Radius: `var(--radius-card)` on cards, `rounded` on inputs
- All edit icon buttons: 44×44px touch target minimum, `aria-label="Edit [name/code]"`

---

## Section Header Pattern (all cards)

```
┌─ Card ─────────────────────────────────────────────────────┐
│  SECTION LABEL              [Add X ▸]  [Edit ▸]           │
│  ───────────────────────────────────────────────────────── │
│  content                                                    │
└─────────────────────────────────────────────────────────────┘
```

- Label: `text-xs font-semibold text-gray-500 uppercase tracking-wide`
- Buttons: `<Btn variant="secondary" size="sm">` — right-aligned via `flex justify-between items-center`
- Single-entity sections (Pay Cycle): one "Edit" button
- List sections (Grades, Designations, Rules, Overrides): one "Add [X]" button + per-row edit icon

---

## Per-Row Edit Pattern

```
│  Grade Code      Description                    [✎]       │
```

- Edit icon: pencil SVG 16px, gray-400 → gray-700 on hover
- `<button aria-label="Edit [code]" className="p-2.5 rounded hover:bg-gray-100">` — 44×44px effective target
- Placed at far right of each row

---

## Read-Only Code Input (grade/designation immutability)

```html
<div class="relative">
  <input value="GRADE_CODE" disabled
    class="w-full bg-gray-100 text-gray-500 rounded px-3 py-2 pr-8 text-sm cursor-not-allowed" />
  <LockIcon class="absolute right-2.5 top-2.5 w-4 h-4 text-gray-400" />
</div>
```

---

## Pay Cycle Edit SlideOver

```
┌─ SlideOver: Edit Pay Cycle ───────────────────────────────┐
│                                                            │
│  Frequency                                                 │
│  [Monthly              ▾]                                  │
│                                                            │
│  Run Day      Cutoff Day    Payment Day                    │
│  [  25  ]     [  20  ]      [  28  ]                       │
│                                                            │
│  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄   │
│  ⓘ Run day, cutoff day, and payment day are stored for    │
│    reference only and are not currently used in payroll    │
│    calculations.                                           │
│                                                            │
│  ─────────────────────────────────────────────────────── │
│                              [Cancel]  [Save Changes →]   │
└───────────────────────────────────────────────────────────┘
```

- Informational note: `text-xs text-gray-500` with `ⓘ` prefix
- Day inputs: `type="number" min="1" max="31"` — 80px width
- 409 error: AlertBanner (error) at top of SlideOver

---

## Grade / Designation SlideOvers

**Add Grade:**
```
┌─ SlideOver: Add Grade ────────────────────────────────────┐
│  Grade Code *                                              │
│  [                    ]  ← required, uppercased            │
│                                                            │
│  Description                                               │
│  [                    ]  ← optional                        │
│  ─────────────────────────────────────────────────────── │
│                              [Cancel]  [Add Grade →]      │
└───────────────────────────────────────────────────────────┘
```

**Edit Grade:**
```
┌─ SlideOver: Edit Grade ───────────────────────────────────┐
│  Grade Code                                                │
│  [🔒 GRADE_CODE         ]  ← read-only, grey bg           │
│                                                            │
│  Description                                               │
│  [  Senior Associate   ]  ← editable                      │
│  ─────────────────────────────────────────────────────── │
│                              [Cancel]  [Save Changes →]   │
└───────────────────────────────────────────────────────────┘
```

---

## Salary Definition Edit SlideOver (most complex)

```
┌─ SlideOver: Edit Salary Definition ───────────────────────┐
│ "Associate Director — AD"                                  │
│                                                            │
│ ┌─ AlertBanner (info) ──────────────────────────────────┐ │
│ │ Changes apply from the next payroll run only. They    │ │
│ │ do not affect runs already in progress.               │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                            │
│  Component          Amount (₦)                            │
│  ─────────────────────────────────                        │
│  BASIC              [  200,000  ]              (hidden)   │
│  HOUSING            [   80,000  ]              (hidden)   │
│  TRANSPORT          [   40,000  ]              (hidden)   │
│  MEAL_ALLOWANCE     [   25,000  ]              [✕]        │
│  ─────────────────────────────────                        │
│  + Add Component                                           │
│    [CODE      ] [  Amount  ] [Add]                        │
│                                                            │
│  ─────────────────────────────────────────────────────── │
│                              [Cancel]  [Save Changes →]   │
└───────────────────────────────────────────────────────────┘
```

- Amount inputs: right-aligned, `₦` prefix label, `type="number" min="0.01" step="0.01"`
- Remove button: shown only for non-mandatory components — hidden (not disabled) for BASIC/HOUSING/TRANSPORT
- "Add Component" section: code input (40% width) + amount input (50%) + "Add" Btn (sm)
- **409 error (run in flight):** AlertBanner (error) at top: "This salary definition cannot be edited while a payroll run is in progress or pending approval."
- Footer: sticky, `[Cancel]` secondary left, `[Save Changes →]` primary right

---

## Payroll Rules Table (updated)

```
┌──────────────────┬──────────────────┬──────────────────┬──────────────────────┐
│ Name             │ Type             │ Status  ⓘ        │                      │
├──────────────────┼──────────────────┼──────────────────┼──────────────────────┤
│ Basic Overtime   │ Unit × Rate      │ ● ACTIVE         │ [Deactivate]         │
│ Shift Bonus      │ Fixed Amount     │ ● INACTIVE       │ [Activate]           │
└──────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```

- Status column header: `ⓘ` tooltip: "Current activation state. Historical state per run is visible in the Run Trace."
- Status: `<StatusBadge status="ACTIVE|INACTIVE" size="sm">`
- Toggle button: `<Btn variant="secondary" size="sm">` with text label — not icon-only (compliance-critical action needs visible label)
- Post-toggle: dismissible AlertBanner (info) below the table

---

## Component Override SlideOver

```
┌─ SlideOver: Edit Component Override ──────────────────────┐
│ PAYE — Income Tax Deduction                                │
│                                                            │
│  Status                                                    │
│  [● Enabled]  ←  primary Btn when enabled                 │
│  [○ Disabled] ←  secondary Btn when disabled              │
│                                                            │
│  [AlertBanner warning — appears when set to Disabled]     │
│  "Disabling this component means it will not be           │
│   calculated for any employee in the next payroll run."   │
│                                                            │
│  Proration Strategy                                        │
│  [Full Month          ▾]                                   │
│                                                            │
│  ─────────────────────────────────────────────────────── │
│                              [Cancel]  [Save Changes →]   │
└───────────────────────────────────────────────────────────┘
```

- On 422 (statutory): AlertBanner (error) at **top** of SlideOver (above Status field), not inline below toggle
- Proration select: native `<select>` at 36px height matching button height scale

---

## Empty States

| Section | Copy | CTA(s) |
|---------|------|--------|
| Component Overrides | "No overrides configured. Statutory components use platform defaults." | `<Btn>Add Override</Btn>` |
| Payroll Rules | "No payroll rules defined for this workspace." | `<Btn>Add Rule</Btn>` + `<Btn variant="secondary">Update Config</Btn>` |
| Salary Definitions | "No salary definitions. Upload a configuration file to get started." | `<Btn>Update Config</Btn>` |

---

## Accessibility

- All icon buttons: `aria-label="Edit [entity name/code]"`
- All SlideOvers: focus trap on open, Escape closes, focus returns to trigger on close
- Error messages: associated with form fields via `aria-describedby`
- Color not used alone to convey meaning (StatusBadge uses dot + text)
- Touch targets: minimum 44×44px on all interactive elements
