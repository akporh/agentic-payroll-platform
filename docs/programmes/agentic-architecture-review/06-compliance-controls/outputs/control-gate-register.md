# Stage 06 Output: Control-Gate Register

Compliance/control **launch gates** for each of the 15 approved capabilities (D-03-01). These are distinct from Stage 05's `capability-readiness-matrix.md` (technical readiness) and aligned with it — a capability launches only when both its technical gaps and the gates below are closed. Gates reference this stage's outputs rather than restating them.

Standing cross-portfolio controls (apply to every row, not repeated):

- **SC-1** — verified identity + token-derived workspace (`attribution-identity-requirements.md` R1/R2); no compliance-evidence feature ships in placeholder-identity mode (R6)
- **SC-2** — independent tool-layer workspace check on every tool, regardless of repository correctness (D-02-02; Stage 03 cross-cutting req. 1)
- **SC-3** — agent/tool audit standard (`agent-tool-audit-standard.md`) for every LLM-touching capability; audit integrity properties (`audit-expansion-requirements.md` §3) for every audit write
- **SC-4** — audit-record retention floor of 7 years for payroll-relevant evidence pending DQ-008

| Capability | Compliance/control launch gates (beyond SC-1..4) | Gate ID |
|---|---|---|
| C1 — Identity & Auth Foundation | Treated as remediation of an absent control environment (`tenant-isolation-control-assessment.md` §4), not a feature. Gate: 100% of routes authenticate; zero surfaces accept workspace identity from caller input; audit actor fields switch to verified principals with a documented cut-over epoch for pre-auth records. | CG-1 |
| C2 — Event/Tool/Notification Foundation | Audit writes gain the reliability property (outbox-coupled, not fire-and-forget) in the same build (`audit-expansion-requirements.md` §3.2); PII-sanitizer rule-set is versioned so tool logs can cite the version applied. | CG-2 |
| C3 — Operator Assistant (current-state) | Tool-call logging live per SC-3 before first operator use; refusal outcomes logged as first-class; current-state-only boundary (D-02-03) enforced and its refusals testable. | CG-3 |
| C4 — Historical Payroll Explanation | Blocked (D-02-03) — no launch gate defined beyond the block itself; define gates when unblocked. | CG-4 |
| C5 — Trace Explanation | Null-trace refusal implemented and logged; zero-hallucination eval evidence retained as launch evidence (numeric-value provenance check, per Stage 03); trace fields surfaced are logged for evidence-linking. | CG-5 |
| C6 — Payroll Readiness Service | Notifications written via C2's reliable path; no additional compliance gate (read-only detection, no LLM in critical path). | CG-6 |
| C7 — Input Anomaly Detection | Exception-resolution workflow exists first (D-04-01 hard gate — its records are compliance evidence and must be auditable per `audit-expansion-requirements.md` domain 3); threshold changes versioned/auditable (D-04-01); shadow-mode results retained as calibration evidence. | CG-7 |
| C8 — Reconciliation Investigation | Blocked (D-02-02 + D-02-03). Control-evidence closure list: `tenant-isolation-control-assessment.md` §3 (code fix + invariant-named regression tests + per-route negative-path checks + isolation control statement), plus reproducibility closure. | CG-8 |
| C9 — Trace Agent | Rejected (Stage 03) — no gates; must not be built as a standalone capability. | CG-9 |
| C10 — Structured Confirmation Protocol | Every proposal/confirmation/rejection/expiry is an audit record under SC-3's standard and retention (resolves the Stage 03 matrix's "Stage 06 to confirm requirements"); confirmations attributable per R4. | CG-10 |
| C11 — Compliance Monitoring | Source policy enforced in code (Tier-1-only operative claims, mandatory provenance fields — `compliance-monitoring-source-policy.md`); DQ-006 (legal source authority) resolved by human + professional advice **before build authorisation**; monitoring-stall alerting present; C12 exists or ships together (F-02-12 sequencing, reconfirmed by Stage 05). | CG-11 |
| C12 — Statutory-Rule Change Management | Full gate list in `statutory-change-control-design.md` §9: verified-identity approvals; generalized audit mechanism holding the §4 approval record; pre-emptive duplicate/conflict + `rules_jsonb` shape validation with graceful-rejection tests; impact preview at approval time; append-only/correction handling with recoverability tested; DQ-007 (segregation waiver) resolved. | CG-12 |
| C13 — Onboarding Mapping Assistant | C14 live first (binding condition, reconfirmed); every proposed mapping + operator correction logged per SC-3 (the correction stream is both audit evidence and the eval baseline); no direct writes (proposals only). | CG-13 |
| C14 — Deterministic Import Validation & Dry-Run | Dry-run results retained as pre-commit evidence linked to the commit action; commit action attributable (SC-1). No LLM gates (deterministic by design). | CG-14 |
| C15 — Email Notifications | Deferred. Pre-launch: no PII in subject lines/preview text (Stage 03's own hygiene note); email content carries no payroll figures beyond what the notification policy allows off-platform. | CG-15 |

## Register maintenance

Owned by this programme until Phase 3 adoption; Stage 13 consumes it when sequencing. A gate may only be weakened by a recorded human decision — gates must not be reduced to documentation warnings (stage constraint, restated as a standing rule).
