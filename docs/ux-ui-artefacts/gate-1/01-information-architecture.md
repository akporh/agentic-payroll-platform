# Gate 1 — Information Architecture

---

## Core Insight

This platform has two distinct mental models operating simultaneously:
1. **Bureau-level** — Chidi monitoring and managing all client workspaces.
2. **Workspace-level** — Adaeze, Emeka, Ngozi doing their jobs inside one client's context.

The IA must make the transition between these two levels feel natural, not like switching applications. The workspace sidebar must give Adaeze everything she needs without ever leaving workspace context.

---

## Navigation Architecture

```
ROOT: Bureau Dashboard
│
├── [Workspace Card] ──► Workspace Context
│   │
│   ├── Dashboard (workspace home)
│   │
│   ├── PAYROLL (primary section)
│   │   ├── Runs
│   │   │   ├── Run List
│   │   │   ├── New Run (form)
│   │   │   └── Run Detail ──► [tabs]
│   │   │       ├── Results
│   │   │       ├── Reconciliation
│   │   │       ├── Timeline
│   │   │       └── Audit Log
│   │   └── Inputs
│   │       ├── Input Inbox
│   │       └── Bulk Upload
│   │
│   ├── PEOPLE (secondary section)
│   │   └── Employees
│   │       ├── Employee List
│   │       └── Bulk Contract Update
│   │
│   └── SETTINGS (tertiary section)
│       ├── Workspace Config (overview: grades, designations, salary defs, rules, overrides)
│       ├── Payroll Config (PH rules, attendance behaviour)
│       ├── Public Holidays
│       ├── Rate Codes
│       └── Setup Wizard (only visible if workspace is not LIVE)
│
└── [+ New Workspace] ──► Create Workspace (modal)
```

---

## Navigation Hierarchy Decisions

### Decision 1: Two-Tier Navigation
**Pattern:** Bureau switcher at the top + workspace left sidebar.

The top bar holds: Bureau name / logo | Workspace picker (dropdown if multiple assigned) | User identity.

The left sidebar holds all workspace-scoped navigation. This keeps the workspace context unambiguous — the user always knows which client they're in.

**Inspired by:** Linear's team/project pattern. Vercel's team switcher + project sidebar.

**Why not tabs at the top:** Payroll Runs are the most-used section. Tabs push primary actions too far from the content — sidebar scales better as the nav grows.

---

### Decision 2: Run Detail Uses Tabs, Not Separate Pages
A payroll run has four views: Results, Reconciliation, Timeline, Audit Log. These are all facets of the same object. Tabs keep the run context in view (status badge, period, totals) while the user switches between views.

**Tabs order:** Results (primary) | Reconciliation | Timeline | Audit Log
The order matches the frequency of use: Results is accessed by everyone, Audit Log by Emeka only.

---

### Decision 3: Setup Wizard Is Hidden Once LIVE
The onboarding wizard (S3/S4) is only surfaced in the Settings section when a workspace is not LIVE. Once LIVE, the entry point disappears. The workspace status indicator in the header (or sidebar) links back to it if the workspace regresses.

---

### Decision 4: Inputs Are Under Payroll, Not People
Payroll Inputs are variable events that feed the payroll engine. They belong to the Payroll section — Adaeze thinks of them as "things I need to enter before I run payroll", not as employee data.

---

## Content Hierarchy Within Key Screens

### Payroll Run Detail (most complex screen)
Priority order when user arrives:
1. **Status badge + period** — Where is this run? (3-second scan)
2. **Totals summary** — How much? (gross, deductions, net, employee count)
3. **Action button** — What do I do next? (single primary action based on status)
4. **Results table** — Employee detail (scrollable, secondary)
5. **Tab navigation** — Other views (Reconciliation, Timeline, Audit)

### Bureau Dashboard
Priority order:
1. **Alert banner** — Any workspaces needing immediate attention? (PARTIAL, MISMATCH)
2. **Workspace grid/list** — All clients with status and key metrics
3. **New Workspace** — Chidi's secondary task

---

## URL Structure (Proposed)

```
/                           → Bureau Dashboard
/workspaces/new             → Create Workspace (or modal on /)

/w/{workspace_id}/          → Workspace Dashboard
/w/{workspace_id}/runs      → Payroll Runs List
/w/{workspace_id}/runs/new  → New Run Form
/w/{workspace_id}/runs/{run_id}/results        → Results tab
/w/{workspace_id}/runs/{run_id}/reconciliation → Reconciliation tab
/w/{workspace_id}/runs/{run_id}/timeline       → Timeline tab
/w/{workspace_id}/runs/{run_id}/audit          → Audit Log tab
/w/{workspace_id}/inputs    → Input Inbox
/w/{workspace_id}/inputs/bulk → Bulk Upload
/w/{workspace_id}/employees → Employee List
/w/{workspace_id}/settings/config      → Workspace Config
/w/{workspace_id}/settings/payroll-config → Payroll Config (PH rules)
/w/{workspace_id}/settings/holidays    → Public Holidays
/w/{workspace_id}/settings/rate-codes  → Rate Codes
/w/{workspace_id}/setup     → Setup Wizard (visible only if not LIVE)
```

---

## Breadcrumb Strategy

All workspace-level pages show:
`[Bureau Name] / [Workspace Name] / [Section] / [Detail]`

Example on a run results page:
`PayManager / Acme Corp / Payroll Runs / March 2026 / Results`

Clicking workspace name returns to Workspace Dashboard.
Clicking section name returns to section list.

---

## Empty State Hierarchy

Every section has a defined empty state with an action:

| Screen | Empty State Message | Action |
|---|---|---|
| Bureau Dashboard | "No workspaces yet. Add your first client." | + New Workspace |
| Payroll Runs | "No runs yet. [Workspace not LIVE: complete setup first. LIVE: run your first payroll.]" | → Setup or → New Run |
| Input Inbox | "No pending inputs. Add overtime, leave, or other variable pay before running payroll." | + Add Input |
| Employee List | "No employees. Complete workspace onboarding first." | → Setup Wizard |
| Public Holidays | "No custom holidays for [year]. National holidays are shown below." | + Add Holiday |

---

## Information Architecture Validation

- [ ] Primary user (Adaeze) can reach Inputs → Runs → Results in 2 clicks from Workspace Dashboard
- [ ] Finance Authoriser (Emeka) can find CALCULATED runs and act within 3 clicks from Bureau Dashboard
- [ ] All error recovery paths have a named destination (e.g. "Salary definitions are missing → Go to Settings → Workspace Config")
- [ ] No section is deeper than 3 levels (Bureau → Workspace → Screen is the max before tabs)
- [ ] Settings is clearly separated from operational sections — config changes don't interrupt payroll workflows
