# Stage 11 Output: Product Scope Boundaries as Commercial Decisions (Q3 + Q4)

Classifies each product scope boundary as **in-scope-now** / **later-increment** / **requires-human-decision**, and records the DQ-005 joint disposition. Human decisions are classified and forwarded with options — none is decided here (POLICY).

## 1. DQ-005 joint disposition: `run_type = CORRECTION` UI exposure

**Disposition: Stage 11 CONCURS with Stage 09's recommendation (DEC-11-02). DQ-005 closes as an agreed implementation-specification.**

Stage 09's recommendation (its `stage-11-handoff.md` §1): no generic Run-Payroll-dropdown exposure; introduce CORRECTION as a **context-launched "Create correction run" CTA with/after the C12 build**, pre-filling period/type and carrying linkage to what it corrects.

Stage 11's half of the joint test was whether any *commercial* need exists for standalone correction runs earlier than C12. Checked against this stage's evidence base:

- No registered source or logged human statement records a client or operator demand for UI-initiated correction runs (F-11-02's general absence applies; nothing capability-specific either).
- The bureau operates single-operator on its own platform — the operator retains the API path for genuine pre-C12 correction needs; the current state is a usability gap (Stage 05's classification), not a service gap a client can see.
- The commercial value of corrections lands *through* C12's story ("recoverable, recorded statutory corrections") — exposing CORRECTION contextlessly earlier would weaken exactly the guardrail posture the platform intends to sell (Stage 09's "the cheap option is the wrong one," commercially endorsed here).

Since both co-owners now agree and no product/risk choice remains, the queue item converts to an implementation specification bound to the C12 build (per this stage's CONTEXT authority: concurrence "turns it into an agreed implementation-specification rather than a choice"). If a client-driven need for earlier standalone correction runs *ever* materialises, that is a new scope question with Stage 09's reasoning attached — not a silent re-open.

`decision-queue.md` updated accordingly.

## 2. Boundary classifications

### 2.1 Multi-operator workspaces — **later-increment**

Stage 09 established this is a distinct product increment, not an account-settings toggle: notification read-state (single-row `read_at`, broadcast rows) and exception ownership (assign-to-me against a membership list of one) are both load-bearing single-operator designs; crossing the boundary needs per-operator read state and real assignment/escalation flows, plus the in-app escalation recipient model deferred in v1.

Commercial assessment: no registered evidence of a second operator existing or being planned (F-11-02); the deployment reality is a single-operator family bureau. There is no current commercial forcing function, and the v1 posture is internally consistent. **Revisit triggers** (any one): Sandy adds payroll staff; a multi-tenant move is proposed (which independently re-opens bigger questions, §2.2); the DQ-007 resolution lands on an option that requires a second approver (that specific outcome would make multi-operator a *prerequisite*, not an increment — noted in `pre-build-decision-logistics.md` §2).

### 2.2 Multi-tenant SaaS commercialisation — **requires-human-decision** (not proposed by this stage)

**This stage explicitly does not propose multi-tenant SaaS commercialisation. RR-1 trigger (c) therefore does not fire, and DEC-07-04/DEC-10-16's bounded reaffirmation stands unchanged (DEC-11-04).**

The classification, for Stage 12/13:

- **Documented intent exists but is unscoped**: FEAT-021 remains a stub ("Acceptance criteria: TBD", Status FUTURE — re-verified live 2026-07-18, F-11-01), and `Clients/Sandy/CLAUDE.md` records "Phase 2 (future): Agentic SaaS payroll platform… Broader market" as business intent. Intent is documented; scope, demand evidence, and a risk decision are all absent.
- **It is a bundle of at least three human decisions, not one**: (a) the product/market decision itself (no demand evidence registered — EG-005); (b) **RR-1 re-opened as a human risk decision** — hosting other bureaus' data under one DB superuser voids the audit-tamper reaffirmation by that decision's own boundary clause (risk acceptance on behalf of third parties is not an executor call); (c) a scope decision on everything the single-bureau posture currently makes cheap (multi-operator UX per §2.1, tenant management, billing, isolation-assurance productisation).
- **What can be said now without deciding**: the platform's assurance posture (SS-1 route-table-generated isolation tests, the four claimable properties) is *the right substrate* for an eventual SaaS story — the work being sequenced for the single bureau is not throwaway with respect to the ambition. That observation requires no decision and no overclaim.

**Forwarded**: to Stage 12 (target direction must state whether the direction is "single-bureau excellence, SaaS-ready posture" or "active SaaS trajectory" — the former is executor-safe, the latter needs the human decision bundle) and to Stage 13 (if any roadmap item exists *because of* SaaS ambition, the decision bundle goes on the critical path first).

### 2.3 C15 email notifications — **later-increment** (reconfirmed, not re-opened)

Deferred by the source document's own sequencing (after C2 proven in production), reconfirmed by Stage 04 and deliberately excluded from Stage 09's notification design (escalation-on-evidence posture). No new fact changes it; no commercial claim in `positioning-and-claims.md` depends on it. It becomes commercially interesting only if bureau-client-facing notifications (not operator-facing) enter scope — which would be a new boundary question, not this one.

### 2.4 Operational reporting / client-profitability insight (opportunity area 15, F-04-06) — **later-increment**, with the prerequisite named

Stage 04 explicitly passed this to Stage 11 as a business-strategy call. Assessment: plausible INT + CLI value (a bureau that can show clients per-run evidence and cost/error trends has a service-quality story), but (a) its hard platform prerequisite — the audit-coverage fix (F-01-40 family) — is itself still open; (b) no demand evidence exists (EG-005); (c) the closed-exception history that C2/C7 produce is the natural substrate, and it does not exist yet. Classification: **later-increment**, to be re-assessed *after* the exception workflow and audit-coverage remediations are live, when its substrate is real and its cost is a reporting layer rather than a data-foundation project. Not a human decision today because no evidence supports choosing it over the already-sequenced work.

### 2.5 In-scope-now (for completeness)

The boundaries already inside the approved portfolio and its conditions: the 15-capability set with D-03-01 dispositions, single-operator v1, current-state-only assistant boundary (D-02-03), no-write AI (C10 deferred until a consumer exists). These are restated as *the* current scope, not re-decided.

## 3. Summary table

| Boundary | Classification | Owner of next move |
|---|---|---|
| DQ-005 CORRECTION UI exposure | **Closed** — implementation-specification bound to C12 build (joint concurrence) | Phase 3 C12 build item |
| Multi-operator workspaces | Later-increment; named revisit triggers | Trigger-driven; DQ-007 outcome may promote it |
| Multi-tenant SaaS | Requires-human-decision (bundle: product + RR-1 risk + scope); **not proposed now — RR-1(c) not fired** | Human reviewer, via Stage 12/13 framing |
| C15 email | Later-increment (post-C2-proven), reconfirmed | Stage 13 sequencing only |
| Operational reporting / profitability insight | Later-increment; prerequisite = audit-coverage fix + exception substrate live | Re-assess post-C2/C7 |
