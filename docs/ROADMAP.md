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
| **Phase 1 — Sprints 1–6** | 4✅ | 2✅ | 8✅ | 6✅ | 6✅ | 6✅ |
| **Phase 2 — Sprints 7–8** | 17✅ 2⚠️ 1🔜 2⬜ | — | 18✅ | 1⚠️ | 4✅ | 4✅ 2⬜ |
| **Phase 2 — Client B Sprint 10+** | 6✅ 2⬜ (Tracks L+O) | — | 4✅ 3✅ 3⬜ 2🔜 1🔮 (Tracks K+M+N+O) | — | — | 1⬜ (Track N) |
| **Sprint 13** | — | — | 3✅ (M3/M4/M5) | — | — | 3✅ (S1/S2/S3) |
| **Sprint 14** | 1✅ (WorkspaceConfig P2 fix) | — | 1✅ (hire proration P1 — N2-partial resolved) | — | — | — |
| **Track S — Security** | — | — | — | — | — | 3✅ (SEC-S1/S2/S3 shipped Sprint 13) |
| **Track Q — Audit Observations** | — | — | 3🔜 (AUD-1 trace gap, AUD-2 period_type on retry, AUD-3 simulate script) | — | — | — |
| **Track UI — Design System** | Gate 1✅ Gate 2✅ Gate 3✅ Gate 4✅ Gate 5✅ Gate 6✅ | — | — | — | — | — |
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
- Define payroll rules — standalone form, not raw JSON textarea ✅ (P3-1)

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
- Export net pay for bank upload ✅ (P0-3)
- Export PAYE remittance schedule ✅ (P1-4)
- Export full payroll detail ✅

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
- Configure pay cycle post-setup — update endpoint ✅ (WC-1, Track J)
- View applicable statutory rules — read endpoint + UI ⬜ (P3-2)
- Statutory rule management UI for bureau ⬜ (P3-2)
- Configure WorkspacePayrollConfig (ph_mode, weekend PH rules, D3/D4 flags, effective_from versioned rows) ✅ (PH-6) ← arch-council: effective_from required
- Seed rate_code_registry with platform OT codes (OT001–OT007) — no is_pensionable column ✅ (PH-7) ← arch-council: pension via component_metadata not registry
- Rate code registry — read endpoint + UI view ✅ (PH-7)
- Seed component_metadata row for PH_OT with is_pensionable=true ⚠️ (PH-7/OQ1) — row seeded; is_pensionable flag intentionally deferred until PH_OT handler ships atomically
- PH-1: National public holiday calendar (NationalPublicHoliday table, seeded for NGA) ✅ (PH-1)
- PH-1: Workspace-specific PH additions (WorkspacePublicHoliday table) ✅ (PH-1)
- PH-1: PH snapshot at run approval (source-tagged, immutable) ✅ (PH-1)
- PH-2b: Weekend PH classification config (saturday_ph_rule, sunday_ph_rule) ✅ (PH-2b)

**A2 — Workforce**
- Define payroll rules — standalone form ✅ (WC-9, Track J)
- Add grade / designation post-onboarding via UI ✅ (WC-2/WC-4, Track J)
- Edit grade / designation description via UI ✅ (WC-3/WC-5, Track J)
- Add new salary definition via UI ✅ (WC-6, Track J)
- Edit salary definition components via UI (amounts, add/remove) ✅ (WC-7, Track J)
- Toggle payroll rule active/inactive via UI ✅ (WC-8, Track J)
- Edit/toggle statutory component override via UI ✅ (WC-10/WC-11, Track J)
- Enforce salary definition effective dates at run time ✅ (P3-5) — already done
- Onboard ot_multiplier payroll rules via Excel/JSON (rate_code field) ✅ (PH-8/WI-05)
- Onboard Client 3 shift allowance rules (basic_daily base) 🔜 (PH-12)

### Execution (A4)

**── Mandatory defect fixes (FIX-1 to FIX-5) — must land before any PH/OT feature ──**
- FIX-1: Fix cross-period prefetch dead code — isinstance guard for list inputs ✅ (prerequisite for PH_OT cross-period inputs)
- FIX-2: Align NHF key to employee_rate in retry service + simulate_payroll ✅ (silent financial error on retried runs)
- FIX-3: Fix health/dev levy extraction key in route + retry service ✅ (P1-2/P1-3)
- FIX-4: tax_bands float → Decimal at extraction ✅ (amplified by OT→PAYE path)
- Fix rent_relief rate "TBD" in DB seed ✅ (P0-6)
- Fix _resolve_inputs type mismatch bug (reads dict, receives list) ✅ (live defect)
- Add quantity ≥ 0 DB CHECK constraint on payroll_input ✅ (INP10)

**── PH/OT engine (Track B schema first, then Track C execution) ──**
- absent_days bounds check (absent_days ≤ working_days) ✅ — already done (P2-5)
- PH-2: expected_hours computed from PH-adjusted working days ✅ (PH-2)
- PH-3: OT3 calculation at 3.25× basic_hourly for PH hours worked ✅ (PH-3) — classify_day defined; ot_multiplier handler reads hours from inputs; note: classify_day has no call site yet (dead code)
- PH-4: OT3 flows into GROSS_PAY and PAYE base ✅ (PH-4)
- PH-5: Manual OT3 hour adjustment with floor validation ✅ (PH-5)
- Compute expected_days in execution context (PH-aware, separate from expected_hours) ✅ (PH-9)
- ot_multiplier in apply_payroll_rules — Model A: extend signature with expected_hours/expected_days/proration_factor/rate_code_map kwargs ✅ (PH-8) ← arch-council decision
- Snapshot expected_days + ph_dates_used in run trace header ✅ (PH-9)
- FIX-5: Retry context — expected_hours/expected_days/ph_dates_used/ph_source from snapshot ✅ (retry determinism)
- PH pre-flight check for AUTOMATIC mode runs ✅ (PH-11)
- PH count mismatch and duplicate warnings in execution trace ✅ (PH-10)

### Governance (A5)

- Real user identity in performed_by — frontend sends X-Performed-By header ⚠️ (P2-2) — backend reads header on approve/lock/retry routes; frontend does not send it yet (defaults to "admin@internal")

### Disbursement (A6)

- Export net pay for bank upload — route + UI download button ✅ (P0-3)
- Export PAYE remittance schedule — route + UI ✅ (P1-4)
- Export pension contribution schedule — route + UI ✅ (P1-5)
- Export full payroll detail — route + UI ✅

### Correctness & Audit (A10)

- Expose snapshot content with structured UI renderer ⬜
- Replay a run using frozen snapshot ⬜ (P4-2) — may move to Phase 3
- Extend run trace header: expected_days, ph_dates_used, ph_source ✅ (PH-9)
- build_runtime_component_registry: include ot_multiplier-computed components in GROSS_PAY chain ✅ (PH-8)

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
| 8 | PH-6: WorkspacePayrollConfig + effective_from + versioned-row select ✅ | Onboarding (A1) | PH-6 | Prerequisite for PH-2, PH-3, PH-8, PH-9 |
| 9 | PH-7: rate_code_registry (no is_pensionable) + platform seeds ✅ | Onboarding (A1) | PH-7 | Prerequisite for PH-8, PH-12 |
| 10 | PH-7: Seed component_metadata row for PH_OT (is_pensionable=true) ⚠️ | Onboarding (A1) | PH-7/OQ1 | Row seeded; is_pensionable flag deferred until PH_OT handler ships atomically |
| 11 | PH-1: NationalPublicHoliday + WorkspacePublicHoliday + NGA 2026 seed ✅ | Onboarding (A1) | PH-1 | Prerequisite for PH-2, PH-9, PH-10, PH-11 |
| 12 | PH-2b: Weekend PH classification config (saturday/sunday_ph_rule) ✅ | Onboarding (A1) | PH-2b | Prerequisite for PH-3 |

### Track C — Execution Engine (after all of Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 13 | PH-2: expected_hours in context (PH-adjusted working days) ✅ | Execution (A4) | PH-2 | |
| 14 | PH-9: expected_days in context + ph_dates_used snapshot ✅ | Execution (A4) | PH-9 | |
| 15 | PH-8: ot_multiplier — Model A: extend apply_payroll_rules signature ✅ | Execution (A4) | PH-8 | **Model A confirmed by arch-council** |
| 16 | PH-8: build_runtime_component_registry includes ot_multiplier ✅ | Correctness (A10) | PH-8 | Atomic with #15 |
| 17 | FIX-5: Retry context — add OT/PH keys from snapshot (same release as #13–16) ✅ | Execution (A4) | FIX-5 | **Must ship with Track C** |
| 18 | PH-3: OT3 calculation (classify_day + PH_OT handler) ✅ | Execution (A4) | PH-3 | classify_day defined; no call site yet |
| 19 | PH-4: OT3 → GROSS_PAY + PAYE ✅ | Execution (A4) | PH-4 | Tax compliance |
| 20 | PH-5: Manual OT3 adjustment with floor validation ✅ | Execution (A4) | PH-5 | |

### Track D — Warnings & Pre-flight (after Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 21 | PH-10: PH count mismatch + duplicate warnings in trace ✅ | Execution (A4) | PH-10 | |
| 22 | PH-11: PH pre-flight check (AUTOMATIC mode, empty calendar) ✅ | Execution (A4) | PH-11 | |

### Track E — Client 3 Onboarding (after Track C)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 23 | PH-12: Client 3 shift allowance — SHIFT2/SHIFT3/SHIFT4 (basic_daily) | Onboarding (A2) | PH-12 | |

### Track F — API Routes (after Track B)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 24 | WorkspacePayrollConfig GET + PUT ✅ | Onboarding (A1) | PH-6 | |
| 25 | rate_code_registry GET + POST + DELETE ✅ | Onboarding (A1) | PH-7 | |
| 26 | public-holidays GET + POST + DELETE ✅ | Onboarding (A1) | PH-1 | |

### Track G — Frontend (after Track F)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 27 | WorkspaceSetup: Payroll Behaviour section (PH-6) ✅ | Onboarding (A1) | PH-6 | |
| 28 | WorkspaceSetup: Rate Code Registry section (PH-7) ✅ | Onboarding (A1) | PH-7 | |
| 29 | Public Holidays page (new page + sidebar nav) ✅ | Onboarding (A1) | PH-1 | |
| 30 | PayrollResults: PH warning banner (PH-10) ✅ | Execution (A4) | PH-10 | |
| 31 | Execution Timeline: warn state amber rendering (PH-10) ✅ | Execution (A4) | PH-10 | |

### Track H — Exports (independent, run parallel with C+)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 32 | Export net pay for bank upload | Disbursement (A6) | P0-3 | ✅ Sprint 10 |
| 33 | Export PAYE remittance schedule | Disbursement (A6) | P1-4 | ✅ Sprint 10 |
| 34 | Export pension contribution schedule | Disbursement (A6) | P1-5 | ✅ Sprint 10 |

### Track I — Governance (independent)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 35 | Real user identity in performed_by (X-Performed-By header) ⚠️ | Governance (A5) | P2-2 | Backend reads header; frontend doesn't send it yet |

### Track J — Post-Onboarding Config Management (independent, parallel with H+)

Arch-council reviewed April 2026. 8 binding decisions (D-ARCH-1 through D-ARCH-8).
Stories: `docs/stories/track-j-workspace-config-management.md`
UX/UI: `docs/ux-design-brief/gate-6/`

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| 36 | Migration: add `is_active` + `proration_strategy` to `client_component_metadata` | Onboarding (A1) | WC-10/D-ARCH-4 | **BLOCKER — must land first** |
| 37 | PATCH `/{wid}/pay-cycle` — update active pay cycle with run-state + frequency guards | Onboarding (A1) | WC-1 | D-ARCH-6/7 |
| 38 | PATCH `/{wid}/grade/{code}` + PATCH `/{wid}/designation/{code}` — update description | Onboarding (A2) | WC-3/WC-5 | |
| 39 | PATCH `/{wid}/salary-definition/{id}` — update components_jsonb with edit-lock | Onboarding (A2) | WC-7 | D-ARCH-1/5 critical |
| 40 | PATCH `/{wid}/payroll-rule/{id}` — toggle is_active, update definition | Onboarding (A2) | WC-8/WC-9 | |
| 41 | Statutory component hard reject on component-override PATCH | Onboarding (A1) | WC-10/D-ARCH-2 | 422 for statutory_deduction class |
| 42 | Extend GET `/{wid}/configuration` — add IDs, is_active, proration_strategy | Onboarding (A1) | All WC | Needed by frontend |
| 43 | Frontend: WorkspaceConfig.tsx full interactive overhaul (Gate 6) | Onboarding (A1+A2) | WC-1→WC-11 | See Gate 6 in UI track |

> **Arch-council gate:** Tracks B, C, and E introduce migrations and data contracts. Do not begin Track B without `/arch-council` sign-off (completed April 2026 — decisions recorded in `docs/stories/arch-council-sprint7-decisions.md` and `~/.claude/plans/peaceful-purring-starlight.md`).
> Track A fixes are pre-approved — no gate needed.

---

### Track S — Security (rolling register; no arch-council gate)

Findings are logged here as they are identified by `/security` reviews. Full narrative for each sprint lives in `docs/security/`. No finding is discarded — closed items are marked ✅.

| # | Item | Severity | File | Ref | Sprint Found | Status |
|---|------|----------|------|-----|--------------|--------|
| S1 | Replace raw `_wpc_err!s` exception string in `warnings` response with a generic message; log internally | Medium | `backend/api/routes/onboarding.py:589` | SEC-S1 | Sprint 13 | ✅ |
| S2 | Add application-level allowlist validation for `workspace_payroll_config` enum fields before DB upsert | Low | `backend/api/routes/onboarding.py:575–586` | SEC-S2 | Sprint 13 | ✅ |
| S3 | Move `import logging` to module level in `payroll.py`; replace inline `_logging.getLogger` call | Low | `backend/api/routes/payroll.py:498` | SEC-S3 | Sprint 13 | ✅ |
| S4 | Grade query in `/run-payroll` route hardened with `workspace_id` filter to prevent cross-workspace grade leakage ✅ | Low | `backend/api/routes/payroll.py` | SEC-S4 | Sprint 11 | ✅ |
| S5 | `shift_type`, `state_of_tax`, `skill_level` onboarding endpoint: enum allowlist validation + VARCHAR length guards added ✅ | Low | `backend/api/routes/onboarding.py` | SEC-S5 | Sprint 11 | ✅ |

> **Policy:** Security findings are batched into the next sprint unless severity is Critical or High, in which case they block sprint closure. Full review narratives: `docs/security/`.

---

### Track Q — Audit Observations (rolling register; no arch-council gate)

Observations are logged here as they are identified by `/auditor` reviews. Full narrative for each sprint lives in `docs/audit/`. Observations do not block sprint closure but must be addressed before external audit or UAT sign-off. Closed items are marked ✅.

| # | Item | Type | File | Ref | Sprint Found | Status |
|---|------|------|------|-----|--------------|--------|
| Q1 | Add `"component_source"` field to `fixed_amount` trace entry when fallback fires — derivation path must be auditable | Observation | `backend/domain/payroll/rule_evaluator.py:327–338` | AUD-1 | Sprint 10 | 🔜 |
| Q2 | Store `period_type` on `payroll_run` row; pass to `build_period_context` on retry — CUSTOM runs must reproduce with correct annualization | Observation | `backend/application/payroll_retry_service.py:147–151` (migration required) | AUD-2 | Sprint 10 | 🔜 |
| Q3 | Simulate script: replace raw `dict(b)` tax band mapping with explicit `Decimal(str(...))` conversion to match production path | Observation | `scripts/simulate_payroll_components.py:508` | AUD-3 | Sprint 10 | 🔜 |
| Q4 | `salary_basis` + `shift_type` added as named fields in `_period_context` trace header in `sequential_executor.py` — per-employee context that gates calculations is now auditable ✅ | Resolved | `backend/domain/payroll/sequential_executor.py` | AUD-4 | Sprint 11 | ✅ |

> **Policy:** Observations are batched into the next available sprint. Any Observation rated "must fix before UAT/external audit" is escalated to Finding status and blocks the relevant sign-off gate. Full review narratives: `docs/audit/`.

---

### Track K — Client B Engine Defect Fixes (Sprint 9, Track A class — no arch-council gate)

Identified during Client B gap audit (2026-04-30). These are pre-approved defect fixes with no migration or data-contract change.

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| K1 | GAP-2-FIX: Remove double-subtraction of PH days in AUTOMATIC mode (`payroll.py:505`) ✅ | Execution (A4) | GAP-2 | Sprint 10 (CB-1) |
| K2 | GAP-5-FIX: PAYE CUSTOM annualization → ×12 (`period_context.py:211–216`) ✅ | Execution (A4) | GAP-5 | Sprint 10 (CB-2) |
| K3 | WI-04 Sub-A: `component_source` in `fixed_amount` handler (`rule_evaluator.py:316`) — ₦0 fix for salary-referenced rules ✅ | Execution (A4) | WI-04a | Sprint 10 (CB-7) |

---

### Track L — Client B Onboarding & Rate Code Foundations (Sprint 9, Track B class)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| L1 | WI-01: OT multiplier seed correction — guarded `UPDATE rate_code_registry`: OT001→1.5×, OT002→2.0×, OT003→3.25× ✅ | Onboarding (A1) | WI-01 | Seeds already correct; no migration needed (confirmed Sprint 12 session) |
| L2 | WI-02: `ot_code`→`rate_code` normalisation — defensive read in Excel parser + remove dead fallback in WorkspaceConfig.tsx ✅ | Onboarding (A2) | WI-02 | Parser silently maps legacy `ot_code` → `rate_code`; WorkspaceConfig.tsx fallback removed (Sprint 12 session) |
| L3 | WI-05: Excel `ot_multiplier` rule-type parsing — `'ot multiplier': 'ot_multiplier'` in `RULE_TYPE_MAP`; `rate_code` in `rule_definition_json` ✅ | Onboarding (A2) | WI-05 | Sprint 10 (CB-10) |
| L4 | WI-06/H2: `workspace_payroll_config` onboarding integration — optional 7th Excel sheet; seed `ph_mode=FILE_BASED` default if absent ✅ | Onboarding (A1) | WI-06 | Sprint 10 (CB-11) |
| L5 | VERIFY-PH-ADDITIVE: PH_ADDITIVE removed from UI; backend graceful fallback to LEAVE_ABSORBS_PH with WARN log ✅ | Onboarding (A1) | WI-12 | Sprint 10 (CB-12) |
| L6 | VERIFY-API-COVERAGE: `rate_code_registry` + `public-holidays` GET/POST/DELETE confirmed live ✅ | Onboarding (A1) | WI-35 | Sprint 10 |

---

### Track M — Statutory Deduction Completeness (arch-council joint review required before any implementation)

Run a **single arch-council session covering NEW-GAP14 + NEW-GAP15 together** before writing any code — they share the executor GROSS_PAY / TAXABLE_INCOME data-contract surface.

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| M1 | NEW-GAP14: Non-taxable component class — `component_class='non_taxable'`; exclude from `_handle_sum_earnings` (GROSS_PAY); include in net-pay total but not TAXABLE_INCOME ✅ | Execution (A4) | NEW-GAP14 | Sprint 12 — arch-council reviewed; migrations applied |
| M2 | NEW-GAP15: PAYE-only additions path — `payroll_input.input_category VARCHAR(20) DEFAULT 'standard'`; executor aggregates `paye_only` rows into TAXABLE_INCOME only ✅ | Execution (A4) | NEW-GAP15 | Sprint 12 — arch-council reviewed; migrations applied |
| M3 | NEW-GAP6: Check-off dues handler — `2% × (BASIC + HOUSING + TRANSPORT)`, `component_class='statutory_deduction'`; seed `component_metadata` row ✅ | Execution (A4) | NEW-GAP6 | Sprint 13 — `percentage_of_sum` calculation method; is_union_member eligibility gate |
| M4 | GAP-10-FIX: Life insurance flat ₦2,000 — change `rate × GROSS_PAY` to flat-amount pattern; seed `employer_amount=2000` in `rules_jsonb` ✅ | Execution (A4) | GAP-10 | Sprint 13 — flat-amount handler with DEPRECATION fallback for rate-based clients |
| M5 | NEW-GAP7: NSITF/ITF employer cost handlers — `1% × (BASIC + HOUSING + TRANSPORT)` each; `component_class='employer_cost'`; no employee net-pay deduction ✅ | Execution (A4) | NEW-GAP7 | Sprint 13 — ITF threshold gate (≥5 employees AND ≥₦50M annual payroll) |

---

### Track N — Proration Audit Trail & Proration Fix (arch-council gate)

WI-08 must land before WI-03 can be safely implemented. WI-03 remains blocked until the client confirms the proration ordering model.

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| N1 | WI-08: Merge `_rule_trace` from `apply_payroll_rules()` into `component_trace_jsonb` (currently discarded unconditionally); add `rate_basis` field to each trace entry ⬜ | Correctness (A10) | WI-08 | **Arch-council required** — extends `component_trace_jsonb` schema contract; downstream: UI renderer + retry snapshot reader |
| N2 | WI-03: Proration factor fix — `ot_multiplier` + `daily_rate_deduction` to reconstruct full BASIC as rate base (**PARTIALLY ADDRESSED**) 🔜 | Execution (A4) | WI-03 | Ordering fix (hire proration moved after `apply_payroll_rules`) lands in Sprint 14 — resolves `daily_rate_deduction` rate-base issue. `ot_multiplier` rate-base reconstruction is separate story if still needed. |

---

### Track O — Employee Schema & Complex Features (later Phase 2 sprint; arch-council per item)

All items require arch-council pre-clearance before implementation begins. Entry gate: all of Tracks K–N complete.

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| O1 | NEW-GAP4 + NEW-GAP13: Employee payroll-critical fields — `shift_type`, `state_of_tax`, `skill_level` columns; migration `f1e2d3c4b5a6`; API GET/PATCH wired; onboarding validation + length guards ✅ | Onboarding (A2) | NEW-GAP4/13 | Sprint 11 |
| O2 | NEW-GAP12: Grade percentage structure — `total_monthly`, `basic_pct`, `housing_pct`, `transport_pct`, `utility_pct` on `grade` table; migration `a2b3c4d5e6f7`; `salary_derivation.py` pure function; grade pct wins when `total_monthly` non-null (D6); round-half-up + residual (D7) ✅ | Onboarding (A2) | NEW-GAP12 | Sprint 11 |
| O3 | WI-04 Sub-B + NEW-GAP8: Shift gate in `rule_evaluator.py` — D9 decision: `basic_daily ot_multiplier` returns ₦0 for `shift_type` in (None, "DAY"); `shift_type` threaded per employee in `batch_processor.py` ✅ | Execution (A4) | WI-04b | Sprint 11 |
| O4 | SHIFT-ALLOWANCE-CLIENT3: Extend shift allowance for `basic_daily` rate base; SHIFT2/SHIFT3/SHIFT4 rate code seeding migration ⬜ | Execution (A4) | WI-34 | Deferred — needs stable Client 3 workspace identifier before seeding migration can run |
| O5 | NEW-GAP11: LTA anniversary trigger — `AnniversaryService` auto-injects `payroll_input` (category=`paye_only`) for employees where `date_engaged` anniversary falls in pay period; configurable LTA amount ⬜ | Execution (A4) | NEW-GAP11 | Deferred to Sprint 12 (D10); blocked on M2 (PAYE-only additions path must land first) |
| O6 | NEW-GAP1: Timesheet / Attendance Layer — `timesheet_entry` table; derivation pipeline auto-populates configurable OT/PH inputs at run-claim time (not hardcoded OT1/OT2/OT3 codes) 🔄 Sprint 16 in progress | Pay Events (A3) | NEW-GAP1 | Sprint 15 design sprint (arch-council locked AC-1–AC-10, C1, C2); Sprint 16 implementation: migrations MIG-D/E/A/B/C applied; timesheet derivation service + routes + frontend complete |

---

### Track UI — UX/UI Design System & Screen Assembly

Three-gate delivery. Skills active throughout: `/ui-designer`, `/ux-designer`.

| Gate | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| **Gate 1** | UX/UI Design Brief — IA, flows, wireframes, 18 design decisions, 45-component inventory (`docs/ux-design-brief/gate-1/`) | ✅ | Completed April 2026 |
| **Gate 2** | Design System — `frontend/src/design-system/` — `tokens.css` (Tailwind v4 `@theme` + `:root`) + 45 React components across 7 files | ✅ | Completed April 2026 |
| **Gate 3** | Adaeze's payroll operator journey — 6 screens migrated to design system (PayrollInputs, BulkUpload, PayrollRuns, RunPayroll, PayrollResults with 4-tab DD-2, Reconciliation redirect) + 6 amendments applied (Lock button bug, Inbox link, error hint, poll-failure banner, date guard, 409 copy) | ✅ | Completed April 2026 |
| **Gate 4** | Bureau / workspace setup journey — 8 pages migrated (BureauDashboard + NewClient SlideOver, WorkspaceDashboard, WorkspaceSetup shell, Employees, WorkspaceConfig, PublicHolidays, JsonOnboarding deleted, router cleaned) | ✅ | Completed April 2026 |
| **Gate 5** | Navigation modernisation + workspace context + Rate Codes page | ✅ | Completed (TopBar+Sidebar in MainLayout, Breadcrumb across pages, RateCodes.tsx wired in router) |
| **Gate 6** | Post-Onboarding Config Management — WorkspaceConfig.tsx interactive overhaul (WC-1→WC-11, Track J) | ✅ | Completed (all SlideOvers: AddGrade, EditGrade, AddDesignation, EditDesignation, EditSalaryDef, EditPayrollRule, EditPayrollConfig, AddRateCode) |

**Gate 5 — Sprint 8 scope**

| Story | What | Status |
|-------|------|--------|
| **UI-NAV-1** | Wire `TopBar` + `WorkspaceSidebar` (design system NAV-1/NAV-2) into `MainLayout` — replaces legacy `Sidebar.tsx`. Workspace name + status visible in sidebar header. TopBar workspace picker for quick switching. Collapse toggle. | ✅ |
| **UI-NAV-2** | Breadcrumb (NAV-3) on all 8 workspace pages via `ContentHeader` `back` prop — `Bureau Dashboard / [Client Name] / [Section]`. Powered by `WorkspaceContext` React context in `MainLayout`. | ✅ |
| **UI-NAV-3** | Rate Code Registry page (`/workspaces/:id/rate-codes`) — Platform codes read-only, workspace codes CRUD. Exposes OT/PH/Shift multipliers (PH-7 UI). Backend API complete (Track F ✅). | ✅ |

PM story for UI-NAV-3:
```
As a payroll operator,
I want a dedicated Rate Codes page to view platform codes and manage
workspace-specific codes for overtime, public holidays, and shift allowances,
So that I understand and control how special pay types are calculated without
navigating through the setup wizard.
```

---

**Gate 4 — Pages Remaining**

| # | Page | File | Priority |
|---|------|------|----------|
| UI-1 | Bureau Dashboard | `BureauDashboard.tsx` | High |
| UI-2 | Workspace Dashboard | `WorkspaceDashboard.tsx` | High |
| UI-3 | Workspace Setup (onboarding wizard) | `WorkspaceSetup.tsx` | High |
| UI-4 | Employees list | `Employees.tsx` | Medium |
| UI-5 | JSON Onboarding | `JsonOnboarding.tsx` | Medium |
| UI-6 | Workspace Config | `WorkspaceConfig.tsx` | Medium |
| UI-7 | Public Holidays | `PublicHolidays.tsx` | Medium |

**Design decisions carried into Gate 4 (from Gate 1 brief, all 18 must be honoured):**
- DD-1: PageShell wraps every page (TopBar + WorkspaceSidebar)
- DD-5: Every list page has an empty state with a specific CTA
- DD-12: StatusBadge — dot + text, never colour alone
- DD-14: 8pt grid — all spacing multiples of 4/8px
- DD-15: WCAG AA — all status colours use `bg-*-100 text-*-800` (≥7:1 contrast)
- Full list in `docs/ux-design-brief/gate-1/04-design-decisions.md`

---

## Sprint 14 — Workspace-Configurable Hire Proration

**Sprint goal:** Make mid-period hire and termination proration respect the per-component `proration_strategy` already configured by each workspace (`work_days`, `calendar_days`, `fixed_30`). Fix the sequencing bug that causes hire proration to corrupt the rate base for absence deductions. Introduce structured per-component proration entries in `component_trace_jsonb`. Fix the WorkspaceConfig UI overwrite bug that silently resets `proration_strategy` on save.

**Arch-council:** ✅ APPROVED WITH CONDITIONS — session 2026-05-05. All conditions resolved.

**Story file:** `docs/stories/sprint-14-hire-proration-configurable.md`

**Roadmap refs:** Track N (N2 partial), Track UI (WorkspaceConfig bug)

---

### Story Index

| Story | Summary | Priority | Effort | Gate |
|-------|---------|----------|--------|------|
| P1 ✅ | Workspace-configurable hire proration — strategy-aware `compute_hire_termination_factor`, ordering fix, per-component loop, trace entries | P1 | M | Arch-council ✅ |
| P2 ✅ | WorkspaceConfig second edit-form `proration_strategy` default overwrite fix | P2 | XS | None |

---

### Explicitly Out of Scope (Sprint 14)

| Item | Ref | Reason |
|------|-----|--------|
| N1 — Merge `_rule_trace` into `component_trace_jsonb` | N1 | Separate arch-council gate |
| `ot_multiplier` rate-base reconstruction | N2 remainder | Self-prorating via input quantity; separate story if needed |
| Retroactive re-calculation of existing runs | — | Runs are immutable once persisted |
| Workspace-level global `proration_strategy` default | — | Per-component is correct granularity; global default is a future enhancement |

---

## Known Test Failures (Pre-existing — Live State as of Sprint 14, 2026-05-10)

Table updated each sprint by `/tester`. Confirmed pre-existing via `git stash` before recording.

| # | Test | File | Root Cause | Fix Needed | Linked Item | Status |
|---|------|------|------------|------------|-------------|--------|
| TF-1 | `test_paid_transition_writes_audit_entry` | `tests/test_payroll_paid_lifecycle.py:418` | Test sent `actor_id` in body; endpoint now reads `X-Performed-By` header | — | Track I #35 (P2-2) | ✅ RESOLVED Sprint 10 |
| TF-2 | `TestDailyRateDeduction::test_deduction_floored_at_zero` | `tests/test_rule_evaluator.py` | Test expected floor-at-zero; code now raises `ValueError` for `absent_days > working_days` | — | Execution correctness | ✅ RESOLVED Sprint 10 |
| TF-3 | `test_payroll_approval_and_lock_e2e` | `tests/test_payroll_lock_and_approval.py` | Test expects `net_pay=578273.33`; engine produces `590773.33` — diff=₦12,500 = NHF (2.5% × ₦500k basic) not deducted in test fixture workspace | Investigate NHF toggle/key in test fixture setup | F1 / SR9 area | 🔴 Open |
| TF-4 | `test_full_payroll_pipeline_e2e` | `tests/test_payroll_pipeline_e2e.py` | Same root cause as TF-3 | Same fix | F1 / SR9 area | 🔴 Open |
| TF-5 | `test_partial_payroll_run_e2e` | `tests/test_payroll_partial_run_e2e.py` | Same root cause as TF-3 | Same fix | F1 / SR9 area | 🔴 Open |
| TF-6 | `test_payroll_retry_e2e` | `tests/test_payroll_retry.py` | Same root cause as TF-3 | Same fix | F1 / SR9 area | 🔴 Open |

---

## Phase 3 — Platform Scale (Future)

Deferred until Phase 2 (including Tracks K–O) is complete and a second client is onboarded.

- Employee payslip PDF generation and distribution (P4-1)
- Snapshot replay endpoint (P4-2)
- Life insurance — full employer cost reporting (P4-3)
- Agentic workflow integration (P4-4)
- Role-based access control — no auth on any DB operation today (P4-5)
- Multi-tenant bureau scaling (P4-6)
- Automated payroll scheduling (pay cycle scheduler)
- Statutory rule management for bureau operators (manage PAYE bands, NHF rates via UI)
