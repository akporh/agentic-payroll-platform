# Stage 07: Security & Identity — Context

## Status

context-ready (populated 2026-07-17 by the controller on Stage 06's closure — critic PASS, re-critic addendum in `06-compliance-controls/outputs/critic-review.md`)

## Objective

Define the security and identity architecture — at requirements/design level — that the approved 15-capability portfolio needs: the identity/auth foundation (C1), tenant-isolation enforcement and its verification standard, the tool-layer security pattern, audit-store integrity, and approval-action security. This stage owns security mechanism *design decisions* (auth model, session/token approach, enforcement patterns); Stage 08 owns the broader technical architecture that implements them. Stage 06's attribution/identity requirements R1–R6 are binding compliance obligations on this stage's design — the design must show how each is satisfied.

This stage implements nothing. Its deliverable is the security architecture the build must follow and the verification standard that proves it.

## Binding decisions inherited from Stage 02 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-3:

- **D-02-02**: `payroll_reconciliation` repository-level workspace-scoping fix (F-01-33) is mandatory and is a precondition for any agent tool touching it (e.g. `get_reconciliation`). Tool-layer workspace-ownership validation is additionally mandatory as defence in depth — explicitly not an acceptable permanent substitute for the repository-level fix. This stage should verify both layers are actually in place before any agent tool goes live, not just one.

## Binding decisions inherited from Stage 03 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-6 (D-03-01) and `03-agent-portfolio/outputs/tool-portfolio-matrix.md`:

- The revised 15-capability portfolio (`03-agent-portfolio/outputs/agent-capability-matrix.md`) is **approved** — this stage reviews security against that portfolio, not the source architecture document's original tracks.
- **Condition 14**: every tool must have independent workspace-ownership verification — this stage should verify the actual implementation pattern (e.g. a shared decorator/middleware, per Stage 03's `stage-08-handoff.md` recommendation) is applied consistently across all 11 tools in `03-agent-portfolio/outputs/tool-portfolio-matrix.md` (the original 10 plus the new workspace-catalog tool for C13).
- **Conditions 2–3**: `get_reconciliation` and any tool touching `payroll_reconciliation` remain blocked until the repository-level fix lands; this stage should verify tool-layer enforcement specifically once that fix is confirmed by Stage 05.

## Binding requirements inherited from Stage 06 (compliance obligations on this stage's design)

From `06-compliance-controls/outputs/attribution-identity-requirements.md` (R1–R6) via `06-compliance-controls/outputs/stage-07-handoff.md`:

- **R1**: verified actor on every mutating action — the audit-actor derivation path is part of the auth design, not just route protection.
- **R2**: workspace identity derived from the token only — no surface accepts workspace identity from caller input.
- **R3**: named service principals for system-initiated actions (no more `"system"`/`"admin@internal"` literals).
- **R4**: non-repudiation-grade records for approval-class actions.
- **R5**: live-session confirmation for platform-blast-radius approvals; step-up auth vs live-session check is this stage's design choice to make.
- **R6**: no compliance-evidence feature operates in placeholder-identity mode (standing control SC-1 in the control-gate register).

Also binding from Stage 06's outputs: audit-store integrity is a security property (`stage-07-handoff.md` — an attacker who can UPDATE audit rows defeats non-repudiation; DB-layer protection is in this stage's threat model), and the classification upgrade — F-05-03 is a **compliance control failure with false attestation**, F-05-01 a **control-environment failure**; treat auth as compliance remediation with the urgency that framing implies.

## Confirmed platform facts from Stages 05–06 (consume, do not re-verify)

- **F-05-01**: zero authentication exists anywhere; `workspace_id` is caller-supplied throughout. Every scoping assessment to date assumes an honest caller.
- **F-05-03**: reconciliation workspace scoping is open and decorative — three "workspace-scoped" routes accept and discard `workspace_id` (`05-platform-readiness/outputs/reconciliation-scoping-assessment.md`).
- **F-05-11**: two tool-wrapping risks — `load_inputs_for_run(payroll_run_id)` (no workspace parameter at all) and `workspace_info()` (arbitrary `LIMIT 1` workspace pick). Stage 05 suggested checking `workspace_info()`'s current callers directly — that check is in this stage's scope.
- **F-06-01**: the existing audit trail records self-asserted identity (header/body actor inputs, hardcoded defaults) — evidence at `06-compliance-controls/evidence/06-attribution-and-audit-integrity-excerpts.md` §1; note line-number citations pin commit `265db10` and have drifted at HEAD — re-resolve at this stage's own commit.
- **F-06-02/03**: audit writes are post-commit fire-and-forget; no immutability or retention protection on `audit_log`/`event_store` (10 trigger-protected payroll/config tables exist as the platform's own precedent; none covers the audit tables).
- **F-06-05**: the tenant-isolation classification (control failure / control-environment failure / weakness three-way split) — carry it, do not re-derive it.

## Required inputs

Read:

- `docs/programmes/agentic-architecture-review/README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`
- all files under `_core/`
- `05-platform-readiness/outputs/stage-07-handoff.md`, `reconciliation-scoping-assessment.md`, `tool-readiness-baseline.md`, `readiness-closure-plan.md`
- `06-compliance-controls/outputs/stage-07-handoff.md`, `attribution-identity-requirements.md`, `tenant-isolation-control-assessment.md`, `audit-expansion-requirements.md` (§3 integrity properties), `control-gate-register.md`
- `03-agent-portfolio/outputs/tool-portfolio-matrix.md` and `stage-08-handoff.md` (tool-layer pattern recommendation)
- the source architecture document's Track P (auth/identity) design, as the design under review — not as authority
- relevant code to verify security claims: route surfaces, `workspace_info()` and its callers, `load_inputs_for_run` callers, reconciliation routes/repo, audit write paths

Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. What identity architecture (operator model, credential/session/token design, at requirements level) satisfies R1–R6 for this platform's actual deployment shape (small multi-client bureau, single or few operators)?
2. How is workspace identity derived from the token alone (R2) at both the API layer and the tool layer, and what is the standard tool-layer enforcement pattern (Condition 14) — one pattern, applied to all 11 tools, with a verification standard that proves consistency?
3. How are system-initiated actions attributed (R3) — what named service principals exist, and how do they reach the audit record?
4. What makes an approval-class record non-repudiation-grade (R4) on this platform, and does R5 resolve to step-up auth or a live-session check for platform-blast-radius approvals (C12)? Record the design choice and reasoning.
5. What DB-layer protection does the audit store need (F-06-02/03) in this stage's threat model — and does the cut-over epoch treatment for historical unverified-identity audit rows (forwarded by Stage 06 as implementation specification) hold up, or can it be improved?
6. What security closure evidence closes F-05-03 (beyond the code fix — per the tenant-isolation assessment's control-evidence set) and the two F-05-11 functions? What are `workspace_info()`'s current callers, and is it already producing wrong results in a multi-workspace deployment?
7. What is the agent/tool-layer threat model — prompt-injection-to-tool-misuse, tool parameter tampering, cross-workspace exfiltration via tool outputs — and what controls bound it for the 5 LLM-touching capabilities?
8. For each of the 15 capabilities, what security launch gates apply (aligned with, not duplicating, the compliance control-gate register CG-1–15 and Stage 05's readiness matrix)?

## Required investigation

### 1. Identity & auth architecture requirements (C1) — primary task

Review the source document's Track P design against the approved portfolio and R1–R6. Define the operator/principal model (human operators + named service principals), token/session requirements, the audit-actor derivation path (R1), and token-derived workspace identity (R2). Requirements level: what the build must guarantee and how it is verified — not library or framework choices unless security-load-bearing.

### 2. Tenant-isolation enforcement and verification standard

From F-05-03/F-06-05 and D-02-02: define the two-layer enforcement standard (repository-level + tool-layer) and the verification standard that proves it — invariant-named regression tests, per-route negative-path checks, and the isolation control statement from `tenant-isolation-control-assessment.md` §3. Include the F-05-11 functions; check `workspace_info()` callers directly.

### 3. Tool-layer security pattern

Resolve Condition 14 into one concrete pattern (shared decorator/middleware or equivalent) with mandatory properties, applied uniformly across the 11-tool portfolio; define how tool-layer refusals are logged (ties to SC-3).

### 4. Audit-store integrity threat model

Treat `audit_log`/`event_store` integrity as a security property: who can tamper, via what path, and what protection (append-only enforcement, access separation) the threat model requires. Confirm or improve the historical-rows cut-over epoch treatment. Mechanism choice (trigger vs role permissions) may be constrained here but is built by Stage 08.

### 5. Approval-action security (R4/R5)

Define non-repudiation-grade approval record properties and resolve R5 (step-up vs live-session) for C12-class approvals, recording the reasoning.

### 6. Agent-layer threat model

For the 5 LLM-touching capabilities and C10's confirmation protocol: prompt-injection and tool-misuse threat model, output-handling rules, and the controls that bound blast radius (read-only tools, proposal-only writes, confirmation gates).

### 7. Security gate register

Per-capability security launch gates, aligned with CG-1–15 and Stage 05's blocker register — security-specific criteria only; no duplication.

## Required outputs

Create:

1. `outputs/identity-architecture-requirements.md`
2. `outputs/tenant-isolation-verification-standard.md`
3. `outputs/tool-layer-security-pattern.md`
4. `outputs/audit-integrity-threat-model.md`
5. `outputs/approval-security-design.md` (incl. the R5 resolution)
6. `outputs/agent-layer-threat-model.md`
7. `outputs/security-gate-register.md`
8. `outputs/stage-08-handoff.md`
9. `outputs/stage-10-handoff.md` (verification/assurance standards for Stage 10 to evaluate against)

Update:

- `findings.md` (F-07-* per finding discipline below)
- `decisions.md`
- `_inputs/source-register.md` where required
- `review-state.md`
- `decision-queue.md` for any non-blocking forwarded question

(`outputs/critic-review.md` is produced by the independent critic, not the executor.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` extended with the Stage 05/06 field pattern: finding ID / affected capability(ies) / current implementation / expected guarantee (or intended design) / evidence / gap / consequence / severity / classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner. Keep confirmed, draft and parked findings separate. Verify security claims against code and tests, not documents alone. Committed evidence only, pinned to a named commit; label any working-tree observation separately.

## Explicitly out of scope

- implementing fixes, code, tests or migrations
- technical mechanism build design beyond security properties — outbox, schema, tool contracts (Stage 08)
- UI design (Stage 09)
- evaluation methodology (Stage 10 — this stage hands it verification standards, not eval design)
- commercial sequencing (Stage 11)
- re-litigating DQ-006/DQ-007/DQ-008 (queued human decisions) or reopening Stage 02–06 decisions
- re-verifying Stage 05/06 confirmed platform facts (consume them; re-resolve drifted line numbers only)
- starting Stage 08

## Constraints

- Read-only with respect to production code, configuration and data.
- Writes stay inside `docs/programmes/agentic-architecture-review/` (programme policy).
- Do not infer security adequacy from the architecture document alone; verify against code and tests.
- Every security requirement must name its verification method — a requirement without closure evidence is not complete.
- Do not weaken any gate in the compliance control-gate register; security gates add to CG-1–15, never subtract.
- Do not create artificial human decisions where evidence and inherited principles already resolve the issue — but do not absorb genuine product/risk/compliance choices either; classify them per `CRITIC.md`.

## Completion criteria

Stage 07 is ready for the critic only when:

- the identity architecture satisfies R1–R6 with each requirement's satisfaction path stated explicitly
- the tenant-isolation two-layer standard and its verification standard are defined, including the F-05-11 functions and the `workspace_info()` caller check
- the tool-layer pattern resolves Condition 14 concretely for all 11 tools
- the audit-integrity threat model covers F-06-02/03 and disposes of the cut-over epoch question
- R5 is resolved with recorded reasoning
- the agent-layer threat model covers all 5 LLM-touching capabilities and C10
- every capability has a security launch-gate entry
- all human decisions are recorded and classified; non-blocking questions are in `decision-queue.md`
- Stage 08 and Stage 10 handoffs are complete and consistent with findings

## Completion procedure (D-003 lifecycle)

1. Mark Stage 07 `awaiting-critic` in `review-state.md` and this file.
2. The controller runs the independent critic per `CRITIC.md`; report saved to `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, the controller closes the stage and opens Stage 08 automatically per `RUNBOOK.md`.
4. Do not begin Stage 08 before closure.

## Next action

**Run the Stage 07 primary-executor pass per `RUNBOOK.md`.**
