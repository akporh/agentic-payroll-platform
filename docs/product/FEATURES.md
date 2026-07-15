# Features Registry

A feature sits between a capability and a story — e.g. under the `Employee Lifecycle Management` durable capability, candidate features include *Employee CRUD*, *Enrollment*, *Bulk Upload*, *Status Management*, *Contract Management* (see Section 7 of the discovery document). Every story in `STORY-REGISTRY.md` maps to exactly one feature.

**Phase 4A pilot (D-015):** `FEAT-1`/`FEAT-2` were added under the bounded two-story pilot migration authorised 2026-07-15. **Phase 4B confirmed-batch (D-016):** `FEAT-3`/`FEAT-4`/`FEAT-5` were added under the bounded confirmed-story batch migration (capability area A1+A2) authorised 2026-07-15 — see `docs/programmes/product-traceability/decisions.md` D-015/D-016 and the corresponding run records under `docs/programmes/product-traceability/runs/`. Full Phase 4 (historical migration) remains unauthorised; the discovery document's remaining candidate items are not pre-assigned to a feature by either batch — assigning them is Phase 4 work.

**Human-readable names (D-016):** the `capability_name` column is a display-only convenience — `capability_id` remains the authoritative reference. A displayed name must exactly match the current `name` held in `CAPABILITIES.md`; a rename there must update every duplicated `capability_name` here in the same controlled change. `validate_registry.py` enforces this. Never resolve a feature's capability by name — always by `capability_id`.

## Schema

| Column | Meaning |
|---|---|
| `feature_id` | Stable identifier, format `FEAT-<n>`. Never reused, never renumbered. |
| `name` | Short name. |
| `description` | One or two sentences. |
| `capability_id` | The durable `capability_id` (from `CAPABILITIES.md`, `type: durable`) this feature belongs to. Authoritative for identity — resolve relationships by this column, never by `capability_name`. |
| `capability_name` | Display-only copy of the referenced capability's current `name` (from `CAPABILITIES.md`). Must be updated in the same change as any rename of that capability. Not authoritative — `validate_registry.py` rejects any row where this drifts from the capability's actual name. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `story_count` | Count of stories in `STORY-REGISTRY.md` mapped to this feature — kept in sync manually or via `validate_registry.py`. |

## Registry

| `feature_id` | `name` | `description` | `capability_id` | `capability_name` | `status` | `story_count` |
|---|---|---|---|---|---|---|
| `FEAT-1` | Payroll calculation trace auditability | Ensuring `component_trace_jsonb` entries name the derivation source for a value, not just the value itself, so an auditor never needs to re-query live DB state to verify a calculation. | `CAP-1` | Governed, auditable payroll execution | `active` | 1 |
| `FEAT-2` | File upload security controls | Server-side size/validity guards on file-upload endpoints (timesheet upload and any future upload surface), enforced independently of any client-side advisory check. | `CAP-2` | Sustainable delivery process | `active` | 1 |
| `FEAT-3` | Post-onboarding configuration management | Editing workspace payroll configuration (grades, designations, salary definitions, payroll rules, statutory component overrides, pay-cycle settings) through a UI after initial onboarding, without needing to re-run onboarding or hand-edit JSON. Corresponds to `docs/ROADMAP.md` Track J. | `CAP-3` | Onboarding & Workforce Setup | `active` | 9 |
| `FEAT-4` | Employee lifecycle management | Creating, editing, and managing employee HR records and their payroll-relevant attributes (schema fields, grade percentage structure, CRUD API, enrollment pre-population) across their lifecycle. | `CAP-3` | Onboarding & Workforce Setup | `active` | 8 |
| `FEAT-5` | Attendance & timesheet configuration | Workspace-level setup of attendance codes, policies, and timesheet configuration that must exist before timesheet processing (a separate feature from timesheet processing itself, which belongs to Pay Events). | `CAP-3` | Onboarding & Workforce Setup | `active` | 2 |
