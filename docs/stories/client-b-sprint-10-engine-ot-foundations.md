# Client B Sprint 10 — Engine Stability & OT / Rate Code Foundations

**Sprint goal:** Zero runtime crashes, correct PH subtraction, correct PAYE annualization, and an end-to-end OT multiplier pipeline ready for Client B's first payroll run in AUTOMATIC mode.

**Arch-council:** Not required for this sprint. All items are Track K (engine defect fixes) and Track L (onboarding/rate code foundations). No new migrations touch a data contract, status field, or aggregation function. Track M (statutory deductions) and Track N (proration/audit trail) are explicitly out of scope and require arch-council before proceeding.

**Source:** Client B gap closure audit (2026-04-30) — `docs/data/Client B/gaps/client-b-execution-roadmap-2026-04-30.md`

**Roadmap refs:** Track K (K1–K3), Track L (L1–L6), INP10

---

## Story Index

| Story | Summary | Priority | Effort | Track |
|-------|---------|----------|--------|-------|
| CB-1  | Remove PH double-subtraction in AUTOMATIC mode (GAP-2-FIX) | P0 | S | K1 |
| CB-2  | PAYE CUSTOM annualization → ×12 (GAP-5-FIX) | P0 | S | K2 |
| CB-3  | Fix `_resolve_inputs` list/dict type mismatch (WI-15) | P0 | S | Track A |
| CB-4  | Fix cross-period prefetch dead code (FIX-1 / WI-18) | P1 | S | Track A |
| CB-5  | Align NHF key in retry service + simulation scripts (FIX-2 / WI-19) | P1 | S | Track A |
| CB-6  | `tax_bands` float → Decimal at extraction (FIX-4) | P1 | S | Track A |
| CB-7  | `component_source` in `fixed_amount` handler — ₦0 fix (WI-04 Sub-A) | P1 | S | K3 |
| CB-8  | OT rate code configurability — workspace-level rate code assignment (WI-01) | P1 | M | L1 |
| CB-9  | Excel upload template: rename `ot_code` column → `rate_code` (WI-02) | P2 | XS | L2 |
| CB-10 | Excel `ot_multiplier` rule-type parsing (WI-05) | P1 | M | L3 |
| CB-11 | `workspace_payroll_config` onboarding — optional 7th Excel sheet (WI-06) | P1 | M | L4 |
| CB-12 | Verify or remove `PH_ADDITIVE` engine path (VERIFY-PH-ADDITIVE) | P1 | S | L5 |
| CB-13 | Verify Track F API routes are live (VERIFY-API-COVERAGE) | P1 | S | L6 |
| CB-14 | `payroll_input.quantity ≥ 0` DB constraint (WI-23 / INP10) | P2 | XS | Track B |

---

## Explicitly Parked (not in this sprint)

| Item | Ref | Reason |
|------|-----|--------|
| Health/dev levy extraction key fix | WI-20 / FIX-3 | Parked per client review — not blocking first run |
| Rent-relief "TBD" Decimal crash | WI-22 | Parked per client review — not applicable to Client B first run |
| Life insurance flat ₦2,000 | GAP-10-FIX | Parked — low priority |
| Non-taxable component class | NEW-GAP14 | Arch-council required — Sprint 10+ |
| PAYE-only additions path | NEW-GAP15 | Arch-council required — Sprint 10+ |
| Check-off dues handler | NEW-GAP6 | Requires NEW-GAP14 — Sprint 10+ |
| `_rule_trace` persistence (WI-08) | Track N | Arch-council required — Sprint 10+ |
| Proration factor fix (WI-03) | Track N | BLOCKED — awaiting Model A/B decision |
| Employee schema extensions | Track O | Arch-council required — later Phase 2 sprint |

---

## CB-1 — Remove PH Double-Subtraction in AUTOMATIC Mode (GAP-2-FIX)

**Priority:** P0 — financial correctness; every Client B run in AUTOMATIC mode is wrong until this lands.

```
As a payroll operator running payroll in AUTOMATIC mode,
I want public holiday days to be subtracted exactly once from working days,
So that proration factors, expected hours, and PAYE annualization are all
based on the correct number of working days for the period.
```

**What is wrong today:**
`payroll.py:505` does: `expected_working_days = period_ctx.working_days - len(ph_weekday_dates)`.
But `build_period_context()` already returns `working_days` with PHs excluded in AUTOMATIC mode — so this line double-subtracts. A period with 2 PH weekdays computes `working_days` as `21 - 2 = 19` instead of the correct `21`.

**Acceptance Criteria:**

- In AUTOMATIC mode (`ph_mode == 'AUTOMATIC'`): the second `- len(ph_weekday_dates)` subtraction is removed from `payroll.py:505`. `expected_working_days` equals `period_ctx.working_days` directly.
- In FILE_BASED mode (`ph_mode == 'FILE_BASED'`): behaviour is unchanged — `ph_weekday_dates` remains `[]` and the line is a no-op whether removed or retained. Confirm there is no regression.
- Downstream values that consume `expected_working_days` (proration_factor, expected_hours at line ~512, PAYE annualization denominator) all reflect the corrected value automatically.
- A payroll run for Client B's Feb 21–Mar 20 period with NGA 2026 PHs in AUTOMATIC mode produces `expected_working_days` equal to the correct Mon–Fri count minus confirmed PH weekdays for that range (verify against NGA calendar).
- Existing test suite passes. No new test failures.

**Out of scope:** Changing `build_period_context()` itself. Changing FILE_BASED mode behaviour. Any UI changes.

**Business Risk:** Without this fix, AUTOMATIC mode systematically under-reports working days → proration is wrong → every prorated employee is overpaid → PAYE is under-collected → statutory compliance failure on first Client B run.

---

## CB-2 — PAYE CUSTOM Annualization → ×12 (GAP-5-FIX)

**Priority:** P0 — systematic PAYE over-deduction on Client B's custom pay cycle periods.

```
As a payroll operator using a CUSTOM pay cycle (e.g. 21st–20th calendar month),
I want PAYE to be annualized using a factor of 12,
So that employees are not systematically over-taxed due to a variable day-count
in a custom period being misread as an annual multiplier.
```

**What is wrong today:**
`period_context.py:211–216` — the `_DEFAULT_ANNUALIZATION` map has no entry for `PeriodType.CUSTOM`. The fallback computes `365 / period_length_days`. For a Feb 21–Mar 20 period (28 days), this yields ≈ 13.04× instead of 12×. Client B employees are over-taxed by roughly 8.7% every month.

**Acceptance Criteria:**

- `_DEFAULT_ANNUALIZATION` is extended: `PeriodType.CUSTOM → 12`.
- If `pay_cycle.annualization_factor` is explicitly set and non-null, that value takes precedence over the default (preserves future flexibility without requiring it now).
- A CUSTOM period run produces `ann_factor = 12.0` in the execution context.
- The `365 / period_days` fallback path is either removed or explicitly guarded so CUSTOM never hits it.
- Monthly (`PeriodType.MONTHLY`) and bi-weekly (`PeriodType.BI_WEEKLY`) annualization factors are unchanged.
- Existing test suite passes; add one test: CUSTOM period with 28-day range → assert `ann_factor == 12`.

**Out of scope:** Adding a `annualization_factor` UI field to WorkspaceConfig (that is a separate story). Changing how `PeriodType` is stored.

**Business Risk:** Without this, PAYE is over-collected by ~8.7% per month on every Client B employee. This is a statutory liability — over-deduction must be corrected and refunded. Trust damage with client on first run.

---

## CB-3 — Fix `_resolve_inputs` List/Dict Type Mismatch (WI-15)

**Priority:** P0 — silent ₦0 on every OT, PH, and custom input-driven calculation.

```
As a payroll operator who stages OT hours or PH hours inputs before a run,
I want those inputs to be correctly read by the calculation engine,
So that overtime pay, PH overtime pay, and any payroll_input-driven
components produce non-zero amounts instead of silently returning ₦0.
```

**What is wrong today:**
`payroll.py` — `_resolve_inputs()` calls `.get("amount")` on the data structure, but `payroll_input` rows are returned as a list, not a dict. The result is `None` for every input → all input-driven calculations silently produce ₦0. Operators see results, believe them to be correct, but OT amounts are all zero.

**Acceptance Criteria:**

- `_resolve_inputs()` correctly iterates the list of `payroll_input` rows and extracts `quantity` (not `amount`) per input code.
- A staged `ot1_hours = 16` input on a run produces a non-zero OT1 computed amount in `component_trace_jsonb`.
- A staged `ph_hours_worked = 8` input produces a non-zero trace entry.
- No `AttributeError` or silent `None` when a valid input list is provided.
- Regression: runs with no staged inputs continue to compute correctly (empty list case).
- Existing test suite passes.

**Out of scope:** Changing the payroll_input data model. Changing how inputs are staged.

**Business Risk:** Without this, every run at Client B that relies on period input files (OT hours, PH hours, absences) produces ₦0 for those components with no error message. Operators believe the run is correct. This is an invisible financial error.

---

## CB-4 — Fix Cross-Period Prefetch Dead Code (FIX-1 / WI-18)

**Priority:** P1 — prerequisite for OT3/PH_OT cross-period inputs in Track C.

```
As a payroll engine executing a run that includes cross-period rules,
I want cross-period rule sets to be correctly prefetched at run start,
So that PH_OT and multi-period OT calculations can resolve inputs
from adjacent periods without failing silently.
```

**What is wrong today:**
`payroll.py:383` — an `isinstance` guard always evaluates to `False` for lists, meaning the cross-period prefetch block never executes. Any rule that requires inputs from a different period than the current run gets no data.

**Acceptance Criteria:**

- The `isinstance` guard at `payroll.py:383` is corrected so cross-period rule sets are successfully prefetched when present.
- A run containing a rule that references an adjacent period does not fail or silently omit that rule's contribution.
- No regression on standard same-period runs.

**Out of scope:** Implementing new cross-period rule types. UI changes.

**Business Risk:** Without this, Track C OT3/PH_OT pipeline (Sprint 10+) will be built on a broken prefetch path and fail in production. Must land before Track C work begins.

---

## CB-5 — Align NHF Key in Retry Service + Simulation Scripts (FIX-2 / WI-19)

**Priority:** P1 — silent NHF under-deduction on retried runs; statutory compliance on retry path.

```
As a payroll operator retrying a failed run,
I want NHF to be calculated using the correct employee rate,
So that NHF deductions on retried employees are statutory-compliant
and match what a fresh run would produce.
```

**What is wrong today:**
`payroll_retry_service.py` reads `nhf.rate` when constructing the statutory context for a retry. The correct key (per SR9 fix applied to the main route) is `nhf.employee_rate`. The same wrong key exists in `simulate_payroll_components.py`. NHF is silently ₦0 on every retry.

**Acceptance Criteria:**

- `payroll_retry_service.py` is updated: change `nhf.rate` → `nhf.employee_rate` at all read sites (lines 500–516 and 767–782 per the gap audit).
- `simulate_payroll_components.py` is updated with the same key change.
- A retry of a run with an NHF-eligible employee produces the same NHF amount as the original run.
- Confirm with a grep that `nhf.rate` (the wrong key) no longer appears in any of: `payroll.py`, `payroll_retry_service.py`, `simulate_payroll_components.py`.

**Out of scope:** Changing the NHF rate stored in DB. Changing the main route (SR9 already fixed it).

**Business Risk:** Without this, every retried run at Client B produces NHF = ₦0. Pension remittances submitted after a retry are statutorilyi non-compliant. NHF under-remittance carries penalties.

---

## CB-6 — `tax_bands` Float → Decimal at Extraction (FIX-4)

**Priority:** P1 — floating-point drift in PAYE; amplified once OT/PH flows into PAYE base.

```
As the payroll engine computing PAYE,
I want all tax band boundary values to use Decimal arithmetic,
So that progressive PAYE calculations are free from floating-point
rounding drift, particularly once OT and PH amounts begin flowing
into the PAYE tax base.
```

**What is wrong today:**
`payroll.py:195–202` — `tax_bands` values are extracted as floats. Progressive PAYE uses these boundaries in comparisons and multiplications. With small salaries the drift is minor; once OT→PAYE path goes live (Track C), the drift compounds across every OT-earning employee.

**Acceptance Criteria:**

- All `tax_bands` values (lower_bound, upper_bound, rate) are converted to `Decimal` at extraction time in `payroll.py:195–202`, before any comparison or multiplication.
- PAYE computation for an employee with a known gross produces the exact expected Decimal result (no floating-point discrepancy to 2dp).
- Existing PAYE tests pass.

**Out of scope:** Changing how tax bands are stored in DB. Changing the PAYE formula itself.

**Business Risk:** Float drift in tax bands is a correctness risk that silently underpays or overpays PAYE by fractions. Undetectable without Decimal-level comparison. Statutory penalties apply to under-remittance, even if small per employee.

---

## CB-7 — `component_source` in `fixed_amount` Handler (WI-04 Sub-A)

**Priority:** P1 — shift allowance and any salary-referenced fixed-amount rule produces ₦0 today.

```
As a payroll operator with rules that reference a salary component
(e.g. a shift allowance equal to the employee's TRANSPORT component),
I want the engine to look up the component value at run time
when the rule's fixed amount is zero and a component_source is specified,
So that salary-referenced rules produce correct non-zero amounts
without requiring a separate override per employee.
```

**What is wrong today:**
`rule_evaluator.py:316` — the `fixed_amount` handler reads `amount` from the rule definition. If `amount == 0` (which is valid when the rule is meant to reference a salary component), the handler returns ₦0 without checking `component_source`. Any rule of the form "shift allowance = TRANSPORT component" silently pays ₦0.

**Acceptance Criteria:**

- When `amount == 0` in a `fixed_amount` rule and `component_source` is present in the rule definition, the handler reads `components.get(component_source, Decimal("0"))` from the employee's salary components at evaluation time.
- When `amount > 0`, existing behaviour is unchanged — the fixed amount is used directly.
- **Double-count guard:** If `component_source` points to a component that is already included in `GROSS_PAY` as a salary component, the rule output must replace, not add to, that salary component's contribution. The handler must not double-count. Document the resolution (e.g. component entry in salary_components is excluded from raw GROSS_PAY summation when a rule also references it, or rule output overwrites the entry).
- A rule `{calculation_method: "fixed_amount", amount: 0, component_source: "TRANSPORT"}` produces an amount equal to the employee's TRANSPORT salary component value.
- Existing `fixed_amount` rules with a positive `amount` are unaffected.

**Out of scope:** WI-04 Sub-B (full shift allowance handler with shift_days_worked — that is Track O, requires NEW-GAP4). Building the shift allowance rule in WorkspaceConfig UI.

**Business Risk:** Any client with salary-referenced rules (shift allowance, component-linked bonuses) gets ₦0 for those components on every run with no error. The operator has no way to detect this without manually cross-checking each employee's trace.

---

## CB-8 — OT Rate Code Configurability — Workspace-Level Assignment (WI-01)

**Priority:** P1 — OT multipliers must use client-configured rate codes, not hardcoded platform defaults.

```
As a payroll operator configuring overtime rules for my workspace,
I want to select which rate code governs each OT type (weekday OT,
Saturday OT, Public Holiday OT) from the rate code registry,
So that my workspace's OT calculation uses the correct multiplier
(e.g. OT005 at 2.5× for weekday instead of OT001 at 1.5×) without
requiring a platform code change.
```

**Background:**
The platform seeds OT001 (1.5×), OT002 (2.0×), OT003 (3.25×) etc. as platform defaults. But Client B may define overtime bands that map to different rate codes (e.g. OT005 at a negotiated rate). The current engine uses hardcoded lookups by rate code name. Rate codes should be configurable per workspace per OT category.

**Open Question (must resolve before implementation):**
1. Where does the workspace OT rate code mapping live? Options: (a) `workspace_payroll_config` — add fields `weekday_ot_rate_code`, `saturday_ot_rate_code`, `ph_ot_rate_code`; (b) on the payroll rule itself — the `rate_code` field in `rule_definition_json` already specifies which code to use per rule. If option (b) is already the design (operators select `rate_code` when creating an OT rule), then this story reduces to: ensure the rate_code_registry has the correct multiplier for whichever code the workspace assigns, and ensure the seeded platform codes (OT001–OT003) cannot be overridden by workspace rows with different values for the same code.
2. Are the platform OT seeds (OT001=1.5×, OT002=2.0×, OT003=3.25×) currently correct in the DB? The gap audit flagged a possible seed mismatch. Verify with `SELECT code, multiplier FROM rate_code_registry WHERE workspace_id IS NULL` before writing any migration.

**Acceptance Criteria (contingent on open question resolution):**

- Platform-seeded rate codes (`workspace_id IS NULL`) cannot be shadowed by workspace rows with a different multiplier for the same code. Workspace rows can ADD new codes but not override platform multipliers.
- An OT rule with `rate_code: "OT005"` where OT005 exists only in the workspace's registry correctly uses the workspace multiplier.
- An OT rule with `rate_code: "OT001"` uses the platform multiplier (1.5×) regardless of whether a workspace row exists for OT001.
- If the open-question answer is (a): `workspace_payroll_config` gains nullable `weekday_ot_rate_code`, `saturday_ot_rate_code`, `ph_ot_rate_code` fields. The engine reads these at run start. Migration is wrapped in duplicate-column guards.
- Operator can see and verify assigned rate codes in the Rate Code Registry page (Track G / Gate 5) before running payroll.

**Out of scope:** Building a new UI for rate code assignment (that is Gate 5 / UI-NAV-3, already in roadmap). Changing the rate for an existing platform code (platform codes are immutable).

**Business Risk:** Without this, Client B's OT calculations use whatever multiplier happens to be seeded in the platform codes, which may not match the employment contract. OT underpayment is a labour law violation.

---

## CB-9 — Excel Upload Template: Rename `ot_code` Column → `rate_code` (WI-02)

**Priority:** P2 — template alignment; low-effort cleanup.

```
As a payroll operator uploading OT multiplier rules via Excel,
I want the column header to be named "rate_code" rather than "ot_code",
So that the upload template reflects the canonical field name used by
the system and I do not need to remember that "ot_code" maps to "rate_code".
```

**Background:**
The gap audit noted that old Excel templates use `ot_code` as the column for the rate code value. The engine stores this as `rate_code` in `rule_definition_json`. Per client review, the simplest fix is to update the Excel template column header. If the upload parser already accepts `rate_code`, no code change may be needed — this story should verify before implementing.

**Acceptance Criteria:**

- Verify: does `WorkspaceExcelUpload.tsx` currently accept `rate_code` as a column header for OT multiplier rules? If yes: update the downloadable template file only; no parser code change needed.
- The upload template's OT rules sheet uses `rate_code` as the column header for the rate code value.
- Uploading a file with `ot_code` header: the parser either (a) normalises `ot_code` → `rate_code` silently (one-line defensive read), or (b) surfaces a clear validation error: "Column 'ot_code' is no longer supported. Please use 'rate_code'."
- Uploading a file with `rate_code` header works correctly end-to-end.

**Out of scope:** Changing how rate codes are evaluated in the engine. Any UI form changes.

---

## CB-10 — Excel `ot_multiplier` Rule-Type Parsing (WI-05)

**Priority:** P1 — without this, OT multiplier rules cannot be uploaded via Excel; Client B must use JSON onboarding.

```
As a payroll operator onboarding OT rules via Excel upload,
I want the system to recognise "ot multiplier" as a valid rule type
in the upload template,
So that I can define all my payroll rules in the familiar Excel format
without falling back to raw JSON.
```

**What is wrong today:**
`WorkspaceExcelUpload.tsx` `RULE_TYPE_MAP` (around line 242) does not include `'ot multiplier': 'ot_multiplier'`. Rows in the rules sheet with type "ot multiplier" are silently skipped or produce a parse error, leaving the workspace with no OT rules after Excel onboarding.

**Acceptance Criteria:**

- `RULE_TYPE_MAP` includes `'ot multiplier': 'ot_multiplier'` (case-insensitive matching consistent with existing entries).
- An Excel rules sheet row with `rule_type = "ot multiplier"` and `rate_code = "OT001"` produces a `payroll_rule` row with `calculation_method = 'ot_multiplier'` and `rule_definition_json = {"rate_code": "OT001"}`.
- If `rate_code` value is not found in `rate_code_registry` for this workspace (platform or workspace-scoped), a **warning** (not a hard block) is surfaced in the upload preview: "Rate code OT001 not found in registry — rule will be created but may not evaluate."
- Upload does not hard-block on unknown rate codes — operator can proceed and fix the registry separately.
- All existing rule types in the map continue to parse correctly.

**Out of scope:** Validating the multiplier value itself. Creating rate codes from the upload (that is the rate code registry flow).

**Business Risk:** Without this, operators cannot onboard Client B via the standard Excel path for OT rules. Every OT rule must be manually created via JSON or the rules UI, which is error-prone at scale and increases onboarding time.

---

## CB-11 — `workspace_payroll_config` Onboarding Integration (WI-06 / H2)

**Priority:** P1 — without this, every new workspace defaults to FILE_BASED mode; Client B's AUTOMATIC mode intent is never persisted at onboarding time.

```
As a payroll operator onboarding a new workspace via Excel upload,
I want to specify the payroll configuration (PH mode, weekend PH rules,
leave overlap and absence rules) in an optional sheet,
So that the workspace is correctly configured for AUTOMATIC mode
from its very first payroll run without a separate post-onboarding step.
```

**What is wrong today:**
The `workspace_payroll_config` table and its CRUD endpoints exist. But the onboarding commit handler (`onboarding.py`) never reads or writes this table. Every workspace lands in an implicit `FILE_BASED` default. Client B, who will run in AUTOMATIC mode, must manually configure this after onboarding — which is a missed step risk.

**Acceptance Criteria:**

- The onboarding commit handler (`backend/api/routes/onboarding.py`) checks for `workspace_payroll_config` in the payload. If present, it calls `upsert_workspace_payroll_config(workspace_id, config, effective_from=period_start)`.
- If the payload has no `workspace_payroll_config` key, the handler seeds an explicit default row: `ph_mode='FILE_BASED'`, `d3='LEAVE_ABSORBS_PH'`, `d4='ABSENT_IS_DEDUCTIBLE'`. This makes the default explicit and auditable, not implicit.
- `WorkspaceExcelUpload.tsx` — add an optional 7th sheet "Workspace Payroll Config" with columns: `ph_mode`, `saturday_ph_rule`, `sunday_ph_rule`, `d3_leave_overlap_rule`, `d4_absence_rule`.
- Validation: `ph_mode` must be `AUTOMATIC` or `FILE_BASED`. Invalid value surfaces a clear upload error: "ph_mode must be 'AUTOMATIC' or 'FILE_BASED'."
- The existing sub-item from Sprint 8 (WI-11): `WorkspaceConfig.tsx:1657–1658` — change `?? ''` fallback to `?? 'LEAVE_ABSORBS_PH'` and `?? 'ABSENT_IS_DEDUCTIBLE'` for d3/d4 dropdowns. This is a one-line fix bundled here.
- **Dependency:** CB-1 (GAP-2-FIX) must be merged before AUTOMATIC mode is used in production. This story wires the configuration; CB-1 makes AUTOMATIC mode safe.

**Out of scope:** WorkspaceConfig UI overhaul (that is Track J / Gate 6). Building the versioned-row selector in the engine (VERIFY-PH6-VERSIONED-ROW is a separate verification gate).

**Business Risk:** Without this, every workspace onboarded via Excel silently defaults to FILE_BASED mode. A Client B operator running their first run in AUTOMATIC mode will get wrong results because the config was never written. Missed configuration at onboarding is the highest-probability failure mode.

---

## CB-12 — Verify or Remove `PH_ADDITIVE` Engine Path (VERIFY-PH-ADDITIVE)

**Priority:** P1 — a UI option that silently produces wrong results is worse than no option.

```
As a payroll operator choosing a leave-overlap rule in WorkspaceConfig,
I want every visible option to produce correct results,
So that selecting "PH Additive" does not silently fail or use an
unimplemented code path.
```

**What is verified:**
Run: `grep -r "PH_ADDITIVE\|leave_overlap" backend/domain/payroll/`

Two outcomes:
- **Handler found:** Document the expected behaviour, write a targeted test, mark as verified.
- **Handler absent:** Remove `PH_ADDITIVE` from the d3 dropdown in `WorkspaceConfig.tsx`. Default must be `LEAVE_ABSORBS_PH`. Update the `useEffect` fallback in `WorkspaceConfig.tsx` to use `'LEAVE_ABSORBS_PH'` (not empty string) — also covered by CB-11 sub-item.

**Acceptance Criteria:**

- Grep is run and the result is documented in a code comment or a brief note in `docs/stories/`.
- If handler absent: `PH_ADDITIVE` is removed from the d3 dropdown. A workspace that somehow has `d3='PH_ADDITIVE'` stored does not crash the engine (graceful fallback to `LEAVE_ABSORBS_PH` with a warn trace entry).
- If handler present: a test covers the happy path for a leave day that overlaps a PH in AUTOMATIC mode. Test passes.
- No UI option is visible that leads to an unimplemented or broken code path.

**Out of scope:** Implementing PH_ADDITIVE if it is absent — that is a future feature decision.

**Business Risk:** If `PH_ADDITIVE` is selectable in the UI but has no engine handler, any workspace that selects it runs payroll silently wrong. A payroll operator cannot detect this; they will not see an error.

---

## CB-13 — Verify Track F API Routes Are Live (VERIFY-API-COVERAGE)

**Priority:** P1 — prerequisite for the Rate Code Registry UI page (Track G / Gate 5).

```
As a developer completing the Rate Code Registry UI page,
I want to confirm that GET, POST, and DELETE endpoints for
rate_code_registry and public-holidays exist and return correct responses,
So that the frontend implementation does not need to build against
undocumented or missing routes.
```

**What is verified:**
Check that the following routes are live and return expected responses:
- `GET /{wid}/rate-codes` — list platform + workspace rate codes
- `POST /{wid}/rate-codes` — create workspace-scoped rate code
- `DELETE /{wid}/rate-codes/{code}` — delete workspace-scoped code (platform codes: 405 or 403)
- `GET /{wid}/public-holidays` — list national + workspace PHs for a given period
- `POST /{wid}/public-holidays` — add workspace-specific PH
- `DELETE /{wid}/public-holidays/{id}` — remove workspace-specific PH

**Acceptance Criteria:**

- Each endpoint is exercised with a valid request (via `curl` or test client) and returns the correct HTTP status and response shape.
- Any missing route is logged as a new item: created in `docs/stories/` or as a task, not silently missing.
- The Rate Code Registry UI page (UI-NAV-3 / Gate 5 Track G #3) is only scheduled once this verification passes.
- Results of the verification are documented (a brief note in the PR or a comment in the routes file).

**Out of scope:** Building missing routes in this story — those become new stories if found absent.

---

## CB-14 — `payroll_input.quantity ≥ 0` DB Constraint (WI-23 / INP10)

**Priority:** P2 — route-level validation already exists; this is DB-level defence-in-depth.

```
As the system,
I want a DB-level CHECK constraint to enforce non-negative quantities
on payroll_input rows,
So that bulk uploads or direct DB writes that bypass route validation
cannot inject negative quantities that silently corrupt OT or PH calculations.
```

**Acceptance Criteria:**

- Migration: `ALTER TABLE payroll_input ADD CONSTRAINT payroll_input_quantity_non_negative CHECK (quantity >= 0)`. Wrapped in duplicate-constraint guard (`DO $$ BEGIN ... IF NOT EXISTS ... END $$`).
- Attempting to insert a `payroll_input` row with `quantity = -1` via any path raises a DB constraint violation (not a silent success).
- Existing `payroll_input` rows with `quantity >= 0` are unaffected.
- Migration has a working downgrade (`DROP CONSTRAINT IF EXISTS payroll_input_quantity_non_negative`).
- Route-level validation remains unchanged (defence-in-depth — both layers active).

**Out of scope:** Changing how route validation works. Adding constraints to other tables.

---

## Sprint Exit Gate

Client B can run their first payroll in AUTOMATIC mode and meet all of the following:

1. **No runtime crashes** on any statutory deduction path for Client B's employee set
2. **Correct working days** — PH double-subtraction removed; `expected_working_days` matches NGA calendar for the period
3. **Correct PAYE annualization** — CUSTOM period uses ×12, not `365/period_days`
4. **OT inputs return non-zero** — `_resolve_inputs` correctly reads staged input quantities
5. **OT multiplier pipeline wired** — `ot_multiplier` rule type parseable from Excel; rate code registry verified
6. **Workspace payroll config persisted at onboarding** — ph_mode explicitly stored, not implicit
7. **No dead UI option** — PH_ADDITIVE verified or removed from dropdown

## Business Risk Summary (Cost of Not Doing This Sprint)

| Risk | Impact |
|------|--------|
| GAP-2-FIX not landed | Every AUTOMATIC mode run miscounts working days → wrong proration, wrong PAYE annualization, systematic over/under-pay |
| GAP-5-FIX not landed | Client B employees over-pay PAYE by ~8.7% every month → must refund + re-file |
| WI-15 not landed | All OT and PH inputs silently return ₦0 → financial statements look clean but are wrong |
| OT pipeline not wired | Client B cannot process OT hours for any employee → manual workaround required for first run |
| WI-06 not landed | Every workspace onboarded via Excel starts in FILE_BASED mode by mistake → first run in wrong mode |
