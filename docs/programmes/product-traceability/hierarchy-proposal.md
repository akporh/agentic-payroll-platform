# Hierarchy Proposal — Phase 3B, Stage 1

**Programme:** `product-traceability` · **Phase:** 3B `hierarchy completion` · **Authorised by:** D-022
**Status:** **PROPOSAL — not adopted.** Nothing in `docs/product/` has been changed. This document exists to be approved, amended or rejected as a whole.
**Date:** 2026-07-28

---

## 1. What this is, and why it exists

Phases 4A and 4B migrated 21 stories and, in doing so, invented only the hierarchy rows needed to hold them: `OUT-3`, `CAP-3`, `FEAT-3`, `FEAT-4` and `FEAT-5` exist because 19 Onboarding stories needed a home. Nobody has ever seen the intended full shape, so there has been nothing to approve and no way to tell whether the tree is a quarter or a tenth complete.

This document proposes the **complete** hierarchy — every outcome, capability and feature — and places **every** item in the 148-item discovery inventory against it, whether or not that item has been migrated or was ever delivered.

Three rules held throughout:

- **Nothing is invented.** Every row traces to the discovery document, `docs/ROADMAP.md`, or a decision already recorded.
- **Nothing is upgraded.** Confidence levels are carried across verbatim; a `tentative` item stays `tentative`.
- **Disagreements are surfaced, not smoothed.** Section 8 lists eight open questions, including one arithmetic discrepancy I could not resolve.

---

## 2. Outcomes — and the `OUT-1/2/3` collision

### The collision

The live registry and the discovery document use the **same identifiers for different outcomes**:

| Live `OUTCOMES.md` | Discovery document §5 |
|---|---|
| `OUT-1` Governed, auditable payroll execution | `OUT-3` |
| `OUT-2` Sustainable delivery process | `OUT-4` |
| `OUT-3` Operationally usable payroll administration | `OUT-2` |
| — | `OUT-1` Accurate, compliant statutory payroll calculation *(never adopted)* |
| — | `OUT-5` AI-assisted payroll operations *(never adopted)* |

Two documents that cite each other, using `OUT-1` to mean two different things. `OUTCOMES.md`'s preamble does record the renumbering, but in prose, in a paragraph most readers will not reach.

### Proposed resolution — keep live numbering, retire the discovery numbering

The **live** registry's numbering is authoritative. The discovery document's `OUT-*` numbering is declared **superseded and historical**, with the mapping table above written into `OUTCOMES.md` as a permanent decode. The two unadopted outcomes are added as new rows, taking the next free numbers.

This is preferred to renumbering the live rows because those three IDs are cited across 21 story files, and because we are already taking one exception to "never renumbered" for stories (D-020) — taking a second, avoidable one for outcomes would make the rule meaningless.

### Proposed outcome set

| ID | Name | Status | Change |
|---|---|---|---|
| `OUT-1` | Governed, auditable payroll execution | `active` | unchanged |
| `OUT-2` | Sustainable delivery process | `active` | unchanged |
| `OUT-3` | Operationally usable payroll administration | `active` | unchanged |
| `OUT-4` | Accurate, compliant statutory payroll calculation | `active` | **new** — discovery `OUT-1`. The single largest cluster of delivered work (A4, A7–A10, Tracks K/L/M); the platform's core reason to exist. It had no home at all in the live registry. |
| `OUT-5` | AI-assisted payroll operations | `planned` | **new** — discovery `OUT-5`. Phase 2 Tracks P/V/W/X/Y. **Zero delivered stories.** Named so the Phase 2 work has somewhere to attach, and so its emptiness is visible rather than implied. |

---

## 3. Capabilities

The discovery document proposed ~9 durable capabilities (§6) but never adopted them. Three live rows exist. Two of those three are problematic:

- **`CAP-1` is named identically to `OUT-1`**, and **`CAP-2` identically to `OUT-2`**. A capability whose name duplicates its parent outcome adds no information — both were created to hold a single pilot story each (`PT-A4-31`, `PT-A4-32`) and were shaped by that batch, not by product logic.

**Proposed fix: rename `CAP-1` and `CAP-2`; keep their IDs.** The ID is the authoritative reference and does not change; `name` is a display field, and `validate_registry.py` already enforces name-sync across the registries. No re-keying, no broken references.

| ID | Name | Type | Outcome | ROADMAP area | Change |
|---|---|---|---|---|---|
| `CAP-1` | Correctness, Audit & Snapshot | durable | `OUT-1` | A7–A10, Track Q | **renamed** from "Governed, auditable payroll execution" |
| `CAP-2` | Security & Compliance Hardening | durable | `OUT-2` | Track S | **renamed** from "Sustainable delivery process" |
| `CAP-3` | Onboarding & Workspace Setup | durable | `OUT-3` | A1 (config side) | **narrowed** — employee-lifecycle work moves to `CAP-4` |
| `CAP-4` | Employee Lifecycle Management | durable | `OUT-3` | A2 | **new** |
| `CAP-5` | Pay Events & Inputs | durable | `OUT-3` | A3 | **new** |
| `CAP-6` | Execution Engine | durable | `OUT-4` | A4 | **new** |
| `CAP-7` | Governance & Run State Machine | durable | `OUT-1` | A5 | **new** |
| `CAP-8` | Disbursement & Exports | durable | `OUT-1` | A6 | **new** |
| `CAP-9` | Design System & Navigation | durable | `OUT-3` | Track UI | **new** |
| `CAP-10` | Delivery Infrastructure | durable | `OUT-2` | CI / test harness | **new** |
| `CAP-11` | Programme Governance & Assurance | durable | `OUT-2` | audit-program, arch-review, ICM | **new** |
| `CAP-12` | Agent Layer | durable | `OUT-5` | Tracks P/V/W/X/Y | **new, `planned`, zero stories** |

**On `CAP-3`'s narrowing:** A1+A2 is one column in `docs/ROADMAP.md` but two genuinely different product areas — configuring a workspace, and managing the people in it. It is also by far the largest area (47 of 149 items). The discovery document proposed both "Workspace & Workforce Setup" *and* "Employee Lifecycle Management" as separate durable capabilities; this follows that proposal. Consequence: `FEAT-4` moves from `CAP-3` to `CAP-4`, and some of its current stories move to new features (§4).

**Delivery-type capabilities (`EPIC-*`):** the `durable`/`delivery` split fixed by D-008 is retained in the schema, but **no `EPIC-*` row is proposed**. Sprint and track membership is already captured per story in `sprint_refs`, and creating ~33 epic rows that duplicate it would add maintenance burden without answering a question the registry cannot already answer. Recommended as a **deliberate non-adoption**, not an oversight — flagged as OQ-7 for your ruling.

---

## 4. Features

41 features across 11 populated capabilities. Live `FEAT-1`–`FEAT-5` are retained by ID; two are re-scoped as noted.

### `CAP-3` Onboarding & Workspace Setup
| ID | Name | Scope |
|---|---|---|
| `FEAT-3` | Post-onboarding configuration management | *(live)* Editing grades, designations, salary definitions, rules, statutory overrides and pay cycles after onboarding — Track J |
| `FEAT-5` | Attendance & timesheet configuration | *(live)* Workspace-level attendance codes, policies and timesheet setup |
| `FEAT-6` | Client onboarding & workspace creation | Workspace creation, country-code validation, pay-cycle guards, onboarding Excel ingestion |
| `FEAT-7` | Public holiday & rate-code configuration | PH engine, `rate_code_registry`, OT multiplier seeding, PH mode config |

### `CAP-4` Employee Lifecycle Management
| ID | Name | Scope |
|---|---|---|
| `FEAT-4` | Employee records & CRUD | *(live, re-scoped)* Employee schema, grade percentage structure, CRUD API, unified creation path, register/edit forms |
| `FEAT-8` | Enrollment & payroll readiness | Enrollment flow, pre-population, readiness badges, activation CTAs |
| `FEAT-9` | Employee status & lifecycle actions | ACTIVE/INACTIVE toggle, payroll-exclusion warnings, row-level payroll actions |
| `FEAT-10` | Bulk employee upload & import | Smart upload, alias header detection, upload/enroll separation |
| `FEAT-11` | Employee page UX | Split row actions, contract-date display, colour-coded warnings, mid-period hire warnings, mismatch badge |

### `CAP-5` Pay Events & Inputs
| ID | Name | Scope |
|---|---|---|
| `FEAT-12` | Payroll input capture & validation | Input codes, staging, negative-quantity guards, future-input blocking, multi-row entry |
| `FEAT-13` | Timesheet capture & derivation | Upload, parsing, employee matching, three-step cap formula, manual OT override, approval flow, audit trail |
| `FEAT-14` | Bulk input upload & reconciliation intake | Smart period-input upload, idempotency, reconciliation file upload and comparison |

### `CAP-6` Execution Engine
| ID | Name | Scope |
|---|---|---|
| `FEAT-18` | Core calculation & component execution | Component execution order, input claiming, period context freeze, Decimal precision |
| `FEAT-19` | Statutory deduction correctness | PAYE on taxable income, NHF/health/levy, non-taxable class, PAYE-only additions, check-off dues, NSITF/ITF, life insurance |
| `FEAT-20` | Proration & period handling | Partial-period proration, workspace-configurable hire/termination strategy |
| `FEAT-21` | Overtime, shift & public-holiday pay | PH-aware expected hours/days, OT3, manual OT adjustment, shift-gated OT, PH warnings |
| `FEAT-22` | Rule resolution & versioning behaviour | Historical rate resolution, date-aware rule lookup, legacy fallback, DISTINCT ON date cap |
| `FEAT-23` | Run retry & recovery | Per-employee retry, total recalculation, retry audit writes, retry-path rate fixes |
| `FEAT-24` | Engine defect remediation | Track A mandatory fixes; GAP-2, GAP-5, `fixed_amount` fallback |
| `FEAT-25` | Execution observability | Execution trace and timeline view |

### `CAP-1` Correctness, Audit & Snapshot
| ID | Name | Scope |
|---|---|---|
| `FEAT-1` | Payroll calculation trace auditability | *(live)* `component_trace_jsonb`, `component_source`, trace-header fields, per-employee calculation steps |
| `FEAT-26` | Period & rule snapshot integrity | `rule_set` effective-from, frozen `proration_strategy`, retry context from snapshot |
| `FEAT-27` | Audit-observation remediation | Closing Track Q audit findings (e.g. APPROVED timesheet re-upload guard) |
| `FEAT-28` | Legacy executor observability | Deprecation warnings and metrics on the legacy executor path |

### `CAP-7` Governance & Run State Machine
| ID | Name | Scope |
|---|---|---|
| `FEAT-29` | Run state machine & approval | Forward-only progression, DB trigger enforcement, dedup, Approve/Lock/Mark-paid |
| `FEAT-30` | Audit trail & actor attribution | Audit log and event store reads, `X-Performed-By`, approver identity |
| `FEAT-31` | Statutory & payroll rule versioning | Statutory `effective_from` UNIQUE, rule versioning + auto-publish, WITHDRAWN status |

### `CAP-8` Disbursement & Exports
| ID | Name | Scope |
|---|---|---|
| `FEAT-32` | Payroll reconciliation | Status view, LOCKED/PAID gating, duplicate handling, MISMATCH correction |
| `FEAT-33` | Payment & statutory exports | Bank upload, PAYE remittance, pension schedule, full payroll detail |

### `CAP-2` Security & Compliance Hardening
| ID | Name | Scope |
|---|---|---|
| `FEAT-2` | File upload security controls | *(live)* Server-side size and validity guards on upload endpoints |
| `FEAT-34` | Input validation & enum guards | Allowlist validation, enum/length guards, generic error messages, logging hygiene |
| `FEAT-35` | Workspace isolation & data scoping | Workspace-scoped queries; cross-workspace leakage fixes |
| `FEAT-36` | Dependency & supply-chain hygiene | Pinning and dependency management |

### `CAP-9` Design System & Navigation
| ID | Name | Scope |
|---|---|---|
| `FEAT-15` | Design system foundations | Design brief, tokens, 45-component library |
| `FEAT-16` | Operator & bureau journeys | Gate 3 operator journey, Gate 4 bureau setup, Gate 6 config overhaul |
| `FEAT-17` | Navigation & information architecture | Nav modernisation, Rate Codes page, stale-copy cleanup |

### `CAP-10` Delivery Infrastructure
| ID | Name | Scope |
|---|---|---|
| `FEAT-37` | Test harness & regression coverage | Fixture scaffold, financial-engine tests, API/migration tests, async-contract rewrites |
| `FEAT-38` | CI/CD pipeline & branch protection | Branch cleanup, CI gate, pre-push hook, fresh-migrated Postgres |
| `FEAT-39` | Code simplification & technical debt | Deferred `/simplify` items, script hygiene |

### `CAP-11` Programme Governance & Assurance
| ID | Name | Scope |
|---|---|---|
| `FEAT-40` | Independent review programmes | `audit-program`, `agentic-architecture-review` |
| `FEAT-41` | Sprint workflow model | ICM `STAGE-REGISTRY.md` / `WORKFLOW.md` |

---

## 5. Story ID allocation and feature assignment

Per D-019: seed allocation runs in **chronological delivery order**, ties broken by capability area then original inventory ID. The ID is a handle — chronology is carried by `sprint_refs` and is sortable independently. **`M` = already migrated** into `docs/product/` (21 items).

### Sprint 0 — Foundation
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0001` | PT-A3-01 | List valid/unclaimed input codes; delete staged input; download template | `FEAT-12` | tentative | |
| `STORY-0002` | PT-A3-02 | Stage input against specific past month / period-agnostic | `FEAT-12` | tentative | |
| `STORY-0003` | PT-A3-03 | Block future inputs from being claimed | `FEAT-12` | tentative | |
| `STORY-0004` | PT-A4-01 | Claim variable inputs at run time; canonical component execution order | `FEAT-18` | tentative | |
| `STORY-0005` | PT-A4-02 | Prorate pay for partial-period employees | `FEAT-20` | tentative | |
| `STORY-0006` | PT-A4-03 | Freeze period context at run start; Decimal precision | `FEAT-18` | tentative | |
| `STORY-0007` | PT-A4-04 | PAYE computed on taxable income not gross | `FEAT-19` | tentative | |
| `STORY-0008` | PT-A5-01 | State-machine enforcement, forward-only progression, initial DRAFT | `FEAT-29` | tentative | |
| `STORY-0009` | PT-A5-02 | Dedup runs by idempotency key/period; dedup per-employee results | `FEAT-29` | tentative | |
| `STORY-0010` | PT-A6-01 | Reconciliation status view | `FEAT-32` | tentative | |

### Sprints 1–6 — Core MVP
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0011` | PT-A1-03 | Workspace creation + country-code statutory-rule validation (P3-7) | `FEAT-6` | strongly inferred | |
| `STORY-0012` | PT-A1-04 | Component overrides update endpoint (P1-8) | `FEAT-3` | strongly inferred | |
| `STORY-0013` | PT-A1-05 | Active pay-cycle guard, one active per workspace (PC4) | `FEAT-6` | strongly inferred | |
| `STORY-0014` | PT-A1-06 | Payroll rules as a standalone form, not raw JSON (P3-1) | `FEAT-3` | strongly inferred | |
| `STORY-0015` | PT-A1-12 | Salary definition effective-date enforcement at run time (P3-5) | `FEAT-3` | strongly inferred | |
| `STORY-0016` | PT-A3-04 | Single payroll input negative-quantity guard (INP10/P3-4) | `FEAT-12` | strongly inferred | |
| `STORY-0017` | PT-A3-05 | Bulk upload inputs with dedup guard (P3-3) | `FEAT-14` | strongly inferred | |
| `STORY-0018` | PT-A4-05 | Run payroll with period_type/working_days_override/retry_strategy UI (P1-7) | `FEAT-18` | strongly inferred | |
| `STORY-0019` | PT-A4-06 | Historical input-rate resolution with fallback flagging (P2-7) | `FEAT-22` | strongly inferred | |
| `STORY-0020` | PT-A4-07 | Retry failed employees; full-run retry; retry recalculates totals (P0-2/P1-1) | `FEAT-23` | strongly inferred | |
| `STORY-0021` | PT-A4-08 | Retry writes to audit_log + event_store (P2-3) | `FEAT-23` | strongly inferred | |
| `STORY-0022` | PT-A4-09 | Execution trace/timeline view (P1-6) | `FEAT-25` | strongly inferred | |
| `STORY-0023` | PT-A4-10 | NHF key fix, employee_rate (SR9) | `FEAT-19` | strongly inferred | |
| `STORY-0024` | PT-A5-03 | Approve/Lock/Mark-paid UI buttons (P0-1) | `FEAT-29` | strongly inferred | |
| `STORY-0025` | PT-A5-04 | Read run audit trail + event store history (P2-1) | `FEAT-30` | strongly inferred | |
| `STORY-0026` | PT-A5-05 | Statutory rule effective_from UNIQUE constraint (G7) | `FEAT-31` | strongly inferred | |
| `STORY-0027` | PT-A6-02 | Reconciliation gated to LOCKED/PAID; duplicate 409 not 500 (P0-4/P0-5) | `FEAT-32` | strongly inferred | |
| `STORY-0028` | PT-A6-03 | Correct a MISMATCH — RESOLVED status + PATCH (RC5) | `FEAT-32` | strongly inferred | |
| `STORY-0029` | PT-A7-01 | Component-level calculation trace in UI; rule trace (P2-4/P2-7) | `FEAT-1` | strongly inferred | |
| `STORY-0030` | PT-A7-02 | rule_set effective_from UNIQUE; cross-period rule set access (P2-6) | `FEAT-26` | strongly inferred | |
| `STORY-0031` | PT-A7-03 | Per-employee calculation steps snapshot, component_trace_jsonb (P2-4) | `FEAT-1` | strongly inferred | |
| `STORY-0032` | PT-A7-04 | Legacy executor observability — deprecation warning + metrics (G12) | `FEAT-28` | strongly inferred | |

### Sprint 7 — including Track A defect fixes
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0033` | PT-A3-06 | Quantity ≥ 0 DB CHECK constraint on `payroll_input` (INP10) | `FEAT-12` | strongly inferred | |
| `STORY-0034` | PT-A4-14 | Track A mandatory defect fixes (FIX-1–5) | `FEAT-24` | strongly inferred | |
| `STORY-0035` | PT-A1-01 | Workspace-configurable public-holiday engine (PH-1…PH-11) | `FEAT-7` | strongly inferred | |
| `STORY-0036` | PT-A1-02 | Rate code registry + OT multiplier seeding (PH-7) | `FEAT-7` | strongly inferred | |
| `STORY-0037` | PT-A4-15 | PH-2/PH-9: expected_hours/expected_days computed PH-aware | `FEAT-21` | strongly inferred | |
| `STORY-0038` | PT-A4-16 | PH-3/PH-4: OT3 3.25× calculation flowing into GROSS_PAY/PAYE | `FEAT-21` | **tentative** — `classify_day` marked ✅ but noted as dead code | |
| `STORY-0039` | PT-A4-17 | PH-5: Manual OT3 adjustment with floor validation | `FEAT-21` | strongly inferred | |
| `STORY-0040` | PT-A4-18 | PH-10/PH-11: PH count-mismatch warnings + pre-flight check | `FEAT-21` | strongly inferred | |
| `STORY-0041` | PT-A5-06 | X-Performed-By header read on approve/lock/retry routes (P2-2) | `FEAT-30` | **tentative** — backend reads, frontend never sends | |
| `STORY-0042` | PT-A7-09 | Snapshot expected_days/ph_dates_used/ph_source in trace header (PH-9) | `FEAT-1` | strongly inferred | |
| `STORY-0043` | PT-A7-10 | Retry context carries OT/PH keys from snapshot (FIX-5) | `FEAT-26` | strongly inferred | |

### Track UI Gates 1–2 (April 2026)
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0044` | PT-UI-01 | Gate 1 — UX/UI design brief, 18 decisions, 45-component inventory | `FEAT-15` | strongly inferred | |
| `STORY-0045` | PT-UI-02 | Gate 2 — Design system tokens + 45 React components | `FEAT-15` | strongly inferred | |

### Track J / Gate 6 — Post-onboarding config (2026-04-21)
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0046` | PT-A1-07 | WC-1: Pay-cycle post-setup update endpoint | `FEAT-3` | confirmed | M |
| `STORY-0047` | PT-A1-08 | WC-2/3/4/5: Grade/designation add + edit via UI | `FEAT-3` | confirmed | M |
| `STORY-0048` | PT-A1-09 | WC-6/7: Salary definition add + edit via UI | `FEAT-3` | confirmed | M |
| `STORY-0049` | PT-A1-10 | WC-8: Payroll rule active/inactive control via UI | `FEAT-3` | confirmed | M |
| `STORY-0050` | PT-A1-11 | WC-10/11: Statutory component override edit/toggle via UI | `FEAT-3` | confirmed | M |
| `STORY-0051` | PT-A1-15 | `client_component_metadata` add `is_active` + `proration_strategy` | `FEAT-3` | confirmed | M |
| `STORY-0052` | PT-A1-16 | Statutory component hard reject on override PATCH (D-ARCH-2) | `FEAT-3` | confirmed | M |
| `STORY-0053` | PT-A1-17 | Extend `/configuration` GET with IDs/is_active/proration_strategy | `FEAT-3` | confirmed | M |
| `STORY-0054` | PT-A1-18 | WorkspaceConfig.tsx full interactive overhaul (Gate 6) | `FEAT-3` | confirmed | M |
| `STORY-0055` | PT-UI-06 | Gate 6 — Post-onboarding config management overhaul (frontend) | `FEAT-16` | confirmed | |
| `STORY-0056` | PT-UI-03 | Gate 3 — Operator journey, 6 screens + 6 amendments | `FEAT-16` | strongly inferred | |
| `STORY-0057` | PT-UI-04 | Gate 4 — Bureau/workspace-setup journey, 8 pages | `FEAT-16` | **tentative** — ROADMAP ✅ vs story file "implementation pending" (D-012) | |

### Sprint 9 — Client B
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0058` | PT-A6-07 | Export full payroll detail (S9-1/S9-2) | `FEAT-33` | strongly inferred | |

### Sprint 10 — Client B fixes, exports, onboarding integration
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0059` | PT-A1-13 | ot_multiplier rules onboarding via Excel/JSON (PH-8/WI-05) | `FEAT-7` | strongly inferred | |
| `STORY-0060` | PT-A1-43 | WorkspacePayrollConfig onboarding integration, 7th Excel sheet (WI-06/H2) | `FEAT-6` | strongly inferred | |
| `STORY-0061` | PT-A1-44 | PH_ADDITIVE removed from UI, fallback to LEAVE_ABSORBS_PH (WI-12) | `FEAT-7` | strongly inferred | |
| `STORY-0062` | PT-A1-45 | OT multiplier seed correction (WI-01) | `FEAT-7` | **tentative** — closed by confirming a non-defect | |
| `STORY-0063` | PT-A1-46 | `ot_code`→`rate_code` normalisation (WI-02) | `FEAT-7` | strongly inferred | |
| `STORY-0064` | PT-A1-47 | Excel `ot_multiplier` rule-type parsing (WI-05) | `FEAT-7` | strongly inferred | |
| `STORY-0065` | PT-A4-11 | GAP-2: remove double-subtraction of PH days in AUTOMATIC mode | `FEAT-24` | confirmed | |
| `STORY-0066` | PT-A4-12 | GAP-5: PAYE CUSTOM annualization ×12 fix | `FEAT-24` | confirmed | |
| `STORY-0067` | PT-A4-13 | `fixed_amount` component_source fallback fix (WI-04a) | `FEAT-24` | confirmed | |
| `STORY-0068` | PT-A6-04 | Export net pay for bank upload (P0-3) | `FEAT-33` | confirmed | |
| `STORY-0069` | PT-A6-05 | Export PAYE remittance schedule (P1-4) | `FEAT-33` | confirmed | |
| `STORY-0070` | PT-A6-06 | Export pension contribution schedule (P1-5) | `FEAT-33` | confirmed | |

### Sprint 11 — Employee schema & shift gating
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0071` | PT-A1-19 | Employee schema: shift_type, state_of_tax, skill_level (NEW-GAP4/13) | `FEAT-4` | confirmed | M |
| `STORY-0072` | PT-A1-20 | Grade percentage structure (NEW-GAP12) | `FEAT-4` | confirmed | M |
| `STORY-0073` | PT-A4-19 | Shift-gated OT rule; shift_type threaded per employee (WI-04b) | `FEAT-21` | confirmed | |
| `STORY-0074` | PT-A4-20 | Retry-path input/rate-code fixes | `FEAT-23` | confirmed | |
| `STORY-0075` | PT-A7-05 | shift_type/salary_basis added to `_period_context` (AUD-4/Q4) | `FEAT-1` | confirmed | |
| `STORY-0076` | PT-S-04 | SEC-S4: workspace_id filter on grade query, leakage fix | `FEAT-35` | confirmed | |
| `STORY-0077` | PT-S-05 | SEC-S5: shift_type/state_of_tax/skill_level enum + length guards | `FEAT-34` | confirmed | |

### Sprint 12
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0078` | PT-A4-21 | Non-taxable component class (NEW-GAP14/M1) | `FEAT-19` | confirmed | |
| `STORY-0079` | PT-A4-22 | PAYE-only additions path, input_category (NEW-GAP15/M2) | `FEAT-19` | confirmed | |

### Sprint 13
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0080` | PT-A4-23 | Check-off dues handler, percentage_of_sum (NEW-GAP6/M3) | `FEAT-19` | confirmed | |
| `STORY-0081` | PT-A4-24 | Life insurance flat-amount handler (GAP-10-FIX/M4) | `FEAT-19` | strongly inferred | |
| `STORY-0082` | PT-A4-25 | NSITF/ITF employer-cost handlers, threshold-gated (NEW-GAP7/M5) | `FEAT-19` | strongly inferred | |
| `STORY-0083` | PT-S-01 | SEC-S1: generic message + server-side log for `_wpc_err!s` | `FEAT-34` | strongly inferred | |
| `STORY-0084` | PT-S-02 | SEC-S2: allowlist validation for `workspace_payroll_config` enums | `FEAT-34` | strongly inferred | |
| `STORY-0085` | PT-S-03 | SEC-S3: module-level logging import fix | `FEAT-34` | strongly inferred | |

### Sprint 14
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0086` | PT-A4-26 | Workspace-configurable hire/termination proration (P1) | `FEAT-20` | confirmed | |
| `STORY-0087` | PT-S-06 | SEC-S6: `proration_strategy` enum validation, API guard | `FEAT-34` | **tentative** — partially delivered; DB constraint still open | |

### Sprint 15 (design) / Sprint 16 (delivery) — Timesheet layer
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0088` | PT-A1-42 | Workspace timesheet configuration + attendance code seeding (TM-1) | `FEAT-5` | confirmed | M |
| `STORY-0089` | PT-A1-41 | Attendance code + policy configuration, CRUD + immutability (TM-7) | `FEAT-5` | confirmed | M |
| `STORY-0090` | PT-A3-07 | Timesheet upload — parsing, matching, code validation, PH header (TM-2) | `FEAT-13` | confirmed | |
| `STORY-0091` | PT-A3-08 | Timesheet derivation — three-step cap formula (TM-3) | `FEAT-13` | confirmed — client-validated against spreadsheet | |
| `STORY-0092` | PT-A3-09 | Manual OT override, source=MANUAL_OT (TM-4) | `FEAT-13` | confirmed | |
| `STORY-0093` | PT-A3-10 | Timesheet-to-pay-instruction flow, atomic approval + readiness gate (TM-5) | `FEAT-13` | confirmed | |
| `STORY-0094` | PT-A3-11 | Timesheet audit trail — derivation summary, policy snapshot, per-day grid (TM-6) | `FEAT-13` | confirmed | |
| `STORY-0095` | PT-A3-12 | Per-employee expected_hours from shift_type (C1) | `FEAT-13` | confirmed | |
| `STORY-0096` | PT-A3-13 | Timesheet completeness gate before link_inputs_to_run (C2) | `FEAT-13` | confirmed | |
| `STORY-0097` | PT-A7-06 | timesheet_source added to `_period_context` (AUD-16-3/Q5) | `FEAT-1` | confirmed | |
| `STORY-0098` | PT-UI-05 | Gate 5 — Navigation modernisation + Rate Codes page (UI-NAV-1/2/3) | `FEAT-17` | confirmed | |

### 2026-05-26 — Retrospective delivery increment
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0099` | PT-A1-28 | Employee page enhancements: contract dates, colour-coded warnings | `FEAT-11` | confirmed | M |
| `STORY-0100` | PT-A1-29 | Nav reorder + employee-mismatch badge | `FEAT-11` | strongly inferred | |

### Sprint 17 — Employee lifecycle refactor (2026-05-27)
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0101` | PT-A1-21 | Employee CRUD API + D-ARCH-1 run-lock/backdating guard (B1) | `FEAT-4` | confirmed | M |
| `STORY-0102` | PT-A1-22 | Unified employee creation path via `employee_repo` (B2) | `FEAT-4` | confirmed | M |
| `STORY-0103` | PT-A1-23 | Employees.tsx split-action rework (B3) | `FEAT-11` | **tentative** — browser UAT BLOCKED | |
| `STORY-0104` | PT-A1-24 | Fix LATERAL join bugs in readiness + timesheet derivation (B0a/B0b) | `FEAT-8` | **mixed** — confirmed B0a, tentative B0b | |
| `STORY-0105` | PT-A1-25 | Split Edit vs Change Grade/Salary row action (EMP-UX-1) | `FEAT-11` | confirmed | M |
| `STORY-0106` | PT-A1-26 | Mid-period hire warning in AddEmployeeSlideOver (EMP-UX-3) | `FEAT-11` | strongly inferred | |
| `STORY-0107` | PT-A1-27 | Payroll Inputs issues badge (EMP-UX-4) | `FEAT-11` | strongly inferred | |

### Sprint 22 — Bulk upload / enroll separation
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0108` | PT-A1-40 | Bulk upload / bulk enroll separation (EMP-BULK-1/2/3) | `FEAT-10` | strongly inferred | |

### Sprint 24 — Enrollment UX clarity + audit fixes
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0109` | PT-A1-30 | AlertBanner + nav badge when canEnroll=false (EMP-UX-5) | `FEAT-8` | strongly inferred | |
| `STORY-0110` | PT-A7-07 | Guard APPROVED timesheet re-upload (Q6-FIX) | `FEAT-27` | confirmed | |
| `STORY-0111` | PT-A7-08 | `proration_strategy` frozen in snapshot, no-code close (Q8-FIX) | `FEAT-26` | confirmed — closed by confirming existing behaviour | |

### Sprint 26 — Employee registration & status management
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0112` | PT-A1-31 | Enrollment auto-suggest salary def from grade label (EMP-ENROLL-AUTODEF-1) | `FEAT-8` | strongly inferred | |
| `STORY-0113` | PT-A1-32 | Register new employee full form (EMP-REG-1) | `FEAT-4` | strongly inferred | |
| `STORY-0114` | PT-A1-33 | Edit employee — name/number/TIN/RSA/bank (EMP-EDIT-1) | `FEAT-4` | strongly inferred | |
| `STORY-0115` | PT-A1-34 | Status toggle ACTIVE↔INACTIVE with payroll-exclusion warning (EMP-STATUS-1) | `FEAT-9` | strongly inferred | |
| `STORY-0116` | PT-A1-35 | Per-row payroll readiness badge (EMP-BADGE-1) | `FEAT-8` | strongly inferred | |
| `STORY-0117` | PT-A1-36 | Consistent icon set + payroll actions from row (EMP-ICONS-1, EMP-PAYROLL-ACTIONS-1) | `FEAT-9` | strongly inferred | |

### Sprint 27 — Smart native upload
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0118` | PT-A1-37 | Smart employee upload — alias header detection, mapping panel (EMP-NATIVE-1) | `FEAT-10` | strongly inferred | |
| `STORY-0119` | PT-A3-14 | Smart period-inputs upload — header parsing, @rate derivation, dedup (INP-NATIVE-1) | `FEAT-14` | strongly inferred | |
| `STORY-0120` | PT-A3-15 | Multi-row period input entry SlideOver (INP-MULTI-1) | `FEAT-12` | strongly inferred | |
| `STORY-0121` | PT-A3-17 | Payroll reconciliation upload — mapping, comparison, mismatch filter (PAY-RECON-1) | `FEAT-14` | strongly inferred | |

### Sprint 28 — Upload error visibility
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0122` | PT-A3-16 | Period-inputs bulk upload idempotency — IntegrityError→skip (UPLOAD-SKIP-1) | `FEAT-14` | strongly inferred | |

### 2026-06 — Fix sprints
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0123` | PT-A1-38 | Enrollment pre-population normalisation fix (EMP-REG-5) | `FEAT-8` | confirmed | M |
| `STORY-0124` | PT-A1-39 | Workspace activation CTA reachable from 3 landing points | `FEAT-8` | confirmed | M |

### Sprint RULE-VER-1 (2026-06-21)
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0125` | PT-A5-07 | Payroll rule versioning: effective_from, auto-publish, UNIQUE (RULE-VER-1/2/3) | `FEAT-31` | confirmed | |

### Sprint A (2026-07-04) — Rule versioning integrity
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0126` | PT-A4-28 | Date-aware payroll-input-codes-by-date endpoint | `FEAT-22` | strongly inferred | |
| `STORY-0127` | PT-A4-29 | Legacy-workspace historical fallback in cross-period prefetch | `FEAT-22` | confirmed | |
| `STORY-0128` | PT-A4-30 | Date cap + DISTINCT ON on legacy current-period rule loader | `FEAT-22` | confirmed | |

### Sprint B-UI — Rule versioning copy cleanup
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0129` | PT-A5-08 | WITHDRAWN status badge + one-way withdraw action (B-UI-1/2/3) | `FEAT-31` | confirmed | |
| `STORY-0130` | PT-UI-07 | B-UI-4/5 — stale copy/banner cleanup on Payroll Rules tab | `FEAT-17` | confirmed | |

### Sprints 29–32 — Delivery infrastructure
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0131` | PT-X-01 | Dead branch cleanup, CI gate on merge, branch protection (PIPE-1/2/3) | `FEAT-38` | strongly inferred | |
| `STORY-0132` | PT-X-02 | Test-fixture scaffold: conftest, db/workspace/employee fixtures (HARN-1) | `FEAT-37` | strongly inferred | |
| `STORY-0133` | PT-A7-11 | Test harness baseline + regression-gap audit | `FEAT-37` | confirmed — documents one open GAP (`overrides_json`) | |
| `STORY-0134` | PT-A7-12 | Financial-engine unit test suite, all 6 calculation methods (TEST-A1) | `FEAT-37` | strongly inferred | |
| `STORY-0135` | PT-A7-13 | API/migration integration tests, workspace-isolation assertions | `FEAT-37` | strongly inferred | |

### 2026-07-11/12 — Test harness workstream
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0136` | PT-X-03 | Pre-push hook + CI workflow against fresh-migrated Postgres | `FEAT-38` | confirmed | |
| `STORY-0137` | PT-A7-14 | 4 stale async-contract e2e tests rewritten (TF-3–TF-7) | `FEAT-37` | confirmed — commit `2a069d6` | |

### ICM sprints (2026-07-12 / 07-13)
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0138` | PT-A4-31 *(= PT-Q-01)* | AUD-1/Q1: `component_source` on `fixed_amount` trace fallback | `FEAT-1` | confirmed | M |
| `STORY-0139` | PT-A4-32 *(= PT-S-07)* | SEC-S7: 10 MB server-side timesheet upload size guard | `FEAT-2` | confirmed | M |

### Programme-level meta-work
| New ID | Origin | Title | Feature | Confidence | M |
|---|---|---|---|---|---|
| `STORY-0140` | PT-M-01 | `docs/audit-program/` — 13-stage Phase 1 audit, closed with 4 decisions | `FEAT-40` | confirmed | |
| `STORY-0141` | PT-M-02 | `agentic-architecture-review` — 13-stage Phase 2 review | `FEAT-40` | confirmed — **in progress, not delivered** | |
| `STORY-0142` | PT-M-03 | ICM sprint-workflow model (`STAGE-REGISTRY.md`, `WORKFLOW.md`) | `FEAT-41` | confirmed | |

### Not delivered — backlog (allocated IDs so coverage is complete)
Per D-011 these are **backlog, not delivered**. They receive IDs so that the tree is complete and they can never be mistaken for delivered work by omission.

| New ID | Origin | Title | Feature | Status | M |
|---|---|---|---|---|---|
| `STORY-0143` | PT-A1-14 | Client 3 shift allowance onboarding (SHIFT2/3/4) | `FEAT-7` | backlog | |
| `STORY-0144` | PT-Q-02 | AUD-2/Q2: period_type on payroll_run, passed to retry context | `FEAT-23` | backlog | |
| `STORY-0145` | PT-Q-03 | AUD-3/Q3: simulate script `Decimal(str(...))` conversion | `FEAT-39` | backlog | |
| `STORY-0146` | PT-Q-07 | AUD-16-1/Q7: no approved_by actor identity on timesheet transitions | `FEAT-30` | backlog — deferred to Track P (auth) | |
| `STORY-0147` | PT-S-08 | S8: pin `python-multipart==0.0.28` | `FEAT-36` | backlog | |
| `STORY-0148` | PT-X-04 | Two deferred `/simplify` items (shared date utils, shared get_latest_rule_set) | `FEAT-39` | backlog | |

### Excluded from allocation (with reasons)

| Origin | Reason |
|---|---|
| `PT-A4-27` | Grouping row only — "grouped here only for capability-matrix completeness"; its constituent items are allocated individually under `FEAT-13`. |
| `PT-Q-01`, `PT-Q-04`, `PT-Q-05`, `PT-Q-06`, `PT-Q-08` | Explicit duplicates of `PT-A4-13`/`PT-A4-31`, `PT-A7-05`, `PT-A7-06`, `PT-A7-07`, `PT-A7-08`. The discovery document states these are "not double-counted in the 148 total." |
| `PT-S-07` | Same item as `PT-A4-32` — the duplicate-ID mapping flagged as unresolved in the Phase 4A pilot. **Resolved here:** one story (`STORY-0139`) carrying both origin codes. |
| `PT-M-04` | This programme itself — "not applicable to confidence scoring; it is the artefact producing this inventory, not an inventoried item." |

**This resolves both outstanding duplicate-ID mappings** carried since the Phase 4A pilot (`PT-A4-31`/`PT-Q-01` → `STORY-0138`; `PT-A4-32`/`PT-S-07` → `STORY-0139`), each as a single story with two origin codes.

---

## 6. Coverage

| | Count |
|---|---|
| Items allocated an ID | **148** |
| — delivered | 142 |
| — backlog / not delivered | 6 |
| Already migrated into `docs/product/` | **21** (14%) |
| Remaining to migrate | 127 |
| Excluded as duplicates / grouping rows | 9 |

By confidence (delivered items only, carried across verbatim):

| Confidence | Count | Migrated |
|---|---|---|
| confirmed | 60 | 21 |
| strongly inferred | 65 | 0 |
| tentative | 17 | 0 |

Coverage by capability:

| Capability | Stories | Migrated |
|---|---|---|
| `CAP-1` Correctness, Audit & Snapshot | 12 | 1 |
| `CAP-2` Security & Compliance Hardening | 8 | 1 |
| `CAP-3` Onboarding & Workspace Setup | 24 | 11 |
| `CAP-4` Employee Lifecycle Management | 18 | 8 |
| `CAP-5` Pay Events & Inputs | 20 | 0 |
| `CAP-6` Execution Engine | 27 | 0 |
| `CAP-7` Governance & Run State Machine | 9 | 0 |
| `CAP-8` Disbursement & Exports | 7 | 0 |
| `CAP-9` Design System & Navigation | 7 | 0 |
| `CAP-10` Delivery Infrastructure | 9 | 0 |
| `CAP-11` Programme Governance & Assurance | 3 | 0 |
| `CAP-12` Agent Layer | 0 | 0 |

**The single most useful number here: the Execution Engine — 27 stories, the platform's core reason to exist — has zero migrated coverage**, because the batch rule selected A1+A2. That is exactly the distortion a batch-shaped hierarchy produces and top-down definition prevents.

---

## 7. What changes for the 21 already-migrated stories

| Change | Effect |
|---|---|
| Re-key `PT-*` → `STORY-<nnnn>` | All 21; original codes preserved in `origin_code` |
| `FEAT-4` moves capability | `CAP-3` → `CAP-4` |
| Two stories move feature | `PT-A1-25` and `PT-A1-28` → `FEAT-11`; `PT-A1-38`/`PT-A1-39` → `FEAT-8` |
| `CAP-1`, `CAP-2` renamed | IDs unchanged; display names updated everywhere in one controlled change |
| Parent names added to story files | Completes D-016's convention |
| `origin_code` added | New mandatory field |

No migrated story's *content* changes. No story is un-migrated.

---

## 8. Open questions — for your ruling

| # | Question |
|---|---|
| **OQ-1** | **Item-count discrepancy.** The discovery document states 148 items. Summing its own tables and removing the 9 documented duplicates/grouping rows yields **149**. I have allocated 148 and cannot account for the last one without a line-by-line recount of §3.1–3.11. Recommend: proceed, and reconcile during Stage 3 when each story file is created — the mismatch surfaces itself at that point. |
| **OQ-2** | **Sprint PAY-TAX-1 appears to be missing from the inventory.** `docs/ROADMAP.md` carries "Sprint PAY-TAX-1 — NG PAYE Bands NTA 2025" and `CLAUDE.md` records it closed, but I found no `PT-*` item for it in the discovery inventory. If confirmed, this is a genuine discovery-phase gap, not a hierarchy problem. It would belong to `FEAT-19`. |
| **OQ-3** | **Sprint 25 has no inventory items.** `docs/ROADMAP.md` has a Sprint 25 section (badge real-time update, Employees table UX). No `PT-*` item maps to it. Same question as OQ-2. |
| **OQ-4** | **`CAP-1`/`CAP-2` renaming** — do you accept renaming live capabilities (IDs unchanged) to remove the name-duplication with their outcomes? |
| **OQ-5** | **`CAP-3` narrowing** — do you accept splitting A1+A2 into Onboarding (`CAP-3`) and Employee Lifecycle (`CAP-4`), moving `FEAT-4` across? |
| **OQ-6** | **`OUT-5` / `CAP-12` with zero stories** — keep them as named-but-empty for visibility, or omit until Phase 2 work begins? |
| **OQ-7** | **No `EPIC-*` delivery rows proposed** (§3). Sprint/track membership is already per-story in `sprint_refs`. Accept the non-adoption, or do you want delivery epics as first-class rows? |
| **OQ-8** | **`STORY-0104` (`PT-A1-24`) has mixed confidence** — B0a confirmed, B0b tentative. Split into two stories, or keep as one at the lower confidence? Splitting is a merge/split decision requiring your approval per `POLICY.md`. |

---

## 9. What happens next

Stage 2 renders this as the visual sign-off artefact. **Nothing is applied to `docs/product/` until you approve.** Phase 3B halts at that gate by design.
