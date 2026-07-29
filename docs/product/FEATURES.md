# Features Registry

A feature sits between a capability and a story. Every story maps to exactly one feature.

**Approved as a complete set 2026-07-28 (D-023).** This layer had never existed: the discovery document explicitly deferred defining it (§7–8) until the hierarchy model was approved, and Phases 4A/4B then created only the five features needed to hold their batches' stories. All 41 are now defined together, so feature boundaries come from product logic rather than from what a batch happened to contain.

## Reading the counts

- **`stories`** — the story IDs actually present in `STORY-REGISTRY.md` (i.e. migrated, with a story file). This is the inverse lookup that `story_count` alone could never give you.
- **`migrated`** / **`allocated`** — migrated rows versus total items assigned to this feature in `ID-ALLOCATION.md`. The gap between them *is* the remaining migration backlog. A feature with `0/31` is not empty; it is unmigrated.

**As of 2026-07-29 (D-027) `migrated` equals `allocated` on every row.** There are no allocated-but-unmigrated IDs left; Phase 4 is closed. `CAP-12` Agent Layer holds no features and no stories by design (D-023, OQ-6) — that emptiness is a deliberate, visible gap, not an unmigrated one.

## Human-readable names (D-016)

`capability_name` is display-only — `capability_id` is authoritative. A displayed name must exactly match the current `name` in `CAPABILITIES.md`; `validate_registry.py` enforces this. Never resolve a feature's capability by name.

## Schema

| Column | Meaning |
|---|---|
| `feature_id` | Stable identifier, format `FEAT-<n>`. Never reused, never renumbered. |
| `name` | Short name. |
| `description` | One or two sentences. |
| `capability_id` | The durable `capability_id` this feature belongs to. Authoritative. |
| `capability_name` | Display-only copy of the referenced capability's current `name`. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `stories` | The `story_id`s in `STORY-REGISTRY.md` mapped to this feature. Validator-enforced against the registry, both directions. |
| `migrated` | Count of `stories`. |
| `allocated` | Total items assigned to this feature in `ID-ALLOCATION.md`, migrated or not. |

## Registry

| `feature_id` | `name` | `description` | `capability_id` | `capability_name` | `status` | `stories` | `migrated` | `allocated` |
|---|---|---|---|---|---|---|---|---|
| `FEAT-1` | Payroll calculation trace auditability | Ensuring trace entries name the derivation source for a value, not just the value, so an auditor never needs to re-query live DB state. | `CAP-1` | Correctness, Audit & Snapshot | `active` | `STORY-0029`, `STORY-0031`, `STORY-0042`, `STORY-0075`, `STORY-0097`, `STORY-0145` | 6 | 6 |
| `FEAT-26` | Period & rule snapshot integrity | Freezing the rule set, period context and proration strategy a run was calculated against. | `CAP-1` | Correctness, Audit & Snapshot | `active` | `STORY-0030`, `STORY-0043`, `STORY-0112` | 3 | 3 |
| `FEAT-27` | Audit-observation remediation | Closing Track Q audit findings raised against delivered behaviour. | `CAP-1` | Correctness, Audit & Snapshot | `active` | `STORY-0111` | 1 | 1 |
| `FEAT-28` | Legacy executor observability | Deprecation warnings and metrics on the legacy executor path. | `CAP-1` | Correctness, Audit & Snapshot | `active` | `STORY-0032` | 1 | 1 |
| `FEAT-2` | File upload security controls | Server-side size and validity guards on file-upload endpoints, enforced independently of any client-side check. | `CAP-2` | Security & Compliance Hardening | `active` | `STORY-0146` | 1 | 1 |
| `FEAT-34` | Input validation & enum guards | Allowlist and enum validation, length guards, generic error messages, logging hygiene. | `CAP-2` | Security & Compliance Hardening | `active` | `STORY-0077`, `STORY-0083`, `STORY-0084`, `STORY-0085`, `STORY-0087` | 5 | 5 |
| `FEAT-35` | Workspace isolation & data scoping | Workspace-scoped queries; cross-workspace leakage fixes. | `CAP-2` | Security & Compliance Hardening | `active` | `STORY-0076` | 1 | 1 |
| `FEAT-36` | Dependency & supply-chain hygiene | Dependency pinning and management. | `CAP-2` | Security & Compliance Hardening | `active` | `STORY-0154` | 1 | 1 |
| `FEAT-3` | Post-onboarding configuration management | Editing grades, designations, salary definitions, rules, statutory overrides and pay cycles through a UI after onboarding. Track J. | `CAP-3` | Onboarding & Workspace Setup | `active` | `STORY-0012`, `STORY-0014`, `STORY-0015`, `STORY-0046`, `STORY-0047`, `STORY-0048`, `STORY-0049`, `STORY-0050`, `STORY-0051`, `STORY-0052`, `STORY-0053`, `STORY-0054` | 12 | 12 |
| `FEAT-5` | Attendance & timesheet configuration | Workspace-level attendance codes, policies and timesheet setup — distinct from timesheet processing itself. | `CAP-3` | Onboarding & Workspace Setup | `active` | `STORY-0088`, `STORY-0089` | 2 | 2 |
| `FEAT-6` | Client onboarding & workspace creation | Workspace creation, country-code validation, pay-cycle guards, onboarding Excel ingestion. | `CAP-3` | Onboarding & Workspace Setup | `active` | `STORY-0011`, `STORY-0013`, `STORY-0060` | 3 | 3 |
| `FEAT-7` | Public holiday & rate-code configuration | PH engine, `rate_code_registry`, OT multiplier seeding, PH mode configuration. | `CAP-3` | Onboarding & Workspace Setup | `active` | `STORY-0035`, `STORY-0036`, `STORY-0059`, `STORY-0061`, `STORY-0062`, `STORY-0063`, `STORY-0064`, `STORY-0150` | 8 | 8 |
| `FEAT-4` | Employee records & CRUD | Employee schema, grade percentage structure, CRUD API, unified creation path, register and edit forms. | `CAP-4` | Employee Lifecycle Management | `active` | `STORY-0071`, `STORY-0072`, `STORY-0101`, `STORY-0102`, `STORY-0117`, `STORY-0119`, `STORY-0120` | 7 | 7 |
| `FEAT-8` | Enrollment & payroll readiness | Enrollment flow, pre-population, readiness badges, activation CTAs, readiness-service correctness. | `CAP-4` | Employee Lifecycle Management | `active` | `STORY-0104`, `STORY-0110`, `STORY-0118`, `STORY-0122`, `STORY-0129`, `STORY-0130` | 6 | 6 |
| `FEAT-9` | Employee status & lifecycle actions | ACTIVE/INACTIVE transitions, payroll-exclusion warnings, row-level payroll actions. | `CAP-4` | Employee Lifecycle Management | `active` | `STORY-0121`, `STORY-0123` | 2 | 2 |
| `FEAT-10` | Bulk employee upload & import | Smart upload, alias header detection, upload/enroll separation. | `CAP-4` | Employee Lifecycle Management | `active` | `STORY-0109`, `STORY-0124` | 2 | 2 |
| `FEAT-11` | Employee page UX | Split row actions, contract-date display, colour-coded warnings, mid-period hire warnings, inactive styling. | `CAP-4` | Employee Lifecycle Management | `active` | `STORY-0099`, `STORY-0103`, `STORY-0106`, `STORY-0107`, `STORY-0115`, `STORY-0116` | 6 | 6 |
| `FEAT-12` | Payroll input capture & validation | Input codes, staging, negative-quantity guards, future-input blocking, multi-row entry. | `CAP-5` | Pay Events & Inputs | `active` | `STORY-0001`, `STORY-0002`, `STORY-0003`, `STORY-0016`, `STORY-0033`, `STORY-0126` | 6 | 6 |
| `FEAT-13` | Timesheet capture & derivation | Upload, parsing, employee matching, three-step cap formula, manual OT override, approval flow, audit trail. | `CAP-5` | Pay Events & Inputs | `active` | `STORY-0090`, `STORY-0091`, `STORY-0092`, `STORY-0093`, `STORY-0094`, `STORY-0095`, `STORY-0096`, `STORY-0105` | 8 | 8 |
| `FEAT-14` | Bulk input upload & reconciliation intake | Smart period-input upload, dedup and idempotency, reconciliation file upload and comparison. | `CAP-5` | Pay Events & Inputs | `active` | `STORY-0017`, `STORY-0125`, `STORY-0127`, `STORY-0128` | 4 | 4 |
| `FEAT-18` | Core calculation & component execution | Component execution order, input claiming at run time, period-context freeze, Decimal precision. | `CAP-6` | Execution Engine | `active` | `STORY-0004`, `STORY-0006`, `STORY-0018`, `STORY-0157` | 4 | 4 |
| `FEAT-19` | Statutory deduction correctness | PAYE on taxable income and its statutory bands, NHF/health/levy, non-taxable class, PAYE-only additions, check-off dues, NSITF/ITF, life insurance. | `CAP-6` | Execution Engine | `active` | `STORY-0007`, `STORY-0023`, `STORY-0078`, `STORY-0079`, `STORY-0080`, `STORY-0081`, `STORY-0082`, `STORY-0131`, `STORY-0156` | 9 | 9 |
| `FEAT-20` | Proration & period handling | Partial-period proration; workspace-configurable hire and termination strategy. | `CAP-6` | Execution Engine | `active` | `STORY-0005`, `STORY-0086` | 2 | 2 |
| `FEAT-21` | Overtime, shift & public-holiday pay | PH-aware expected hours and days, OT3, manual OT adjustment, shift-gated OT, PH warnings. | `CAP-6` | Execution Engine | `active` | `STORY-0037`, `STORY-0038`, `STORY-0039`, `STORY-0040`, `STORY-0073` | 5 | 5 |
| `FEAT-22` | Rule resolution & versioning behaviour | Historical rate resolution, date-aware rule lookup, legacy-workspace fallback, date cap on the legacy loader. | `CAP-6` | Execution Engine | `active` | `STORY-0019`, `STORY-0133`, `STORY-0134`, `STORY-0135` | 4 | 4 |
| `FEAT-23` | Run retry & recovery | Per-employee retry, total recalculation, retry audit writes, retry-path rate correctness. | `CAP-6` | Execution Engine | `active` | `STORY-0020`, `STORY-0021`, `STORY-0074`, `STORY-0151` | 4 | 4 |
| `FEAT-24` | Engine defect remediation | Track A mandatory fixes; GAP-2, GAP-5, `fixed_amount` fallback. | `CAP-6` | Execution Engine | `active` | `STORY-0034`, `STORY-0065`, `STORY-0066`, `STORY-0067` | 4 | 4 |
| `FEAT-25` | Execution observability | Execution trace and timeline view. | `CAP-6` | Execution Engine | `active` | `STORY-0022` | 1 | 1 |
| `FEAT-29` | Run state machine & approval | Forward-only progression, DB trigger enforcement, dedup, Approve/Lock/Mark-paid. | `CAP-7` | Governance & Run State Machine | `active` | `STORY-0008`, `STORY-0009`, `STORY-0024` | 3 | 3 |
| `FEAT-30` | Audit trail & actor attribution | Audit log and event store reads, `X-Performed-By`, approver identity. | `CAP-7` | Governance & Run State Machine | `active` | `STORY-0025`, `STORY-0041`, `STORY-0153` | 3 | 3 |
| `FEAT-31` | Statutory & payroll rule versioning | Statutory `effective_from` UNIQUE, payroll rule versioning and auto-publish, WITHDRAWN status. | `CAP-7` | Governance & Run State Machine | `active` | `STORY-0026`, `STORY-0132`, `STORY-0136` | 3 | 3 |
| `FEAT-32` | Payroll reconciliation | Status view, LOCKED/PAID gating, duplicate handling, MISMATCH correction. | `CAP-8` | Disbursement & Exports | `active` | `STORY-0010`, `STORY-0027`, `STORY-0028` | 3 | 3 |
| `FEAT-33` | Payment & statutory exports | Bank upload, PAYE remittance, pension schedule, full payroll detail. | `CAP-8` | Disbursement & Exports | `active` | `STORY-0058`, `STORY-0068`, `STORY-0069`, `STORY-0070` | 4 | 4 |
| `FEAT-15` | Design system foundations | Design brief, tokens, 45-component library. | `CAP-9` | Design System & Navigation | `active` | `STORY-0044`, `STORY-0045` | 2 | 2 |
| `FEAT-16` | Operator & bureau journeys | Gate 3 operator journey, Gate 4 bureau setup, Gate 6 configuration overhaul. | `CAP-9` | Design System & Navigation | `active` | `STORY-0055`, `STORY-0056`, `STORY-0057` | 3 | 3 |
| `FEAT-17` | Navigation & information architecture | Navigation modernisation, Rate Codes page, sidebar badges and their live-update behaviour, stale-copy cleanup. | `CAP-9` | Design System & Navigation | `active` | `STORY-0098`, `STORY-0100`, `STORY-0108`, `STORY-0113`, `STORY-0114`, `STORY-0137` | 6 | 6 |
| `FEAT-37` | Test harness & regression coverage | Fixture scaffold, financial-engine tests, API/migration tests, async-contract rewrites. | `CAP-10` | Delivery Infrastructure | `active` | `STORY-0139`, `STORY-0140`, `STORY-0141`, `STORY-0142`, `STORY-0144` | 5 | 5 |
| `FEAT-38` | CI/CD pipeline & branch protection | Branch cleanup, CI gate, pre-push hook, fresh-migrated Postgres. | `CAP-10` | Delivery Infrastructure | `active` | `STORY-0138`, `STORY-0143` | 2 | 2 |
| `FEAT-39` | Code simplification & technical debt | Deferred `/simplify` items, script hygiene. | `CAP-10` | Delivery Infrastructure | `active` | `STORY-0152`, `STORY-0155` | 2 | 2 |
| `FEAT-40` | Independent review programmes | `audit-program`, `agentic-architecture-review`. | `CAP-11` | Programme Governance & Assurance | `active` | `STORY-0147`, `STORY-0148` | 2 | 2 |
| `FEAT-41` | Sprint workflow model | ICM `STAGE-REGISTRY.md` / `WORKFLOW.md`. | `CAP-11` | Programme Governance & Assurance | `active` | `STORY-0149` | 1 | 1 |

**Totals:** 41 features · **157 migrated · 157 allocated — no backlog remaining** (D-027, 2026-07-29).

## Amendment history

- **2026-07-28 (D-023):** `FEAT-4` moved from `CAP-3` to `CAP-4` and re-scoped to employee records/CRUD; `FEAT-6`–`FEAT-41` added; `stories`, `migrated` and `allocated` columns added. Four stories reassigned: `PT-A1-25` and `PT-A1-28` from `FEAT-4` to `FEAT-11`; `PT-A1-38` and `PT-A1-39` from `FEAT-4` to `FEAT-8`.
- **2026-07-28 (D-024):** `FEAT-17` took the sidebar-badge items (`PT-A1-27`, `PT-A1-29`, `BADGE-RT-1`, `BADGE-RT-2`) so navigation badges sit together rather than splitting across `FEAT-11`; `FEAT-19` took the newly-captured `PAY-TAX-1`.
- **2026-07-29 (D-027):** `stories` and `migrated` updated on every feature by the Phase 4D remainder batch. Every feature now lists its full story set and `migrated` equals `allocated` throughout.
