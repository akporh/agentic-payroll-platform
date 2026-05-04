# Sprint 13 — Track M (M3–M5 Statutory Completeness) & Track S (Security Hardening)

**Sprint goal:** Introduce a new `percentage_of_sum` calculation method to the rule evaluator — making percentage-of-earnings deductions workspace-configurable without hardcoded handlers — then seed check-off dues, NSITF, and ITF as workspace rules using that method. Also fix the life insurance flat-amount miscalculation and remediate the three low-severity security findings in Track S.

**Arch-council gate — MANDATORY before plan mode:**

M3 covers two data contract surfaces — both must be reviewed in the same arch-council session:

1. **New `calculation_method` value** — `percentage_of_sum` with `rule_definition_json` schema `{rate, base_components: [...], eligibility_field?: string}`. Downstream readers (rule evaluator, retry snapshot, any export that reads rule definitions) must all be audited.
2. **New `employee_contract` column** — `is_union_member BOOLEAN DEFAULT FALSE`. Employee context must be threaded through the rule evaluator so `eligibility_field` can be resolved at evaluation time. This touches the executor → rule evaluator call signature and the retry snapshot (must freeze the employee flag at run time, not re-read live).

M4 and M5 have no data contract risk — no arch-council gate required for either.
Track S items are defect remediations — no arch-council gate.
N1 (rule trace consolidation) remains excluded and requires its own standalone arch-council session.

**Roadmap refs:** Track M (M3–M5), Track S (S1–S3)

---

## Story Index

| Story | Summary | Priority | Effort | Track | Gate |
|-------|---------|----------|--------|-------|------|
| M3 | Add `percentage_of_sum` calculation method to rule evaluator + seed check-off dues workspace rule | P1 | M | M | **Arch-council required** |
| M4 | Life insurance flat ₦2,000 — rate×GROSS_PAY → flat-amount pattern | P2 | XS | M | After M1 ✅ |
| M5 | NSITF/ITF statutory handlers + `component_metadata` seeds + workspace toggle | P2 | S | M | After M1 ✅ |
| S1 | Mask raw exception string in `workspace_payroll_config` warnings response | P2 | XS | S | None |
| S2 | Enum allowlist validation for `workspace_payroll_config` fields before DB upsert | P2 | XS | S | None |
| S3 | Move `import logging` to module level in `payroll.py` | P3 | XS | S | None |

---

## Explicitly Out of Scope (Sprint 13)

| Item | Ref | Reason |
|------|-----|--------|
| N1 — Merge `_rule_trace` into `component_trace_jsonb` | N1 | Requires standalone arch-council session; medium schema-contract risk |
| N2 — Proration factor fix | N2 | BLOCKED — awaiting client Model A/B proration decision |
| O4 — Shift allowance for Client 3 | O4 | Blocked on stable Client 3 workspace identifier for seeding migration |
| O5 — LTA anniversary trigger | O5 | Deferred; M2 unblocked it but arch-council required before implementation |
| Q1–Q3 — Audit observations | Track Q | Deferred to a sprint after N1 lands; Q1 is downstream of rule trace |
| Pre-existing test failures (TF-3 to TF-6) | F1/SR9 | NHF key mismatch in e2e test fixtures — separate investigation track |
| Employer cost export schedule | — | Future sprint; no export story here |
| UI changes for any M or S item | — | Backend + API changes only this sprint |

---

## Pre-Sprint Checklist

Before entering plan mode, confirm the following:

- [x] **Arch-council sign-off obtained for M3** — verdict: CONCUR WITH ADDITIONS (2026-05-04). Six binding decisions D1–D6 recorded. Two story doc corrections C1 (not_applied trace entry) and C2 (BASIC_MONTHLY→BASIC) applied. Implementation may begin.
- [x] M3: Check-off dues applies to **union members only** — per-employee flag (`is_union_member BOOLEAN` on `employee_contract`). The `percentage_of_sum` method will support an optional `eligibility_field` key in `rule_definition_json`; when present, the rule evaluator gates the calculation on the named employee context field. *(Confirmed 2026-05-04)*
- [x] M3: Rate is per-workspace via `payroll_rule.definition_json` — supported by default with `percentage_of_sum`. *(Confirmed 2026-05-04)*
- [x] M4: ₦2,000 flat amount is **Client B only** — `flat_amount` must live in `client_component_metadata` for Client B's workspace, not the platform seed row. Platform seed retains the legacy `rate`-based `rules_jsonb` as the default for all other workspaces. *(Confirmed 2026-05-04)*
- [x] M5: ITF threshold (≥5 employees, annual payroll ≥₦50M) is **platform-enforced**, toggled at workspace level. Implementation note: platform currently does not store workspace headcount or annual payroll total — plan mode must resolve where this data lives (new fields on workspace, or derived at run time from employee count + run total). *(Confirmed 2026-05-04)*
- [x] S1–S3: No client confirmation needed — these are internal security remediations.

---

## M3 — `percentage_of_sum` Calculation Method + Check-Off Dues Workspace Rule (NEW-GAP6)

**Priority:** P1 — Union contractual obligation and engine extensibility. For Client B's unionised workforce, failure to deduct check-off dues creates a breach of the collective bargaining agreement. More broadly: without a `percentage_of_sum` method, every new percentage-of-earnings deduction (NSITF, ITF, future items) requires a new hardcoded engine handler — making the platform increasingly rigid.

**Prerequisite:** M1 (`component_class` enum extension) merged in Sprint 12 ✅.

**Arch-council required — do not implement before sign-off.** This story introduces a new `calculation_method` value and a new `rule_definition_json` schema shape. Both are data contracts with downstream readers.

```
As a payroll operator configuring a workspace,
I want to define percentage-of-earnings deductions as workspace payroll rules
specifying a rate and a list of base salary components,
So that statutory and contractual deductions like check-off dues, NSITF, and ITF
are calculated automatically from a rule — without requiring a platform code change
for each new deduction type.
```

**What is wrong today:**
The rule evaluator supports four `calculation_method` values (`unit_multiplier`, `daily_rate_deduction`, `fixed_amount`, `ot_multiplier`). None of them supports "rate × sum of named salary components." As a result, check-off dues, NSITF, and ITF cannot be expressed as workspace rules — they either require manual `payroll_input` entries each month or a new hardcoded engine handler per deduction type. Both paths are brittle and do not scale.

**Acceptance Criteria:**

**Engine — `percentage_of_sum` method (arch-council gated):**
- A new `calculation_method` value `'percentage_of_sum'` is implemented in `rule_evaluator.py`.
- `rule_definition_json` schema for this method:
  `{"rate": <decimal>, "base_components": ["COMPONENT_A", ...], "eligibility_field": "<key>"}` — `eligibility_field` is optional.
- At evaluation time, if `eligibility_field` is present, the handler reads that key from the per-employee context dict. If the value is falsy (`False`, `None`, `0`), the handler returns `Decimal('0.00')` and writes a `"status": "not_applied"` trace entry recording the eligibility field and its resolved value — the rule did not fire but the evaluation is auditable. *(C1 — arch-council correction: a missing trace entry cannot answer a union challenge against non-deduction; the not_applied entry is mandatory.)*
- If `eligibility_field` is absent, the rule applies to all employees — no gate.
- The handler resolves each name in `base_components` against the already-computed salary components dict. Components not found are treated as `Decimal('0')` — not an error.
- Computed value: `Decimal(str(rate)) × sum(resolved_base_components)`.
- Result written to `component_trace_jsonb` with: computed amount, rate, base component names, resolved value of each, and the `eligibility_field` key that was checked (if applicable).
- On retry, `rate`, `base_components`, and `eligibility_field` are read from the frozen rule snapshot. The employee eligibility flag value is read from the frozen employee snapshot — not the live `employee_contract` table.
- `calculation_method='percentage_of_sum'` is added to the CHECK constraint governing allowed method values. Migration includes idempotency guard.
- The method is generic — `base_components` can contain any combination of salary component names; `eligibility_field` can reference any boolean employee context key.

**`is_union_member` migration (arch-council gated):**
- A migration adds `is_union_member BOOLEAN NOT NULL DEFAULT FALSE` to `employee_contract`.
- `ADD COLUMN` wrapped in `DO $$ BEGIN … EXCEPTION WHEN duplicate_column THEN NULL; END $$`.
- Downgrade removes the column only if no rows have `is_union_member = TRUE` (check count; raise if > 0).
- The onboarding Excel parser and employee PATCH endpoint accept and persist `is_union_member`.

**Employee context threading (arch-council gated):**
- The executor passes a per-employee context dict to `apply_payroll_rules()` that includes `is_union_member` (and any future eligibility fields) sourced from `employee_contract`.
- On retry the employee flag is read from the frozen run snapshot — a contract change between runs does not alter a retry result.
- Arch-council to confirm the cleanest threading point in the executor → rule evaluator call chain.

**Check-off dues workspace rule seed (follows engine):**
- A `component_metadata` platform row seeded for `CHECK_OFF_DUES`: `component_class='statutory_deduction'`, canonical order after PAYE and Pension.
- A seed migration creates a `payroll_rule` row for the applicable workspace:
  `{"calculation_method": "percentage_of_sum", "rate": 0.02, "base_components": ["BASIC", "HOUSING", "TRANSPORT"], "eligibility_field": "is_union_member"}` *(C2 — arch-council correction: BASIC_MONTHLY does not exist as a component code; BASIC is the canonical code used throughout migrations and salary derivation.)*
- Workspace-specific and opt-in. `component_class='statutory_deduction'` reduces `NET_PAY`; does NOT enter `TAXABLE_INCOME`.

**Edge Cases:**
- `eligibility_field` present, `is_union_member=False`: return ₦0, write `"status": "not_applied"` trace entry — rule did not fire but evaluation is auditable.
- `eligibility_field` present, `is_union_member=True`: compute and trace normally.
- `base_components` list is empty: return ₦0, write trace entry, log `WARNING` — misconfiguration.
- All resolved base components are ₦0 (new-joiner): return ₦0, write trace entry — valid.
- `rate` missing from `rule_definition_json`: raise `ValueError` naming the rule — misconfiguration.
- Component name in `base_components` not found in salary dict: treat as ₦0 — not an error.

**Confirmed decisions:**
- Check-off dues applies per `is_union_member` flag on `employee_contract` — not all employees.
- `eligibility_field` is generic: any future boolean employee context key can be used, not just union membership.

**Open Questions (arch-council items):**
- Where is the canonical validation point for `calculation_method` — DB CHECK constraint, Python-level enum in domain layer, or both?
- Should `base_components` entries be validated at rule-creation time (fail-fast) or resolved lazily at evaluation time?
- Where is the cleanest point to freeze the employee eligibility flag into the retry snapshot — at run-claim time, result-write time, or as part of the per-employee execution context?

**Out of Scope:**
- Check-off dues remittance export schedule. Future sprint.
- UI to create or edit `percentage_of_sum` rules. The new method becomes an option in the existing rule management interface.
- Enforcement of union membership validity — the flag is set by the operator via onboarding or PATCH; the platform trusts it.

**Business Risk:**
- **Cost of NOT doing this:** Every new percentage-of-earnings deduction requires a platform code deployment. Three are pending now (check-off dues, NSITF, ITF); more will follow. The platform remains brittle and operator-dependent for each one.
- **Cost of doing it wrong (engine):** If `base_components` resolution is incorrect (wrong component names, wrong dict keys), deductions silently compute to ₦0 or wrong amounts across all employees for all future runs. The trace entry must record resolved values so this is detectable without re-running. Explicit numeric assertions in the test suite are mandatory.
- **Cost of doing it wrong (data contract):** If the `rule_definition_json` schema is introduced without auditing the retry snapshot reader and any export that reads rule definitions, those callers will encounter unexpected key shapes at runtime. Arch-council must identify all downstream readers before implementation begins.

---

## M4 — Life Insurance Flat ₦2,000 (GAP-10-FIX)

**Priority:** P2 — Financial accuracy fix. The current rate-based formula happens to produce ₦2,000 for employees at the exact gross pay where `rate × GROSS_PAY = 2000`, but diverges for every other salary level — producing over- or under-deductions that will not reconcile with the insurer's premium schedule.

**Prerequisite:** M1 (`component_class` enum extension) merged in Sprint 12 ✅.

```
As a payroll operator,
I want life insurance deducted as a flat ₦2,000 per employee per period
regardless of their salary level,
So that every employee's deduction exactly matches the policy premium
and the platform reconciles cleanly with the insurance provider's statement.
```

**What is wrong today:**
The life insurance handler computes `rate × GROSS_PAY`. For a ₦500,000 gross-pay employee at a 0.4% seed rate, this equals ₦2,000 and appears correct. But the policy contract specifies a flat premium — not a percentage. For any employee with gross pay above ₦500,000, the current handler over-deducts. For employees below ₦500,000, it under-deducts. The discrepancy accumulates silently.

**Acceptance Criteria:**

- The life insurance handler is updated to read a `flat_amount` key from `rules_jsonb` when present. If `flat_amount` is present, it is used as-is: `LIFE_INSURANCE = Decimal(str(flat_amount))`.
- Backward-compat fallback: if `rules_jsonb` does not contain `flat_amount` but contains a `rate` key, the handler falls back to `rate × GROSS_PAY`, logs a `DEPRECATION` warning at `WARNING` level, and continues. This prevents breaking workspaces that have not been migrated.
- The **platform `component_metadata` seed row for `LIFE_INSURANCE` is unchanged** — it retains the legacy `rate`-based `rules_jsonb` as the default for all workspaces.
- A migration adds a `client_component_metadata` override row for **Client B's workspace only**: `rules_jsonb = {"flat_amount": 2000}`. This override takes precedence over the platform seed via the existing override resolution order. Migration is idempotent — safe to re-run.
- `component_trace_jsonb` records the deduction amount and source path: `"source": "flat_amount"` or `"source": "rate_fallback"` — audit trail shows which path fired.
- The migration downgrade removes the Client B override row (does not touch the platform seed).

**Confirmed decisions:**
- ₦2,000 flat amount is **Client B only**. Platform seed remains rate-based. Other workspaces continue to use `rate × GROSS_PAY` via the fallback path until they explicitly opt into flat-amount via their own `client_component_metadata` override. *(Confirmed 2026-05-04)*

**Edge Cases:**
- `flat_amount = 0` in `rules_jsonb`: valid — deduction is ₦0. Write to trace with `flat_amount` source.
- `rules_jsonb` is null or empty: handler raises `ValueError` naming the component — misconfiguration.
- Client B override present with `flat_amount`: takes precedence over platform seed rate — correct.
- Any workspace without an override: falls back to `rate × GROSS_PAY` from platform seed — logs `DEPRECATION` warning.

**Out of Scope:**
- Removing the rate-based fallback path in this sprint. Leave it in place — audit which workspaces still use a `rate`-based seed before removal.
- UI changes.

**Business Risk:**
- **Cost of NOT doing this:** Incorrect deductions per employee each period. For high earners (e.g. ₦1M gross), over-deduction is ₦4,000/month above the policy premium — eroding employee net pay and creating insurer reconciliation failures.
- **Cost of doing it wrong:** If the fallback path is removed prematurely, existing workspaces that were never migrated silently deduct ₦0 (no `flat_amount` key, no fallback). The backward-compat fallback is non-negotiable until all workspaces are confirmed.

---

## M5 — NSITF / ITF Statutory Handlers (NEW-GAP7)

**Priority:** P2 — Statutory employer obligation. NSITF (Nigeria Social Insurance Trust Fund) and ITF (Industrial Training Fund) are employer-side contributions fixed by law at 1% each. They are not deducted from employee pay but must be calculated, tracked, and remitted by the employer. Their absence from the payroll record means finance cannot reconcile total employment cost from the platform alone.

**Prerequisite:** M1 (`employer_cost` component class, Sprint 12 ✅). Independent of M3 — no arch-council gate required. M5 follows the same statutory handler pattern as NHF and Health Insurance.

```
As a payroll operator,
I want to toggle NSITF and ITF employer contributions on or off for my workspace,
So that when enabled they are automatically calculated at the statutory rate
(1% of BASIC + HOUSING + TRANSPORT) and appear in the payroll audit record —
without affecting employee take-home pay.
```

**What is wrong today:**
No NSITF or ITF handlers exist in the platform. Employer contributions must be calculated manually in a spreadsheet after each payroll run, making the payroll record structurally incomplete and cost reporting non-auditable from the platform alone.

**Why statutory handler pattern (not payroll rule):**
NSITF and ITF are statutory obligations with rates fixed by law — an operator should not be able to set or change the rate, only toggle the component on or off for their workspace. This is identical to how NHF (2.5%, fixed), Health Insurance, and Development Levy work. The `client_component_metadata` toggle pattern is the correct model. Using a workspace payroll rule would permit operators to edit the statutory rate, which is incorrect.

**Acceptance Criteria:**

- Two handlers are added to the sequential executor following the NHF/Health Insurance pattern: `_handle_nsitf_employer()` and `_handle_itf_employer()`.
- Formula for each: `Decimal('0.01') × (BASIC_MONTHLY + HOUSING + TRANSPORT)`. Components absent from the salary dict are treated as `Decimal('0')` — not an error.
- `component_metadata` platform rows are seeded for `NSITF_EMPLOYER_COST` and `ITF_EMPLOYER_COST`:
  - `component_class='employer_cost'` for both.
  - Rate stored in `rules_jsonb` (e.g. `{"rate": "0.01"}`), read by the handler — not hardcoded in Python.
  - Canonical order: after all employee deductions (last in the execution chain).
- Workspaces toggle each component via `client_component_metadata.is_active`. A workspace without the entry, or with `is_active=false`, receives no calculation and no trace entry — identical to how NHF opt-out works today.
- `component_class='employer_cost'` is enforced by the executor:
  - Does NOT reduce employee `NET_PAY`.
  - Does NOT enter `TAXABLE_INCOME`.
  - IS written to `component_trace_jsonb` with computed amount, rate, and resolved base values.
  - Is NOT included in the net pay bank export.
  - Is NOT included in the PAYE remittance export.
- On retry: handlers re-derive from the frozen salary snapshot and frozen `component_metadata` rate — not live tables.
- Computed amount of `Decimal('0.00')` is valid (e.g. new-joiner with no salary components yet). Write trace entry — do not skip silently.

**Edge Cases:**
- Only NSITF or only ITF enabled for a workspace: each handler is independently gated by its own `client_component_metadata` row.
- One or more base salary components absent for an employee: treat as ₦0 — partial base is valid.
- `rules_jsonb` rate missing from `component_metadata` row: handler raises `ValueError` naming the component — misconfiguration, not a runtime edge case.

**Confirmed decisions:**
- ITF threshold (≥5 employees, annual payroll ≥₦50M) is **platform-enforced**, toggled at workspace level. *(Confirmed 2026-05-04)*
- Implementation note: the platform does not currently store workspace headcount or cumulative annual payroll total. Plan mode must resolve this — two viable approaches:
  1. **Derive at run time**: `employee_count` = live count of active employees in the workspace; `annual_payroll_ytd` = sum of `payroll_run.total_net_pay` for the workspace year-to-date. No new stored fields — computed on each run before the handler fires.
  2. **Store on workspace**: add `employee_threshold_met BOOLEAN` and `annual_payroll_ytd DECIMAL` as workspace-level fields updated at run approval. Requires a migration. More reliable but more moving parts.
- Arch-council is NOT required for M5 (no new data contract). The threshold enforcement approach is a plan-mode decision.

**Out of Scope:**
- Employer cost export schedule or download endpoint. Future sprint.
- Payslip lines for employer costs — employer obligations are not shown on employee payslips.
- Any UI beyond the existing component toggle mechanism.

**Business Risk:**
- **Cost of NOT doing this:** Finance cannot close month-end cost reporting from the platform record alone. Manual spreadsheet creates reconciliation errors and an incomplete audit trail.
- **Cost of doing it wrong:** If the `employer_cost` class check is absent or bypassed, employer costs flow into `NET_PAY` — employees receive inflated salaries silently. The test suite must assert `NET_PAY` is unchanged before and after enabling NSITF/ITF components.

---

## S1 — Mask Raw Exception String in `workspace_payroll_config` Warnings Response (SEC-S1)

**Priority:** P2 (Medium severity finding from Sprint 10 `/security` review).

**Location:** `backend/api/routes/onboarding.py:589`

```
As an operator using the workspace payroll configuration endpoint,
I want informative but safe error messages when config validation fails,
So that I can diagnose the problem without the API exposing internal
exception details to the caller.
```

**What is wrong today:**
When `workspace_payroll_config` validation raises an exception, the raw exception string (`_wpc_err!s`) is placed directly into the API `warnings` response field. This exposes internal stack trace fragments, module names, and implementation detail to the API consumer — a security anti-pattern that aids an attacker mapping the system.

**Acceptance Criteria:**

- The `warnings` field in the response for the `workspace_payroll_config` endpoint never contains a raw Python exception message or stack trace.
- On validation failure, a human-readable, non-implementation-specific message is returned: e.g. `"Workspace payroll configuration could not be applied. Check the submitted values and try again."`.
- The original exception is logged internally at `ERROR` level with the full message and traceback, so the operator team can diagnose without relying on the API response.
- The HTTP status code behaviour (200 with warnings vs 422) is unchanged — this is a response body change only.
- A unit test asserts that when the config handler raises, the response `warnings` field does not contain the exception class name or message text.

**Out of Scope:**
- Changing the HTTP status code for config validation failures.
- Adding a structured error code scheme (future hardening sprint).

**Business Risk:**
- **Cost of NOT doing this:** Internal module and exception names are exposed in API responses — aids an attacker enumerating the platform's internal structure. Medium severity.
- **Cost of doing it wrong:** If the replacement message is too vague and the log is not written, operators lose the ability to diagnose real config errors.

---

## S2 — Enum Allowlist Validation for `workspace_payroll_config` Fields (SEC-S2)

**Priority:** P2 (Low severity finding from Sprint 10 `/security` review).

**Location:** `backend/api/routes/onboarding.py:575–586`

```
As a platform developer,
I want enum fields in the workspace payroll config endpoint validated against
an explicit allowlist before they are written to the database,
So that invalid or unexpected values are rejected at the application layer
and cannot reach the DB constraint.
```

**What is wrong today:**
The `workspace_payroll_config` upsert route passes enum fields (e.g. `ph_mode`, `saturday_ph_rule`, `sunday_ph_rule`, D3/D4 flags) directly to the DB upsert without application-layer validation. The DB check constraint is the only guard. While the constraint prevents persistence of invalid values, it produces a raw PostgreSQL `CheckViolation` exception that (before S1 is fixed) leaks into the API response. Defence in depth requires application-level validation before the DB call.

**Acceptance Criteria:**

- An explicit allowlist is defined for each enum field accepted by the `workspace_payroll_config` endpoint. Allowlists are defined as module-level constants (not inline magic strings).
- Before the DB upsert call, each enum field in the request body is validated against its allowlist. An invalid value returns HTTP 422 with a structured error body naming the field and the accepted values.
- Valid values pass through to the DB upsert unchanged — no logic change.
- The allowlists are consistent with the DB check constraint values (single source of truth; document the dependency).
- A unit test for each enum field: valid value → 200; invalid value → 422 with field name in response.

**Out of Scope:**
- Changing the DB check constraints to match the allowlists (they should already match — verify only).
- Adding allowlist validation to other endpoints in this sprint. Focus is the `workspace_payroll_config` endpoint only.

**Business Risk:**
- **Cost of NOT doing this:** The DB is the only validation layer — any PostgreSQL constraint change (even in a migration) silently widens or narrows what the API accepts. Defence in depth is missing.
- **Cost of doing it wrong:** If the allowlist is narrower than the DB constraint, valid values are rejected. Allowlists must be kept in sync with migrations.

---

## S3 — Move `import logging` to Module Level in `payroll.py` (SEC-S3)

**Priority:** P3 (Low severity / code quality finding from Sprint 10 `/security` review).

**Location:** `backend/api/routes/payroll.py:498`

```
As a developer maintaining the payroll route,
I want the logging import at module level following Python conventions,
So that the logger is consistent across all call sites and import-time
side effects are predictable.
```

**What is wrong today:**
`import logging` and `_logging.getLogger(...)` appear inline inside a function body in `payroll.py`. This is a Python anti-pattern: the import succeeds every call (Python caches it, so performance is not the issue), but the inline logger is not reachable from tests or from other functions in the module. Any log message from that function is emitted from a logger instance that cannot be easily configured or captured in test assertions.

**Acceptance Criteria:**

- `import logging` is moved to the module-level import block in `payroll.py`.
- The inline `_logging.getLogger(...)` call is replaced with a module-level `logger = logging.getLogger(__name__)`.
- All logging calls in the affected function use `logger` (not `_logging`).
- No behaviour change — this is a refactor only.
- The module imports cleanly and existing tests pass.

**Out of Scope:**
- Changing log levels or log message content.
- Refactoring logging across other files.

**Business Risk:**
- Low. This is a code quality fix with no runtime behaviour change. Risk of doing it wrong: introducing a naming collision with an existing `logger` import. Check for existing `logger` variable before renaming.

---

## Dependency Map

```
Arch-council (M3 only — percentage_of_sum data contract)
        │
        ▼
M1 (Sprint 12 ✅) ──► M3 (percentage_of_sum engine + check-off dues payroll rule seed)
                  │
                  ├──► M4 (life insurance flat — independent of M3)
                  │
                  └──► M5 (NSITF/ITF statutory handlers — independent of M3,
                            follows NHF/Health Insurance pattern,
                            no arch-council gate)

S1, S2, S3 are independent of all M items and of each other — run in parallel.

N1 (rule trace) ── NOT in this sprint ── requires standalone arch-council session
N2 (proration fix) ── BLOCKED ── awaiting client Model A/B decision
                                  (MODEL_A default confirmed; system will be configurable)
```

---

## Definition of Done (Sprint 13)

**Track M:**
- [ ] **Arch-council sign-off documented** for M3 — covering: (1) `percentage_of_sum` method + `eligibility_field` schema, (2) `is_union_member` migration on `employee_contract`, (3) employee context threading through rule evaluator + retry snapshot
- [ ] M3: `percentage_of_sum` handler in `rule_evaluator.py`; `eligibility_field` gates per-employee; `base_components` resolved against salary dict; missing components treated as ₦0; `calculation_method` CHECK constraint updated; migration idempotent
- [ ] M3: `is_union_member BOOLEAN DEFAULT FALSE` migration on `employee_contract`; onboarding parser + employee PATCH accept the field
- [ ] M3: Employee context dict threads `is_union_member` into `apply_payroll_rules()`; flag frozen in retry snapshot
- [ ] M3: `CHECK_OFF_DUES` `component_metadata` row seeded; workspace `payroll_rule` row seeded with `eligibility_field: "is_union_member"`; opt-in per workspace
- [ ] M3: Trace entry includes computed amount, rate, base component names, resolved values, and eligibility field checked
- [ ] M4: Life insurance handler reads `flat_amount` from `rules_jsonb`; backward-compat fallback to `rate × GROSS_PAY` preserved with `DEPRECATION` log; trace records `source` field
- [ ] M4: `client_component_metadata` override row for Client B seeded with `flat_amount=2000`; platform `component_metadata` seed unchanged; migration idempotent
- [ ] M5: `_handle_nsitf_employer()` and `_handle_itf_employer()` handlers implemented in sequential executor following NHF pattern; rate read from `component_metadata.rules_jsonb`
- [ ] M5: `NSITF_EMPLOYER_COST` and `ITF_EMPLOYER_COST` `component_metadata` seed rows added; `employer_cost` class; workspace toggle via `client_component_metadata`
- [ ] M5: `employer_cost` class verified to exclude from NET_PAY, TAXABLE_INCOME, and all exports; trace entry records computed amount + base values
- [ ] M5: Pre-sprint checklist item confirmed (ITF threshold handling)

**Track S:**
- [ ] S1: Raw exception string removed from `warnings` response; exception logged at ERROR level internally; unit test asserts exception class/message text absent from response body
- [ ] S2: Enum allowlists defined as module-level constants; 422 returned for invalid values with field name in response; unit tests cover each enum field
- [ ] S3: `import logging` moved to module level; `logger = logging.getLogger(__name__)` at module level; no behaviour change; existing tests pass

**Cross-cutting:**
- [ ] `/tester` verification:
  - M3: numeric assertion — `percentage_of_sum` with known rate + base produces correct amount; employee with `is_union_member=False` receives ₦0 and no trace entry; employee with `is_union_member=True` receives correct deduction; non-opted-in workspace receives no deduction
  - M4: Client B workspace deducts flat ₦2,000 regardless of gross pay level; non-Client-B workspace falls back to `rate × GROSS_PAY` and logs DEPRECATION; trace records correct `source` field for each path
  - M5: employer cost components appear in trace with computed amount and base values; `NET_PAY` identical before and after enabling NSITF/ITF; workspace with toggle off receives no calculation and no trace entry
  - S1–S3: no regression on existing payroll and onboarding routes
- [ ] `/security` review on changed files (new `percentage_of_sum` method + S1–S3 route changes)
- [ ] `/auditor` review on trace schema additions (M3 `percentage_of_sum` trace format; M5 employer cost entries)
- [ ] All migrations include matching downgrade and idempotency guards
- [ ] `/retro` run at sprint close
