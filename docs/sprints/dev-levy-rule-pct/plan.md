<!--
Copied verbatim from ~/.claude/plans/steady-petting-orbit.md immediately
after plan approval, per D5 (docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-implementation-plan.md).
The harness-owned original at that path is untouched — this is a durable
repository copy, not a move.

Note on the approval mechanism: plan mode had already exited earlier in
this session (a harness event, not an explicit ExitPlanMode call), so the
normal ExitPlanMode approval gate was unavailable when this revision was
ready. Approval was instead obtained directly via AskUserQuestion
("Approve the revised plan... so it can be copied into the sprint
workspace as plan.md and implementation can start?" → "Approved").
Recorded as decisions.md DEC-dev-levy-rule-pct-10.

Approved: 2026-07-16.
-->

# Sprint plan — Development Levy fix + Percentage-of-Basic rule config

Sprint workspace: `docs/sprints/dev-levy-rule-pct/` (`CONTEXT.md`, `decisions.md`, `architecture.md`, `state.md`). This revision incorporates the arch-council Council Summary (`architecture.md`) and all 9 resolved human decisions (`decisions.md` DEC-01 through DEC-09). Revision history at the bottom.

## Context

The Jan 2026 reconciliation against Sandy's legacy system (run `e3bd910a`) showed every one of 184 employees short a ₦100 Development Levy deduction. Investigation found the software engine handler exists (`development_levy_flat`, priority 430) but never fires and would compute ₦0 even if it did. Separately, Michael wants operators to be able to configure "percentage of basic" earning rules; exploration showed the engine already supports this via `percentage_of_sum` — the gap is UI-only, plus a latent bug where the rule form's PERCENTAGE_OF_GROSS option emits an invalid method string that the DB CHECK constraint rejects.

**PM decisions (DEC-01 through DEC-09, `decisions.md`):**
- Levy cadence: **two independent triggers**, both evaluated every run, OR'd together — never exclusive branches: (a) the run period contains January, (b) this is the employee's first paid month. A December-start hire is correctly charged in December (trigger b) **and again** the following January (trigger a) — one charge per calendar year; not a double-charge bug (DEC-04).
- Levy amount source: statutory default (₦100) + optional per-workspace override, key **`annual_amount`** (renamed from `monthly_amount` this sprint, DEC-08).
- A workspace override may be explicitly **zero** (`annual_amount: 0`), distinct from no override present, which resolves to the statutory default (DEC-09).
- Percentage-of-basic: earnings only.
- 2026 arrears: **accepted as a gap, not remediated.** No correction run for the 184 already-reconciled January 2026 employees. This sprint's levy fix governs periods from its deploy date forward only (DEC-06). **This removes the original "reconciliation diff → 0 for all 184 employees" acceptance criterion** — see revised AC below.
- An employee INACTIVE during their own eligible trigger month is a known, accepted edge case — no special handling this sprint (DEC-07).

## Story 1 — DEV-LEVY-1: Development Levy applied correctly (P1 — statutory compliance)

**As a** payroll operator, **I want** the Development Levy deducted per statute (₦100/employee/year, January and each employee's first paid month) **so that** software runs reconcile with legal obligations going forward.

### Root causes (all three must be fixed; any one alone yields ₦0 or an overcharge)
1. Global `component_metadata.DEVELOPMENT_LEVY.is_active = FALSE` (data drift — seed migration `c1d2e3f4a5b6` set TRUE) → component excluded from the execution graph by `backend/api/routes/payroll.py:415-422` (query filters `is_active = TRUE`) and `sequential_executor.py:658`. The "Active" toggle the operator sees is `client_component_metadata.is_active` (a different flag) — and `overrides_json.is_active` is a third, **dead** key nothing reads.
2. Amount resolves to 0: no `development_levy` key in `statutory_rule.rules_jsonb` (`payroll.py:281` defaults "0"), and no workspace override amount exists (the Edit Override SlideOver only renders keys already present — an amount can never be added; `WorkspaceConfig.tsx:815-832`).
3. Cadence: current handler (`sequential_executor.py:423-428`) is flat-per-run — would deduct ₦100 every month (12× the statutory amount) if simply switched on.

### Changes

**Migration A (data repair, idempotent, tightened per arch-council):**
- Guarded: `UPDATE component_metadata SET is_active = TRUE WHERE component_code = 'DEVELOPMENT_LEVY' AND country_code = 'NG' AND is_active = FALSE` — not a blind `SET`. Emit `RAISE NOTICE` with the affected row count.
- Downgrade: no-op with a comment (seed truth is TRUE; downgrading to FALSE would just reintroduce the original bug).
- Dead-key cleanup, as a separate guarded step: for each `client_component_metadata` row, **before** deleting the dead `overrides_json.is_active` key, check whether its value disagrees with the dedicated `is_active` column. If any row disagrees, log it (`RAISE NOTICE`) rather than silently deleting — it may be forensic evidence of a past bug, not just dead data. Only delete keys that agree or are absent from disagreement.

**Migration B (statutory seed):**
- Add `development_levy` to `statutory_rule.rules_jsonb` for both NG rule rows: `{"amount": 100, "cadence": "ANNUAL"}`. Single pinned literal — `ANNUAL` — not `ANNUAL_FIRST_ELIGIBLE_MONTH` (earlier draft's inconsistent literal, now retired). `ANNUAL` means "both triggers below apply"; `MONTHLY` (existing implicit default before this migration) remains a valid override value for any workspace that deliberately wants flat-per-run behaviour.
- In-place `rules_jsonb` update with existence pre-check (skip if `development_levy` key already present); downgrade removes the key.
- **Do not bump the `version` column** — it participates in an `ORDER BY` at `payroll.py:251` and bumping it is unrelated to this data change.
- Docstring must name the specific Nigerian statute/circular this levy derives from (per the `PAY-TAX-1` retro convention — statutory seeds must be verified against a named Act, not just copied from an existing pattern). **Verify the exact citation before writing this migration** — do not proceed on assumption.
- Update the now-stale `component_metadata.metadata_json` note ("Flat monthly state levy" → reflects the new annual/first-paid-month cadence).

**Deploy/migration sequencing (arch-council CRITICAL finding — deploy-order hazard):**
The levy-reading code already runs in production every period (`payroll.py:281`, the existing flat handler). If Migrations A+B ship *before* the cadence-gated handler code is live, every run in the gap window deducts ₦100 **every month** against real payroll data. Required order:
1. Deploy the cadence-gated handler code first, with the DB still in its current state (`is_active=FALSE`, no `development_levy` key) — this is inert, changes nothing in production, and is safe to ship standalone.
2. Confirm the new code is live (e.g. a smoke-check that the handler reads `development_levy_amount`/`cadence` from context without erroring even though the DB doesn't have the key yet).
3. Only then run Migrations A and B.
This ordering constraint must be called out explicitly in the PR/deploy notes for this sprint, not left implicit.

**Engine cadence gate** in `_handle_development_levy_flat` (`backend/domain/payroll/sequential_executor.py:423`):
- Apply the amount when **either** (a) the run period contains January, **or** (b) `ctx["is_first_paid_month"]` is true for this employee — evaluated independently (`if a or b`, never `elif`). Both can fire for the same employee in different runs within weeks of each other (December hire → charged in Dec and again in Jan) — this is correct, not a bug (DEC-04).
- Cadence-absent default is **ANNUAL**, not MONTHLY (arch-council: MONTHLY-as-silent-default is a dangerous 12× overcharge risk; ANNUAL is the safe default and matches what every workspace actually wants unless it deliberately opts into MONTHLY).
- When neither trigger fires, emit a ₦0 trace entry with an explanatory note ("not applied — annual levy already outside eligible month"), matching existing not-applied trace conventions.
- **`is_first_paid_month` signal source:** *not* `contract.start_date` (rejected — `employee_contract_snapshot` only stores the run-period contract's dates, so a naive `MIN(start_date)` check breaks under retry). Instead, compute it once at run creation time in `payroll.py` (same place `is_union_member` is already computed and threaded, ~lines 223-240): for each employee, `is_first_paid_month = NOT EXISTS (SELECT 1 FROM payroll_result pr JOIN payroll_run r ON pr.payroll_run_id = r.payroll_run_id WHERE pr.employee_id = employee.employee_id AND r.workspace_id = :workspace_id AND r.period_start < :this_period_start AND pr.status = 'SUCCESS')`. Store this boolean in `per_employee_context_json` alongside `is_union_member` — it is then automatically captured by the existing snapshot mechanism and reproduces correctly on retry with zero new snapshot columns.
- Cadence value itself (`ANNUAL`/`MONTHLY`) threaded from `rules_jsonb.development_levy.cadence` in `payroll.py`, same pattern as `development_levy_amount`. Same threading applies in `payroll_retry_service.py:370` (already reads the snapshot, no new mechanism needed there).

**UI — Edit Override SlideOver (`frontend/src/pages/WorkspaceConfig.tsx:800-905`):**
- Render amount inputs driven by `component_metadata.metadata_json.engine_behavior.workspace_override_key` (seeded for DEVELOPMENT_LEVY → **`annual_amount`**, renamed from `monthly_amount` this sprint per DEC-08) instead of only keys already present in `overrides_json`.
- Blank field = statutory default, shown as a placeholder with helper text "Leave blank to use the statutory default (₦100/year)." Levy-specific helper copy: "Deducted once per year — in January, and again in a new hire's first paid month if different."
- **Zero must be preserved distinctly from blank** (DEC-09): the save logic must check `"annual_amount" in overrides_json` (key presence), never a truthy check on the value — `Decimal("0")` is falsy in a naive truthy check and would be wrongly treated as "no override." Blank input on save → **omit** the key entirely (not write `0`). An explicit `0` entered by the operator → **write** the key with value `0`.
- **CRITICAL — merge, not replace (arch-council top finding):** the PATCH call must merge the changed key(s) into the existing `overrides_json`, never submit a full replacement object built only from keys the SlideOver happened to render. This was the actual failure mode of the prior draft (and a recurrence of a previously logged incident — `component_class`/`flat_amount` keys would be silently destroyed). Concretely: `PATCH` payload carries only the fields being changed; `workspace.py::patch_component_override` does `existing_overrides_json | payload` (dict merge favoring new values), not `payload` as the new `overrides_json` wholesale.

**API validation (arch-council MEDIUM finding):** add a Pydantic model for the PATCH body — the amount field (`annual_amount` or whichever `workspace_override_key` applies to the component being patched) must validate as `Decimal | None`, `ge=0`, with a sane upper bound (e.g. `le=10_000_000`) — rejecting malformed input at the API boundary with a generic message, not letting it fail deep inside a payroll run as an opaque `Decimal` error. Per this repo's standing rule, never return `str(e)`.

**Data hygiene:** covered under Migration A above (dead-key strip with disagreement pre-check).

### Acceptance criteria (revised — the original 184-employee AC is dropped per DEC-06)
- For any run whose period *from this sprint's deploy date forward* contains January: every active employee has DEVELOPMENT_LEVY = ₦100 (or their workspace override) in results and component trace.
- For a run in a non-January period: levy = ₦0 for an employee whose `is_first_paid_month` is false, with a "not applied" trace note; = ₦100 (or override) for an employee whose `is_first_paid_month` is true.
- An employee whose first paid month is December, run in a workspace that also processes the following January: charged in both runs (two separate calendar-year charges), confirmed as intended via an explicit regression test.
- Workspace override `annual_amount: 150` → runs use 150. Override `annual_amount: 0` → runs use 0 (explicit zero, not treated as "no override"). No override key present → statutory default 100.
- PATCH with a non-numeric or negative `annual_amount` → HTTP 422 with a generic message, no exception string leaked.
- Retry of a pre-fix run reproduces the original (snapshot) result — no retroactive levy injection. Retry of a post-fix run reproduces `is_first_paid_month` correctly from `per_employee_context_json` snapshot, no live re-query.
- `GET /platform-components` now lists DEVELOPMENT_LEVY (previously hidden by the same `is_active` filter, `workspace.py:1079`).
- PATCH on any other component's `overrides_json` (e.g. one carrying `component_class`/`flat_amount`) is unaffected by an unrelated DEVELOPMENT_LEVY override save on the same workspace — explicit regression test for the merge-not-replace fix.
- Regression tests named for each invariant above (cadence OR logic, ANNUAL default, zero-vs-absent override, snapshot immunity, merge-not-replace).

### Out of scope
- 2026 arrears remediation (DEC-06 — explicitly not doing this).
- INACTIVE-in-eligible-month handling (DEC-07 — accepted edge case).
- Reconciling the three `is_active` flags into one model, beyond the dead-key strip in Migration A.
- HEALTH_INSURANCE_EMPLOYEE amount seeding.
- D-ARCH-2 statutory hard-reject re-enablement (already disabled, `workspace.py:1316-1319`) — flag to backlog.

## Story 2 — RULE-PCT-1: "Percentage of basic" earning rule configurable (P2)

**As a** payroll operator, **I want** to configure an earning rule as a percentage of BASIC **so that** percentage-structured allowances don't require engineering.

### Key finding — no engine change, no migration
`percentage_of_sum` (`rule_evaluator.py:633-726`) already computes `rate × sum(base_components)`; `base_components: ["BASIC"]` is exactly "X% of basic". It is in the DB CHECK constraint (`2b3c4d5e6f7a`) and auto-publish copies definitions verbatim. **Do not add a new calculation_method.**

Latent bug fixed as part of this story: `RULE_TYPE_METHOD` maps PERCENTAGE_OF_GROSS → `percentage_of_gross`, an **invalid** method (rejected by the DB CHECK; the test suite literally uses that string as the canonical unknown method). Pre-implementation data check: confirm no `payroll_rule` rows exist with `calculation_method='percentage_of_gross'` (CHECK constraint should make this impossible).

### Changes (frontend + tests; one backend validation addition)
- `WorkspaceConfig.tsx:1116-1131`: replace `PERCENTAGE_OF_GROSS` option with `PERCENTAGE_OF_BASIC` ("Percentage of basic (%)") mapping to `percentage_of_sum`; restrict to EARNING rule type per PM decision.
- `RuleFields` (`:1133-1261`): percent input (operator enters 5 = 5%), converted to multiplier 0.05 in `buildDefinition` (`:1304`), emitting `{"calculation_method":"percentage_of_sum","rate":0.05,"base_components":["BASIC"],"prorate_on_hire":true}`. Display conversion ×100 in edit view (method stays read-only per standing UI decision).
- **`prorate_on_hire: true` (arch-council correction — do not accept the overpayment):** the earlier draft proposed documenting full-month BASIC for mid-month hires as an accepted limitation. That's wrong — the executor already has a `prorate_on_hire: true` opt-in (`executor.py:270-283`) that correctly single-applies proration (verified: rules → proration → gross sweep is a fixed order, so no double-proration risk). Emit this flag on every rule created through this UI path.
- **Save-time validation (arch-council MEDIUM finding):** before saving a `percentage_of_sum` rule with `base_components: ["BASIC"]`, verify `BASIC` actually exists in the workspace's configured base salary components (this repo already supports non-standard base component codes elsewhere, e.g. NHF's configurable base) — reject the save with a clear error if it doesn't, rather than silently persisting a rule that will compute ₦0 forever while marked "applied."
- `METHOD_TO_RULE_TYPE` (`:1390-1396`): map `percentage_of_sum` + `base_components===["BASIC"]` → PERCENTAGE_OF_BASIC; other shapes render read-only generic.
- Copy audit for removed PERCENTAGE_OF_GROSS references (retro lesson: feature-removal copy audit).
- **Tests (backend, closing a coverage hole):** `tests/test_rule_evaluator.py` gains `percentage_of_sum` coverage — happy path over `["BASIC"]`, rounding (ROUND_HALF_UP to 0.01), empty `base_components` → not_applied, eligibility gate, and a `prorate_on_hire` proration test for a mid-month hire. Template: existing `TestFixedAmount` classes.

### Acceptance criteria
- Operator creates "Hazard Allowance — 5% of basic" via the Add Rule SlideOver; next run shows the component = 5% of that employee's (correctly prorated, if mid-month hire) BASIC, present in gross and trace.
- Editing the rule shows "5%" (never 0.05); method not editable.
- PERCENTAGE_OF_GROSS no longer selectable; no orphaned copy mentions it.
- Attempting to save a percentage-of-basic rule in a workspace with no `BASIC` component fails with a clear, actionable error — verified by test, not just documented as a limitation.
- A mid-month hire's percentage-of-basic component is correctly prorated to their partial-month BASIC (via `prorate_on_hire: true`), not the full-month amount.

### Out of scope
- Exposing `base_components` as a picker, deduction-type percentage rules, `eligibility_field` UI, a distinct `percentage_of_basic` method string.

## Test-impact housekeeping (arch-council LOW findings — do in this sprint, not deferred)
- `tests/test_statutory_flat_amount_keys_e2e.py` posts a run with no explicit period (defaults to wall-clock current month) and asserts `EXPECTED_NET` including `LEVY_AMOUNT`. Once cadence gating ships, this becomes month-sensitive/flaky. Pin it to an explicit January period (or explicitly assert the ₦0 not-applied case for a pinned non-January period) as part of this sprint.
- Audit `simulate_payroll.py`, `simulate_payroll_components.py`, `simulate_stepthrough.py` for `development_levy_amount` threading — update to reflect cadence-gated behaviour, or add an explicit comment flagging the divergence if updating is out of scope for this pass.
- Every other existing CI test that resolves the seeded NG statutory rows over a January period will legitimately gain a ₦100 deduction once Migration B lands. Triage each resulting failure individually: "assertion now correctly includes the levy" (fix the expected value) vs. "test resolves the wrong statutory row" (real bug) — do not blanket-adjust expected values without checking which case applies.

## Execution order
1. Cadence-gated handler code + `is_first_paid_month` threading + tests (backend track) — **deployed and confirmed live before any migration runs**, per the sequencing note above.
2. Migrations A and B.
3. Story 1 + 2 UI changes in `WorkspaceConfig.tsx` (single file, one pass; then `npx tsc --noEmit`).
4. Test-impact housekeeping (pin the e2e test, audit simulation scripts, triage any newly-red CI assertions).
5. Full suite `python -m pytest -q` green; `/security` (touched routes: `workspace.py` PATCH validation, `payroll.py` if route bodies change), `/auditor` (statutory calculation change), `/tester` vs ACs, `/retro`, commit+push.

## Verification (end-to-end)
- Seed a test workspace; run a January period → assert ₦100 levy per employee via API response and `component_trace_jsonb`.
- Run a non-January period on the same workspace → assert ₦0 + trace note for existing employees; add an employee whose `is_first_paid_month` is true in that period → assert ₦100 for them only.
- Simulate a December-hire employee, run December then January → assert both runs charge the levy (regression test for the intended dual-charge behaviour, DEC-04).
- Set an explicit `annual_amount: 0` override → assert ₦0, and confirm it's distinguishable in the trace/response from "no override, statutory default applies."
- Create the 5%-of-basic rule via the UI (live app, `/verify` — API-to-frontend boundary is touched) for both a full-month and a mid-month-hire employee; run, and check the component in the run detail page for both.
- Attempt to PATCH an unrelated component's override on a workspace that also has a DEVELOPMENT_LEVY override set — confirm the DEVELOPMENT_LEVY override survives (merge-not-replace regression check, live).
- **Not verified this sprint (by design, DEC-06):** the original Jan 2026 reconciliation diff for the 184 employees. That run is out of scope; do not re-run the reconciliation export expecting it to change.

## Open item carried to Sandy (not in sprint)
The PAYE differences (exactly one month's basic × 15% ÷ 12 for ~90 employees) — awaiting Sandy's confirmation of the legacy 13th-month/leave-allowance treatment before scoping.

## Revision history
- 2026-07-15 — initial draft.
- 2026-07-15 — arch-council review (Senior Architect + Principal Engineer), interim verdict NEEDS REVISION. See `docs/sprints/dev-levy-rule-pct/architecture.md`.
- 2026-07-16 — DEC-04: cadence trigger independence corrected (not "mid-year hire," both triggers OR'd, Dec-hire dual-charge is intended).
- 2026-07-16 — DEC-06 through DEC-09: arrears accepted as a gap, INACTIVE-in-month accepted as edge case, rename to `annual_amount` approved, explicit zero-override approved.
- 2026-07-16 — this revision: all 9 arch-council findings + all 4 newly-resolved decisions incorporated.
- 2026-07-16 — approved via direct chat confirmation (ExitPlanMode unavailable, plan mode already exited); copied into this sprint workspace per D5.
