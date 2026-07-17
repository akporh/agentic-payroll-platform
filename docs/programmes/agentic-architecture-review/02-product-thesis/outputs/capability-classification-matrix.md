# Stage 02 Output: Capability Classification Matrix

Every meaningful capability proposed or implied in `docs/architecture/agent-layer-architecture.html`, classified per the Stage 02 prompt's taxonomy. "LLM necessary?" and "simpler approach safer?" are judgment calls made from Stage 01 evidence where available; see `findings.md` for the reasoning behind each non-obvious call.

| # | Capability (track) | Classification | LLM necessary? | Simpler approach safer? | Evidence / uncertainty |
|---|---|---|---|---|---|
| 1 | JWT auth, `operator` table, `get_current_operator` (Track P) | Deterministic software | No | Yes — this is conventional auth engineering | No AI content in the proposal at all; see F-02-03 |
| 2 | Transactional outbox, new domain events (Track V1/V2) | Deterministic software / workflow automation | No | Yes | Event sourcing pattern; no reasoning involved |
| 3 | PII-sanitizing tool serializer (Track V4) | Deterministic software | No | Yes | Rule-based field allowlist/denylist |
| 4 | Event consumer worker, APScheduler (Track V3) | Workflow automation | No | Yes | Polling loop; single-worker constraint noted by the doc itself |
| 5 | In-app notification layer (Track V7) | Workflow automation | No | Yes | Plain table + delivery; email variant (Y3) likewise |
| 6 | Read-only tool definitions (`get_employee`, `get_run_results`, etc., Track V5) | Deterministic software (retrieval layer) | No | Yes — these are query wrappers | The tools themselves are not AI; they are what an agent calls |
| 7 | Navigation Guide mode (Track W) | Retrieval and explanation / probabilistic AI assistance | Yes, for natural-language question interpretation | No — the underlying deep-link data is deterministic, but matching an arbitrary question to it benefits from an LLM | F-02-11 |
| 8 | State Explainer mode (Track W) | Retrieval and explanation | Yes, for composing a narrative from multiple deterministic facts | Partially — the individual facts must come from deterministic tools; only the narrative composition needs the LLM | F-02-11; depends on tool set including all underlying facts, not a pre-packaged "why" tool |
| 9 | Action Planner mode (Track W) | Retrieval and explanation / bounded agentic workflow | Yes, for producing a contextual step sequence | No simpler substitute identified for arbitrary phrasing of "I need to..." requests | Not independently verified against Stage 01 evidence beyond the general Track W assessment |
| 10 | `explain_component_trace` tool | Probabilistic AI assistance, tightly bounded (slot-filling) | Yes, for prose generation only — the underlying numbers must come from the trace | The numeric content should not be LLM-derived at all; only the phrasing | F-02-07 — sound design, depends on trace completeness |
| 11 | Prep Agent — missing timesheets check (Track X2) | Deterministic software (rules engine) | No | Yes — plain query | F-02-04 |
| 12 | Prep Agent — missing salary definition check (Track X2) | Deterministic software (rules engine) | No | Yes — already computed today by `payroll_readiness_service.py` | F-02-04; Stage 01 F-01-19/20 |
| 13 | Prep Agent — contract expiry check (Track X2) | Deterministic software (rules engine) | No | Yes — date comparison | F-02-04 |
| 14 | Prep Agent — anomalous input quantities check (Track X2) | Analytics / anomaly detection | Not necessarily — a statistical rule (threshold/z-score) could suffice; LLM only useful for narrating flagged anomalies | Yes, for detection; LLM optional for narration | F-02-04 |
| 15 | Reconciliation Investigation Agent — causal diff (Track X3) | Should be deterministic software (rules engine / diff computation) | No — the diff itself is a deterministic computation over `component_trace_jsonb` | Yes | F-02-05 — ambiguous in the document as written; recommend explicit separation |
| 16 | Reconciliation Investigation Agent — plain-English presentation (Track X3) | Retrieval and explanation | Yes, for prose only | The causal facts must be pre-computed, not LLM-derived | F-02-05 |
| 17 | Trace Agent (Track X4, named but not detailed in the document) | Retrieval and explanation (inferred) | Likely yes, for prose; underlying data deterministic | Not enough detail in the source document to fully classify | Flagged for Stage 03 — no dedicated card exists for X4 beyond its appearance in the architecture diagram |
| 18 | Structured confirmation UI + `pending_action_id` (Track X) | Deterministic software (workflow / approval mechanism) | No | Yes | F-02-13; this is a UI/state-machine mechanism, not an AI capability |
| 19 | Compliance Monitoring — external source monitoring (Track Y1) | Analytics / retrieval, potentially probabilistic AI assistance for interpreting legal text changes | Plausibly yes for summarizing/interpreting regulatory text; high-risk given legal consequence | Given the legal stakes, a human-in-the-loop review of any AI-drafted interpretation is essential regardless of LLM use | Compliance question forwarded to Stage 06; see F-02-12 |
| 20 | Compliance Monitoring — diff against `statutory_rule` (Track Y1) | Deterministic software | No | Yes — table diff | Part of Y1 but distinct in kind from item 19 |
| 21 | Compliance Monitoring — proposing/applying a migration (Track Y1) | Capability that should not be built as currently scoped | N/A — blocked on missing precondition | A structured, human-approved change-management workflow (deterministic) should exist independent of whether AI detected the need | F-02-12 — no current application mechanism exists at all |
| 22 | Onboarding Agent — messy Excel interpretation, column mapping (Track Y2) | Probabilistic AI assistance / interpretation of unstructured input | Yes — this is inherently a fuzzy-matching problem | No credible simpler substitute for arbitrary human-authored spreadsheets | F-02-10 — one of the better-justified AI capabilities in the proposal |
| 23 | Onboarding Agent — dry-run payroll before commit (Track Y2) | Deterministic software (validation gate) | No | Yes — and necessary as the safety backstop for item 22 | Mechanism itself ("dry-run") is unspecified; see F-02-10 |
| 24 | Email notifications (Track Y3) | Workflow automation | No | Yes | Extension of the deterministic in-app notification layer (item 5) |

## Summary counts

| Classification | Count |
|---|---|
| Deterministic software | 10 |
| Workflow automation | 3 |
| Analytics or anomaly detection | 2 |
| Retrieval and explanation | 5 |
| Probabilistic AI assistance | 2 (items 10, 22, with item 19 plausibly a third) |
| Bounded agentic workflow | 1 (item 9, arguably) |
| Autonomous agent | 0 — nothing in the current proposal is autonomous; Track Y explicitly still requires operator approval for every consequential action |
| Capability that should not be built (as scoped) | 1 (item 21) |

**Headline observation**: of 24 identified capabilities, 10 are plain deterministic software mislabeled (by association with their track) as part of an "agent" proposal, and only 2–3 are capabilities where an LLM is doing something a deterministic mechanism could not — matching the Stage 02 prompt's concern about "agent" terminology being applied to ordinary workflow automation (see F-02-03, F-02-04).
