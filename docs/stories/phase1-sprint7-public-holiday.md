# Phase 1 — Sprint 7: Public Holiday Awareness
**Domain:** Payroll Engine — Period Context & Overtime
**Status:** Draft — D1, D2, D3, D4 resolved; PH-6 through PH-12 added
**Source:** Reverse-engineered from March 2026 payroll run + Arch Council review

---

## Background

The current payroll engine has no concept of public holidays. The `PeriodContext`
computes `working_days` as a simple Mon–Fri count with no PH deduction. This
means:

- The `expected_hours` denominator used for OT rate calculation is wrong in any
  period containing a PH weekday
- OT3 (Public Holiday premium at 3.25× basic hourly rate) cannot be calculated
- Employees who work on Public Holidays receive no premium pay

This sprint makes the engine PH-aware end-to-end: from period setup through to
OT3 calculation and inclusion in gross pay and PAYE.

> **Arch Council verdict (April 2026):** NEEDS REVISION — DO NOT change the
> semantics of `working_days` in `PeriodContext`. Introduce a separate
> `expected_hours` field for OT rate computation only. See constraint notes
> on each story below.

---

## Stories

---

### PH-1 — Public Holiday Calendar (Three-Tier Model)

**Priority:** P1 — blocks all other PH stories

```
As a payroll operator,
I want the engine to automatically apply Nigerian national public holidays
and allow me to add custom client-site holidays on top,
So that the correct PH dates are used for every payroll run without
duplicating the national calendar for each workspace.
```

#### Three-Tier PH Model

```
Tier 1 — National calendar (platform-managed, country-wide)
  NationalPublicHoliday
  ├── country_code   e.g. 'NGA'
  ├── date
  └── description

  - Applies to ALL workspaces in that country automatically
  - No operator action required for standard national holidays
  - Maintained by the platform (seeded / updated by platform admin)
  - NOT workspace-scoped

Tier 2 — Workspace ad-hoc PHs (operator-managed, workspace-scoped)
  WorkspacePublicHoliday
  ├── workspace_id
  ├── date
  └── description

  - Operator adds custom client-site holidays on top of Tier 1
  - e.g. factory shutdown day, company founder's day
  - Workspace-scoped — only affects that client's runs

Tier 3 — Employee rate override (Phase 2 — design only this sprint)
  EmployeeRateOverride
  ├── employee_id
  ├── period_id
  ├── override_rate   ENUM('OT1', 'OT2', 'OT3') or custom agreed rate
  └── source          period input file or timesheet (Phase 2)

  - Day classification does NOT change for the employee
  - Only the rate applied to that employee's hours changes
  - An employer can agree to pay a specific employee at OT rates
    on a day that is not a PH for anyone else
  - Rate source (input file / timesheet) is Phase 2
```

#### Effective PH List for a Period

```
effective_phs(workspace_id, country_code, period) =
    NationalPublicHoliday WHERE country_code = workspace.country_code
                           AND date BETWEEN period.start AND period.end
  UNION
    WorkspacePublicHoliday WHERE workspace_id = run.workspace_id
                            AND date BETWEEN period.start AND period.end
```

This combined list is what the engine uses for:
- Computing `expected_working_days` (Mon–Fri PHs only)
- Classifying days as `PUBLIC_HOLIDAY` in timesheet entries
- Triggering OT3 for hours worked on those days

#### Acceptance Criteria

**Tier 1 — National calendar:**
- Given a payroll run is initiated for a Nigeria workspace
- The engine automatically includes all NGA national PHs within the period
  dates — no operator input required
- National PHs are visible to the operator (read-only) when setting up a period

**Tier 2 — Workspace ad-hoc PHs:**
- Given a payroll period is being created or edited
- When the operator adds a custom PH date for their workspace
- Then that date is stored as a workspace-level PH for that workspace only
- Other workspaces are not affected
- Validation: date must fall within the period's `start_date` and `end_date`
- Validation: duplicate dates (national or workspace) within the same period
  are rejected: _"[date] is already a public holiday for this period"_
- A PH on a Saturday or Sunday is accepted and stored but does NOT reduce
  `expected_working_days` (only Mon–Fri PHs affect the denominator)

**Snapshot at approval:**
- The effective PH list (Tier 1 + Tier 2) applied to a run is snapshotted
  at approval time — future changes to either calendar cannot alter a
  completed run
- The snapshot must identify the source of each PH (NATIONAL or WORKSPACE)
  for audit purposes

**Failure:**
- If a workspace PH date is outside the period range, the system returns:
  _"[date] is outside the period [start] – [end]"_

#### Out of Scope
- Automatic sync of national PH calendar from an external government source
- Per-employee PH exemptions
- State-specific PH calendars (e.g. Lagos vs Abuja) — single national
  calendar for Nigeria
- UI for national calendar management — platform admin only
- Tier 3 employee rate overrides — Phase 2

#### Business Risk
- **Not doing this:** Every OT3 calculation is blocked. Employees working PHs
  are not compensated correctly — legal and contractual exposure.
- **Wrong national calendar:** Affects every workspace simultaneously.
  Platform admin changes must be reviewed carefully.
- **Workspace PH on wrong date:** Shifts `expected_hours` for that workspace's
  run, making every OT rate wrong across all employees in that run.

---

### PH-2 — Period Context Computes `expected_hours` with PH Awareness

**Priority:** P1 — blocks OT rate calculation

```
As the payroll engine,
I want to compute expected_hours using the PH-adjusted working day count,
So that the basic hourly rate used for OT1, OT2, and OT3 is correct for
periods containing public holidays.
```

#### Acceptance Criteria

**Computation rule:**
- `expected_working_days` = count of Mon–Fri days in the period
  minus count of PHs that fall on a Mon–Fri
- `expected_hours` = `expected_working_days × 8`
- Example: Feb 21 – Mar 20 with PHs on Mar 19 (Thu) and Mar 20 (Fri):
  20 weekdays − 2 PH weekdays = 18 expected working days → 144 expected hours ✓

**Separation of concerns — CRITICAL:**
- The existing `working_days` field in `PeriodContext` retains its current
  meaning: count of Mon–Fri days, **no PH deduction**
- `working_days` continues to be the denominator for absence deductions and
  hire/termination proration — its semantics MUST NOT change
- `expected_hours` is a NEW field introduced specifically for OT rate computation
- These two fields will differ in any period containing a PH on a weekday

**No override bypass:**
- If a `working_days_override` is supplied via the API, it applies to
  `working_days` only (the existing absence field)
- Any override must be recorded in the execution trace with the operator's
  justification — it must not pass silently

**Reproducibility:**
- Given the same period dates and the same PH list, `expected_hours` must
  always produce the same result
- The PH list used must be readable from the run's snapshot after approval

#### Out of Scope
- Changing how `working_days` is used for absence deductions — that is a
  separate story requiring a separate client sign-off
- Variable hours-per-day (all shifts normalise to 8h/day for this denominator)

#### Business Risk
- **Not doing this:** `basic_hourly_rate = basic_salary / expected_hours` is
  wrong in PH months. Every OT calculation for every employee is wrong.
- **Doing it wrong (changing `working_days` semantics):** Breaks the absence
  deduction guard (hard 500 error for employees on extended sick leave),
  silently overpays mid-period hires, and corrupts all historical period
  contexts which are built with no PH awareness.

#### Open Questions
- None — separation of `working_days` and `expected_hours` is an arch-council
  requirement, not a choice.

---

### PH-2b — Workspace PH Weekend Classification Config

**Priority:** P1 — required before OT3 can be calculated for weekend PHs

```
As a payroll administrator,
I want to configure how Public Holidays falling on weekends are classified
for each workspace,
So that different clients can apply their own policy without code changes.
```

#### Acceptance Criteria

- `WorkspacePayrollConfig` has two new fields:
  - `saturday_ph_rule` — `ENUM('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')`
  - `sunday_ph_rule`   — `ENUM('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')`
- Both default to `PH_TAKES_PRECEDENCE` for new and existing workspaces
- Settings are applied at run time via the day classification function — not
  hardcoded per shift type
- Both values are recorded in the run snapshot at approval time so the rule
  applied is auditable on any historical run
- Changes to these settings do NOT retroactively affect approved runs

#### Out of Scope
- Per-employee or per-shift-type override of weekend PH rules
- UI for editing these settings — API-only for this sprint

#### Business Risk
- **Not doing this:** Weekend PH classification is hardcoded, forcing code
  changes for any client with a different policy.
- **Wrong default:** A new workspace defaults to `PH_TAKES_PRECEDENCE` —
  errs on the side of paying employees more, not less. Safer default.

#### Open Questions
- None — decision confirmed.

---

### PH-3 — OT3 Calculation for Public Holiday Hours Worked

**Priority:** P1 — core premium pay obligation

```
As an employee who works on a public holiday,
I want to receive overtime pay at the workspace-configured PH rate
(default 3.25× basic hourly rate) for every hour worked on that day,
So that I am compensated correctly per the employment terms.
```

#### Acceptance Criteria

**Calculation:**
```
basic_hourly_rate = basic_salary_monthly / expected_hours
                                           ^^^^^^^^^^^^^^
                                           PH-adjusted (from PH-2)

ph_rate_code  = WorkspacePayrollConfig.ph_rate_code   (default: OT005)
registry_row  = rate_code_registry.lookup(workspace_id, ph_rate_code)
PH_OT_amount  = basic_hourly_rate × registry_row.multiplier × total_ph_hours
```

The multiplier is **never hardcoded** — it is always read from `rate_code_registry`
via the workspace's configured `ph_rate_code`. For Sandy and current Phase 1 clients
this resolves to OT005 (3.25×). A workspace negotiating a different PH rate can
configure OT006 (3.5×) or a custom registry code without code changes.

**Inputs:**
- `ph_hours_worked` = hours recorded by the employee on any PH date in the period
- `manual_ph_adjustment` = operator-entered correction (positive or negative)
- `total_ph_hours = ph_hours_worked + manual_ph_adjustment`
- `total_ph_hours` must be ≥ 0 — if the adjustment would produce a negative
  total, the system rejects it with a clear error:
  _"PH adjustment of [x] would result in negative total PH hours ([result])"_

**Applies to:** All shift types (DAY, 2-SHIFT, 4-SHIFT)

**Weekend PH classification — configurable per workspace:**
- Day classification when a PH falls on a Saturday or Sunday is controlled by
  two workspace-level settings:

```
WorkspacePayrollConfig
├── saturday_ph_rule   ENUM('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')
│                      DEFAULT: 'PH_TAKES_PRECEDENCE'
│
└── sunday_ph_rule     ENUM('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')
                       DEFAULT: 'PH_TAKES_PRECEDENCE'
```

- `PH_TAKES_PRECEDENCE` — the PH overrides the day-of-week; all shift types
  receive OT3 for hours worked on that day
- `DAY_OF_WEEK_TAKES_PRECEDENCE` — Saturday/Sunday retains its normal
  classification (OT2 for DAY shift on Saturday; normal shift day for
  4-SHIFT/2-SHIFT on Saturday)
- Current client (Sandy): both settings = `PH_TAKES_PRECEDENCE`
- Weekday PHs (Mon–Fri) always trigger OT3 — these settings do not apply

**Day classification logic:**
```
classify_day(date, day_of_week, is_ph, config):

  IF is_ph:
    IF day_of_week == SATURDAY:
      IF config.saturday_ph_rule == 'PH_TAKES_PRECEDENCE' → PUBLIC_HOLIDAY
      ELSE                                                 → SATURDAY
    ELIF day_of_week == SUNDAY:
      IF config.sunday_ph_rule == 'PH_TAKES_PRECEDENCE'   → PUBLIC_HOLIDAY
      ELSE                                                 → SUNDAY
    ELSE:
      → PUBLIC_HOLIDAY   (weekday PH — always OT3)

  ELIF day_of_week == SATURDAY → SATURDAY
  ELIF day_of_week == SUNDAY   → SUNDAY
  ELSE                         → WEEKDAY
```

**No stacking:**
- An hour classified as OT3 cannot also contribute to OT1
- PH hours do NOT count toward the `expected_hours` threshold for OT1 purposes

**Trace:**
- PH overtime must appear in `component_trace_jsonb` under the key `PH_OT`.
  The component body must include:
  ```json
  {
    "rate_code": "<ph_rate_code from WorkspacePayrollConfig>",
    "multiplier": "<from registry_row>",
    "base_rate": "<basic_hourly_rate>",
    "quantity": "<total_ph_hours>",
    "ph_hours_system": "<ph_hours_worked — system-derived>",
    "ph_hours_manual_adjustment": "<manual_ph_adjustment — operator-entered>",
    "amount": "<computed PH_OT_amount>"
  }
  ```
  The fixed key `PH_OT` ensures consistent payslip labelling regardless of
  which rate code is configured. The `rate_code` field inside provides full
  registry traceability for audit.
- The `saturday_ph_rule` and `sunday_ph_rule` values applied must be recorded
  in the run snapshot so the classification is auditable on historical runs

**OT base is basic only:**
- Housing allowance, transport allowance, and utility allowance are excluded
  from the OT3 base rate — only `basic_salary_monthly` is used

#### Out of Scope
- OT3 for employees on annual leave during a PH — decision D3 pending
- Retrospective OT3 corrections on approved runs

#### Business Risk
- **Not doing this:** Employees working PHs are underpaid. Contractual and
  potential labour law exposure.
- **Doing it wrong (wrong `expected_hours` base):** OT rate is too high or too
  low for every employee, every PH month. Scales with headcount.
- **Wrong weekend PH config:** Underpays (if PH should trigger OT3 but
  DAY_OF_WEEK is set) or overpays (opposite). Config is workspace-level so
  the risk is contained to one client at a time.

#### Open Questions
- None — D3 resolved: `LEAVE_ABSORBS_PH` is the default. Configurable per workspace via
  `WorkspacePayrollConfig.d3_leave_overlap_rule`. See PH-6.

---

### PH-4 — OT3 Flows into Gross Pay and PAYE

**Priority:** P1 — statutory tax compliance

```
As the payroll engine,
I want OT3 pay to be included in gross salary and PAYE annualisation,
So that the correct amount of income tax is withheld from Public Holiday
overtime pay.
```

#### Acceptance Criteria

**Gross pay inclusion:**
- `gross_salary` = basic + housing + transport + utility + shift_allowance
  + OT1 + OT2 + **OT3**
- OT3 must be present in the earnings sum before PAYE is computed

**PAYE annualisation:**
- OT3 is annualised at 12× the monthly OT3 amount when computing
  `gross_paye_annual` (same treatment as OT1 and OT2)
- OT3 is taxable under Nigerian law — it must not be excluded from
  `gross_paye_annual`

**Rule classification:**
- The OT3 rule DB row must carry `rule_type = "EARNING"` so that
  `_handle_sum_earnings` in the sequential executor includes it in `GROSS_PAY`
- A missing or incorrect `rule_type` would silently exclude OT3 from PAYE —
  this is a tax compliance failure, not just a calculation error

**Verification:**
- A post-run check query must confirm `GROSS_PAY` for any employee with
  `PH_OT_amount > 0` includes that PH_OT amount
- The execution trace must show `PH_OT` as a component under the `GROSS_PAY`
  aggregation step

#### Out of Scope
- Retrospective PAYE corrections for historical runs where OT3 was excluded
- PAYE re-calculation for already-approved runs

#### Business Risk
- **Not doing this / doing it wrong:** Under-withholding PAYE is a statutory
  violation. The employer is liable for the shortfall plus penalties.
  This is a P1 tax compliance requirement, not optional.

#### Open Questions
- None — Nigerian PITA treats overtime as taxable income. OT3 inclusion in
  PAYE is non-negotiable.

---

### PH-5 — Manual OT3 Adjustment with Floor Validation

**Priority:** P2 — operator correction workflow

```
As a payroll operator,
I want to manually adjust an employee's OT3 hours up or down,
So that I can correct timesheet errors without re-running the full period.
```

#### Acceptance Criteria

**Input:**
- Operator can enter a positive or negative `manual_ph_adjustment` value for
  any employee in a DRAFT run
- Adjustment is stored as a `payroll_input` row with
  `input_code = "MANUAL_PH_ADJUSTMENT"`

**Validation:**
- `ph_hours_worked + manual_ph_adjustment >= 0` must hold
- If the result would be negative, reject with:
  _"Adjustment of [x] hours would result in [result] total PH hours.
  Total cannot be negative."_
- Adjustment is blocked on any run with status APPROVED

**Trace:**
- Both `ph_hours_system` (system-derived from `ph_hours_worked`) and
  `ph_hours_manual_adjustment` (operator) must appear separately in the
  `PH_OT` component trace body (see PH-3 trace spec) so the audit trail
  shows what was adjusted and by whom

**Dependency:**
- This story depends on INP10 (non-negative quantity constraint) being resolved
  first. The floor validation in this story is additional to, not a replacement
  for, the INP10 DB-level constraint.

#### Out of Scope
- Bulk OT3 adjustments across multiple employees in one action
- Adjustment approval workflow (second sign-off) — out of scope for this sprint
- Adjustments to APPROVED runs

#### Business Risk
- **Not doing this:** Operators cannot correct PH hours without a full re-run.
  Operational blocker on payroll close.
- **Doing it wrong (no floor validation):** A large negative adjustment produces
  a negative net pay. P0 data integrity issue.

#### Open Questions
- None — floor validation is an arch-council requirement.

---

### PH-6 — WorkspacePayrollConfig: PH Mode and Behavioural Flags

**Priority:** P1 — required before any OT/PH engine changes run in production

```
As a payroll operator,
I want to configure how each workspace handles public holidays, leave overlap,
and absence-on-PH,
So that different clients can apply their own policy without code changes.
```

#### New Table: `workspace_payroll_config`

| Field | Type | Default | Options |
|-------|------|---------|---------|
| `ph_mode` | TEXT | `FILE_BASED` | `AUTOMATIC`, `FILE_BASED` |
| `ph_rate_code` | TEXT | `OT005` | Any active code in `rate_code_registry` |
| `saturday_ph_rule` | TEXT | `PH_TAKES_PRECEDENCE` | `PH_TAKES_PRECEDENCE`, `DAY_OF_WEEK_TAKES_PRECEDENCE` |
| `sunday_ph_rule` | TEXT | `PH_TAKES_PRECEDENCE` | `PH_TAKES_PRECEDENCE`, `DAY_OF_WEEK_TAKES_PRECEDENCE` |
| `d3_leave_overlap_rule` | TEXT | `LEAVE_ABSORBS_PH` | `LEAVE_ABSORBS_PH`, `PH_ADDITIVE` |
| `d4_absence_rule` | TEXT | `ABSENT_IS_DEDUCTIBLE` | `ABSENT_IS_DEDUCTIBLE`, `PH_EXCUSES_ABSENCE` |
| `effective_from` | DATE | `'2000-01-01'` | — (the config row effective on or before run period start is selected) |
| `updated_at` | TIMESTAMPTZ | `now()` | — |
| `updated_by` | UUID | NULL | — |

> **Arch-council addition (April 2026):** `effective_from` is required for audit reproducibility.
> When the operator changes `ph_mode`, a new row is inserted (not an in-place update) with the
> new `effective_from`. The run selects the row WHERE `effective_from <= period_start ORDER BY
> effective_from DESC LIMIT 1`. The selected `ph_mode` and `ph_rate_code` are snapshotted into
> `rules_context_snapshot` at run time so retries use the same config as the original run.

`ph_rate_code` is the rate code used to calculate PH overtime pay. It is looked up
from `rate_code_registry` at run time. The default `OT005` (3.25×) applies to all
current Phase 1 clients (Sandy/Client 1). A workspace with a different PH pay
agreement sets this field to the appropriate code (e.g. `OT006` for 3.5×).

**ph_mode semantics:**
- `FILE_BASED` — PH days come entirely from the period input file. Engine does not query the
  PH calendar for `expected_days`. `expected_hours = working_days × 8`.
- `AUTOMATIC` — Engine queries `NationalPublicHoliday` + `WorkspacePublicHoliday` to compute
  `expected_days`. `expected_hours = expected_days × 8`.

#### Acceptance Criteria

- Given a workspace has no `workspace_payroll_config` row, all defaults apply — no crash
- Given `ph_mode = FILE_BASED`, the engine does not query the PH calendar for `expected_days`
- Given `ph_mode = AUTOMATIC`, `expected_days = working_days − ph_weekday_count`
- All five config values are recorded in `workspace_config_snapshot` on `payroll_run` at run
  creation time
- Changes to config after run creation have no effect on that run
- UI: when operator changes `d3_leave_overlap_rule` or `d4_absence_rule`, an inline worked
  example showing the financial implication appears before the change is saved
- UI: changing `ph_mode` shows descriptive text explaining the implication immediately

#### Out of Scope
- Per-employee config overrides
- UI for `ph_mode` management (API/onboarding JSON only this sprint)

#### Business Risk
- **Not doing this:** PH behaviour is hardcoded — no way to support clients with different
  leave or absence policies without code changes.
- **Wrong default (`ph_mode = AUTOMATIC` for File-Based clients):** Engine queries a PH
  calendar that has no data for the client → `expected_days` wrong for every employee.

---

### PH-7 — Rate Code Registry

**Priority:** P1 — required before `ot_multiplier` rules can be onboarded

```
As a bureau administrator,
I want to define and manage rate codes (OT multipliers, shift multipliers)
at platform and workspace level,
So that payroll rules can reference codes by name rather than hardcoded
multiplier values, and clients can customise their own rates without
platform code changes.
```

#### New Table: `rate_code_registry`

```
rate_code_id  UUID PK
workspace_id  UUID nullable   -- NULL = platform-wide seed
code          TEXT            -- e.g. OT001, SHIFT2
multiplier    DECIMAL         -- e.g. 1.5, 3.25, 0.10
unit          TEXT            -- hour | day
base          TEXT            -- basic_hourly | basic_daily
description   TEXT
is_active     BOOLEAN DEFAULT TRUE
UNIQUE(workspace_id, code)
```

> **Arch-council decision (April 2026):** `is_pensionable` is **NOT** stored on `rate_code_registry`.
> The pension handler reads pensionable status from `component_metadata.metadata_json["legal_role"]["is_pensionable"]`
> — not from `rate_code_registry`. Storing it here would be dead data that gives operators false confidence.
> Pension treatment for `ot_multiplier` components is controlled as follows:
> - A `component_metadata` seed row must be added for `PH_OT` with
>   `metadata_json = {"legal_role": {"is_pensionable": true}}` (default: pensionable, per PRA 2014 decision)
> - Workspace admins can override via `client_component_metadata.overrides_json` for `PH_OT`
> - The same applies to any other `ot_multiplier` component (e.g. SHIFT2, OT1)

**Platform seed codes (`workspace_id = NULL`):**

| Code | Multiplier | Unit | Base | Description |
|------|-----------|------|------|-------------|
| OT001 | 1.0 | hour | basic_hourly | Straight time |
| OT002 | 1.5 | hour | basic_hourly | Time and a half |
| OT003 | 2.0 | hour | basic_hourly | Double time |
| OT004 | 2.5 | hour | basic_hourly | Double time and a half |
| OT005 | 3.25 | hour | basic_hourly | Triple time and a quarter (PH default) |
| OT006 | 3.5 | hour | basic_hourly | Triple time and a half |
| OT007 | 3.9 | day | basic_hourly | Custom — triple+ |

> **Correction note:** Earlier drafts of this table had OT001–OT005 in a different order.
> The arch-council decisions document (`arch-council-sprint7-decisions.md`) is the canonical
> source. OT005 = 3.25 is the PH default rate code.

**Lookup rule:** workspace-specific row takes priority over platform seed for the same code.
Query: `ORDER BY workspace_id NULLS LAST LIMIT 1`.

**Three client paths:**
1. Flat rate (Client 1) — `unit_multiplier` rule, `rate_code_map = {}`, registry never consulted
2. Platform codes (Client 2) — `ot_multiplier` rule references OT001–OT007, falls back to platform seed
3. Custom codes (Client 3) — workspace defines SHIFT2/SHIFT3/SHIFT4 with `base = basic_daily`

#### Acceptance Criteria

- Given a workspace has no custom row for OT001, the platform seed (`workspace_id = NULL`) is used
- Given a workspace defines its own OT001, that row takes priority
- Given `base = basic_daily`, the handler uses `expected_days` as the denominator
- Given `base = basic_hourly`, the handler uses `expected_hours` as the denominator
- PH_OT and all `ot_multiplier` shift allowance components are pensionable by default
- Pension treatment is controlled via `component_metadata.metadata_json["legal_role"]["is_pensionable"]`, NOT via `rate_code_registry`
- The migration must seed a `component_metadata` row for `PH_OT` with `{"legal_role": {"is_pensionable": true}}`
- Workspace admins can override pension treatment per component via `client_component_metadata.overrides_json`

#### Out of Scope
- UI for rate code creation/editing (read-only view only; additions via onboarding JSON)
- Rate codes for non-salary bases (e.g. previous month's earnings)

#### Business Risk
- **Not doing this:** Every OT/shift multiplier is a hardcoded value in the rule definition.
  Any rate change requires a new rule set and code review — no client self-service.
- **Wrong `is_pensionable` default:** Pension under/overpayment for every affected employee
  every month until corrected. Must be confirmed per client before first run.

---

### PH-8 — `ot_multiplier` Calculation Method in Rule Evaluator

**Priority:** P1 — required before Client 2 or Client 3 OT/shift rules can run

```
As the payroll engine,
I want to compute OT and shift allowance amounts using a multiplier
against a salary-derived base rate,
So that variable-rate earnings are calculated correctly for any
multiplier configuration without hardcoded values.
```

#### Formula

```
base = basic_hourly:  pay = quantity × (BASIC / expected_hours) × multiplier
base = basic_daily:   pay = quantity × (BASIC / expected_days)  × multiplier
```

#### Architecture Decision (arch-council confirmed — Model A, April 2026)

The `ot_multiplier` computation lives in `apply_payroll_rules` in `rule_evaluator.py`
(**not** in the sequential executor handler). Execution order is:
1. `apply_payroll_rules` — pre-computes all rule values into `salary_components`
2. `build_runtime_component_registry` — synthesises component entries
3. `run_sequential_payroll` — reads pre-computed values

**Model A implementation:** Extend `apply_payroll_rules` signature with three new
keyword-only parameters:
```python
def apply_payroll_rules(
    ...,                             # existing params unchanged
    *,
    expected_hours: Decimal | None = None,
    expected_days:  Decimal | None = None,
    proration_factor: Decimal = Decimal("1"),
    rate_code_map: dict[str, dict] | None = None,  # pre-fetched from route layer
    ...                              # existing temporal params unchanged
)
```

- `expected_hours` / `expected_days`: computed in route layer, passed in as scalars
- `proration_factor`: from `executor.py` proration step — allows handler to reconstruct full BASIC
- `rate_code_map`: `{code: {multiplier, unit, base}}` — pre-fetched by route from `rate_code_registry`, passed as plain dict. **No infra import in domain code.**

`build_runtime_component_registry` must include `"ot_multiplier"` in its allowed set so
the pre-computed shift/OT allowance enters `results{}`, `_handle_sum_earnings`, and GROSS_PAY.

**Rule definition JSON structure:**
```json
{
  "calculation_method": "ot_multiplier",
  "rate_code": "OT001",
  "unit": "hour",
  "input_field": "ot1_hours"
}
```
Note: field is `rate_code` (not `ot_code`) — renamed as part of this sprint, pre-implementation
so no existing data is broken.

**Mid-period hire — full BASIC (D-ARCH-9):**
`executor.py:210–224` prorates `salary_components` before `apply_payroll_rules` runs.
The `ot_multiplier` branch reconstructs full BASIC as:
```python
full_basic = salary_components["BASIC"] / proration_factor
```
`proration_factor` defaults to `Decimal("1")` (no proration) — safe for all non-prorated employees.
Attendance is captured in the input quantity — dividing already-prorated BASIC by `expected_hours`
would double-prorate and halve the OT rate for mid-period hires.

#### Acceptance Criteria

- Given `base = basic_hourly`, pay = `quantity × (BASIC / expected_hours) × multiplier`
- Given `base = basic_daily`, pay = `quantity × (BASIC / expected_days) × multiplier`
- Given BASIC is absent or zero, handler raises hard `ValueError` (never silent ₦0)
- Given `expected_days` is absent from execution context, handler raises hard `ValueError`
- Given `rate_code` cannot be resolved from `rate_code_registry`, handler raises hard error
- `build_runtime_component_registry` includes `ot_multiplier`-computed components so they
  appear in GROSS_PAY
- Rule evaluator trace entry shows: `rate_code`, `multiplier`, `base_rate`, `quantity`,
  `computed_amount`
- Full monthly BASIC is used — not prorated BASIC — to avoid double-proration for
  mid-period hires

#### Out of Scope
- `ot_multiplier` for non-basic bases; sequential executor handler path for this method

#### Business Risk
- **Not doing this:** Client 2 OT and Client 3 shift allowances produce silent ₦0 with no
  trace entry. Employees underpaid with no error surfaced.
- **Wrong layer (sequential executor instead of rule evaluator):** Computation never happens
  because the executor only reads pre-computed values. Rule evaluator is the only viable layer
  given execution order.

---

### PH-9 — `expected_days` in Execution Context and Run Trace

**Priority:** P1 — required for `basic_daily` handler and audit reproducibility

```
As the payroll engine and as an auditor,
I want expected_days to be computed, stored in the execution context,
and snapshotted on the run,
So that shift allowance calculations are correct and permanently
reproducible without relying on live calendar data.
```

#### Acceptance Criteria

- Given `ph_mode = AUTOMATIC`, `expected_days = working_days − count(PHs in period on weekdays)`
- Given `ph_mode = FILE_BASED`, `expected_days = working_days` (no PH calendar query)
- `expected_days` is an explicit key in the execution context dict — not derived from
  `expected_hours / 8` at handler time
- The run trace header step (`_period_context`) records:
  - `working_days`
  - `expected_days`
  - `expected_hours`
  - `ph_dates_used` — list of date strings (e.g. `["2026-03-08", "2026-03-29"]`)
  - `ph_source` — `AUTOMATIC` or `FILE_BASED`
- Once a run is approved, the `ph_dates_used` snapshot is immutable — future changes to
  `NationalPublicHoliday` or `WorkspacePublicHoliday` do not alter it
- An auditor can reconstruct the shift allowance calculation from the run trace alone,
  without querying live calendar tables

#### Out of Scope
- `expected_days` as the absence deduction denominator (separate story, requires explicit
  client sign-off on financial impact)

#### Business Risk
- **Not doing this:** Shift allowance calculations cannot be audited or reproduced. If the
  PH calendar is corrected after a run, the original calculation is unverifiable.
- **Using `expected_hours / 8` instead of independent computation:** Couples two semantically
  distinct values; defensible today but breaks with any future non-8h/day client.

---

### PH-10 — PH Validation Warnings (FILE_BASED Mode Cross-Check)

**Priority:** P2 — operator safety net

```
As a payroll operator,
I want the system to warn me when the public holidays in the input file
don't match what the calendar expects,
So that I catch missing, duplicated, or out-of-period PH entries before
a run is approved.
```

Applies to: **all `ph_mode` configurations.** Even in `FILE_BASED` mode, the engine still
cross-checks the national PH calendar for the period.

#### Warning Scenarios

| Code | Trigger | Message |
|------|---------|---------|
| `PH_COUNT_MISMATCH_EXCESS` | File has more PH entries than calendar | "File contains [n] PH entries but calendar shows [m] for this period. Review whether the extra entry is a contractual rate day that should be handled separately." |
| `PH_COUNT_MISMATCH_DEFICIT` | Calendar shows more PHs than file | "Calendar shows [n] PHs for this period but only [m] appear in the input file. A public holiday may be missing — review to avoid underpayment." |
| `PH_DUPLICATE_IN_FILE` | Same employee has duplicate `ph_days` entries | "Employee [X] has duplicate ph_days entries for [date]. This may cause double-counting." |
| `PH_OUT_OF_PERIOD` | `reference_date` outside period | "Input row has reference_date [date] which falls outside the period [start]–[end]. Verify this is not a data entry error." |

**Mechanism:** Uses existing `execution_trace` table via `ExecutionTracer.warn_persist(step_name, context)`.
Writes rows with `status = 'warn'`. No new table needed.

#### Acceptance Criteria

- Given file has more PH entries than calendar, a `warn` trace row is written with
  `step_name = 'PH_COUNT_MISMATCH_EXCESS'`
- Given file has fewer PH entries than calendar, `step_name = 'PH_COUNT_MISMATCH_DEFICIT'`
- Given duplicate `ph_days` entries for the same employee, a `warn` trace row is written
- Given `reference_date` is outside the period, a `warn` trace row is written
- Warnings do NOT block the run — advisory only
- Warnings are visible in the UI on the run's execution trace view (amber highlight)

#### Out of Scope
- Unrecognised PH date validation — Phase 2
- Hard-blocking a run on PH count mismatch

#### Business Risk
- **Not doing this:** Operators submit runs with missing or duplicated PH days and find out
  on payslip disputes, not before approval.

---

### PH-11 — PH Pre-flight Check (AUTOMATIC Mode)

**Priority:** P2 — operator confidence before AUTOMATIC runs

```
As a payroll operator,
I want the system to verify the PH calendar is populated before starting
an AUTOMATIC-mode run,
So that I am warned if expected_days will silently default to working_days
due to an empty calendar.
```

Applies to: `ph_mode = AUTOMATIC` only. `FILE_BASED` clients bypass entirely.

#### Acceptance Criteria

- Given `ph_mode = AUTOMATIC` and no `NationalPublicHoliday` rows exist for the workspace's
  `country_code` and period, the system emits a warning before execution:
  "No public holidays found in the calendar for [country] [period]. `expected_days` will equal
  `working_days`. Verify the PH calendar is up to date."
- Given at least one PH row exists for the period, no pre-flight warning is emitted
- Pre-flight check is a warning, not a hard block — operator can proceed

#### Out of Scope
- Pre-flight check for `FILE_BASED` mode
- Automatic calendar population

#### Business Risk
- **Not doing this:** A calendar with missing entries causes incorrect `expected_days` silently —
  shift allowance and OT rates are wrong with no user alert.

---

### PH-12 — Client 3 Shift Allowance Setup (basic_daily, ot_multiplier)

**Priority:** P2 — new client onboarding capability

```
As a bureau administrator onboarding Client 3,
I want to configure shift allowances as a percentage of daily basic rate,
So that 2-shift, 3-shift, and 4-shift employees receive the correct
variable shift allowance each period.
```

**Formula:** `shift_allowance = percentage × (BASIC / expected_days) × shift_days_worked`

**Client 3 rates:**
- 2-shift: 10% (`SHIFT2`, `multiplier = 0.10`, `base = basic_daily`, `is_pensionable = TRUE`)
- 3-shift: 15% (`SHIFT3`, `multiplier = 0.15`, `base = basic_daily`, `is_pensionable = TRUE`)
- 4-shift: 25% (`SHIFT4`, `multiplier = 0.25`, `base = basic_daily`, `is_pensionable = TRUE`)

**Payroll rules (onboarding JSON/Excel):**
```json
{ "calculation_method": "ot_multiplier", "rate_code": "SHIFT2", "unit": "day", "input_field": "shift2_days" }
{ "calculation_method": "ot_multiplier", "rate_code": "SHIFT3", "unit": "day", "input_field": "shift3_days" }
{ "calculation_method": "ot_multiplier", "rate_code": "SHIFT4", "unit": "day", "input_field": "shift4_days" }
```

**Period input codes for Client 3:** `shift2_days`, `shift3_days`, `shift4_days`

Client 3 requires `ph_mode = AUTOMATIC` — `expected_days` from the PH calendar is the
daily rate denominator.

#### Acceptance Criteria

- Given BASIC = ₦200,000, `expected_days` = 20, `shift2_days` = 20:
  `shift_allowance = 200,000 / 20 × 0.10 × 20 = ₦20,000` ✓
- Given same employee joins mid-month, `shift2_days` = 15:
  `shift_allowance = 200,000 / 20 × 0.10 × 15 = ₦15,000` ✓
  (quantity naturally handles partial attendance — no additional proration factor applied)
- Shift allowance appears in GROSS_PAY
- Shift allowance enters pension base (`is_pensionable = TRUE` by default)
- `component_trace_jsonb` shows: `rate_code`, `base_rate`, `multiplier`, `quantity`, `amount`

**Dependencies:** PH-8 (`ot_multiplier` handler), PH-9 (`expected_days`), PH-7 (`rate_code_registry`),
PH-6 (`ph_mode = AUTOMATIC` config)

#### Out of Scope
- UI for rate code creation
- Pensionability toggle in UI (API/onboarding JSON only this sprint)

#### Business Risk
- **Not doing this:** Client 3 cannot be onboarded. Shift workers receive ₦0 shift allowance
  silently (no error, no trace entry) due to `build_runtime_component_registry` filter gap.
- **Pensionability unresolved at onboarding:** Pension wrong every month until corrected.
  Must be confirmed before Client 3's first run.

---

---

## Mandatory Defect Fixes (arch-council April 2026 — implement before Track C)

These are pre-existing bugs identified during the arch-council review. They must be
fixed before any PH/OT feature code lands because several will crash retried runs.

---

### FIX-1 — Cross-Period Prefetch Dead Code

**Priority:** P0 — prerequisite for PH_OT cross-period inputs
**File:** `backend/api/routes/payroll.py:383`

**Problem:** `if not isinstance(_data, dict): continue` — employee input values are lists
`[{quantity, reference_date}]`. The isinstance check is always `True`, so
`cross_period_ref_dates` is always empty. Historical rate resolution never fires.
Any input with a `reference_date` outside the current period uses the current-period rate.

**Fix:** Replace with `if not isinstance(_data, list): continue`

**Why it matters for Sprint 7:** PH_OT inputs carry event dates (the actual holiday date)
which often fall in the previous month's period. Without this fix, those inputs silently
use the wrong rate and are permanently claimed against the run with no audit signal.

---

### FIX-2 — NHF Key Divergence (3 callers)

**Priority:** P1 — silent financial error on retried runs
**Files:**
- `backend/api/routes/payroll.py:182` — reads `employee_rate` ✓
- `backend/application/payroll_retry_service.py:175` — reads `rate` ✗ (wrong)
- `backend/scripts/simulate_payroll.py:639` — reads `rate` ✗ (wrong)

**Problem:** Route and retry service use different JSON keys to extract NHF rate from
`statutory_rule.rules_jsonb`. The retry service silently falls back to the hardcoded
`0.025` default whenever the statutory rule JSON uses `employee_rate`. Retried runs
produce different NHF deductions than original runs.

**Fix:** Change `"rate"` → `"employee_rate"` in both `payroll_retry_service.py:175` and
`scripts/simulate_payroll.py:639`.

**Acceptance Criteria:**
- Given a statutory rule with `nhf.employee_rate = 0.025`, a retried run produces identical
  NHF deduction as the original run
- Given `simulate_payroll.py` uses the same NHF rate as `payroll.py`

---

### FIX-3 — Health Insurance + Development Levy Extraction Key

**Priority:** P1 — silent ₦0 for any workspace with these components
**Files:**
- `backend/api/routes/payroll.py:183–184`
- `backend/application/payroll_retry_service.py:176–177`

**Problem:** The extraction reads `rules_jsonb["health_insurance"]["employee_monthly_amount"]`
and `rules_jsonb["development_levy"]["monthly_amount"]`. If the actual statutory rule
JSONB uses `employee_amount` and `amount` (the canonical keys per CLAUDE.md), both callers
return ₦0. The handlers are correct — the bug is in extraction.

**Fix:**
- `payroll.py:183`: change key from `employee_monthly_amount` → `employee_amount`
- `payroll.py:184`: change key from `monthly_amount` → `amount`
- Same changes in `payroll_retry_service.py:176–177`

**Acceptance Criteria:**
- Given a workspace with `health_insurance.employee_amount = 5000` in statutory rules,
  `HEALTH_INSURANCE_EMPLOYEE` deduction = ₦5,000 per employee per month (not ₦0)
- Same for development levy

---

### FIX-4 — `tax_bands` Float → Decimal

**Priority:** P1 — floating-point rounding error in PAYE (amplified by new OT→PAYE path)
**File:** `backend/api/routes/payroll.py:195–202`

**Problem:** Tax band boundaries are extracted as Python `float`. When passed to
`calculate_paye_for_period`, `str(float)` representations can introduce rounding artifacts
(e.g. `float("0.07")` → `"0.07000000000000001"`).

**Fix:** Wrap extractions with `Decimal(str(...))`:
```python
tax_bands = [
    {
        "lower_limit": Decimal(str(r[0])),
        "upper_limit": Decimal(str(r[1])) if r[1] is not None else None,
        "rate":        Decimal(str(r[2])),
    }
    for r in tax_rows
]
```

---

### FIX-5 — Retry Context Missing OT/PH Keys

**Priority:** P1 — PARTIAL runs with OT employees cannot be retried after Sprint 7
**File:** `backend/application/payroll_retry_service.py:310–325`

**Problem:** `_build_shared_context` builds the execution context without
`expected_hours`, `expected_days`, `ph_dates_used`, `ph_source`. After Sprint 7 lands,
any PARTIAL run with an `ot_multiplier` rule will silently produce ₦0 OT on retry
(not a crash — the ot_multiplier branch gets `None` for `expected_hours`).

**Fix:** After loading `original_snapshot = row[5]`, extract:
```python
expected_hours   = original_snapshot.get("expected_hours")
expected_days    = original_snapshot.get("expected_days")
ph_dates_used    = original_snapshot.get("ph_dates_used", [])
ph_source        = original_snapshot.get("ph_source", "FILE_BASED")
ph_rate_code     = original_snapshot.get("ph_rate_code", "OT005")
```
Add these to the returned `context` dict. Also pass `rate_code_map` (pre-fetched from
`rate_code_registry` using the same logic as the route layer, or reconstructed from snapshot).

**Pattern:** Follow `historical_rule_sets` at `payroll_retry_service.py:304–308` — read
from snapshot, not from live tables.

**Acceptance Criteria:**
- Given a PARTIAL run where employee A succeeded and employee B failed (OT employee)
- When the run is retried
- Then employee B's OT amount matches what it would have been in the original run
- And the retry context has `expected_hours` populated (not `None`)

---

## Dependency Map

```
FIX-1 (cross-period dead code)    ← must land BEFORE any PH_OT input is introduced
FIX-2 (NHF key)                   ← can land any time; independent
FIX-3 (health/dev levy key)       ← can land any time; independent
FIX-4 (tax_bands float→Decimal)   ← must land BEFORE PH-4 (OT→PAYE)
FIX-5 (retry context)             ← must land WITH Track C (same release)
         │
INP10 (non-negative input)        ← must land BEFORE PH-5
         │
PH-6 (WorkspacePayrollConfig)    ← must land BEFORE PH-2, PH-3, PH-8
         │
PH-7 (rate_code_registry)        ← must land BEFORE PH-8, PH-12
         │
PH-1 (PH calendar tables)        ← must land BEFORE PH-2, PH-3, PH-9, PH-10, PH-11
         │
PH-2  (expected_hours field)     ← must land BEFORE PH-3, PH-4
PH-2b (weekend PH config)        ← must land BEFORE PH-3
PH-9  (expected_days + snapshot) ← must land BEFORE PH-8, PH-12
         │
PH-8 (ot_multiplier handler)     ← must land BEFORE PH-4 (OT3), PH-12 (shift)
         │
PH-3 (OT3 calculation)           ← must land BEFORE PH-4
         │
PH-4 (OT3 → gross/PAYE)          ← final validation gate
         │
PH-5  (manual adjustment)        ← can run in parallel with PH-3/PH-4
PH-10 (PH warnings)              ← can run after PH-1
PH-11 (PH pre-flight)            ← can run after PH-1
PH-12 (Client 3 shift allowance) ← after PH-7, PH-8, PH-9
```

---

## Decisions Required Before Sprint Starts

| # | Question | Who decides | Impact if wrong |
|---|---|---|---|
| D1 | Is the PH calendar per-workspace or country-wide? | **RESOLVED** | Three-tier model: Tier 1 = Nigeria national calendar (platform-managed, all workspaces); Tier 2 = workspace ad-hoc additions (operator-managed); Tier 3 = employee rate override (Phase 2 — rate only, no day classification change). |
| D2 | PH falling on Saturday/Sunday for 4-SHIFT/2-SHIFT: OT3 or normal shift day? | **RESOLVED** | Both Saturday and Sunday configurable per workspace via `saturday_ph_rule` / `sunday_ph_rule`. Default: `PH_TAKES_PRECEDENCE` (OT3 for all shifts). |
| D3 | Employee on annual leave on a PH: does PH pay apply on top? | **RESOLVED** | `LEAVE_ABSORBS_PH` is the default (leave absorbs the PH, no PH pay on top of leave). Configurable per workspace via `WorkspacePayrollConfig.d3_leave_overlap_rule`. UI shows worked example when operator changes this setting. |
| D4 | Is `attendance_entry = ABSENT` on a PH day a deductible absence? | **RESOLVED** | `ABSENT_IS_DEDUCTIBLE` is the default (absence on a PH day is still deductible). Configurable per workspace via `WorkspacePayrollConfig.d4_absence_rule`. |

---

## Out of Scope (Sprint 7)

- Automatic national PH calendar sync from any external source
- State-specific PH calendars (Lagos vs Abuja vs Ogun)
- Changing absence deduction denominator to be PH-adjusted — separate story,
  requires explicit client sign-off on the financial impact
- Retrospective corrections on approved runs
- Gratuity, NHF, NHIS, Development Levy interactions with PH
- UI for PH calendar management (API-only for this sprint)
- **Tier 3 employee rate overrides** — design captured in PH-1, implementation
  deferred to Phase 2. Rate source (period input file or timesheet) to be
  confirmed before Phase 2 planning.
