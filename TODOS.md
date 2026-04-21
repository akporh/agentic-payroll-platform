# Project TODOs

Parked work and outstanding actions that don't belong on the sprint roadmap.
Add items here when you want to remember something without blocking current work.

---

## Simulation Script Audit Fixes — DONE (2026-04-20)

**Audit report**: `/Users/michaelemedo/.claude/plans/floofy-dazzling-lemon.md`

All 10 sim-script gaps fixed in `scripts/simulate_payroll_components.py`:

| Gap | Status | What was done |
|-----|--------|---------------|
| GAP-01 | Done | Replaced `workspace.statutory_rule_id` with SQL lookup by `country_code` |
| GAP-02 | Done | Added NHF via `calculate_nhf()` + display section |
| GAP-03 | Done | Added Health Insurance flat deduction from component metadata |
| GAP-04 | Done | Added Development Levy flat deduction from component metadata |
| GAP-05 | Done | NET_PAY deducts pension + PAYE + NHF + HI + DevLevy |
| GAP-06 | Done | `PeriodContext` + `calculate_paye_for_period()`; `--period-start`/`--period-end` CLI args added |
| GAP-07 | Done | Pension base reads `client_meta.legal_role.is_pensionable`; falls back to statutory default |
| GAP-08 | Done | `--inputs` JSON arg added; `apply_payroll_rules()` called with `rate_code_map`; trace shows applied/not-applied |
| GAP-09 | Done | `ANNUAL_RENT_PAID` extracted from `--inputs`; `calculate_rent_relief_for_period()` fully wired |
| GAP-10 | Done | GROSS_PAY sums only `component_class="earning"` components |
| GAP-11 | Open | **Engine gap** — pension base override replaces rather than augments statutory default. Needs a future sprint. |

`simulate_stepthrough.py` also updated (same session):
- NHF/HI/DevLevy now read from `client_meta` (component_metadata) not `rules_jsonb`
- `rate_code_map` passed to `apply_payroll_rules()` — `ot_multiplier` rules now work
- `ENGINE_CODE` snippets updated: `calculate_rent_relief_for_period`, `calculate_paye_for_period`
- Final summary shows NHF, Health Insurance, Development Levy deduction lines

---

## Carry-forward from Last Session (Gate 3 + Gate 4)

From handoff note — not yet completed:

- [ ] Run `/tester` against Gate 3 + Gate 4 acceptance criteria
- [ ] Run `/retro` to update skill checklists
- [ ] Run `/save-session`
- [ ] Optional: create story files
  - `docs/stories/gate-3-payroll-operator-journey.md`
  - `docs/stories/gate-4-bureau-workspace-setup.md`
