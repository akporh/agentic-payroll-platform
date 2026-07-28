# Stage 13 Output: Final Decision Pack (Q3 + Q5)

The consolidated set of human decisions, visibility items, and evidence-gap asks that the Stage 13 roadmap-approval touchpoint carries — **and precisely what Stage 13 approval does and does not authorise**. Every item from **both** stage-13 handoffs (`12-target-direction/outputs/stage-13-handoff.md` §3; `11-commercial-product-strategy/outputs/stage-13-handoff.md` §2 + `pre-build-decision-logistics.md`) appears here **exactly once**, classified per `CRITIC.md`'s taxonomy.

**The executor resolves none of these.** Options and consequences are presented; the choice is the human reviewer's, recorded in `_core/HUMAN-DECISIONS.md`. The readable one-page pack the reviewer responds to is `stage-13-approval-prompt.md` (Q6) — this file is the reasoned backing for it.

---

## Q3 — The decision pack

### Classification taxonomy (per `CRITIC.md`)

`blocking-human-decision` · `non-blocking-forwarded-decision` · `implementation-specification` · `evidence-gap` · `not-a-decision`

### Item index

| # | Item | Classification | What it gates |
|---|---|---|---|
| DP-1 | DQ-007 single-operator segregation waiver **+ MFA hard-gate** | blocking-human-decision | C12 build authorisation (Tranche 2) |
| DP-2 | Source-document disposition (approve/amend) — resolves D-02-01 | blocking-human-decision | The revision path for `agent-layer-architecture.html` (Phase 3 rewrite) |
| DP-3 | SaaS fork (F-11-01) — single-bureau default vs active multi-tenant trajectory | blocking-human-decision **only if SaaS is taken up**; otherwise default carries | Whether the F-11-01 bundle goes on the critical path first |
| DP-4 | DQ-006 + DQ-008 professional-advice engagement (bundled) | non-blocking-forwarded-decision (initiate now) | DQ-006 → C11 build (Tranche 5); DQ-008 → retention enforcement (never near-term) |
| DP-5 | RR-1 audit-tamper residual — visibility | not-a-decision (visibility) unless SaaS (→ DP-3) | Nothing near-term; re-opens only on a trigger |
| DP-6 | DEC-08-09 statutory UNIQUE widening — visibility | not-a-decision (visibility) | Rides C12's `/arch-council` review (Tranche 2) |
| DP-7 | EG-004 next-onboarding timing | evidence-gap (ask Michael) | The unrecoverable B1/B2 window (W2) / C13 claims |
| DP-8 | EG-005 commercial-demand evidence | evidence-gap (ask Michael) | External-facing claims and any SaaS step |
| DP-9 | Roadmap approval itself | blocking-human-decision | Phase 1 closure; the sequenced build proposal |

---

### DP-1 — DQ-007: single-operator segregation waiver + MFA hard-gate  *(blocking-human-decision)*

**The decision (two parts, decided together — Stage 07 amendment).**

*Part A — segregation of duties on C12 statutory approvals:*

| Option | What it means | Consequence |
|---|---|---|
| **A1 — Waive proposer ≠ approver** (accept single-operator approval with compensating controls) | One operator both proposes and approves a statutory change; compensating controls apply: cooling-off delay + second-channel notification (`statutory-change-control-design.md` §8) | C12 builds as a **single-operator** workflow — no multi-operator work needed. Compensating controls must be named in the C12 build story. Faster changes; the segregation risk is accepted and recorded |
| **A2 — Hold proposer ≠ approver** | Statutory changes require a second person to approve | **Multi-operator capability is promoted from a later-increment to a C12 *prerequisite*** (`product-scope-boundaries.md` §2.1) — a direction-level scope change: Tranche 2 grows to include multi-operator UX/roles/notification-routing before C12 can launch. Slower changes; stronger control |

*Part B — MFA as a hard C12 launch gate:*

| Option | What it means | Consequence |
|---|---|---|
| **B1 — MFA is a hard gate** | Approval-capable operators must enrol in MFA before C12 launches | Stronger approval security; adds an MFA enrolment/verification build item to C12's DoD |
| **B2 — Password-only step-up is the floor** | Step-up re-auth (DEC-07-03) stands; MFA not required at launch | The accepted floor (DEC-07-03); MFA can be ratcheted in later (registers only tighten) |

**Why this is the earliest gate.** DQ-007 has **zero external dependency** and gates C12 (Tranche 2 — the earliest deterministic differentiator). Resolving it at this touchpoint keeps it off every sprint's critical path (`pre-build-decision-logistics.md` §1). Password-only step-up is the *floor* until Part B is decided (RR-2 register note).

**The executor recommends nothing** — this is a risk-appetite call. The pack surfaces the A2 consequence explicitly because it changes Tranche 2's scope.

---

### DP-2 — Source-document disposition (resolves D-02-01)  *(blocking-human-decision)*

**The recommendation on the table** (`12-target-direction/outputs/source-document-disposition.md` §1, DEC-12-04): **supersede-and-replace, preserving what survived review.** The five-track/three-phase structure of `docs/architecture/agent-layer-architecture.html` (and its `frontend/public/` mirror) is retired as the target description; still-valid content (security invariants, confirmed design constraints, the As-Is diagnosis where confirmed) is carried into a revision whose substance is the four Stage 12 direction outputs.

| Option | Consequence |
|---|---|
| **Approve the disposition** | D-02-01/HD-2 resolves: the record states the document is superseded by the approved direction outputs. A **Phase 3 work item** rewrites/replaces both HTML copies from the direction outputs (a Phase 3 act — not done at approval, DEC-12-04). Until then the file keeps its "NEEDS REVISION" pill and remains stated intent only |
| **Amend the disposition** | The reviewer specifies what to carry forward differently; the revision path adjusts accordingly |

**Carried-forward-without-re-deciding (flagged, not endorsed):** the Technology Decisions table (primary/fallback LLMs, Vercel AI Gateway, APScheduler, ephemeral-session + audit-log history, narrow tool granularity) was locked by the repo's arch-council 2026-06-11 and was **not** re-litigated (DEC-12-05); it carries as standing intent **subject to normal re-validation at Phase 3 build time** (model availability/pricing/gateway posture are environment facts this programme did not verify). This is a currency flag, not a proposal to change them.

---

### DP-3 — SaaS fork (F-11-01)  *(blocking-human-decision only if taken up)*

**The direction's default** (which this synthesis commits to absent a human decision): **single-bureau excellence with a SaaS-ready posture** (`target-direction-statement.md` §5). The roadmap in `proposed-roadmap.md` is built on this default.

| Option | Consequence |
|---|---|
| **Carry the default** (single-bureau, SaaS-ready posture) | The roadmap as proposed stands. RR-1 stays a visibility item (DP-5). No change |
| **Take up the active multi-tenant SaaS trajectory** | The **F-11-01 decision bundle goes on the critical path first** (Stage 11→13 handoff §5): (a) the product/market decision itself — with **zero registered demand evidence** (EG-005, DP-8); (b) **RR-1 re-opened as a human risk decision** — hosting other bureaus' data under one DB superuser voids the audit-tamper reaffirmation by that decision's own boundary clause (RR-1 trigger (c)); (c) the scope decision on everything the single-bureau posture makes cheap (multi-operator UX, tenant management, billing, isolation-assurance productisation) |

**RR-1 trigger (c) discipline held:** no roadmap item exists *because of* SaaS ambition, so the executor does **not** place the bundle on the critical path. The fork is framed, not decided (DEC-11-04, DEC-12-01).

---

### DP-4 — DQ-006 + DQ-008 professional engagement (bundled)  *(non-blocking-forwarded-decision — initiate now)*

Both need the **same** Nigerian tax/legal domain and adviser profile — one engagement, not two (DEC-11-05). **Initiate at/immediately after approval** (Tranche 0, T0.3); external-adviser lead time is the risk, not cost.

| Sub-item | The question | Blocks | Becomes critical when |
|---|---|---|---|
| **DQ-006** | Which external sources (FIRS, PenCom, gazette…) are *legally sufficient* for statutory-change monitoring to meet the bureau's professional-duty obligations (`compliance-monitoring-source-policy.md` §4) | C11 register row (CG-11) — **build authorisation**, not design | C11 enters a sprint (Tranche 5) |
| **DQ-008** | The statutory minimum (FIRS/PenCom/labour) and any data-protection maximum for audit/evidence retention; the source doc's 7-year figure is uncited | Only building of purge/retention-enforcement mechanisms (SC-4) | Only if/when retention enforcement is proposed |

**Deliverables**: DQ-006 → a recorded decision naming the confirmed Tier-1 allowlist + the cadence it was confirmed against; DQ-008 → a recorded decision confirming minimum and maximum (RR-5 then converts to a closed note or revised retention design). "Keep at least 7 years, no purge" is the working floor meanwhile (Posture P-C; O9).

**Nothing here is resolved by the executor** — these are professional-input decisions. The pack asks only that the engagement be *initiated* now so the runway exists.

---

### DP-5 — RR-1 audit-tamper residual — visibility  *(not-a-decision, unless SaaS → DP-3)*

**Presented for visibility, not re-decision.** RR-1 (audit-tamper by DB superuser / infra provider; in-DB controls don't bind a superuser; external anchoring judged disproportionate for a single-bureau managed-Postgres deployment) was **reviewed and reaffirmed** at Stage 10 (DEC-10-16, `residual-risk-register.md` §3), explicitly **bounded to the current deployment shape**. Forward hooks (DB-clock timestamps; record shapes that don't preclude hash-chaining) are preserved. The reviewer sees it at this touchpoint regardless (RR-1 trigger (e)).

**It becomes a live decision only if:** a client/regulator demands stronger tamper-evidence; the deployment moves off managed Postgres or adds DB principals; **multi-tenant SaaS is proposed (DP-3 trigger (c))**; or a suspected-tamper incident occurs. Absent a trigger, no action.

---

### DP-6 — DEC-08-09 statutory UNIQUE widening — visibility  *(not-a-decision)*

**Already decided at design level; flagged for pre-build awareness.** C12's correction mechanics commit Phase 3 to a data-contract change: `statutory_rule` UNIQUE widens `(country_code, effective_from)` → `(country_code, effective_from, version)` (resolution stays total-ordered; the tie-break already exists in code, F-08-01). It **rides the repo's standing `/arch-council` gate inside the C12 build item** (Tranche 2, budgeted in C12's DoD). Not a new decision — a visibility item so the reviewer is not surprised by it at build time.

---

### DP-7 — EG-004 next-onboarding timing  *(evidence-gap — ask Michael)*

**The single scheduling fact the unrecoverable B1/B2 window (W2) hinges on:** whether/when Sandy expects the next new payroll client. Only Michael can supply it (evidence type 5 — never invented). K2's onboarding-comparison claims depend on it.

**The ask:** if an onboarding is plausible within the C13/C14 horizon, the B1/B2 observation protocol (one-page timing sheet + comparison sheet) must be **armed *before* it happens — regardless of build order** (Tranche 0, T0.2). If the next onboarding lands after C13 ships, C13's improvement claims are permanently anchorless (K2 then reports absolute values, labelled).

---

### DP-8 — EG-005 commercial-demand evidence  *(evidence-gap — ask Michael)*

**No registered source or logged human statement records client demand** for any capability or for SaaS commercialisation (F-11-02). Value-map "differentiation" rows mean *claimable*, not *market-verified*, until this closes.

**The ask (no action required to approve the roadmap):** EG-005 is **required before any external-facing claim or any SaaS step** (feeds DP-3). Direction language stays **capability-led** ("what we can credibly offer"), never demand-led, until Michael supplies type-5 statements or registered external sources. "Provable" and "proven to sell" remain distinct claims.

---

### DP-9 — Roadmap approval itself  *(blocking-human-decision)*

Approve (or amend) `proposed-roadmap.md` — the sequenced tranche structure, per-item scope, cost placements, definitions of done, and baseline threading — as the Phase 1 output. Approval closes Phase 1; it authorises no build (see Q5).

---

## Q5 — Phase boundary statement

**Precisely what Stage 13 approval does and does not authorise** (POLICY §Human approval required for; §Executor/controller may not; WORKFLOW §Human gating; CONTEXT §Objective).

### Approval **does** authorise / record

1. **The target direction** (`target-direction-statement.md`, posture, narrative, end-state map, KPIs) as the approved direction — resolving D-02-01/HD-2 (this is the sole stage authorised to record it).
2. **The source-document disposition** (DP-2) — the record that `agent-layer-architecture.html` is superseded by the direction outputs; the HTML rewrite is a **Phase 3 act**, not authorised here.
3. **The proposed roadmap** (`proposed-roadmap.md`) as the approved sequence and definition-of-done set for future build.
4. **DQ-007's resolution** (DP-1) as a recorded decision the C12 build story will consume — *resolving the decision*, not authorising the C12 build.
5. **Initiation of the DQ-006/DQ-008 professional engagement** (DP-4) — a non-build, lead-time action.
6. **Closure of Phase 1** of the Agentic Architecture Review Programme.

### Approval **does not** authorise

1. **Starting any build.** No Tranche 1–6 item, no remediation, no near-term build task is authorised. Phase 2/3 authorisation is a **separate human gate** after approval (POLICY §Autonomy mode: Phases 2–3 `phase-gated`; RUNBOOK §Human stop points).
2. **Any edit to production code, migrations, config, or data** — including the HTML rewrite, `docs/ROADMAP.md`, or `docs/product/` adoption (those are Phase 3 acts under their own grant; POLICY §Executor/controller may not).
3. **The remaining pre-build human gates.** DQ-006 (pre-C11), DQ-008 (pre-retention-enforcement), and the DEC-08-09 `/arch-council` review (pre-C12 data-contract change) **remain their own gates** — approval does not pre-clear them.
4. **The SaaS trajectory** (DP-3) unless the reviewer explicitly takes it up; the default single-bureau posture carries otherwise.
5. **Any weakening of a gate, register row, or posture constraint** — the ratchet rule stands (DEC-10-02); weakening requires its own recorded human decision.
6. **Any success claim** not yet backed by a green register row and (where required) a captured baseline (P-G; overclaim table).

### One-line boundary

> Stage 13 approval settles **what to build, in what order, and what "done" means** — and **nothing about when building starts or whether it is authorised**, which is a separate, later human gate.
