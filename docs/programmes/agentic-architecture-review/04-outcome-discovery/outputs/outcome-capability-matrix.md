# Stage 04 Output: Outcome ↔ Capability Matrix

Maps every approved capability (`03-agent-portfolio/outputs/agent-capability-matrix.md`) to the lifecycle outcome(s) it serves, and flags capabilities/outcomes with no counterpart in the other direction.

## Capability → outcome coverage

| Capability | Lifecycle area(s) served | Outcome rationale | Status |
|---|---|---|---|
| C1 — Identity & Auth Foundation | 1 (workspace/client setup), all others indirectly | Prerequisite for verified identity/workspace isolation everywhere | Foundational — no direct outcome of its own, enables all others |
| C2 — Event/Tool/Notification Foundation | 6, 8 (readiness, exception handling) | Prerequisite for any proactive notification | Foundational |
| C3 — Operator Assistant, Current-State Mode | 12 (post-payroll support) | Reduces support burden, current-state "why" explanations | Retained AI capability |
| C4 — Historical Payroll Explanation | 12 (post-payroll support, historical) | Same outcome as C3, extended to history | Blocked (D-02-03) — outcome deferred, not rejected |
| C5 — Trace Explanation | 7 (calculation), 12 (support) | Evidence-linked explanation of current-run results | Retained AI capability |
| C6 — Payroll Readiness Service | 6 (readiness) | Proactive surfacing of 3 named readiness conditions | Reclassified deterministic |
| C7 — Input Anomaly Detection | 5 (input collection), 8 (exception handling) | Catches data-entry errors before they enter a run | Retained (deterministic detection + optional narration) |
| C8 — Reconciliation Investigation | 9 (reconciliation) | Automated causal diagnosis of MISMATCH | Blocked (D-02-02 + D-02-03) |
| C9 — Trace Agent | (rejected — see C5/existing UI) | N/A | Rejected as standalone |
| C10 — Structured Confirmation Protocol | 8 (exception handling, future write actions), 10 (approval, future) | Prerequisite for any future write-capable agent | Foundational, not itself outcome-bearing yet |
| C11 — Compliance Monitoring (narrowed) | 13 (statutory monitoring) | Faster detection of external regulatory change | Retained, restricted scope |
| C12 — Statutory-Rule Change Management | 13 (statutory monitoring) | Real application path for a detected change | New deterministic capability |
| C13 — Onboarding Mapping Assistant | 3 (registration), 14 (new-client onboarding) | Faster, less error-prone bulk mapping | Retained AI capability |
| C14 — Deterministic Import Validation & Dry-Run | 3, 14 | Hard safety gate for C13's proposals | Reclassified deterministic |
| C15 — Email Notifications | 6, 8 (extends C2) | Off-app notification delivery | Deferred, reclassified deterministic |

## Lifecycle areas with no capability at all

| Area | Gap |
|---|---|
| 2 — Structural configuration | Two-entry-point duplication is a UX gap, not covered by any capability; no capability addresses it |
| 4 — Employment/contract configuration | `shift_type` NULL-handling divergence is a product-consistency gap, not covered by any capability |
| 15 — Operational reporting and continuous improvement | No capability in the 15-item portfolio touches this at all — the clearest missing-outcome area in the entire map |

## Outcomes proposed in `CONTEXT.md` §3 ("discover missing outcomes") mapped against the approved portfolio

| Proposed missing outcome | Covered by existing capability? | Assessment |
|---|---|---|
| Pre-approval assurance packs | No | New — see `outcome-prioritisation.md` |
| Material period-on-period movement explanation | Partially — C7's detection logic is adjacent, but framed for input anomalies, not aggregate movement | New/adjacent — see prioritisation |
| Operator work queues and ownership | No | This is exactly the exception-resolution-workflow gap (area 8) — see `exception-resolution-outcome.md` |
| Recurring-error root-cause reporting | No | New — depends on audit-coverage fix (F-01-40) first |
| Payroll deadline-risk visibility | No | New — a readiness/timeline extension, adjacent to C6 |
| Control-completion evidence | No | New — depends on audit-coverage fix (F-01-40) |
| Client profitability or operational-cost insight | No | New, commercial-facing — Stage 11's natural remit more than Stage 04's |
| Support-response drafting | Partially — C3's explanation capability is adjacent but not framed as external-facing drafting | New/adjacent |
| Configuration-drift detection | No | New — related to area 2's two-entry-point gap |
| Unresolved-input visibility | Partially — C7/C6 surface some of this; a dedicated "unresolved inputs" view does not exist | Adjacent — see prioritisation |

## Capabilities whose outcome rationale is weak or under-specified

Per `CONTEXT.md` question 4 ("which capabilities solve weakly-defined or low-value problems"):

- **C9 (Trace Agent)** — already rejected in Stage 03 for lacking a defined outcome at all; reconfirmed here as having no outcome rationale distinct from C5.
- **C10 (Structured Confirmation Protocol)** — not weak, but currently has *no* active outcome to serve, since every capability that would need it (C8, and any write-capable extension of C11) is either blocked or restricted from writing. Its value is entirely prospective. This is not a reason to deprioritize building it correctly when needed, but it should not be scored against a current-state outcome metric — see `measurement-framework.md`.
