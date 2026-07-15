# Outcomes Registry

Top-level product outcomes. An outcome is a durable business result the platform exists to deliver — it does not change with every sprint and is not itself a unit of delivered work.

**Phase 4A pilot (D-015):** `OUT-1`/`OUT-2` were added under the bounded two-story pilot migration authorised 2026-07-15. **Phase 4B confirmed-batch (D-016):** `OUT-3` was added under the bounded confirmed-story batch migration (capability area A1+A2) authorised 2026-07-15 — see `docs/programmes/product-traceability/decisions.md` D-015/D-016 and the corresponding run records under `docs/programmes/product-traceability/runs/`. Full Phase 4 (historical migration) remains unauthorised; only these three rows exist — no other row from the 148-item discovery inventory has been migrated. Five candidate outcomes were proposed (not adopted) in Section 5 of `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`; `OUT-1`/`OUT-2`/`OUT-3` reuse that section's OUT-3/OUT-4/OUT-2 naming respectively (renumbered as the first three rows actually populated in this registry, in the order their evidencing stories were migrated) because they are the outcomes each batch's stories evidence — not a wholesale adoption of all five.

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
| `OUT-1` | Governed, auditable payroll execution | Execution and audit-trail data must let an auditor verify how a stored value was derived, not just what the value is — without needing to re-query live DB state. | `active` | `CAP-1` | Discovery document Section 5, OUT-3. Evidenced by the Track Q rolling audit register (`docs/ROADMAP.md`) and the closed audit reports `docs/audit/2026-05-01-sprint-10-audit-review.md`, `docs/audit/2026-05-02-sprint-11-audit-review.md`, `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`. |
| `OUT-2` | Sustainable delivery process | Security, audit, and delivery-process discipline that does not itself ship a user-visible payroll feature but is the reason later features can be trusted. | `active` | `CAP-2` | Discovery document Section 5, OUT-4. Evidenced by the Track S security rolling register (`docs/ROADMAP.md`) and the ICM sprint-workflow's own security/verification gate mechanics (`docs/sprints/STAGE-REGISTRY.md`, `docs/sprints/WORKFLOW.md`). |
| `OUT-3` | Operationally usable payroll administration | Onboarding, workspace configuration, and employee-lifecycle management must be usable by a bureau operator through a UI, not just theoretically possible via raw data entry. | `active` | `CAP-3` | Discovery document Section 5, OUT-2. Evidenced by `docs/ROADMAP.md` capability area A1+A2 (Onboarding & Workforce Setup) and the 19 confirmed items migrated in the Phase 4B confirmed-story batch (`docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md`). |
