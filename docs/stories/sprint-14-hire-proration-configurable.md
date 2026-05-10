# Sprint 14 — P1: Workspace-Configurable Hire Proration

**Track:** N (Proration Audit Trail & Proration Fix) — partially closes N2  
**Priority:** P1 — incorrect net pay for mid-period hires on any workspace configured with `fixed_30` or `calendar_days`  
**Effort:** M  
**Arch-council:** ✅ APPROVED WITH CONDITIONS (2026-05-05) — all conditions resolved in plan  
**Plan file:** `~/.claude/plans/zippy-kindling-summit.md`

---

## Problem

Mid-period hire proration ignores the workspace-configured `proration_strategy`.
`compute_hire_termination_factor` always uses a working-days ratio regardless of whether the
workspace has configured `fixed_30` or `calendar_days`.

Example: workspace `a7f69dea` configured `fixed_30` for all components. Employee starts
4 March. Expected: `27/30 = 0.90` (30 − 3 missed days). Actual: `~20/22 ≈ 0.909` (working days).
The error is silent — the result persists as `SUCCESS` with no trace record of which strategy
was applied.

Additionally, `apply_payroll_rules` (absence deductions via `daily_rate_deduction`) runs
**after** hire proration today, meaning it receives a pre-reduced salary as its rate base.
This produces a double-reduction for any employee who is both a mid-period hire and has
absence inputs in the same period.

---

## User Story

```
As a payroll operator,
I want the proration factor for mid-period hires and terminations to respect
the proration_strategy I have configured per component (work_days, calendar_days, or fixed_30),
So that new joiners and leavers are paid exactly what the workspace policy dictates,
and I can verify the calculation from the payslip trace without re-running payroll.
```

---

## Acceptance Criteria

### HP-1 — `fixed_30` hire proration factor
**Given** a workspace with all salary components configured as `proration_strategy = fixed_30`  
**And** an employee whose `contract_start = 2026-03-04` in a March 1–31 run  
**When** the payroll run executes  
**Then** each salary-definition component (BASIC, HOUSING, TRANSPORT) is scaled by `27/30 = 0.9000`  
*(formula: 30 − 3 missed days = 27 active days)*

### HP-2 — `calendar_days` hire proration factor
**Given** a workspace with components configured as `proration_strategy = calendar_days`  
**And** the same employee (March 4 start, March 1–31 period)  
**Then** components are scaled by `28/31 ≈ 0.903226`  
*(28 calendar days active March 4–31)*

### HP-3 — `work_days` unchanged (regression)
**Given** a workspace with `proration_strategy = work_days` (or no strategy set)  
**Then** behaviour is identical to the pre-sprint baseline (working days ratio)

### HP-4 — Full-period employees unaffected
**Given** `contract_start` predates or equals `period_start` AND `contract_end` is null or post-period  
**Then** no proration is applied (factor = 1.0) regardless of strategy

### HP-5 — Hire + absence in same period: correct ordering
**Given** an employee with `contract_start = 2026-03-04` AND a `daily_rate_deduction` input of 2 absent days  
**When** the run executes  
**Then** the absence deduction is computed against the **full-month salary** (not pre-prorated),  
**And** hire proration is applied **after** the absence deduction reduces the component  
*(the absence deduction reduces by 2×daily_rate; hire proration then scales the remainder)*

### HP-6 — Fixed-amount rule outputs not prorated by default
**Given** a `fixed_amount` payroll rule (e.g. ₦50,000 performance bonus)  
**And** `prorate_on_hire` is absent or `false` in the rule definition  
**When** the employee is a mid-period hire  
**Then** the bonus is paid in full  
**And** the trace records `prorate_on_hire: false` for that component

### HP-7 — Fixed-amount rule with `prorate_on_hire: true`
**Given** the same bonus rule with `prorate_on_hire: true` in `rule_definition_json`  
**Then** the bonus is scaled by the hire proration factor using `work_days` strategy  
**And** the trace records `prorate_on_hire: true, strategy: work_days, factor: <value>`

### HP-8 — Per-component trace entries in `component_trace_jsonb`
**Given** any run where hire proration applies (factor < 1)  
**Then** `component_trace_jsonb` contains a `_proration` entry for each component that was scaled, recording:  
`component_code`, `strategy`, `active_from`, `active_to`, `factor`  
**And** the `_period_context` trace header includes `hire_proration_applied: true`

### HP-9 — WorkspaceConfig second edit form preserves existing `proration_strategy`
**Given** a component with `proration_strategy = fixed_30` saved in the DB  
**When** the operator opens the second edit form (salary/rate override SlideOver) and saves any field without touching the proration dropdown  
**Then** `proration_strategy` remains `fixed_30` in the DB  
*(previously defaulted to `work_days` on every save)*

### HP-10 — Rule-injected components (OT, allowances) fall back to `work_days`
**Given** a workspace configured with `fixed_30`  
**And** an OT component injected by a payroll rule (not in `client_component_metadata`)  
**When** a mid-period hire has OT pay  
**Then** the OT component is prorated using `work_days` (the safe default)  
**And** the trace annotates this component with `strategy: work_days (fallback — rule-injected)`

---

## Out of Scope

| Item | Reason |
|------|--------|
| N1 — Merge `_rule_trace` into `component_trace_jsonb` | Separate arch-council gate; different schema contract surface |
| OT multiplier rate-base reconstruction (N2 remainder) | `ot_multiplier` uses actual OT hours input — inherently self-prorating; separate story if needed |
| Workspace-level global default `proration_strategy` overriding per-component config | Per-component is the correct granularity; global default would require new DB column |
| Prorating rule-injected components by anything other than `work_days` | Requires adding rule-injected codes to `client_component_metadata`; deferred |
| Retroactive re-calculation of existing payroll runs | Runs are immutable once persisted; operators must trigger a new run |

---

## Business Risk

| | |
|---|---|
| **Cost of NOT doing** | Every mid-period hire on a `fixed_30` workspace is paid the wrong amount silently. The error is undetectable from the trace. Statutory PAYE, pension, and NHF are all computed on the wrong gross — compounding the error downstream. |
| **Cost of doing wrong** | Wrong proration factor (e.g. still using working-days numerator for `fixed_30`) produces incorrect net pay that passes all validation. Numerator formula (`30 − missed_days`, not `calendar_days_active / 30`) is the critical correctness invariant. |
| **Blocked by this** | Workspace `a7f69dea` cannot confidently run payroll for any employee hired mid-month until this is fixed. |

---

## Implementation Notes (from arch-council + plan)

1. **`compute_hire_termination_factor` signature change**  
   Add `strategy: str = "work_days"` (default preserves existing behaviour).  
   `fixed_30` formula: `max(0, 30 − missed_days) / 30` where  
   `missed_days = (active_from − period_start).days + (period_end − active_to).days`

2. **Ordering fix in `_run_sequential`**  
   Capture `original_component_codes = set(salary_components.keys())` before `apply_payroll_rules`.  
   Move per-component proration block to **after** `apply_payroll_rules`.

3. **Per-component loop**  
   For original components: use `client_meta[code]["calculations_behaviour"]["proration_strategy"]` (default `work_days`).  
   For rule-injected components: skip unless `prorate_on_hire: true` in rule def; always use `work_days` strategy.

4. **Trace**  
   Inject `_proration` entries via `_supplemental_traces`. Add `hire_proration_applied` to `_period_context` header.

5. **Frontend fix**  
   `WorkspaceConfig.tsx` line 916: second SlideOver `prorationStrategy` state must initialise from `co.proration_strategy` (not hardcoded `'work_days'`).

---

## Open Questions

None — all binding decisions captured in arch-council session 2026-05-05.
