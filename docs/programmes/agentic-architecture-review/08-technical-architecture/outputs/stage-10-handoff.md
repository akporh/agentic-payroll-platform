# Stage 08 → Stage 10 Handoff (Evaluation & Assurance)

Every Stage 08 mechanism names its verification method; this handoff consolidates the testability/assurance hooks each design exposes, so Stage 10 designs the evaluation framework against concrete seams rather than re-deriving them. Complements `07-security-identity/outputs/stage-10-handoff.md` (security test standards — unchanged, referenced not restated).

## Per-mechanism verification hooks

| Mechanism | Hooks exposed (design §) | Committed-test closure evidence required |
|---|---|---|
| C1 auth | Route table enumerable from `app.routes`; allowlist is a literal constant; `auth_event`/`step_up_event` tables queryable | Route-enumeration auth test (T4/CG-1); token tamper/expiry/revocation; membership negative paths; step-up freshness + single-consumption; R1 grep-clean + per-route audit-actor tests; epoch labelling fixture test (`auth-foundation-design.md` §6) |
| C2 facade/outbox | Single-transaction facade injectable with failing writers; outbox rows queryable; advisory-lock cycle | Forced-failure atomicity test (SG-2); per-event emission tests (4 events); two-instance single-worker test; consumer idempotency (redelivery) test (`event-audit-foundation-design.md` §8) |
| Append-only floor | Shared trigger function on enumerated table list | UPDATE/DELETE rejection per protected table; step-up `consumed_by` single-transition exception; no-purge design-absence check (DQ-008) |
| Tool layer | Registry enumerable; scoping config introspectable; sanitizer version constant | Uniformity / negative-path / wrapper-independence / fail-closed tests (SS-2, `tool-contracts.md` §5); serialization property tests (Decimal-as-string, PII absence, trace-token provenance for C5) |
| C10 | CAS transitions; `payload_hash`; state snapshot comparand | Double-confirm single-execution; propose→APPROVED-transition→invalidation; concurrent-proposal refusal; terminal-record field assertions (`confirmation-protocol-design.md` §5) |
| C12 | Proposal state machine; Validator pure functions; resolution query with version tie-break | Duplicate-conflict pre-emption; correction recoverability (faulty row readable, v+1 resolves); step-up rejection matrix; origin-equivalence (C11 vs human fixtures identical path); re-validate-at-apply test (`statutory-change-mechanism-design.md` §9) |
| C14 dry run | `dry_run_execution` artifact; input hash; pure-path reuse | **Non-mutation test** (row-count snapshot before/after); dry-run-vs-real equivalence on same fixture; commit-gate hash mismatch rejection (`dry-run-mechanism-design.md` §5) |
| C7 | Pure, replayable detector; versioned thresholds; worked-example fixtures | Formula fixtures pinning R_high/R_low/median/min-window (the 400-vs-42 case); determinism property test; shadow-mode exclusion test; calibration-metric queries (`anomaly-detection-design.md` §7) |
| Remediations | Per-item closure evidence lists | `remediation-designs.md` §§1–8 — notably the cross-workspace reconciliation regression test and the enum-iteration status-classification test |

## Assurance-framework inputs (yours to design, seams provided)

1. **Evidence chain integrity**: session narrative (`agent_session_log`) ↔ `tool_call_log` (SC-3 fields incl. sanitizer version) ↔ C10/C12 records — all 7-year-floor, append-only; Stage 10 can define chain-completeness checks over these linkage keys (`session_ref`, `pending_action_id`, `approval_id`).
2. **LLM capability evals** (gate-level requirements already fixed by SG-3/5/7/11/13): C5 zero-hallucination is enforced *and* testable at the serializer (numeric-token provenance check is code, so the eval measures refusal quality, not just leakage); injection test sets per capability (T1/T2, T5-hostile-source for C11, header-borne for C13) are launch gates whose *existence* Stage 07 fixed — their content/methodology is yours.
3. **Calibration governance (C7)**: the three D-04-01 metrics are derivable from `exception_record` resolution codes + detector replayability — no additional instrumentation needed; Stage 10 defines review cadence and thresholds-change governance.
4. **Fresh-DB discipline**: all closure tests must run against CI's `alembic upgrade head` database (standing rule — local dev DB is drifted); Stage 08's schema designs all include migrations, so every hook above is exercisable in CI.
5. **Residual-risk register items to carry**: DEC-07-04 (audit-tamper residual — review at Stage 10/13, already flagged); trigger-only append-only floor (role separation deferred); dry-run artifacts as gate evidence (retention posture pending DQ-008).
