# S11 — Payroll Results

**Actor:** Payroll Operator (Adaeze), Finance Authoriser (Emeka), Compliance Officer (Tunde)
**Emotional state:** Adaeze — reviewing, checking for failures. Emeka — verifying numbers, risk-averse. Tunde — downloading CSVs.

This is the most complex screen. It changes significantly based on run status.

---

## Layout — Header + Tabs (persistent across all sub-views)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager    [Acme Corp ▾]                        [Emeka ▾]   [?]    │
├──────────────┬─────────────────────────────────────────────────────────────┤
│              │                                                             │
│ Dashboard    │  ← Payroll Runs                                             │
│              │                                                             │
│   Runs  ●   │  March 2026 Payroll                    [CALCULATED]         │
│   Inputs     │  01 Mar 2026 – 31 Mar 2026             Pay date: 28 Mar     │
│              │                                                             │
│ People       │  ┌─────────────────────────────────────────────────────┐   │
│   Employees  │  │  ₦ 24,180,000    ₦ 5,748,000    ₦ 18,432,000  142  │   │
│              │  │  Total Gross     Deductions      Net Pay       Emp  │   │
│ Settings     │  └─────────────────────────────────────────────────────┘   │
│              │                                                             │
│              │  [Results]  [Reconciliation]  [Timeline]  [Audit Log]       │
│              │  ───────────────────────────────────────────────────────   │
│              │                                                             │
│              │  ┌─ ACTION AREA (status-driven) ────────────────────────┐  │
│              │  │                                                      │  │
│              │  │  [CALCULATED STATE]                                  │  │
│              │  │  Review complete? Approve this run to hand off to    │  │
│              │  │  the finance team.                                   │  │
│              │  │                              [Approve Run →]         │  │
│              │  │                                                      │  │
│              │  └──────────────────────────────────────────────────────┘  │
│              │                                                             │
│              │  Search employees...    Filter: [All ▾]   [↓ Export ▾]     │
│              │                                                             │
│              │  ┌───────────────────────────────────────────────────────┐ │
│              │  │ #    Employee          Gross Pay   Deductions Net Pay  │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ 001  Ade Okafor       ₦ 185,000   ₦ 43,250  ₦141,750│ │
│              │  │      [▾ View breakdown]                               │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ 002  Bisi Adeyemi     ₦ 220,000   ₦ 51,800  ₦168,200│ │
│              │  │      [▾ View breakdown]                               │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ 003  Chuka Eze        ₦ 195,000   ₦ 45,900  ₦149,100│ │
│              │  │      [▾ View breakdown]                               │ │
│              │  └───────────────────────────────────────────────────────┘ │
│              │                                                             │
└──────────────┴─────────────────────────────────────────────────────────────┘
```

---

## Employee Row — Expanded Breakdown

```
│ 001  Ade Okafor       ₦ 185,000   ₦ 43,250  ₦141,750  [▲ Hide]  │
│                                                                   │
│      EARNINGS                        DEDUCTIONS                   │
│      Basic Salary      ₦ 150,000    PAYE              ₦ 28,000   │
│      Housing Allow.    ₦  25,000    Pension (8%)      ₦ 12,000   │
│      Transport Allow.  ₦  10,000    NHF (2.5%)        ₦  3,250   │
│                                                                   │
│      ── Component Trace ──────────────────────────────────────    │
│      BASIC    STANDARD   ✓   ₦ 150,000  Full month (no proration) │
│      HOUSING  STANDARD   ✓   ₦  25,000                           │
│      PAYE     CUMULATIVE ✓   ₦  28,000  Annual method, 24% band  │
│      PENSION  PERCENTAGE ✓   ₦  12,000  8% of pensionable pay    │
│      NHF      PERCENTAGE ✓   ₦   3,250  2.5% of basic            │
│                                                                   │
```

---

## Action Area — By Status

### CALCULATING
```
│  ┌──────────────────────────────────────────────────┐  │
│  │  ⟳  Payroll is calculating...                   │  │
│  │     Processing 142 employees. This may take      │  │
│  │     a few minutes.                               │  │
│  │                               [Refresh status]  │  │
│  └──────────────────────────────────────────────────┘  │
```

### PARTIAL (some employees failed)
```
│  ┌──────────────────────────────────────────────────┐  │
│  │  ⚠  3 employees failed to calculate             │  │
│  │     Fix the issues below and retry.              │  │
│  │     Approved employees are unaffected.           │  │
│  │                    [Retry Failed Employees →]    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Filter: [Failed only ▾]   (pre-filtered)               │
│                                                         │
│  ✕ 014  Emeka Nwosu     FAILED  —    —     —            │
│         [▾ View error trace]                            │
│  ✕ 027  Funmi Adamu     FAILED  —    —     —            │
│         [▾ View error trace]                            │
│  ✕ 098  Grace Obi       FAILED  —    —     —            │
│         [▾ View error trace]                            │
```

### FAILED Employee — Expanded Error Trace
```
│  ✕  014  Emeka Nwosu    FAILED                              │
│                                                             │
│  ── Error trace ───────────────────────────────────────    │
│  BASIC    STANDARD   ✓   ₦ 120,000                         │
│  PENSION  PERCENTAGE ✕   ERROR: pension rate not found     │
│           → Check statutory rule configuration             │
│                                                             │
```

### CALCULATED
```
│  ✓  All 142 employees calculated successfully             │
│     Review the results below, then approve.               │
│                              [Approve Run →]              │
```

### APPROVED
```
│  ✓  Approved by Emeka Obi on 14 Apr 2026 at 14:23        │
│     Awaiting lock from the finance team.                  │
│                              [Lock Run →]                 │
```
Retry button hidden. Run Again hidden.

### LOCKED
```
│  🔒  Locked on 14 Apr 2026. Ready for disbursement.      │
│                                                           │
│  Downloads:                                               │
│  [↓ Bank Upload CSV]  [↓ PAYE Remittance]  [↓ Pension]  │
│                                                           │
│  ⚠  2 employees had FAILED results and are excluded      │
│     from all exports.                                     │
│                                                           │
│                              [Mark as Paid →]            │
│                              [View Reconciliation →]      │
```

### PAID (terminal — read only)
```
│  ✓  PAID — 15 Apr 2026                                   │
│     This run is closed. No further changes possible.     │
│                                                           │
│  Downloads:                                               │
│  [↓ Bank Upload CSV]  [↓ PAYE Remittance]  [↓ Pension]  │
```
No action buttons. Read-only badge. All data visible.

---

## Mark as Paid — Confirmation Dialog

```
┌──────────────────────────────────────────────────────┐
│  ⚠ Mark this run as paid?                            │
│                                                      │
│  This action is permanent and cannot be undone.      │
│  Once marked as PAID:                                │
│  · No changes can be made to this run or its results │
│  · The run will be permanently closed                │
│                                                      │
│  March 2026 · Acme Corp · ₦ 18,432,000 net          │
│                                                      │
│            [Cancel]    [Mark as Paid] (red button)   │
└──────────────────────────────────────────────────────┘
```

---

## Key UX Decisions

**Status-driven action area:** The primary action changes completely based on status. One clear call to action per status — never ambiguous.

**Totals summary always visible:** Emeka needs to see the numbers immediately. The four summary cards (gross, deductions, net, headcount) are always at the top — they never scroll away.

**Component trace is secondary, not primary:** Show totals per employee in the table. Expand to reveal the trace. Don't show trace columns by default — it overwhelms Adaeze and Emeka who just want the totals.

**FAILED employees have no amounts shown:** Don't show blank cells or ₦0. Show "FAILED" in red and show only the error trace. Amounts are meaningless for failed calculations.

**Exports gated and explained:** Export buttons only appear on LOCKED/PAID. When gated, show: "Exports available after the run is locked."

**Failed employee exclusion warned explicitly:** Don't let Tunde download a CSV and discover the gaps himself. Warn proactively: "X employees excluded from exports."
