# Stage 12 Output: Target-Direction Statement (Q1)

One page: what the platform is becoming. Pure synthesis — every claim traces to a confirmed finding, binding decision, or recorded handoff fact (citations inline). Nothing here decides a human choice; the one genuine fork is stated in §4 with the executor-safe default and the human alternative cleanly separated.

## 1. What the platform is (product identity)

**A payroll platform with an assistant — never a chat product** (Principle 8, retained unchanged; Stage 11 positioning frame, `positioning-and-claims.md` §1).

Concretely: a **deterministic Nigerian payroll engine** — calculation, statutory execution, state transitions, locking, approval, and every financial mutation fully deterministic and DB-enforced (Stage 02 thesis, F-02-01; Principles 1/2/9) — surrounded by a **small, gated set of AI assistance capabilities** that interpret, narrate, and propose but never compute, decide, or mutate:

- five genuine AI capabilities at end-state: C3 (current-state assistant), C5 (trace narration), C7's optional narration layer, C11 (compliance detection/drafting, narrowed per D-02-04), C13 (onboarding mapping proposals) — exactly the five D-03-01 retained;
- everything else in the portfolio is deterministic platform capability (C1, C2, C6, C10, C12, C14, C15) — deliberately not "agents" (7 reclassifications, D-03-01);
- the differentiation is **visible in the queue, approval, and evidence surfaces** (Stage 09 IA; Stage 11 §1) — where "AI you can audit" is something a viewer can see — with the chat assistant as supporting cast.

The proof layer is part of the product: the launch-gate evidence register, route-table-generated isolation tests, tool-call audit chain, and calibration reports are standing artifacts a client's auditor can check (Stage 10 handoff §2 property 4; the four claimable properties, `positioning-and-claims.md` §2).

## 2. For whom

**Sandy's payroll bureau — a single-operator family bureau — and, through it, the bureau's payroll clients.** The operator gets efficiency and confidence (INT value: C3/C5/C6 support, readiness checks, mapping assistance); the bureau's clients experience service quality (CLI value: statutory changes applied correctly and recoverably, dry-run-evidenced onboarding, input errors caught pre-run) (`commercial-value-map.md` §1). Differentiation claims exist as *claimable and measurable once built* — no capability has registered demand evidence (F-11-02, EG-005), so direction language stays **capability-led** ("what we can credibly offer"), never demand-led, until Michael supplies client-side facts. "Provable" and "proven to sell" remain distinct claims.

## 3. Operated how

**Single-operator, capped-cadence reality is a design constraint, not a temporary limitation:**

- Standing assurance cadence is capped at ~one monthly + one quarterly scripted operator session (`standing-assurance-controls.md` §6, via Stage 10/11 handoffs) — this bounds how many live AI capabilities the bureau can operate concurrently, independent of build capacity.
- Single-operator v1 posture is load-bearing in the designed surfaces (notification read-state, exception ownership — Stage 09, `product-scope-boundaries.md` §2.1); multi-operator is a distinct later increment with named revisit triggers, and may be *promoted to prerequisite* by DQ-007's resolution — team-workflow statements stay conditional until that resolves.
- Trust-led, not speed-led: calibration governance makes C7-class detection slow-burn by design (shadow ≥ 3 cycles + ≥ 20 terminal records, DEC-10-08); the pace of claims — post-gate, post-baseline — is a feature of the trust story, not a delay (Stage 10 handoff §2 property 3; `positioning-and-claims.md` §4).

## 4. The deterministic/AI boundary the direction commits to

AI is used **only** where a task is genuinely not reducible to a deterministic rule (interpretation of natural-language questions, narration of computed facts, fuzzy header mapping, external regulatory-text interpretation) — and even there, always grounded in tool-returned facts, always evidence-linked, always behind the gates (Principles 2/4/9; D-02-02/03/04 embedded, not softened). Calculation, statutory execution, state, mutation, and compliance decisions remain deterministic **permanently** (Principle 1; Stage 02 boundary assessment). Write capability, if it ever arrives, passes through the structured confirmation protocol (C10) — never a natural-language "yes."

## 5. The fork — stated explicitly, not decided

**The direction this synthesis commits to, absent a human decision, is: single-bureau excellence with a SaaS-ready posture.**

- *Single-bureau excellence*: everything in §§1–4, sequenced for Sandy's bureau within the O1–O9/W1–W6 constraint set.
- *SaaS-ready posture*: the assurance substrate being built for the single bureau (SS-1 route-table-generated isolation tests, the four claimable properties, the evidence chain) is the right substrate for an eventual SaaS story — the work is not throwaway with respect to the documented ambition (`product-scope-boundaries.md` §2.2, an observation requiring no decision).

**The alternative — an active multi-tenant SaaS trajectory — is a human decision bundle, not a direction this stage may adopt** (F-11-01; RR-1 trigger (c) discipline per DEC-10-16/DEC-11-04): (a) the product/market decision itself, with zero demand evidence registered (EG-005); (b) RR-1 re-opened as a human risk decision — hosting other bureaus' data under one DB superuser voids the audit-tamper reaffirmation by that decision's own boundary clause; (c) the scope decision on everything the single-bureau posture makes cheap (multi-operator UX, tenant management, billing, isolation-assurance productisation). If Stage 13 is asked to serve the SaaS ambition, this bundle goes on the critical path first (Stage 11 → 13 handoff §5). This stage frames the fork; it does not resolve it.

## 6. The direction in one sentence

**Become the payroll bureau platform whose every AI action is auditable, whose every claim is backed by a standing artifact, and whose deterministic core never shares authority with a model — built to single-bureau depth first, on a substrate that keeps the SaaS option open for a human decision, never a drift.**
