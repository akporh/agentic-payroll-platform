# Stage 07 Output: Approval-Action Security Design (R4/R5)

Defines what makes an approval-class record non-repudiation-grade on this platform (R4) and resolves R5 — the step-up-auth vs live-session-check design choice for platform-blast-radius approvals — with recorded reasoning, per `06-compliance-controls/outputs/stage-07-handoff.md`. Approval-class actions: C12 statutory approvals, C10 confirmations, reconciliation resolutions (`attribution-identity-requirements.md` R4).

## 1. Approval classes by blast radius

| Class | Examples | Blast radius |
|---|---|---|
| **Platform-blast-radius** | C12 statutory-rule approval (every workspace's deductions change — `statutory-change-control-design.md` §1) | All clients simultaneously |
| **Workspace-blast-radius** | C10 pending-action confirmations; reconciliation resolutions; run approve/lock/pay | One client workspace |

R5 binds the first class. The second class requires an ordinary verified session (R1/R2) plus the R4 record — step-up everywhere would train the operator to reflexive re-entry and devalue the signal where it matters (C12 approvals are rare; run approvals are routine).

## 2. R4 — the non-repudiation-grade record (all approval classes)

Every approval/confirmation/rejection record must carry:

1. **Verified principal** — the authenticated approver (C1), never asserted identity.
2. **Auth-context reference** — the token/session identifier (T2, `identity-architecture-requirements.md` §3) and, for platform-blast-radius approvals, the step-up event reference (§3).
3. **Server-side decision timestamp** — DB clock, not client-supplied.
4. **The decision payload as presented** — content (or immutable reference + content hash) of exactly what the approver was shown at decision time: for C12, the proposal + validator results + impact preview per `statutory-change-control-design.md` §4; for C10, the exact record/field/new-value the confirmation UI displayed. "As presented" is the load-bearing phrase: a record of what was *stored* is not proof of what was *shown* if the presentation is computed at render time — the record must freeze the shown content.
5. **Outcome + linkage** — approved/rejected/expired; for applied changes, linkage to the rows actually written.
6. **Storage under the audit integrity properties** — append-only, outbox-coupled, retained (`audit-integrity-threat-model.md`); an approval record that can be silently rewritten proves nothing.

Cryptographic signing of approval records remains **not required** (consistent with Stage 06's R4 framing): the operator stands behind record integrity via append-only storage + verified identity + auth-context reference. The record shape must not preclude adding signatures later (same forward-hook principle as hash-chaining, threat model §5).

## 3. R5 — resolved: step-up re-authentication, not a live-session check alone

**Decision (DEC-07-03): a C12-class approval requires a fresh re-authentication at decision time — credential re-entry (password now; TOTP as second factor once available) producing a recorded step-up event whose ID is embedded in the approval record. A live-session/recency check alone is rejected as insufficient.**

Reasoning, recorded per the handoff's instruction:

1. **The threat R5 names is a hijacked idle session.** A live-session check ("has this session been active recently?") cannot distinguish the operator from an attacker *using* the hijacked session — activity is exactly what an attacker generates. Credential re-entry demands something the session itself does not contain. This is the decisive argument: the control requirement ("a hijacked idle session must not be sufficient to approve a statutory change silently") is not actually met by the live-session option, making this less open a choice than the handoff's phrasing allowed.
2. **Single-operator reality (DQ-007 context).** For a small bureau, the proposer≠approver segregation may be waived with compensating controls. If one human (or one compromised account) can both propose and approve, the step-up event is one of the few remaining independent controls on the highest-blast-radius action. Choosing the weaker R5 option while DQ-007 contemplates weakening segregation would stack two weakenings on the same action.
3. **Cost is negligible at C12's frequency.** Statutory changes are a few events per year; a 10-second credential re-entry adds no meaningful friction. The usual argument against step-up (operator fatigue) does not apply.
4. **Non-repudiation dividend (R4).** "Approver re-authenticated at 14:32:07, step-up event #…" materially strengthens the record against a disputing party versus "a session opened hours earlier was still valid."

Consequences:

- The C1 token/session model must support step-up events as first-class, recorded, referenceable objects (T5) — even though the *consumer* (C12) arrives later. Building C1 without the hook forces a session-model rework at C12 time.
- Step-up events are audited under T6 and append-only storage.
- Step-up freshness window: the step-up must occur within a short window before the approval commit (minutes, not hours — exact value is a Stage 08 parameter), and covers exactly one approval decision — no batch approvals under one step-up.
- If MFA (TOTP) is enrolled by C12 launch, step-up uses it; password-only step-up is the acceptable floor for a single-operator deployment where the second factor doesn't exist yet. MFA enrollment for approval-capable operators is **recommended before C12 launch** and noted in SG-12, but not made a hard gate here — hard-gating it is a risk-appetite call that belongs with DQ-007's resolution, and the two should be decided together (flagged in `decision-queue.md` as an amendment to DQ-007's decision context, not a new queue item).

## 4. Expiry and invalidation interactions (boundary with Stage 08)

C10's protocol questions (expiry, idempotency, conflicting pending actions, run-state invalidation — DQ-002) remain Stage 08's. This document adds only the security constraints on whatever Stage 08 designs: a confirmation submitted twice must not execute twice (idempotency is a security property here, not just correctness); an expired or invalidated pending action must produce an R4-grade record of the expiry/invalidation (silence is an audit gap); and a pending action's payload-as-presented must be frozen at proposal time so the operator never confirms content that changed after review.
