# S10 — Run Payroll (New Run Form)

**Actor:** Payroll Operator (Adaeze)
**Emotional state:** Task-focused, slightly anxious — this action triggers the real calculation

---

## Layout (default state — MONTHLY)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager    [Acme Corp ▾]                        [Adaeze ▾]  [?]    │
├──────────────┬─────────────────────────────────────────────────────────────┤
│              │                                                             │
│ Dashboard    │  ← Back to Runs      New Payroll Run                       │
│ ● Runs       │                                                             │
│   Inputs     │  ┌──────────────────────────────────────────────────────┐  │
│              │  │                                                      │  │
│ People       │  │  Pay period                                          │  │
│   Employees  │  │  ┌─────────────────────┐  ┌─────────────────────┐   │  │
│              │  │  │ From: 01 Mar 2026   │  │ To:   31 Mar 2026   │   │  │
│ Settings     │  │  └─────────────────────┘  └─────────────────────┘   │  │
│              │  │                                                      │  │
│              │  │  Period type                                         │  │
│              │  │  ○ Monthly   ○ Fortnightly   ○ Custom               │  │
│              │  │                                                      │  │
│              │  │  [if Custom selected — Working days field appears]   │  │
│              │  │  ┌────────────────────┐                              │  │
│              │  │  │ Working days  [__] │ *required for Custom        │  │
│              │  │  └────────────────────┘                              │  │
│              │  │                                                      │  │
│              │  │  Run type                                            │  │
│              │  │  ● Regular    ○ Adjustment                          │  │
│              │  │                                                      │  │
│              │  │  [if Adjustment selected — Rule Set picker appears]  │  │
│              │  │  Rule set (optional override)                        │  │
│              │  │  ┌────────────────────────────────────────────┐     │  │
│              │  │  │ Use current rule set (default)         [▾] │     │  │
│              │  │  └────────────────────────────────────────────┘     │  │
│              │  │                                                      │  │
│              │  │  ──────────────────────────────────────────────     │  │
│              │  │                                                      │  │
│              │  │  ℹ Unclaimed inputs for this period: 47 inputs      │  │
│              │  │    These will be included in this run automatically. │  │
│              │  │    [View Inputs →]                                   │  │
│              │  │                                                      │  │
│              │  └──────────────────────────────────────────────────┘  │
│              │                                                             │
│              │                    [Cancel]   [Run Payroll →]              │
│              │                                                             │
└──────────────┴─────────────────────────────────────────────────────────────┘
```

---

## States

### Submitting
```
│                    [Cancel]   [Running...    ⟳]   │
```
Button disabled. Note: run may take time — show progress context:
```
│  ℹ Payroll calculation is running.                │
│    This may take 30–90 seconds for large teams.   │
│    You'll be redirected when complete.            │
```

### Error — Readiness Check Failed (422)
```
│  ┌─ Setup required before running payroll ─────┐  │
│  │                                             │  │
│  │  ✕  Salary definitions are missing          │  │
│  │     → Go to Settings → Workspace Config     │  │
│  │                                             │  │
│  │  ✕  No active payroll rules found           │  │
│  │     → Go to Settings → Workspace Config     │  │
│  │                                             │  │
│  │  ✕  No statutory rule found for Nigeria     │  │
│  │     → Contact your platform administrator  │  │
│  │                                             │  │
│  └─────────────────────────────────────────────┘  │
```
Each error has a specific link to where the issue is resolved.

### Error — Duplicate Period (409)
```
│  ┌─ Run already exists ────────────────────────┐  │
│  │                                             │  │
│  │  ⚠  A run for March 2026 already exists.   │  │
│  │     Status: PARTIAL · 3 employees failed    │  │
│  │                                             │  │
│  │                         [View Existing Run →]│  │
│  └─────────────────────────────────────────────┘  │
```

### Warning — Inputs pending for a different period
```
│  ⚠  4 inputs have a reference date outside this  │
│     period (Feb 2026). They will be included and  │
│     calculated using Feb 2026 rates.              │
```

---

## Key UX Decisions

**Dates pre-filled to current month:** Adaeze runs monthly payroll. Don't make her enter the same dates every month. Pre-fill intelligently.

**Period type pre-selected from pay cycle:** The workspace pay_cycle.frequency drives the default. If it's "monthly", MONTHLY is pre-selected.

**Working days field conditionally visible:** Only show when CUSTOM is selected. Conditional fields reduce cognitive load.

**Inputs count displayed:** Showing "47 unclaimed inputs will be included" reassures Adaeze that the inputs she entered will be picked up. Reduces the anxiety of "did I remember to add them?"

**No technical jargon in errors:** "statutory_rule not found" → "No tax rules are configured for Nigeria. Contact your platform administrator."
