# Architecture — `dev-levy-rule-pct`

**Note on provenance:** the Senior Architect and Principal Engineer agents ran earlier in this session, against the pre-revision draft of `~/.claude/plans/steady-petting-orbit.md`. The verbatim agent output was lost to a context compaction before it was persisted anywhere. What follows is a reconstruction from the working notes that survived compaction (a detailed structured summary, not the raw agent text). Treat findings as accurate in substance; do not treat any bracketed wording as a verbatim quote from either agent. If a re-run is cheap, re-running `/arch-council` against the revised plan (once DEC-04's cadence-logic correction is folded in) will produce a fresh, genuinely verbatim record — recommended before this gates `ExitPlanMode`.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SENIOR ARCHITECT ASSESSMENT (reconstructed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**What was done well:** correctly identified `percentage_of_sum` already exists (no new calc method, no CHECK-constraint migration needed); root-caused the levy gap to two independent faults rather than one; PM decisions captured up front.

**Architectural concerns:**
1. In-place `rules_jsonb` backfill needs a docstring naming the statute; must not bump `version` (used in an `ORDER BY` at `payroll.py:251`).
2. Cadence gate as drafted risked double-charging under non-calendar-aligned periods; "period contains January" is looser than needed — should be "contains January 1." **Note:** DEC-04 (2026-07-16) clarifies the two triggers are meant to fire independently — a Dec-hire correctly gets charged in Dec and again in Jan. This concern should be re-scoped in the plan revision to "guard against a single trigger firing twice for the same period" (e.g. a fortnightly period that spans two calendar months), not "guard against both triggers firing in the same rolling window."
3. Default-to-MONTHLY when the cadence key is absent is a dangerous silent 12x overcharge default.
4. Migration A's blind `SET is_active = TRUE` should be a guarded `WHERE is_active = FALSE` + row-count notice.
5. Deleting the dead `overrides_json.is_active` key needs a pre-check for rows where the JSON value disagrees with the dedicated column (forensic evidence of a past bug).
6. **CRITICAL:** the SlideOver rewrite + PATCH's full-JSON-replace semantics will silently destroy other `overrides_json` keys (`component_class`, `flat_amount`) unless changed to merge-preserve — recurrence of the logged incident in `project_overrides_json_silent_destruction` memory.
7. No Pydantic validation on `monthly_amount` at the PATCH boundary — malformed input fails deep inside a payroll run as an opaque Decimal error.
8. Story 2's "documented limitation" framing (full-month BASIC for mid-month hires) is wrong — the executor already has a `prorate_on_hire: true` opt-in that correctly single-applies; should be used, not documented around.
9. Test blast radius (existing CI assertions over January periods) not assessed.

**Open questions:** cadence-absent default, rename `monthly_amount` -> `annual_amount` now or defer, PATCH validation shape, whether to re-enable D-ARCH-2, prorate_on_hire adoption.

**Verdict:** NEEDS REVISION.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRINCIPAL ENGINEER REVIEW (reconstructed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Where the architect was right:** the overrides_json destruction risk, the MONTHLY default danger, the prorate_on_hire correction.

**Where I disagree / see more risk:**
- "Rename `monthly_amount` -> `annual_amount` is free" is wrong — 5 read-sites plus `metadata_json.engine_behavior.workspace_override_key` depend on the literal key name; a coordinated multi-file change, not a rename.
- The proposed "first paid month" fix (`MIN(contract.start_date)`) doesn't hold under retry — `employee_contract_snapshot` only stores the run-period contract's dates, not earliest-ever. Reuse `per_employee_context_json` (the existing mechanism for `is_union_member`) instead of new contract-loading.
- Disagree with "fail loud" on cadence-absent — default should be ANNUAL, not an exception; fail-loud is disproportionate for a config gap with a safe default.

**What the architect missed (new findings):**
- **Deploy-order hazard:** the levy-reading code already runs in production every period. If Migrations A+B ship before the cadence-gate code, every run in the gap window deducts ₦100 every month against live payroll.
- **2026 arrears unaddressed, makes the plan's own AC unachievable:** January 2026 is already closed. Under "period contains January 1," no future 2026 period will ever satisfy the January branch for the existing 184 employees — the AC "reconciliation diff -> 0 for all 184" cannot be met by the cadence gate alone. Needs an explicit remediation/correction-run decision.
- **Residual missed case:** an employee INACTIVE in January (valid HR state) and reactivated later never gets charged that year under either trigger as currently scoped.
- Story 2's hardcoded `base_components: ["BASIC"]` will silently compute ₦0 while marking "applied" for any workspace whose basic component isn't literally coded `BASIC` — this repo already supports configurable base components elsewhere (NHF). Needs save-time validation.
- `test_statutory_flat_amount_keys_e2e.py` posts a run with no period (defaults to wall-clock month) — becomes flaky/month-sensitive under annual gating; needs pinning this sprint.
- Simulation scripts thread `development_levy_amount` and will silently diverge from the new cadence behavior unless updated.

**Stress test:** the architect's fixes solve the mechanics but not the two business-level gaps (arrears, INACTIVE residual) — those are missing PM decisions, not code defects.

**Verdict:** CONCUR WITH ADDITIONS.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COUNCIL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Combined verdict: NEEDS REVISION**

**Ranked, must-fix before implementation:**
1. **CRITICAL** — `overrides_json` PATCH must merge, not replace.
2. **CRITICAL** — cadence-gate code must deploy before migrations A/B, or live runs overcharge 12x in the gap window.
3. **HIGH** — cadence-absent default -> ANNUAL, not MONTHLY.
4. **HIGH** — 2026 arrears: plan's own AC is unachievable as scoped without a remediation decision (DEC pending).
5. **HIGH** — "first paid month" signal -> use `per_employee_context_json`, not contract `MIN(start_date)`.
6. **MEDIUM** — PATCH needs Pydantic validation on `monthly_amount`.
7. **MEDIUM** — Story 2: validate `BASIC` exists in workspace's base components at save time.
8. **MEDIUM** — adopt `prorate_on_hire: true` for the percentage rule rather than accepting overpayment.
9. **LOW** — pin `test_statutory_flat_amount_keys_e2e.py`'s period; audit simulation scripts; tighten Migration A; docstring Migration B against the named statute; don't bump `rules_jsonb.version`.

**Note post-DEC-04:** item 3 in the architect's original concern list ("cadence gate double-charges") is resolved as *intended behavior*, not a defect — Michael confirmed a Dec-hire is correctly charged in both Dec and the following Jan (DEC-dev-levy-rule-pct-04, `decisions.md`). The plan revision should keep the OR logic as originally drafted and instead tighten the guard to "don't double-fire the *same* trigger within one period" (e.g. a fortnightly period straddling a month boundary), not "don't let both triggers fire close together."

**Open questions requiring a human decision** (tracked in `CONTEXT.md`, not yet answered):
1. 2026 arrears — correction run for the 184 employees, or accept the gap and fix forward only?
2. INACTIVE-in-January residual case — accept as edge case, or add explicit handling?
3. Rename `monthly_amount` -> `annual_amount` this sprint, or defer?
4. Explicit `override = 0` semantics — should a workspace be able to zero out the levy?
