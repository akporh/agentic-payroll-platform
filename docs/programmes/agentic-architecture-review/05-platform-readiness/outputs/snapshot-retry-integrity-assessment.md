# Stage 05 Output: Snapshot and Retry Integrity Assessment

## Real, committed progress since Stage 01: the 04-001/05-001 remediation

Commit `68e9307` ("Remediate 04-001 (S0) + 05-001: snapshot-first statutory retry, fail-visible snapshot creation") is a genuine, committed fix, verified in this stage:

- **04-001 (retry statutory-rule source)**: retry no longer re-resolves `statutory_rule`/`tax_band` from live tables keyed by a frozen date. It now reads exclusively from `payroll_run.rules_context_snapshot["statutory_rule"]` — the exact content the original run froze — and hard-fails before any calculation, deletion, or write for legacy/incomplete snapshots, never falling back to a live query. The commit message states this was verified against "the exact Stage 04 [audit-program] controlled-reproduction script: previously REPRODUCED, now REJECTED" — i.e., a specific reproducible bug was fixed and proven fixed.
- **05-001 (fail-visible snapshot creation)**: a related gap in `build_rules_context_snapshot` was found and fixed during implementation — v2 statutory-snapshot emission was incorrectly coupled to `rule_set_id` presence, which would have silently broken snapshot creation for the 47 of 70 workspaces in the dev DB with no published `rule_set`. Fixed as part of the same commit.
- A new `FAILED` status (`migrations/versions/b8c9d0e1f2a3_add_failed_payroll_run_status.py`) makes snapshot-creation failure visible as a terminal run state rather than a silent or ambiguous outcome, reachable only from `DRAFT`.
- A new test, `tests/test_payroll_retry_snapshot_first.py`, exercises this specific scenario (a second `statutory_rule` inserted with a later `effective_from` than the original run) and asserts retry snapshot behavior — this is a genuine regression test for exactly the class of bug fixed.

**This is confirmed, real progress — not aspirational.** It directly closes a specific retry-time statutory-rule-divergence risk that this review's Stage 01 evidence (and the separate `docs/audit-program` workstream's own 04-001/05-001 findings) had both independently flagged.

## What this fix does NOT close

- It does not touch `salary_definition` edit-locking (F-01-27) — a different snapshot source entirely (`employee_contract_snapshot`/`component_metadata_snapshot`, not `rules_context_snapshot`).
- It does not touch the `component_trace_jsonb` fallback ambiguity (F-01-29).
- It does not touch the D-ARCH-1 lock check's dead branches (F-01-38).
- It does not touch reconciliation workspace scoping (F-01-33).

## Retry vs. original-run consistency, reassessed

- **Original runs and retries now use the correct authoritative snapshot source for statutory rules** (per the fix above) — this specific consistency gap is closed.
- **Retry strategy cannot silently change the source of truth**: confirmed — `retry_strategy` is DB-constrained to `'PER_EMPLOYEE'` only (Stage 01 F-01-30/31, unchanged), and the new fix adds a hard-fail rather than a silent fallback for the statutory-rule case specifically.
- **Retry does not delete/overwrite successful historical evidence incorrectly**: unchanged from Stage 01 — retry only re-processes `payroll_result` rows with `status='FAILED'`, using delete-then-insert only for those rows (F-01-32), which remains correct and was not altered by this remediation.
- **Legacy vs. sequential execution path guarantee compatibility**: unchanged from Stage 01 (F-01-24/28) — the legacy executor remains reachable code that skips rule evaluation entirely if invoked; not addressed by this remediation, not in scope for it.
- **Trace and totals consistency between original-run and retry paths**: the statutory-rule-source fix directly improves this for the specific case it addresses (statutory rate consistency across retry); the broader `component_trace_jsonb` fallback ambiguity (F-01-29) is unrelated and unaddressed.

## Conclusion

Snapshot and retry integrity has **measurably improved** since Stage 01 in one specific, well-scoped, tested dimension (statutory-rule-source consistency at retry time). The remaining Stage 01 findings in this area (F-01-27, F-01-29, F-01-38) are unaffected by this fix and remain open, per `historical-reproducibility-assessment.md`. This is a genuine partial-closure result, not a full closure — do not conflate the two.
