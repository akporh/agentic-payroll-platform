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
| **Sprint 15** | — | ⬜→🔜 (timesheet layer arch-council locked) | — | — | — | — |
| **Sprint 16** | 2✅ (employee page enhancements + contract edit fix) | 7✅ (TM-1→TM-7 complete) | 2✅ (C1 per-employee expected_hours; C2 readiness gate) | — | — | 1✅ (AUD-16-3 timesheet_source trace) |
| **Sprint 17** | 6✅ (B0a–B4 employee lifecycle refactor + EMP-UX-1/UX-3/UX-4) | — | — | — | — | 2✅ (SEC-17-1 str(e) fix; SEC-17-2 max_length guard) |
| **Track S — Security** | — | — | — | — | — | 5✅ closed; 3⬜ open (S6 DB constraint, S7 upload cap, S8 pin dep) |
| **Track Q — Audit Observations** | — | — | 3🔜 open (Q1/Q2/Q3); 3✅ (Q5/Q6/Q8); 1⬜ open (Q7) | — | — | — |
| **Track UI — Design System** | Gate 1✅ Gate 2✅ Gate 3✅ Gate 4✅ Gate 5✅ Gate 6✅ | — | — | — | — | — |
| **Sprints 24–26 — Employee Lifecycle UX** | 14✅ (enrollment UX, badge, registration, status mgmt) | — | — | — | — | 2✅ |
| **Sprint 27 — Smart Native Upload** | 2✅ (EMP-NATIVE-1, INP-NATIVE-1) | 2✅ (INP-MULTI-1, PAY-RECON-1) | 1🔜 (EMP-REG-5-FIX) | — | — | — |
| **Sprint 28 — Upload Error Visibility** | 2✅ (UPLOAD-ERR-1, UPLOAD-SKIP-1) | — | — | — | — | — |
| **Fix — Workspace Activation Coverage** | 3✅ (WS-ACTIVATE-1: Config page · WS-ACTIVATE-2: PayrollRuns READY state · WS-ACTIVATE-3: Setup ExistingConfigView) | — | — | — | — | — |
| **Phase 2 — Agent Layer (Planned)** | Track P (auth) ⬜ | — | — | — | — | Tracks V/W/X/Y ⬜ |
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
| S6 | `proration_strategy` no enum validation — arbitrary string silently stored; engine falls back with no error. API guard added ✅. DB CHECK constraint still missing. | Medium→Low | `backend/api/routes/workspace.py` + migration needed | SEC-S5 (report) | Sprint 14 | ⬜ DB constraint pending |
| S7 | Add file size cap (10 MB) on timesheet upload — `openpyxl.load_workbook` loads entire file into memory; no current guard | Low | `backend/api/routes/payroll.py:1492` | SEC-S6 (report) | Sprint 16 | ⬜ |
| S8 | Pin `python-multipart==0.0.28` in `requirements.txt` (currently unpinned; safe at 0.0.28 but unguarded against future regression) | Low | `requirements.txt` | SEC-S7 (report) | Sprint 16 | ⬜ |

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
| Q5 | `timesheet_source` missing from `_period_context` trace header — auditor cannot determine from trace whether hours came from timesheet upload vs. manual entry ✅ | Resolved | `backend/domain/payroll/sequential_executor.py:718` | AUD-16-3 | Sprint 16 | ✅ |
| Q6 | Re-upload overwrites APPROVED timesheet entries without guard — evidence destruction; APPROVED status must block upsert ✅ | Finding → Resolved | `backend/application/timesheet_derivation_service.py` | AUD-16-2 | Sprint 16 | ✅ Sprint 24 |
| Q7 | No actor identity (`approved_by`) on timesheet state transitions — who approved cannot be determined from audit log | Observation | `backend/api/routes/payroll.py` (approve endpoint) + migration | AUD-16-1 | Sprint 16 | ⬜ |
| Q8 | `proration_strategy` not captured in `rules_context_snapshot` — already frozen in `client_component_metadata_snapshot` at run start; retry reads from snapshot, not live table ✅ | Resolved | `backend/application/snapshot_service.py:47–91` | AUD-14-1 | Sprint 14 | ✅ Sprint 24 (no-code close) |

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

## Known Test Failures (Pre-existing — Live State as of Sprint 18, 2026-05-31)

Table updated each sprint by `/tester`. Confirmed pre-existing via `git stash` before recording.

| # | Test | File | Root Cause | Fix Needed | Linked Item | Status |
|---|------|------|------------|------------|-------------|--------|
| TF-1 | `test_paid_transition_writes_audit_entry` | `tests/test_payroll_paid_lifecycle.py:418` | Test sent `actor_id` in body; endpoint now reads `X-Performed-By` header | — | Track I #35 (P2-2) | ✅ RESOLVED Sprint 10 |
| TF-2 | `TestDailyRateDeduction::test_deduction_floored_at_zero` | `tests/test_rule_evaluator.py` | Test expected floor-at-zero; code now raises `ValueError` for `absent_days > working_days` | — | Execution correctness | ✅ RESOLVED Sprint 10 |
| TF-3 | `test_payroll_approval_and_lock_e2e` | `tests/test_payroll_lock_and_approval.py` | Fixture `effective_from='1999-01-01'` collided with UNIQUE constraint; seed at `2026-01-01` won temporal query over fixture | Fixed Sprint 18: effective_from→`2026-04-01`; EXPECTED_NET corrected (no NHF workspace rule) | Sprint 18 | ✅ RESOLVED Sprint 18 |
| TF-4 | `test_full_payroll_pipeline_e2e` | `tests/test_payroll_pipeline_e2e.py` | Same root cause as TF-3 | Fixed Sprint 18: effective_from→`2026-02-01`; EXPECTED_NET/NHF corrected | Sprint 18 | ✅ RESOLVED Sprint 18 |
| TF-5 | `test_partial_payroll_run_e2e` | `tests/test_payroll_partial_run_e2e.py` | Same root cause as TF-3 | Fixed Sprint 18: effective_from→`2026-03-01`; EXPECTED_NET corrected | Sprint 18 | ✅ RESOLVED Sprint 18 |
| TF-6 | `test_payroll_retry_e2e` | `tests/test_payroll_retry.py` | Same root cause as TF-3; also: period_start/period_end NULL on run blocked P1-3 retry guard | Fixed Sprint 18: effective_from→`2026-02-15`; EXPECTED_NET_A/B corrected; route now persists computed period dates | Sprint 18 | ✅ RESOLVED Sprint 18 |

---

## Sprint 15 — Timesheet Layer Design Sprint

**Sprint goal:** Lock all arch-council decisions for the Sprint 16 timesheet derivation layer. No implementation code — design-only sprint.

**Sprint date:** 2026-05-12

**Deliverable:** `docs/stories/sprint-16-timesheet-layer.md` — complete story set (TM-1 through TM-7) with full acceptance criteria, three-step cap formula specification, canonical upload format schema (AC-10), and all 10 binding arch-council decisions (AC-1 through AC-10 + C1, C2 + H1–H4) resolved.

**Arch-council:** ✅ APPROVED — session 2026-05-12 (10 binding decisions). Attendance config revision ✅ APPROVED — 2026-05-13 (two-table split, template versioning, onboarding flow, `resolve_hours()` spec).

**Key decisions locked:**
- `payroll_input` IS the canonical pay instruction model — no new abstraction (AC-1)
- `timesheet_entry` stores raw grid + derivation metadata; status machine: `PENDING → DERIVED → APPROVED / FAILED` (AC-4)
- Three-step cap formula for `proration_factor` — prevents ₦10–13K overpayment per employee per period (TM-3-AC-5)
- `expected_hours` must be per-employee (from `shift_type`), not a batch scalar — C1 (live bug)
- Timesheet completeness gate in `payroll_readiness_service` before `link_inputs_to_run` — C2
- `attendance_code_config` + `attendance_policy_config` two-table architecture for workspace-configurable codes (attendance revision)
- Rate codes resolved from `ot_trigger_config` — not hardcoded (AC-3)

**Three-employee Client B validation:** gross figures verified to match client spreadsheet exactly (Jan 21–Feb 20, 4-SHIFT, 152h expected, PH = Thu 29 Jan).

---

## Sprint 16 — Timesheet Derivation Layer

**Sprint goal:** Implement the full timesheet upload, derivation, approval, and audit trail pipeline (TM-1 through TM-7) plus the attendance code configuration system. Onboard timesheet-based clients on the platform.

**Sprint date:** 2026-05-13 (start); full delivery 2026-05-26

**Arch-council:** ✅ APPROVED WITH CONDITIONS — Sprint 15 locked all decisions. All pre-conditions (H1–H4, C1, C2) resolved in this sprint.

**Story files:** `docs/stories/sprint-16-timesheet-layer.md`

**Roadmap refs:** Track O (O6 — NEW-GAP1 complete)

---

### Story Index

| Story | Summary | Status |
|-------|---------|--------|
| TM-1 | Workspace timesheet configuration (`timesheet_enabled` flag, attendance code seeding) | ✅ |
| TM-2 | Timesheet upload — row parsing, employee matching, code validation, PH header check | ✅ |
| TM-3 | Timesheet derivation pipeline — three-step cap formula, policy-driven OT classification | ✅ |
| TM-4 | Manual OT override (`source = 'MANUAL_OT'`) | ✅ |
| TM-5 | Timesheet-to-pay-instruction flow — atomic approval, readiness gate, executor hire-proration suppression | ✅ |
| TM-6 | Timesheet audit trail — per-employee derivation summary, policy snapshot, per-day grid | ✅ |
| TM-7 | Attendance code + policy workspace configuration (CRUD + immutability guards) | ✅ |
| C1 | Per-employee `expected_hours` from `shift_type` (live bug fix) | ✅ |
| C2 | Timesheet completeness gate in `payroll_readiness_service` | ✅ |

**Also shipped in Sprint 16:**
- Employee page enhancements: add single employee form, edit contract end date, start/end date columns display, contract edit silent no-op fix
- `dbbc8b8` — ended-contract employees now shown in Employees list
- FULL_RUN retry disabled; period-overlap predicates replace `CURRENT_DATE` in retry paths
- NG statutory rule + PAYE bands seeded
- AUD-16-3 (Q5) — `timesheet_source` added to `_period_context` trace header
- SEC-S5 API guard (applied); SEC-S6 upload cap (pending); SEC-S7 dep pin (pending)
- Render + Vercel deployment config (`de9fb22`)
- Post-sprint: migration revision ID conflict resolved, TypeScript build errors fixed, VITE_API_URL Vercel env var wired

**Migrations applied:** MIG-A (`timesheet_entry` + `derivation_status` enum), MIG-B (`timesheet_enabled` + `attendance_template_version`), MIG-C (standalone AUTOCOMMIT — `uq_payroll_input_unclaimed` includes `source`), MIG-D (platform template tables + v1 seed), MIG-E (`attendance_code_config` + `attendance_policy_config`)

**Test report:** `docs/test-reports/2026-05-13-sprint-16.md` — 22 code-level checks, 22 PASS. Runtime deferred to staging.

**Alembic state post-sprint:** two heads (`a2b3c4d5e6f7`, `ee5ff6aa7bb8`) — MIG-C is a standalone AUTOCOMMIT migration; two heads are expected and correct.

---

### Explicitly Out of Scope (Sprint 16)

| Item | Reason |
|------|--------|
| Executor changes for new pay types | Derivation produces `payroll_input` rows in existing format; executor unchanged |
| Attendance policy config via onboarding file | Post-onboarding config via TM-7 covers Sprint 16; Excel onboarding deferred |
| Template drift propagation admin endpoint | UI warning (TM-1-AC-7) covers the case; admin endpoint deferred |
| Retroactive re-derivation for approved runs | Runs immutable once APPROVED |
| Fuzzy employee matching | Exact `employee_number` match only |

---

## Sprint 17 — Employee Lifecycle Refactor

**Sprint goal:** Decouple employee management from the bulk-upload onboarding path. Add a proper CRUD API for employees and contracts, fix two blocking LATERAL join bugs, and wire the UI split-action row operations.

**Sprint date:** 2026-05-27

**Arch-council:** ✅ APPROVED WITH CONDITIONS — session 2026-05-27. All 6 blocking issues resolved.

**Story files:** `docs/stories/sprint-17-employee-crud.md`, `docs/stories/sprint-17-employee-ux.md`

**Roadmap refs:** Track B (employee lifecycle)

---

### Story Index

| Story | Summary | Status |
|-------|---------|--------|
| B0a | Fix LATERAL join in `payroll_readiness_service.py` — date-filtered, no false-positive block for multi-contract employees | ✅ |
| B0b | Fix LATERAL join in `timesheet_derivation_service.py` — unconditional most-recent contract (no date filter) | ✅ |
| B1 | New employee CRUD API: `GET/PATCH /{wid}/employees/{eid}`, `POST /{wid}/employees/{eid}/contracts`, `PATCH /{wid}/employee-contracts/{cid}` — with D-ARCH-1 run-lock + backdating guard | ✅ |
| B2 | Replace inline SQL in `onboarding.py:451–598` with `employee_repo` calls — unified creation path | ✅ |
| B3 | `Employees.tsx` rework — split `EditSlideOver` (name+status only) + `ChangeContractSlideOver` + `ViewContractsSlideOver`; new `frontend/src/api/employees.ts` | ✅ |
| B4 | Migration `b6c7d8e9f0a1` — `idx_employee_contract_employee_date` on `(employee_id, start_date)` | ✅ |
| EMP-UX-1 | Split "Edit" row action into "Edit Details" and "Change Grade / Salary" (EMP-UX-1) | ✅ |
| EMP-UX-3 | Mid-period hire warning in `AddEmployeeSlideOver` when `contract_start` falls in current month | ✅ |
| EMP-UX-4 | Payroll Inputs issues badge — `GET /payroll/inputs/issues` endpoint; nav badge; `AlertBanner` in `PayrollInputs.tsx` | ✅ |

**Also shipped post-Sprint 17:**
- SEC-17-1: `str(e)` replaced with generic messages + `_log.error` server-side in `employees.py` (standing prohibition)
- SEC-17-2: `max_length=255` on `full_name` and `change_reason` Pydantic fields
- CORS fix 1: `allow_credentials=True` incompatible with wildcard origin — resolved
- CORS fix 2: proxy `/api/v1` through Vercel rewrite to eliminate CORS entirely

**Test report:** `docs/test-reports/2026-05-27-sprint-17-full.md` — 266 unit/integration tests passed (1 skipped); 14 live API checks PASS; 13 static/compile checks PASS; 1 infrastructure check PASS; 2 BLOCKED (B3 browser UAT, B0b multi-contract test data).

---

### Deferred from Sprint 17

| Ref | Item | Target |
|-----|------|--------|
| B3-BROWSER | Manual browser UAT of Edit / Change Grade / View Contracts SlideOvers | Sprint 18 or UAT |
| B0b-VERIFY | Multi-contract employee through timesheet derivation (needs test data) | Sprint 18 |
| Attendance Codes nav entry | `AttendanceConfiguration.tsx` built but not in Settings sidebar (`Navigation.tsx`) | Sprint 18 |
| AUD-16-2 | Re-upload overwrites APPROVED timesheet entries — no guard | Sprint 18 |
| AUD-16-1 | No `approved_by` on timesheet state transitions | Sprint 18 |
| AUD-14-1 | `proration_strategy` missing from `rules_context_snapshot` | Sprint 18 |

---

### Explicitly Out of Scope (Sprint 17)

| Item | Target sprint |
|------|--------------|
| Deactivation UI (dedicated flow + input warning) | Sprint 20 (EMP-P3-2 / EMP-UX-2) |
| Contract history showing multiple past rows | Sprint 20 (EMP-P3-1) |
| External ID field | Sprint 20 |
| "Final period" badge on payroll results | Sprint 20 (EMP-P3-2) |

---

## Sprint 24 — Enrollment UX Clarity + Audit Fixes


**Sprint date:** 2026-06-09
**Sprint goal:** Fix post-upload UX confusion (unenrolled employees look broken but aren't); close Q6 audit finding (APPROVED timesheet overwrite); close Q8 (already resolved via snapshot); surface excluded employees on PayrollResults.

### Story Index

| Story | Summary | Status |
|-------|---------|--------|
| EMP-UX-5 | AlertBanner `info` + "Set up salary structure →" CTA when no salary defs; nav badge shows not-enrolled count (priority over unmatched) | ✅ |
| EMP-RUN-1 | PayrollResults: warning banner when workspace has unenrolled employees ("N not included in this run") | ✅ |
| Q6-FIX | Guard APPROVED timesheet re-upload: prefetch approved_ids before loop, reject per employee | ✅ |
| Q8-FIX | CLOSED (no-code): `proration_strategy` already frozen in `client_component_metadata_snapshot` | ✅ |
| EMP-VERIFY-1 | Browser verification of auto-suggest banner (Sprint 23) | 🔜 |

**Files changed:** `Employees.tsx`, `MainLayout.tsx`, `Layout.tsx`, `Navigation.tsx`, `PayrollResults.tsx`, `timesheet_repo.py`, `timesheet_derivation_service.py`, `ROADMAP.md`

---

## Sprint 25 — Badge Real-time Update + Employees Table UX Fixes

**Sprint date:** 2026-06-10
**Sprint goal:** Sidebar badge updates in real-time on payroll input mutations; employees table UX regressions and contract date display fixed.

**Story files:** `docs/stories/sprint-25-badge-realtime-update.md`, `docs/stories/sprint-25a-employees-table-ux-fixes.md`, `docs/stories/sprint-25b-no-longer-active-ux.md`, `docs/stories/sprint-25c-edit-employee-contract-end-date.md`, `docs/stories/sprint-25d-register-employee-contract-dates.md`

| Story | Summary | Status |
|-------|---------|--------|
| BADGE-RT-1 | Payroll Inputs sidebar badge reflects live pending count via `window.dispatchEvent` on mutations | ✅ |
| BADGE-RT-2 | Badge shows total pending inputs (not just issue inputs) | ✅ |
| EMP-TABLE-1 | Employees table UX fixes: start/end date both visible, column alignment, inactive employee styling | ✅ |
| EMP-TABLE-2 | "No longer active" state surfaced correctly; contract end date editable | ✅ |
| EMP-TABLE-3 | Register employee: contract start and end date fields added to AddEmployeeSlideOver | ✅ |

---

## Sprint 26 — Employee Registration & Status Management

**Sprint date:** 2026-06-11
**Sprint goal:** Complete employee lifecycle CRUD: registration, edit, status transitions (ACTIVE/INACTIVE), enrollment auto-defaults, and payroll action badges.

**Story file:** `docs/stories/sprint-26-employee-registration-status-management.md`

| Story | Summary | Status |
|-------|---------|--------|
| EMP-REG-1 | Register new employee: full form (name, ID, TIN, RSA, bank, contract dates) | ✅ |
| EMP-EDIT-1 | Edit employee: name, employee number, TIN, RSA, bank; contract dates via separate slide-over | ✅ |
| EMP-STATUS-1 | Status toggle: ACTIVE ↔ INACTIVE with confirmation; payroll exclusion warning for INACTIVE + live contract | ✅ |
| EMP-BADGE-1 | Per-row payroll readiness badge: enrolled/not enrolled/unmatched indicators | ✅ |
| EMP-ENROLL-AUTODEF-1 | Enroll slide-over: auto-suggest salary definition from imported grade label | ✅ |
| EMP-ICONS-1 | Consistent icon set across employee row actions | ✅ |
| EMP-PAYROLL-ACTIONS-1 | Payroll-specific actions (enroll, view inputs) surfaced from employee row | ✅ |

---

## Sprint 27 — Smart Native Upload

**Sprint date:** 2026-06-12
**Sprint goal:** Accept client spreadsheets as-is. Auto-detect column headers, let the operator verify the mapping, then submit to existing endpoints unchanged.

**Story file:** `docs/stories/sprint-27-smart-native-upload.md`

| Story | Summary | Status |
|-------|---------|--------|
| EMP-NATIVE-1 | Smart employee upload: alias-based header detection, row-picker fallback, column mapping panel, per-row result | ✅ |
| INP-NATIVE-1 | Smart period inputs upload: period+keyword header parsing, `@rate` quantity derivation, duplicate column dedup, long-format row emission | ✅ |
| PAY-RECON-1 | Payroll reconciliation upload (old system vs new): column mapping, comparison table, mismatch filter, XLSX download | ✅ |
| INP-MULTI-1 | Multi-row period input entry SlideOver: anchor employee + line-item table, partial success handling | ✅ |
| EMP-REG-5-FIX | Enrollment slide-over pre-population: normalised grade/designation matching (spaces→underscores), pre-fills fields from imported labels; fixes EMP-REG-5 (Sprint 23) | 🔜 |

**New shared infrastructure:** `NativeUploadFlow.tsx`, `ColumnMappingPanel.tsx`, `nativeExcelParser.ts`

---

## Sprint 28 — Upload Error Visibility + Duplicate Skip

**Sprint date:** 2026-06-13
**Sprint goal:** Make upload failures visible and portable across all upload flows; make period input re-uploads idempotent.

**Story file:** `docs/stories/sprint-28-upload-error-visibility.md`

| Story | Summary | Status |
|-------|---------|--------|
| UPLOAD-ERR-1 | Consistent three-layer error state across all upload flows: status banner + amber "Download before you close" block + scrollable error table; downloadable CSV | ✅ |
| UPLOAD-SKIP-1 | Period inputs bulk upload: `IntegrityError` → silent skip (not error); response adds `skipped` count; re-upload is idempotent | ✅ |

**Files changed:** `NativeUploadFlow.tsx`, `PayrollInputsBulkUpload.tsx`, `EmployeeUpload.tsx`, `payroll_input.py`

---

## Phase 2 — Agent Layer (Planned)

AI-powered operator assistant layer built on top of the deterministic payroll engine.

**Arch-council review:** 2026-06-11 — **NEEDS REVISION**. Five blocking conditions recorded before sprint planning can begin.

**Blocking conditions (must resolve in order):**
1. No authentication system exists — `performed_by = "admin@internal"` hardcoded; workspace_id from request body, not JWT. Pre-requisite sprint required.
2. NDPR compliance for employee PII sent to external LLM API — mitigated by PII sanitisation contract (V4); client must be informed.
3. Transactional outbox + full event gap closure must ship before any proactive agent (V1+V2).
4. `explain_component_trace` must use structured slot-filling — LLM cannot introduce numbers not sourced from trace data.
5. `agent_session_log` must wait for auth — partial audit trail (placeholder operator_id) is worse than none.

**Technology decisions (arch-council locked 2026-06-11):**
- Primary LLM: Claude Sonnet (chat) / Claude Opus (investigation agents) via Vercel AI Gateway
- Fallback LLM: GPT-4o (automatic reroute on Anthropic unavailability — silent to operator, logged)
- No Celery/Redis — APScheduler polling loop; single-worker constraint documented
- Conversation history: ephemeral per session; `agent_session_log` persists audit trail (not replay)
- All write actions in Phase 2B require service-layer `pending_action_id` + structured confirmation UI component (not chat reply)

---

### Track P — Authentication (Pre-requisite: Phase 1 routes + Agent Layer)

Arch-council finding: no JWT auth exists anywhere in the system. Must ship before Phase 2A begins. Also closes Track I #35 (P2-2) and Q7 (no actor identity on transitions).

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| P1 | `operator` table — id, workspace_id, email, role, password_hash | Auth | — | Stable identity anchor |
| P2 | `POST /auth/login` → JWT with workspace_id + operator_id claims | Auth | — | |
| P3 | FastAPI `get_current_operator` dependency — injected into all routes | Auth | — | Replaces hardcoded "admin@internal" |
| P4 | workspace_id extracted from JWT in all routes (not request body) | Auth | — | **Non-negotiable invariant — never from message content** |
| P5 | `performed_by` populated from JWT identity across all audit writes and state transitions | Auth | P2-2 / Q7 | Closes Track I #35 and Q7 atomically |
| P6 | Session workspace_id locked from JWT at chat session creation — new session required on workspace switch | Auth | — | Prevents mid-session workspace drift |

> **Gate:** No Phase 2A sprint begins until Track P is complete and verified.

---

### Track V — Agent Foundation (after Track P)

| # | Item | Area | Ref | Notes |
|---|------|------|-----|-------|
| V1 | Transactional outbox — write events inside same DB transaction as state change; relay process moves to `event_store` | Event Reliability | — | **Prerequisite for all Phase 2B proactive agents** — current post-commit write is fire-and-forget |
| V2 | Add missing events: reconciliation MISMATCH, employee enrollment, employee status change (ACTIVE/INACTIVE), payroll input submitted | Event Completeness | — | Ship atomically with V1 |
| V3 | Event consumer worker — APScheduler polling `event_store` for unprocessed events; `processed_at` column on `event_store`; single-worker deployment documented; distributed lock required if multi-process | Event Routing | — | Dispatches to agent handlers; no Celery |
| V4 | PII sanitisation contract — strip direct identifiers (name, employee_number, TIN, RSA pin, bank account) from all tool responses before LLM context; UUID-only employee reference in LLM context; frontend maps UUID to display name | NDPR Compliance | — | Defined and enforced in tool serialisation layer — not ad-hoc per tool author |
| V5 | Agent tool layer — 10 read-only workspace-scoped tool definitions; workspace_id from JWT only, never from message content; result set caps on all list tools | Tool Layer | — | See tool list below |
| V6 | Tool schema contract tests — lightweight assertions each tool returns expected shape; Phase 1 migration that breaks tool layer caught before deployment | Tool Reliability | — | Tool definitions frozen per agent session at session start |
| V7 | Notification layer — in-app alert model (`workspace_notification` table: workspace_id, operator_id, type, message, entity_ref, read_at, created_at) | Notifications | — | Email deferred to Track Y |

**Tool definitions (all read-only; workspace_id from JWT; freeform string fields wrapped in structured envelope before LLM context):**

| Tool | Description | Cap |
|------|-------------|-----|
| `get_employee` | Single employee by ID or search query | — |
| `get_employees` | Filtered employee list (status, enrolled, grade) | 50 rows |
| `get_payroll_run` | Run header + status | — |
| `get_run_results` | Per-employee results for a run | 100 rows |
| `explain_component_trace` | Structured slot-filled trace — LLM fills named slots from trace data only; cannot introduce numbers not in source | — |
| `get_reconciliation` | Reconciliation record for a run | — |
| `get_pending_inputs` | Inputs not yet claimed for current run | 200 rows |
| `get_enrollment_status` | Enrolled vs unenrolled employee counts | — |
| `get_statutory_rules` | Active statutory rules for workspace | — |
| `get_salary_definitions` | Salary definition list | 50 rows |

---

### Track W — Operator Chat Agent — Phase 2A (after Track V)

| # | Item | Sprint | Notes |
|---|------|--------|-------|
| W1 | Chat API endpoint — `POST /api/chat`; workspace context injected at session start (current pay period, run state, enrollment gaps); streaming | A2 | Rate limiting ships here — not deferred to A4 |
| W2 | Vercel AI Gateway integration — Claude Sonnet primary; GPT-4o fallback; zero-data-retention mode; per-workspace usage observable | A2 | Fallback silent to operator; logged in session |
| W3 | Rate limiting — N requests per workspace per minute; hard daily ceiling per workspace | A2 | **Non-negotiable: ships with W1** |
| W4 | Chat UI — floating bubble (bottom-right); expands to panel; streaming renderer; session reset on workspace switch | A3 | |
| W5 | `agent_session_log` table — workspace_id, operator_id, session_id, turn_sequence, role, content, tool_calls_jsonb, created_at; 7-year retention; ships after Track P | A4 | operator_id must be real auth identity — do not ship with placeholder |
| W6 | Degraded mode UX — graceful copy when both providers unavailable; payroll operations unblocked | A4 | |

> **Arch-council condition:** Rate limiting (W3) ships in Sprint A2. `agent_session_log` (W5) ships after Track P is complete. Do not invert this ordering.

---

### Track X — Proactive Agents — Phase 2B (after Track W)

**Pre-condition before Phase 2B sprint planning:** Confirmation protocol must be fully specified. Mechanism: structured confirmation UI component (not chat reply) showing exact record ID, field, and new value — backed by a service-layer `pending_action_id`. Operator must interact with the component to confirm; natural-language "yes" in chat is not sufficient.

| # | Item | Sprint | Notes |
|---|------|--------|-------|
| X1 | Structured confirmation component — `pending_action_id` pattern; mutation layer separate from conversation layer | B1 | Required before any write tool introduced |
| X2 | Payroll Prep Agent — pre-run checklist: missing timesheets, unenrolled employees, expiring contracts, anomalous inputs; surfaced before run creation | B1 | Triggered by: operator navigates to New Run |
| X3 | Reconciliation Investigation Agent — MISMATCH root cause explanation + resolution options with evidence trail | B2 | Triggered by: `reconciliation.MISMATCH` event (requires V1+V2) |
| X4 | Exception Trace Agent — period-over-period pay change explanation per employee using `component_trace_jsonb` | B3 | Triggered by: operator query in chat |

---

### Track Y — Autonomous Agents — Phase 2C (future)

| # | Item | Notes |
|---|------|-------|
| Y1 | Compliance Monitoring Agent — detects statutory rule changes; proposes migration; requires operator approval | After notification layer proven |
| Y2 | Onboarding Agent — guided bulk import; dry-run payroll before commit; maps salary definitions | Requires PII policy confirmed with client |
| Y3 | Email notifications | After in-app notification layer (V7) proven in production |

---

## Phase 3 — Platform Scale (Future)

Deferred until Phase 2 (including Tracks K–O and Agent Layer) is complete and a second client is onboarded.

- Employee payslip PDF generation and distribution (P4-1)
- Snapshot replay endpoint (P4-2)
- Life insurance — full employer cost reporting (P4-3)
- Multi-tenant bureau scaling (P4-6)
- Automated payroll scheduling (pay cycle scheduler)
- Statutory rule management for bureau operators (manage PAYE bands, NHF rates via UI)
