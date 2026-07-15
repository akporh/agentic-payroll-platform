# Features Registry

A feature sits between a capability and a story — e.g. under the `Employee Lifecycle Management` durable capability, candidate features include *Employee CRUD*, *Enrollment*, *Bulk Upload*, *Status Management*, *Contract Management* (see Section 7 of the discovery document). Every story in `STORY-REGISTRY.md` maps to exactly one feature.

**Phase 4A pilot (D-015):** two rows below were added under the bounded two-story pilot migration authorised 2026-07-15 — see `docs/programmes/product-traceability/decisions.md` D-015 and `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md`. Full Phase 4 (historical migration) remains unauthorised; the discovery document's remaining 146 candidate items are not pre-assigned to a feature by this pilot — assigning them is Phase 4 work.

## Schema

| Column | Meaning |
|---|---|
| `feature_id` | Stable identifier, format `FEAT-<n>`. Never reused, never renumbered. |
| `name` | Short name. |
| `description` | One or two sentences. |
| `capability_id` | The durable `capability_id` (from `CAPABILITIES.md`, `type: durable`) this feature belongs to. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `story_count` | Count of stories in `STORY-REGISTRY.md` mapped to this feature — kept in sync manually or via `validate_registry.py`. |

## Registry

| `feature_id` | `name` | `description` | `capability_id` | `status` | `story_count` |
|---|---|---|---|---|---|
| `FEAT-1` | Payroll calculation trace auditability | Ensuring `component_trace_jsonb` entries name the derivation source for a value, not just the value itself, so an auditor never needs to re-query live DB state to verify a calculation. | `CAP-1` | `active` | 1 |
| `FEAT-2` | File upload security controls | Server-side size/validity guards on file-upload endpoints (timesheet upload and any future upload surface), enforced independently of any client-side advisory check. | `CAP-2` | `active` | 1 |
