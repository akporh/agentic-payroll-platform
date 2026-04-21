# S3 — Workspace Setup (Onboarding Stepper)

**Actor:** Bureau Administrator (Chidi), HR Admin (Ngozi)
**Emotional state:** Setting things up properly — methodical, doesn't want to re-do steps

---

## Layout — Stepper with progress indicator

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager    [Eagle Transport ▾]                    [Chidi ▾]  [?]   │
├──────────────────────────────────────────────────────────────────────────── │
│                                                                            │
│  Workspace Setup — Eagle Transport                                         │
│                                                                            │
│  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━○━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━○  │
│  1 Structure              2 Compensation                3 Rules & Go Live  │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  STEP 1 — Structure                                                        │
│  Define how your organisation is structured.                               │
│                                                                            │
│  ── Pay Cycle ───────────────────────────────────────────────────────     │
│  Frequency    ○ Monthly   ○ Fortnightly   ○ Weekly                        │
│  Run day      [25    ]  ─  employees paid by day [28    ]                 │
│  Input cutoff [20    ]  (last day inputs are accepted)                     │
│                                                                            │
│  ── Grades ─────────────────────────────────────────────────────────     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Code           Description                                [✕ Remove]│  │
│  │ STEP_1         Step 1 – Junior                                      │  │
│  │ STEP_2         Step 2 – Mid-level                                   │  │
│  │ STEP_3         Step 3 – Senior                                      │  │
│  │ MANAGER        Management Grade                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│  [+ Add Grade]                                                             │
│                                                                            │
│  ── Designations ───────────────────────────────────────────────────     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Code           Description                                [✕ Remove]│  │
│  │ DRIVER         Driver                                               │  │
│  │ OFFICER        Administrative Officer                               │  │
│  │ SUPERVISOR     Supervisor                                           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│  [+ Add Designation]                                                       │
│                                                                            │
│                                          [Next: Compensation →]            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 2 — Compensation (Salary Definitions)

```
│  STEP 2 — Compensation                                                     │
│  Define salary templates. Each employee is assigned one.                   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Code    Name              BASIC        HOUSING    TRANSPORT  [Edit] │  │
│  │ STEP_1  Step 1 – Junior   ₦ 80,000     ₦ 20,000   ₦ 10,000        │  │
│  │ STEP_2  Step 2 – Mid      ₦ 120,000    ₦ 30,000   ₦ 15,000        │  │
│  │ STEP_3  Step 3 – Senior   ₦ 180,000    ₦ 45,000   ₦ 20,000        │  │
│  │ MANAGER Management        ₦ 350,000    ₦ 80,000   ₦ 30,000        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│  [+ Add Salary Definition]                                                 │
│                                                                            │
│  [← Back]                               [Next: Rules & Go Live →]         │
```

---

## Step 3 — Rules & Go Live (Payroll Rules + Component Overrides)

```
│  STEP 3 — Rules & Go Live                                                  │
│  Configure variable pay rules and then go live.                            │
│                                                                            │
│  ── Payroll Rules ───────────────────────────────────────────────────     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Name                Type        Method         Active               │  │
│  │ Overtime Pay        EARNING     PERCENTAGE      ✓                   │  │
│  │ Leave Without Pay   DEDUCTION   WORKING_DAYS    ✓                   │  │
│  │ Transport Claims    EARNING     FLAT_AMOUNT      ✓                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│  [+ Add Rule]                                                              │
│                                                                            │
│  ── Statutory Component Overrides ───────────────────────────────────    │
│  These are the statutory deductions. You can customise amounts here.      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Component              Active   Override Amount      Proration      │  │
│  │ PAYE                   ✓        —                    —              │  │
│  │ Pension (Employee 8%)  ✓        —                    FULL_MONTH     │  │
│  │ NHF (2.5% basic)       ✓        —                    —              │  │
│  │ Health Insurance       ✓        ₦ 2,500 /month       —              │  │
│  │ Development Levy       ✓        ₦ 100 /year          —              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  [← Back]                                    [Preview Onboarding →]       │
```

---

## Preview + Commit Panel

```
│  ── Preview Results ─────────────────────────────────────────────────    │
│                                                                           │
│  ┌─ ✓ Validation passed ──────────────────────────────────────────────┐  │
│  │  3 warnings (non-blocking)                                         │  │
│  │                                                                    │  │
│  │  ⚠ STEP_1 salary definition has no components defined             │  │
│  │  ⚠ No payroll rules for information-type inputs                   │  │
│  │  ⚠ Health insurance override not set — using statutory default    │  │
│  │                                                                    │  │
│  │  Preview looks good?                                               │  │
│  │                                     [Commit Workspace →]          │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Or if errors:                                                            │
│  ┌─ ✕ Validation failed ──────────────────────────────────────────────┐  │
│  │  2 errors must be fixed before committing                          │  │
│  │                                                                    │  │
│  │  ✕ Pay cycle is missing (required for payroll runs)               │  │
│  │  ✕ No salary definitions found                                    │  │
│  │                                              [← Fix Issues]       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
```

---

## Post-Commit — Go Live

```
│  ✓  Workspace configured successfully!                                    │
│                                                                           │
│  Eagle Transport is READY.                                                │
│  All configuration has been saved.                                        │
│                                                                           │
│  Ready to go live?                                                        │
│  Going live enables payroll runs for this workspace.                      │
│  You can always return to settings to adjust configuration.               │
│                                                                           │
│                [Not yet — I'll configure more]   [Go Live →]             │
```

---

## Alternative Path — JSON Onboarding (S4)

```
│  Advanced: Have a structured JSON file?                                   │
│  [→ Switch to JSON onboarding]                                            │
```
Offered as a small link at the bottom of the stepper, not a prominent CTA.
