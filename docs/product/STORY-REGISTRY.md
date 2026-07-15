# Story Registry

The primary traceability table — one row per delivered (or in-flight) product story, at the granularity fixed by D-007 (the same story/feature-line granularity already used throughout `docs/ROADMAP.md`'s Story Index tables — 148 candidate items were reconstructed at this grain in the discovery phase).

**Phase 4A pilot (D-015):** two rows below were added under the bounded two-story pilot migration authorised 2026-07-15 — see `docs/programmes/product-traceability/decisions.md` D-015 and `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md`. Full Phase 4 (historical migration) remains unauthorised; no other row from the 148-item discovery inventory has been migrated.

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
| `story_file` | Relative path under `stories/` to this story's full record — filename is `<story-id>-<descriptive-slug>.md` (e.g. `stories/PT-A4-31-component-source-trace-fix.md`); `validate_registry.py` matches by story-ID prefix, not exact-stem equality. |

## Registry

| `story_id` | `title` | `feature_id` | `classification` | `status` | `confidence` | `sprint_refs` | `evidence_refs` | `story_file` |
|---|---|---|---|---|---|---|---|---|
| `PT-A4-31` | AUD-1/Q1: `component_source` field added to `fixed_amount` trace on fallback | `FEAT-1` | operational story | `delivered` | `confirmed` | ICM sprint `aud-q1-trace-source` (Sprint 10 raised, closed 2026-07-12) | `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`, `docs/test-reports/2026-07-12-aud-q1-trace-source.md`, `docs/sprints/aud-q1-trace-source/` | `stories/PT-A4-31-component-source-trace-fix.md` |
| `PT-A4-32` | SEC-S7: 10 MB server-side timesheet upload size guard | `FEAT-2` | compliance story | `delivered` | `confirmed` | ICM sprint `sec-s7-timesheet-upload-guard` (Sprint 16 raised, closed 2026-07-13) | `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md`, `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md`, `docs/sprints/sec-s7-timesheet-upload-guard/` | `stories/PT-A4-32-timesheet-upload-size-guard.md` |
