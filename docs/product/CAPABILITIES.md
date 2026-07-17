# Capabilities Registry

A capability sits between an outcome and a feature. Per the hybrid framing adopted in D-008/D-009 (Section 6 of the discovery document), this registry holds two kinds of entries, distinguished by the `type` column:

- **`durable`** — a lasting product area that persists across many sprints (e.g. "Employee Lifecycle Management," "Execution Engine"). Roughly corresponds to `docs/ROADMAP.md`'s A1–A10 capability-area columns.
- **`delivery`** — a bounded delivery effort (a sprint or track) that fed one or more durable capabilities (e.g. "Sprint 16 — Timesheet Layer," "Track J — Post-Onboarding Config Management"). Roughly corresponds to `docs/ROADMAP.md`'s Sprint/Track sections.

This distinction lets the registry express both "what lasting product area does this belong to" and "which bounded effort delivered it" without inventing a fifth hierarchy level.

**Phase 4A pilot (D-015):** rows `CAP-1`/`CAP-2` were added under the bounded two-story pilot migration authorised 2026-07-15. **Phase 4B confirmed-batch (D-016):** row `CAP-3` was added under the bounded confirmed-story batch migration (capability area A1+A2) authorised 2026-07-15 — see `docs/programmes/product-traceability/decisions.md` D-015/D-016 and the corresponding run records under `docs/programmes/product-traceability/runs/`. Full Phase 4 (historical migration) remains unauthorised; only these three rows exist — no other row from the 148-item discovery inventory has been migrated.

**Human-readable names (D-016):** the `outcome_name` column is a display-only convenience — `outcome_id` remains the authoritative reference for identity and relationships. A displayed name must exactly match the current `name` held in `OUTCOMES.md`; a rename there must update every duplicated `outcome_name` here in the same controlled change. `validate_registry.py` enforces this. Never resolve a capability's outcome by name — always by `outcome_id`.

## Schema

| Column | Meaning |
|---|---|
| `capability_id` | Stable identifier, format `CAP-<n>` (durable) or `EPIC-<n>` (delivery). Never reused, never renumbered. |
| `name` | Short name. |
| `type` | `durable` \| `delivery`. |
| `description` | One or two sentences. |
| `outcome_id` | The `outcome_id` (from `OUTCOMES.md`) this capability serves. A capability serves exactly one outcome; if it genuinely serves more than one, that is itself a decision for a human to make, not an inference for a future migration pass to guess at. Authoritative for identity — resolve relationships by this column, never by `outcome_name`. |
| `outcome_name` | Display-only copy of the referenced outcome's current `name` (from `OUTCOMES.md`). Must be updated in the same change as any rename of that outcome. Not authoritative — `validate_registry.py` rejects any row where this drifts from the outcome's actual name. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `sprint_or_track_refs` | For `delivery` type: the sprint/track IDs from `docs/ROADMAP.md` this epic corresponds to (e.g. `Sprint 16`, `Track J`). For `durable` type: leave blank or list the ROADMAP capability-area column it corresponds to (e.g. `A1+A2`). |

## Registry

| `capability_id` | `name` | `type` | `description` | `outcome_id` | `outcome_name` | `status` | `sprint_or_track_refs` |
|---|---|---|---|---|---|---|---|
| `CAP-1` | Governed, auditable payroll execution | `durable` | Roughly corresponds to `docs/ROADMAP.md` Track Q (Audit Observations) — the durable product area of making stored calculation results independently verifiable from persisted trace data. | `OUT-1` | Governed, auditable payroll execution | `active` | Track Q |
| `CAP-2` | Sustainable delivery process | `durable` | Roughly corresponds to `docs/ROADMAP.md` Track S (Security) — the durable product area of security/process discipline applied to every route and input handler, not a single feature. | `OUT-2` | Sustainable delivery process | `active` | Track S |
| `CAP-3` | Onboarding & Workforce Setup | `durable` | Roughly corresponds to `docs/ROADMAP.md` capability area A1+A2 — the durable product area of configuring a workspace's payroll settings (grades, designations, salary definitions, rules, statutory overrides) and managing the employee record lifecycle (CRUD, enrollment, attendance/timesheet configuration). | `OUT-3` | Operationally usable payroll administration | `active` | A1+A2 |
