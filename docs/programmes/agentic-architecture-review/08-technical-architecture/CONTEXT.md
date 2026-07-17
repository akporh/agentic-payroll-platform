# Stage 08: Technical Architecture — Context

## Status

awaiting-critic (executor pass complete 2026-07-17; all 10 outputs produced, findings/decisions/queue updated; evidence pinned at `573be0d`)

## Objective

Design the technical mechanisms that implement the approved 15-capability portfolio's platform foundations and the requirements Stages 05–07 fixed: the C1 auth build, the event/outbox/notification foundation (C2) with generalised audit persistence, the tool layer (contracts + guard wrapper), the C10 confirmation protocol, the C12 statutory-change mechanism, the C14 dry-run mechanism, and the C7 detection formulas. **Design level, not implementation**: schemas, state machines, contracts, and mechanism choices with their verification standards — the build itself happens outside this programme (Phase 3 adoption).

This stage is where the accumulated implementation-specification queue (DQ-001–005, plus DQ-008's mechanism constraint) gets answered. Compliance requirements (Stage 06) and security requirements (Stage 07) are binding inputs — this stage chooses *how*, never *whether*.

## Binding decisions inherited from Stage 02 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-3–HD-5:

- **D-02-02**: any tool touching `payroll_reconciliation` requires both the repository-level workspace-scoping fix and independent tool-layer validation — design both, not either/or.
- **D-02-03**: historical reproducibility (F-01-27/29/38) must be resolved before designing any mechanism that explains/reconstructs historical payroll outcomes (Track X investigation agents, Track W historical-explanation mode). Design work for these can proceed on the resolution mechanism itself, but the agent-facing capability built on top is launch-blocked until it's resolved.
- **D-02-04**: design the statutory-rule change-management mechanism as its own deterministic capability, separate from any AI compliance-detection design (Y1). Y1's design must not include migration-authoring/execution/deployment capability.
- Also carried from Stage 02: what "dry-run payroll" means mechanically for the Onboarding Agent (Y2) safety gate — does it exercise the real sequential executor/snapshot path, or a separate simulation (F-02-10)? This needs a concrete answer, not an assumption.

## Binding decisions inherited from Stages 03–07 (pre-scope — do not re-litigate)

- **D-03-01** (HD-6): the 15-capability portfolio and 11-tool list (`03-agent-portfolio/outputs/agent-capability-matrix.md`, `tool-portfolio-matrix.md`) are approved and are not re-decided here; Stage 08 designs mechanisms for them. All 14 approved conditions preserved. C4/C8 blocked, C9 rejected, C15 deferred.
- **D-04-01** (HD-7): C7 uses the layered calibration shape (absolute thresholds → period-on-period variance gated on a history window; peer-pattern deferred); design the formulas within that shape. C7 is hard-gated on the exception-resolution workflow existing.
- **Stage 06 requirements** (critic-passed, closed): audit-expansion domains 1–4 and integrity properties (`audit-expansion-requirements.md`), the C12 control design (`statutory-change-control-design.md` — roles, evidence, approval record §4, append-only rule history §5), the agent/tool audit standard (SC-3 fields, 7-year retention floor pending DQ-008), and CG-1–15. Mechanisms must satisfy them; none may be weakened.
- **Stage 07 requirements** (critic-passed, closed): `07-security-identity/outputs/stage-08-handoff.md` items 1–10 are the security constraints on this stage's designs — notably **DEC-07-02** (operator↔workspace membership relation, not Track P's single column), **DEC-07-03** (step-up re-auth for C12 approvals with freshness window and one-approval-per-event), the tool-guard wrapper properties P1–P8, the audit-store protection floor (append-only triggers; outbox covers audit records), the cut-over epoch as persisted data, and SG-1–15.

## Confirmed platform facts to consume (do not re-verify)

- F-05-01/02/04 (zero auth; no event consumer/notification/exception foundation; C12 greenfield) and the full blocker register + `readiness-closure-plan.md` minimums.
- F-06-01–05 (self-asserted audit identity; fire-and-forget audit writes; no audit immutability/retention; no statutory provenance schema; tenant-isolation classifications).
- F-07-01–03 (five decorative routes — the fix list is stage-08-handoff item 3; `workspace_info()` disposition; CORS pinning at C1).
- Line-number citations pin `ea1590a` — re-resolve at this stage's own commit where needed.

## Required inputs

Read:

- `docs/programmes/agentic-architecture-review/README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`
- all files under `_core/`
- the four stage-08 handoffs: `03-agent-portfolio/outputs/stage-08-handoff.md`, `05-platform-readiness/outputs/stage-08-handoff.md`, `06-compliance-controls/outputs/stage-08-handoff.md`, `07-security-identity/outputs/stage-08-handoff.md`
- Stage 06/07 requirement outputs cited above; Stage 05 `readiness-closure-plan.md`, `platform-blocker-register.md`, `tool-readiness-baseline.md`
- the source architecture document's Tracks P/V/X/Y mechanism proposals (design under review, not authority)
- relevant code to ground designs: `backend/domain/payroll/audit_events.py`, `audit_log_repo.py`/`event_store_repo.py`, `payroll_run_service.py` (run creation path for dry-run design), `sequential_executor.py` (dry-run feasibility), reconciliation model/repo/service/routes, migration precedents (`3da637afb11b` triggers; `a0b1c2d3e4f5` updated_at)

Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. **C1 build design**: operator + membership schema, token claims/lifetime/revocation posture, the shared route dependency and unauthenticated allowlist, step-up event objects, auth-event audit records, R1 rewiring plan (removing the caller-supplied actor inputs), R2 path-vs-claim enforcement point, cut-over epoch persistence (07 handoff items 1–3, 6–7).
2. **Event/outbox/audit mechanism (C2)**: transactional outbox design covering notification events **and** audit records; the audit-mechanism generalisation (arbitrary entity types — signature generalisation vs parallel builders); the four new events; consumer worker (single-worker constraint); `workspace_notification` schema; exception data model (D-04-01's workflow substrate).
3. **Tool contracts**: field-level contracts for all 11 tools incl. the C13 catalog tool (Stage 03 handoff items 3, 4, 8), the guard-wrapper implementation shape (P1–P8), null-trace behaviour, Decimal-as-string serialization, PII sanitizer versioning.
4. **C10 protocol**: pending-action state machine — expiry, conflict, idempotency, run-state invalidation (DQ-002) — with the security constraints from `07-security-identity/outputs/approval-security-design.md` §4 (payload freezing, expiry records, idempotent execution).
5. **C12 mechanism**: schema/routes/state machine holding the §4 approval record; statutory provenance schema (F-06-04); pre-emptive duplicate/conflict validation; impact-preview computation placement (Stage 06 §7); append-only rule history + correction handling with recoverable prior values; step-up integration (DEC-07-03).
6. **C14 dry-run mechanism** (DQ-003/004): real-executor-path vs simulation, what "safely separated from production state" means operationally (does it create a `payroll_run` row?), under the operator's verified identity (SG-14).
7. **C7 formulas** (DQ-001): concrete statistics, thresholds, minimum history window within D-04-01's layered shape.
8. **Remediation designs**: reconciliation workspace-scoping fix (column+backfill+repo+service+routes per Stage 05's five items), the five decorative routes (F-05-03 + F-07-01), `load_inputs_for_run` and `workspace_info()` closures, audit-store append-only mechanism choice (trigger vs role separation), `salary_definition` edit-lock and D-ARCH-1 status-drift items from the closure plan's High tier.
9. **DQ-008 mechanism constraint**: retention posture implementation (keep-at-least-7y, no deletion mechanism) — confirm no design pre-empts the legal determination.

## Required outputs

Create under `outputs/`:

1. `auth-foundation-design.md` (C1 — answers Q1)
2. `event-audit-foundation-design.md` (C2 + audit generalisation — Q2)
3. `tool-contracts.md` (all 11 tools + wrapper shape — Q3)
4. `confirmation-protocol-design.md` (C10 — Q4)
5. `statutory-change-mechanism-design.md` (C12 — Q5)
6. `dry-run-mechanism-design.md` (C14 — Q6)
7. `anomaly-detection-design.md` (C7 — Q7)
8. `remediation-designs.md` (Q8 fix designs with closure evidence per item)
9. `stage-09-handoff.md` (UI-relevant mechanism surfaces: C10 confirmation UI, C12 approval UI, notification/work-queue, C13/C14 flows)
10. `stage-10-handoff.md` (testability/verification hooks each mechanism exposes)

Update: `findings.md` (F-08-*), `decisions.md`, `_inputs/source-register.md` where required, `review-state.md`, `decision-queue.md` (mark DQ-001–005 resolved with design references where answered; DQ-006/007/008 remain human-gated).

(`outputs/critic-review.md` is produced by the independent critic, not the executor.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` extended with the Stage 05/06 field pattern (consequence/classification/minimum remediation/closure evidence/confidence/required human decision/downstream owner). Verify mechanism-feasibility claims against code, not documents alone. Committed evidence only, pinned to a named commit; label any working-tree observation separately.

## Explicitly out of scope

- implementing anything — no code, tests, or migrations
- UI design (Stage 09 — hand it surfaces, not screens)
- evaluation methodology (Stage 10)
- commercial sequencing (Stage 11); roadmap (Stage 13)
- re-litigating DQ-006/007/008 or any closed-stage decision; weakening any CG/SG gate
- re-verifying Stage 05–07 confirmed facts (consume; re-resolve drifted line numbers only)
- starting Stage 09

## Constraints

- Read-only with respect to production code, configuration and data. Writes stay inside `docs/programmes/agentic-architecture-review/`.
- Every mechanism design must state how it satisfies the binding compliance/security requirements it implements, and name its verification method — a design without closure evidence is not complete.
- Mechanism choices constrained by prior stages (outbox direction, append-only floor, wrapper properties P1–P8, membership model, step-up) are freedoms only within the stated constraints.
- Do not create artificial human decisions where evidence and inherited principles already resolve the issue; classify genuine choices per `CRITIC.md`.

## Completion criteria

Stage 08 is ready for the critic only when:

- every Q1–Q9 question has a design answer or an explicitly-classified open item
- DQ-001–005 are each resolved by a named design section (or re-classified with reasoning)
- every design names its binding requirements (CG/SG/R1–R6/SC/SS references) and its verification method
- the remediation designs cover all of Q8 with closure evidence per item
- Stage 09 and Stage 10 handoffs are complete and consistent with the designs
- all human decisions are recorded and classified; non-blocking questions are in `decision-queue.md`

## Completion procedure (D-003 lifecycle)

1. Mark Stage 08 `awaiting-critic` in `review-state.md` and this file.
2. The controller runs the independent critic per `CRITIC.md`; report saved to `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, the controller closes the stage and opens Stage 09 automatically per `RUNBOOK.md`.
4. Do not begin Stage 09 before closure.

## Next action

**Run the independent critic per `CRITIC.md`** (report → `outputs/critic-review.md`), then controller disposition.
