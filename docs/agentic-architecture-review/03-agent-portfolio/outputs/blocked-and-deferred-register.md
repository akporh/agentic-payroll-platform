# Stage 03 Output: Blocked and Deferred Register

Single place to check what is blocked, deferred, or rejected, why, and what unblocks it. Cross-references `agent-capability-matrix.md` for full detail per capability.

## Blocked

### C4 — Historical Payroll Explanation
- **Blocked by**: D-02-03 (`_core/HUMAN-DECISIONS.md` HD-4)
- **Reason**: historical reproducibility gaps confirmed in Stage 01 (F-01-27, F-01-29, F-01-38)
- **Unblock condition**: F-01-27 (salary_definition editable pre-PAID), F-01-29 (trace-persistence fallback ambiguity), F-01-38 (dead status branches in D-ARCH-1 guard) must all close
- **Owner of unblock work**: Stage 05 (Platform Readiness) to assess and scope; Stage 08 (Technical Architecture) for mechanism design
- **Not an accepted residual risk** — per D-02-03, this is explicitly not to be disclosed to operators as a known limitation while shipping the capability anyway

### C8 — Reconciliation Investigation
- **Blocked by**: D-02-02 AND D-02-03 (`_core/HUMAN-DECISIONS.md` HD-3, HD-4) — two independent blockers, both must clear
- **Reason (D-02-02)**: `payroll_reconciliation` has no repository-level workspace scoping (F-01-33); the `get_reconciliation` tool this capability depends on cannot be built safely until fixed
- **Reason (D-02-03)**: the run being investigated has already completed by the time MISMATCH fires, and its causal explanation depends on the same historical-reproducibility guarantees as C4
- **Unblock condition**: repository-level fix for F-01-33 (+ mandatory tool-layer defence-in-depth check) AND the C4 unblock conditions
- **Owner of unblock work**: Stage 05 (both preconditions), Stage 07 (tool-layer scoping verification)

### `get_reconciliation` tool (tool-level block, distinct from C8's capability-level block)
- **Blocked by**: D-02-02 specifically
- **Reason**: repository functions (`insert_reconciliation`, `update_reconciliation`, `get_reconciliation`) scope solely by `payroll_run_id`, with no workspace check (F-01-33)
- **Unblock condition**: repository-level fix, plus independent tool-layer workspace-ownership verification (both required, neither sufficient alone)
- **Owner of unblock work**: Stage 05 (repo fix), Stage 07 (tool-layer verification), Stage 08 (tool implementation)

## Rejected

### C9 — Trace Agent (Track X4)
- **Rejected as**: a standalone capability
- **Reason**: the source document never defines this capability beyond a diagram label; its evident intent duplicates C5 (`explain_component_trace`) for current-run trace explanation and the existing Timeline/Results UI (Stage 01 F-01-41) for past-run trace review
- **Disposition**: merge its evident intent into C5; do not build separately
- **Reopening condition**: if a future stage identifies a concrete capability need for X4 that C5 and the existing UI genuinely cannot cover, it should be re-proposed as a new, specifically-defined capability — not resurrected under the same undefined name

## Deferred

### C15 — Email Notifications (Track Y3)
- **Deferred per**: the source document's own stated sequencing ("deferred until in-app notifications are proven in production") — not a new decision from this stage
- **Reason**: no new reason beyond the source document's own sequencing logic, which this stage found no reason to override
- **Unblock condition**: C2 (in-app notification layer) must ship and be proven in production first
- **Owner**: Stage 11 (Commercial & Product Strategy) for sequencing into a roadmap

## Restricted (not blocked, but scope-limited)

### C11 — Compliance Monitoring (Track Y1)
- **Restricted by**: D-02-04 (`_core/HUMAN-DECISIONS.md` HD-5)
- **Restriction**: may detect, compare, and propose only; must never author, execute, or deploy a production migration
- **Not blocked outright** because the detect/compare/propose scope is buildable independent of C12 existing — but its output has nowhere to go until C12 exists (see below)
- **Dependency**: C12 must exist for C11's output to be actionable — recommend scoping/building together even though they are separate capabilities

## New capability named by this stage (not previously in the source document)

### C12 — Statutory-Rule Change Management
- **Status**: not blocked, not yet scoped — a genuinely new capability this stage identified as missing (F-02-12's gap, given an owner)
- **Owner**: Stage 06 (Compliance & Controls) for the approval-workflow design; Stage 08 (Technical Architecture) for the mechanism
- **Priority signal**: without this, C11 (Compliance Monitoring) is not shippable end-to-end — recommend Stage 11 sequence them together

## Reclassified (not blocked, not agent work)

The following are not blocked or deferred — they are simply moved off the "agent portfolio" and onto ordinary engineering backlogs, per the Stage 03 prompt's "reclassify as deterministic platform work" disposition:

- C1 — Identity & Auth Foundation
- C2 — Event/Tool/Notification Foundation
- C6 — Payroll Readiness Service
- C10 — Structured Confirmation/Pending Action Protocol
- C14 — Deterministic Import Validation & Dry-Run (the dry-run mechanism itself still needs Stage 08 definition, but the capability is not AI work)

None of these require an agent-portfolio decision beyond "build it as conventional software" — see `agent-capability-matrix.md` for full detail per item.
