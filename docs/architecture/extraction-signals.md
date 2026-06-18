# Service Extraction Signals

Tracks the 5 conditions that would justify extracting a module from the monolith into a standalone service.
Updated by `/arch-council` at each gate run. Decision to extract is always a human call.

---

## How to Use

At each `/arch-council` run, check each signal against current state and record the reading.
A signal moves to **AMBER** when it is approaching threshold. **RED** means evaluate extraction now.

---

## Signal Definitions and Current Readings

### S1 — Deployment Cadence Divergence

**Threshold:** A module needs to deploy 5× more often than the rest of the codebase.

**Rationale:** Forces unrelated code through release cycles, slows delivery, increases regression risk.

**Current reading:** GREEN — single monolith, single deploy pipeline. No divergence.

---

### S2 — Resource Profile Divergence

**Threshold:** A module requires a fundamentally different compute profile (GPU, high memory, specialised runtime).

**Rationale:** Forcing GPU workloads through a CPU-optimised monolith wastes money and constrains scaling.

**Current reading:** GREEN — Phase 1 is CPU/DB only. Phase 2 AI inference layer is the likely first trigger.

**Watch:** When Phase 2 agent/inference work begins, re-read this signal immediately.

---

### S3 — Team Ownership Split

**Threshold:** A second team owns a module and deployment coupling creates coordination friction.

**Rationale:** Conway's Law — architecture follows team structure. Shared deployment of separately-owned code creates bottlenecks.

**Current reading:** GREEN — solopreneur, single owner. Not applicable until team grows.

---

### S4 — Compliance Boundary

**Threshold:** A module handles data under a materially stricter regulatory regime than the rest (e.g. PII vault, payment processing under PCI-DSS, data residency constraint).

**Rationale:** Audit scope, penetration testing surface, and data retention rules become unmanageable when compliance-sensitive code is entangled with general business logic.

**Current reading:** GREEN — all data is co-located, single jurisdiction (Nigeria). Monitor if platform expands to additional markets.

---

### S5 — Latency Isolation

**Threshold:** One slow module is measurably degrading p95 response times for unrelated user-facing features.

**Rationale:** Monolith request contention — a heavy background job starves API threads.

**Current reading:** GREEN — no production traffic yet. Re-read when Phase 2 has real load.

---

## Signal History

| Date | Sprint | Signal | Reading | Notes |
|------|--------|--------|---------|-------|
| 2026-06-12 | Phase 1 baseline | All | GREEN | Initial doc — no extraction pressure |
| 2026-06-18 | is_active fix | All | GREEN | No extraction pressure. Retry path correctness defect flagged — internal to monolith, no extraction implication. |

---

## Extraction Playbook (when a signal hits RED)

1. `/arch-council` flags the signal and names the candidate module
2. Bounded architectural review: draw the proposed boundary, audit data ownership, design the inter-service contract
3. `/arch-council` runs on the proposed extraction design before any implementation
4. Human approves the extraction decision
5. Strangler fig pattern — new service runs alongside monolith, traffic migrated incrementally, old code removed only after validation

---

## Likely First Extraction Candidate

**AI inference / agent layer (Phase 2)**

- Divergent compute profile (S2)
- Divergent deployment cadence — model updates decouple from business logic releases (S1)
- Natural API boundary already implied by Phase 2 architecture

No action until Phase 2 signals confirm.
