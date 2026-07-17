# Stage 07: Security & Identity — Decisions

Stage-local log. Master log for human decisions: `_core/HUMAN-DECISIONS.md`. Entries below are executor conclusions recorded for auditability under D-003's continuous execution model — none required a human stop; classification reasoning is given per entry.

## Gate

- **Stage opened**: 2026-07-17 (context-ready on Stage 06 closure; executor pass same day)
- **Stage closed**: pending critic (D-003 automatic closure on PASS + no blocking decision)

## Decisions log

### DEC-07-01 — Track P reviewed as design-under-review; corrections recorded rather than re-derivation
Track P's P1–P6 stories are adopted as the C1 baseline with named corrections (membership model, service principals, token lifetime posture, auth-event audit, step-up hook) in `outputs/identity-architecture-requirements.md` §8. Classification: executor synthesis per the stage context ("the design under review — not as authority"); no human choice arises because no correction contradicts a prior human decision.

### DEC-07-02 — Operator↔workspace is a membership relation, not Track P's single `workspace_id` column
Reasoning in `outputs/identity-architecture-requirements.md` §2: the bureau's own operators administer many client workspaces; a one-workspace-per-account model fragments human identity across accounts and defeats R1's purpose. Classification: **executor conclusion from evidence and inherited principles**, not a human decision — the bureau deployment shape is an established business-context fact (Stage 06 tenant-isolation assessment §1) and no reasonable single-workspace reading exists. The single-active-workspace-per-token property (P6) is retained, so R2 enforcement is unchanged in shape.

### DEC-07-03 — R5 resolved: step-up re-authentication for platform-blast-radius (C12-class) approvals
Live-session-check-only rejected. Full reasoning recorded in `outputs/approval-security-design.md` §3 (hijacked-session threat is not met by activity recency; DQ-007 single-operator context; negligible cost at C12 frequency; R4 dividend). Classification: this **is** the design choice Stage 06 explicitly delegated to Stage 07 ("step-up auth vs live-session check is this stage's design choice to make" — stage context, R5) — making it here is the assignment, not an absorbed human decision. One consequence flagged into the queue: whether MFA enrollment becomes a *hard* C12 gate is left to be decided together with DQ-007 (see decision-queue amendment) since both are risk-appetite calls on the same approval action.

### DEC-07-04 — Audit-store residual risk accepted at requirements level (DB-superuser tampering; no cryptographic signing; no external anchoring)
Recorded in `outputs/audit-integrity-threat-model.md` §5 and `outputs/approval-security-design.md` §2, with cheap forward hooks (DB-clock timestamps; record shapes that do not preclude hash-chaining/signatures). Classification: executor conclusion **within inherited risk framing** — Stage 06's R4 already fixed "no cryptographic signing required at requirements level"; extending the same proportionality logic to superuser-tampering residual is consistent application, not a new risk acceptance. Flagged for visibility: if the human reviewer wants stronger tamper-evidence as a product stance, that reversal belongs at Stage 10/13 review of the named sections.

### DEC-07-05 — Finding severity calibration for F-07-01 (Medium) and F-07-02 (Low)
F-07-01 rates below F-05-03 (Critical) deliberately: same pattern, materially lower data sensitivity (trace/ops metadata vs client payroll financials). F-07-02 rates Low on present impact (legacy internal page, name+headcount) with the wrap-risk already carried by F-05-11 — avoiding double-rating the same risk, mirroring Stage 06's practice of not re-rating consumed findings. Classification: severity judgment call logged per `_core/SEVERITY-MODEL.md`.

## Next action

**Stage 07 marked `awaiting-critic` — run the independent critic per `CRITIC.md`.**
