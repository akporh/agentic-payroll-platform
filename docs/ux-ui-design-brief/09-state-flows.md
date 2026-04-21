# Artefact 9 — State and Status Flows

> Source: DB models, migrations (`enforce_payroll_run_state_machine`), route logic, and
> frontend type definitions. All transitions listed here are enforced at both application
> and DB trigger level unless noted otherwise.

---

## 1. Payroll Run Lifecycle

### States

| Status | Meaning |
|---|---|
| DRAFT | Run record created but calculation not yet triggered (not used in current API — run creation immediately triggers calculation) |
| CALCULATING | Engine is actively computing employee payrolls |
| CALCULATED | All employees processed successfully; awaiting review |
| PARTIAL | Some employees failed; others succeeded. Retry is available |
| APPROVED | Finance authoriser has signed off; awaiting lock |
| LOCKED | Run is immutable; ready for disbursement and reconciliation |
| PAID | Terminal state; DB trigger prevents all further changes |

### Valid Transitions

```
[New Run Submitted]
        │
        ▼
  CALCULATING
     │      │
     │      ▼
     │   PARTIAL ──────► [Fix data] ──► CALCULATING (retry)
     │      │
     │      │ (all employees succeed)
     │      │
     ▼      ▼
  CALCULATED
        │
        │ [Operator approves]
        ▼
    APPROVED
        │
        │ [Authoriser locks]
        ▼
    LOCKED
        │
        │ [Authoriser marks paid]
        ▼
      PAID (terminal)
```

### Blocked Transitions (enforced by DB trigger)
- PAID → any other status: blocked by `trg_prevent_paid_run_update`
- APPROVED → CALCULATED: blocked (cannot un-approve)
- LOCKED → APPROVED: blocked
- Any state → DRAFT: not supported after creation

### UI Rules Derived from States
- CALCULATING: show spinner/pending indicator; disable all actions.
- PARTIAL: show "X employees failed" alert; show Retry button; list failed employees.
- CALCULATED: show Approve button; show results summary.
- APPROVED: show Lock button; disable Retry; disable "Run Again".
- LOCKED: enable export downloads; show Reconciliation link; show Mark as Paid button.
- PAID: full read-only; exports still available; no action buttons.

---

## 2. Payroll Result (Per-Employee) Lifecycle

### States

| Status | Meaning |
|---|---|
| SUCCESS | net_pay and component_trace_jsonb are populated; employee included in totals |
| FAILED | Calculation error; net_pay is null; excluded from exports |
| PARTIAL | Intermediate state within a run (not a terminal per-employee state in current code) |

### Transitions
- Created as SUCCESS or FAILED when the run executes.
- FAILED → SUCCESS: when the parent run is retried and the employee succeeds.
- SUCCESS → immutable: once the parent run reaches PAID (DB trigger blocks updates).

### UI Rules
- SUCCESS: show green indicator; display full pay breakdown.
- FAILED: show red indicator; show component trace for diagnosis; do not show pay amounts.
- FAILED employees are excluded from CSV exports — the UI should note this.

---

## 3. Reconciliation Lifecycle

### States

| Status | Meaning |
|---|---|
| PENDING | Legacy placeholder — not created by current code paths |
| MATCHED | actual_total == expected_total; reconciliation complete |
| MISMATCH | actual_total != expected_total; operator must investigate |
| RESOLVED | A MISMATCH that has been manually closed by an operator |

### Transitions

```
[Run reaches LOCKED]
        │
        │ [Submit actual_payment]
        ▼
  MATCHED ──────────────────────────────────────┐
                                                │
  MISMATCH ──► [Operator enters notes + name] ─► RESOLVED
```

### Constraints
- Only one reconciliation record per run (unique constraint on payroll_run_id).
- Only LOCKED runs can have a reconciliation submitted (400 otherwise).
- Only MISMATCH records can be resolved (MATCHED cannot be resolved).
- RESOLVED is terminal — no further state change is possible.

### UI Rules
- No reconciliation yet: show submission form (only if run is LOCKED).
- MATCHED: show confirmation summary; hide form.
- MISMATCH: show variance (actual − expected) prominently in red; show resolution form.
- RESOLVED: show read-only summary including notes, resolved_by, resolved_at; hide form.

---

## 4. Workspace Lifecycle (Onboarding State Machine)

### States

| Status | Meaning |
|---|---|
| DRAFT | Workspace created; no structure defined yet |
| STRUCTURE_DEFINED | Grades, designations, and pay cycle are present |
| COMPENSATION_DEFINED | Salary definitions are present |
| RULES_DEFINED | Payroll rules are present |
| READY | All readiness checks pass; workspace can accept a run |
| LIVE | Operator has explicitly confirmed the workspace is production-ready |

### Transitions

```
DRAFT
  │ [Onboarding commit: grades + designations + pay_cycle present]
  ▼
STRUCTURE_DEFINED
  │ [Salary definitions present]
  ▼
COMPENSATION_DEFINED
  │ [Payroll rules present]
  ▼
RULES_DEFINED
  │ [Readiness checks pass]
  ▼
READY
  │ [Manual "Go Live" action]
  ▼
LIVE
```

**Note:** The auto-advance through DRAFT → READY happens atomically during the onboarding commit. Manual LIVE transition requires a separate action (via the `/{workspace_id}/transition` endpoint).

### UI Rules
- DRAFT, STRUCTURE_DEFINED, COMPENSATION_DEFINED, RULES_DEFINED: show onboarding progress indicator; show what's missing.
- READY: show "Go Live" action.
- LIVE: full access to all features; "New Run" is enabled.
- Not LIVE: "New Run" button is disabled with explanation.

---

## 5. Employee Status

### States

| Status | Meaning |
|---|---|
| ACTIVE | Included in payroll runs; visible in employee list |
| INACTIVE | Excluded from payroll runs; may still be visible in history |

### Transitions
- Not explicitly modelled in the API — status is set during onboarding or contract management.
- The payroll run query filters `WHERE e.status = 'ACTIVE'`.

### UI Rules
- INACTIVE employees should be visually distinguished in the employee list.
- Show INACTIVE employees in historical results (they may have had prior run results).

---

## 6. Payroll Input (Claimed / Unclaimed)

### States

| State | Meaning |
|---|---|
| Unclaimed | payroll_run_id IS NULL — available to be picked up by the next run |
| Claimed | payroll_run_id IS NOT NULL — linked to a specific run; cannot be deleted |

### Transition
- Unclaimed → Claimed: automatically when a payroll run executes and links inputs to itself.

### UI Rules
- Unclaimed inputs: show delete button; show "pending" indicator.
- Claimed inputs: no delete button; show which run they belong to.
- The current inputs list screen (S7) only shows unclaimed inputs — claimed inputs are viewable within the run results.
