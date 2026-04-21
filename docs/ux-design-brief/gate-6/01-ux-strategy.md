# Gate 6 — UX Strategy: Post-Onboarding Workspace Configuration Management

## Target User

**Payroll bureau operator** — seated at a desktop, managing 5–20 client workspaces. Arrives on this page with a specific correction to make (wrong cutoff day, new salary band, suspend a bonus rule). Emotional state: methodical and precise, not exploratory. They are not browsing — they know what they need to fix.

## Core Insight

Operators already trust WorkspaceConfig as a reference page. Edit affordances must not disrupt that trust. Discoverability must be high; accidental change risk must be zero.

## Key UX Decisions

### 1. Section-level persistent edit affordances — not hover-reveal

Each Card section header has a persistent "Edit" or "Add" button (secondary, sm). Never hidden behind hover.

**Why:** Operators scan in an F-pattern. Hover-only reveals break the scan and increase discovery time. Payroll professionals do not mouse-hunt.

### 2. All edits via SlideOver — payroll rule toggle via confirmation dialog

Inline editing creates accidental-save risk and unclear save scope. SlideOver provides a clear edit/cancel contract — operator knows exactly what is changing and can abandon without consequence.

**Exception:** Payroll rule is_active toggle is a single discrete action — uses a confirmation dialog directly (no SlideOver needed).

### 3. Code immutability shown visually — not via tooltip

Grade and designation codes are rendered in a read-only styled input (grey background + lock icon). Makes immutability obvious on first sight without requiring discovery of a tooltip.

### 4. "Next run only" warning inside salary def SlideOver — not page-level

Warning about next-run impact appears inside the SlideOver as an AlertBanner (info) at the top — contextual to the action, not ambient noise that trains operators to ignore it.

### 5. Statutory component disable: server-side 422 is the real guard

Frontend inline warning is a secondary signal. The API enforces the restriction (D-ARCH-2). SlideOver shows the 422 in an AlertBanner (error) at the top — not just below the toggle.

### 6. Salary def edit-lock 409: name the blocking run

When a salary def edit is blocked (D-ARCH-1), the 409 error message names the specific blocking run so the operator knows when they can return to make the edit.

### 7. Pay cycle informational note — inside SlideOver, not tooltip

`run_day`, `cutoff_day`, `payment_day` are not read by the execution engine. This is disclosed inside the SlideOver below the fields as grey text (text-xs). Not hidden.

### 8. Payroll rules is_active column — current state, not historical

The `is_active` column shows live management state. Historical "state at run time" is in the Run Trace (sourced from `rule_set_item` snapshots). Column header carries an info tooltip to clarify this distinction.

### 9. Post-rule-change dismissible banner

After any payroll rule toggle or add, a dismissible AlertBanner (info) appears on the main config page: "Rule changes take effect only after the rule set is re-published from Workspace Setup → Rules." Dismissed per session only.

### 10. Empty states are actionable

| Section | Empty copy | CTA |
|---------|-----------|-----|
| Component Overrides | "No overrides configured. Statutory components use platform defaults." | Add Override |
| Payroll Rules | "No payroll rules defined for this workspace." | Add Rule + Update Config |
| Salary Definitions | "No salary definitions. Upload a configuration file to get started." | Update Config |

### 11. Error recovery — SlideOver stays open

On any save failure: SlideOver remains open, values are preserved, error AlertBanner appears at the top. Operator can fix and retry without re-entering data.

### 12. Optimistic UI for rule toggle — with rollback

Payroll rule toggle updates the local state immediately on confirmation. Reverts with an error banner on the main page if the API call fails. Non-blocking.

## Biggest UX Risk

Operator edits a salary definition component amount, sees the success banner, and assumes it applies to the current in-progress run. The "next run only" AlertBanner inside the SlideOver must be at the top — not below the form where it risks being missed.

## Flows

### Edit Salary Definition (highest-risk path)
```
Config page → Click "Edit" on salary def expandable row header
  → SlideOver opens
    → [AlertBanner info] "Changes apply from the next payroll run only."
    → Component table: editable amounts, locked rows for mandatory components
    → Add Component row at bottom
    → [Save Changes] [Cancel]
      → On 409 (run in flight): error AlertBanner with blocking run name
      → On 422 (validation): field-level errors, form stays open
      → On success: SlideOver closes, card reloads, page shows success
```

### Toggle Statutory Component (compliance-sensitive)
```
Config page → Click Edit on component override row
  → SlideOver opens
    → Toggle is_active to Disabled
      → Inline AlertBanner (warning): "Disabling means not calculated next run"
    → [Save Changes]
      → On 422 (statutory_deduction): AlertBanner (error) at top of SlideOver
        "PAYE cannot be disabled. It is a statutory obligation under Nigerian law."
      → Operator cannot proceed — must keep enabled
```
