# Sprint 12 — Track M (Statutory Deduction Completeness) & Track N (Proration Audit Trail)

**Sprint goal:** Extend the payroll engine with non-taxable component support, a PAYE-only additions path, check-off dues, and employer-cost handlers (Track M); and surface the rule evaluation trace in the persistent audit record with a standardised `rate_basis` field (Track N).

**Arch-council gate (MANDATORY — no code before this):**
- Track M: Run a single joint arch-council session covering M1 (NEW-GAP14) + M2 (NEW-GAP15) together before any implementation begins. They share the GROSS_PAY / TAXABLE_INCOME aggregation contract surface in `sequential_executor.py`.
- Track N / N1: Run arch-council before N1. Merging `_rule_trace` into `component_trace_jsonb` extends a persisted schema contract with downstream readers (UI renderer, retry snapshot reader).
- Track N / N2: Remains **BLOCKED** — awaiting Model A/B proration decision from client. Do NOT implement N2 in Sprint 11.

**Roadmap refs:** Track M (M1–M5), Track N (N1–N2)

---

## Story Index

| Story | Summary | Priority | Effort | Track | Gate |
|-------|---------|----------|--------|-------|------|
| M1 | Non-taxable component class — exclude from GROSS_PAY + TAXABLE_INCOME | P1 | M | M | Arch-council (joint M1+M2) |
| M2 | PAYE-only additions path — `input_category='paye_only'` into TAXABLE_INCOME | P1 | M | M | Arch-council (joint M1+M2) |
| M3 | Check-off dues handler — 2% × (BASIC + HOUSING + TRANSPORT) | P2 | S | M | After M1 |
| M4 | Life insurance flat ₦2,000 — change rate×GROSS_PAY to flat-amount pattern | P3 | XS | M | After M1 |
| M5 | NSITF/ITF employer cost handlers — 1% × (BASIC + HOUSING + TRANSPORT) each | P3 | S | M | After M1 |
| N1 | Merge `_rule_trace` into `component_trace_jsonb`; add `rate_basis` per entry | P1 | M | N | Arch-council (standalone) |
| N2 | Proration factor fix — ot_multiplier + daily_rate_deduction rate base | — | — | N | **BLOCKED — do not start** |

---

## Explicitly Out of Scope (Sprint 11)

| Item | Ref | Reason |
|------|-----|--------|
| Proration factor fix (WI-03) | N2 | BLOCKED — client has not confirmed Model A or Model B proration ordering |
| Employee schema extensions (shift_type, state_of_tax, skill_level) | Track O | Entry gate: Tracks K–N complete first |
| Grade percentage structure | O2 | Arch-council required; Track O gate |
| Full shift allowance handler | O3, O4 | Blocked on O1 |
| LTA anniversary trigger | O5 | Arch-council required; Track O gate |
| Timesheet / Attendance Layer | O6 | Requires full dedicated PM + arch-council sprint |
| Snapshot replay endpoint | P4-2 | Phase 3 |

---

## Pre-Sprint Checklist

Before entering plan mode, confirm the following with the user:

- [ ] Arch-council session for M1+M2 is scheduled (cannot begin Track M implementation without it)
- [ ] Arch-council session for N1 is scheduled (cannot begin N1 implementation without it)
- [ ] Client has confirmed which statutory deductions apply to their workforce (check-off dues, NSITF/ITF — confirm Client A vs Client B applicability)
- [ ] Life insurance ₦2,000 flat amount confirmed for all clients or only specific workspace(s)
- [ ] N2 proration model decision from client — if unblocked, add N2 to scope and rerun arch-council

---

## M1 — Non-Taxable Component Class (NEW-GAP14)

**Priority:** P1 — financial correctness. If a non-taxable allowance is incorrectly included in GROSS_PAY, the employee is over-taxed on PAYE every period.

**Arch-council required (joint with M2) — do not implement before sign-off.**

```
As a payroll operator configuring a workspace,
I want to mark certain salary components as non-taxable,
So that those allowances are paid to the employee in full but do not inflate
the PAYE base, and PAYE is calculated only on the components the law requires.
```

**What is wrong today:**
All positive pay components flow into `_handle_sum_earnings` and are included in `GROSS_PAY`, which feeds `TAXABLE_INCOME`. There is no mechanism to add an allowance that is paid to the employee but excluded from PAYE. Nigerian law explicitly provides for non-taxable allowances (e.g. certain transport, meal, and utility allowances up to statutory limits).

**Acceptance Criteria:**

- A new `component_class` value `'non_taxable'` is defined and documented. Existing `component_class` values (`'earning'`, `'deduction'`, `'statutory_deduction'`, `'employer_cost'`) are unchanged in meaning.
- In `sequential_executor.py`, `_handle_sum_earnings` excludes any component whose `component_class` is `'non_taxable'` from the `GROSS_PAY` total.
- `TAXABLE_INCOME` computation does not include `non_taxable` components (since it is derived from `GROSS_PAY` plus/minus adjustments — confirm downstream formula is safe).
- `non_taxable` components ARE included in the employee's `NET_PAY` total — the employee receives them; they just do not attract PAYE.
- `component_trace_jsonb` records the component and its class, so an auditor can see which components were excluded from the PAYE base.
- Existing workspaces with no `non_taxable` components are unaffected — backward compatibility is preserved.
- A migration adds the `non_taxable` value to the allowed `component_class` enum/check constraint. Pre-check guard in `DO $$ BEGIN … END $$` block confirms the value does not already exist before insertion.
- Downgrade removes the enum value only if no live rows use it (check row count in downgrade body; raise if > 0).

**Open Questions:**
- Does the Nigerian statutory limit on non-taxable transport allowance (currently ₦20,000/month) need to be enforced at this stage, or is the operator responsible for entering the correct amount?
- Is `non_taxable` a property of the `component_metadata` row or the `salary_definition` component entry? (Arch-council to decide — affects where the class is read at run time.)

**Out of Scope:**
- Statutory cap enforcement (e.g. transport allowance ₦20,000 limit). Track M just introduces the class.
- Any UI changes. This sprint is backend engine + migration only.
- Changing the meaning of `'earning'` — do not repurpose existing classes.

**Business Risk:**
- Cost of NOT doing this: employees are over-taxed each period; operator cannot model tax-efficient salary structures; PAYE remittances are overstated.
- Cost of doing it wrong: if `NET_PAY` accidentally excludes the component, employees are underpaid. If `TAXABLE_INCOME` still includes it, the feature is a no-op. Both must be tested explicitly.

---

## M2 — PAYE-Only Additions Path (NEW-GAP15)

**Priority:** P1 — compliance correctness for bonus and benefit structures that must attract PAYE but are not cash allowances paid to the employee (e.g. notional benefits, LTA).

**Arch-council required (joint with M1) — do not implement before sign-off.**

```
As a payroll operator,
I want to flag a payroll input as 'paye_only',
So that the amount is added to the employee's taxable income for PAYE purposes
without being paid out in their net salary.
```

**What is wrong today:**
All `payroll_input` rows are treated identically — their amounts flow through the normal component chain into both GROSS_PAY and NET_PAY. There is no way to say "this ₦X increases the employee's PAYE liability but is not a cash disbursement" — which is required for notional benefits and some LTA structures under Nigerian tax law.

**Acceptance Criteria:**

- A migration adds `input_category VARCHAR(20) NOT NULL DEFAULT 'standard'` to `payroll_input`. Allowed values: `'standard'`, `'paye_only'`. No other values are valid.
- The migration includes a `CHECK (input_category IN ('standard', 'paye_only'))` constraint. Migration guard prevents duplicate column if already added.
- In the executor, `paye_only` input rows are aggregated into a separate `PAYE_ONLY_ADDITIONS` subtotal.
- `PAYE_ONLY_ADDITIONS` is added to `TAXABLE_INCOME` (increases the PAYE base).
- `PAYE_ONLY_ADDITIONS` is NOT added to `GROSS_PAY` or `NET_PAY` (not a cash disbursement).
- `component_trace_jsonb` records `PAYE_ONLY_ADDITIONS` as a named component with its value, so an auditor can verify the PAYE uplift.
- On retry, the snapshot captures `PAYE_ONLY_ADDITIONS` so the retry reproduces the same TAXABLE_INCOME — not a live re-read of inputs.
- Existing `payroll_input` rows default to `'standard'` and behave identically to today.
- A `paye_only` input staged for a period with zero value is silently skipped (no-op, no trace entry).

**Open Questions:**
- Should `paye_only` inputs be claimable via the standard input claiming endpoint at run start, or is there a separate intake path? (If standard claiming, the `input_category` must be preserved through the claim cycle.)
- Should `paye_only` inputs appear in the exported PAYE remittance schedule? They increase the PAYE liability but have no gross-pay line. (Confirm with operator — likely yes, with a separate section.)
- Does LTA (NEW-GAP11) use `input_category='paye_only'`? If so, M2 is a prerequisite for O5. Confirm this dependency.

**Out of Scope:**
- UI for marking an input as `paye_only` at staging time. This sprint is backend only.
- Changes to the net pay bank export. `paye_only` inputs do not affect disbursement amounts.
- Automatic injection of `paye_only` inputs (that is Track O / O5 LTA). M2 only handles the engine-side aggregation.

**Business Risk:**
- Cost of NOT doing this: notional benefits and LTA cannot be processed; PAYE is under-collected; statutory compliance failure.
- Cost of doing it wrong: if `paye_only` incorrectly enters NET_PAY, employees receive phantom cash; if it does not enter TAXABLE_INCOME, PAYE is under-collected. Both cases are silent financial errors — must be caught by the tester with explicit numeric assertions.

---

## M3 — Check-Off Dues Handler (NEW-GAP6)

**Priority:** P2 — required for Client B workforce (union deduction). Not a statutory obligation in the same class as PAYE/Pension, but contractually required for covered employees.

**Prerequisite:** M1 must be merged first (requires the `component_class` map to be complete).

```
As a payroll operator running payroll for a unionised workforce,
I want check-off dues to be calculated automatically as 2% of
(BASIC + HOUSING + TRANSPORT),
So that the correct union deduction is applied without manual input each month.
```

**What is wrong today:**
No check-off dues handler exists. The deduction must be entered manually as a raw input, which is error-prone and not reproducible from rules alone.

**Acceptance Criteria:**

- A new component handler for `CHECK_OFF_DUES` is implemented following the established handler pattern in `rule_evaluator.py`.
- Formula: `CHECK_OFF_DUES = 2% × (BASIC_MONTHLY + HOUSING + TRANSPORT)`. Components are read from the already-computed salary components dict at the point the handler fires.
- `component_class` for `CHECK_OFF_DUES` is `'statutory_deduction'` (same class as NHF, Pension) — it reduces NET_PAY and does NOT reduce TAXABLE_INCOME.
- A `component_metadata` row is seeded for `CHECK_OFF_DUES` with the correct `component_class` and canonical component order.
- The handler only fires for workspaces where the `CHECK_OFF_DUES` component is enabled in their `client_component_metadata`. It must be opt-in, not default-on for all workspaces.
- `component_trace_jsonb` includes a `CHECK_OFF_DUES` entry with the computed amount and the three base components used.
- On retry, the handler re-derives from the frozen salary snapshot — not live salary tables.

**Open Questions:**
- Is check-off dues applicable to all employees in the workspace or only those with a specific contract type / grade? If grade-scoped, the handler needs an employee-level flag — confirm with client before implementation.
- Is the 2% rate configurable per workspace, or fixed across all clients?

**Out of Scope:**
- Check-off dues export schedule (separate disbursement item — not in this sprint).
- UI to enable/disable the component per workspace. Use the existing component override mechanism.

**Business Risk:**
- Cost of NOT doing this: manual workaround each month; union compliance risk for Client B.
- Cost of doing it wrong: over- or under-deducting union dues creates employee trust issues and potential grievance claims.

---

## M4 — Life Insurance Flat ₦2,000 (GAP-10-FIX)

**Priority:** P3 — correctness fix for existing behaviour; low financial impact per employee.

**Prerequisite:** M1 must be merged first (class map validation; backward-compat fallback needed for other clients still using rate-based).

```
As a payroll operator,
I want life insurance deducted as a flat ₦2,000 per employee per period,
So that the deduction matches the actual policy premium rather than
a percentage of gross pay.
```

**What is wrong today:**
The life insurance handler currently computes `rate × GROSS_PAY`, which is wrong. The correct amount is a flat ₦2,000. For a ₦500,000 gross-pay employee at a 0.4% rate, the current handler deducts ₦2,000 — which happens to match. But for higher-earners the rate-based formula over-deducts, and any workspace where the rate seed is wrong produces incorrect results.

**Acceptance Criteria:**

- The life insurance handler is changed to read a flat `employer_amount` from `rules_jsonb` rather than a `rate` × `GROSS_PAY` formula.
- The `component_metadata` seed row for life insurance is updated: `employer_amount = 2000` in `rules_jsonb`. The old `rate` key is removed from the seed.
- A backward-compat fallback is preserved: if a workspace's `rules_jsonb` still contains a `rate` key (no `employer_amount`), the handler logs a deprecation warning and falls back to `rate × GROSS_PAY`. This prevents breaking existing workspaces during the transition.
- `component_trace_jsonb` records the deduction amount and the source field (`employer_amount` or rate-based fallback) so the path is auditable.
- A data migration updates the existing seeded value in the platform's `component_metadata` rows. Idempotent — safe to re-run.

**Open Questions:**
- Confirm: is ₦2,000 the correct flat amount for all clients, or is it workspace-specific? If workspace-specific, the amount must live in `client_component_metadata`, not the platform seed.

**Out of Scope:**
- Removing the rate-based fallback path in this sprint. Leave it in place until all existing workspaces have been confirmed to be migrated.

**Business Risk:**
- Low per-period impact (₦2,000 is a small deduction). Risk is primarily audit consistency — a rate-based formula is not reproducible against the policy document.

---

## M5 — NSITF/ITF Employer Cost Handlers (NEW-GAP7)

**Priority:** P3 — statutory employer obligation (Industrial Training Fund + NSITF). Not deducted from employee pay. Required for correct cost reporting.

**Prerequisite:** M1 must be merged first (requires `employer_cost` class map extension).

```
As a payroll operator producing employer cost reports,
I want NSITF and ITF employer contributions calculated automatically as
1% of (BASIC + HOUSING + TRANSPORT) each,
So that the full cost of employment is captured in the payroll record
without affecting employee take-home pay.
```

**What is wrong today:**
No NSITF or ITF handlers exist. Employer costs must be calculated manually outside the platform, making the payroll record incomplete and reconciliation with finance difficult.

**Acceptance Criteria:**

- Two component handlers are implemented: `NSITF_EMPLOYER` and `ITF_EMPLOYER`.
- Formula for each: `1% × (BASIC_MONTHLY + HOUSING + TRANSPORT)`.
- `component_class` for both is `'employer_cost'`. Employer costs do NOT reduce employee NET_PAY and do NOT enter TAXABLE_INCOME.
- `component_metadata` seed rows for both handlers are added with canonical order after all employee deductions.
- Both handlers are opt-in per workspace via `client_component_metadata` — not default-on.
- `component_trace_jsonb` records both amounts and the base components used.
- The net pay bank export does NOT include employer cost components. The PAYE remittance schedule does NOT include them. A separate employer cost report (future sprint) will surface them.

**Open Questions:**
- Confirm with client: is the ITF rate 1% for all covered employers or does the rate differ by payroll size? (The statutory rate is 1% for employers with ≥ 5 employees and annual payroll ≥ ₦50M — confirm whether we enforce the threshold or leave that to the operator.)
- Is there a combined employer cost export required in Sprint 11 or deferred to a later sprint?

**Out of Scope:**
- Employer cost export schedule. Deferred to a later sprint.
- Employee-visible payslip lines for employer costs. Employer costs are not payslip items.

**Business Risk:**
- Cost of NOT doing this: employer cost reporting is incomplete; finance cannot reconcile total employment cost from the payroll record alone.
- Cost of doing it wrong: if employer costs accidentally enter NET_PAY, employees receive inflated salaries.

---

## N1 — Merge `_rule_trace` into `component_trace_jsonb`; Add `rate_basis` Field (WI-08)

**Priority:** P1 — audit completeness. Rule evaluation outcomes are currently discarded after every run. An auditor cannot verify from the DB how a component amount was derived — they can only see the result, not the inputs to the rule evaluation.

**Arch-council required (standalone session) — do not implement before sign-off.**

```
As an auditor or payroll operator reviewing a completed payroll run,
I want to see how each pay component was calculated — including the rate
and base values the rule evaluator used — in the persisted audit record,
So that I can verify the calculation is correct without re-running the payroll
or reading the source code.
```

**What is wrong today:**
`apply_payroll_rules()` in `rule_evaluator.py` produces a `_rule_trace` dict that contains the rate, base, and derivation path for each evaluated rule. In the current executor, this dict is **discarded unconditionally** after the call returns — it is never written to the DB. `component_trace_jsonb` records what was computed, not how. This gap was flagged as AUD-1 in Sprint 10.

**Acceptance Criteria:**

- `apply_payroll_rules()` returns `_rule_trace` alongside the existing component values (or it is read from the returned dict — arch-council to decide the merge point).
- In `sequential_executor.py`, `_rule_trace` entries are merged into the corresponding entries in `component_trace_jsonb`. Each component entry in the trace gains a `rate_basis` object with (at minimum):
  - `rate_source`: the field name from `rules_jsonb` that provided the rate (e.g. `'employee_rate'`, `'employer_amount'`, `'percentage'`)
  - `rate_value`: the Decimal value of the rate used
  - `base_value`: the Decimal value of the base the rate was applied to (e.g. `BASIC_MONTHLY` for NHF, `GROSS_PAY` for pension)
  - `derivation_path`: one of `'direct'`, `'fallback'`, `'cross_period'`
- For the `fixed_amount` handler specifically: if a salary-definition reference was used (not a hardcoded value), `rate_basis.component_source` records the salary component name — this closes AUD-1.
- For components that have no rate (e.g. sum aggregates like `GROSS_PAY`): `rate_basis` is omitted or set to `null`. Do not add noise.
- `component_trace_jsonb` schema is backward-compatible: existing entries without `rate_basis` are valid. The UI renderer and retry snapshot reader must tolerate absent `rate_basis` fields.
- On retry, the `rate_basis` from the original snapshot is preserved — not recomputed. This is critical for audit reproducibility.
- The existing test suite passes. New tests assert that after a run, at least the NHF, Pension, and PAYE trace entries contain a populated `rate_basis` field.
- No change to the DB column type or constraint — `component_trace_jsonb` remains `JSONB`. No migration required unless arch-council identifies one.

**Open Questions (arch-council items):**
- Where is the cleanest merge point? Options: (a) `apply_payroll_rules()` returns an enriched dict; (b) `_rule_trace` is returned alongside and merged in the executor; (c) each handler writes directly into a trace accumulator. Arch-council to decide.
- `_rule_trace` is currently keyed by `component_name`. `component_trace_jsonb` is a list. Confirm the merge key and handle the case where a component appears in one but not the other.
- Does adding `rate_basis` to existing `component_trace_jsonb` entries break the UI renderer or the retry snapshot reader? Audit both callers before implementation.
- For cross-period inputs (FIX-1 path): `derivation_path='cross_period'` should capture which period the rate was sourced from. Is this already available in the rule evaluator context, or does it need to be threaded through?

**Out of Scope:**
- UI renderer for `rate_basis` fields. The data will be in the DB; displaying it is a separate story.
- Changing the `component_trace_jsonb` column type.
- Back-filling historical run records. Only new runs get the enriched trace.

**Business Risk:**
- Cost of NOT doing this: audit trail is structurally incomplete; an external auditor cannot verify PAYE calculation from the DB record alone; platform cannot pass a financial audit.
- Cost of doing it wrong: if `rate_basis` merging corrupts existing trace entries, the calculation trace for all future runs is unreadable — this is a high-severity data quality risk. Arch-council must review the merge strategy before any code is written.

---

## N2 — Proration Factor Fix (WI-03) — **BLOCKED — DO NOT START**

**Status:** BLOCKED. Awaiting Model A/B proration ordering decision from client.

**What is blocked:**
`ot_multiplier` and `daily_rate_deduction` handlers currently use the prorated salary as their rate base, which means mid-period hires receive incorrectly scaled OT and deduction amounts. The fix is to reconstruct the full (unprorated) BASIC as the rate base and apply proration separately. However, two valid models exist (Model A: prorate result; Model B: prorate base before applying rule) and the client must confirm which they need before any schema or executor change.

**Unblocking criteria (must be met before this story re-enters scope):**
- Client confirms in writing which proration model applies to `ot_multiplier` rules.
- Client confirms which proration model applies to `daily_rate_deduction` rules.
- If different, confirm whether the model is configurable per rule or per component.
- Arch-council re-run after unblocking — the configurable proration model preferred by the roadmap requires a new field on `payroll_rule` or `client_component_metadata`.

**Do not add N2 to Sprint 11 scope without explicit user confirmation that these blockers are resolved.**

---

## Dependency Map

```
Arch-council (M1+M2 joint) ──► M1 ──► M3, M4, M5
                          └──► M2

Arch-council (N1 standalone) ──► N1

Client Model A/B decision ──► N2 (re-enter arch-council) ──► N2 implementation
```

Track M items have no dependency on Track N and can proceed in parallel once arch-council clears M1+M2.

---

## Definition of Done (Sprint 11)

- [ ] Arch-council sign-off documented for M1+M2 (joint session) and N1 (standalone session)
- [ ] M1: `non_taxable` class implemented; `_handle_sum_earnings` excludes it; `NET_PAY` includes it; migration applied
- [ ] M2: `input_category` column added; `paye_only` aggregated into TAXABLE_INCOME only; migration applied; retry snapshot preserves the value
- [ ] M3: `CHECK_OFF_DUES` handler implemented; opt-in per workspace; `component_metadata` seeded
- [ ] M4: Life insurance handler changed to flat-amount; backward-compat fallback in place; seed updated
- [ ] M5: NSITF/ITF employer cost handlers implemented; do not enter NET_PAY; opt-in per workspace
- [ ] N1: `_rule_trace` merged into `component_trace_jsonb`; `rate_basis` present on NHF/Pension/PAYE entries; retry preserves original trace
- [ ] N2: Remains blocked — no implementation
- [ ] `/tester` verification: numeric assertions for M1 (NET_PAY includes non-taxable, TAXABLE_INCOME excludes it), M2 (PAYE increases; NET_PAY unchanged), M3 (2% formula correct), N1 (rate_basis fields populated in DB after run)
- [ ] `/security` review completed (new `input_category` field is user-supplied — validate allowlist)
- [ ] `/auditor` review completed (TAXABLE_INCOME formula changes and trace schema extension)
- [ ] `/retro` run at sprint close
