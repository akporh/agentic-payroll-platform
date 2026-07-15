# Stage 04 Output: Exception Resolution — Outcome and Handoff

Defines the desired outcome and handoff for exception resolution across the portfolio (readiness gaps from C6, anomalies from C7, and — once unblocked — reconciliation mismatches from C8). This is an outcome/workflow framing, not a UX design — Stage 09 owns the interface.

## Why this is one workflow, not three

C6, C7, and (eventually) C8 each *detect* something an operator needs to act on. None of them, individually or collectively, currently have a defined path from "flagged" to "resolved." Stage 03 named this gap for C7 and for C11→C12; this stage generalizes it: **every exception-producing capability in the portfolio needs the same downstream workflow**, so it should be designed once, not three times.

## The eight stages of the outcome, defined

| Stage | Desired outcome | Notes |
|---|---|---|
| **Issue creation** | Every flagged exception becomes a discrete, addressable record — not just a transient notification that disappears if unread | Must persist (per C2's notification table or an equivalent), not be chat-only or ephemeral |
| **Prioritisation** | An operator facing multiple open exceptions can tell which matters most without reading each one individually | Severity/urgency signal needed — e.g. proximity to pay-cutoff, financial magnitude, statutory relevance |
| **Ownership** | Every exception has exactly one accountable operator at any point in time | Prevents the "everyone's queue, no one's queue" failure mode |
| **Evidence** | The exception record links to the specific data that triggered it (the anomalous input value, the missing timesheet, the reconciliation delta) | Same evidence-linking discipline as Principle 4 — an exception without evidence is just an assertion |
| **Recommended next action** | Where a clear next step exists (e.g. "confirm this OT value with the employee's manager"), it's suggested, not left to the operator to invent each time | This is a legitimate, bounded use of AI narration — recommending an action from already-known facts, never inventing the facts themselves |
| **Resolution** | The operator records what was actually done (confirmed correct, corrected, escalated, etc.) | This is the record that makes false-positive/false-negative measurement possible (see `anomaly-detection-outcome-policy.md`) |
| **Verification** | For anything resolved by correcting data, a lightweight check that the correction actually took effect (e.g. the anomalous value no longer flags on re-check) | Prevents "marked resolved" from silently meaning "forgotten about" |
| **Closure** | The exception reaches a terminal state with its full history intact — never deleted, matching this review's own append-only decision-log discipline | Enables the recurring-error root-cause reporting outcome (`product-opportunity-map.md` area 15) once built |

## Explicitly not designed here

The actual UI (exception queue vs. dashboard vs. inline banners), the specific severity-scoring algorithm, and the exact data schema for an exception record are Stage 09's and Stage 08's work respectively. This document defines *what the workflow must accomplish*, not how it looks or is implemented.

## Dependency on C2

This workflow cannot exist before C2 (Event/Tool/Notification Foundation) lands — issue creation needs somewhere durable to write to. This is already reflected in `outcome-prioritisation.md`'s sequencing signal (C1 → C2 → ... → exception-resolution-workflow design).

## Consequence for C7, C8, and future exception producers

Any future capability that flags an exception (anomaly detection, readiness gaps, and eventually reconciliation mismatches) should write into this one shared workflow rather than inventing its own resolution mechanism. This is the structural fix for the coherence gap Stage 03 identified (`portfolio-boundary-map.md` §8) and this stage generalizes across all three current and prospective exception sources.
