# Story Registry

The primary traceability table — one row per delivered (or in-flight) product story, at the granularity fixed by D-007 (the same story/feature-line granularity already used throughout `docs/ROADMAP.md`'s Story Index tables — 148 candidate items were reconstructed at this grain in the discovery phase).

**This registry is currently empty of content rows.** It was scaffolded in Phase 3 (`structure implementation`) and is populated only by an authorised Phase 4 (`historical migration`) run — see `docs/product/README.md`. No story file exists yet under `stories/` except the template.

## Schema

| Column | Meaning |
|---|---|
| `story_id` | Stable identifier. During Phase 4, the discovery document's provisional IDs (e.g. `PT-A1-01`) are the expected source, re-keyed to a permanent scheme if the human decides one is needed — that re-keying is itself a Phase 4 decision, not assumed here. |
| `title` | Short title. |
| `feature_id` | The `feature_id` (from `FEATURES.md`) this story belongs to. |
| `classification` | One of: `user-facing story` \| `operational story` \| `compliance story` \| `platform capability` \| `technical enabler` \| `defect/remediation` \| `discovery or architecture item` — per the discovery document's classification scheme (do not force fictional user-story wording onto technical work). |
| `status` | `delivered` \| `in-flight` \| `backlog`. Only `delivered` stories should carry a `confidence` value below other than `not-applicable`. |
| `confidence` | `confirmed` \| `strongly inferred` \| `tentative` \| `requires human classification` — per the discovery document's confidence scheme. Migrated verbatim from the discovery document; a migration must not silently upgrade a confidence level. |
| `sprint_refs` | Sprint(s)/track(s) that delivered this story (e.g. `Sprint 16`, `Sprint 15 (design) / Sprint 16 (delivery)`). |
| `evidence_refs` | Path(s) to the evidence that supports this story's delivery (test report, audit report, security review, story file). |
| `story_file` | Relative path under `stories/` to this story's full record (e.g. `stories/PT-A1-01.md`). |

## Registry

| `story_id` | `title` | `feature_id` | `classification` | `status` | `confidence` | `sprint_refs` | `evidence_refs` | `story_file` |
|---|---|---|---|---|---|---|---|---|
| *(no rows — populated in Phase 4, not yet authorised)* | | | | | | | | |
