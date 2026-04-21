# Remaining Screen Wireframes (S4–S6, S13–S18)

---

# S4 — JSON Onboarding

**Actor:** Bureau Administrator (technical / power user)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  JSON Onboarding                  [Preview]      [Commit]                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─ Editor ───────────────────────────────────────────────────────────┐   │
│  │ {                                                                  │   │
│  │   "workspace_id": "...",                                           │   │
│  │   "employees": [...],                                              │   │
│  │   "salary_definitions": [...],                                     │   │
│  │   "payroll_rules": [...],                                          │   │
│  │   "grades": [...],                                                 │   │
│  │   "designations": [...]                                            │   │
│  │ }                                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─ Response panel (after Preview/Commit) ───────────────────────────┐   │
│  │  Status: valid                                                    │   │
│  │  Warnings: [...]                                                  │   │
│  │  Errors: []                                                       │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

**States:** Editor idle | Preview (response visible) | Error (errors in response) | Committed (success banner)

**Note:** This is a power-user tool. Keep it minimal. No explanatory UI needed — users of this path understand JSON.

---

# S5 — Workspace Configuration

**Actor:** Bureau Administrator, Payroll Operator

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Settings → Workspace Config                                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [Overview] [Pay Cycle] [Grades] [Designations] [Salary Defs] [Rules]     │
│  [Component Overrides] ← tab nav                                           │
│                                                                            │
│  ── Overview ──────────────────────────────────────────────────────────    │
│  Workspace:    Acme Corporation          Status: ● LIVE                   │
│  Country:      Nigeria (NG)              Currency: NGN                    │
│  Pay Cycle:    Monthly · Run day 25 · Pay day 28 · Cutoff day 20          │
│                                                                            │
│  ── Component Overrides ───────────────────────────────────────────────    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Component           Active  Override              Proration          │  │
│  │ PAYE                [✓]     Platform rule         —                  │  │
│  │ PENSION_EMPLOYEE    [✓]     Platform rule         FULL_MONTH [▾]    │  │
│  │ NHF                 [✓]     Platform rule         —                  │  │
│  │ HEALTH_INSURANCE    [✓]     ₦ 2,500 /month [edit] —                 │  │
│  │ DEVELOPMENT_LEVY    [✓]     ₦ 100 /year [edit]    —                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    [Save Changes]                          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

# S6 — Employee List

**Actor:** HR Admin (Ngozi), Payroll Operator (Adaeze)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  People → Employees                                                        │
│                                                                            │
│  Search employees...       [Filter: Active ▾]    [↑ Bulk Update Contracts] │
│                                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Name              #      Status    Grade    Designation   From       │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  Ade Okafor       001    ● ACTIVE  STEP_2    OFFICER       1 Jan 2024 │ │
│  │                                                          [Edit →]    │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  Bisi Adeyemi     002    ● ACTIVE  STEP_3    SUPERVISOR    1 Mar 2023 │ │
│  │                                                          [Edit →]    │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  Chuka Eze        003    ○ INACTIVE STEP_1   DRIVER        1 Jun 2022 │ │
│  │                          (left 31 Dec 2025)               [Edit →]   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  142 active · 8 inactive                                                  │
└────────────────────────────────────────────────────────────────────────────┘
```

**Edit Contract inline/modal:** Grade dropdown | Designation dropdown | Save
**Bulk Update modal:** Upload CSV (employee_number, contract_start, contract_end?) | Result: X updated, not_found list

---

# S13 — Public Holidays Calendar

**Actor:** Bureau Administrator, Payroll Operator

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Settings → Public Holidays                                                │
│                                                                            │
│  Year: [2026 ▾]                                [+ Add Holiday]            │
│                                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Date            Name                           Tier      Action      │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  1 Jan 2026      New Year's Day                 National   —          │ │
│  │  1 Jan 2026      New Year Holiday               National   —          │ │
│  │  18 Apr 2026     Good Friday                    National   —          │ │
│  │  20 Apr 2026     Easter Monday                  National   —          │ │
│  │  1 May 2026      Workers' Day                   National   —          │ │
│  │  12 Jun 2026     Democracy Day                  National   —          │ │
│  │  25 Dec 2026     Christmas Day                  National   —          │ │
│  │  26 Dec 2026     Boxing Day                     National   —          │ │
│  │  ─────────────────────────────────────────────────────────────────  │ │
│  │  15 Jan 2026     Company Foundation Day         Workspace  [🗑]       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ℹ National holidays are managed by your platform administrator.           │
│    Only workspace-specific holidays can be added or removed here.          │
└────────────────────────────────────────────────────────────────────────────┘
```

**Add Holiday inline form:**
```
│  Date: [date picker]    Name: [___________]    [Save]  [Cancel]    │
```

---

# S14 — Workspace Payroll Config (PH Rules)

**Actor:** Bureau Administrator, Payroll Operator

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Settings → Payroll Config                                                 │
│                                                                            │
│  Public holiday and attendance behaviour rules.                            │
│  Changes take effect from the date you specify.                            │
│                                                                            │
│  Effective from: [01 Apr 2026]                                             │
│                                                                            │
│  ── Public Holiday Mode ───────────────────────────────────────────────    │
│  ○ Automatic    Engine detects PH dates and applies PH pay automatically   │
│  ● File-based   PH events must be submitted as payroll inputs              │
│                                                                            │
│  PH rate code: [OT005 — 1.5× basic daily  ▾]                              │
│  (Determines the multiplier used for public holiday pay)                   │
│                                                                            │
│  ── Conflict Rules ────────────────────────────────────────────────────    │
│                                                                            │
│  When a public holiday falls on a Saturday:                                │
│  ● PH takes precedence    Employee is paid at PH rate for the Saturday     │
│  ○ Day of week rule       Saturday is treated as a normal Saturday         │
│                                                                            │
│  When a public holiday falls on a Sunday:                                  │
│  ● PH takes precedence                                                     │
│  ○ Day of week rule                                                        │
│                                                                            │
│  When a leave day overlaps with a public holiday (D3):                     │
│  ● Leave absorbs PH       The PH is absorbed into the leave period        │
│  ○ PH is additive         Employee receives PH pay on top of leave        │
│                                                                            │
│  When an employee is absent on a public holiday (D4):                      │
│  ● Absence is deductible  Absent employees have the PH day deducted       │
│  ○ PH excuses absence     PH day is not deducted even if absent           │
│                                                                            │
│                                               [Save Payroll Config]        │
└────────────────────────────────────────────────────────────────────────────┘
```

**Note:** Each conflict rule option includes a plain-English explanation. These choices have significant payroll accuracy implications and must not be presented as raw enum values.

---

# S15 — Rate Code Registry

**Actor:** Bureau Administrator

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Settings → Rate Codes                                                     │
│                                    [+ Add Rate Code]                       │
│                                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Code    Description              Multiplier  Unit  Base    Scope     │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │  OT001   Standard Overtime        1.5×        hour  basic   Platform  │ │
│  │  OT002   Double Time              2.0×        hour  basic   Platform  │ │
│  │  OT005   Public Holiday Rate      1.5×        day   basic   Platform  │ │
│  │  CUSTOM1 Weekend Allowance        1.25×       day   basic   Workspace [🗑]│ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ℹ Platform rate codes cannot be deleted. Add workspace-specific codes to  │
│    create custom multipliers for this client.                              │
└────────────────────────────────────────────────────────────────────────────┘
```

**Platform codes:** No delete control. Greyed or "Platform" badge.
**Add form:** Code | Multiplier (number) | Unit (hour/day) | Base (basic_hourly/basic_daily) | Description | [Save]

---

# S16 — Run Timeline (Execution Trace)

**Actor:** Bureau Administrator, Payroll Operator (debugging)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  March 2026 Payroll  [Results] [Reconciliation] [Timeline●] [Audit Log]   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Execution Timeline                                                        │
│  Step-by-step log of this payroll run's calculation.                      │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  09:00:01.001  Run started · workspace=Acme Corp · 142 employees    │  │
│  │  09:00:01.045  Rule set resolved · effective_from=2026-01-01        │  │
│  │  09:00:01.067  Statutory rule resolved · Nigeria · v3               │  │
│  │  09:00:01.100  Component metadata loaded · 12 components            │  │
│  │  09:00:01.200  Inputs linked · 47 inputs claimed                    │  │
│  │  09:00:02.100  Employee 001 · ✓ SUCCESS                             │  │
│  │  09:00:02.200  Employee 002 · ✓ SUCCESS                             │  │
│  │  09:00:02.250  Employee 014 · ✕ FAILED · pension rate not found     │  │
│  │  ...                                                                │  │
│  │  09:00:35.000  Run complete · 139 success · 3 failed               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ℹ This is a diagnostic view for troubleshooting failed runs.              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

# S17 — Run Audit Log

**Actor:** Finance Authoriser (Emeka), Bureau Administrator (Chidi)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  March 2026 Payroll  [Results] [Reconciliation] [Timeline] [Audit Log●]   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Audit Log — March 2026 Payroll                                            │
│  Immutable record of all actions taken on this run.                       │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  When                Action      By               Details            │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  14 Apr · 09:00     CREATED     adaeze@bureau    Period: Mar 2026   │  │
│  │  14 Apr · 09:01     CALCULATED  system           139 success, 3 fail│  │
│  │  14 Apr · 09:45     RETRIED     adaeze@bureau    3 failed employees  │  │
│  │  14 Apr · 10:02     CALCULATED  system           142 success         │  │
│  │  14 Apr · 14:23     APPROVED    emeka@bureau     —                  │  │
│  │  14 Apr · 16:11     LOCKED      emeka@bureau     —                  │  │
│  │  15 Apr · 09:47     RECONCILED  emeka@bureau     MATCHED ₦18,432,000│  │
│  │  15 Apr · 10:30     PAID        emeka@bureau     —                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ℹ This log is immutable. No entries can be modified or deleted.           │
└────────────────────────────────────────────────────────────────────────────┘
```

---

# S18 — Workspace Dashboard

**Actor:** Payroll Operator (Adaeze), Bureau Administrator (Chidi)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Acme Corporation                              ● LIVE · Nigeria · NGN      │
│                                                                            │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐               │
│  │ 142            │ │ 47             │ │ CALCULATED       │               │
│  │ Active         │ │ Pending inputs │ │ Last run status  │               │
│  │ employees      │ │ this period    │ │ March 2026       │               │
│  └────────────────┘ └────────────────┘ └─────────────────┘               │
│                                                                            │
│  ── What needs attention ──────────────────────────────────────────────    │
│  ● March 2026 run is CALCULATED — awaiting approval    [Approve →]         │
│  ● 47 inputs pending — confirm before running payroll  [View Inputs →]    │
│                                                                            │
│  ── Recent runs ───────────────────────────────────────────────────────    │
│  Mar 2026   CALCULATED   —              [View →]                          │
│  Feb 2026   PAID         ₦ 18,430,000  [View →]                          │
│  Jan 2026   PAID         ₦ 18,210,500  [View →]                          │
│                                                                            │
│  [→ All Runs]     [→ Add Inputs]     [→ Employees]     [→ Settings]       │
└────────────────────────────────────────────────────────────────────────────┘
```
