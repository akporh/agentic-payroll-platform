# Sprint 31 — Financial Engine Test Suite

## Goal
Write verified unit tests for the payroll calculation engine and rule evaluator. These are the highest-risk files in the system — a silent error here means Sandy's employees receive the wrong pay.

## Background
`sequential_executor.py` and `rule_evaluator.py` contain the core statutory calculation logic: PAYE (cumulative annual method), Pension (8% employee / 10% employer), NHF (2.5% of basic), Health Insurance, Development Levy, overtime, deductions. Tests here are pure Python — no database required. Some tests already exist (`test_calculation_scenarios.py`, `test_payroll_calculator.py`, `test_pension.py`). This sprint fills the gaps and asserts exact `Decimal` values against statutory worked examples.

---

## TEST-A1 — Sequential Executor Unit Tests · P0

**As the developer,**
**I want verified tests for the sequential executor covering all statutory components,**
**So that any change to the calculation engine is immediately caught before it reaches production.**

### Acceptance Criteria
- Tests cover: PAYE (standard, cumulative annual, relief calculations), Pension (employee + employer), NHF, Health Insurance, Development Levy
- All monetary assertions use `Decimal` (never float comparison)
- At least one test per statutory component at boundary values (₦0, minimum wage threshold, upper tax band)
- Tests for mid-period hires (proration)
- Tests for PAYE_ONLY inputs (enter taxable income only, not gross/net)
- Tests for non_taxable component class (excluded from gross, included in net)
- All tests pass `pytest tests/ -x -q` with no DB

### Out of Scope
- UI-level payroll run tests
- Retry logic tests (covered separately)

---

## TEST-A2 — Rule Evaluator Unit Tests · P1

**As the developer,**
**I want verified tests for all rule calculation methods,**
**So that payroll rules (overtime, deductions, fixed amounts) produce correct outputs.**

### Acceptance Criteria
- Tests cover all 6 live `calculation_method` values: `unit_multiplier`, `fixed_amount`, `ot_multiplier`, `daily_rate_deduction`, `percentage_of_sum`, and any remaining methods
- Tests assert rule application does not mutate inputs
- Tests cover priority ordering (higher priority rules applied first)
- Combo scenarios: multiple rules in the same run period

### Out of Scope
- Rule CRUD API tests (covered in Sprint 32)
