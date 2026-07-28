# Stage 10 Output: Residual-Risk Register (Q8)

Consolidates the accepted residual risks into one register with owners and review triggers, and performs the DEC-07-04 review this stage owes. Register semantics (DEC-10-15): **RR- rows are accepted residuals** — risks a recorded conclusion/decision has accepted, with named re-review triggers. **Pending risk decisions are pointers** to `decision-queue.md` — they are *not* residuals yet and nothing here pre-empts them (POLICY: the executor may not resolve a material risk choice).

## 1. Accepted residuals

| ID | Residual | Accepted by / where | Owner | Re-review triggers | Standing mitigations / forward hooks |
|---|---|---|---|---|---|
| RR-1 | **Audit-tamper by DB superuser / infrastructure provider** — in-DB controls (append-only triggers, outbox) do not bind a superuser; external anchoring (WORM, hash anchoring) judged disproportionate for a single-bureau managed-Postgres deployment | DEC-07-04 (`audit-integrity-threat-model.md` §5); **reviewed and reaffirmed this stage — §3 below (DEC-10-16)** | Platform operator | (a) any client or regulator demands stronger tamper-evidence; (b) deployment moves off managed Postgres or adds DB principals; (c) multi-tenant SaaS commercialisation is proposed (Stage 11/12 must check this trigger explicitly); (d) any suspected-tamper incident; (e) Stage 13 visibility touchpoint (already flagged in `decision-queue.md`) | DB-clock insertion timestamps (not app-supplied); record shapes must not preclude later hash-chaining — both hooks must be preserved by migration reviews (Class D check, `standing-assurance-controls.md` §5) |
| RR-2 | **Append-only floor is trigger-only** — no DB role separation backs the triggers; a privileged connection could drop them | Stage 08 (`stage-10-handoff.md` item 5: "role separation deferred") | Platform operator | Any new DB principal or infra change (Class D role review); RR-1's triggers apply (same threat family) | Trigger-presence is exercisable in CI (the ET-1 rejection tests fail if triggers are absent from the migrated schema) |
| RR-3 | **No cryptographic signing of approval records** — non-repudiation rests on append-only storage + verified identity + auth-context reference + step-up linkage | Stage 07 (`approval-security-design.md` §2) | Platform operator | An approval dispute incident; external counterparty demand; RR-1 escalation (the two strengthen together) | Record shape must not preclude adding signatures later (checked with RR-1's hook) |
| RR-4 | **Pre-epoch audit records are permanently unverified-identity** — historical rows cannot be re-attributed | Stage 07 (`audit-integrity-threat-model.md` §6 — confirmed correct; rewriting history would itself violate append-only) | Platform operator | None scheduled (the residual is permanent and shrinking in relative weight); revisit only if a regulator/client questions historical attribution | Epoch as data (`platform_metadata`); labelling enforced at mechanism (ET-1 test), surface (UX behaviour 23), and report (`evidence-chain-and-baselines.md` A§3) layers |
| RR-5 | **Dry-run artifacts and audit evidence retained under an unconfirmed legal basis** — 7-year floor is a working assumption pending professional confirmation | Stage 06 working posture ("keep at least 7y" floor while DQ-008 is open) — the *floor* is the accepted interim; the *final basis* is the pending decision | Platform operator | DQ-008 resolution (the register row converts to a closed note or a revised retention design at that point) | No purge/retention-enforcing mechanism may be built meanwhile (DQ-008 mechanism constraint, honoured by Stage 08 design-absence checks) |

## 2. Pending risk decisions (pointers — not accepted residuals)

| Queue item | Risk content | Where it resolves |
|---|---|---|
| DQ-007 (amended Stage 07) | Single-operator segregation-of-duties waiver for C12 + whether MFA enrollment becomes a hard C12 launch gate — two risk-appetite calls on the same approval action, decided together | Human reviewer, pre-C12 build (surfaces at Stage 13) |
| DQ-007's step-up floor | Password-only step-up is the accepted *floor* only until the MFA question is decided — not registered as a standalone residual to avoid pre-empting the joint decision | With DQ-007 |
| DQ-008 | Legal retention basis (statutory minimum, data-protection maximum) | Human reviewer + professional advice |
| DQ-006 | Tier-1 source-allowlist legal sufficiency (C11) — a compliance-risk decision, listed for completeness though its register home is CG-11 | Human reviewer + professional advice, pre-C11 build |

## 3. DEC-07-04 review (the review this stage owes)

**Disposition: reaffirmed (DEC-10-16)** — an executor conclusion within the inherited risk framing, same authority level as the original DEC-07-04; not a new risk acceptance and not a human decision, because no changed fact requires one.

Checked against the acceptance's own stated basis:

1. **Deployment shape unchanged**: single bureau, managed Postgres, single operator — nothing in Stages 08–09's designs or findings changes it. The exposure window is unchanged.
2. **No new obligation surfaced**: no client, regulator, or standard demanding external anchoring appears anywhere in Stages 06–09's evidence; DQ-008 (retention basis) is adjacent but does not bear on tamper-evidence strength.
3. **Forward hooks are preserved in the Stage 08 designs**: DB-clock timestamps are required by the R4 record standard (`approval-security-design.md` §2 item 3) and the append-only design carries no shape that precludes hash-chaining (`event-audit-foundation-design.md` §5) — the acceptance's two escape hatches remain real, not aspirational.
4. **Proportionality holds**: external anchoring's cost/complexity is unchanged, and the platform's assurance investment is currently better spent on the controls that bind the *likely* threat actors (application-layer paths — which the append-only + outbox + route/tool tests do bind) than on the superuser threat that anchoring addresses.

**Boundary of this reaffirmation**: it holds for the current deployment shape only. Trigger (c) is armed deliberately — if Stage 11/12 propose multi-tenant SaaS commercialisation, other bureaus' data sits under one superuser and this reaffirmation does **not** carry over; RR-1 must then be re-reviewed as a human decision (risk acceptance on behalf of third parties is not an executor call). The Stage 13 visibility item in `decision-queue.md` stands unchanged — the human reviewer sees RR-1 at the roadmap touchpoint regardless.

## 4. Review mechanism

- **Owner**: platform operator (single-operator reality — one owner for all rows; the register itself is the shared memory).
- **Scheduled review**: at Stage 13 roadmap approval (human touchpoint — RR-1 explicitly); annually thereafter; and on any row's trigger firing.
- **Register discipline**: rows are added when a residual is *accepted by a recorded conclusion/decision* — never as a place to quietly park unresolved risk choices (those live in `decision-queue.md` until decided). Removing or materially weakening a row requires a recorded human decision (the gate registers' rule, applied here).
- Maintenance transfers with the other registers at Phase 3 adoption (`launch-gate-evidence-register.md` §5).
