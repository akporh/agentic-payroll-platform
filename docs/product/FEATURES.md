# Features Registry

A feature sits between a capability and a story — e.g. under the `Employee Lifecycle Management` durable capability, candidate features include *Employee CRUD*, *Enrollment*, *Bulk Upload*, *Status Management*, *Contract Management* (see Section 7 of the discovery document). Every story in `STORY-REGISTRY.md` maps to exactly one feature.

**This registry is currently empty of content rows.** It was scaffolded in Phase 3 (`structure implementation`) and is populated only by an authorised Phase 4 (`historical migration`) run — see `docs/product/README.md`. The discovery document deliberately did not pre-assign all 148 candidate items to a specific feature name (its Section 7), since the "correct" feature boundary depends on the hierarchy model, which was only decided in Phase 2 (D-008) — assigning features is Phase 4 work.

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
| *(no rows — populated in Phase 4, not yet authorised)* | | | | | |
