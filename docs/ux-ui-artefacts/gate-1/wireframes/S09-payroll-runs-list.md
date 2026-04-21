# S9 — Payroll Runs List

**Actor:** Payroll Operator (Adaeze), Finance Authoriser (Emeka)
**Emotional state:** Adaeze — task-oriented, scanning for her current run. Emeka — reviewing, looking for CALCULATED runs.

---

## Layout (LIVE workspace, runs exist)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager    [Acme Corp ▾]                        [Adaeze ▾]  [?]    │
├──────────────┬─────────────────────────────────────────────────────────────┤
│              │                                                             │
│ Dashboard    │  Payroll Runs                         [+ New Run]           │
│              │                                                             │
│ ● Runs       │  ┌─ PARTIAL ALERT (conditional) ──────────────────────────┐ │
│   Inputs     │  │ ⚠  March 2026 run has 3 failed employees.              │ │
│              │  │    Review and retry before approving.    [View Run →]   │ │
│ People       │  └────────────────────────────────────────────────────────┘ │
│   Employees  │                                                             │
│              │  Filter: [All statuses ▾]    Search period...              │
│ Settings     │                                                             │
│   Config     │  ┌───────────────────────────────────────────────────────┐ │
│   Payroll    │  │ Period          Status       Net Pay      Pay Date     │ │
│   Config     │  ├───────────────────────────────────────────────────────┤ │
│   Holidays   │  │ ⚠ Mar 2026     [PARTIAL]    —            28 Mar 2026  │ │
│   Rate Codes │  │ 1 Mar – 31 Mar  3 failed    [View →]                  │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Feb 2026        [PAID]    ₦ 18,430,000   28 Feb 2026  │ │
│              │  │ 1 Feb – 28 Feb             [View →]                   │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Jan 2026        [PAID]    ₦ 18,210,500   28 Jan 2026  │ │
│              │  │ 1 Jan – 31 Jan             [View →]                   │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Dec 2025        [PAID]    ₦ 17,980,000   28 Dec 2025  │ │
│              │  └───────────────────────────────────────────────────────┘ │
│              │                                                             │
│              │  Showing 4 runs                                            │
└──────────────┴─────────────────────────────────────────────────────────────┘
```

---

## Status Badge Designs

| Status | Badge colour | Icon |
|---|---|---|
| CALCULATING | Blue (pulsing) | ⟳ spinner |
| PARTIAL | Amber | ⚠ |
| CALCULATED | Teal | ✓ |
| APPROVED | Purple | ✓✓ |
| LOCKED | Indigo | 🔒 |
| PAID | Green | ✓ paid |

---

## States

### Empty — Workspace LIVE, No Runs Yet
```
│                                                             │
│         [Icon: payroll/calculator]                         │
│                                                             │
│    No payroll runs yet                                      │
│    Run your first payroll to get started.                   │
│    Make sure all variable inputs are entered first.         │
│                                                             │
│         [+ New Run]                                         │
│                                                             │
```

### Empty — Workspace NOT LIVE
```
│         [Icon: lock/setup]                                  │
│                                                             │
│    Workspace is not live                                    │
│    Complete workspace setup before running payroll.         │
│                                                             │
│    Setup progress: ████████░░ 80%                           │
│    Missing: Payroll rules                                   │
│                                                             │
│         [Continue Setup →]                                  │
│                                                             │
```
"+ New Run" button is disabled (greyed, tooltip: "Workspace must be LIVE to run payroll").

### CALCULATING Run (auto-refresh every 5s)
```
│  ⟳ Mar 2026     [CALCULATING]   —            28 Mar 2026  │
│  1 Mar – 31 Mar  Processing...               [View →]      │
```

---

## Key UX Decisions

**Alert banner for PARTIAL at top:** Adaeze needs to know immediately if a run needs attention. Don't make her scan the list to find it.

**Net Pay shown only on PAID/LOCKED:** Showing amounts on in-progress runs could be misleading if some employees failed. Only show totals once complete.

**"+ New Run" always visible (but gated):** The button is always shown but disabled with an explanation if workspace is not LIVE. Don't hide the button — hiding it creates confusion about where the feature went.

**Period displayed as human-readable:** "Mar 2026" not "2026-03-01 – 2026-03-31". Payroll operators think in months, not ISO dates.
