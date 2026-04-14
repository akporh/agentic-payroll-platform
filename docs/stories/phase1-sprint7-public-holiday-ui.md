# Sprint 7 — Public Holiday & OT Config: Frontend Design Specification

Companion file to `phase1-sprint7-public-holiday.md`. Documents all UI changes required by PH-1 through PH-12.

---

## Affected Files

| File | Change Type | Stories |
|------|-------------|---------|
| `frontend/src/pages/WorkspaceSetup.tsx` | Extend — add Payroll Behaviour section + Rate Code Registry section | PH-6, PH-7 |
| `frontend/src/pages/PublicHolidays.tsx` | New page | PH-1 |
| `frontend/src/pages/PayrollResults.tsx` | Extend — PH warning banner | PH-10 |
| `frontend/src/components/payroll/ExecutionTimeline.tsx` | Extend — warn state rendering | PH-10 |
| `frontend/src/api/payroll.ts` | New endpoints: public holidays, rate code registry, workspace config | PH-1, PH-6, PH-7 |
| `frontend/src/types/payroll.ts` | New types + ExecutionTraceStep status extension | All |

---

## Design System Reference

All new UI uses existing components only. No new primitives.

| Component | Usage |
|-----------|-------|
| `Btn` | All action buttons |
| `Card` | Section containers |
| `AlertBox` | Warning banners, validation messages |
| `PageHeader` | New PublicHolidays page header |
| `StatusBadge` | Source tags (NATIONAL / WORKSPACE), warn state |
| `Table` / `tbody` / `tr` | Registry and holiday list tables |

Tailwind scale: spacing `p-4`, `gap-3`, `mt-6`; typography `text-sm`, `font-medium`, `text-gray-500`.

---

## Screen 1 — WorkspaceSetup: Payroll Behaviour Section (PH-6)

**Route:** existing `/workspace/:id/setup`
**Placement:** new collapsible card below "Component Overrides", above "Review & Confirm"

### Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  Payroll Behaviour                                    [▼ expand] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Public Holiday Mode                                              │
│  ○ Automatic   ● File-based                                       │
│    Calendar-driven   Manual PH input                              │
│    expected_days     file only                                    │
│                                                                   │
│  ─────────────────────────────────────────────────────────────   │
│                                                                   │
│  Weekend Public Holiday Rules                                     │
│                                                                   │
│  Saturday PH falls on weekend   [ Observed on Monday  ▼ ]        │
│  Sunday PH falls on weekend     [ Observed on Monday  ▼ ]        │
│                                                                   │
│  Options: Observed on Monday | Ignore | Count as extra PH        │
│                                                                   │
│  ─────────────────────────────────────────────────────────────   │
│                                                                   │
│  Leave & Absence Rules                                            │
│                                                                   │
│  Leave on a public holiday      [●] Leave absorbs PH (default)   │
│                                 [ ] PH is separate (employee     │
│                                     gets both days back)         │
│                                                                   │
│  Absent on a public holiday     [●] Absence is deductible        │
│                                 [ ] Absence is not deductible    │
│                                     (employee gets PH pay)       │
│                                                                   │
│  ─────────────────────────────────────────────────────────────   │
│                                                                   │
│  ? What does "Leave absorbs PH" mean?                            │
│  ╰─ When an employee is on approved leave and a public holiday    │
│     falls within that leave period, the PH is counted as a       │
│     leave day — not deducted separately from their balance.       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### State Matrix

| State | Behaviour |
|-------|-----------|
| Loading | Section skeleton (3 rows, gray pulse) |
| No config row yet | Defaults shown (Automatic, Observed on Monday, Leave absorbs PH, Absent is deductible) |
| Dirty | "Save Payroll Behaviour" Btn enabled |
| Saved | Inline success flash ("Saved"), btn resets to disabled |
| Error | AlertBox under the section ("Could not save payroll behaviour. Try again.") |
| Workspace LIVE | All inputs read-only; section header shows lock icon |

### UX Notes

- Inline explanatory text for D3 and D4 toggles is mandatory — these are non-obvious defaults that operators will get wrong without context
- ph_mode radio changes should not auto-save — operator must click "Save Payroll Behaviour" explicitly
- Weekend PH rules are only shown when ph_mode = AUTOMATIC (hide for FILE_BASED)
- Workspace LIVE lock: read-only display only, no edit affordance

---

## Screen 2 — WorkspaceSetup: Rate Code Registry Section (PH-7)

**Route:** existing `/workspace/:id/setup`
**Placement:** new collapsible card below Payroll Behaviour

### Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  Rate Code Registry                                   [▼ expand] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Platform codes are seeded automatically. Add workspace-specific │
│  codes below.                                                     │
│                                                                   │
│  Code      Label                  Base          ×    Pensionable │
│  ──────────────────────────────────────────────────────────────  │
│  OT001     Standard OT            basic_hourly  1.5  ✓           │
│  OT002     Overtime (Weekend)     basic_hourly  2.0  ✓           │
│  OT003     Public Holiday OT      basic_hourly  3.25 ✓           │
│  OT004     Night Shift Premium    basic_hourly  0.25 ✓           │
│  OT005     Double Time            basic_hourly  2.0  ✓           │
│  OT006     Shift 2                basic_daily   0.10 ✓           │
│  OT007     Shift 3                basic_daily   0.15 ✓           │
│  ──────────────────────────────────────────────────────────────  │
│  SHIFT4    4-Shift Premium  [___] basic_daily ▼ [0.25] [✓] [ + ] │
│                                                                   │
│  [+ Add workspace code]                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Two-Tier Display

- **Platform rows** (workspace_id IS NULL): read-only, rendered with muted text (`text-gray-400`), no edit/delete controls
- **Workspace rows** (workspace_id = this workspace): editable inline, delete icon on hover

### State Matrix

| State | Behaviour |
|-------|-----------|
| Loading | Table skeleton (7 shimmer rows) |
| Empty workspace codes | Platform rows shown, "No workspace-specific codes yet" below divider |
| Adding | Inline form row appended at bottom of workspace section |
| Code collision | Inline error under code field: "Code OT001 is already in use" |
| Saved | Row appears in table, form clears |
| Workspace LIVE | Platform rows read-only (unchanged); workspace rows read-only with no add/edit/delete |

### UX Notes

- Platform codes are never editable or deletable — do not render controls
- `base` dropdown: "basic_hourly" | "basic_daily" — use friendly labels
- `is_pensionable` rendered as checkbox, default checked
- Multiplier field: numeric input, 2 decimal places, min 0.01

---

## Screen 3 — Public Holidays Page (PH-1)

**Route:** `/workspace/:id/public-holidays` (new route)
**Sidebar nav entry:** "Public Holidays" under workspace admin section

### Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  Public Holidays                                                  │
│  Workspace: Acme Corp · Nigeria (NGA)              [2026 ▼]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ← 2025          13 holidays in 2026          2027 →             │
│                                                                   │
│  Date           Name                          Source    Actions  │
│  ──────────────────────────────────────────────────────────────  │
│  01 Jan 2026    New Year's Day                NATIONAL           │
│  20 Jan 2026    Armed Forces Remembrance Day  NATIONAL           │
│  18 Apr 2026    Good Friday                   NATIONAL           │
│  20 Apr 2026    Easter Monday                 NATIONAL           │
│  01 May 2026    Workers' Day                  NATIONAL           │
│  12 Jun 2026    Democracy Day                 NATIONAL           │
│  28 Jul 2026    Eid al-Adha (est.)            NATIONAL           │
│  01 Oct 2026    Independence Day              NATIONAL           │
│  25 Dec 2026    Christmas Day                 NATIONAL           │
│  26 Dec 2026    Boxing Day                    NATIONAL           │
│  ──────────────────────────────────────────────────────────────  │
│  14 Apr 2026    Company Founding Day          WORKSPACE  [× del] │
│                                                                   │
│  ─────────────────────────────────────────────────────────────   │
│                                                                   │
│  Add workspace holiday                                            │
│  Date [      ] Name [                          ] [Add Holiday]   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Source Badges

- `NATIONAL` — blue badge (`bg-blue-100 text-blue-700`), read-only
- `WORKSPACE` — amber badge (`bg-amber-100 text-amber-700`), deletable

### State Matrix

| State | Behaviour |
|-------|-----------|
| Loading | Table skeleton |
| No national holidays seeded | AlertBox (warning): "National holidays for NGA have not been seeded. Contact platform support." |
| No workspace holidays | Section shows "No workspace-specific holidays added" below divider |
| Date collision (national) | Inline error: "01 Jan 2026 is already a national holiday" |
| Date collision (workspace) | Inline error: "14 Apr 2026 already added" |
| Add success | Row appears in workspace section, form clears |
| Delete | Confirm modal: "Remove Company Founding Day?" [Cancel] [Remove] |

### UX Notes

- Year navigator allows browsing past and future years
- National holidays are never editable — read-only rows, no delete control
- Only workspace-specific holidays are user-managed
- Past dates: workspace holidays with dates in the past still show, with no special styling (they're historical record)

---

## Screen 4 — PayrollResults: PH Warning Banner (PH-10)

**Route:** existing `/payroll/:runId/results`
**Placement:** below run header, above employee results table — only shown when warnings exist

### Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠  Public Holiday Warnings                        [▼ show all] │
│                                                                   │
│  • Expected 3 public holidays in November 2026, found 2 in       │
│    snapshot. One PH may be missing from this run.                │
│                                                                   │
│  • Employee E004 (Adebayo, Chidi): PH date 01 Nov 2026 falls     │
│    outside the pay period. Input may be miscoded.                │
│                                                                   │
│  These warnings do not block payroll. Review before approving.   │
└─────────────────────────────────────────────────────────────────┘
```

### Design

- Container: `bg-amber-50 border border-amber-200 rounded-lg p-4`
- Icon: amber triangle (`text-amber-500`)
- Title: `font-medium text-amber-800`
- Body: `text-sm text-amber-700`
- Collapsible: show first warning expanded, rest collapsed if > 2 warnings

### State Matrix

| State | Behaviour |
|-------|-----------|
| No warnings | Banner not rendered at all |
| 1–2 warnings | All shown expanded |
| 3+ warnings | First shown, rest behind "show all" toggle |
| Run APPROVED | Banner still shown (read-only, historical) |

---

## Screen 5 — Execution Timeline: Warn State (PH-10)

**Route:** existing payroll timeline / execution trace view

### Wireframe

```
  ○──────○──────⚠──────○──────○
  │      │      │       │      │
  init  rules  _ph    exec  summary
              context

  _ph_context step (warn):
  ┌────────────────────────────────────────────────────────┐
  │  ⚠ _period_context                         warn       │
  │                                                         │
  │  working_days: 20                                       │
  │  expected_days: 19   (PH: 01 Nov 2026)                 │
  │  expected_hours: 152                                    │
  │  ph_source: SNAPSHOT                                    │
  │                                                         │
  │  Warning: PH count in snapshot (2) differs from        │
  │  national calendar (3). Run may be missing one PH.     │
  └────────────────────────────────────────────────────────┘
```

### Warn State Rendering

- Timeline node: amber circle (`bg-amber-400`) instead of green
- Step detail panel: amber left border (`border-l-4 border-amber-400`)
- Status badge: `StatusBadge` with `variant="warn"` — amber background, "warn" label
- Warning message: rendered from `execution_trace.context.warning` field

### Type Change Required

`ExecutionTraceStep.status` in `frontend/src/types/payroll.ts`:

```typescript
// Before
status: 'success' | 'error'

// After
status: 'success' | 'error' | 'warn'
```

Downstream: timeline node colour, step panel border, StatusBadge variant — all derive from this field.

---

## State Coverage Summary

| Screen | Loading | Empty | Error | Success | Warn |
|--------|---------|-------|-------|---------|------|
| Payroll Behaviour | ✓ | ✓ (defaults) | ✓ | ✓ | — |
| Rate Code Registry | ✓ | ✓ | ✓ | ✓ | — |
| Public Holidays | ✓ | ✓ | ✓ | ✓ | — |
| PH Warning Banner | — | hidden | — | shown | shown |
| Execution Timeline | — | — | ✓ | ✓ | ✓ |

---

## API Surface (new endpoints needed)

| Method | Path | Purpose | Story |
|--------|------|---------|-------|
| GET | `/workspaces/:id/payroll-config` | Fetch WorkspacePayrollConfig | PH-6 |
| PUT | `/workspaces/:id/payroll-config` | Upsert WorkspacePayrollConfig | PH-6 |
| GET | `/workspaces/:id/rate-codes` | List rate_code_registry (platform + workspace) | PH-7 |
| POST | `/workspaces/:id/rate-codes` | Add workspace-specific rate code | PH-7 |
| DELETE | `/workspaces/:id/rate-codes/:code` | Remove workspace rate code | PH-7 |
| GET | `/workspaces/:id/public-holidays?year=2026` | List NationalPublicHoliday + WorkspacePublicHoliday | PH-1 |
| POST | `/workspaces/:id/public-holidays` | Add workspace holiday | PH-1 |
| DELETE | `/workspaces/:id/public-holidays/:id` | Remove workspace holiday | PH-1 |
