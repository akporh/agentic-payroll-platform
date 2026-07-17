# Run Record — `historical-migration-pilot-run-001`

**Phase:** 4A — bounded two-story pilot migration (Phase 4 `historical migration`, pilot scope only)
**Date:** 2026-07-15
**Authorising prompt:** `docs/diagnostics/2026-07-15-prompt-authorise-phase-4a-two-story-pilot-migration.md`
**Authorising decision:** D-015 (`docs/programmes/product-traceability/decisions.md`)

---

## Start state

- Phase 3 (`structure implementation`) complete: `docs/product/` scaffold existed with empty registries (schema only, zero content rows), `stories/TEMPLATE.md`, and `docs/product/validate_registry.py`.
- Phase 4 (`historical migration`) as a whole: not authorised.
- `docs/programmes/product-traceability/decisions.md` already contained D-001–D-014.
- Pre-existing, unrelated uncommitted working-tree state at run start (left untouched by this run): `docs/ROADMAP.md` (modified), `docs/test-harness-checklist.md` (deleted), `docs/test-reports/test-harness/` (untracked), `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md` (untracked). None of these paths were read from or written to by this run.

## Authorisation decision

D-015 was recorded in `decisions.md` (see that file) authorising a bounded Phase 4A pilot: exactly two named ICM sprint-workflow stories (`aud-q1-trace-source`, `sec-s7-timesheet-upload-guard`) may be migrated into `docs/product/`. Phase 4 as a whole remains unauthorised; the decision explicitly states pilot completion does not auto-authorise a broader batch.

## Source files inspected

Governing inputs (read only): `PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `docs/product/README.md`, `OUTCOMES.md`, `CAPABILITIES.md`, `FEATURES.md`, `STORY-REGISTRY.md`, `stories/TEMPLATE.md`, `validate_registry.py`, `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md`.

Sprint evidence (read only):
- `docs/sprints/aud-q1-trace-source/`: `state.md`, `CONTEXT.md`, `decisions.md`, `plan.md`, `audit.md`, `retrospective.md`, `evidence/implementation/component_source_trace_fix.md`, `evidence/test/component_source_verification.md`.
- `docs/sprints/sec-s7-timesheet-upload-guard/`: `state.md`, `CONTEXT.md`, `decisions.md`, `retrospective.md`, `evidence/implementation/size_guard.md`, `evidence/security/review.md`, `evidence/test/verification.md`, `evidence/verification/live_run.md`.
- Cross-referenced existing convention outputs: `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`, `docs/test-reports/2026-07-12-aud-q1-trace-source.md`, `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md`, `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md` (referenced by path in story records; not modified).
- Git history: `git log --oneline -- backend/domain/payroll/rule_evaluator.py` and `--grep` searches resolved commit SHAs `a8ffc76` (AUD-1/Q1) and `be337aa`/`58ec4f8` (SEC-S7).

## Hierarchy choices and rationale

- **Outcomes:** Reused the discovery document's Section 5 `OUT-3`/`OUT-4` naming intent, renumbered `OUT-1`/`OUT-2` as the first rows actually populated in `OUTCOMES.md` (not a wholesale adoption of all five proposed outcomes — only the two the pilot's stories evidence).
  - `OUT-1` "Governed, auditable payroll execution" — the durable business result the AUD-1/Q1 fix serves (an auditor can verify a derivation from stored trace data alone).
  - `OUT-2` "Sustainable delivery process" — the durable business result the SEC-S7 fix serves (security/process discipline that doesn't itself ship a payroll feature but is why later features can be trusted).
- **Capabilities:** One durable capability per outcome, corresponding to the ROADMAP track each story's source item comes from — `CAP-1` (Track Q, audit observations) and `CAP-2` (Track S, security). No `delivery`-type (`EPIC-`) row was created because the pilot's two ICM sprints are already fully represented via `sprint_refs` in `STORY-REGISTRY.md`; adding a bounded-delivery capability row for a two-item pilot would be over-fragmentation for no traceability gain.
- **Features:** One feature per story (`FEAT-1` under `CAP-1`; `FEAT-2` under `CAP-2`) — each names a genuinely distinct product-intent area (trace auditability vs. upload-endpoint security controls), not a delivery-order artefact of two different sprints. They are not the same feature because a future story about, say, employee-CRUD trace auditability would belong under `FEAT-1` while a future story about a different upload endpoint's security guard would belong under `FEAT-2` — the boundary reflects what each feature is about, not which sprint delivered it.
- No speculative hierarchy entries were created for any of the other 146 discovery items.

## Files created/modified

Created:
- `docs/product/stories/PT-A4-31-component-source-trace-fix.md`
- `docs/product/stories/PT-A4-32-timesheet-upload-size-guard.md`
- `docs/programmes/product-traceability/runs/historical-migration-pilot-run-001.md` (this file)
- `docs/programmes/product-traceability/critic-review-phase-4a-pilot.md` (written after critic review — see below)

Modified:
- `docs/product/OUTCOMES.md` — added `OUT-1`, `OUT-2` rows.
- `docs/product/CAPABILITIES.md` — added `CAP-1`, `CAP-2` rows.
- `docs/product/FEATURES.md` — added `FEAT-1`, `FEAT-2` rows.
- `docs/product/STORY-REGISTRY.md` — added `PT-A4-31`, `PT-A4-32` rows; updated `story_file` schema note for the descriptive-slug filename convention.
- `docs/product/stories/TEMPLATE.md` — amended (see "Template amendment" below); naming instruction updated for the descriptive-slug convention.
- `docs/product/README.md` — status section updated to reflect Phase 4A pilot completion and continued non-authorisation of the broader batch.
- `docs/product/validate_registry.py` — two fixes (see "Amendments made after criticism" — recorded here as pre-critic self-corrections, not critic-driven amendments; both discovered while running validation during this same pass):
  1. Table-cell parsing now strips Markdown backticks, so a populated ID cell (`` `PT-A4-31` ``) matches a bare filename stem — this was a latent parser defect invisible on the empty Phase 3 scaffold (zero rows meant the comparison was never exercised).
  2. Story-file matching changed from exact-stem equality to story-ID-prefix matching, to support the descriptive-slug filename convention adopted at the human's request mid-run (see below).
- `docs/programmes/product-traceability/decisions.md` — D-015 appended (recorded at the start of this run, per the prompt's instruction).
- `docs/programmes/product-traceability/PHASES.md` — Phase 4 section rewritten to distinguish pilot (authorised/complete-for-scope) from the remainder (not authorised).
- `docs/programmes/product-traceability/state.md` — current phase, executor/critic status, human-gate status, completed outputs, and next permitted action all updated for the pilot.
- `docs/programmes/product-traceability/phase-inputs.yaml` — pilot run ID, current phase, migrated story IDs, and pilot outputs recorded; `recommended_next_phase_authorised` remains `false`.
- `docs/programmes/product-traceability/exceptions.md` — Phase 4A section appended (see below).

## Template amendment (recorded per the prompt's requirement)

`stories/TEMPLATE.md` was amended, not left as-is, because the pilot's two stories could not be recorded to the letter of the migration rules (which require outcome ID, capability ID, decision references, dependencies "or an explicit empty value," and append-only delivery history) without four fields the original template lacked: **Outcome**, **Capability**, **Decision references**, **Dependencies**, and **Delivery history** (distinct from the pre-existing single "Delivery sprint(s)" line, which cannot function as an append-only log). This is recorded as a genuine schema defect discovered by the pilot, not scope creep — the template's own amendment note states the same reasoning in place. Separately, the template's file-naming instruction was updated for the descriptive-slug convention (see below) — a naming-convenience change, not a field-schema change.

## Filename descriptiveness — mid-run human request

Mid-run, the human noted the story files (originally created as bare `PT-A4-31.md` / `PT-A4-32.md`) did not let the story be identified from the filename alone. Both files were renamed to `PT-A4-31-component-source-trace-fix.md` and `PT-A4-32-timesheet-upload-size-guard.md`. This required extending `validate_registry.py`'s story/file matching from exact-stem equality to story-ID-prefix matching (a file matches a registry `story_id` if its stem equals the ID exactly, or starts with `"<story_id>-"`), and updating `STORY-REGISTRY.md`'s `story_file` column, `TEMPLATE.md`'s naming instruction, and this run record accordingly. This is a naming/tooling convenience within the authorised `docs/product/` scope — it does not change any story's `story_id`, content, classification, evidence, or hierarchy placement.

## Validator output

```
$ python3 docs/product/validate_registry.py
PASS — docs/product/ registries are internally consistent (8 total content row(s) checked).
```

(8 rows = 2 outcomes + 2 capabilities + 2 features + 2 stories.)

## Executor findings

- Exactly two non-template story files exist under `stories/`.
- `STORY-REGISTRY.md` has exactly two content rows.
- Every `feature_id`/`capability_id`/`outcome_id` referenced by a lower-level row exists in the row above it (confirmed by the validator and by direct inspection).
- Every story file has one matching registry row and vice versa (confirmed by the validator's prefix-matching logic).
- All cited evidence paths (`docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`, `docs/test-reports/2026-07-12-aud-q1-trace-source.md`, `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md`, `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md`, both sprint workspace directories) exist on disk — confirmed by direct `find`/read during evidence-gathering.
- Both commit references (`a8ffc76`; `58ec4f8`, `be337aa`) exist in `git log` and match the described change in file and message.
- No forbidden path (`docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/security/`, `docs/test-reports/`, `docs/retro-reports/`, `docs/audit-program/`, `docs/agentic-architecture-review/`, `backend/`, `frontend/`, `migrations/`, `~/.claude/`) was modified by this run — confirmed by `git status --short` showing modifications confined to `docs/product/` and `docs/programmes/product-traceability/`.
- Pre-existing unrelated working-tree changes (`docs/ROADMAP.md`, `docs/test-harness-checklist.md`, `docs/test-reports/test-harness/`, `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md`) were left exactly as found — not read from, not written to, not staged, not committed by this run.
- Two discovery-document duplicate-provisional-ID mappings surfaced (`PT-A4-31`/`PT-Q-01`; `PT-A4-32`/`PT-S-07`) — recorded as unresolved questions in each story file and in `state.md`, not silently resolved.
- The pilot exercises all eight product-governance disciplines listed in the authorising prompt: stable IDs (fixed, never reused); source-of-truth ownership (story records summarise and link to sprint evidence, never duplicate acceptance criteria); explicit state (`status`/`confidence` are separate fields, both populated); evidence links (every claim resolves to a checked repository path); decision traceability (`Decision references` section cites both sprint-local `DEC-*` IDs and programme-level `D-015`); dependency visibility (`Dependencies` explicitly states "None" for both, not left blank); append-only delivery history (`Delivery history` records the original sprint contribution and this migration as separate, non-overwriting lines); human-gate discipline (`PHASES.md`/`state.md`/`phase-inputs.yaml` all state the broader batch is not authorised and pilot completion does not grant it).

## Critic verdict

See `critic-review-phase-4a-pilot.md`, produced by an independent read-only critic pass after all executor artefacts above existed.

## Amendments made after criticism

Verdict: `approve-with-amendments` (see `critic-review-phase-4a-pilot.md` for full detail). One required amendment, explicitly stated by the critic as mechanical and not requiring a full re-review:

- Corrected three stale story-file path references left over from the mid-run descriptive-slug rename — `PHASES.md` (Required outputs line), `state.md` (Completed outputs list), and `phase-inputs.yaml` (`historical_migration_pilot_outputs_delivered`) all cited the pre-rename bare filenames `PT-A4-31.md`/`PT-A4-32.md`; updated to the actual filenames `PT-A4-31-component-source-trace-fix.md`/`PT-A4-32-timesheet-upload-size-guard.md`. `STORY-REGISTRY.md` and this run record already had the correct names — only these three files needed the fix.
- Re-ran `python3 docs/product/validate_registry.py` after the fix: `PASS — docs/product/ registries are internally consistent (8 total content row(s) checked).` — unaffected, as the critic predicted (none of the three corrected files are read by the validator).

No other amendment was required. Two items were noted by the critic for future-decision visibility only (not required amendments): the `PT-A4-13`/`PT-Q-01` and `PT-S-07` duplicate-provisional-ID questions, and whether the security review's separately-flagged upload content-type Observation should become a future backlog item.

## Commit SHA(s)

`c4c8c9b` — "docs: pilot product traceability migration with two ICM stories", pushed to `origin/uat` (28b270c..c4c8c9b). Only the 16 authorised files under `docs/product/` and `docs/programmes/product-traceability/` were staged and committed; the pre-existing unrelated working-tree changes (`docs/ROADMAP.md`, `docs/test-harness-checklist.md`, `docs/test-reports/test-harness/`, `docs/ux-design-brief/gate-6/ia-timesheet-discoverability.md`) were left uncommitted, exactly as found at run start. Pre-push hook ran the full backend suite (308 passed, 1 pre-existing skip, 0 failed) and frontend typecheck (clean) before the push completed.

## Outstanding questions

- Whether `PT-A4-13`/`PT-Q-01` should be retired as duplicates of `PT-A4-31`, or kept as distinct historical markers (a future migration-pass decision, not resolved here).
- Whether `PT-S-07` should be retired as a duplicate of `PT-A4-32`, or kept as distinct (same note).
- The security review's separately-flagged Observation (no content-type/malformed-file validation on the timesheet-upload endpoint) is not yet represented anywhere in `docs/product/` — it was explicitly out of scope for SEC-S7 and is not itself a delivered story.
- The two pre-existing open follow-up investigations (PH_OT `is_pensionable`, D-010/DP-04; Gate 4 status contradiction, D-012/DP-06) remain open and are unaffected by this pilot.

## Next permitted action

Human review of the pilot's quality (registry rows, story files, critic verdict), and explicit authorisation of any broader Phase 4 migration batch scope only, if and when desired. No further story may be migrated, and full Phase 4 must not begin, without a further explicit human decision.
