# S7 — Payroll Inputs (Variable Event Inbox)

**Actor:** Payroll Operator (Adaeze)
**Emotional state:** Methodical, checking items off a list before the run

---

## Layout (inputs present)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager    [Acme Corp ▾]                        [Adaeze ▾]  [?]    │
├──────────────┬─────────────────────────────────────────────────────────────┤
│              │                                                             │
│ Dashboard    │  Payroll Inputs                                             │
│   Runs       │  Variable events to be included in the next payroll run.   │
│ ● Inputs     │                                                             │
│              │  [+ Add Input]       [↑ Bulk Upload]      47 pending       │
│ People       │                                                             │
│   Employees  │  Search by employee...  Filter: [All categories ▾]         │
│              │                                                             │
│ Settings     │  ┌───────────────────────────────────────────────────────┐ │
│              │  │ Employee      Code        Category   Qty  Ref Period  │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Ade Okafor    OVERTIME     EARNING    8h   Mar 2026   │ │
│              │  │ #001                                       [🗑]        │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Bisi Adeyemi  LEAVE_NOPAY  DEDUCTION  2d   Mar 2026   │ │
│              │  │ #002                                       [🗑]        │ │
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Chuka Eze     BONUS        EARNING    —    Feb 2026 ⚑  │ │
│              │  │ #003          (no quantity)           [Cross-period]  [🗑]│
│              │  ├───────────────────────────────────────────────────────┤ │
│              │  │ Dele Sani     OVERTIME     EARNING    12h  Mar 2026   │ │
│              │  │ #011                                       [🗑]        │ │
│              │  └───────────────────────────────────────────────────────┘ │
│              │                                                             │
│              │  Showing 47 unclaimed inputs                               │
└──────────────┴─────────────────────────────────────────────────────────────┘
```

---

## Add Input Slide-Over

```
┌──────────────────────────────────────────────┐
│  Add Payroll Input                      [✕] │
├──────────────────────────────────────────────┤
│                                              │
│  Employee *                                  │
│  ┌──────────────────────────────────────┐    │
│  │ Search by name or number...      [▾] │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  Input type *                                │
│  ┌──────────────────────────────────────┐    │
│  │ Select...                        [▾] │    │
│  └──────────────────────────────────────┘    │
│  OVERTIME (EARNING)                          │
│  LEAVE_NOPAY (DEDUCTION)                     │
│  BONUS (EARNING)                             │
│  TRANSPORT_CLAIM (EARNING)                   │
│  [more codes from active rules...]           │
│                                              │
│  Quantity (hours/days/units)                 │
│  ┌──────────────────────────────────────┐    │
│  │ 0                                    │    │
│  └──────────────────────────────────────┘    │
│  Must be 0 or greater                        │
│                                              │
│  Applies to period                           │
│  ┌──────────────────────────────────────┐    │
│  │ Mar 2026                         [▾] │    │
│  └──────────────────────────────────────┘    │
│  Leave blank to use the current period.      │
│  Set a past period for late-arriving events. │
│                                              │
│               [Cancel]  [Add Input]          │
└──────────────────────────────────────────────┘
```

---

## Empty State

```
│                                                     │
│         [Icon: inbox / tray]                        │
│                                                     │
│   No pending inputs                                 │
│   Add overtime, leave, bonuses, or other            │
│   variable events before running payroll.           │
│   Inputs without a reference period will be         │
│   included in the next run.                         │
│                                                     │
│   [+ Add Input]    [↑ Bulk Upload]                 │
│                                                     │
```

---

## Cross-Period Input Indicator

Inputs with a reference_date outside the current period are visually flagged:
```
│ Chuka Eze  BONUS  EARNING  —  Feb 2026 ⚑ [Cross-period] │
```
Tooltip on ⚑: "This input applies to February 2026. It will be calculated using February's payroll rules."

---

## Delete Confirmation

Clicking 🗑 shows an inline confirm rather than a dialog:
```
│ Ade Okafor  OVERTIME  EARNING  8h  Mar 2026   [Cancel] [Delete] │
```
No modal needed for a low-stakes single-row delete.

---

## Key UX Decisions

**"Inbox" framing:** Calling this the "input inbox" mentally positions it as something to be processed before running payroll — a checklist, not a database.

**Input code dropdown shows human names:** "OVERTIME (EARNING)" not just "OVERTIME". Category helps Adaeze understand what type of event she's adding.

**Reference period defaults to current month:** If Adaeze doesn't change it, the input applies to the current run. She only needs to touch it for late-arriving historical events.

**Cross-period inputs flagged:** Adaeze needs to know which inputs will use historical rates. A visual flag with a tooltip is less intrusive than inline explanatory text.

**Bulk upload button in the header:** Adaeze will use bulk upload frequently. Don't hide it in a submenu.

**Count shown prominently:** "47 pending" tells Adaeze she has inputs waiting. Reassures her that the inputs she uploaded earlier are there.
