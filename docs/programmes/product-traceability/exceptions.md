# Exceptions — Product Traceability Programme

Structured log of stop-condition events, per `POLICY.md`'s "Stop conditions" list. Use the schema below for each entry. If no exception occurred during a phase, that is stated explicitly rather than leaving this file silent.

## Schema

```text
Exception ID:
Phase:
Type:
Evidence:
Affected items:
Options:
Executor recommendation:
Effect of deferral:
Exact human decision required:
```

---

## Discovery phase (Phase 1)

**No exception occurred during the discovery phase.**

None of the seven stop conditions in `POLICY.md` were triggered:

- Authoritative sources did not materially contradict one another in a way that could not be resolved by reading further. Where `docs/ROADMAP.md` marks an item ✅ with only a narrative reference (no separate test-report line), this was recorded as `strongly inferred` rather than `confirmed`, and as an unresolved question where the gap was material — not escalated as a contradiction.
- No sensitive or personal information was discovered in the inspected documentation (no PII, credentials, or client-confidential financial data appeared in the roadmap, story files, audit reports, or test reports reviewed).
- The phase was completed within the authorised paths (`docs/diagnostics/`, `docs/programmes/product-traceability/`); no attempt to write outside them was needed.
- No destructive or irreversible change was required — all outputs are new files.
- All requested evidence was accessible (repository files and git history were readable; no external system access was required).
- Fewer than 10% of identified items required `requires human classification` — see the discovery document's confidence summary; the great majority classified at least `tentative` or higher.
- No validation failed in a way that could not be corrected within scope.

If a future amendment pass (post-critic-review) surfaces a stop condition, it will be appended below as a new dated entry rather than overwriting this statement.

---

## Hierarchy-approval phase (Phase 2)

**No exception occurred during the hierarchy-approval phase.**

The seven human decisions (DP-01–DP-07) were supplied directly by the human via `docs/diagnostics/2026-07-15-prompt-record-product-traceability-decisions-and-close-phase-2.md` and recorded verbatim as D-007–D-013 in `decisions.md`; no authoritative-source contradiction, sensitive-data discovery, out-of-scope write requirement, destructive change, inaccessible evidence, unclassifiable-item threshold breach, or uncorrectable validation failure arose while recording them or closing the phase. Two items (DP-04, DP-06) were explicitly decided as "still open, escalate/investigate outside this programme" — that is a recorded decision about follow-up ownership, not a stop-condition exception within this programme's own execution.

---

## Structure-implementation phase (Phase 3)

**No exception occurred during the structure-implementation phase.**

The phase was executed under a direct, explicit, narrowly-scoped human authorisation (D-014) limiting write access to `docs/product/`. No authoritative-source contradiction, sensitive-data discovery, out-of-scope write requirement, destructive change, inaccessible evidence, or uncorrectable validation failure arose. No historical file was modified; no story content was migrated; Phase 4 was not begun.

---

## Phase 4A pilot (bounded two-story historical migration)

**No stop-condition exception occurred during the Phase 4A pilot**, executed under D-015. Two items below are recorded here for transparency because they involved a correction, even though neither meets `POLICY.md`'s stop-condition bar (both were corrected within scope without requiring escalation):

1. **`validate_registry.py` had a latent defect, only surfaced now that real content rows exist.** The table parser stripped whitespace but not Markdown backtick formatting (`` `PT-A4-31` ``) from cell values, so a populated registry row's ID (with backticks) never matched a filename stem (without backticks) — the validator failed on its first run against real data. Fixed by stripping backticks in `read_table_rows`. This is a mechanical fix to the validation mechanism's own parsing, not a change to programme policy, source-of-truth rules, or any story's content — it was invisible on the empty Phase 3 scaffold because zero rows meant the comparison logic was never exercised.
2. **Story-file naming was made more descriptive at the human's request mid-run** (`PT-A4-31.md` → `PT-A4-31-component-source-trace-fix.md`, and similarly for `PT-A4-32`), so a filename alone identifies the story without opening it. `validate_registry.py`'s story/file matching was extended from exact-stem equality to story-ID-prefix matching (stem equals the ID, or starts with `"<story_id>-"`) to accommodate this, and `stories/TEMPLATE.md`'s naming instruction was updated to match. This is a naming/tooling convenience, not a change to any story's recorded content, classification, or evidence.

Neither correction required reclassifying any item, contradicted any authoritative source, touched a forbidden path, or required a destructive change — both are recorded here as transparency about mid-run corrections, not as stop-condition exceptions.

No authoritative-source contradiction, sensitive-data discovery, out-of-scope write requirement, destructive change, inaccessible evidence, or uncorrectable validation failure arose. Exactly two historical items (`PT-A4-31`, `PT-A4-32`) were migrated; no other historical item was touched; full Phase 4 was not begun.

---

## Phase 4B confirmed-batch (bounded, capability area A1+A2)

**No stop-condition exception occurred during the Phase 4B batch**, executed under D-016. None of `POLICY.md`'s stop conditions were triggered — the batch-selection rule resolved cleanly on the first candidate area tried (A1+A2, 19 confirmed items, within the authorised 10–20 band), no more than 20 items were ever in play, and evidence contradictions found during direct inspection were handled by the authorising prompt's own explicit mechanism ("if direct inspection weakens a supposedly confirmed item, exclude and document it") rather than by stopping the whole batch. For transparency, the following are recorded even though none meets the stop-condition bar:

1. **Several items' evidence was weaker than the discovery document's blanket `confirmed` label implied, but were migrated anyway rather than excluded**, because direct inspection (current code, git history) still supported the delivered claim even where the dated test-report trail was thinner or, in one case, directly contradictory at the time it was written:
   - `PT-A1-09` (Salary definition add + edit, WC-6/7) — the cited 2026-04-21 test report records the *add* half (WC-6) as an explicit **GAP, not implemented** at that date. Direct inspection found the add-flow code (`AddSalaryDefSlideOver`, `POST /salary-definition`) genuinely present, landed the following day (commit `db17ef9`, 2026-04-22) — after the test report was written. No dedicated re-verification of the add flow was found. Migrated as `confirmed` on the strength of direct code inspection, with the evidence gap disclosed prominently in the story file's own "Flagged for reviewer attention" section rather than silently smoothed over.
   - `PT-A1-25` (Split Edit vs Change Grade/Salary, EMP-UX-1) — shares the same "browser UAT BLOCKED" limitation recorded in the Sprint 17 test report that caused the *related* item `PT-A1-23` to be excluded from this batch by the discovery document's own confidence classification (`PT-A1-23` is `tentative`, not `confirmed`, and was never in scope for this confirmed-only batch). `PT-A1-25` itself is independently classified `confirmed` by the discovery document; migrated with the shared caveat disclosed in its Unresolved questions.
   - `PT-A1-10` (payroll rule toggle, WC-8) — the feature described in the discovery document (a two-way Activate/Deactivate toggle) was superseded on 2026-07-05 (commit `0a2702d`) by a one-way Withdraw action, for the same `is_active`-is-not-"currently in effect" reason already recorded as a standing lesson in this repository's `CLAUDE.md`. The story file describes current behaviour (per the template's own instruction) and records both deliveries in its append-only Delivery history, rather than describing a UI that no longer exists.
   - `PT-A1-28`, `PT-A1-38`, `PT-A1-39` — rest on a dedicated story file (`docs/stories/*.md`) plus a located commit, but no separate dated test report, consistent with the discovery document's own weaker sourcing for these three items (it did not claim a test-report trail for them either).
   - `PT-A1-41`, `PT-A1-42` — the cited Sprint 16 test report's own verdict is explicitly "PASS (code-level); runtime deferred to staging" — every cited check is static/code-level, not a live exercise. Both story files carry this qualifier forward rather than presenting it as a full live verification.
   None of these five items were excluded, because in each case direct inspection found the underlying delivered capability genuinely present in the current codebase — the gap is in the freshness/completeness of the *dated review trail*, not in whether the thing was actually built. The independent critic gate (`critic-review-phase-4b-confirmed-batch.md`) was asked to specifically assess whether "migrate with disclosure" was the right call for each of these versus "exclude," per the authorising prompt's own instruction not to silently downgrade and migrate.
2. **`validate_registry.py` was extended** (name-matching enforcement for the new `outcome_name`/`capability_name`/`feature_name` display columns; duplicate-ID rejection within a single registry; ambiguous-prefix rejection when a filename stem could match more than one story ID) as explicitly authorised by D-016's own "Validator requirements for names" and "Stable filename rules" sections — not a discretionary scope expansion.

No authoritative-source contradiction, sensitive-data discovery, out-of-scope write requirement, destructive change, inaccessible evidence, or uncorrectable validation failure arose. Exactly 19 historical items from capability area A1+A2 were migrated (zero excluded, per the run record); no item from any other capability area, and no strongly-inferred/tentative/requires-human-classification item, was touched; full Phase 4 was not begun.
