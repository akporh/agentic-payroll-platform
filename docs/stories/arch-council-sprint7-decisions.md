# Arch-Council Decisions — Sprint 7 (OT / PH / Shift Allowance)

Recovered from conversation transcripts 2026-04-10 to 2026-04-12.
Sessions: 8× arch-council subagents (senior-architect + principal-reviewer pairs).
Open questions Q1–Q6 and decisions D1–D4 confirmed closed from
`docs/stories/phase1-sprint7-public-holiday.md` (status line: "D1, D2, D3, D4 resolved").

---

## Binding Decisions

### D-ARCH-1 — `working_days` semantics are frozen
`PeriodContext.working_days` must NOT change meaning. It remains the count of Mon–Fri weekdays in the period with no PH subtraction. Changing it breaks:
- PAYE annualisation factor
- Proration (`compute_hire_termination_factor`)
- Absence deduction (`daily_rate_deduction`) — hard 500 error on extended sick leave if reduced

### D-ARCH-2 — `expected_hours` and `expected_days` live in the execution context dict, not in `PeriodContext`
Both fields must be computed once at the API layer and inserted into the execution context dict. They must NOT be added as fields on `PeriodContext` — that is a pure date-arithmetic object; adding DB-backed workspace-scoped PH data to it breaks audit reproducibility for historical period context rebuilds.

- `expected_hours = expected_working_days × 8` (Sprint 7 — variable hours-per-day is out of scope)
- `expected_days` is NOT derived from `expected_hours / 8` — it is computed independently from the PH calendar

### D-ARCH-3 — `ot_multiplier` handler ownership: Rule Evaluator (confirmed)
`ot_multiplier` computation lives in `apply_payroll_rules` in `rule_evaluator.py`, **not** in the sequential executor. Execution order is:
1. `apply_payroll_rules` — pre-computes all rule values into `salary_components`
2. `build_runtime_component_registry` — synthesises component entries (must be extended to include `ot_multiplier`)
3. `run_sequential_payroll` — reads pre-computed values

Routing `ot_multiplier` to the sequential executor is architecturally incoherent — `apply_payroll_rules` runs before the executor and the executor only reads pre-computed values.

### D-ARCH-4 — `_resolve_inputs` / `_check_eligibility` type mismatch is a pre-existing defect — fix before OT3
`_resolve_inputs` in `sequential_executor.py` (lines 123, 156) expects `employee_inputs[code]` to be a dict with an `"amount"` key. The repository returns a list of `{quantity, category, reference_date}` dicts. Any handler using these functions silently returns zero or raises `AttributeError`. The rent_relief handler is already exposed. OT3 must NOT use `_resolve_inputs` — read from the event list format directly (as `rule_evaluator.py` does).

### D-ARCH-5 — INP10 DB-level constraint is incomplete
A route-level guard exists but there is no CHECK constraint on the `payroll_input` table protecting against direct inserts of negative quantities. PH-5's stated dependency on "INP10 DB-level constraint" is not satisfied until the DB-level constraint is added.

### D-ARCH-6 — `WorkspacePayrollConfig` is a blocking dependency — must land before PH-2, PH-3, PH-8
The table does not exist yet. PH-2b, PH-3, and PH-8 all reference `saturday_ph_rule`, `sunday_ph_rule`, `ph_mode`, `d3_leave_overlap_rule`, `d4_absence_rule`. None of these stories can start until the PH-6 migration is merged.

### D-ARCH-7 — PH snapshot storage: add `ph_dates_used` key to `rules_context_snapshot` JSONB
The PH list applied to a run must be snapshotted at approval time. Storage location: add a `"public_holidays": [{"date": "...", "source": "NATIONAL|WORKSPACE"}]` key to `payroll_run.rules_context_snapshot`. This is a data contract change on that field. The run trace header step (`_period_context`) must also record `expected_days`, `expected_hours`, `ph_dates_used`, and `ph_source`.

### D-ARCH-8 — OT3 must flow into `GROSS_PAY` before PAYE annualisation
OT income is taxable under Nigerian PITA. OT3 must be included in `gross_salary` before the PAYE cumulative annualisation step. The OT3 rule DB row must carry `rule_type = "EARNING"` — missing or wrong `rule_type` silently excludes OT3 from PAYE. This is a statutory tax compliance failure, not a calculation error.

### D-ARCH-9 — Mid-period hire: use full monthly BASIC, not prorated BASIC
For mid-period hires, `salary_components["BASIC"]` is already prorated when rule evaluation runs. The `ot_multiplier` handler must use full monthly BASIC as the numerator. Attendance is already captured by the quantity (`shift_days` / `ot_hours`). Applying a second proration to BASIC would double-prorate every mid-period hire silently.

### D-ARCH-10 — `rate_code_registry` rename + handler must be atomic
Table rename from `ot_code_registry` → `rate_code_registry` and field rename from `ot_code` → `rate_code` inside `rule_definition_json` must land in the same deploy as the OT3 handler. Any workspace row written with the new `rate_code` key before the handler deploys produces silent ₦0 at run time.

### D-ARCH-11 — `build_runtime_component_registry` currently excludes `ot_multiplier` — must be fixed in PH-8
`build_runtime_component_registry` in `sequential_executor.py` silently discards `ot_multiplier` rules. This means shift allowances and OT3 never enter `results{}`, `_handle_sum_earnings`, or GROSS_PAY. Fixing this is part of PH-8 scope.

### D-ARCH-12 — PH calendar: Three-Tier Model (RESOLVED)
- **Tier 1 `NationalPublicHoliday`** — country-wide (`country_code = 'NGA'`), platform-managed. Applies to ALL workspaces in that country automatically. Seeded via PH-1 migration.
- **Tier 2 `WorkspacePublicHoliday`** — workspace-scoped, operator-managed. Custom client-site or factory holidays on top of Tier 1.
- **Tier 3** — employee rate override only (not day classification change). Phase 2 — design captured, implementation deferred.
- `workspace.country_code` must be populated and validated for all existing workspaces before PH-1 deploys — null value returns empty PH list and silently produces wrong `expected_hours`.

---

## Resolved Domain Questions (D1–D4 + Q1–Q6)

### Q1 / hours_per_day — RESOLVED
`hours_per_day = 8` is baked into the formula for Sprint 7. All shift types normalise to 8h/day for the `expected_hours` denominator regardless of physical shift pattern (6.5h, 11h). Variable hours-per-day is explicitly out of scope. Formula: `expected_hours = expected_working_days × 8`. No DB config needed.

### Q2 / no_stack_with — RESOLVED (remove from schema)
No-stacking is a structural domain rule, not a data-driven config. The `classify_day` function is deterministic and mutually exclusive — an hour classified as OT3 cannot also contribute to OT1 because PH hours are excluded from the OT1 `expected_hours` threshold. `no_stack_with` adds complexity for a guarantee the classifier already provides. Remove from the registry schema.

### D3 / Q3 — leave on a PH — RESOLVED
`LEAVE_ABSORBS_PH` is the default: leave absorbs the PH, no PH pay on top of leave. Configurable per workspace via `WorkspacePayrollConfig.d3_leave_overlap_rule`:
- `LEAVE_ABSORBS_PH` (default) — PH counted as a leave day, no extra pay
- `PH_ADDITIVE` — employee gets both the leave day and the PH back
UI shows a worked financial example when operator changes this setting.

### D4 / Q3b — absent on a PH — RESOLVED
`ABSENT_IS_DEDUCTIBLE` is the default: absence on a PH day is a deductible absence. Configurable per workspace via `WorkspacePayrollConfig.d4_absence_rule`:
- `ABSENT_IS_DEDUCTIBLE` (default)
- `PH_EXCUSES_ABSENCE` — employee gets PH pay regardless of ABSENT attendance entry

### D1 — PH calendar scope — RESOLVED (Three-Tier; see D-ARCH-12 above)

### D2 — PH on Saturday/Sunday — RESOLVED
Both Saturday and Sunday are configurable per workspace via `saturday_ph_rule` / `sunday_ph_rule` on `WorkspacePayrollConfig`. Default: `PH_TAKES_PRECEDENCE` for both (all shift types receive OT3). Weekday PHs always trigger OT3 — weekend rules do not apply to weekday PHs.

### Q4 — Seeding mechanism — RESOLVED
- `NationalPublicHoliday` for NGA: seeded in PH-1 migration by platform admin. No automatic external sync (out of scope).
- `rate_code_registry` platform rows (OT001–OT007, `workspace_id = NULL`): seeded in PH-7 migration. Platform codes are never editable by operators (read-only in UI).

### Q5 — Shift allowance pensionable — RESOLVED
`is_pensionable = TRUE` is the default on all `rate_code_registry` rows (including SHIFT2/SHIFT3/SHIFT4 for Client 3). Configurable by updating the workspace registry row. **Must be confirmed with each client before their first run** — wrong default produces incorrect pension every month until corrected.

### Q6 — OT3 `rule_type` — RESOLVED
OT3 rule DB row must carry `rule_type = "EARNING"`. Hard requirement enforced at rule publication, not at run time. Under-withholding PAYE is a statutory violation — the employer is liable for the shortfall plus penalties.

---

## `WorkspacePayrollConfig` — Full Schema (PH-6)

| Field | Type | Default | Options |
|-------|------|---------|---------|
| `ph_mode` | TEXT | `FILE_BASED` | `AUTOMATIC`, `FILE_BASED` |
| `ph_rate_code` | TEXT | `OT005` | Any active code in `rate_code_registry` |
| `saturday_ph_rule` | TEXT | `PH_TAKES_PRECEDENCE` | `PH_TAKES_PRECEDENCE`, `DAY_OF_WEEK_TAKES_PRECEDENCE` |
| `sunday_ph_rule` | TEXT | `PH_TAKES_PRECEDENCE` | `PH_TAKES_PRECEDENCE`, `DAY_OF_WEEK_TAKES_PRECEDENCE` |
| `d3_leave_overlap_rule` | TEXT | `LEAVE_ABSORBS_PH` | `LEAVE_ABSORBS_PH`, `PH_ADDITIVE` |
| `d4_absence_rule` | TEXT | `ABSENT_IS_DEDUCTIBLE` | `ABSENT_IS_DEDUCTIBLE`, `PH_EXCUSES_ABSENCE` |
| `updated_at` | TIMESTAMPTZ | `now()` | — |
| `updated_by` | UUID | NULL | — |

`ph_mode` semantics:
- `FILE_BASED` — PH days from input file only. Engine does NOT query PH calendar for `expected_days`. `expected_hours = working_days × 8`.
- `AUTOMATIC` — Engine queries `NationalPublicHoliday` + `WorkspacePublicHoliday`. `expected_days = working_days − ph_weekday_count`. `expected_hours = expected_days × 8`.

Client 3 requires `ph_mode = AUTOMATIC`. Current clients (Sandy/Client 1): `FILE_BASED`.

---

## `rate_code_registry` — Platform Seed Codes (PH-7)

> **This table is canonical.** The PH-7 table in `phase1-sprint7-public-holiday.md`
> previously had OT001–OT005 in a different order (OT003 = 3.25). That table has been
> corrected to match this one. Always use this document as the source of truth for
> rate code assignments.

| Code | Multiplier | Unit | Base | Description | Pensionable |
|------|-----------|------|------|-------------|-------------|
| OT001 | 1.0 | hour | basic_hourly | Straight time | TRUE |
| OT002 | 1.5 | hour | basic_hourly | Time and a half | TRUE |
| OT003 | 2.0 | hour | basic_hourly | Double time | TRUE |
| OT004 | 2.5 | hour | basic_hourly | Double time and a half | TRUE |
| OT005 | 3.25 | hour | basic_hourly | Triple time and a quarter (PH) | TRUE |
| OT006 | 3.5 | hour | basic_hourly | Triple time and a half | TRUE |
| OT007 | 3.9 | day | basic_hourly | Custom — triple+ | TRUE |

Client 3 workspace codes: SHIFT2 (0.10, day, basic_daily), SHIFT3 (0.15), SHIFT4 (0.25).

Lookup rule: workspace-specific row takes priority over platform seed for the same code.
Query: `ORDER BY workspace_id NULLS LAST LIMIT 1`.

---

## Sprint 7 Dependency Order (binding)

```
INP10 (DB-level CHECK constraint)   ← before PH-5
PH-6 (WorkspacePayrollConfig)      ← before PH-2, PH-2b, PH-3, PH-8, PH-9
PH-7 (rate_code_registry)          ← before PH-8, PH-12
PH-1 (PH calendar tables)          ← before PH-2, PH-3, PH-9, PH-10, PH-11
PH-2 (expected_hours)              ← before PH-3, PH-4
PH-2b (weekend PH config)          ← before PH-3
PH-9 (expected_days + snapshot)    ← before PH-8, PH-12
PH-8 (ot_multiplier handler)       ← before PH-4 (OT3), PH-12 (shift)
PH-3 (OT3 calculation)             ← before PH-4
PH-4 (OT3 → gross/PAYE)            ← final validation gate
PH-5 (manual OT3 adjustment)       ← parallel with PH-3/PH-4
PH-10 (PH warnings)                ← after PH-1
PH-11 (PH pre-flight AUTOMATIC)    ← after PH-1
PH-12 (Client 3 shift allowance)   ← after PH-7, PH-8, PH-9
```

---

## Arch-Council Verdicts Summary

| Council Session | Verdict |
|----------------|---------|
| SA: Public Holiday design | NEEDS REVISION |
| PE: PH design challenge | OVERTURNED (more severe — `working_days` change breaks absence guard with hard 500 errors) |
| SA: OT codes / PH modes / D3/D4 JSON schema | NEEDS REVISION |
| PE: OT codes / PH modes / D3/D4 challenge | CONCUR WITH ADDITIONS (+4 blockers: M1 `hours_per_day` unresolved, M2 registry lookup not wired to rule evaluator, M3 empty-calendar silent wrong results, M4 PH input validation needs date-keyed inputs) |
| SA: Client 3 shift allowance | NEEDS REVISION |
| PE: Client 3 shift allowance challenge | CONCUR WITH ADDITIONS + architectural correction (layer ownership is rule evaluator, not executor; double-proration defect for mid-period hires must be resolved before Client 3 onboarding) |
| SA: OT/PH gap analysis | NEEDS REVISION |
| PE: OT/PH challenge | CONCUR WITH ADDITIONS + C1 partial overturning (`expected_hours` must NOT go in `PeriodContext`; goes in execution context dict at API layer) |
