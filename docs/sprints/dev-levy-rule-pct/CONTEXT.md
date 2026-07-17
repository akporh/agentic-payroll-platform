# Sprint — `dev-levy-rule-pct`

**Status:** scope confirmed 2026-07-15 (three PM decisions below); arch-council interim verdict NEEDS REVISION; plan not yet revised or approved.
**Role:** Two real fixes surfaced by an ad-hoc reconciliation investigation (Jan 2026 software-vs-legacy diff, Google Sheet `1yGlXsm9YK03OBbXhJcgODHmB69LQ6mD5`) — not started from `/roadmap`. This workspace exists to give that investigation's output (arch-council review, pending decisions) a durable home instead of living only in chat, where a context compaction already lost the verbatim arch-council text once.

---

## Goal

1. Fix the Development Levy calculation so it actually deducts ₦100 per employee per calendar year — charged every January, and separately in whichever month is an employee's first paid month (see DEC-04 below: these are two independent triggers, and a December-start hire correctly gets charged in both December and the following January, one charge per calendar year, not a double-charge bug). Currently computes ₦0 for everyone — two independent root causes.
2. Let operators configure a "percentage of basic" earning rule via UI (engine already supports it via `percentage_of_sum`; gap is UI-only, plus a latent invalid-method bug in the existing PERCENTAGE_OF_GROSS option).

## Source item

Not yet in `docs/ROADMAP.md` — confirmed by grep (2026-07-15): no `DEV-LEVY`/`RULE-PCT`/"development levy"/"percentage of basic" entries exist there. Flagged for the next `/roadmap` sync, not bundled into this sprint's scope.

Originating investigation: Jan 2026 payroll reconciliation against Sandy's legacy system found all 184 employees short the ₦100 statutory Development Levy, plus a ~₦98.91 SMC-employee diff (root-caused separately to legacy including an extra month's BASIC in a 13th-month/leave-allowance PAYE calc — NOT a software bug, carried to Sandy outside this sprint, see "Open item" below).

## PM decisions (Michael, 2026-07-15/16 session — see `decisions.md` DEC-01/02/03/04)

- Levy cadence: **two independent triggers, both fire whenever their condition holds — not exclusive branches**:
  1. Every January run (any active employee).
  2. **Every employee's first paid month**, whenever in the calendar that falls — not restricted to "mid-year." A hire's first paid month always gets charged, regardless of which calendar month that is.
  - **Correction, 2026-07-16 (DEC-04):** "mid-year hire" in the original framing was imprecise and is retired. The trigger is "first paid month," full stop — it applies to every hire, January included. Consequence, confirmed intended by Michael, not a bug to guard against: an employee whose first paid month is **December** is charged ₦100 in December (trigger 2) **and again in January** the same or following cycle (trigger 1) — two charges ~1 month apart is correct, because each trigger is independently evaluated per run, and "first paid month" and "the January run" are different events even when they land close together.
  - Implication for the cadence gate: it must be `if condition_a OR condition_b`, never `elif` / mutually exclusive — this was already how the plan's engine-cadence-gate section was worded, so no code-shape change, but the CONTEXT/AC language must stop saying "January, or a mid-year hire's first paid month" as if those were alternate branches for the same one-time charge.
- Levy amount source: **statutory default (₦100) + per-workspace override** (matches pension/NHF pattern).
- Percentage-of-basic: **earnings only**.

## In-scope stories

### Story 1 — DEV-LEVY-1: Development Levy applied correctly (P1 — statutory compliance)
Root causes: (a) `component_metadata.DEVELOPMENT_LEVY.is_active = FALSE` globally (data drift from seed truth) excludes it from the execution graph entirely; (b) no amount anywhere in `statutory_rule.rules_jsonb` or workspace `overrides_json`; (c) new cadence requirement not yet modeled (current handler is flat-per-run, would 12× overcharge).
Full root-cause detail, file/line references, and draft changes: see the plan file `~/.claude/plans/steady-petting-orbit.md` (pre-arch-council-revision draft) and `architecture.md` (council findings) in this folder.

### Story 2 — RULE-PCT-1: "Percentage of basic" earning rule configurable (P2)
No engine change needed — `percentage_of_sum` with `base_components=["BASIC"]` already computes this. Gap is UI (`WorkspaceConfig.tsx`) plus fixing the existing PERCENTAGE_OF_GROSS option, which emits an invalid `calculation_method` string rejected by the DB CHECK constraint.

## Acceptance criteria

See the plan file's per-story AC sections — **must be revised** to drop the original "reconciliation diff → 0 for all 184 employees" AC per DEC-06 (arrears accepted as a gap, not remediated). Replacement AC: the cadence gate correctly governs all periods from its deploy date forward; the already-reconciled Jan 2026 run is explicitly out of scope and stays as-is.

## Out of scope

- Reconciling the three separate `is_active` flags (`component_metadata`, `client_component_metadata`, dead `overrides_json.is_active` key) into one model, beyond deleting the dead key.
- HEALTH_INSURANCE_EMPLOYEE amount seeding.
- D-ARCH-2 statutory hard-reject re-enablement (already disabled, `workspace.py:1316-1319`).
- Exposing `base_components` as a picker, deduction-type percentage rules, `eligibility_field` UI, a distinct `percentage_of_basic` method string.

## Open item carried to Sandy (not in this sprint)

The PAYE differences (~one month's basic × 15% ÷ 12 for ~90 employees) — awaiting Sandy's confirmation of the legacy 13th-month/leave-allowance treatment before scoping.

## Open questions — resolved 2026-07-16 (see `decisions.md` DEC-06 through DEC-09)

1. **2026 arrears:** accept the gap, fix forward only. No correction run for the 184 employees. (DEC-06)
2. **INACTIVE-in-January residual case:** accept as a known edge case, no explicit handling this sprint. (DEC-07)
3. **Rename `monthly_amount` → `annual_amount`:** yes, this sprint. Coordinated change across the seed value, ~5 code read-sites, and the frontend field key. (DEC-08)
4. **Explicit `override = 0`:** allowed — a workspace can zero out the levy via an explicit `annual_amount: 0`. Must stay distinct from "no override" (→ default 100). (DEC-09)

All four open questions are now resolved. Remaining work before this can gate `ExitPlanMode`: revise `~/.claude/plans/steady-petting-orbit.md` to incorporate the 9 ranked arch-council findings (`architecture.md`) plus these 4 resolutions, then either re-run `/arch-council` against the revised plan for a genuinely verbatim record, or proceed directly to `ExitPlanMode` if the revision is judged mechanical enough not to need a second pass.
