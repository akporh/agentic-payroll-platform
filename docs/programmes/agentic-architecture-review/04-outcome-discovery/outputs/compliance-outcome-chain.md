# Stage 04 Output: Compliance Outcome Chain (C11 → C12)

Frames the complete end-to-end outcome chain from external regulatory change to applied, tested platform rule — spanning C11 (Compliance Monitoring, narrowed) and C12 (Statutory-Rule Change Management, deterministic), which remain **separate capabilities** per D-02-04. This document defines the outcome chain that connects them without merging their scopes.

## The chain, stage by stage

| Stage | Owner capability | Outcome | Evidence/note |
|---|---|---|---|
| 1. Detect possible external change | C11 | An external FIRS/PenCom (or other statutory-body) update is noticed, not missed | Depends on external-source monitoring reliability — forwarded to Stage 06 as a trust/freshness/provenance question, not resolved here |
| 2. Verify source and effective date | C11 | The detected change is confirmed against an authoritative source with a specific effective date, not just a rumor or a secondary summary | This is where the legal-risk exposure concentrates — C11 must never present a low-confidence or unverified signal as though it were confirmed |
| 3. Compare with current platform rules | C11 | A precise, deterministic diff against the current `statutory_rule`/`tax_band` state (Stage 01 F-01-45/46) | This comparison step itself is deterministic (Stage 03 C11 disposition) — the LLM's role is upstream (interpreting external text), not this diff |
| 4. Assess affected clients/runs | C11 or C12 (boundary question, see below) | Operators know which workspaces/periods a change would affect before approving it | Needs a clear owner — see open boundary question |
| 5. Prepare a proposal | C11 | A human-reviewable proposal exists: what changes, effective when, citing what source | C11's output; must never be auto-applied (D-02-04) |
| 6. Review and approve | Human (via C12's workflow) | A compliance-responsible human reviews the proposal and explicitly approves or rejects it | This is the mandatory human gate — not optional, not bypassable regardless of C11's confidence level |
| 7. Apply through the separate deterministic mechanism | C12 | The approved change is written to `statutory_rule`/`tax_band` through an application-level workflow, not a developer-authored migration | This is exactly the gap Stage 01 (F-01-45/46) and Stage 02 (F-02-12) identified as missing entirely today |
| 8. Test and evidence the result | C12 (or `test`/`audit` per the sprint workflow) | The applied change produces correct calculations for at least one representative case before being trusted in production | Should reuse existing calculation-correctness discipline (Stage 01's deterministic engine), not invent a new verification mechanism |

## Open boundary question (stage 4 above)

Whether "assess affected clients/runs" belongs to C11 (part of the proposal, so the human reviewer sees impact before approving) or C12 (part of the application workflow, so impact is assessed against the *approved* change specifically) is not resolved by this stage — it's a genuine design choice with a plausible case either way, forwarded to Stage 06/08 as an open question, not adjudicated here. What is fixed: the assessment must happen somewhere in the chain before stage 7 (application), not be skipped.

## Why the separation matters for the outcome, not just the architecture

Keeping C11 and C12 separate is not just an architectural tidiness preference (per D-02-04) — it materially changes the outcome's risk profile. If detection and application were one capability, an over-confident or manipulated detection step could flow directly into a production change with no independent gate. Splitting them means C11's worst failure mode (a wrong or premature detection) is contained by C12's mandatory human-approval gate, regardless of how the detection went wrong. This is the outcome-level justification for a decision that was originally made on architectural grounds.

## What "the end-to-end outcome" actually measures

Per `measurement-framework.md`: time-to-detection and time-to-apply, both measured end-to-end across the full chain above, not per-capability. A fast C11 feeding an unbuilt or slow C12 produces the same poor outcome as a slow C11 — the metric must reflect the whole chain's performance, which is precisely why this document frames it as one chain even though it's built as two capabilities.
