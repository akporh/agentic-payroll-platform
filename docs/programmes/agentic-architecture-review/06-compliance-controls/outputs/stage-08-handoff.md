# Stage 06 → Stage 08 Handoff (Technical Architecture)

## What Stage 06 fixed at requirements level (design within these; do not reopen)

1. **C12 control workflow** — `outputs/statutory-change-control-design.md`: proposer/validator/approver with segregation; mandatory evidence set (source citation, effective date, deterministic diff, impact preview, validation results); approval-record content (§4); append-only rule history with corrections as a first-class change type whose pre-correction values stay DB-recoverable; one workflow regardless of C11-vs-human source.
2. **Audit expansion** — `outputs/audit-expansion-requirements.md`: four domains (domain-config change, statutory approval, exception-resolution, agent/tool) + four integrity properties (attributable, reliably written, immutable, retained). The mechanism must stop hardcoding `PAYROLL_RUN` (`audit_events.py:34,60`) — generalise or parallel-build, your choice.
3. **Agent/tool audit standard** — `outputs/agent-tool-audit-standard.md`: mandatory fields (§3) and the retention resolution (tool-call records = 7-year, same as `agent_session_log`; operational telemetry may be short-lived).
4. **C11 proposal schema obligations** — `outputs/compliance-monitoring-source-policy.md` §2: provenance fields are structured and mandatory; Tier-1-only operative claims enforced in code; source snapshot/hash; monitoring-stall alerting.

## Mechanism questions now owned by Stage 08

- **DQ-004** (dry-run production-state separation) and **DQ-002/DQ-003** — unchanged, already forwarded by earlier stages.
- **C12 correction mechanics**: supersede-in-place vs same-date replacement row for a faulty rule — free choice within the recoverability + attribution requirements (§5 of the control design).
- **Impact-preview computation placement** (Stage 04's boundary question, control requirement now fixed): the approver-facing preview is computed deterministically C12-side against live state at review time; whether C11's advisory summary reuses the same computation is a design freedom. (`statutory-change-control-design.md` §7.)
- **Audit write reliability**: the architecture document's own outbox direction satisfies the "reliably written" property — extend it to audit records, not just notification events (F-06-02).
- **Immutability enforcement**: DB trigger vs role permissions for append-only audit tables (F-06-03) — pattern precedent exists (`3da637afb11b` protects `payroll_result` for PAID runs).
- **Retention enforcement**: build nothing that deletes at 7 years until DQ-008 (legal retention parameters, min and max) resolves; "keep at least" is the working posture.
- **`statutory_rule` provenance schema**: the table currently has no timestamps, source-citation, or approval linkage (F-06-04; model at `backend/infra/db/models/statutory_rule.py:7-23`) — the C12 build must add whatever schema carries §4's approval record and its rule-row linkage.

## Constraints worth restating

- No LLM anywhere in C12's critical path (D-02-04; the capability matrix already says this).
- Validator checks (duplicate/conflict, `rules_jsonb` shape) run pre-approval so the approver never sees a proposal that would fail the DB constraint (F-05-04: today the UNIQUE constraint is the *only* protection, with no pre-emptive validation).
- Date-driven rule resolution only — no "current rule" shortcuts (the platform's `payroll_rule.is_active` lesson, generalised to statutory data).
- Every gate in `outputs/control-gate-register.md` is a launch gate, not a documentation warning; weakening one requires a recorded human decision.
