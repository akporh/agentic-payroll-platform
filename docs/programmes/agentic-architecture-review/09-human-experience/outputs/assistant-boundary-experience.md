# Stage 09 Output: Assistant Boundary Experience — C3 (Q3)

Designs the chat boundary UX for the Operator Assistant. **Binding inputs rendered**: the five pre-specified refusal conditions and current-state-only launch boundary (`03-agent-portfolio/outputs/portfolio-boundary-map.md` §3, Condition 5 / D-03-01); C3's capability-scoped tool registry (`08-technical-architecture/outputs/tool-contracts.md` §1 — `get_employee`, `get_employees`, `get_payroll_run`, `get_enrollment_status`, `get_salary_definitions`); the Stage 04 warning against designing for chat volume (`measurement-framework.md` C3). Chat is the approved primary surface for C3 **only** — every other capability has a non-chat surface (portfolio §7).

## 1. Surface shape

A floating assistant bubble opening a side chat panel, available on workspace pages (workspace context = the session's `wid`; C3 tools scope through it mechanically — P2). Not present on the bureau dashboard in v1: C3's tools are workspace-scoped, and a cross-workspace assistant would invite exactly the questions it must refuse.

Three modes (Navigation Guide / State Explainer / Action Planner) are **presentation-invisible** — one assistant, one input box. The mode split is an internal capability boundary (D-03-01), not a user-facing choice; forcing operators to pick a mode before asking would be a taxonomy quiz.

## 2. Refusal UX — the five conditions, with copy patterns

Refusals are first-class answers, not errors: rendered as a normal assistant reply with a distinct "boundary" presentation (muted info styling, never red/error styling — the assistant working as designed is not a failure state). Copy patterns (final microcopy is Phase 3 `/ux-copywriter` territory; the *content requirements* below are binding):

| Condition (boundary map §3) | Copy pattern | Content requirements |
|---|---|---|
| **Missing facts** (tool returns empty/null for a required field) | "I can't confirm that — {fact} isn't recorded for {entity}. You can check {surface}." | States which fact is unavailable, plainly; never infers or guesses a value; offers the owning surface where the operator could fix/verify |
| **Historical reconstruction** | "I can only answer about the **current** state. Reconstructing what a past run saw isn't supported yet — that's a platform limitation, not a permissions issue. The run's stored results and audit log are here: {link}." | Explicit refusal; names the limitation as platform capability (per §3: "platform limitation, not permission-denial"); never silently answers with current-state data as if historical; links to the deterministic record that *does* exist (run detail tabs) |
| **Cross-workspace** (entity outside the session workspace) | "I couldn't find that {entity type} in this workspace." | Identical wording to genuine not-found — the tool layer's uniform `REFUSED`/not-found (P5) propagates as-is; **UX-critical invariant: no copy variant may distinguish "exists elsewhere" from "doesn't exist"** (no existence disclosure) |
| **Ambiguous tool result** (unexpected multiple match) | "I found more than one record matching that, which shouldn't normally happen: {identifiers}. Please pick one, or check {surface}." | Surfaces the ambiguity explicitly with the candidate identifiers; never picks one silently |
| **Null trace** (legacy-executor result) | Fixed text from the tool contract: "A calculation trace is not available for this result; it was produced by the legacy execution path." | Verbatim contract text (`tool-contracts.md` §3.5 `TRACE_UNAVAILABLE`); no degraded generic explanation substituted |

Refusal condition 2 (historical) must hold at ~100% for genuinely historical questions — the Stage 04 safety metric; Stage 10 owns the eval set (`stage-10-handoff.md`).

## 3. Grounding presentation — "Based on"

Every substantive answer carries a **grounding footer**: "Based on: {Employee record — Adaeze O.}, {Enrollment status}, {Current run PR-2026-07}" — one chip per tool result consumed, each a link to the owning surface. Rendered mechanically from the session's tool-call results (which are logged per invocation — `tool_call_log`, P7), never model-asserted. An answer with no tool facts behind it (pure navigation guidance) shows no footer — absence of chips is itself the signal that nothing was read.

- UUIDs in tool results are mapped to display names frontend-side (`tool-contracts.md` §2 — PII stripped at the tool layer; the UI, inside the operator's authorised workspace session, resolves names).
- Numbers in answers are render-verified against tool-result values for C5-adjacent trace prose (the serializer-level provenance check is Stage 08's; the UI simply must not display text that bypassed it).

## 4. Not burying one-glance information (the Stage 04 constraint)

Design rules preventing the interface from *encouraging* unnecessary chat:

1. **Deep-link over reproduce**: when an answer's substance is a list or table the UI already renders (enrollment gaps, input issues, run status), the assistant answers with the fact summary + a link ("3 employees aren't enrolled — open Employees → Not enrolled") rather than reproducing the table in chat. Chat never becomes an alternate data browser.
2. **No chat-only information**: nothing is answerable in chat that has no owning UI surface. If a genuinely useful fact keeps being asked and has no surface, that's a product-gap finding for the roadmap, not a chat feature.
3. **No proactive chat**: the bubble never auto-opens, never badges, never generates notifications. Proactive surfacing is C6/C7's job through the exception queue — push belongs to the queue, pull belongs to chat (the Stage 03 trigger-direction split, kept literally in the UX).
4. **Metrics**: nothing in the UI instruments "messages per operator" as a success signal (measurement framework prohibition); Stage 10's evaluation reads outcome metrics only.

## 5. C10 proposal boundary in chat

When a C3 conversation leads to a proposable action (Action Planner mode), the assistant's reply may include a **proposal card** — status display of a created `pending_action` (from its frozen payload, `payload_jsonb`). **UX-critical invariant (T7/SG-10): the card in chat carries no Confirm control.** It links to the pending-action surface (`confirmation-experience.md`), where confirmation is a distinct authenticated action. The card's later states (executed/expired/invalidated) update from the record, so a stale chat transcript never misrepresents an action's outcome as pending.

## 6. Error and empty behaviour

- Tool `ERROR` outcomes: generic assistant apology + retry offer; never `str(e)` or tool internals (standing prohibition extends to chat).
- The assistant does not retry silently more than once; repeated failure → "Something's failing on my side — the {surface} page has this information directly."
