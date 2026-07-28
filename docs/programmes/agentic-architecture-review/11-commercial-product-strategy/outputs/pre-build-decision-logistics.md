# Stage 11 Output: Pre-Build Decision Logistics (Q6)

The concrete resolution path for DQ-006, DQ-007 and DQ-008 — who provides input, what lead time to plan for, and what each blocks — so Stage 13 can place them on the critical path deliberately rather than discovering them as sprint blockers. Nothing here resolves any of the three (all are human decisions; POLICY).

## 1. Per-decision logistics

### DQ-006 — Tier-1 authoritative-source allowlist (blocks C11 build authorisation)

- **The question**: which external sources (FIRS, PenCom, gazette, etc.) are *legally sufficient* for statutory-change monitoring, such that relying on them meets the bureau's professional-duty obligations (`compliance-monitoring-source-policy.md` §4).
- **Who**: the human reviewer (Michael) **with professional Nigerian tax/legal advice** — the stage 06 record is explicit that this is outside the review's authority and expertise.
- **What it blocks**: the C11 register row cannot close without the recorded decision (CG-11); C11 *design* work is not blocked, only build authorisation and launch.
- **Lead time driver**: engaging a Nigerian tax/legal professional — an external-party clock the build plan doesn't control. Unknown duration; the risk is starting it late, not its cost.
- **Deliverable**: a recorded human decision (programme decision log) naming the confirmed Tier-1 allowlist and the review cadence it was confirmed against.

### DQ-007 — Single-operator segregation waiver + MFA hard-gate question (blocks C12 build authorisation)

- **The question** (two parts, decided together per the Stage 07 amendment): (a) accept single-operator statutory approval with compensating controls (cooling-off delay, second-channel notification) vs hold proposer ≠ approver and accept slower changes; (b) whether MFA enrollment for approval-capable operators becomes a *hard* C12 launch gate (password-only step-up is the floor per DEC-07-03).
- **Who**: the human reviewer alone — this is an internal risk-appetite call; no external professional is strictly required (options and compensating controls are already designed, `statutory-change-control-design.md` §8).
- **What it blocks**: the C12 register row (CG-12). **This is the earliest human gate any plausible build sequence hits** — C12 is pursue-now, deterministic, and unlocks C11.
- **Lead time driver**: none external — only decision scheduling. The natural slot is the **Stage 13 roadmap-approval touchpoint**, which the human reviewer attends anyway (RR-1 visibility is already scheduled there).
- **Interaction to surface**: if the resolution holds proposer ≠ approver, multi-operator capability becomes a C12 *prerequisite* rather than a later increment (`product-scope-boundaries.md` §2.1) — the options pack must make this consequence explicit.
- **Deliverable**: one recorded decision covering both parts, with the chosen compensating controls (if any) named so the C12 build story can include them.

### DQ-008 — Legal retention basis (blocks retention-enforcing mechanisms only)

- **The question**: the statutory minimum (FIRS/PenCom/labour record-keeping) and any data-protection maximum for audit/evidence retention; the source document's 7-year figure is uncited.
- **Who**: the human reviewer with professional legal advice — same professional domain as DQ-006.
- **What it blocks**: only the building of purge/retention-enforcement mechanisms (SC-4's design-absence check enforces this). Nothing in the near-term build sequence needs it; "keep at least 7 years" stands meanwhile.
- **Lead time driver**: same external-professional clock as DQ-006.
- **Deliverable**: recorded decision confirming minimum and maximum; RR-5 then converts to a closed note or a revised retention design.

## 2. Logistics recommendation (DEC-11-05 — an efficiency observation, not a decision)

- **Bundle DQ-006 and DQ-008 into a single professional-advice engagement**: same domain (Nigerian statutory/tax/data-protection law), same adviser profile, one engagement overhead instead of two. Initiate the engagement **at or immediately after Stage 13 approval** — well before any C11 sprint, and early enough that DQ-008's answer arrives before anyone is tempted to build retention tooling.
- **Package DQ-007 (both parts) into the Stage 13 decision pack** alongside the items already scheduled for that touchpoint (RR-1 visibility, DEC-08-09 visibility, final roadmap approval). It needs no external input and gates the earliest deterministic differentiator — resolving it at Stage 13 keeps it off every sprint's critical path.
- **Sequencing insurance**: if Stage 13's approved roadmap puts C12 in the first build tranche (likely, given pursue-now status), DQ-007's resolution at the same touchpoint means zero added calendar cost. DQ-006 only becomes calendar-critical when C11 enters a sprint plan — but since C11 rides with/after C12, starting the professional engagement at Stage 13 gives it the longest possible runway at no extra cost.

## 3. Stage 13 placement summary

| Decision | Resolve at | External dependency | Becomes critical when |
|---|---|---|---|
| DQ-007 (+ MFA) | Stage 13 decision pack | None | C12 enters a sprint (first tranche, likely) |
| DQ-006 | Professional engagement initiated at Stage 13 | Nigerian tax/legal adviser | C11 enters a sprint |
| DQ-008 | Same engagement as DQ-006 | Same adviser | Only if/when retention enforcement is proposed |
