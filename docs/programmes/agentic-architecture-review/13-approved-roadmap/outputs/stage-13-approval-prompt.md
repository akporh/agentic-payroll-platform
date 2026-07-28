# Stage 13 Approval — Approved Roadmap (Final Phase 1 Gate)

**This is the one document you respond to.** It is self-contained — you do not need to open any other file to make these decisions. Deeper backing lives in `proposed-roadmap.md`, `final-decision-pack.md`, and `baseline-and-near-term-plan.md`, but everything you need to decide is below.

This is the **final gate of Phase 1** of the Agentic Architecture Review Programme. Approving it settles **what to build, in what order, and what "done" means** — and **nothing about when building starts**, which is a separate later gate. It also records approval of the target direction and retires the old architecture document as the target description.

---

## 1. What you are approving (the direction, in one paragraph)

A **Nigerian payroll platform with an assistant — never a chat product**: a fully deterministic payroll engine (calculation, statutory execution, state, locking, approval, every financial mutation — DB-enforced, no AI), surrounded by a small, gated set of **five AI capabilities that interpret, narrate, and propose but never compute, decide, or mutate** (C3 current-state assistant, C5 trace narration, C7 optional narration, C11 compliance drafting, C13 onboarding mapping). Everything else is deterministic platform capability. The differentiator is **"AI you can audit"** — visible in the queue, approval, and evidence surfaces, backed by standing artifacts (isolation tests, tool-call audit chain, calibration reports) a client's auditor can check. Built to **single-bureau depth first (Sandy), on a substrate that keeps the SaaS option open for a human decision — never a drift.**

---

## 2. The roadmap (order is fixed by dependencies; timing/capacity is yours to set later)

Sequenced strictly by the value-priority order, which equals the readiness order — no trade-off:
**C1 → C2 → C12 & C14 → C6/C3/C5 → C7 shadow → C11 → C13.** Every ordering (O1–O9) and calendar window (W1–W6) is honoured with **zero departures**, so no sequencing choice is asked of you.

| Tranche | Build items | What lands | Pre-build gate |
|---|---|---|---|
| **0 — Near-term** (no build authorisation) | Capture B3/B5 baselines now; ask EG-004; initiate DQ-006/008 engagement; package DQ-007 here; flag FULL_RUN removal | The cheapest de-risking actions; see §4 | — |
| **1 — Deterministic foundations** | **C1** Identity & Auth (+ frontend test harness; + route-table isolation harness + decorative-route/reconciliation-scoping fixes) → **C2** Event/Tool/Notification (+ exception-resolution workflow substrate + audited tool layer + no-purge floor) | Verified identity + workspace isolation on every request; the reliable event/notification/exception substrate and audited tool layer everything rides on | — |
| **2 — Deterministic differentiators** | **C12** Statutory-Rule Change Management (+ the first platform-level frontend area) · **C14** Deterministic Import Validation & Dry-Run | Statutory changes applied through recorded human approval, no dev migration; dry-run evidence before any onboarding commit — the two strongest deterministic differentiators | **DQ-007 (+ MFA)** — decided in this pack (§3, DP-1) |
| **3 — Readiness & assistance** | **C6** Readiness Service (+ CI schedule seam) · **C3** Operator Assistant (+ LLM eval infrastructure) · **C5** Trace Explanation | Proactive readiness checks; the current-state chat assistant; plain-English narration of a computed trace — all evidence-linked | — |
| **4 — Input anomaly detection** | **C7** Input Anomaly Detection (shadow → GA) | Data-entry errors flagged pre-run; **GA only after ≥ 3 payroll cycles + ≥ 20 terminal records in shadow** — slow-burn by design | — |
| **5 — Compliance monitoring** | **C11** Compliance Monitoring (narrowed: detect/compare/summarise/draft, feeds C12) | Time-to-detection of statutory changes shrinks to the monitored cadence | **DQ-006** — professional engagement must conclude first |
| **6 — Onboarding mapping** | **C13** Onboarding Mapping Assistant | Messy-spreadsheet onboarding accelerated; proposals only, applied via the deterministic path with C14's dry-run as backstop | **B1/B2 baselines must be captured on a real onboarding *before* C13 ships (unrecoverable)** |

**Definition of "done" for every item** = the launch-gate evidence register's rows are green (committed CI tests, eval reports, config inspections, or dated baseline artifacts). "Done = row green" — not asserted.

**Deliberately not built:** C4 (historical explanation — blocked), C8 (reconciliation investigation — blocked; its repo-level fixes ride Tranche 1), C9 (trace agent — rejected permanently), C15 (email — deferred), and multi-tenant SaaS (needs the decision bundle in §3, DP-3).

---

## 3. The decisions in front of you

Nine items. Some are genuine choices; some are visibility items needing only your acknowledgement; two are facts only you can supply. **Nothing below has been decided for you.**

### DP-1 — DQ-007: single-operator approval + MFA  *(genuine decision — gates Tranche 2)*

This is the **earliest gate any build hits**. Two parts, decided together:

**Part A — who can approve a statutory change?**
- **A1 — Waive proposer ≠ approver** (one operator proposes *and* approves, with compensating controls: cooling-off delay + second-channel notification). → C12 builds as a single-operator workflow. Faster; the segregation risk is accepted and recorded.
- **A2 — Hold proposer ≠ approver** (a second person must approve). → **Multi-operator capability is promoted to a C12 prerequisite** — Tranche 2 grows to include multi-operator roles/UX before C12 can launch. Slower; stronger control.

**Part B — is MFA a hard launch gate for C12?**
- **B1 — Yes, MFA required** for approval-capable operators before C12 launches. Stronger; adds an MFA enrolment item to C12.
- **B2 — No, password-only step-up is the floor** (the current accepted floor); MFA can be added later.

> **Your call:** A1 or A2? · B1 or B2? (Recommendation withheld — this is a risk-appetite call only you can make.)

### DP-2 — Source-document disposition  *(genuine decision — resolves the old architecture doc's status)*

The old `agent-layer-architecture.html` (five-track / three-phase, marked "NEEDS REVISION") is recommended to be **superseded and replaced** by the approved direction outputs, preserving its still-valid security invariants and design constraints. On approval, a **Phase 3 work item** rewrites both HTML copies from the direction outputs — not done now.
> **Your call:** Approve the supersede-and-replace disposition, or amend it?
> *(Note: the locked Technology Decisions table — LLM choices, AI Gateway, APScheduler — carries forward unchanged, subject to normal re-validation at build time. Not a proposal to change them.)*

### DP-3 — SaaS fork  *(genuine decision only if you take it up)*

The roadmap's default is **single-bureau excellence with a SaaS-ready posture**. No roadmap item exists *because of* SaaS ambition.
- **Carry the default** → roadmap as proposed stands.
- **Take up active multi-tenant SaaS** → the decision bundle goes on the **critical path first**: (a) the product/market decision (with **zero demand evidence** today, DP-8); (b) **RR-1 re-opened** as a risk decision (hosting other bureaus' data under one DB superuser); (c) scope of multi-operator/tenant-management/billing.
> **Your call:** Carry the single-bureau default, or open the SaaS bundle?

### DP-4 — DQ-006 + DQ-008 professional engagement  *(action to authorise — not resolved here)*

Bundle both into **one Nigerian tax/legal engagement**, initiated at/after approval (lead time is the risk):
- **DQ-006** — which sources are *legally sufficient* for statutory monitoring; must conclude before any C11 sprint.
- **DQ-008** — the legal retention basis (the "7-year" figure is uncited); blocks only retention-enforcement tooling. "Keep at least 7 years, no purge" holds meanwhile.
> **Your call:** Authorise initiating the bundled engagement now?

### DP-5 — RR-1 audit-tamper residual  *(visibility — acknowledge)*

In-DB audit controls don't bind a DB superuser; external anchoring was judged disproportionate for a single-bureau managed-Postgres deployment, and this was **reaffirmed** at Stage 10, bounded to the current shape. It re-opens only on a trigger (notably a SaaS move — DP-3).
> **Your call:** Acknowledge (no action), unless you are taking up SaaS.

### DP-6 — DEC-08-09 statutory UNIQUE widening  *(visibility — acknowledge)*

C12 will widen a database uniqueness constraint (`statutory_rule`) to support versioned corrections. Already decided at design level; it rides the repo's standing `/arch-council` gate inside the C12 build. Flagged so it's not a surprise.
> **Your call:** Acknowledge.

### DP-7 — EG-004: next-onboarding timing  *(fact only you can supply)*

Whether/when Sandy expects the next new payroll client. This is the single fact the **unrecoverable B1/B2 baseline window** hinges on — if the next onboarding happens after C13 ships, C13's improvement claims are permanently anchorless.
> **Your input:** Is a new client onboarding plausible in the next couple of quarters? (If yes, we arm the B1/B2 measurement protocol ahead of it, regardless of build order.)

### DP-8 — EG-005: commercial-demand evidence  *(fact only you can supply)*

No source anywhere records client demand for any capability or for SaaS. Everything is **claimable**, not **market-verified**. Not needed to approve the roadmap; needed before any external-facing claim or SaaS step.
> **Your input (optional now):** Any client-side demand signal to register? Otherwise language stays capability-led.

### DP-9 — The roadmap itself  *(genuine decision)*

> **Your call:** Approve `proposed-roadmap.md` as the sequenced build plan and definition-of-done set, or amend it?

---

## 4. Near-term actions (cheap, calendar-bound — placed so none is lost)

These need no build authorisation:

1. **Capture B3 (time-to-go-live) and B5 (statutory time-to-apply) retrospectives now** — near-zero cost; the first two "measured, not asserted" artifacts.
2. **Ask EG-004** (DP-7) and ready the B1/B2 protocol if an onboarding is coming.
3. **Pin B6 to C3 sprint-planning** (4-week support-question tally) and **B4 to C6 sprint-planning** (3-cycle detection observation) — easily forgotten because they start at planning, not ship.
4. **Initiate the DQ-006/DQ-008 engagement** (DP-4).
5. **FULL_RUN dead-option removal** — a trivial frontend fix flagged to the repo's standing maintenance workflow (outside this programme's authority).
6. **Optional:** browser-e2e automation for two scripted-manual UX behaviours — cheap to include with the Tranche 1 harness, safe to defer.

---

## 5. What approval does and does not authorise

**Approval DOES:** record the target direction as approved (resolves the old doc's open status); record the source-document supersede-and-replace disposition; approve the roadmap and its definitions of done; record DQ-007's resolution; authorise *initiating* the DQ-006/008 engagement; **close Phase 1**.

**Approval DOES NOT:** authorise starting **any** build; authorise **any** production-code/migration/config change (including the HTML rewrite and roadmap/product-doc adoption — those are Phase 3 acts under their own grant); pre-clear the remaining pre-build gates (DQ-006, DQ-008, the DEC-08-09 `/arch-council` review); adopt the SaaS trajectory unless you take it up; weaken any gate or claim beyond its evidence.

> **Phase 2/3 authorisation is a separate human gate, requested after this approval.**

---

## 6. Required updates on your decision

- Record the decisions in `13-approved-roadmap/decisions.md` and `_core/HUMAN-DECISIONS.md` (next `HD-` identifiers), including: roadmap approval, direction approval (D-02-01 resolution), source-document disposition, DQ-007 (+ MFA) resolution, and any of DP-3–DP-8 you act on.
- Mark the DQ items resolved/forwarded in `decision-queue.md` with the decision reference; move DQ-007 to resolved; note DQ-006/008 engagement initiated.
- Mark Stage 13 `closed` and **Phase 1 complete** in `review-state.md` and `state.md`.
- Do **not** modify production code, migrations, or any path outside this programme.
- Do **not** begin Phase 2.

---

## 7. Completion report to return

- Stage status (Stage 13 → closed; Phase 1 → complete)
- Decisions recorded (DP-1 A?/B?, DP-2, DP-3, and any of DP-4–DP-8)
- `_core/HUMAN-DECISIONS.md` HD identifiers created
- Roadmap approved / amended (and any amendments)
- Pre-build gates still open (DQ-006, DQ-008, DEC-08-09 review)
- Near-term actions authorised (baselines, engagement, EG-004 answer)
- Next gate (Phase 2 authorisation — separate request)

---

## Stage 13 status report

```
STAGE 13 — APPROVED ROADMAP  ·  status: awaiting-human-decision (post critic PASS)
Phase 1 (diagnostic + direction + roadmap): COMPLETE pending this approval

Executor pass ......... complete — 4 outputs produced
  · proposed-roadmap.md ............ Q1 (6 build tranches + Tranche 0) + Q2 (done = register row green)
  · final-decision-pack.md ......... Q3 (9 items DP-1..DP-9, classified) + Q5 (phase boundary)
  · baseline-and-near-term-plan.md . Q4 (B3/B5 now; B1/B2 window; B6/B4 pinned; FULL_RUN; browser-e2e)
  · stage-13-approval-prompt.md .... Q6 (this document — self-contained)

Constraint audit ...... O1–O9 + W1–W6 all honoured, ZERO departures
Value sequence ........ C1 → C2 → C12 & C14 → C6/C3/C5 → C7 shadow → C11 → C13
RR-1 trigger (c) ...... held — single-bureau, SaaS-ready; no item exists because of SaaS ambition
Findings (F-13-*) ..... none (roadmap assembly exposed no inconsistency between confirmed prior facts)
Executor decisions .... DEC-13-01..06 logged (no human decision made by the executor)
Decision pack ......... DP-1 DQ-007+MFA | DP-2 source-doc | DP-3 SaaS fork | DP-4 DQ-006+008
                        DP-5 RR-1 | DP-6 DEC-08-09 | DP-7 EG-004 | DP-8 EG-005 | DP-9 roadmap

Awaiting: human decision on DP-1..DP-9. On approval → Stage 13 closed, Phase 1 closed.
This stage NEVER closes automatically — approval is the human reviewer's act alone.
```
