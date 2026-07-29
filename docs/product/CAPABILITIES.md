# Capabilities Registry

A capability sits between an outcome and a feature: a lasting product area that persists across many sprints. Roughly corresponds to `../ROADMAP.md`'s A1–A10 capability-area columns and its cross-cutting Tracks.

**Approved as a complete set 2026-07-28 (D-023).** Previously this registry held three rows, each created to hold a migration batch's stories.

## On `type`, and why no `EPIC-*` rows exist

D-008 fixed a hybrid model with two entry types — `durable` (a lasting product area) and `delivery` (a bounded sprint or track). The `type` column is retained, but **no `delivery` row is proposed or created** (D-023, OQ-7). A capability already functions as an epic in this model, and sprint/track membership is carried per story in `STORY-REGISTRY.md`'s `sprint_refs` column — a parallel `EPIC-*` layer would duplicate it without answering any question the registry cannot already answer. This is a recorded non-adoption, not an oversight.

## Human-readable names (D-016)

`outcome_name` is display-only — `outcome_id` remains the authoritative reference. A displayed name must exactly match the current `name` in `OUTCOMES.md`; a rename there must update every duplicated `outcome_name` here in the same controlled change. `validate_registry.py` enforces this. Never resolve a capability's outcome by name.

## Schema

| Column | Meaning |
|---|---|
| `capability_id` | Stable identifier, format `CAP-<n>` (durable) or `EPIC-<n>` (delivery — unused, see above). Never reused, never renumbered. |
| `name` | Short name. |
| `type` | `durable` \| `delivery`. |
| `description` | One or two sentences. |
| `outcome_id` | The `outcome_id` this capability serves. Authoritative — resolve relationships by this column, never by `outcome_name`. |
| `outcome_name` | Display-only copy of the referenced outcome's current `name`. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `roadmap_area` | The `../ROADMAP.md` capability-area column or Track this corresponds to. |

## Registry

| `capability_id` | `name` | `type` | `description` | `outcome_id` | `outcome_name` | `status` | `roadmap_area` |
|---|---|---|---|---|---|---|---|
| `CAP-1` | Correctness, Audit & Snapshot | `durable` | Making stored calculation results independently verifiable from persisted trace and snapshot data, and closing audit observations raised against them. | `OUT-1` | Governed, auditable payroll execution | `active` | A7–A10, Track Q |
| `CAP-2` | Security & Compliance Hardening | `durable` | Security and input-validation discipline applied to every route and input handler — not a single feature but a standing posture. | `OUT-2` | Sustainable delivery process | `active` | Track S |
| `CAP-3` | Onboarding & Workspace Setup | `durable` | Configuring a workspace's payroll settings — grades, designations, salary definitions, rules, statutory overrides, pay cycles, public holidays, rate codes, attendance policy. | `OUT-3` | Operationally usable payroll administration | `active` | A1 |
| `CAP-4` | Employee Lifecycle Management | `durable` | Creating, editing, enrolling and managing employee records and their payroll-relevant attributes across their lifecycle. | `OUT-3` | Operationally usable payroll administration | `active` | A2 |
| `CAP-5` | Pay Events & Inputs | `durable` | Capturing what varies per period — payroll inputs, timesheets, overtime — and turning it into pay instructions. | `OUT-3` | Operationally usable payroll administration | `active` | A3 |
| `CAP-6` | Execution Engine | `durable` | Gross-to-net calculation: component execution, statutory deductions, proration, overtime and public-holiday pay, rule resolution, retry. | `OUT-4` | Accurate, compliant statutory payroll calculation | `active` | A4 |
| `CAP-7` | Governance & Run State Machine | `durable` | Run lifecycle, approval, immutability, audit trail and actor attribution, and the versioning of the rules a run was calculated against. | `OUT-1` | Governed, auditable payroll execution | `active` | A5 |
| `CAP-8` | Disbursement & Exports | `durable` | Reconciliation of actual against expected, and the export formats that carry payroll out to banks and statutory bodies. | `OUT-1` | Governed, auditable payroll execution | `active` | A6 |
| `CAP-9` | Design System & Navigation | `durable` | The design system, component library, operator journeys and information architecture the platform is presented through. | `OUT-3` | Operationally usable payroll administration | `active` | Track UI |
| `CAP-10` | Delivery Infrastructure | `durable` | Test harness, regression coverage, CI/CD and the technical-debt discipline that makes delivery repeatable. | `OUT-2` | Sustainable delivery process | `active` | Sprints 29–32, test-harness workstream |
| `CAP-11` | Programme Governance & Assurance | `durable` | Independent review programmes and the sprint-workflow model itself — process capability, not product features. | `OUT-2` | Sustainable delivery process | `active` | `audit-program`, `agentic-architecture-review`, ICM |
| `CAP-12` | Agent Layer | `durable` | Agentic assistance over payroll operations. **Zero stories** — retained so the unbuilt Phase 2 work is a visible gap (D-023, OQ-6). | `OUT-5` | AI-assisted payroll operations | `planned` | Tracks P/V/W/X/Y |

## Amendment history

- **2026-07-28 (D-023):** `CAP-1` renamed from "Governed, auditable payroll execution" and `CAP-2` from "Sustainable delivery process" — both had been named identically to their parent outcome, which told a reader nothing, because each was created to hold a single Phase 4A pilot story. `CAP-3` narrowed from "Onboarding & Workforce Setup" (A1+A2) to Onboarding only (A1), with employee-lifecycle work moving to the new `CAP-4`. Identifiers unchanged throughout — only display names and scope. `CAP-4`–`CAP-12` added.
