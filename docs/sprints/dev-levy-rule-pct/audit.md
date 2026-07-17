# Audit Review — Sprint `dev-levy-rule-pct` — 2026-07-16

**Reviewer:** Claude Code (`/auditor` skill)
**Branch:** `uat`
**Scope:** Development Levy cadence gating (Story 1) and `PERCENTAGE_OF_BASIC` earning rule type (Story 2, RULE-PCT-1)

---

## Findings

### CRITICAL — Story 2's `percentage_of_sum` rule-injected components are silently excluded from GROSS_PAY / NET_PAY in the production pipeline

**Type:** Finding — **Closed this session.** Was a must-fix-before-sign-off blocker on Story 2's own stated acceptance criteria.

**Status: FIXED.** `"percentage_of_sum"` added to the method whitelist at `sequential_executor.py:250`. Re-ran the live reproduction below after the fix: `HAZARD_ALLOWANCE` now appears in `gross_components_jsonb` (`{'BASIC': 100000, 'HOUSING': 20000, 'HAZARD_ALLOWANCE': 5000.00}`) and `GROSS_PAY` correctly rolls up to `125000.00`. Two new regression tests added to `tests/test_sequential_executor.py`: `TestBuildRuntimeComponentRegistry::test_percentage_of_sum_rule_added_as_earning` (registry synthesis) and `TestRuleInjectedEarningInGrossPay::test_percentage_of_sum_rule_injected_earning_included_in_gross_pay` (full-pipeline: asserts the component lands in `results{}` and `GROSS_PAY`, not just the trace). Full suite: 327 passed, 1 skipped (was 325 passed before the two new tests). `npx tsc --noEmit` clean.

**Location:** `backend/domain/payroll/sequential_executor.py:245-260` (`build_runtime_component_registry`, "Source 2 — dynamic_components_from_rules")

**Control Gap:** `build_runtime_component_registry` synthesises a `component_metadata` registry entry (`calculation_method: "salary_component"`, so the sequential executor actually reads the rule's computed value into `results{}`) **only** for rule-injected components whose `calculation_method` is `unit_multiplier`, `fixed_amount`, or `ot_multiplier` (line 250: `if method not in (...): continue`). `percentage_of_sum` is not in that list.

The only reason the existing `percentage_of_sum` use case (`CHECK_OFF_DUES`, Sprint 13 M3) works end-to-end is that it has its **own dedicated seed migration** (`3c4d5e6f7a8b_seed_check_off_dues.py`) permanently registering a platform `component_metadata` row for the literal code `CHECK_OFF_DUES` with `calculation_method='salary_component'`, `execution_priority=450` — i.e. it enters the registry via **Source 1** (pre-seeded platform metadata), not Source 2 (dynamic rule synthesis).

Story 2 (`PERCENTAGE_OF_BASIC`) lets an operator create a **new** `percentage_of_sum` rule through the UI with an **arbitrary `rule_name`** (whatever they type as the rule name, e.g. "Hazard Allowance"). No migration seeds a matching platform `component_metadata` row for that name, and `build_runtime_component_registry`'s Source 2 synthesis explicitly skips `percentage_of_sum`. The result: the rule's computed amount is written into `salary_components` inside `apply_payroll_rules` (correctly, including correct hire-proration via the `prorate_on_hire: true` flag threaded from `executor.py:270-288`), and it correctly appears in `component_trace_jsonb` marked `"status": "applied"` — but it is **never picked up by `run_sequential_payroll`**, because no metadata row exists for it. It therefore never enters `results{}`, never enters `GROSS_PAY` (`_handle_sum_earnings` sums `results{}`, not `salary_components`), never enters `TAXABLE_INCOME`, and never reaches the employee's net pay.

**Live reproduction** (confirms this is not a theoretical concern):

```python
# BASIC=100000, HOUSING=20000, rule: HAZARD_ALLOWANCE = 5% of BASIC (percentage_of_sum, prorate_on_hire=True)
out = _run_sequential(components, component_metadata, context, tax_bands=[])

out['component_trace_jsonb']:
    BASIC             | None      | 100000
    HOUSING           | None      | 20000
    GROSS_PAY         | None      | 120000        # HAZARD_ALLOWANCE's ₦5,000 is NOT included
    HAZARD_ALLOWANCE  | applied   | 5000.00        # trace says "applied"...

out['gross_components_jsonb']:
    {'BASIC': {'amount': 100000}, 'HOUSING': {'amount': 20000}}   # ...but it's absent here
```

**Risk:** This is the worst kind of payroll bug — it presents as *working*. `component_trace_jsonb` shows `"status": "applied"` with a correctly-computed, correctly-prorated amount, so an operator or auditor reading the trace alone would conclude the rule fired correctly. The money is silently never paid. Story 2's own acceptance criteria ("next run shows the component = 5% of that employee's ... BASIC, present in gross and trace") is explicitly *not* met — it is present in trace, absent from gross. This would have shipped as a UI feature that appears to work in every manual spot-check of the SlideOver/save flow, and only fail once someone reconciled an actual payslip against the configured rate.

**Evidence Required:** `HAZARD_ALLOWANCE` (or any arbitrarily-named `percentage_of_sum` rule component) present in `results{}`, `gross_components_jsonb`, and reflected in `GROSS_PAY`/`NET_PAY` — not just in `component_trace_jsonb`.

**Recommended Fix:** Add `"percentage_of_sum"` to the method whitelist at `sequential_executor.py:250` alongside `unit_multiplier`, `fixed_amount`, `ot_multiplier`, so Source 2 synthesises a registry entry for it too (same `calculation_method: "salary_component"`, `execution_priority: RULE_COMPONENT_PRIORITY`). Re-run the live reproduction above after the fix to confirm `HAZARD_ALLOWANCE` appears in `gross_components_jsonb` and `GROSS_PAY`. This is a one-line change in the tuple at line 250, but it is load-bearing for the entirety of Story 2 — no test in this sprint's diff (`tests/test_rule_evaluator.py`'s new `TestPercentageOfSum` class) exercises the full `executor.py → build_runtime_component_registry → run_sequential_payroll` pipeline; those tests call `apply_payroll_rules` in isolation, which is why this gap passed the full suite green.

---

### Observation — `is_first_paid_month` cadence gate not recorded as a named field in the `_period_context` trace header

**Type:** Observation (per this skill's Check #11 — "a gate that is not in the trace header cannot be proven to have fired")

**Location:** `backend/domain/payroll/sequential_executor.py:731-752` (`_period_context` trace header construction)

**Control Gap:** `is_first_paid_month` is a per-employee context value that materially gates whether the Development Levy fires outside a January period (`_handle_development_levy_flat`, `sequential_executor.py:449-452`). It is threaded correctly through `per_employee_context_json` for retry reproducibility (confirmed: `executor.py:183`, `payroll_retry_service.py:657-726` restore the frozen snapshot via `get_employee_context_from_result`), but it is not surfaced as a dedicated key in the `_period_context` header dict the way `shift_type`, `salary_basis`, and `hire_proration_applied` are (compare `sequential_executor.py:746-749`).

**Risk:** An automated compliance report or a future auditor filtering `component_trace_jsonb` for "which employees had the levy cadence gate fire via first-paid-month vs. calendar-January" cannot do so without re-deriving `is_first_paid_month` from `payroll_result` history — the same value the engine itself already had in hand at calculation time. This is a lower-severity version of the same failure mode called out in Check #11: the value only becomes visible indirectly, via whether `DEVELOPMENT_LEVY`'s trace entry shows `applied` vs. `not_applied`, not via a directly queryable field.

**Related, same root cause:** When the levy **does** apply, `_handle_development_levy_flat` returns `{code: amount}` with no `_store_trace_extra` call recording *which* of the two triggers ((a) period contains January, (b) `is_first_paid_month`) caused it to fire — only the `not_applied` branch calls `_store_trace_extra`. Per Check #9 ("amount alone is not evidence, amount + source is evidence"), a trace reader can see the levy was charged but not why, in the applied case specifically.

**Evidence Required:** `is_first_paid_month` as a named key in the `_period_context` header (alongside the existing per-employee-context keys already there), and a `_store_trace_extra` call on the `DEVELOPMENT_LEVY` applied path recording which trigger(s) fired (e.g. `{"trigger": "january"}`, `{"trigger": "first_paid_month"}`, or `{"trigger": "both"}` for the documented December-hire-then-January double-fire case).

**Recommended Fix:** Not a blocker for this sprint's sign-off (the levy calculation itself is correct and the underlying value is reconstructible from `payroll_result` history plus the applied/not_applied trace status). Worth a small follow-up: two lines in `_period_context` (add `"is_first_paid_month": ctx.get("is_first_paid_month", False)`) and a `_store_trace_extra` call in the applied branch of `_handle_development_levy_flat` naming the trigger.

### Checked, no issue

- **Multi-Caller Key Consistency (Check #7):** `development_levy_amount` and `development_levy_cadence` use identical key names across `payroll.py`, `payroll_retry_service.py`, and `simulate_payroll.py`/`simulate_payroll_components.py`. `simulate_stepthrough.py` and the simulation scripts don't thread `development_levy_cadence` — flagged in-code (per this sprint's plan, Test-impact housekeeping) as an accepted, documented divergence for non-production simulation tooling, not a production correctness gap.
- **Retry Reproducibility (Check #10):** `is_first_paid_month` is computed once at run creation, frozen into `per_employee_context_json`, and restored via `get_employee_context_from_result` on retry — confirmed retry cannot silently re-derive a different value against live data. `development_levy_cadence`/`development_levy_amount` are re-derived from the workspace's `statutory_rule.rules_jsonb` at retry time via the same temporal-selection path as the original run (statutory rule resolution is date-driven and version-pinned, not "current" — consistent with this repo's `payroll_rule.is_active` standing rule).
- **`percentage_of_sum` trace completeness (Check #9), in isolation:** the `rule_evaluator.py` trace entry itself (lines 703-719) is fully auditable — records `rate`, `base_components`, `resolved_base_values`, `base_total`, and the derivation formula in `note`. The CRITICAL finding above is not a trace-quality gap; the trace is accurate. The gap is entirely downstream, in whether the traced amount ever reaches the payslip.
- **Decimal usage:** all money in both changed handlers (`_handle_development_levy_flat`, `percentage_of_sum` branch) uses `Decimal`, no float. ✅
- **Statutory rule version pinning:** Development Levy amount/cadence are read from the resolved `statutory_rule.rules_jsonb` for the period (same temporal-selection query as every other statutory value), not a live/mutable global. ✅
- **Immutability of finalised records:** no change in this sprint touches `APPROVED`/`PAID` run mutation paths.

## Verdict

**PASS.** CRITICAL finding fixed and re-verified this session (registry whitelist fix, live reproduction re-confirmed, two new full-pipeline regression tests, full suite green at 327 passed/1 skipped, `tsc --noEmit` clean). Story 1 (Development Levy cadence) was already correct and auditable, with one non-blocking Observation logged for a future trace-header hardening pass (not a blocker). Cleared to proceed to `/tester`, including Story 2's live-verification AC checks.
