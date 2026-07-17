# Stage 06: Compliance & Controls — Findings

Schema: `_core/FINDING-SCHEMA.md`, extended with the Stage 05 field pattern per this stage's `CONTEXT.md` finding discipline. Draft and confirmed findings are kept in separate sections below — never merge them.

All code evidence read at git commit `265db103cfb6a6b490c8655d5ceb4b776303e6fe` (branch `uat`, 2026-07-15) — committed state only; no working-tree observations were used.

## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

_None._

---

## Confirmed Findings

(meet the evidence standard in `_core/EVIDENCE-STANDARD.md` — safe to cite from later stages)

### F-06-01: Audit-record actor identity is caller-supplied and self-asserted on every attributed write path
- **Affected capability(ies)**: all compliance-evidence capabilities (C12, C10), plus the existing run-transition and reconciliation-resolution audit trail
- **Current implementation**: `performed_by` arrives via an unauthenticated `X-Performed-By` request header defaulting to `"admin@internal"` (`backend/api/routes/payroll.py:1146,1173,1193` — retry/approve/lock); the pay transition takes `actor_id` from the request body defaulting to `"system@internal"` (payroll.py:1211–1225); reconciliation resolution takes `resolved_by` as free text from the request body (payroll.py:1318–1331). Service-layer defaults hardcode `"admin@internal"` (`payroll_approval_service.py:44,114,187`; `payroll_retry_service.py:497,508,680`).
- **Intended design**: the source architecture document's own principle — "Placeholder operator_id audit trail is worse than none" (`agent-layer-architecture.html:496`) — and F-05-01's consumed fact that no verified identity exists yet. No documented intent says header/body attribution was meant to be permanent; it is a pre-auth placeholder in production write paths.
- **Identified gap**: every attributed record in `audit_log` (and `resolved_by` on reconciliation rows) is unverifiable — any caller can assert any identity, and absent callers are recorded as `admin@internal`/`system@internal` placeholders indistinguishable from deliberate attribution.
- **Evidence**: `evidence/06-attribution-and-audit-integrity-excerpts.md` §1 (direct code excerpts with path:line)
- **Consequence**: every attributed audit record written to date is inadmissible as attribution evidence — any caller can assert any identity — and no approval-class action can meet the non-repudiation requirement (R4) until verified identity ships.
- **Severity**: High — the audit trail that exists cannot attribute any action for compliance purposes under realistic conditions; not Critical because it does not itself miscalculate or corrupt financial data, and the systemic auth absence is already rated by F-05-01.
- **Classification**: control failure (attribution) — remediation dependent on the C1 control-environment fix (F-05-01); the attribution control cannot be built before verified identity exists.
- **Minimum remediation**: audit actor derived from the verified principal only (R1, `outputs/attribution-identity-requirements.md`); caller-supplied actor inputs (header `X-Performed-By`, body `actor_id`/`resolved_by`) and hardcoded service-layer defaults removed; documented cut-over epoch labelling pre-auth audit rows "identity unverified" (the past cannot be re-attributed).
- **Closure evidence**: committed tests proving every mutating route derives the audit actor from the authenticated principal and rejects unauthenticated callers; a grep-clean check that no route or service accepts caller-supplied actor identity; the cut-over epoch documented.
- **Confidence**: High
- **Required human decision**: none — the cut-over-epoch treatment is an implementation specification (forwarded in `outputs/stage-07-handoff.md`), not a risk choice.
- **Downstream owner**: Stage 07 (identity mechanism, R1–R6), Stage 08 (audit write path); gates CG-1 and SC-1 in `outputs/control-gate-register.md`.
- **Status**: confirmed
- **Date**: 2026-07-15
- **Raised by**: Stage 06, attribution/identity investigation (§5 of `CONTEXT.md`)

### F-06-02: Audit and event writes are post-commit, non-transactional, fire-and-forget
- **Affected capability(ies)**: all four audit domains in `outputs/audit-expansion-requirements.md`; compliance-evidence completeness generally
- **Current implementation**: state changes commit first; `save_audit_log`/`save_event` are then called outside that transaction, each opening its own `SessionLocal()` and committing independently (`payroll_approval_service.py:88–102`, comment "Write audit trail after successful commit"; `audit_log_repo.py:25–75`; `event_store_repo.py`). No retry, outbox, or failure alarm exists (event-store consumer confirmed absent by F-05-02).
- **Intended design**: the architecture document's own Blocking Condition 3 acknowledges "Events written post-commit (fire-and-forget)" as a gap and assigns the transactional-outbox fix to Track V (`agent-layer-architecture.html`, blocking item 3).
- **Identified gap**: a failed audit/event INSERT after a successful state-change commit leaves the state change standing with no audit record and no error surfaced — audit-trail completeness is not guaranteed, which undermines its evidentiary value even where coverage exists.
- **Evidence**: `evidence/06-attribution-and-audit-integrity-excerpts.md` §2
- **Consequence**: audit-trail completeness cannot be attested — a state change can stand with no audit record and no alarm — which undermines the evidentiary value of the whole trail even where coverage exists.
- **Severity**: Medium — an edge-condition integrity gap (requires a write failure in the narrow post-commit window); already on the intended-fix path for events, but the fix must be explicitly extended to audit records, which no document currently states.
- **Classification**: control weakness — the "reliably written" integrity property (`outputs/audit-expansion-requirements.md` §3.2) is absent; an intended fix direction (Track V transactional outbox) exists but does not yet name audit records.
- **Minimum remediation**: couple audit and event writes to the state-change transaction via the transactional outbox, explicitly extended to audit records across all four audit domains — not notification events alone.
- **Closure evidence**: committed test demonstrating that a failed audit write cannot leave a committed state change without an audit record (rollback or guaranteed retry); outbox path shown to cover all four audit domains.
- **Confidence**: High
- **Required human decision**: none.
- **Downstream owner**: Stage 08 (outbox mechanism, per `outputs/stage-08-handoff.md`); gate CG-2.
- **Status**: confirmed
- **Date**: 2026-07-15
- **Raised by**: Stage 06, audit-expansion investigation (§4 of `CONTEXT.md`)

### F-06-03: No immutability protection and no retention policy exists for `audit_log`/`event_store`
- **Affected capability(ies)**: all compliance-evidence capabilities; non-repudiation (R4 in `outputs/attribution-identity-requirements.md`)
- **Current implementation**: no DB trigger, constraint, or permission restricts UPDATE/DELETE on `audit_log` or `event_store` (trigger sweep, corrected 2026-07-17 per critic RC-1: **10** trigger-bearing migrations exist, all on payroll/config tables — workspace-live enforcement, payroll_run paid/snapshot/state-machine/status-transition locks, payroll_result paid/mutation locks, payroll readiness, salary_definition paid-lock, snapshot physical immutability — none references the audit tables); no retention, purge, or archival mechanism exists anywhere in `backend/` or `migrations/` (grep sweep, zero matches); `ea05e71efbd7:12` explicitly leaves both tables unconstrained even for payload shape.
- **Intended design**: the platform already demonstrates the intended pattern elsewhere — `3da637afb11b` protects `payroll_result` rows for PAID runs with UPDATE **and** DELETE triggers; the architecture document proposes 7-year retention, but only for the future `agent_session_log` (`agent-layer-architecture.html:938,1150–1151`), with no stated policy for the existing audit tables.
- **Identified gap**: audit rows are mutable and deletable by any DB-level actor with app credentials, and their retention is accidental (nothing deletes them, but nothing guarantees or protects them either) — the records cannot currently support a non-repudiation claim.
- **Evidence**: `evidence/06-attribution-and-audit-integrity-excerpts.md` §§3–4, 7
- **Consequence**: audit records cannot support a non-repudiation claim (R4) — a DB-level actor can silently alter or delete history — and their retention is accidental rather than guaranteed.
- **Severity**: Medium — no current production harm observed and exploitation requires DB access, but the gap structurally caps the evidentiary value of every audit record written today.
- **Classification**: control gap — the "immutable" and "retained" integrity properties (`outputs/audit-expansion-requirements.md` §3) are absent; the platform's own trigger pattern (10 migrations protecting payroll/config tables) shows the mechanism precedent exists.
- **Minimum remediation**: append-only enforcement on `audit_log`/`event_store` (DB trigger vs role permissions is a Stage 08 choice; precedent `3da637afb11b`); retention posture "keep at least 7 years, build no deletion mechanism" pending DQ-008.
- **Closure evidence**: committed test proving UPDATE/DELETE against the audit tables is rejected; a recorded retention policy citing the DQ-008 resolution.
- **Confidence**: High
- **Required human decision**: DQ-008 (legal basis of the 7-year retention figure) — non-blocking, forwarded in `decision-queue.md`; the interim keep-at-least posture does not pre-empt it.
- **Downstream owner**: Stage 08 (enforcement mechanism), Stage 07 (audit-store integrity in the threat model); standing controls SC-3/SC-4.
- **Status**: confirmed
- **Date**: 2026-07-15
- **Raised by**: Stage 06, audit-expansion investigation

### F-06-04: The database retains no provenance, approval, or history for statutory-rule content changes
- **Affected capability(ies)**: C12 (primary), C11, C4/C5 (historical explanation of rule-driven outcomes)
- **Current implementation**: `statutory_rule` carries no `created_at`/`updated_at`, no source-citation field, and no approval linkage — full column list: `statutory_rule_id, state, version, rules_jsonb, tax_method, country_code, effective_from` (`backend/infra/db/models/statutory_rule.py:7–23`; the `a0b1c2d3e4f5` updated_at migration covered five other tables and not this one). The one historical rate correction (`de1f2a3b4c5d`, NG PAYE bands to NTA 2025) destructively `DELETE`d and re-inserted `tax_band` rows; the Act citation, the description of the error, and the old values survive only in the migration file's docstring/constants and git history — the database records none of it.
- **Intended design**: undocumented — no spec states the DB should carry rule-change provenance today; the requirement is established by this stage's C12 control design (approval record, §4) and D-02-04's compliance-owned change-management decision.
- **Identified gap**: even a perfectly executed manual rate change is invisible as compliance evidence: who changed statutory rates, when, on what authority, and what the prior values were cannot be answered from the platform's own records.
- **Evidence**: `evidence/06-attribution-and-audit-integrity-excerpts.md` §§5–6
- **Consequence**: even a perfectly executed statutory-rate change is invisible as compliance evidence — who changed rates, when, on what authority, and what the prior values were cannot be answered from the platform's own records — and C12's approval record (control design §4) has no schema to land in.
- **Severity**: Medium — the current developer-migration path leaves provenance in git (weak but non-zero), and D-02-04's workflow is not yet built; the gap becomes Critical-blocking only for C12's launch, which `outputs/control-gate-register.md` CG-12 already gates.
- **Classification**: control gap — greenfield, consistent with F-05-04's blocked readiness classification for C12.
- **Minimum remediation**: `statutory_rule` provenance schema (timestamps, source citation, approval-record linkage) carrying the §4 approval record; append-only rule history with pre-correction values DB-recoverable (`outputs/statutory-change-control-design.md` §5; schema item in `outputs/stage-08-handoff.md`).
- **Closure evidence**: committed schema plus tests proving an approved statutory change records approver, source citation, effective date, and recoverable prior values.
- **Confidence**: High
- **Required human decision**: DQ-007 (single-operator segregation-of-duties waiver) must resolve before the C12 build — non-blocking for the review, forwarded in `decision-queue.md`.
- **Downstream owner**: Stage 08 (schema and mechanism); gate CG-12.
- **Status**: confirmed
- **Date**: 2026-07-15
- **Raised by**: Stage 06, statutory-change control investigation (§1 of `CONTEXT.md`)

### F-06-05: The reconciliation scoping gap is a compliance control failure; the platform-wide auth absence is a control-environment failure
- **Affected capability(ies)**: C8 (directly), C1 (framing), every workspace-scoped surface
- **Current implementation**: consumed from Stage 05 without re-verification, per stage context — F-05-03 (unscoped data path; three routes accept and discard `workspace_id`) and F-05-01 (no authentication; `workspace_id` caller-supplied everywhere).
- **Intended design**: a payroll bureau owes each client company data isolation as a baseline professional/confidentiality obligation (business-context fact: multi-client bureau model; see `outputs/tenant-isolation-control-assessment.md` §1); the routes' own signatures assert workspace scoping.
- **Identified gap**: this stage's contribution is classification, not new technical fact: (a) F-05-03 is a **control failure with false attestation** — the API surface asserts an isolation control that does not exist, which defeats review as well as isolation; (b) F-05-01 is a **control-environment failure** — every isolation control on the platform currently lacks an enforcement layer beneath it. F-05-11's two internal functions remain control *weaknesses* (fix-before-wrapping), not failures — deliberately not upgraded.
- **Evidence**: F-05-03/F-05-01 (confirmed Stage 05 findings); `outputs/tenant-isolation-control-assessment.md` (classification reasoning); corroboration noted there from `docs/audit-program/09-security-tenant-isolation/findings.md` (09-000/09-002/09-004)
- **Consequence**: a falsely-attesting isolation control on bureau-client data defeats both isolation and review — it could pass a superficial audit — and for a multi-client bureau the isolation obligation is professional/confidentiality baseline, not merely a technical property; auth remediation must therefore carry compliance urgency, not just security urgency.
- **Severity**: High — severity here rates the classification's consequence for control posture (a falsely-attesting control on bureau-client data); the underlying technical severity remains with F-05-03 (Critical) and is not re-rated or duplicated by this finding.
- **Classification**: this finding *is* the classification — F-05-03: control failure with false attestation; F-05-01: control-environment failure; F-05-11's two internal functions: control weakness (fix-before-wrapping), deliberately not upgraded (E-06-5).
- **Minimum remediation**: as F-05-03's technical fix (workspace_id column + backfill, repo/service enforcement, the three decorative routes fixed), plus the control-evidence set in `outputs/tenant-isolation-control-assessment.md` §3 — remediating the code without producing the control evidence does not close the compliance item.
- **Closure evidence**: `outputs/tenant-isolation-control-assessment.md` §3 — invariant-named regression tests proving cross-workspace access is rejected, per-route negative-path checks, and a documented isolation control statement.
- **Confidence**: High
- **Required human decision**: none.
- **Downstream owner**: Stage 07 (auth-as-compliance-remediation framing, per `outputs/stage-07-handoff.md`), Stage 13 (prioritisation weight); gates CG-1 and CG-8.
- **Status**: confirmed
- **Date**: 2026-07-15
- **Raised by**: Stage 06, tenant-isolation control assessment (§6 of `CONTEXT.md`)

---

## Parked / Rejected

_None._

## Next action

**None — stage closed 2026-07-17 on critic PASS** (one REVISE cycle: RC-1/RC-2 corrections applied here and verified by the re-critic addendum in `outputs/critic-review.md`). F-06-01–05 are safe to cite from later stages.
