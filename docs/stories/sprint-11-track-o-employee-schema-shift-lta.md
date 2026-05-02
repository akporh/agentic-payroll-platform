# Sprint 11 — Track O: Employee Schema & Complex Features

**Sprint goal:** Land the employee payroll-critical fields (shift type, tax jurisdiction, skill level), grade percentage salary structure, and the shift allowance handler — enabling Client B's full shift-based OT routing and unblocking the LTA anniversary trigger.

**Entry gate:** Tracks K, L, M, and N must be complete before Sprint 11 begins. Confirm status before planning session.

**Arch-council gate (MANDATORY — one session per item group):**
- O1: Joint arch-council for NEW-GAP4 + NEW-GAP13. Must settle: (a) which table the fields land on — `employee` vs `employee_contract` — and (b) whether `employee_contract.start_date` already serves as `date_engaged`.
- O2: Standalone arch-council for NEW-GAP12. Changes how `salary_components` dict is populated at run time — every handler that reads BASIC is downstream.
- O3: Standalone arch-council for WI-04 Sub-B. Blocked on O1 (shift_type must exist); arch-council after O1 merges.
- O5: Standalone arch-council for NEW-GAP11. New cross-cutting service that auto-injects payroll inputs — idempotency on retry must be explicitly designed before any code.
- O6: **Full dedicated PM + arch-council sprint required.** Do NOT include in Sprint 11 scope. Placeholder story included for reference only.

**Roadmap refs:** Track O (O1–O6)

---

## Story Index

| Story | Summary | Priority | Effort | Track | Status |
|-------|---------|----------|--------|-------|--------|
| O1 | Employee payroll-critical fields — shift_type, state_of_tax, skill_level (+ date_engaged pre-check) | P1 | M | O | ✅ Sprint 11 |
| O2 | Grade percentage salary structure — total_monthly + pct fields | P1 | M | O | ✅ Sprint 11 |
| O3 | D9 shift gate — ot_multiplier basic_daily returns ₦0 for DAY/NULL shift_type; full SHIFT_ALLOWANCE handler deferred | P1 | M | O | ✅ (gate) / ⬜ (handler) Sprint 12 |
| O4 | Client 3 shift allowance — SHIFT2/SHIFT3/SHIFT4 with basic_daily rate base | P2 | S | O / Track E | ⬜ Deferred — needs Client 3 workspace ID |
| O5 | LTA anniversary trigger — auto-inject paye_only input at anniversary date | P2 | L | O | ⬜ Deferred Sprint 12 — blocked on M2 |
| O6 | Timesheet / Attendance Layer | — | — | O | ⬜ BLOCKED — dedicated sprint required |

---

## Explicitly Out of Scope (Sprint 11)

| Item | Ref | Reason |
|------|-----|--------|
| Timesheet / Attendance Layer (O6) | NEW-GAP1 | Requires full dedicated PM + arch-council sprint; blocked on Tracks K–N complete |
| NSITF/ITF employer cost handlers | M5 | Sprint 12 (Track M) |
| Non-taxable component class | M1 | Sprint 12 (Track M) |
| PAYE-only additions path | M2 | Sprint 12 (Track M) — O5 may need to be re-sequenced if M2 slips |
| Proration factor fix (WI-03) | N2 | BLOCKED — client Model A/B decision not yet made |
| PAYE jurisdiction routing via state_of_tax | O1 extension | O1 adds the column; routing logic follows in a later sprint after arch-council confirms the statutory rule selection contract change |

---

## Pre-Sprint Checklist

Before entering plan mode, confirm the following with the user:

- [ ] Tracks K, L, M, and N are all complete (entry gate met)
- [ ] Arch-council session for O1 (joint NEW-GAP4/13) is scheduled
- [ ] Arch-council session for O2 (NEW-GAP12) is scheduled
- [ ] Client confirms: which employees are on `2_SHIFT` vs `4_SHIFT` vs `DAY` — is this in the existing onboarding Excel or a new column needed in the upload template?
- [ ] Client confirms: is `employee_contract.start_date` the same as `date_engaged` for LTA purposes, or is there a distinct "hire date" that differs from "contract start date" (e.g. for employees who changed contract terms)?
- [ ] Client confirms: is `state_of_tax` already carried in any existing `personal_details_encrypted` JSONB on the employee table — if so, extract it rather than adding a duplicate column
- [ ] Client confirms: LTA amount — is it a fixed amount per workspace, per grade, or per employee? Determines where the config lives.
- [ ] O5 dependency on M2 (paye_only path): if Track M slips to Sprint 12, O5 cannot ship. Confirm sequencing.

---

## O1 — Employee Payroll-Critical Fields: shift_type, state_of_tax, skill_level (NEW-GAP4 + NEW-GAP13)

**Priority:** P1 — `shift_type` directly gates OT2 routing and the shift allowance handler (O3). Without it, Client B employees on 2-shift or 4-shift schedules receive wrong OT calculations.

**Arch-council required (joint session for all O1 fields) — do not implement before sign-off.**

```
As a payroll operator onboarding a workforce with different shift patterns,
I want each employee to have their shift type, tax jurisdiction, and skill
level recorded in the system,
So that the payroll engine routes overtime, PAYE, and allowances correctly
for each employee without manual overrides at run time.
```

**Pre-investigation required before arch-council (do not write code — read and report):**

Before the arch-council session, answer the following questions by reading the live schema:

1. **`date_engaged` vs `start_date`:** `employee_contract.start_date` already exists (`migrations/versions/7685c65f5d2_add_grade_and_employee_contract_tables.py:43`). Confirm whether new-hire proration (`payroll_run_service.py`) reads this field for its start-date calculation. If it does, `date_engaged` = `start_date` and no new column is needed — O5 (LTA) should read `employee_contract.start_date` directly.

2. **`state_of_tax` location:** Check `employee.personal_details_encrypted` JSONB (referenced in `migrations/versions/6c2ecc683076_add_employee_number_and_status_fields.py`) for any existing jurisdiction or state field. If it's already there, adding a duplicate column creates a sync problem.

3. **`shift_type` table placement:** Client noted `shift_type` should be on `employee_contract`, not `employee` — an employee could change shift pattern without a new contract entity. Arch-council must decide: `employee` (one value, simpler) vs `employee_contract` (follows the contract versioning model, more correct for history).

4. **`skill_level` table placement:** Client noted it "should be able to map to employee contract". Confirm whether this is an FK to a `skill_level` reference table or a free-text column.

**Acceptance Criteria (after arch-council confirms all above):**

- A single atomic migration adds the confirmed new columns. Migration is never split — all new employee fields land together.
- Every `ADD COLUMN` is wrapped in `DO $$ BEGIN ... EXCEPTION WHEN duplicate_column THEN NULL; END $$`.
- All new columns are nullable. Existing employees default to `NULL`. Engine behaviour for `NULL shift_type` is: treat as `'DAY'` shift (default). Document this invariant in code.
- `shift_type` allowed values: `'DAY'`, `'2_SHIFT'`, `'4_SHIFT'`. A `CHECK` constraint enforces this. NULL is allowed (= default DAY).
- In `rule_evaluator.py:classify_day()`, after the migration, `shift_type` is read from the employee execution context (threaded through from the employee query at run preparation) rather than a workspace-level default.
- OT2 eligibility: only `DAY` shift (or NULL) employees qualify for OT2 under the current rule. `2_SHIFT` and `4_SHIFT` employees route to the appropriate OT handler — arch-council to confirm the routing table.
- The onboarding Excel parser accepts a `shift_type` column in the employee sheet. Invalid values fail validation with a clear error (e.g. `"shift_type 'NIGHT' is not valid — allowed values: DAY, 2_SHIFT, 4_SHIFT"`).
- `GET /workspaces/{id}/employees` response includes `shift_type`, `state_of_tax`, and `skill_level` fields. NULL is returned as `null` in JSON — not omitted.
- A `PATCH /workspaces/{wid}/employees/{eid}/contract` endpoint (or the existing update endpoint at `workspace.py:311`) supports patching the new fields post-onboarding. Input validation enforces the `shift_type` allowlist.
- Downgrade removes only the newly added columns. Pre-check in downgrade body: if any non-NULL values exist in the columns being dropped, log a warning (do not silently discard data, but do not block the downgrade).

**Open Questions (for arch-council):**
- Does `state_of_tax` change which `statutory_rule` row is selected at `payroll.py:154–162`? If yes, this is a data contract change to the statutory rule selection algorithm and must be explicitly designed.
- Should `skill_level` be a FK to a `skill_level` lookup table (future-proofing) or a free-text VARCHAR? Client said "should be able to map to employee contract" — clarify.
- If `shift_type` goes on `employee_contract` (versioned), how does the executor query it? It needs the contract that is active for the run's period, not the latest contract.

**Out of Scope:**
- Full PAYE jurisdiction routing via `state_of_tax`. This sprint adds the column and the data. Routing logic requires its own arch-council session (different statutory rule selection contract).
- UI for editing shift_type in the WorkspaceConfig employee list. Backend + onboarding parser only this sprint.

**Business Risk:**
- Cost of NOT doing this: OT routing is wrong for all Client B shift workers; shift allowance cannot be implemented; LTA trigger cannot be built.
- Cost of doing it wrong: if `shift_type` defaults to the wrong value, employees receive incorrect OT pay silently. NULL-as-DAY invariant must be tested with an explicit assertion.

---

## O2 — Grade Percentage Salary Structure (NEW-GAP12)

**Priority:** P1 — Client B uses total-monthly-with-percentage-split salary structures rather than absolute component amounts. Without this, their grade structure cannot be represented in the system.

**Arch-council required (standalone session) — do not implement before sign-off.**

```
As a payroll operator for a client whose salary grades are defined as a
total monthly amount split by percentage across components,
I want to configure grades with total_monthly and component percentages,
So that the payroll engine derives the correct BASIC, HOUSING, TRANSPORT,
and UTILITY values without me manually computing and entering absolute amounts.
```

**What is wrong today:**
`salary_definition.components_jsonb` stores absolute amounts per component. For clients who define salary as `total_monthly × basic_pct + total_monthly × housing_pct` etc., the operator must pre-compute absolute amounts externally, which introduces rounding errors and makes salary band changes expensive.

**Acceptance Criteria:**

- A migration adds `total_monthly DECIMAL(15,2) NULL`, `basic_pct DECIMAL(5,4) NULL`, `housing_pct DECIMAL(5,4) NULL`, `transport_pct DECIMAL(5,4) NULL`, `utility_pct DECIMAL(5,4) NULL` to the `grade` table. All nullable.
- Every `ADD COLUMN` wrapped in duplicate-column guard.
- A `CHECK` constraint enforces: if any pct column is non-null, all four pct columns must be non-null and must sum to exactly 1.0000 (±0.0001 tolerance for floating-point input rounding). Document the tolerance value.
- At run time, the salary derivation service checks whether the employee's current grade has `total_monthly` set. If yes: derive component amounts as `total_monthly × pct`, rounded to 2 decimal places (Decimal arithmetic, not float). If no: fall back to `salary_definition.components_jsonb` absolute amounts (existing path, unchanged).
- The two models are mutually exclusive per employee-grade assignment. An employee whose grade uses the percentage model does not also read `components_jsonb` components for the same component names. Document this invariant; add an assertion in the derivation service.
- `component_trace_jsonb` records `"salary_basis": "grade_percentage"` or `"salary_basis": "salary_definition_absolute"` so an auditor knows which path was used.
- Onboarding Excel parser: the grade sheet accepts `total_monthly`, `basic_pct`, `housing_pct`, `transport_pct`, `utility_pct` columns. If any pct column is present, all must be present — partial presence is a validation error.
- Existing grades with no pct columns are unaffected — backward compatibility preserved.
- Downgrade removes the five added columns only if all are NULL across all rows. If any workspace has live percentage-model grades, the downgrade must fail with a clear error rather than destroying data.

**Open Questions (for arch-council):**
- Rounding rule: who owns the rounding? Round each derived component independently, or round all and adjust the last to ensure the sum equals `total_monthly` exactly? (The "adjust last component" approach avoids ₦1–2 rounding gaps in net pay.)
- Does the percentage model replace `salary_definition` entirely for those employees, or do they still have a `salary_definition` row (possibly with zero/placeholder amounts)? If they still need a `salary_definition` FK for the contract, what is in it?
- If `total_monthly` changes mid-year (salary review), is a new `grade` row created or a new `employee_contract` row? Confirm the versioning model before implementing the derivation service.

**Out of Scope:**
- UI for entering grade percentage structure in WorkspaceConfig. Backend + onboarding parser only this sprint.
- Grade percentage structure for Client A (absolute amounts only). Do not change Client A's derivation path.

**Business Risk:**
- Cost of doing it wrong: if the percentage derivation is incorrect, BASIC is wrong, which cascades to NHF, Pension, PAYE, and every downstream deduction. A ₦1 rounding error per employee per month is a compliance issue at scale.

---

## O3 — Full Shift Allowance Handler (WI-04 Sub-B + NEW-GAP8)

**Priority:** P1 — Client B shift workers are entitled to a shift allowance. Without this handler, the allowance is ₦0 for all shift employees.

**Prerequisite:** O1 must be merged and deployed first (`shift_type` must be readable from the execution context).
**Arch-council required (standalone session after O1 merges) — do not implement before sign-off.**

```
As a payroll operator,
I want the shift allowance calculated automatically from the employee's
shift percentage, their expected working days, and the shift days they worked,
So that shift workers receive the correct allowance each period without manual calculation.
```

**Formula:**
```
SHIFT_ALLOWANCE = shift_pct × basic_monthly / expected_days × shift_days_worked
```

Where:
- `shift_pct` comes from the employee's active `payroll_rule` of type `shift_allowance`
- `basic_monthly` is the BASIC component from `salary_components` at run time
- `expected_days` is the PH-adjusted working-day count already in the execution context (from PH-9)
- `shift_days_worked` is a named `payroll_input` staged by the operator before the run (code: `SHIFT_DAYS_WORKED`)

**Acceptance Criteria:**

- A new `_handle_shift_allowance` handler is implemented in `rule_evaluator.py` following the established handler pattern.
- The handler reads `shift_type` from the employee execution context (landed by O1). Employees with `shift_type = 'DAY'` or `NULL` produce `SHIFT_ALLOWANCE = 0` — the handler is a no-op for day-shift employees.
- `shift_days_worked` is read from staged `payroll_input` rows with `input_code = 'SHIFT_DAYS_WORKED'`. If no input is staged, the handler returns `0` and adds a `WARN`-level trace entry: `"SHIFT_DAYS_WORKED input not staged — SHIFT_ALLOWANCE defaulted to ₦0"`.
- Floor validation: `shift_days_worked` must be ≤ `expected_days`. If it exceeds, the run fails with a validation error (not a silent clamp): `"SHIFT_DAYS_WORKED (N) exceeds expected_days (M) for period"`.
- `SHIFT_ALLOWANCE` flows into `GROSS_PAY` and therefore `TAXABLE_INCOME` — it is a taxable earning.
- `component_trace_jsonb` records: `shift_pct`, `basic_monthly`, `expected_days`, `shift_days_worked`, and the computed `SHIFT_ALLOWANCE`.
- On retry, `shift_days_worked` is sourced from the original run's claimed inputs (snapshot), not re-staged.
- A `component_metadata` seed row for `SHIFT_ALLOWANCE` is added with `component_class = 'earning'` and canonical order after OT components.
- Handler is opt-in per workspace via `client_component_metadata`.

**Open Questions (for arch-council):**
- Is `shift_pct` a single value per employee (from their `payroll_rule`) or differentiated by `shift_type`? For example, `2_SHIFT` might have a different pct than `4_SHIFT`. Confirm whether `shift_type` is used to look up the pct or whether the employee's assigned `payroll_rule` already encodes the correct pct.
- What is the `component_class` for `SHIFT_ALLOWANCE`? If it is `'earning'`, it enters GROSS_PAY. If it should be `'non_taxable'` (e.g. for specific shift allowance types), the class must be set correctly. Confirm with client.

**Out of Scope:**
- Client 3 `basic_daily` shift allowance variant (that is O4 — depends on O3 landing first).
- Shift allowance export schedule. Surfaced in the existing payroll detail export.

**Business Risk:**
- Cost of NOT doing this: shift workers receive ₦0 shift allowance; every Client B SHIFT-type employee is underpaid each period.
- Cost of doing it wrong: incorrect `shift_pct` or wrong base (`basic_monthly` vs prorated) leads to systematic over/under-payment for all shift employees.

---

## O4 — Client 3 Shift Allowance: SHIFT2 / SHIFT3 / SHIFT4 (SHIFT-ALLOWANCE-CLIENT3 / PH-12)

**Priority:** P2 — required for Client 3 onboarding. Extends the shift allowance handler to support a `basic_daily` rate base (different from Client B's `basic_monthly` base).

**Prerequisite:** O3 must be merged first.

```
As a payroll operator onboarding Client 3,
I want SHIFT2, SHIFT3, and SHIFT4 allowance bands to be calculated using
a basic_daily rate base rather than basic_monthly,
So that Client 3's shift pay structure is handled correctly without
a separate manual calculation.
```

**What is different from O3:**
Client B's shift allowance uses `basic_monthly / expected_days × shift_days_worked`. Client 3 uses `basic_daily × shift_days_worked` directly, where `basic_daily` is the rate from the `rate_code_registry`. The handler needs to support both rate base conventions, controlled by the rule's `rate_code` field.

**Acceptance Criteria:**

- The `_handle_shift_allowance` handler is extended to support two rate base modes, controlled by `rate_code` in the rule's `rule_definition_json`:
  - `basic_monthly` mode (existing O3 path): `shift_pct × basic_monthly / expected_days × shift_days_worked`
  - `basic_daily` mode (Client 3): `basic_daily_rate × shift_days_worked`, where `basic_daily_rate` is read from `rate_code_registry` for the codes `SHIFT2`, `SHIFT3`, `SHIFT4`
- Rate codes `SHIFT2`, `SHIFT3`, `SHIFT4` are seeded in `rate_code_registry` with `unit='day'`, `base='basic_daily'` and the correct multipliers confirmed with the client.
- The handler selects the mode by checking `rate_code` in `rule_definition_json`. If `rate_code` is present and resolves to a `basic_daily` entry in the registry, use basic_daily mode. Otherwise fall back to basic_monthly mode.
- `component_trace_jsonb` records the rate base mode used (`"rate_basis": "basic_daily"` or `"rate_basis": "basic_monthly"`).
- Client B's existing shift allowance rules are unaffected — they have no `rate_code` or have a `basic_monthly` rate code.

**Open Questions:**
- Confirm exact multiplier values for SHIFT2, SHIFT3, SHIFT4 with Client 3 before seeding.
- Does Client 3 also use `SHIFT_DAYS_WORKED` as the input code, or a different code per band (e.g. `SHIFT2_DAYS_WORKED`, `SHIFT3_DAYS_WORKED`)?

**Out of Scope:**
- Client 3 full onboarding (separate story). This sprint only delivers the handler extension; Client 3 onboarding can proceed in the same sprint or the next.

---

## O5 — LTA Anniversary Trigger (NEW-GAP11)

**Priority:** P2 — statutory/contractual obligation for clients with Length-of-Service awards. Not blocking first-run for Client B, but required before UAT sign-off for affected employees.

**Prerequisites:**
- O1 must be merged (`date_engaged` / `start_date` confirmed available in execution context)
- M2 must be merged (`paye_only` input path in executor) — if M2 slips to Sprint 12, O5 cannot ship in Sprint 11

**Arch-council required (standalone session) — do not implement before sign-off.**

```
As a payroll operator,
I want the system to automatically include a Leave Travel Allowance (LTA)
in the payroll for employees whose employment anniversary falls in the pay period,
So that LTA is never missed and is correctly treated as taxable income
without being paid as a cash disbursement.
```

**Design question flagged by client (must be answered before arch-council):**

> "Is AnniversaryService an eligibility thing and should we design that as a pattern into the system? Other eligibility requirements include rent relief, accident-free allowance."

This is a significant design question. If LTA is just the first of several eligibility-triggered injections (rent relief, accident-free allowance, service increments), building a generic `EligibilityService` is more durable than a one-off `AnniversaryService`. Arch-council must decide: **bespoke AnniversaryService** (MVP, ship fast, refactor later) vs **generic EligibilityEngine** (more upfront work, avoids another rewrite for rent relief). The decision belongs to arch-council, not implementation.

**Acceptance Criteria (after arch-council confirms design):**

- At run preparation (before inputs are claimed), the system checks all active employees in the workspace: if `date_engaged` (or `employee_contract.start_date` — confirmed in O1) has an anniversary falling within the run's pay period, the employee is eligible for LTA in this period.
- For each eligible employee, a `payroll_input` row is auto-created with:
  - `input_code = 'LTA_AMOUNT'`
  - `quantity = <configured LTA amount for this employee or workspace>`
  - `input_category = 'paye_only'` (requires M2)
  - `source = 'SYSTEM_ANNIVERSARY'` (or equivalent field — arch-council to confirm whether a `source` field is added to `payroll_input`)
- The auto-created input row is claimed at run start alongside operator-staged inputs. It is indistinguishable to the executor from a manually staged input — the `paye_only` path handles it.
- Idempotency: if the anniversary-triggered input already exists for this period (e.g. re-run after a failed run), the service does not create a duplicate. Check by `(employee_id, input_code, period)` before inserting.
- On retry, the retry service reads the `paye_only` LTA input from the frozen claimed inputs — it does NOT re-trigger the anniversary check. The original injection is preserved.
- LTA amount configuration: the amount is configurable per workspace (stored in `workspace_payroll_config` or a new `workspace_lta_config` row — arch-council to decide). If no amount is configured, the service skips injection and logs a `WARN`.
- `component_trace_jsonb` records an LTA trace entry with `"trigger": "anniversary"`, `"date_engaged": <date>`, `"anniversary_year": N`, and the LTA amount. This closes the audit trail for the auto-injection.
- Run summary / execution trace shows eligible employees and whether LTA was injected or skipped (no config).

**Open Questions (for arch-council):**
- Generic EligibilityEngine vs bespoke AnniversaryService — which pattern? (See design question above.)
- Where does the LTA amount live — workspace config, per-grade rule, or per-employee contract? Different clients may need different models.
- What is the "anniversary date" exactly — the calendar anniversary of `start_date` in the pay period, or the first pay period after the anniversary? (Month boundaries may not align with anniversary dates.)
- Should the operator be able to override or cancel an auto-injected LTA input before the run is submitted? If yes, what prevents double-injection after cancellation?

**Out of Scope:**
- Rent relief and accident-free allowance eligibility triggers. If the generic EligibilityEngine is chosen, this sprint implements the engine + LTA only. Other triggers are follow-on stories.
- UI for LTA configuration. Config is set via migration seed or API in Sprint 11; UI deferred.

**Business Risk:**
- Cost of NOT doing this: employees who hit employment anniversaries receive no LTA; contractual obligation is missed; operator must track and manually stage it each month.
- Cost of doing it wrong: if idempotency fails, employees receive double LTA injections on retry; if the retry path re-triggers the check, anniversary LTA is doubled on every retry.

---

## O6 — Timesheet / Attendance Layer (NEW-GAP1) — BLOCKED — DO NOT START

**Status:** Out of scope for Sprint 11. This item requires a **full dedicated PM + arch-council sprint** before implementation begins. It is included here only to prevent it from being accidentally scoped in.

**Why it is blocked:**
- The timesheet layer introduces a new `timesheet_entry` table and a derivation pipeline that auto-populates OT/PH inputs at run-claim time.
- This changes the fundamental input-claim contract: currently, operators stage inputs manually; with timesheet, inputs are derived from attendance records.
- The interaction with manual overrides, PH AUTOMATIC mode, and OT routing is not designed.
- Entry gate requires all of Tracks K–N to be complete (to be confirmed at sprint entry).

**Unblocking criteria (before this enters any sprint scope):**
- Tracks K–N all complete and deployed.
- A dedicated PM session producing a full story with data model, derivation algorithm, override rules, and idempotency design.
- Arch-council sign-off on the derivation pipeline.
- Client confirms which input codes are auto-derived (OT1? OT2? PH?) vs which remain manually staged.

---

## Dependency Map

```
O1 (shift_type, state_of_tax, skill_level) ──► O3 (shift allowance handler)
                                           └──► O5 (LTA — if date_engaged = start_date)

O2 (grade pct structure) ──► (independent; can run parallel with O1)

O3 ──► O4 (Client 3 shift allowance extension)

M2 (paye_only path) ──► O5 (LTA uses paye_only input_category)

O1 + O2 + O3 + O4 + O5 ──► O6 (entry gate + own dedicated sprint)
```

---

## Definition of Done (Sprint 11)

- [x] Arch-council sign-off documented for O1, O2, O3 — binding decisions D5/D6/D7/D9/D10 recorded; O5 deferred (blocked on M2)
- [x] Pre-investigation answers documented before O1 arch-council (date_engaged = employee_contract.start_date confirmed; state_of_tax not in personal_details_encrypted; shift_type placed on employee_contract; skill_level free-text VARCHAR)
- [x] O1: Migration `f1e2d3c4b5a6` applied; shift_type/state_of_tax/skill_level on employee_contract; shift_type threaded per employee in batch_processor.py; onboarding parser + length guards added; GET /employees + PATCH /contract wired
- [x] O2: Migration `a2b3c4d5e6f7` applied; total_monthly + pct columns on grade; salary_derivation.py pure function with D5/D6/D7 (grade pct wins when total_monthly non-null; round-half-up + largest-component residual); component_trace includes salary_basis field
- [x] O3 (D9 gate — partial): shift_type routing implemented in rule_evaluator.py (ot_multiplier with basic_daily base returns ₦0 for shift_type in (None, 'DAY'); 2_SHIFT/4_SHIFT pass through). Full SHIFT_ALLOWANCE handler (SHIFT_DAYS_WORKED input, floor validation, component_metadata seeding) deferred to Sprint 12.
- [ ] O4: Deferred — needs stable Client 3 workspace identifier before rate code seeding migration can run
- [ ] O5: Deferred to Sprint 12 — blocked on M2 (PAYE-only additions path must land first; D10)
- [x] O6: Confirmed not started — blocked; dedicated PM + arch-council sprint required before any implementation
- [x] `/tester` verification: numeric assertions run for O2 pct derivation and O3 D9 shift gate routing (test_client3_shift_allowance.py updated with shift_type kwarg)
- [x] `/security` review: SEC-S4 resolved (grade query hardened with workspace_id filter); SEC-S5 resolved (shift_type/state_of_tax/skill_level onboarding endpoint: enum allowlist + VARCHAR length guards)
- [x] `/auditor` review: AUD-4 resolved (salary_basis + shift_type added as named fields in _period_context trace header in sequential_executor.py)
- [ ] `/retro` run at sprint close
