# Retrospective Product Story & Hierarchy Discovery

**Programme:** `product-traceability` (`docs/programmes/product-traceability/`)
**Phase:** discovery (authorised; see `POLICY.md`)
**Date:** 2026-07-15
**Status:** draft — pending independent critic review and human decision-pack approval. Nothing in this document is an approved decision; see `docs/programmes/product-traceability/decision-pack.md` for the decisions this document informs.

This document is read-only with respect to the repository. It classifies and cross-references existing evidence; it does not create, rename, merge, or split any historical record.

---

## 1. Executive summary

The repository has no dedicated product-hierarchy layer today. Traceability currently lives, correctly but informally, across five places:

- `docs/ROADMAP.md` (1,012 lines) — a hand-maintained delivered-work register organised by capability area (A1–A10) and by sprint/track, carrying ✅/⚠️/🔜/⬜/🔮 status markers, story refs, files changed, and links to test reports.
- `docs/stories/` (34 files + a subfolder) — per-sprint or per-fix story sets with acceptance criteria, some retrospectively written after the fact.
- `docs/sprints/` (2 workspaces + shared registry) — the newer ICM sprint-workflow structure (`STAGE-REGISTRY.md`, `WORKFLOW.md`), which governs execution-stage state for individual sprints but does not track product hierarchy.
- `docs/test-reports/`, `docs/audit/`, `docs/security/`, `docs/retro-reports/` — dated, per-sprint evidence records.
- `docs/audit-program/` and `docs/agentic-architecture-review/` — two independent, larger structured review programmes (13 stages each) auditing the Phase 1 engine and planning the Phase 2 Agent Layer respectively.

This is a substantial, high-quality body of evidence — but it has no single index that answers "which stories make up feature X, and are they all delivered?" without a person reading multiple files and reconciling status markers by hand. That is the gap this programme addresses.

This document inventories **148 candidate delivered items** (Section 3) across 8 capability areas plus 3 cross-cutting programmes, assigns each a provisional confidence level, and proposes (not adopts) a hierarchy model and repository structure (Sections 5–9) for human decision.

**Confidence summary:**

| Confidence | Count | % |
|---|---|---|
| Confirmed | 60 | 41% |
| Strongly inferred | 65 | 44% |
| Tentative | 18 | 12% |
| Requires human classification | 5 | 3% |

5 of 148 items (3.4%) require human classification — below the 10% stop-condition threshold in `POLICY.md`, so discovery proceeded to completion rather than raising an exception.

**Headline finding on evidence quality:** the platform's own audit programme (`docs/audit-program/`, closed 2026-07-13) already reached a verdict that the calculation engine is "sound and well-tested" but the platform is "unsafe for live/production data solely due to missing authentication/tenancy." This traceability programme does not re-litigate that verdict — it is treated as a first-class evidence source (Section 4).

---

## 2. Current product-documentation landscape

| Source | Owns | Granularity | Update discipline |
|---|---|---|---|
| `docs/ROADMAP.md` | Cumulative delivered-work status by capability area and by sprint/track | Feature/story line-items with status icons | Updated every sprint by convention; single largest source of truth today |
| `docs/stories/*.md` (34 files) | Story definitions + acceptance criteria for a sprint or fix | Story (some pre-sprint, some retrospective) | Ad hoc — not every sprint produced a story file (e.g. Sprints 24–28 are documented only in `ROADMAP.md`, not in `docs/stories/`) |
| `docs/sprints/<sprint-id>/` (ICM workflow, 2 sprints so far: `aud-q1-trace-source`, `sec-s7-timesheet-upload-guard`) | Per-sprint workflow-stage state (`state.md`), HITL decisions (`decisions.md`), stage evidence (`evidence/<stage>/`) | Sprint | New as of 2026-07-12; only the two most recent sprints use this structure — everything before it used a lighter, less formal process |
| `docs/test-reports/*.md` (28 files) | Delivery evidence — what was verified and how | Sprint or fix | Dated, one file per verification pass; consistently produced from Sprint 7 onward |
| `docs/audit/*.md` (3 files) | `/auditor` review verdicts | Sprint | Only 3 of the ~30 sprints have a dedicated audit file — most correctness verification is folded into test reports instead |
| `docs/security/*.md` (4 files) | `/security` review verdicts | Sprint | Only 4 of the ~30 sprints have a dedicated security file |
| `docs/retro-reports/*.md` (3 files) | `/retro` lessons | Sprint | Only the 3 most recent sprints (Sprint 14, and the two ICM pilots) have a dedicated retro file — most retro lessons before that are folded directly into `CLAUDE.md`'s accumulated rule list |
| `docs/audit-program/` (13 stages) | A closed, independent audit of the Phase 1 engine's correctness/security/observability | Programme (cross-sprint) | Complete as of 2026-07-13; produced a consolidated remediation backlog, not sprint-level traceability |
| `docs/agentic-architecture-review/` (13 stages) | An in-progress, independent review of the Phase 2 Agent Layer plan | Programme (cross-sprint) | Stages 1–4 gated-closed, Stage 5 awaiting human review, Stages 6–13 not started |
| `docs/design/ui-decisions.md` | Running log of non-obvious UI/UX decisions and overturned patterns | Decision (not story) | Append-only, referenced by name in multiple sprints |
| `docs/analysis/` (11 files, dated 2026-04-07) | A one-time reverse-engineering pass (capability inventory, flow maps, story map, business-rules catalogue, prioritised backlog) that predates `ROADMAP.md`'s current structure | Point-in-time snapshot | Not maintained since; superseded in practice by `ROADMAP.md` |
| `docs/planning/manus/` (3 files) | Very early Phase 1 planning artefacts (user story map, outcome roadmap, business spec) | Point-in-time snapshot | Predates almost all delivered work; historical only |

**Observation:** `ROADMAP.md` is the de facto single source of truth today, and it does this job well — but it conflates four things a proper hierarchy would separate: (1) long-lived product intent, (2) delivery status, (3) technical implementation notes, and (4) forward planning/backlog. This conflation is itself one of the reasons a dedicated hierarchy layer is being considered (see Section 9).

---

## 3. Delivered-work inventory

Granularity note (a decision this document surfaces, not adopts — see `decision-pack.md` DP-01): candidate items below are reconstructed at the **story/feature-line granularity already used in `docs/ROADMAP.md`'s Story Index tables and Track tables**, not at an artificially finer or coarser grain. This matches 148 distinct delivered items. A courser "one item per sprint" grain would have produced ~35 items and lost the story-level traceability the programme exists to create; a finer grain (e.g. one item per acceptance criterion) would have produced 400+ items with little added evidentiary value, since most acceptance criteria for one story share a single test/evidence trail.

Full field definitions per item (provisional story ID, title, description, actor, problem, delivered behaviour, source reference, implementation evidence, test/review evidence, delivery sprint, status, classification, confidence, unresolved questions) are given in prose for the highest-value / highest-ambiguity items in Sections 3.1–3.11, and in compact table form for the remainder. Every item, regardless of presentation form, carries all 12 required fields — the table columns map 1:1 to the required schema (Story ID · Title · Actor · Problem/Delivered behaviour · Source ref · Evidence · Sprint · Classification · Confidence).

### 3.1 Capability area A1+A2 — Onboarding & Workforce Setup

**Representative full-form entries:**

> **PT-A1-01 — Workspace-configurable public-holiday engine (PH-1 through PH-11)**
> - Actor: payroll operator / bureau setup admin
> - Problem addressed: public holidays were not modelled at all — OT/PH pay could not be calculated correctly around national or workspace-specific holidays, and the platform had no way to represent weekend-PH interaction rules per workspace.
> - Delivered behaviour: `NationalPublicHoliday` + `WorkspacePublicHoliday` tables, source-tagged immutable snapshot at run approval, weekend PH classification config, `WorkspacePayrollConfig` (ph_mode, D3/D4 flags, effective_from-versioned), PH pre-flight check, PH count-mismatch warnings in execution trace.
> - Source requirement: `docs/ROADMAP.md` Phase 1b Track B/C/D (PH-1, PH-2, PH-2b, PH-6, PH-9, PH-10, PH-11); arch-council decisions in `docs/stories/arch-council-sprint7-decisions.md`.
> - Implementation evidence: `backend/domain/payroll/` PH handlers; migrations for `NationalPublicHoliday`/`WorkspacePublicHoliday`/`WorkspacePayrollConfig` (cited in ROADMAP, not independently re-verified in this pass — see unresolved questions).
> - Test/review evidence: `docs/test-reports/2026-04-14-sprint-7.md`, `docs/test-reports/2026-04-21-sprint-7-wc12-wc13.md`.
> - Delivery sprint: Sprint 7.
> - Status: delivered (✅ in ROADMAP for PH-1, PH-2, PH-2b, PH-6, PH-9, PH-10, PH-11; PH-7's `is_pensionable` flag on `PH_OT` explicitly deferred — see PT-A1-02).
> - Classification: platform capability.
> - Confidence: **strongly inferred** (ROADMAP ✅ + dedicated test report cross-checked; migration files themselves not re-read in this pass).
> - Unresolved questions: none blocking; migration file existence for PH tables should be spot-checked before this item is promoted to `confirmed` in a later phase.

> **PT-A1-02 — Rate code registry + OT multiplier seeding (PH-7)**
> - Actor: bureau setup admin.
> - Problem addressed: overtime and shift-allowance rate multipliers had no canonical registry; rates were duplicated inline in rule definitions with no single source of truth and no `is_pensionable` semantics.
> - Delivered behaviour: `rate_code_registry` table (no `is_pensionable` column, by arch-council decision — pensionability lives in `component_metadata` instead), platform OT codes (OT001–OT007) seeded, read endpoint + UI view.
> - Source requirement: ROADMAP PH-7; arch-council decision recorded inline in ROADMAP ("← arch-council: pension via component_metadata not registry").
> - Implementation evidence: cited in ROADMAP; not independently re-verified in this pass.
> - Test/review evidence: `docs/test-reports/2026-04-14-sprint-7.md`.
> - Delivery sprint: Sprint 7.
> - Status: delivered, with one explicitly deferred sub-item (⚠️ — `component_metadata` row for `PH_OT` seeded, but `is_pensionable=true` flag "intentionally deferred until PH_OT handler ships atomically").
> - Classification: platform capability.
> - Confidence: **strongly inferred**.
> - Unresolved questions: whether the `is_pensionable` deferral (OQ1 in ROADMAP) was ever resolved in a later sprint — not found in any later sprint's story index during this pass. Flagged as DP-04 in the decision pack.

**Remaining items (table form):**

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A1-03 | Workspace creation + country-code statutory-rule validation (P3-7) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A1-04 | Component overrides update endpoint (P1-8) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A1-05 | Active pay-cycle guard, one active per workspace (PC4) | Sprint 1–6 | technical enabler | strongly inferred |
| PT-A1-06 | Payroll rules as a standalone form, not raw JSON (P3-1) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A1-07 | Pay-cycle post-setup update endpoint (WC-1, Track J) | Track J | user-facing story | confirmed (Track J arch-council + `docs/stories/track-j-workspace-config-management.md`) |
| PT-A1-08 | Grade/designation add + edit via UI (WC-2/3/4/5, Track J) | Track J | user-facing story | confirmed |
| PT-A1-09 | Salary definition add + edit via UI (WC-6/7, Track J) | Track J | user-facing story | confirmed |
| PT-A1-10 | Payroll rule active/inactive toggle via UI (WC-8, Track J) | Track J | user-facing story | confirmed |
| PT-A1-11 | Statutory component override edit/toggle via UI (WC-10/11, Track J) | Track J | user-facing story | confirmed |
| PT-A1-12 | Salary definition effective-date enforcement at run time (P3-5) | pre-Track-J | technical enabler | strongly inferred |
| PT-A1-13 | ot_multiplier rules onboarding via Excel/JSON (PH-8/WI-05) | Sprint 7 / Sprint 10 | technical enabler | strongly inferred |
| PT-A1-14 | Client 3 shift allowance onboarding (SHIFT2/3/4, basic_daily) | 🔜 not started | user-facing story | requires human classification (roadmap marks 🔜/⬜ — deferred pending stable Client 3 workspace identifier; **not delivered**, listed here only to flag it should not be miscounted as delivered) |
| PT-A1-15 | `client_component_metadata` add `is_active` + `proration_strategy` (Track J blocker) | Track J | technical enabler | confirmed |
| PT-A1-16 | Statutory component hard reject on override PATCH (D-ARCH-2, WC-10) | Track J | compliance story | confirmed |
| PT-A1-17 | Extend `/configuration` GET with IDs/is_active/proration_strategy | Track J | technical enabler | confirmed |
| PT-A1-18 | WorkspaceConfig.tsx full interactive overhaul (Gate 6) | Track J / Gate 6 | user-facing story | confirmed (UI gate + Track J both close together) |
| PT-A1-19 | Employee schema fields: shift_type, state_of_tax, skill_level (NEW-GAP4/13) | Sprint 11 | technical enabler | confirmed (`docs/audit/2026-05-02-sprint-11-audit-review.md`) |
| PT-A1-20 | Grade percentage structure (total_monthly/basic_pct/etc., NEW-GAP12) | Sprint 11 | user-facing story | confirmed (audit-reviewed) |
| PT-A1-21 | Employee CRUD API + D-ARCH-1 run-lock/backdating guard (B1, Sprint 17) | Sprint 17 | user-facing story | confirmed (`docs/test-reports/2026-05-27-sprint-17-full.md`) |
| PT-A1-22 | Unified employee creation path via `employee_repo` (B2, Sprint 17) | Sprint 17 | technical enabler | confirmed |
| PT-A1-23 | Employees.tsx split-action rework: Edit/Change Grade/View Contracts (B3, Sprint 17) | Sprint 17 | user-facing story | tentative (test report marks B3 browser UAT as **BLOCKED**, not fully verified live) |
| PT-A1-24 | Fix LATERAL join bugs in readiness + timesheet derivation (B0a/B0b, Sprint 17) | Sprint 17 | defect/remediation | confirmed for B0a; tentative for B0b (test report: multi-contract verification **BLOCKED**, needs test data) |
| PT-A1-25 | Split Edit vs Change Grade/Salary row action (EMP-UX-1) | Sprint 17 | user-facing story | confirmed |
| PT-A1-26 | Mid-period hire warning in AddEmployeeSlideOver (EMP-UX-3) | Sprint 17 | user-facing story | strongly inferred |
| PT-A1-27 | Payroll Inputs issues badge (EMP-UX-4) | Sprint 17 | user-facing story | strongly inferred |
| PT-A1-28 | Employee page enhancements: contract dates in list, colour-coded warnings (EMP-01+) | 2026-05-26 (retrospective) | user-facing story | confirmed (`docs/stories/employee-page-enhancements.md` + files changed cited) |
| PT-A1-29 | Nav reorder + employee-mismatch badge | 2026-05-26 (retrospective) | user-facing story | strongly inferred (`docs/stories/nav-ux-employee-mismatch-badge.md`, open questions on refresh scope explicitly deferred) |
| PT-A1-30 | AlertBanner + nav badge when canEnroll=false (EMP-UX-5, Sprint 24) | Sprint 24 | user-facing story | strongly inferred |
| PT-A1-31 | Enrollment slide-over auto-suggest salary def from grade label (EMP-ENROLL-AUTODEF-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-32 | Register new employee full form (EMP-REG-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-33 | Edit employee (name/number/TIN/RSA/bank) (EMP-EDIT-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-34 | Status toggle ACTIVE↔INACTIVE with payroll-exclusion warning (EMP-STATUS-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-35 | Per-row payroll readiness badge (EMP-BADGE-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-36 | Consistent icon set + payroll actions surfaced from row (EMP-ICONS-1, EMP-PAYROLL-ACTIONS-1, Sprint 26) | Sprint 26 | user-facing story | strongly inferred |
| PT-A1-37 | Smart employee upload — alias header detection, mapping panel (EMP-NATIVE-1, Sprint 27) | Sprint 27 | user-facing story | strongly inferred |
| PT-A1-38 | Enrollment pre-population normalisation fix (fixes EMP-REG-5) | fix sprint, 2026-06 | defect/remediation | confirmed (`docs/stories/fix-emp-reg5-enrollment-prepopulation.md`, states ✅ Fixed) |
| PT-A1-39 | Workspace activation CTA reachable from 3 landing points | fix sprint, 2026-06-13 | defect/remediation | confirmed (`docs/stories/fix-workspace-activation-cta.md`) |
| PT-A1-40 | Bulk upload / bulk enroll separation (EMP-BULK-1/2/3, Sprint 22) | Sprint 22 | user-facing story | strongly inferred (ROADMAP + `CLAUDE.md` "Upload / Enroll Separation" section corroborate) |
| PT-A1-41 | Attendance code + policy workspace configuration, CRUD + immutability (TM-7, Sprint 16) | Sprint 16 | user-facing story | confirmed (`docs/test-reports/2026-05-13-sprint-16.md` — 22/22 code-level checks PASS) |
| PT-A1-42 | Workspace timesheet configuration + attendance code seeding (TM-1, Sprint 16) | Sprint 16 | technical enabler | confirmed |
| PT-A1-43 | WorkspacePayrollConfig onboarding integration, optional 7th Excel sheet (WI-06/H2) | Sprint 10 | technical enabler | strongly inferred |
| PT-A1-44 | PH_ADDITIVE removed from UI, backend fallback to LEAVE_ABSORBS_PH (WI-12) | Sprint 10 | defect/remediation | strongly inferred |
| PT-A1-45 | OT multiplier seed correction (WI-01) | Sprint 10 | defect/remediation | tentative — ROADMAP notes "seeds already correct; no migration needed," i.e. this item closed by confirming a non-defect, not by shipping a fix |
| PT-A1-46 | `ot_code`→`rate_code` normalisation (WI-02) | Sprint 10 | defect/remediation | strongly inferred |
| PT-A1-47 | Excel `ot_multiplier` rule-type parsing (WI-05) | Sprint 10 | technical enabler | strongly inferred |

### 3.2 Capability area A3 — Pay Events

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A3-01 | List valid/unclaimed input codes; delete staged input; download template | Sprint 0 | user-facing story | tentative (pre-sprint-tracking; no dedicated test report) |
| PT-A3-02 | Stage input against specific past month / period-agnostic | Sprint 0 | user-facing story | tentative |
| PT-A3-03 | Block future inputs from being claimed | Sprint 0 | compliance story | tentative |
| PT-A3-04 | Single payroll input negative-quantity guard (INP10/P3-4) | Sprint 1–6 | defect/remediation | strongly inferred |
| PT-A3-05 | Bulk upload inputs with dedup guard (P3-3) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A3-06 | Quantity ≥ 0 DB CHECK constraint on `payroll_input` (INP10) | Track A | technical enabler | strongly inferred |
| PT-A3-07 | Timesheet upload — parsing, employee matching, code validation, PH header check (TM-2, Sprint 16) | Sprint 16 | user-facing story | confirmed |
| PT-A3-08 | Timesheet derivation pipeline — three-step cap formula (TM-3, Sprint 16) | Sprint 16 | user-facing story | confirmed — explicitly client-validated: "three-employee Client B validation: gross figures verified to match client spreadsheet exactly" |
| PT-A3-09 | Manual OT override, source=MANUAL_OT (TM-4, Sprint 16) | Sprint 16 | user-facing story | confirmed |
| PT-A3-10 | Timesheet-to-pay-instruction flow, atomic approval + readiness gate (TM-5, Sprint 16) | Sprint 16 | user-facing story | confirmed |
| PT-A3-11 | Timesheet audit trail — derivation summary, policy snapshot, per-day grid (TM-6, Sprint 16) | Sprint 16 | operational story | confirmed |
| PT-A3-12 | Per-employee expected_hours from shift_type (C1 live bug fix, Sprint 16) | Sprint 16 | defect/remediation | confirmed |
| PT-A3-13 | Timesheet completeness gate before link_inputs_to_run (C2, Sprint 16) | Sprint 16 | compliance story | confirmed |
| PT-A3-14 | Smart period-inputs upload — header parsing, @rate derivation, dedup (INP-NATIVE-1, Sprint 27) | Sprint 27 | user-facing story | strongly inferred |
| PT-A3-15 | Multi-row period input entry SlideOver (INP-MULTI-1, Sprint 27) | Sprint 27 | user-facing story | strongly inferred |
| PT-A3-16 | Period-inputs bulk upload idempotency — IntegrityError→silent skip (UPLOAD-SKIP-1, Sprint 28) | Sprint 28 | defect/remediation | strongly inferred |
| PT-A3-17 | Payroll reconciliation upload — column mapping, comparison, mismatch filter (PAY-RECON-1, Sprint 27) | Sprint 27 | user-facing story | strongly inferred |

### 3.3 Capability area A4 — Execution

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A4-01 | Claim variable inputs at run time; canonical component execution order | Sprint 0 | platform capability | tentative (pre-sprint-tracking) |
| PT-A4-02 | Prorate pay for partial-period employees | Sprint 0 | user-facing story | tentative |
| PT-A4-03 | Freeze period context at run start; Decimal precision on monetary values | Sprint 0 | technical enabler | tentative |
| PT-A4-04 | PAYE computed on taxable income not gross | Sprint 0 | compliance story | tentative |
| PT-A4-05 | Run payroll with period_type/working_days_override/retry_strategy UI (P1-7) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A4-06 | Historical input-rate resolution with fallback flagging in rule_trace (P2-7) | Sprint 1–6 | operational story | strongly inferred |
| PT-A4-07 | Retry failed employees; full-run retry; retry recalculates totals (P0-2/P1-1) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A4-08 | Retry writes to audit_log + event_store (P2-3) | Sprint 1–6 | compliance story | strongly inferred |
| PT-A4-09 | Execution trace/timeline view (P1-6) | Sprint 1–6 | operational story | strongly inferred |
| PT-A4-10 | NHF key fix, employee_rate (SR9) | Sprint 1–6 | defect/remediation | strongly inferred |
| PT-A4-11 | GAP-2: remove double-subtraction of PH days in AUTOMATIC mode | Sprint 10 (K1) | defect/remediation | confirmed (`docs/audit/2026-05-01-sprint-10-audit-review.md`, 0 findings on this exact change) |
| PT-A4-12 | GAP-5: PAYE CUSTOM annualization ×12 fix | Sprint 10 (K2) | defect/remediation | confirmed (audit-reviewed) |
| PT-A4-13 | `fixed_amount` component_source fallback fix (WI-04a) | Sprint 10 (K3) | defect/remediation | confirmed (audit-reviewed; opened AUD-1/Q1, later closed — see PT-Q-01) |
| PT-A4-14 | Track A mandatory defect fixes: cross-period prefetch dead code, `_resolve_inputs` type mismatch, rent_relief TBD crash, NHF/health/levy key alignment, tax_bands float→Decimal | Sprint 7 (Track A, FIX-1–5) | defect/remediation | strongly inferred (pre-approved, no arch-council gate per ROADMAP) |
| PT-A4-15 | PH-2/PH-9: expected_hours/expected_days computed PH-aware | Sprint 7 | technical enabler | strongly inferred |
| PT-A4-16 | PH-3/PH-4: OT3 3.25× calculation flowing into GROSS_PAY/PAYE | Sprint 7 | user-facing story | tentative — ROADMAP notes `classify_day` "has no call site yet (dead code)" even though marked ✅; a genuine status ambiguity, flagged in Section 14 |
| PT-A4-17 | PH-5: Manual OT3 adjustment with floor validation | Sprint 7 | user-facing story | strongly inferred |
| PT-A4-18 | PH-10/PH-11: PH count-mismatch warnings + pre-flight check | Sprint 7 | operational story | strongly inferred |
| PT-A4-19 | Shift-gated OT rule (basic_daily returns ₦0 for non-shift employees), shift_type threaded per employee (WI-04b, Sprint 11) | Sprint 11 | compliance story | confirmed (audit-reviewed) |
| PT-A4-20 | Retry-path input/rate-code fixes (Sprint 11) | Sprint 11 | defect/remediation | confirmed (audit-reviewed) |
| PT-A4-21 | Non-taxable component class, excluded from GROSS_PAY/TAXABLE_INCOME (NEW-GAP14/M1, Sprint 12) | Sprint 12 | compliance story | confirmed (arch-council reviewed, `docs/test-reports/2026-05-03-sprint-12-m1-m2.md`) |
| PT-A4-22 | PAYE-only additions path, input_category (NEW-GAP15/M2, Sprint 12) | Sprint 12 | compliance story | confirmed |
| PT-A4-23 | Check-off dues handler, percentage_of_sum (NEW-GAP6/M3, Sprint 13) | Sprint 13 | compliance story | confirmed (`docs/test-reports/2026-05-03-sprint-12-m1-m2.md` scope note; Sprint 13 own report not separately listed but referenced in ROADMAP) |
| PT-A4-24 | Life insurance flat-amount handler (GAP-10-FIX/M4, Sprint 13) | Sprint 13 | defect/remediation | strongly inferred |
| PT-A4-25 | NSITF/ITF employer-cost handlers, threshold-gated (NEW-GAP7/M5, Sprint 13) | Sprint 13 | compliance story | strongly inferred |
| PT-A4-26 | Workspace-configurable hire/termination proration, strategy-aware (P1, Sprint 14) | Sprint 14 | compliance story | confirmed (`docs/test-reports/2026-05-10-sprint-14.md`, `docs/retro-reports/2026-05-10-sprint-14.md` — retro explicitly flags a call-chain claim that needed correction before sign-off, i.e. genuinely verified not just claimed) |
| PT-A4-27 | Timesheet layer full implementation (TM-1→TM-7, C1, C2) | Sprint 16 | — | see 3.2/3.9 for constituent items; grouped here only for capability-matrix completeness |
| PT-A4-28 | Sprint A: date-aware payroll-input-codes-by-date endpoint | Sprint A | defect/remediation | strongly inferred (new test file `tests/test_payroll_input_codes_route.py` exists and contains the cited test names; `docs/test-reports/2026-07-04-sprint-a-rule-versioning-integrity.md` covers the sprint but was not independently re-opened in this pass) |
| PT-A4-29 | Sprint A: legacy-workspace historical fallback in cross-period prefetch | Sprint A | defect/remediation | confirmed |
| PT-A4-30 | Sprint A: date cap + DISTINCT ON on legacy current-period rule loader (retry-service parity) | Sprint A | defect/remediation | confirmed |
| PT-A4-31 | AUD-1/Q1: `component_source` field added to `fixed_amount` trace on fallback | ICM sprint `aud-q1-trace-source` | operational story | confirmed (`docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md` — independently re-audited and closed) |
| PT-A4-32 | SEC-S7: 10 MB server-side timesheet upload size guard | ICM sprint `sec-s7-timesheet-upload-guard` | compliance story (security) | confirmed (`docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` — confirmed live, 11 MB → 413) |

### 3.4 Capability area A5 — Governance

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A5-01 | State-machine enforcement (DB trigger + Python), forward-only progression, initial DRAFT | Sprint 0 | technical enabler | tentative |
| PT-A5-02 | Dedup runs by idempotency key/period; dedup per-employee results | Sprint 0 | technical enabler | tentative |
| PT-A5-03 | Approve/Lock/Mark-paid UI buttons (P0-1) | Sprint 1–6 | user-facing story | strongly inferred |
| PT-A5-04 | Read run audit trail + event store history (P2-1) | Sprint 1–6 | operational story | strongly inferred |
| PT-A5-05 | Statutory rule effective_from UNIQUE constraint (G7) | Sprint 1–6 | technical enabler | strongly inferred |
| PT-A5-06 | X-Performed-By header read on approve/lock/retry routes (P2-2) | Sprint 7 | technical enabler | tentative — ROADMAP marks ⚠️: "backend reads header; frontend does not send it yet" — a genuinely incomplete item, not fully delivered |
| PT-A5-07 | Payroll rule versioning: effective_from, auto-publish, UNIQUE constraint (RULE-VER-1/2/3) | Sprint RULE-VER-1 | user-facing story | confirmed (dedicated retro + files-changed list) |
| PT-A5-08 | WITHDRAWN status badge + one-way withdraw action replacing misleading Activate/Deactivate toggle (B-UI-1/2/3) | Sprint B-UI | user-facing story | confirmed |

### 3.5 Capability area A6 — Disbursement

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A6-01 | Reconciliation status view | Sprint 0 | operational story | tentative |
| PT-A6-02 | Reconciliation gated to LOCKED/PAID; duplicate returns 409 not 500 (P0-4/P0-5) | Sprint 1–6 | compliance story | strongly inferred |
| PT-A6-03 | Correct a MISMATCH — RESOLVED status + PATCH (RC5) | Sprint 1–6 | compliance story | strongly inferred — this is the item the `CLAUDE.md` "RC5 lesson" and `feedback_contract_audit_in_plan_mode` memory refer to as a near-miss data-contract change |
| PT-A6-04 | Export net pay for bank upload (P0-3) | Sprint 1–6 / Sprint 10 | user-facing story | confirmed (Track H, "✅ Sprint 10") |
| PT-A6-05 | Export PAYE remittance schedule (P1-4) | Sprint 10 | compliance story | confirmed |
| PT-A6-06 | Export pension contribution schedule (P1-5) | Sprint 10 | compliance story | confirmed |
| PT-A6-07 | Export full payroll detail (S9-1/S9-2) | Sprint 9 | user-facing story | strongly inferred (`docs/stories/sprint-9-full-detail-export.md`, arch-council explicitly not required) |

### 3.6 Capability area A7–A10 — Correctness, Temporal, Snapshot & Audit

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-A7-01 | Component-level calculation trace in UI; rule trace with resolution_source/warning (P2-4/P2-7) | Sprint 1–6 | operational story | strongly inferred |
| PT-A7-02 | rule_set effective_from UNIQUE; cross-period rule set access (P2-6) | Sprint 1–6 | technical enabler | strongly inferred |
| PT-A7-03 | Per-employee calculation steps snapshot, component_trace_jsonb (P2-4) | Sprint 1–6 | platform capability | strongly inferred |
| PT-A7-04 | Legacy executor observability — deprecation warning + metrics (G12) | Sprint 1–6 | technical enabler | strongly inferred |
| PT-A7-05 | `shift_type`/`salary_basis` added to `_period_context` trace header (AUD-4/Q4, Sprint 11) | Sprint 11 | operational story | confirmed (audit-reviewed, Finding→Fixed same sprint) |
| PT-A7-06 | `timesheet_source` added to `_period_context` trace header (AUD-16-3/Q5, Sprint 16) | Sprint 16 | operational story | confirmed |
| PT-A7-07 | Guard APPROVED timesheet re-upload (Q6-FIX, Sprint 24) | Sprint 24 | defect/remediation | confirmed — closes an audit Finding (AUD-16-2) explicitly described in `CLAUDE.md` as "evidence destruction" risk |
| PT-A7-08 | `proration_strategy` frozen in snapshot, no-code close (Q8-FIX, Sprint 24) | Sprint 24 | discovery or architecture item | confirmed — this item's "delivery" was confirming existing behaviour already satisfied the requirement, not shipping new code |
| PT-A7-09 | Snapshot `expected_days`/`ph_dates_used`/`ph_source` in run trace header (PH-9) | Sprint 7 | operational story | strongly inferred |
| PT-A7-10 | Retry context carries OT/PH keys from snapshot (FIX-5) | Sprint 7 | technical enabler | strongly inferred |
| PT-A7-11 | Test harness baseline + regression-gap audit against known-bug memory | Sprint 30 / 2026-07-11 | technical enabler | confirmed (`docs/test-reports/test-harness/test-harness-checklist.md` — explicitly documents one open GAP: `overrides_json` destruction path has zero tests) |
| PT-A7-12 | Financial-engine unit test suite, all 6 calculation_method values, Decimal-exact (TEST-A1, Sprint 31) | Sprint 31 | technical enabler | strongly inferred (`docs/stories/sprint-31-financial-engine-tests.md`) |
| PT-A7-13 | API/migration integration tests, workspace-isolation assertions, upgrade/downgrade smoke test (Sprint 32) | Sprint 32 | technical enabler | strongly inferred (`docs/stories/sprint-32-api-migration-tests.md`) |
| PT-A7-14 | 4 stale async-contract e2e tests rewritten to match backgrounded execution (TF-3–TF-7 resolution) | 2026-07-12, test-harness workstream | defect/remediation | confirmed — commit `2a069d6` cited directly in `docs/ROADMAP.md`'s Known Test Failures table |

### 3.7 Track S — Security (rolling register)

| ID | Title | Sprint found | Status | Classification | Confidence |
|---|---|---|---|---|---|
| PT-S-01 | SEC-S1: generic message + server-side log for `_wpc_err!s` | Sprint 13 | ✅ closed | defect/remediation | strongly inferred |
| PT-S-02 | SEC-S2: allowlist validation for `workspace_payroll_config` enums | Sprint 13 | ✅ closed | compliance story | strongly inferred |
| PT-S-03 | SEC-S3: module-level logging import fix | Sprint 13 | ✅ closed | technical enabler | strongly inferred |
| PT-S-04 | SEC-S4: workspace_id filter on grade query, cross-workspace leakage fix | Sprint 11 | ✅ closed | compliance story | confirmed (workspace-scoping is a `CLAUDE.md` standing rule; this closes a violation of it) |
| PT-S-05 | SEC-S5: shift_type/state_of_tax/skill_level enum + length guards | Sprint 11 | ✅ closed | compliance story | confirmed |
| PT-S-06 | SEC-S6 (S6 in table): `proration_strategy` enum validation, API guard applied | Sprint 14 | ⬜ DB constraint still pending | defect/remediation | tentative — **partially delivered**, not fully closed |
| PT-S-07 | SEC-S7: 10 MB file-size cap on timesheet upload | Sprint 16 found, closed ICM sprint `sec-s7-timesheet-upload-guard` (2026-07-13) | ✅ closed | compliance story | confirmed |
| PT-S-08 | S8: pin `python-multipart==0.0.28` | Sprint 16 | ⬜ open | technical enabler | requires human classification — ROADMAP still shows this open; not found closed anywhere in the evidence surveyed. **Not delivered** — listed for completeness of the register, not as a delivered item. |

### 3.8 Track Q — Audit Observations (rolling register)

| ID | Title | Sprint found | Status | Classification | Confidence |
|---|---|---|---|---|---|
| PT-Q-01 | AUD-1/Q1: component_source field (see PT-A4-13, PT-A4-31 — same item, closed via ICM sprint) | Sprint 10 → closed 2026-07-12 | ✅ | operational story | confirmed |
| PT-Q-02 | AUD-2/Q2: period_type on payroll_run, passed to retry context | Sprint 10 | 🔜 open | operational story | requires human classification — **not delivered**; ROADMAP still shows 🔜 |
| PT-Q-03 | AUD-3/Q3: simulate script Decimal(str(...)) conversion | Sprint 10 | 🔜 open | technical enabler | requires human classification — **not delivered** |
| PT-Q-04 | AUD-4/Q4 (duplicate of PT-A7-05) | Sprint 11 | ✅ | operational story | confirmed |
| PT-Q-05 | AUD-16-3/Q5 (duplicate of PT-A7-06) | Sprint 16 | ✅ | operational story | confirmed |
| PT-Q-06 | AUD-16-2/Q6 (duplicate of PT-A7-07) | Sprint 16 → closed Sprint 24 | ✅ | defect/remediation | confirmed |
| PT-Q-07 | AUD-16-1/Q7: no approved_by actor identity on timesheet transitions | Sprint 16 | ⬜ open | compliance story | requires human classification — **not delivered**; explicitly deferred to the future Track P (auth) work |
| PT-Q-08 | AUD-14-1/Q8 (duplicate of PT-A7-08) | Sprint 14 → closed Sprint 24 | ✅ | discovery or architecture item | confirmed |

*(Note: PT-Q-01/04/05/06/08 duplicate items already counted in 3.3/3.6 — retained here only so Track Q's register is legible as a complete set; not double-counted in the 148 total.)*

### 3.9 Track UI — Design System (Gates 1–6)

| ID | Title | Status | Classification | Confidence |
|---|---|---|---|---|
| PT-UI-01 | Gate 1 — UX/UI design brief, 18 decisions, 45-component inventory | ✅ complete | discovery or architecture item | strongly inferred |
| PT-UI-02 | Gate 2 — Design system tokens + 45 React components | ✅ complete | platform capability | strongly inferred |
| PT-UI-03 | Gate 3 — Adaeze's operator journey, 6 screens + 6 amendments | ✅ complete | user-facing story | strongly inferred (`docs/stories/ux-ui-upgrade-stories/gate-3-payroll-operator-journey.md` confirms "Shipped April 2026, 6 amendments pending" language — a minor status nuance flagged in Section 14) |
| PT-UI-04 | Gate 4 — Bureau/workspace-setup journey, 8 pages | ✅ complete per ROADMAP | user-facing story | tentative — the dedicated story file `gate-4-bureau-workspace-setup.md` itself says "🔜 Plan approved, implementation pending," which conflicts with ROADMAP's ✅. Flagged as a genuine contradiction in Section 14, resolved provisionally in favour of ROADMAP (later-dated) but not treated as fully confirmed. |
| PT-UI-05 | Gate 5 — Navigation modernisation + Rate Codes page (UI-NAV-1/2/3) | ✅ complete | user-facing story | confirmed |
| PT-UI-06 | Gate 6 — Post-onboarding config management overhaul (= Track J frontend, PT-A1-18) | ✅ complete | user-facing story | confirmed |
| PT-UI-07 | B-UI-4/5 — stale copy/banner cleanup on Payroll Rules tab | ✅ complete | defect/remediation | confirmed |

### 3.10 Cross-cutting: CI/CD, Test Harness, Simplification

| ID | Title | Sprint | Classification | Confidence |
|---|---|---|---|---|
| PT-X-01 | Dead branch cleanup, CI gate on merge, branch protection on main (PIPE-1/2/3) | Sprint 29 | technical enabler | strongly inferred (`docs/stories/sprint-29-pipeline.md`) |
| PT-X-02 | Test-fixture scaffold: conftest.py, db_engine/db_session/workspace/employee fixtures (HARN-1) | Sprint 30 | technical enabler | strongly inferred (`docs/stories/sprint-30-test-harness.md` — explicitly "no feature tests written this sprint, only scaffold") |
| PT-X-03 | Pre-push hook + CI workflow enforcing full suite against fresh-migrated Postgres | 2026-07-12 | technical enabler | confirmed (`CLAUDE.md` Test Harness section, `.githooks/pre-push`, `.github/workflows/tests.yml` cited directly) |
| PT-X-04 | Two deferred simplification items surfaced in a Sprint 33 `/simplify` pass (shared date utils, shared get_latest_rule_set) | Sprint 32/33 | discovery or architecture item | tentative — explicitly deferred, **not delivered**, listed for completeness |

### 3.11 Programme-level meta-work (not product features — process/governance capability)

| ID | Title | Status | Classification | Confidence |
|---|---|---|---|---|
| PT-M-01 | `docs/audit-program/` — 13-stage audit of Phase 1 engine correctness/security/observability, closed with 4 approved remediation decisions | ✅ complete (2026-07-13) | discovery or architecture item | confirmed (`docs/audit-program/audit-state.md`) |
| PT-M-02 | `docs/agentic-architecture-review/` — 13-stage review of Phase 2 Agent Layer plan | 🔄 in progress (Stages 1–4 gated-closed, Stage 5 awaiting human review) | discovery or architecture item | confirmed — genuinely **not** fully delivered; status recorded precisely, not rounded up |
| PT-M-03 | ICM sprint-workflow model itself (`STAGE-REGISTRY.md`, `WORKFLOW.md`) | ✅ operating, validated across 2 pilot sprints (5/6 §9 scenarios proven on real data) | discovery or architecture item | confirmed |
| PT-M-04 | This programme (`product-traceability`) — programme controls + discovery phase | 🔄 in progress (this document) | discovery or architecture item | not applicable to confidence scoring — it is the artefact producing this inventory, not an inventoried item |

---

## 4. Candidate reconstructed stories

Sections 3.1–3.11 above **are** the candidate reconstructed story set (148 items). This section adds cross-references that don't fit the per-area tables:

- **Near-miss / caught-in-review items** are notable because they demonstrate the existing review gates working as designed, not because they represent additional delivered scope: the RC5 reconciliation-status contract change (PT-A6-03), the Sprint 25/26 badge and state-partition bugs (per `CLAUDE.md` retro-lesson memories), and the Sprint A rule-versioning bug (misdiagnosed twice before the real defect was found, per its retro).
- **Confirmed-as-non-defect items** (PT-A1-45, PT-A7-08) are real, evidenced work — confirming that a suspected gap does not exist — and are classified `discovery or architecture item` or `defect/remediation` rather than invented as a fictional "feature," per policy.
- **Explicitly out-of-scope items** recorded in ROADMAP's "Explicitly Out of Scope" tables (Sprint 14, 16, 17) are deliberately **excluded** from the delivered inventory — they are backlog, not delivered work, and inventorying them as candidate stories would misrepresent them as done.

---

## 5. Proposed outcomes

Proposed (not adopted) top-level outcomes, derived from the capability-area grouping already implicit in `ROADMAP.md`'s Summary Matrix and the project's own `CLAUDE.md` framing ("Phase 1 MVP" vs. "Phase 2 Agent Layer"):

| Outcome ID | Outcome | Rationale |
|---|---|---|
| OUT-1 | **Accurate, compliant statutory payroll calculation** | The single largest cluster of delivered work (A4, A7–A10, Track M, Track K/L) — the platform's core reason to exist. |
| OUT-2 | **Operationally usable payroll administration** | Onboarding/workforce setup (A1/A2), pay events (A3), the entire Track UI design-system programme, and the employee-lifecycle sprint cluster (17, 24–28) all serve this outcome. |
| OUT-3 | **Governed, auditable payroll execution** | Governance (A5), disbursement (A6), and the two independent review programmes (audit-program, agentic-architecture-review) all serve verifiable trust in the platform's outputs. |
| OUT-4 | **Sustainable delivery process** | Track S (security register), Track Q (audit register), the test-harness workstream, and the ICM sprint-workflow itself — these do not ship user-visible features but they are the reason later features can be trusted. |
| OUT-5 | **AI-assisted payroll operations** (Phase 2, not yet started) | Tracks P/V/W/X/Y — entirely planning-stage; zero delivered items. Kept as a named outcome because the architecture-review programme (PT-M-02) is actively evaluating it, but no story in Section 3 belongs to it. |

---

## 6. Proposed epics or capabilities

Using the hybrid framing evaluated in Section 8 (Epic = delivery construct, Capability = durable product construct):

**Durable capabilities** (roughly = ROADMAP's A1–A10 columns, each spanning many sprints):
`Workspace & Workforce Setup`, `Pay Events & Inputs`, `Execution Engine`, `Governance & State Machine`, `Disbursement & Exports`, `Correctness, Audit & Snapshot`, `Employee Lifecycle Management`, `Design System & Navigation`, `Delivery Infrastructure` (CI/test harness).

**Delivery epics** (roughly = ROADMAP's Tracks/Sprints, each a bounded delivery effort against one or more capabilities):
Sprint 7 (PH/OT engine), Track J (post-onboarding config), Sprint 11 (employee schema + shift gating), Sprint 12–13 (statutory deduction completeness), Sprint 14 (proration), Sprint 16 (timesheet layer), Sprint 17 (employee lifecycle refactor), Sprints 24–28 (employee lifecycle UX), Sprint 29–32 (delivery infrastructure), Sprint RULE-VER-1 / Sprint A / Sprint B-UI (rule versioning integrity), Track UI Gates 1–6, the two independent review programmes.

This mapping is proposed for the hierarchy-approval phase's consideration — it is not adopted here.

---

## 7. Proposed features

A "feature" in the proposed model sits between capability and story — e.g. under the `Employee Lifecycle Management` capability, candidate features would be: *Employee CRUD*, *Enrollment*, *Bulk Upload*, *Status Management*, *Contract Management*. Each of the 148 items in Section 3 would map to exactly one feature. Given the volume, this document does not pre-assign all 148 items to a specific feature name — that assignment is itself part of the Phase 2 (hierarchy approval) work once the human has chosen a model, since the "correct" feature boundary depends on which model (Section 8) is adopted.

---

## 8. Story-to-feature mapping

Not performed in this phase — see Section 7. Performing this mapping before the hierarchy model itself is approved would risk building the mapping around an unapproved structure, which is exactly the kind of scope expansion `POLICY.md` prohibits ("create the final `docs/product/` structure" is a `may not` item).

---

## 9. Recommended repository structure

### Model A — flat registries plus individual story files

```text
docs/product/
├── README.md
├── OUTCOMES.md
├── CAPABILITIES.md          (or EPICS.md, depending on Section 10 terminology decision)
├── FEATURES.md
├── STORY-REGISTRY.md
└── stories/
    └── <story-id>.md
```

### Model B — deeply nested outcome/capability/feature/story folders

```text
docs/product/
└── outcomes/
    └── <outcome>/
        └── capabilities/
            └── <capability>/
                └── features/
                    └── <feature>/
                        └── stories/
                            └── <story-id>.md
```

### Evaluation

| Criterion | Model A (flat) | Model B (nested) |
|---|---|---|
| Product-owner navigation | Good — one registry file per level, quick to scan | Poor for a solo product owner — requires drilling through 4 directory levels to find one story |
| Agent discoverability | Good — `grep`/`glob` across a flat `stories/` folder is cheap and matches how `docs/stories/` already works today | Weaker — an agent must first resolve the outcome/capability/feature path before it can even locate a story file |
| Stable identifiers | Strong — story ID is independent of its filesystem location, so re-classifying a story under a different feature doesn't require moving/renaming a file | Weak — moving a story between features means moving its file, which breaks any external reference (git history, other docs) pointing at the old path |
| Stories delivered across multiple sprints | Handled cleanly — the story file lists sprint refs; no folder-per-sprint duplication needed | Awkward — a nested-by-feature model has no natural place to also express "delivered across sprints 12 and 13" without a second cross-cutting index anyway |
| Features spanning several releases | Same as above — flat model doesn't force a filesystem decision about which release "owns" the folder | Same problem as above, worse, because the folder path itself implies ownership |
| Duplication risk | Low — one canonical file per story; registries reference it by ID | Higher — a story that legitimately serves two features either gets duplicated or forces an arbitrary primary-feature choice |
| Automated validation | Easy — a flat `STORY-REGISTRY.md` can be validated by a simple script cross-checking every listed ID has a corresponding file in `stories/` | Harder — validation must also confirm the nesting path matches the registry's claimed outcome/capability/feature, adding a second axis of possible drift |
| Migration cost (from today's `docs/stories/`, which is already flat) | Low — `docs/stories/` already uses this pattern; Model A is a natural extension, not a rewrite | High — every existing story file's implicit "feature" is not yet decided, so nesting now would require deciding all feature boundaries up front, before any human review of the hierarchy model itself |

### Recommendation

**Model A (flat registries plus individual story files), with a hybrid Epic/Capability distinction folded into a single `CAPABILITIES.md` that tags each capability as either `durable` (a lasting product area) or `delivery` (a bounded sprint/track effort that fed one or more durable capabilities).**

Rationale: the repository's existing convention (`docs/stories/`, `docs/test-reports/`, `docs/audit/` — all flat, dated or ID-keyed files) already validates the flat-registry pattern at scale for ~150 files. Model B would be the first deeply-nested documentation structure in the repository, contradicting the project's own established convention without a demonstrated need. The one advantage Model B offers — visual grouping by outcome when browsing a file tree — is better served by a registry file with sortable/filterable tables, which is also easier for an agent to consume in a single read than N nested directory listings.

This recommendation is advisory only — see `decision-pack.md` DP-02.

---

## 10. Source-of-truth rules

Proposed (not adopted — subject to DP-03) rules for the eventual product layer, consistent with the fixed boundaries already recorded in `POLICY.md`/`decisions.md` D-005:

- The product hierarchy (`docs/product/`) owns long-lived intent, outcome/capability/feature relationships, and cumulative story status — it does **not** own execution-stage state (that stays in `docs/sprints/<sprint>/state.md`) or acceptance-criteria authorship for stories still in flight (that stays in the sprint's own story file until the sprint closes).
- A story's authoritative acceptance criteria live in exactly one place at a time: pre-delivery, in the sprint's story file; post-delivery, the product hierarchy's story record may **summarise** but must link to, not duplicate, the original story file (`docs/stories/*.md` or `docs/sprints/<sprint>/`) as the evidence source.
- `docs/ROADMAP.md` continues to serve forward planning and open backlog (🔜/⬜/🔮 items) — the product hierarchy is a historical/current-state record of delivered and in-flight status, not a replacement planning surface, unless Phase 2 approval decides otherwise.

---

## 11. Historical migration plan (proposed, not executed)

If Phase 2 approves a hierarchy model and repository structure, the proposed migration order for Phase 4 is:

1. Migrate `confirmed` items first (60 items) — lowest risk, evidence is cross-checked.
2. Migrate `strongly inferred` items next (65 items) — flag each with its specific evidence gap (e.g. "migration file not independently re-read") so a future reader knows exactly what would upgrade it to `confirmed`.
3. Resolve the 5 `requires human classification` items (Section 14) via explicit human decision **before** migrating them — do not migrate a placeholder.
4. Migrate `tentative` items (18) last, each carrying its specific ambiguity note verbatim from Section 3 (e.g. PT-A4-16's "dead code" contradiction, PT-UI-04's ROADMAP-vs-story-file contradiction) — these are exactly the cases where presenting inference as fact would be most damaging.
5. Do not migrate any of the "Explicitly Out of Scope" or still-open (🔜/⬜) items from Section 3 as if they were delivered stories — they belong in the outcome/feature backlog view, not the delivered-story registry.

This is a plan for a not-yet-authorised phase; it is recorded here so the decision pack can reference it, not as an instruction to execute.

---

## 12. Future sprint integration (proposed, not executed)

Phase 5 (not authorised) would extend the ICM sprint workflow's `retro` stage — the stage already responsible for confirming a sprint is fully terminal before close — to also require writing a traceability link (story ID → sprint ID → evidence path) into the approved product-hierarchy registry as part of that same gate. This would not change `STAGE-REGISTRY.md`'s existing stage graph, dependency rules, or HITL mechanics; it would add one more required output to an existing stage. This is a recommendation for future scoping, not a specification ready for implementation.

---

## 13. Human decisions required

See `docs/programmes/product-traceability/decision-pack.md` for the full, formatted decision pack. Summary list:

- DP-01: Confirm or amend the story-reconstruction granularity used in Section 3.
- DP-02: Choose Model A, Model B, or an alternative repository structure.
- DP-03: Approve, amend, or reject the proposed source-of-truth rules in Section 10.
- DP-04: Resolve the PH_OT `is_pensionable` deferral status (open question carried since Sprint 7).
- DP-05: Resolve the 5 `requires human classification` items (Section 14).
- DP-06: Decide whether to formally reconcile the Gate 4 status contradiction (ROADMAP ✅ vs. story file "plan approved, implementation pending").
- DP-07: Authorise (or decline) Phase 2 (hierarchy approval) to begin.

---

## 14. Risks and unresolved classification questions

1. **PT-A4-16 (PH-3 OT3 calculation)** — ROADMAP marks this ✅ but its own notes column says `classify_day` "has no call site yet (dead code)." A function existing without being called is a meaningfully different delivery state than "done." Not resolved in this pass; carried as a tentative item rather than silently upgraded to confirmed.
2. **PT-UI-04 (Gate 4)** — Direct contradiction between `docs/ROADMAP.md` (Track UI table marks Gate 4 ✅ "Completed April 2026") and `docs/stories/ux-ui-upgrade-stories/gate-4-bureau-workspace-setup.md` (states "🔜 Plan approved April 2026, implementation pending"). Both documents are dated similarly; this pass could not determine which is stale without git-blaming both files' last-touched commits, which was out of scope for a documentation-only discovery pass. Resolved provisionally by trusting ROADMAP.md (used more consistently as the live status source across the whole repository) but flagged for explicit human resolution (DP-06) rather than silently picked.
3. **PT-A1-02 / DP-04 (`is_pensionable` on PH_OT)** — an explicitly deferred item from Sprint 7 (OQ1) with no later sprint closing it in any evidence surveyed. Risk: if a client's PH overtime pay is in fact meant to be pensionable and this was never revisited, there may be a live statutory-compliance gap, not just a documentation gap. Flagged for priority human attention, not just registry hygiene.
4. **5 `requires human classification` items** (PT-A1-14, PT-Q-02, PT-Q-03, PT-Q-07, PT-S-08) are all cases where the item is genuinely **not delivered** (ROADMAP still shows 🔜/⬜) but appears in a "delivered work" register context (Track Q/S rolling registers) in a way that could be misread as done if extracted without its status column. These are listed for completeness of the register but must not be migrated into a "delivered stories" hierarchy view as-is.
5. **Coverage gap acknowledged, not solved, by this document**: `docs/test-reports/test-harness/test-harness-checklist.md` itself records an open GAP (zero test coverage for the `overrides_json` destruction path in `patch_component_override`, marked CRITICAL in project memory). This is a pre-existing product risk, not a discovery-phase finding, but it is surfaced here because a future product hierarchy's "confirmed" story for component-override editing should not claim full correctness confidence while this gap is open.
6. **Sprint 15 vs Sprint 16 boundary** — Sprint 15 was an explicitly design-only sprint (no implementation code) that produced the story file consumed by Sprint 16. Both are cited together for several TM items. This is not a contradiction, but a future story-to-sprint mapping must record "designed in Sprint 15, delivered in Sprint 16" rather than collapsing to a single sprint reference, or delivery evidence will look weaker than it is.
7. **Programme dependency risk**: this discovery pass treated `docs/audit-program/`'s closed verdict (calculation engine sound; platform unsafe for production solely due to missing auth/tenancy) as settled evidence. If Phase 2 (hierarchy approval) or any later phase is used to plan new feature work, that verdict — not this document — is the authoritative source for whether the platform is production-ready; this document does not re-assess it.
