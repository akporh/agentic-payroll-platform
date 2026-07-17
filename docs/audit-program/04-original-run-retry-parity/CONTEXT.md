# Stage 04 — Original-Run and Retry Parity

**Status:** in-progress (see [`../audit-state.md`](../audit-state.md))

## Purpose

Determine whether an original payroll run and every supported retry path use
equivalent inputs, configuration, snapshots, rules, calculations, totals,
persistence, trace behaviour, and state transitions. Distinguish intentional
divergence, legacy compatibility behaviour, confirmed parity, plausible
divergence mechanisms, reproduced divergences, and observability gaps that
prevent parity verification.

## Primary input: Stage 03 finding 03-002

Retry re-resolves the statutory rule/tax bands **live**, keyed only on the
frozen `statutory_effective_date` scalar, even though the original run
already froze the exact resolved content (`rules_context_snapshot.statutory_rule`)
and that key is never read by retry. Mechanism confirmed by code citation in
Stage 03; not yet confirmed as an observed, reproduced divergence. This stage's
top priority is a controlled non-production reproduction attempt.

## Governing sources (confirmed, carried from Stages 01–03)

- `CLAUDE.md` is the sole governing instruction source.
- `docs/wrapper-command/` is reference-only, non-authoritative (01-013).
- Read-only against production code and shared data; controlled test
  fixtures are permitted only in an isolated non-production environment
  (this machine's local `payroll_dev` Postgres instance, confirmed reachable
  — not a shared/production database) and must be fully documented and torn
  down.

## Inputs

- Stage 01 findings — executor-path baseline (01-004/01-005), repository
  layer split (01-002).
- Stage 02 findings — production execution-flow map, execution-trace
  lifecycle map (02-001), retry's zero `execution_trace` step rows (02-002),
  which limits what trace evidence this stage can use to prove parity.
- Stage 03 findings — full configuration catalogue, precedence map,
  duplicate-representation register, snapshot/live boundary map (03-002
  through 03-005) — this stage extends that comparison into calculation and
  persistence parity rather than re-deriving the configuration-source map.
- `tests/test_payroll_retry.py` — existing, working e2e fixture pattern
  (onboarding → PARTIAL run → fix data → retry → assertions → full teardown)
  used as the structural template for this stage's controlled test script.
  Not modified — a new, separate script is used instead, per the
  instruction not to rely on existing scripts/tests without independent
  validation and not to repair retry behaviour.

## Process

1. Build the path-by-path parity map (original run, per-employee retry,
   legacy pre-snapshot/pre-rule-set runs, sequential vs. legacy executor)
   using Stage 01/02 code citations, extended with direct inspection where
   Stage 01–03 did not already cover a required column (rounding, handler
   order, failure/rollback behaviour).
2. Design and run the smallest safe controlled reproduction of the 03-002
   statutory-rule divergence against the local non-production
   `payroll_dev` database: two employees, one fails initially (PARTIAL run),
   a second statutory-rule version is inserted with an effective_from
   between the original resolution and the run's frozen
   `statutory_effective_date`, the failed employee is fixed and retried,
   and the retried employee's PAYE is compared against both candidate
   statutory-rule contents. All test rows are deleted in a `finally` block
   regardless of outcome.
3. Compare context-construction code between `payroll.py` (original) and
   `payroll_retry_service.py` (retry) beyond what Stage 03 already covered
   (client_meta reconciliation) — specifically handler order, rounding,
   and failure/rollback semantics.
4. Verify snapshot parity for every domain in the sprint's required list,
   citing Stage 03's snapshot/live boundary map rather than re-deriving it,
   and filling any gaps (payroll inputs, period context) Stage 03 did not
   explicitly classify.
5. Classify every identified difference using the seven-category scheme in
   the sprint prompt.

## Outputs

Per the sprint prompt's "Required outputs" list (1–14): execution comparison
matrix, context-construction comparison, snapshot-source comparison,
rule-resolution comparison, calculation/rounding comparison,
persistence/state-transition comparison, trace-footprint comparison,
legacy-run compatibility assessment, controlled statutory-divergence test
evidence (or a precise blocked-test design), confirmed-parity register,
divergence register, `findings.md`, `evidence/`, and handoff notes for
Stages 05, 07, 08, 10, 11, 13.

## Prohibited actions

- No edits to production application code, frontend code, migrations, or
  existing tests/scripts.
- No repair of retry behaviour.
- No changes to shared/production data — all controlled execution is
  against the local non-production `payroll_dev` database only, using
  test-scoped IDs, with full teardown.
- Do not start Stage 05 or later.
- Do not rely on Stage 02's flagged-broken scripts without independent
  validation (none are used in this stage).
- Do not infer parity from matching function names or similar code —
  every parity claim must cite the actual comparison performed.

## Completion criteria

- Every path in the sprint's required list is present in the parity map
  with the required per-path fields populated or explicitly marked
  not-applicable with reason.
- The statutory-rule divergence is either reproduced with compliant
  evidence, rejected with compliant evidence, or left `plausible` with an
  explicit statement of what further evidence would resolve it — never
  silently left ambiguous.
- Every required comparison (context construction, snapshot, calculation,
  persistence/state, trace-footprint) is present with evidence citations.
- Every finding uses one of the five valid status values, never a compound
  status string.
- Handoff notes exist for Stages 05, 07, 08, 10, 11, 13.
- `audit-state.md` left `in-progress` — this stage does not self-close.
