# Stage 06 Output: Agent/Tool Audit Standard — Requirements Level

Resolves Stage 03's open question from `tool-portfolio-matrix.md`: every tool row carries "Required audit record: tool-call log — Stage 06 to confirm retention requirement," and the Stage 03→06 handoff asks whether tool-call-level logging needs the same 7-year retention the source document proposes for `agent_session_log`, and what fields are mandatory. Both are answered here. Stage 08 owns the storage mechanism/schema; Stage 07 owns the identity mechanism the records depend on.

## 1. What the source document already proposes (intended design, S-04)

- `agent_session_log`: `workspace_id, operator_id, turn_sequence, tool_calls_jsonb`, 7-year retention (`agent-layer-architecture.html:938`), rationale "audit trail only; 7-year retention for payroll dispute resolution" (line 1150–1151), shipping only after auth so `operator_id` is real ("Placeholder operator_id audit trail is worse than none," line 496).
- Nothing exists in code today: no agent layer, no tool layer, no `agent_session_log` table (F-05-02 — consumed, not re-verified).

## 2. Retention — resolved

**Tool-call records take the same 7-year retention as `agent_session_log`.** Reasoning:

1. The source document's own design already embeds tool calls *inside* the session log (`tool_calls_jsonb` is a column of `agent_session_log`) — so under the document's own proposal, tool-call data was always going to live under the 7-year rule. Splitting tool-call logs out to a shorter retention would weaken the existing intent, not implement it.
2. The stated purpose is payroll dispute resolution. In a dispute, the operative question is "what facts did the assistant/agent actually retrieve, and what did it show the operator" — that is precisely the tool-call record. A session log without its tool calls is narrative without evidence.
3. Retention must be uniform across the evidence chain for one interaction: session narrative, tool calls, and any resulting confirmation/approval record (C10/C12) must all survive together; the chain is only as durable as its shortest-lived link.

**Distinction permitted:** purely operational telemetry (latency metrics, token counts, rate-limit counters) is not compliance evidence and may have ordinary short operational retention — provided the compliance record (§3) is complete without it.

**Residual legal parameter, escalated:** the 7-year figure itself is asserted by the source document without a cited legal basis (evidence file §7). Whether Nigerian statutory record-keeping obligations (FIRS/PenCom/labour) require 6, 7, or another number of years is a legal determination — recorded as **DQ-008** (non-blocking; must be confirmed with professional advice before any retention-enforcing mechanism is built). Until resolved, 7 years stands as the working floor: keep-at-least; do not build deletion at 7 years into the mechanism until the legal minimum and any maximum (data-protection) are both confirmed.

## 3. Mandatory fields per tool-call record

Every tool invocation by any agent capability (C3, C5, C7-narration, C11, C13) must record:

| Field | Requirement |
|---|---|
| Record ID + timestamp | Unique, monotonic within a session |
| Session linkage | FK/reference to the `agent_session_log` entry (or equivalent invoking context — e.g. a scheduled C11 check has a job identity instead of a chat session) |
| **Verified** workspace identity | From the JWT, never caller-supplied (F-05-01 consumed; see `attribution-identity-requirements.md`) |
| **Verified** operator identity | The authenticated principal; for autonomous/scheduled invocations, a named service principal — never a placeholder string |
| Tool name + version | The tool contract version matters: what `get_employee` returned/stripped in v1 vs v2 is dispute-relevant |
| Input parameters | Complete, after PII policy applied |
| Outcome class | `success` / `empty` / `refused` / `error` — refusals are first-class outcomes: the tool matrix specifies refusal behaviours (cross-workspace 404/refusal, null-trace refusal) and a dispute may hinge on proving the system *correctly refused* |
| Result content or digest | What the LLM actually received. Where full payloads are too large, a digest plus row identifiers/counts is acceptable **only if** the underlying data remains reconstructible for the retention period — otherwise store the payload. For `explain_component_trace`, the trace fields actually surfaced must be logged per the tool matrix's own row ("log the trace fields actually surfaced, for evidence-linking") |
| PII disposition | Which PII stripping/allowlist rule-set version was applied (the sanitizer is versioned config; proving *what was withheld* from the LLM is part of the compliance story) |

## 4. Integrity requirements (shared with all audit domains)

Per `audit-expansion-requirements.md` §3: tool-call records must be append-only, immutable, attributable, and written reliably (not fire-and-forget). The existing `audit_log`/`event_store` pattern fails all four today (F-06-01/02/03) — the new mechanism must not inherit it.

## 5. Which capabilities this binds

Applies to every LLM-touching capability the approved portfolio retains (C3, C5, C7-optional-narration, C11, C13) and to C10's confirmation protocol (whose proposal/confirmation/rejection records the Stage 03 matrix already flagged for "Stage 06 to confirm requirements" — confirmed: same standard, same retention, since a confirmed action is exactly the kind of record a dispute turns on). Deterministic reclassified capabilities (C1, C2, C6, C12, C14, C15) fall under the domain-audit requirements in `audit-expansion-requirements.md` instead — same integrity properties, different record shapes.
