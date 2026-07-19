# Stage 13: Approved Roadmap — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Gate opened**: 2026-07-18 (executor pass complete; awaiting critic, then the human approval gate)
- **Gate closed**: not yet — this stage closes only when the human reviewer records approval in `_core/HUMAN-DECISIONS.md` (never automatically)

## Human decisions log

Human decisions taken **2026-07-19** by Michael Emedo. Master entries: `_core/HUMAN-DECISIONS.md` HD-8…HD-16. The executor made **zero** human decisions — these are transcriptions of the reviewer's stated decisions. **Seven recorded; two remain PENDING** (DP-2, DP-9).

| DP | Item | Decision | HD | Status |
|---|---|---|---|---|
| DP-1 | Statutory approval controls (DQ-007 + MFA) | **A1 + B2** — same operator may propose & approve for v1; password re-auth at approval; MFA deferred, not a v1 launch gate, design stays MFA-compatible. **Recorded as A1 + B2, not A2.** | HD-8 | Recorded |
| DP-2 | Source-document disposition (D-02-01) | **PENDING human review** — HTML + mirror NOT superseded/retired; open until the Architecture Baseline Pack is reviewed | HD-9 | **Pending** |
| DP-3 | Product direction | **APPROVED: single-bureau, SaaS-ready** — optimise for Sandy; keep credible SaaS path; SaaS not on critical path; active SaaS needs separate evidence + authorisation | HD-10 | Recorded |
| DP-4 | Professional advice engagement (DQ-006 + DQ-008) | **APPROVED** — initiate NG payroll/tax/legal advisory at the appropriate point; preparatory only, authorises no implementation | HD-11 | Recorded |
| DP-5 | Audit-tamper residual (RR-1) | **NOTED (accepted)** for current single-bureau managed-Postgres deployment; revisit only on an existing trigger | HD-12 | Recorded |
| DP-6 | Statutory-rule UNIQUE widening (DEC-08-09) | **NOTED** — handled via normal arch-council + implementation governance when C12 is authorised; no implementation now | HD-13 | Recorded |
| DP-7 | Onboarding measurement evidence (EG-004) | **RESOLVED with amended evidence approach** — controlled onboarding benchmark from historical/synthetic data, measured consistently vs manual; live evidence collected opportunistically; simulated data labelled as controlled benchmark, never live-performance proof. Amends the prior B1/B2 "unrecoverable live window" framing | HD-14 | Recorded |
| DP-8 | Commercial-demand evidence (EG-005) | **APPROVED** — distinguish validated capability from validated demand; no demand/WTP/adoption/SaaS-viability claims without market evidence | HD-15 | Recorded |
| DP-9 | Roadmap approval | **PENDING final human confirmation** — roadmap is the current *proposed* sequence, not finally approved; final approval depends on Architecture Baseline Pack review | HD-16 | **Pending** |

## Executor synthesis conclusions (DEC-13-*)

These are the executor's roadmap-assembly conclusions — not human decisions. They record how the roadmap was assembled from confirmed prior facts.

### DEC-13-01: Roadmap sequenced in 6 build tranches (+ Tranche 0 near-term); value order = readiness order
- **Conclusion**: The build sequence is `C1 → C2 → C12 & C14 → C6/C3/C5 → C7 shadow → C11 → C13`, grouped into Tranches 1–6, preceded by a no-build-authorisation Tranche 0. This equals both the value-priority signal and the readiness order (DEC-11-03) — no direction-vs-constraint trade-off exists, so the roadmap makes none.
- **Basis**: `sequencing-economics.md` §4; Stage 12 handoff §2; `capability-end-state-map.md`.

### DEC-13-02: Per-item definition-of-done = launch-gate register rows green; B-series threaded at their windows
- **Conclusion**: Every build item's "done" is the launch-gate evidence register's corresponding rows pointing at merged CI-green artifacts (or dated ET-2/3/5/6 records) — "done = row green" (DEC-10-02). B3/B5 captured now (W5); B1/B2 pre-C13 on a real onboarding (W2, unrecoverable); B6 pinned to C3 planning (W3); B4 to C6 planning (W4); C7 GA gated on W1.
- **Amended by HD-14 (DP-7, 2026-07-19)**: the B1/B2 "real onboarding (W2, unrecoverable)" framing above is superseded by the controlled-benchmark evidence approach — B1/B2 may be captured from a governed historical/synthetic onboarding benchmark (labelled controlled-benchmark, never live proof), with live-onboarding evidence collected opportunistically. This DEC line is left intact as the pre-amendment record; the roadmap/KPI text is not rewritten here because DP-9 (roadmap approval) remains pending — reconcile at final approval.
- **Basis**: `launch-gate-evidence-register.md`; `evidence-chain-and-baselines.md`; `direction-kpis.md`.

### DEC-13-03: Decision pack consolidates 9 items from both stage-13 handoffs, each once, classified; executor resolves none
- **Conclusion**: DP-1 (DQ-007+MFA), DP-2 (source-doc disposition), DP-3 (SaaS fork), DP-4 (DQ-006+008 engagement), DP-5 (RR-1 visibility), DP-6 (DEC-08-09 visibility), DP-7 (EG-004), DP-8 (EG-005), DP-9 (roadmap approval) — every item from `12-target-direction/outputs/stage-13-handoff.md` §3 and `11-commercial-product-strategy/outputs/stage-13-handoff.md` §2/§5 appears exactly once, classified per `CRITIC.md`. Options and consequences presented; no human decision made by the executor.
- **Basis**: both stage-13 handoffs; `pre-build-decision-logistics.md`; `decision-queue.md`.

### DEC-13-04: Zero F-13 findings; two placement details are implementation-specifications, not inconsistencies
- **Conclusion**: Roadmap assembly exposed no inconsistency between confirmed prior facts (F-13-* = none). The CI-schedule-seam host (C6 vs C3, `proposed-roadmap.md` Item 3.1) and the C10 build trigger (`proposed-roadmap.md` §3) are sprint-planning details the sources deliberately leave open — classified `implementation-specification`, not `blocking-human-decision`, not findings.
- **Basis**: `findings.md`; `sequencing-economics.md` §3; `capability-end-state-map.md` C10.

### DEC-13-05: RR-1 trigger (c) discipline held — roadmap is single-bureau, SaaS-ready; no item exists because of SaaS ambition
- **Conclusion**: The roadmap carries the single-bureau default (`target-direction-statement.md` §5). No build item exists *because of* SaaS ambition — the assurance substrate is built for the single bureau and is merely not-throwaway for a future SaaS story — so the F-11-01 bundle is **not** placed on the critical path. If the reviewer takes up SaaS (DP-3), the bundle (incl. RR-1 re-open) goes first.
- **Basis**: DEC-10-16, DEC-11-04, DEC-12-01; `product-scope-boundaries.md` §2.2.

### DEC-13-06: Phase boundary — approval settles what/order/done only, not when/whether to build
- **Conclusion**: Stage 13 approval records the direction, the source-document disposition, the roadmap, DQ-007's resolution, and initiation of the DQ-006/008 engagement, and closes Phase 1. It authorises **no** build; Phase 2/3 authorisation and the remaining pre-build gates (DQ-006, DQ-008, DEC-08-09 review) are separate later gates.
- **Basis**: POLICY §Human approval required for / §Executor may not; WORKFLOW §Human gating; `final-decision-pack.md` Q5.

## Next action

**Stage 13 remains OPEN (`awaiting-human-decision`).** Seven DP items recorded 2026-07-19 (HD-8, HD-10–HD-15); **DP-2 (HD-9) and DP-9 (HD-16) remain PENDING** human review of the **Architecture Baseline Pack** (`outputs/architecture-baseline-pack.md`). Recording DP-2 and DP-9 closes Stage 13 and Phase 1 — not yet done; Phase 1 is **not** complete and no implementation, supersession, or programme closure is authorised. (The independent critic PASSed the roadmap on 2026-07-18; a separate independent critic reviews the baseline pack after this executor pass.)
