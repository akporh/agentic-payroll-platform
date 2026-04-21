# S1 — Bureau Dashboard

**Actor:** Bureau Administrator (Chidi)
**Emotional state:** Monitoring, scanning for problems — wants to triage quickly

---

## Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [≡] PayManager Bureau                                    [Chidi Obi ▾] [?] │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Bureau Overview                              [+ New Workspace]            │
│                                                                            │
│  ┌─ ALERT BANNER (conditional) ──────────────────────────────────────────┐ │
│  │ ⚠  3 workspaces need attention                                        │ │
│  │    2 with unresolved MISMATCH · 1 PARTIAL run stuck > 30 min         │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Search workspaces...          [Filter: All ▾]  [Sort: Name ▾]            │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  ACME CORPORATION              ● LIVE                                │ │
│  │  Nigeria · NGN · 142 active employees                                │ │
│  │  Last run: Mar 2026 · ✓ PAID · Reconciled                           │ │
│  │                                             [Open Workspace →]       │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │  ⚠ BRIDGE LOGISTICS            ● LIVE                                │ │
│  │  Nigeria · NGN · 67 active employees                                 │ │
│  │  Last run: Mar 2026 · ⚠ MISMATCH — Reconciliation unresolved        │ │
│  │                                             [Open Workspace →]       │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │  ⚠ COASTAL FOODS               ● LIVE                                │ │
│  │  Nigeria · NGN · 28 active employees                                 │ │
│  │  Last run: Mar 2026 · ⚠ PARTIAL — 3 employees failed                │ │
│  │                                             [Open Workspace →]       │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │  DELTA SERVICES                ○ READY                               │ │
│  │  Nigeria · NGN · 0 active employees                                  │ │
│  │  Setup complete — not yet live                                       │ │
│  │                                             [Open Workspace →]       │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │  EAGLE TRANSPORT               ◌ DRAFT                               │ │
│  │  Nigeria · NGN · —                                                   │ │
│  │  Onboarding in progress                                              │ │
│  │                                             [Open Workspace →]       │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Showing 5 of 18 workspaces                        [Load more]            │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## States

### Empty State (no workspaces)
```
┌──────────────────────────────────────┐
│                                      │
│      [Icon: building/office]         │
│                                      │
│   No client workspaces yet           │
│   Add your first client to get       │
│   started with payroll management.   │
│                                      │
│        [+ Add First Workspace]       │
│                                      │
└──────────────────────────────────────┘
```

### Workspace Card States
- **LIVE, no alerts:** neutral card, grey border
- **LIVE, alert (MISMATCH / PARTIAL):** amber left border + ⚠ icon + alert text
- **READY:** blue border, "Go Live" sub-action visible
- **DRAFT / incomplete:** grey border, muted text, "Continue Setup" sub-action
- **CALCULATING (stuck):** amber pulsing dot, "Calculating..." text with elapsed time

---

## Workspace Status Badges

| Status | Visual |
|---|---|
| LIVE | ● Green filled dot |
| READY | ● Blue filled dot |
| RULES_DEFINED | ◑ Half-filled dot |
| COMPENSATION_DEFINED | ◑ |
| STRUCTURE_DEFINED | ◑ |
| DRAFT | ◌ Empty dot |

---

## Key UX Decisions

**Cards, not a table:** Each workspace is a card with enough context to act without clicking in. Chidi should know the status of every client at a glance.

**Alerts at top, not inline only:** A summary alert banner tells Chidi how many workspaces need action before he has to scroll. The alert banner is dismissible per session.

**Status as the dominant signal:** Status badge and last run state are the two things Chidi needs most. Employee count is secondary context.

**No pagination — load more:** Chidi manages 15–25 clients. A flat list with "load more" is simpler than a paginated table for this scale.
