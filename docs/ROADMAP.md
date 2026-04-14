# Agentic Payroll Platform — Product Roadmap

## Legend

| Icon | Meaning |
|------|---------|
| ✅ | Complete — shipped and verified in code |
| ⚠️ | Partial — logic exists, known gap |
| 🔜 | Planned — next sprint priority |
| ⬜ | Not started |
| 🔮 | Future / Phase 3 |

---

## Summary Matrix

| Phase | Onboarding (A1+A2) | Pay Events (A3) | Execution (A4) | Governance (A5) | Disbursement (A6) | Correctness & Audit (A7+A8+A9+A10) |
|-------|--------------------|-----------------|----------------|-----------------|-------------------|--------------------------------------|
| **Sprint 0 — Foundation** | 10✅ 4⚠️ 1⬜ | 6✅ | 8✅ | 10✅ | 1✅ | 11✅ 1⚠️ |
| **Phase 1 — Sprints 1–6** | 3✅ 1⬜ | 2✅ | 8✅ | 6✅ | 3✅ 3⬜ | 6✅ |
| **Phase 2 — Sprint 7+** | 9🔜 3⬜ | — | 18🔜 2✅ | 1🔜 | 4🔜 1⬜ | 2🔜 2⬜ |
| **Phase 3 — Future** | 🔮 | — | — | 🔮 | — | 🔮 |

---

## Sprint 0 — Foundation (pre-sprint)

Stories built before formal sprint tracking. Covers the core platform skeleton.

### Onboarding (A1 + A2)

**A1 — Workspace Setup**
- Create workspace ✅
- Define pay cycle ⚠️ — definition_json stored but unused in execution scheduling
- Toggle statutory components on/off ✅
- Select effective statutory rule version ✅
- View applicable statutory rules ⬜

**A2 — Workforce**
- Define salary definition ✅
- Define grades ✅
- Define designations ✅
- Publish rule set ✅
- Upload employees via onboarding ⚠️ — TIN/bank/RSA parsed but not displayed in preview
- Map salary grades to definitions ✅
- Validate onboarding payload ✅
- Preview generated SQL ✅
- Update employee contracts post-onboarding ⚠️ — only start/end dates patchable
- Transition workspace to READY ✅
- Check onboarding status/progress ✅

### Pay Events (A3)

- List valid input codes ✅
- List unclaimed inputs ✅
- Delete staged input ✅
- Download input template ✅
- Stage input against a specific past month ✅
- Stage period-agnostic input ✅
- Block future inputs from being claimed ✅

### Execution (A4)

- Claim variable inputs at run time ✅
- Prorate pay for partial-period employees ✅
- List payroll runs ✅
- View per-employee results ✅
- Execute in canonical component order ✅
- Freeze period context at run start ✅
- Decimal precision on all monetary values ✅
- Compute PAYE on taxable income, not gross ✅

### Governance (A5)

- Enforce state machine rules (DB trigger + Python) ✅
- Enforce forward-only state progression ✅
- Enforce initial run status as DRAFT ✅
- Deduplicate runs by idempotency key ✅
- Deduplicate runs by period ✅
- Deduplicate per-employee results ✅
- Retry idempotent when no failures remain ✅
- Require workspace LIVE before payroll ✅
- Validate payroll prerequisites at DB level ✅
- Validate workforce structure uniqueness ✅

### Disbursement (A6)

- View reconciliation status ✅

### Correctness & Audit (A7 + A8 + A9 + A10)

**A8 — Correctness**
- Sort tax bands before applying progressive PAYE ✅
- Freeze calculation snapshot on write ✅
- Block mutation of results once calculated ✅
- Block all writes to a PAID run ✅
- Lock salary definition used in a paid run ✅

**A9 — Temporal & Retroactive**
- Build historical period context for past months ✅
- Retry uses original run's statutory rule ✅
- Retry never re-queries live rule tables ✅
- Retry preserves original period context ✅
- Publish rule set with effective date ✅
- Automatically select rule set effective for run period ✅

**A10 — Snapshot & Reproducibility**
- Capture full rule state at run time (v2 snapshot) ✅
- Support v1 snapshot for pre-temporal runs ✅
- Inspect calculation snapshot ⚠️ — data present, no UI renderer

---

## Phase 1 — Single-Workspace Payroll (Sprints 1–6)

Formal sprint work. All Sprint 1–6 items are now closed.

### Onboarding (A1 + A2)

**A1 — Workspace Setup**
- Validate country code has statutory rules at workspace creation ✅ (P3-7)
- Component overrides update endpoint (PATCH post-onboarding) ✅ (P1-8)
- Active pay cycle guard — at most one active per workspace ✅ (PC4)

**A2 — Workforce**
- Define payroll rules — standalone form, not raw JSON textarea ⬜ (P3-1) — still open, moves to Phase 2

### Pay Events (A3)

- Add single payroll input with quantity validation (negative guard) ✅ (INP10/P3-4)
- Bulk upload inputs with deduplication guard ✅ (P3-3)

### Execution (A4)

- Run payroll with period_type, working_days_override, retry_strategy in UI ✅ (P1-7)
- Resolve historical input rates with fallback flagging in rule_trace ✅ (P2-7)
- Retry failed employees with UI button ✅ (P0-2)
- Retry recalculates run totals ✅ (P1-1)
- Retry writes to audit_log and event_store ✅ (P2-3)
- Full-run retry ✅ (P0-2)
- View execution trace / timeline ✅ (P1-6)
- NHF key fix (employee_rate) ✅ (SR9)

### Governance (A5)

- Approve payroll run — UI button ✅ (P0-1)
- Lock payroll run — UI button ✅ (P0-1)
- Mark run as paid — UI button ✅ (P0-1)
- Read run audit trail — endpoint + UI ✅ (P2-1)
- Read event store history — endpoint ✅ (P2-1)
- Statutory rule effective_from UNIQUE constraint ✅ (G7)

### Disbursement (A6)

- Submit reconciliation gated to LOCKED/PAID runs ✅ (P0-4)
- Duplicate reconciliation returns 409, not 500 ✅ (P0-5)
- Correct a MISMATCH — RESOLVED status and PATCH endpoint ✅ (RC5)
- Export net pay for bank upload ⬜ (P0-3) — still open, moves to Phase 2
- Export PAYE summary ⬜ (P1-4) — still open, moves to Phase 2
- Export full payroll register ⬜ — still open, moves to Phase 2

### Correctness & Audit (A7 + A8 + A9 + A10)

**A7 — Audit & Inspect**
- View component-level calculation trace in UI ✅ (P2-4)
- View rule trace per employee (resolution_source + warning field) ✅ (P2-7)

**A9 — Temporal**
- rule_set effective_from UNIQUE constraint ✅ (P2-6)
- Prefetch all cross-period rule sets before execution ✅
- Override rule set selection for a specific run ✅ (P1-7)
- Access multiple historical rule sets in a single run ✅

**A10 — Snapshot**
- Capture per-employee calculation steps (component_trace_jsonb) ✅ (P2-4)
- Legacy executor observability — warns when legacy path invoked, tracks metrics ✅ (G12)

---

## Phase 2 — Operational Completeness (Sprint 7+)

Open items needed to make the platform production-ready for real clients.

### Onboarding (A1 + A2)

**A1 — Workspace Setup**
- Configure pay cycle post-setup — update endpoint ⬜
- View applicable statutory rules — read endpoint + UI ⬜ (P3-2)
- Statutory rule management UI for bureau ⬜ (P3-2)
- Configure WorkspacePayrollConfig (ph_mode, weekend PH rules, D3/D4 flags, effective_from versioned rows) 🔜 (PH-6) ← arch-council: effective_from required
- Seed rate_code_registry with platform OT codes (OT001–OT007) — no is_pensionable column 🔜 (PH-7) ← arch-council: pension via component_metadata not registry
- Rate code registry — read endpoint + UI view 🔜 (PH-7)
- Seed component_metadata row for PH_OT with is_pensionable=true 🔜 (PH-7/OQ1)
- PH-1: National public holiday calendar (NationalPublicHoliday table, seeded for NGA) 🔜 (PH-1)
- PH-1: Workspace-specific PH additions (WorkspacePublicHoliday table) 🔜 (PH-1)
- PH-1: PH snapshot at run approval (source-tagged, immutable) 🔜 (PH-1)
- PH-2b: Weekend PH classification config (saturday_ph_rule, sunday_ph_rule) 🔜 (PH-2b)

**A2 — Workforce**
- Define payroll rules — standalone form ⬜ (P3-1)
- Enforce salary definition effective dates at run time ✅ (P3-5) — already done
- Onboard ot_multiplier payroll rules via Excel/JSON (rate_code field) 🔜 (PH-8)
- Onboard Client 3 shift allowance rules (basic_daily base) 🔜 (PH-12)

### Execution (A4)

**── Mandatory defect fixes (FIX-1 to FIX-5) — must land before any PH/OT feature ──**
- FIX-1: Fix cross-period prefetch dead code — payroll.py:383 isinstance guard always False for lists 🔜 (prerequisite for PH_OT cross-period inputs)
- FIX-2: Align NHF key to employee_rate in retry service + simulate_payroll (route fixed in SR9, 2 callers still wrong) 🔜 (silent financial error on retried runs)
- FIX-3: Fix health/dev levy extraction key in route + retry service (payroll.py:183–184, retry_service:176–177) 🔜 (P1-2/P1-3) ← arch-council: fix extraction layer not handler
- FIX-4: tax_bands float → Decimal at extraction (payroll.py:195–202) 🔜 (amplified by OT→PAYE path)
- Fix rent_relief rate "TBD" in DB seed — Decimal crash if ANNUAL_RENT_PAID present 🔜 (P0-6)
- Fix _resolve_inputs type mismatch bug (reads dict, receives list) 🔜 (live defect)
- Add quantity ≥ 0 DB CHECK constraint on payroll_input 🔜 (INP10)

**── PH/OT engine (Track B schema first, then Track C execution) ──**
- absent_days bounds check (absent_days ≤ working_days) ✅ — already done (P2-5)
- PH-2: expected_hours computed from PH-adjusted working days 🔜 (PH-2)
- PH-3: OT3 calculation at 3.25× basic_hourly for PH hours worked 🔜 (PH-3)
- PH-4: OT3 flows into GROSS_PAY and PAYE base 🔜 (PH-4)
- PH-5: Manual OT3 hour adjustment with floor validation 🔜 (PH-5)
- Compute expected_days in execution context (PH-aware, separate from expected_hours) 🔜 (PH-9)
- ot_multiplier in apply_payroll_rules — Model A: extend signature with expected_hours/expected_days/proration_factor/rate_code_map kwargs 🔜 (PH-8) ← arch-council decision
- Snapshot expected_days + ph_dates_used in run trace header 🔜 (PH-9)
- FIX-5: Retry context — add expected_hours/expected_days/ph_dates_used/ph_source from snapshot (must land with Track C) 🔜 (retry determinism)
- PH pre-flight check for AUTOMATIC mode runs 🔜 (PH-11)
- PH count mismatch and duplicate warnings in execution trace 🔜 (PH-10)

### Governance (A5)

- Real user identity in performed_by — frontend sends X-Performed-By header 🔜 (P2-2)

### Disbursement (A6)

- Export net pay for bank upload — wire route + UI download button 🔜 (P0-3)
- Export PAYE remittance schedule — wire route + UI 🔜 (P1-4)
- Export pension contribution schedule — wire route + UI 🔜 (P1-5)
- Export full payroll register — wire route + UI ⬜

### Correctness & Audit (A10)

- Expose snapshot content with structured UI renderer ⬜
- Replay a run using frozen snapshot ⬜ (P4-2) — may move to Phase 3
- Extend run trace header: expected_days, ph_dates_used, ph_source 🔜 (PH-9)
- build_runtime_component_registry: include ot_multiplier-computed components in GROSS_PAY chain 🔜 (PH-8)

---

## Phase 2 Priority Order

Reordered after arch-council review (April 2026). Defect fixes gate the feature tracks.

### Track A — Mandatory Defect Fixes (implement first, no PH/OT dependencies)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 1 | Fix cross-period prefetch dead code (payroll.py:383 isinstance guard) | Execution (A4) | FIX-1 | **Prerequisite for all PH_OT cross-period inputs** |
| 2 | Fix _resolve_inputs type mismatch (reads dict, receives list) | Execution (A4) | live defect | Causes silent ₦0 or AttributeError |
| 3 | Fix rent_relief "TBD" Decimal crash | Execution (A4) | P0-6 | Soft-skip when rate="TBD" |
| 4 | Align NHF key → employee_rate in retry service + simulate_payroll | Execution (A4) | FIX-2 | Route fixed in SR9; 2 callers still wrong |
| 5 | Fix health/dev levy extraction key (route + retry service) | Execution (A4) | FIX-3 / P1-2 / P1-3 | Fix extraction layer, not handler |
| 6 | tax_bands float → Decimal at extraction | Execution (A4) | FIX-4 | Must land before OT→PAYE path |

### Track B — Schema Foundations (after Track A; enables Track C)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 7 | Add quantity ≥ 0 DB CHECK constraint on payroll_input | Execution (A4) | INP10 | Prerequisite for PH-5 |
| 8 | PH-6: WorkspacePayrollConfig + effective_from + versioned-row select | Onboarding (A1) | PH-6 | Prerequisite for PH-2, PH-3, PH-8, PH-9 |
| 9 | PH-7: rate_code_registry (no is_pensionable) + platform seeds | Onboarding (A1) | PH-7 | Prerequisite for PH-8, PH-12 |
| 10 | PH-7: Seed component_metadata row for PH_OT (is_pensionable=true) | Onboarding (A1) | PH-7/OQ1 | Arch-council: pension via component_metadata |
| 11 | PH-1: NationalPublicHoliday + WorkspacePublicHoliday + NGA 2026 seed | Onboarding (A1) | PH-1 | Prerequisite for PH-2, PH-9, PH-10, PH-11 |
| 12 | PH-2b: Weekend PH classification config (saturday/sunday_ph_rule) | Onboarding (A1) | PH-2b | Prerequisite for PH-3 |

### Track C — Execution Engine (after all of Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 13 | PH-2: expected_hours in context (PH-adjusted working days) | Execution (A4) | PH-2 | |
| 14 | PH-9: expected_days in context + ph_dates_used snapshot | Execution (A4) | PH-9 | |
| 15 | PH-8: ot_multiplier — Model A: extend apply_payroll_rules signature | Execution (A4) | PH-8 | **Model A confirmed by arch-council** |
| 16 | PH-8: build_runtime_component_registry includes ot_multiplier | Correctness (A10) | PH-8 | Atomic with #15 |
| 17 | FIX-5: Retry context — add OT/PH keys from snapshot (same release as #13–16) | Execution (A4) | FIX-5 | **Must ship with Track C** |
| 18 | PH-3: OT3 calculation (classify_day + PH_OT handler) | Execution (A4) | PH-3 | |
| 19 | PH-4: OT3 → GROSS_PAY + PAYE | Execution (A4) | PH-4 | Tax compliance |
| 20 | PH-5: Manual OT3 adjustment with floor validation | Execution (A4) | PH-5 | |

### Track D — Warnings & Pre-flight (after Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 21 | PH-10: PH count mismatch + duplicate warnings in trace | Execution (A4) | PH-10 | |
| 22 | PH-11: PH pre-flight check (AUTOMATIC mode, empty calendar) | Execution (A4) | PH-11 | |

### Track E — Client 3 Onboarding (after Track C)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 23 | PH-12: Client 3 shift allowance — SHIFT2/SHIFT3/SHIFT4 (basic_daily) | Onboarding (A2) | PH-12 | |

### Track F — API Routes (after Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 24 | WorkspacePayrollConfig GET + PUT | Onboarding (A1) | PH-6 | |
| 25 | rate_code_registry GET + POST + DELETE | Onboarding (A1) | PH-7 | |
| 26 | public-holidays GET + POST + DELETE | Onboarding (A1) | PH-1 | |

### Track G — Frontend (after Track F)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 27 | WorkspaceSetup: Payroll Behaviour section (PH-6) | Onboarding (A1) | PH-6 | |
| 28 | WorkspaceSetup: Rate Code Registry section (PH-7) | Onboarding (A1) | PH-7 | |
| 29 | Public Holidays page (new page + sidebar nav) | Onboarding (A1) | PH-1 | |
| 30 | PayrollResults: PH warning banner (PH-10) | Execution (A4) | PH-10 | |
| 31 | Execution Timeline: warn state amber rendering (PH-10) | Execution (A4) | PH-10 | |

### Track H — Exports (independent, run parallel with C+)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 32 | Export net pay for bank upload | Disbursement (A6) | P0-3 | |
| 33 | Export PAYE remittance schedule | Disbursement (A6) | P1-4 | |
| 34 | Export pension contribution schedule | Disbursement (A6) | P1-5 | |

### Track I — Governance (independent)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 35 | Real user identity in performed_by (X-Performed-By header) | Governance (A5) | P2-2 | |

> **Arch-council gate:** Tracks B, C, and E introduce migrations and data contracts. Do not begin Track B without `/arch-council` sign-off (completed April 2026 — decisions recorded in `docs/stories/arch-council-sprint7-decisions.md` and `~/.claude/plans/peaceful-purring-starlight.md`).
> Track A fixes are pre-approved — no gate needed.

---

## Known Test Failures (Pre-existing — Not Caused by Sprint 7 Track A)

Logged 2026-04-13 during Sprint 7 Track A regression run. Both failures exist in the
working branch before Track A was applied. They are not caused by FIX-1 through FIX-5.

| # | Test | File | Root Cause | Fix Needed | Linked Item |
|---|------|------|------------|------------|-------------|
| TF-1 | `test_paid_transition_writes_audit_entry` | `tests/test_payroll_paid_lifecycle.py:418` | Pre-existing change to `payroll.py` migrated `pay_run` from payload-based `actor_id` to `X-Performed-By` header, but the test still sends `actor_id` in the request body | Update test to send `X-Performed-By: finance@company.com` header, or reconcile the endpoint contract | Track I #35 (P2-2) |
| TF-2 | `TestDailyRateDeduction::test_deduction_floored_at_zero` | `tests/test_rule_evaluator.py` | Pre-existing change to `rule_evaluator.py` added strict bounds check: `absent_days > working_days` now raises `ValueError` instead of flooring at zero. Test expects old floor-at-zero behaviour | Update test to assert `ValueError` is raised for `absent_days=30 > working_days=22`, OR document the floor-at-zero case as a separate test | Execution correctness — no roadmap item yet |

---

## Phase 3 — Platform Scale (Future)

Deferred until Phase 2 is complete and a second client is onboarded.

- Employee payslip PDF generation and distribution (P4-1)
- Snapshot replay endpoint (P4-2)
- Life insurance — full employer cost reporting (P4-3)
- Agentic workflow integration (P4-4)
- Role-based access control — no auth on any DB operation today (P4-5)
- Multi-tenant bureau scaling (P4-6)
- Automated payroll scheduling (pay cycle scheduler)
- Statutory rule management for bureau operators (manage PAYE bands, NHF rates via UI)
