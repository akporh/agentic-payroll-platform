# Stage 10 (Evaluation & Assurance) — Independent Critic Review

*Independent critic pass per `CRITIC.md`, run 2026-07-18 as a separate agent session from the primary executor (D-003/D-004). Executor-pass commit under review: `97789f9`. Report reproduced verbatim below; controller disposition recorded at the end.*

---

### Verdict

**PASS** — no blocking human decision remains. Stage 10 may close and Stage 11 may open per RUNBOOK §8.

### Scope reviewed

CRITIC.md, POLICY.md, RUNBOOK.md, all four `_core/` standards; Stage 10 `CONTEXT.md`, `findings.md`, `decisions.md`, `evidence/10-ci-and-harness-excerpts.md`, and all 9 `outputs/` files. Verified against sources: the three stage-10 handoffs (07/08/09), both gate registers (CG-1..15/SC-1..4, SG-1..15/SS-1..4), `measurement-framework.md`, `anomaly-detection-outcome-policy.md`, `anomaly-detection-design.md`, `audit-integrity-threat-model.md` §5–6, `approval-security-design.md` §2–4, `decision-queue.md`. Independently re-ran the F-10-01/02/03 repo citations and inspected `git show --stat 97789f9`.

### Strengths

- **Determinism-first framing is correct and load-bearing.** `llm-evaluation-framework.md` §1 and `stage-12-handoff.md` §1 hold that most safety properties are code-enforced (ET-1) and evals cover only behavioural residue — and refuse to let an eval substitute for the deterministic floor, honouring the measurement-framework anti-collapse prohibition. Exactly what Stage 08's handoff (input 2) asked for.
- **The 25 UX behaviours are disposed one-for-one with faithful numbering.** Every behaviour 1–25 from `09-human-experience/outputs/stage-10-handoff.md` appears in `ux-verification-plan.md` §2 with its guarantee intact — none dropped, none reworded into a weaker/different guarantee. The two un-automatable-at-launch items (7's two-tab race, 22's full-surface sweep) are split honestly (safety half automated, presentation half scripted-manual).
- **No gate is weakened, waived, or re-scoped.** The evidence register covers SC-1..4, SS-1..4 and every CG/SG capability row; blocked/rejected/deferred capabilities (C4/C8/C9/C15) carry their classification as the evidence requirement rather than inventing launch evidence. It restates the ratchet rule (tighten free; weaken = recorded human decision), mirroring both gate registers.
- **The DEC-07-04 review carries exactly the right authority.** DEC-10-16 is a reaffirmation on unchanged facts (deployment shape, no new obligation, forward hooks preserved), verified against `audit-integrity-threat-model.md` §5. It is bounded to the current deployment shape and arms RR-1 trigger (c) so multi-tenant commercialisation re-opens it as a human decision. It does not pre-empt DQ-006/007/008, which stay as pointers in `residual-risk-register.md` §2, not residuals.
- **Findings are grounded in re-verified current state.** F-10-03 actively corrects the stale "306" figure rather than repeating it — the re-verification discipline `EVIDENCE-STANDARD.md` demands.

### Required corrections

**None.** I looked specifically for correctable gaps and found no factual contradiction with any source, no dropped behaviour or gate, no metric redefinition, and no out-of-authority decision. Not raising RCs for formatting, naming, or already-resolved questions.

### Decision classification (open items)

- **DQ-005** (CORRECTION UI exposure) — non-blocking-forwarded-decision (→ Stage 11). Not blocking Stage 10.
- **DQ-006** (Tier-1 source legal sufficiency) — blocking-human-decision, pre-C11 build (surfaces Stage 13). Not blocking Stage 10.
- **DQ-007** (segregation waiver + MFA hard-gate) — blocking-human-decision, pre-C12 build (surfaces Stage 13). Not blocking Stage 10.
- **DQ-008** (retention legal basis) — non-blocking-forwarded-decision. Not blocking Stage 10.
- **EG-001/002/003** (baseline gaps) — evidence-gap (instrument before C13/C14 launch). Not blocking Stage 10.
- **DEC-10-16 / DEC-07-04 reaffirmation** — not-a-decision for this stage (reaffirmation); a future conditional human decision only if multi-tenancy is proposed.
- **DEC-10-08 governance values** (50% FP, 3 cycles, 20 records) — implementation-specification within CONTEXT Q4 remit; actual go-live remains a recorded operator decision.

No item is a blocking human decision for Stage 10 advancement.

### Evidence-quality assessment

Strong. The three confirmed findings each carry current-implementation / intended-design / identified-gap separation with justified severities (F-10-01 Medium, F-10-02 Informational, F-10-03 Low — reasoned inline). Transient command outputs are duplicated into `evidence/` per standard; stable `path:line` refs are cited directly (permitted). I independently reproduced every load-bearing citation at the current commit (97789f9):

- F-10-01: no `test` script, no vitest/jest/RTL in `package.json`, no config, `find` count 0, frontend CI job is `tsc --noEmit` only, checklist §4 line 45 parks T4.5 for exactly this reason — confirmed.
- F-10-02: `grep -cE "schedule|workflow_dispatch" .github/workflows/tests.yml` → 0 — confirmed.
- F-10-03: `pytest --collect-only` → 328; CLAUDE.md line 94 says "306 passed" — confirmed.

### Consistency assessment

Outputs consume their sources without contradiction. Calibration-governance does **not** redefine the three D-04-01 metrics — it consumes them verbatim from `anomaly-detection-design.md` §5 and adds only cadence/decision rules, within CONTEXT Q4's explicit remit. The baseline consolidation (EG-001..003 + measurement framework's five gaps → six baselines B1–B6) is correct: EG-003 (time-to-go-live) is genuinely distinct from the five gaps, and the two overlaps (EG-001=mapping, EG-002=parallel-run) are correctly merged. Stage 11/12 handoffs are mutually consistent and consistent with `decision-queue.md` (DQ-005 remains jointly with Stage 11; DEC-08-09 carried as a visibility item). `git show --stat 97789f9` confirms only files under `docs/programmes/agentic-architecture-review/` were modified — no production/migration/out-of-scope path; the `state.md` correction is inside authorised paths.

One non-gating observation (not a correction): DEC-10-08's shadow-exit values (≤50% FP, 3 cycles, 20 terminal records) are executor-set governance parameters. They are defensible — CONTEXT Q4 delegates "shadow-mode duration and exit criteria," C7 flags create operator-reviewed exception records rather than mutating payroll, and exit still requires a recorded operator decision (criterion 3), so the human retains the go-live call. Noted only so the parameter's origin is traceable if the human reviewer revisits it at Stage 13.

### Advancement recommendation

Close Stage 10 and open Stage 11 automatically. Every Q1–Q9 has a design answer or an explicitly-classified open item; every output names its gate/hook/behaviour references; both handoffs are complete and consistent; findings are confirmed with re-verified evidence; the sole risk-acceptance touchpoint (DEC-07-04) resolved as an in-authority reaffirmation with the one escalation scenario correctly armed. No stop condition and no blocking human decision remains.

---

## Controller disposition (2026-07-18)

`PASS` + zero required corrections + no blocking human decision → **Stage 10 closed automatically per D-003**; Stage 11 opened context-ready. The critic's non-gating observation (DEC-10-08 parameter origin) requires no change — the parameters' origin is already recorded in `decisions.md` (DEC-10-08) and the critic's note makes it traceable for the Stage 13 reviewer.
