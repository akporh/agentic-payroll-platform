# Capabilities Registry

A capability sits between an outcome and a feature. Per the hybrid framing adopted in D-008/D-009 (Section 6 of the discovery document), this registry holds two kinds of entries, distinguished by the `type` column:

- **`durable`** — a lasting product area that persists across many sprints (e.g. "Employee Lifecycle Management," "Execution Engine"). Roughly corresponds to `docs/ROADMAP.md`'s A1–A10 capability-area columns.
- **`delivery`** — a bounded delivery effort (a sprint or track) that fed one or more durable capabilities (e.g. "Sprint 16 — Timesheet Layer," "Track J — Post-Onboarding Config Management"). Roughly corresponds to `docs/ROADMAP.md`'s Sprint/Track sections.

This distinction lets the registry express both "what lasting product area does this belong to" and "which bounded effort delivered it" without inventing a fifth hierarchy level.

**This registry is currently empty of content rows.** It was scaffolded in Phase 3 (`structure implementation`) and is populated only by an authorised Phase 4 (`historical migration`) run — see `docs/product/README.md`.

## Schema

| Column | Meaning |
|---|---|
| `capability_id` | Stable identifier, format `CAP-<n>` (durable) or `EPIC-<n>` (delivery). Never reused, never renumbered. |
| `name` | Short name. |
| `type` | `durable` \| `delivery`. |
| `description` | One or two sentences. |
| `outcome_id` | The `outcome_id` (from `OUTCOMES.md`) this capability serves. A capability serves exactly one outcome; if it genuinely serves more than one, that is itself a decision for a human to make, not an inference for a future migration pass to guess at. |
| `status` | `active` \| `complete` \| `deprecated` \| `planned`. |
| `sprint_or_track_refs` | For `delivery` type: the sprint/track IDs from `docs/ROADMAP.md` this epic corresponds to (e.g. `Sprint 16`, `Track J`). For `durable` type: leave blank or list the ROADMAP capability-area column it corresponds to (e.g. `A1+A2`). |

## Registry

| `capability_id` | `name` | `type` | `description` | `outcome_id` | `status` | `sprint_or_track_refs` |
|---|---|---|---|---|---|---|
| *(no rows — populated in Phase 4, not yet authorised)* | | | | | | |
