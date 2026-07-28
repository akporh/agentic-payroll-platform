# Stage 12 Output: Target Architecture Posture (Q2)

The structural properties the direction commits to preserving as the platform grows — stated as **direction constraints future work is checked against**, not aspirations. Each cites its binding source. A future proposal that violates one of these is either wrong or requires a recorded human decision (gate-ratchet rule, DEC-10-02 via Stage 10 handoff §3).

## 1. The eight posture constraints

### P-A. Determinism-first guarantees (permanent)

Calculation, statutory execution, tax bands, ordering, eligibility, state transitions, locking, payment, mutation, and compliance decisions are deterministic — enforced in code, proven by committed tests, with no LLM in any of those paths (Stage 02 boundary assessment; Principles 1/9; ET-2 design-absence checks make "no LLM in the detection path" itself register evidence). **Check**: any proposal placing a model in one of these paths is rejected at design time, not reviewed at launch.

### P-B. Generation choke points stay single (route table, tool registry)

The platform's assurance scales because its tests are generated from its own structure: SS-1 isolation tests from the live route table, SC-2/SS-2/SS-4 tool tests from the tool registry (Stage 10 handoff §2 property 2). This is the platform's antibody to its own recurring failure mode (decorative scoping — five routes across two rounds, F-05-03/F-07-01). **Check**: new surface area (routes, tools) must register through these choke points — a route or tool created outside them silently escapes the generated coverage and is a defect by construction.

### P-C. Append-only evidence chain

Audit stores are append-only with UPDATE/DELETE rejection, transactional outbox writes, epoch labelling, and zero-orphan chain-completeness sweeps (SS-3, SC-3; `audit-integrity-threat-model.md` via Stage 10 register §2). The 7-year retention floor stands with **no purge mechanism buildable until DQ-008 resolves** (SC-4, O9). **Check**: no mechanism may mutate or delete audit/evidence rows; retention enforcement waits for the recorded legal basis.

### P-D. Independent tool-layer scoping

Every agent-facing data path independently enforces workspace scoping — inheriting it from an underlying query is never sufficient (Principle 11; D-02-02: repo-level fix mandatory, tool-layer check is defence-in-depth only). Tool access is declarative-wrapper, capability-scoped registries with set-equality session tests (SS-4; `tool-layer-security-pattern.md` P1–P8). **Check**: every new tool ships with its negative-path test and registry entry; every capability session exposes exactly its approved minimum tool set.

### P-E. Capped operating cadence

Steady-state assurance fits one monthly + one quarterly scripted operator session (`standing-assurance-controls.md` §6). **Check**: any capability or control that grows the standing cadence must displace something — the constraint bounds *concurrent live AI capabilities*, and a roadmap that ignores it produces controls that silently stop being run.

### P-F. Pattern-scaling assurance (marginal cost is content, not infrastructure)

A new capability inherits the machinery: registry entry (auto-covered by uniformity/negative-path tests), session-registry equality test, eval corpus in the established format, register rows (Stage 10 handoff §2 property 1). **Check**: capability N+1 must not require new assurance *infrastructure*; if it does, the proposal is either mis-scoped or the framework needs a recorded extension — never a silent bypass.

### P-G. Trust-led pacing (gates and baselines before claims)

C7-class detection features are slow-burn by design (shadow ≥ 3 cycles + ≥ 20 terminal records before GA, DEC-10-08); improvement claims require pre-captured baselines (B1–B6, W1–W5 windows); "done = row green" in the launch-gate evidence register. **Check**: no capability's value is claimed before its gate evidence and baseline exist; "fast AI wins" proposals in the detection space conflict with the platform's own governance and are rejected as posture violations, not negotiated per-case.

### P-H. Residual-risk boundaries hold

The direction's narrative stays inside the accepted residual set: in-DB tamper-evidence only (RR-1 — bounded to the current single-bureau deployment shape; multi-tenant re-opens it as a human decision), no cryptographic approval signing (RR-3), pre-epoch identity permanently unverified and labelled (RR-4), retention basis pending (RR-5) (`residual-risk-register.md` via Stage 10 handoff §3). **Check**: no claim or design may assume a stronger property than the accepted residual provides (the overclaim table, `positioning-and-claims.md` §3, is the operational form of this constraint).

## 2. How these constraints are enforced going forward

- **Register ratchet**: CG/SG/SS registers, the launch-gate evidence register, and eval bars may tighten freely; weakening anything requires a recorded human decision (Stage 10 handoff §3). The posture constraints above inherit that ratchet.
- **Standing repo gates**: data-contract changes (e.g. DEC-08-09's statutory UNIQUE widening) go through the repository's standing `/arch-council` gate at Phase 3 — the posture does not replace the repo's own controls, it rides them.
- **Proposal discipline**: every future capability proposal states, capability-by-capability, why a deterministic or simpler mechanism was insufficient (Principle 9's enforcement mechanism, Stage 02) — the Stage 03 reclassification pattern (7 of 15 "agents" were deterministic software) is the cautionary precedent.

## 3. What the posture is optimised for

These properties are jointly optimised for **trust**: auditable, calibrated, evidence-linked automation for a compliance-sensitive bureau market (Stage 10 handoff §2 property 3). Direction options built on speed-to-AI-claims conflict with the posture; direction options built on demonstrable control are what it exists to serve. The evidence register itself is a sellable artifact — the difference between claiming controls and demonstrating them (property 4).
