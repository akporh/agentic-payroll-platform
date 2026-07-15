# Outcomes Registry

Top-level product outcomes. An outcome is a durable business result the platform exists to deliver — it does not change with every sprint and is not itself a unit of delivered work.

**This registry is currently empty of content rows.** It was scaffolded in Phase 3 (`structure implementation`) and is populated only by an authorised Phase 4 (`historical migration`) run — see `docs/product/README.md`. Five candidate outcomes were proposed (not adopted) in Section 5 of `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`; they are not reproduced here as rows because doing so before Phase 4 is authorised would be migrating content under a different name.

## Schema

| Column | Meaning |
|---|---|
| `outcome_id` | Stable identifier, format `OUT-<n>` (e.g. `OUT-1`). Never reused, never renumbered. |
| `name` | Short name of the outcome. |
| `description` | One or two sentences describing the durable business result. |
| `status` | `active` \| `achieved` \| `deprecated`. |
| `capabilities` | Comma-separated list of `capability_id`s that serve this outcome (see `CAPABILITIES.md`). |
| `evidence_notes` | Free text — where the case for this outcome's existence is documented (e.g. a link to `docs/ROADMAP.md`'s Summary Matrix column, or a client conversation record). |

## Registry

| `outcome_id` | `name` | `description` | `status` | `capabilities` | `evidence_notes` |
|---|---|---|---|---|---|
| *(no rows — populated in Phase 4, not yet authorised)* | | | | | |
