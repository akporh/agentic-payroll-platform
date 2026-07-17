# Stage 06: Compliance & Controls — Context

## Status

closed (2026-07-17 — independent critic PASS after one REVISE cycle: RC-1/RC-2/RC-3 corrections applied and verified by a narrow re-critic pass, addendum in `outputs/critic-review.md`; 0 blocking human decisions; DQ-006/007/008 remain queued as non-blocking. Primary executor pass completed 2026-07-15: all 9 outputs produced, 5 confirmed findings F-06-01–05, 0 draft, 0 parked. Context originally populated 2026-07-15 by the controller on Stage 05's closure.)

## Objective

Assess the platform's compliance and control posture for the approved 15-capability portfolio, and define — at the requirements level — the compliance workflows and control standards the platform must satisfy before the capabilities that depend on them can be built or launched.

This stage owns compliance workflow **design requirements**; it does not implement anything, and it does not own security mechanisms (Stage 07) or technical mechanism design (Stage 08). Its primary deliverable is the control framework: who approves what, on what evidence, with what audit record, retained how long.

## Binding decisions inherited from prior stages (do not re-litigate)

Full detail in `_core/HUMAN-DECISIONS.md`:

1. **D-02-04**: statutory-rule change management (C12) is its own deterministic, compliance-owned capability — independent of Compliance Monitoring (C11), which is restricted to detect/compare/propose only and must never author, execute, or deploy a production migration. Whether C11 may apply migrations directly is decided (no) — do not reopen.
2. **D-02-01**: the agent-layer architecture document's "NEEDS REVISION" status is confirmed still open by the human reviewer; this review is the formal revision path. Resolved — awareness only, no chase-up.
3. **D-03-01**: the 15-capability portfolio is the approved reference portfolio, including C12's split from C11. Capability scope is fixed.
4. **D-04-01**: layered C7 calibration (absolute thresholds → period-on-period variance → peer-pattern deferred), gated on the exception-resolution workflow. Relevant here only insofar as exception-resolution records are compliance evidence.
5. **D-02-02 / D-02-03**: reconciliation workspace scoping and the historical-reproducibility findings (F-01-27/29/38) are mandatory launch preconditions for C8/C4 — Stage 05 re-verified their current status; consume its findings, do not re-derive.

## Confirmed platform facts from Stage 05 (consume, do not re-verify)

- **F-05-01**: zero authentication exists anywhere; there is no verified identity to attribute any approval to. Compliance attribution requirements defined by this stage will be unbuildable until Track-P-equivalent identity ships — state the requirements anyway; Stage 07/08 own the mechanism.
- **F-05-02**: event/notification/exception-tracking foundation is entirely unbuilt.
- **F-05-03**: `payroll_reconciliation` workspace scoping is open and worse than Stage 01 found (decorative "workspace-scoped" routes) — a tenant-isolation control failure with bureau-client data-isolation implications, not purely a Stage 07 technical item.
- **F-05-04**: C12 is entirely greenfield — no admin route, no application-level write path, no duplicate validation, no approval record, no preview/impact analysis. Zero test coverage of the capability itself.
- **Audit coverage (F-01-40 reconfirmed)**: `audit_log`/`event_store` cover only `payroll_run` state transitions. The current audit mechanism cannot record a statutory-rule-change approval at all.

## Required inputs

Read:

- `docs/programmes/agentic-architecture-review/README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`
- all files under `_core/`
- `03-agent-portfolio/outputs/stage-06-handoff.md`
- `03-agent-portfolio/outputs/tool-portfolio-matrix.md` (the "required audit record" column)
- `04-outcome-discovery/outputs/compliance-outcome-chain.md`
- `05-platform-readiness/outputs/stage-06-handoff.md`
- `05-platform-readiness/outputs/statutory-change-platform-readiness.md`
- `05-platform-readiness/outputs/audit-coverage-assessment.md`
- `05-platform-readiness/outputs/reconciliation-scoping-assessment.md`
- `05-platform-readiness/outputs/event-notification-readiness.md`
- the current agent-layer architecture document (including its `agent_session_log` design and proposed 7-year retention)
- relevant code needed to verify control claims: `statutory_rule` model and seed migrations, `backend/domain/payroll/audit_events.py`, `event_store` write path, reconciliation routes/repo, and the test suite's statutory coverage

Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. What approval workflow must govern any statutory-rule change (who approves, what evidence is required, what audit record is created) — and is the workflow identical regardless of whether the change was detected by C11 or by a human?
2. How must that workflow respect the existing `statutory_rule (country_code, effective_from)` UNIQUE invariant and the platform-level (not workspace-scoped) nature of statutory rules?
3. What counts as an authoritative external source for FIRS/PenCom regulatory changes, and what freshness and provenance/citation requirements must C11 proposals meet so a human can verify claims against the regulatory text itself? (Stage 03 flagged the source-authority question as legal-risk territory this review does not adjudicate — define the policy structure and escalate the residual legal question explicitly rather than deciding it.)
4. What audit standard applies to agent/tool activity: mandatory fields and retention period for tool-call records, and whether tool-call-level logging needs the same 7-year retention the source document proposes for `agent_session_log`?
5. What minimum audit expansion (beyond PAYROLL_RUN transitions) is required for the platform to hold compliance evidence: configuration-change history, statutory-change approvals, exception-resolution lifecycle, operator-action attribution?
6. What identity/attribution requirements do the above controls impose (consuming F-05-01), stated as requirements for Stage 07/08 to satisfy?
7. Is the reconciliation workspace-scoping gap a compliance control failure (bureau-client data isolation) in addition to a security defect, and what control evidence closes it?
8. For each approved capability, what compliance/control evidence must exist before launch (control gates, distinct from Stage 05's technical readiness gates)?

## Required investigation

### 1. Statutory-rule change-management control design (C12) — primary task

From the confirmed greenfield baseline (F-05-04), define the required control workflow: proposer → validator → approver roles; required evidence per change (source citation, effective date, impact preview); the approval record's mandatory content; rejection/rollback/correction handling; interaction with effective-dating and the UNIQUE invariant. Same workflow regardless of change source (C11 vs human) unless evidence forces a distinction — record the reasoning either way.

### 2. Compliance-monitoring source policy (C11)

Define authoritative-source criteria, freshness requirements, and provenance/citation requirements for C11 proposals. Explicitly separate what this review can fix as policy structure from the residual legal-risk sign-off that belongs to the human reviewer/professional advice.

### 3. Agent/tool audit standard

Resolve the open "required audit record" level from Stage 03's tool-portfolio matrix: mandatory fields, retention, and whether tool-call logs align with the proposed 7-year `agent_session_log` retention. Verify current logging reality against code before stating the gap.

### 4. Audit-expansion requirements for compliance evidence

From the confirmed PAYROLL_RUN-only audit scope, specify the minimum audit domains the platform must add (domain-change audit, statutory-change approval audit, exception-resolution audit, agent/tool invocation audit) for compliance evidence to exist — requirements only; Stage 08 owns the mechanism.

### 5. Attribution and identity control requirements

State the identity guarantees compliance controls require (verified operator identity on approvals, non-repudiation expectations), consuming F-05-01 without re-verifying it. These become binding requirements on Stage 07's security architecture.

### 6. Tenant-isolation control assessment

Assess the reconciliation scoping gap (F-05-03) as a control failure: what isolation guarantees a payroll bureau owes its clients, whether any other confirmed gap rises to the same classification, and what control evidence (not just code fix) closes each.

### 7. Control-gate register

For each of the 15 capabilities, record the compliance/control launch gates, aligned with (not duplicating) Stage 05's capability-readiness matrix and blocker register.

## Required outputs

Create:

1. `outputs/statutory-change-control-design.md`
2. `outputs/compliance-monitoring-source-policy.md`
3. `outputs/agent-tool-audit-standard.md`
4. `outputs/audit-expansion-requirements.md`
5. `outputs/attribution-identity-requirements.md`
6. `outputs/tenant-isolation-control-assessment.md`
7. `outputs/control-gate-register.md`
8. `outputs/stage-07-handoff.md`
9. `outputs/stage-08-handoff.md`

Update:

- `findings.md` (F-06-* per `_core/FINDING-SCHEMA.md`)
- `decisions.md`
- `_inputs/source-register.md` where required
- `review-state.md`
- `decision-queue.md` for any non-blocking forwarded question

(`outputs/critic-review.md` is produced by the independent critic, not the executor.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` and the Stage 05 pattern: finding ID / affected capability(ies) / current implementation / expected guarantee / evidence / gap / consequence / severity / classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner. Keep confirmed, draft and parked findings separate. Verify control claims against code and tests, not documents alone. Committed evidence only; label any working-tree observation separately.

## Explicitly out of scope

- implementing fixes, code, tests or migrations
- security architecture and auth mechanism design (Stage 07)
- technical mechanism design — outbox, schema, tool contracts, dry-run (Stage 08)
- UI design (Stage 09)
- commercial sequencing (Stage 11)
- adjudicating the legal question of which external sources are authoritative (escalate; do not decide)
- reopening Stage 02–05 decisions or re-verifying Stage 05's confirmed platform facts
- starting Stage 07

## Constraints

- Read-only with respect to production code, configuration and data.
- Writes stay inside `docs/programmes/agentic-architecture-review/` (programme policy).
- Do not infer control adequacy from the architecture document alone; verify against code and tests.
- Do not reduce mandatory control gates to documentation warnings.
- Do not create artificial human decisions where evidence and inherited principles already resolve the issue — but do not absorb genuine product/risk/legal choices either; classify them per `CRITIC.md`.

## Completion criteria

Stage 06 is ready for the critic only when:

- the C12 control workflow is fully specified at requirements level, including the C11-vs-human source question
- C11 source/freshness/provenance policy is defined, with the residual legal sign-off explicitly framed
- the agent/tool audit standard resolves Stage 03's open retention/content question
- audit-expansion requirements cover all four audit domains
- attribution/identity requirements are stated as Stage 07 obligations
- the tenant-isolation control assessment reaches a definitive classification with closure evidence named
- every capability has a compliance/control launch-gate entry
- all human decisions are recorded and classified; non-blocking questions are in `decision-queue.md`
- Stage 07 and Stage 08 handoffs are complete and consistent with findings

## Completion procedure (D-003 lifecycle)

1. Mark Stage 06 `awaiting-critic` in `review-state.md` and this file.
2. The controller runs the independent critic per `CRITIC.md`; report saved to `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, the controller closes the stage and opens Stage 07 automatically per `RUNBOOK.md`.
4. Do not begin Stage 07 before closure.

## Next action

**None — stage closed 2026-07-17.** Stage 07 is open (`07-security-identity/CONTEXT.md`); later stages may cite F-06-01–05 and this stage's outputs.
