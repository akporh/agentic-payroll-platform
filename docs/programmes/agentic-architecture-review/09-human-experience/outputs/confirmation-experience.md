# Stage 09 Output: Confirmation Experience — C10 (Q4)

Designs the operator experience of the structured confirmation protocol. **Mechanism rendered**: `pending_action`, its CAS state machine and terminal states (`08-technical-architecture/outputs/confirmation-protocol-design.md` §§1–4). **Security constraints bound**: render exclusively from frozen `payload_jsonb` (SG-10/T6); confirmation is an authenticated UI action distinct from chat (T7); double-submit returns the recorded outcome.

## 1. Placement in the IA

A workspace-sidebar entry **Pending Actions** adjacent to Exceptions (both in the Payroll section), badge = `PROPOSED` count. Separate from the exception queue because the operator stance differs: exceptions ask "investigate and fix"; pending actions ask "decide yes or no on a specific proposed change." Merging them would force one list to carry two different action grammars.

List view: proposed-by (agent session vs operator — `proposed_by_kind` chip), action type in plain language, target entity (display name), proposed time, **expiry countdown** ("expires in 2 days" — `expires_at`), status. Default filter: Proposed; History filter shows terminal records (permanent, append-only).

## 2. The confirmation card (detail view)

**UX-critical invariant: every field below renders from `payload_jsonb` (frozen at proposal) — never from chat text, an agent restatement, or a live entity read.** The one exception is clearly-separated *context* chrome (§3).

| Region | Content |
|---|---|
| What changes | Entity (name + identifier), field, **old value → new value** as an explicit diff — the exact frozen values the mechanism will apply |
| Who proposed it | `proposed_by_kind` + resolved reference (operator name, or "Assistant session" linking to the session narrative for audit) |
| When / until | Proposed time; expiry countdown |
| Decision actions | **Confirm** (primary) and **Reject** (secondary) |

- Confirm uses the repo's ConfirmDialog convention (name the outcome): button label states the action ("Apply change →"), body restates the diff. Not destructive styling — unless the registered `action_type` is itself destructive, in which case destructive styling and the inline-confirmation convention apply (ui-decisions Sprint 8).
- Reject: optional reason field (recommended, not required — mechanism §4); rejection is recorded with the verified principal like any decision.
- An ordinary authenticated session suffices — **no step-up** (workspace blast radius, approval-security §1). The contrast with C12's step-up is deliberate and should stay visible: operators learn "statutory = re-authenticate, workspace = normal confirm."

## 3. Live-state context (separated from the frozen payload)

Below the frozen card, a visually distinct **"Current state"** strip may show the target's live value with a caption ("live read — the proposal above was made against: {snapshot}"). If live state differs from `target_state_snapshot_jsonb`, the UI warns pre-emptively ("this record has changed since the proposal — confirming will likely invalidate") — but the *guarantee* is the mechanism's execution-time re-check (§3.4 layer 2), not this hint. The strip exists so the eager-invalidation window (consumer lag) never surprises the operator; it must never be visually mergeable with the frozen payload.

## 4. Terminal-state presentation (all four, mechanism §2)

| State | Presentation |
|---|---|
| **EXECUTED** | Success state with `decided_by`/`decided_at` and outcome linkage (`outcome_detail_jsonb` rows written) — link to the affected record and its audit entry |
| **REJECTED** | Rejected badge, decider, reason if given |
| **EXPIRED** | "Expired {date} — never executed." CTA: none (re-proposing is the proposer's move; a new proposal references the expired one). Copy must make "nothing happened" unambiguous |
| **INVALIDATED** | The mechanism's required message: **"The underlying record changed since this was proposed"** — with **both states shown**: the proposal-time snapshot and the conflicting state from `outcome_detail_jsonb`, side by side. Copy must make clear no change was applied |

Terminal records are immutable history; the detail view renders identically forever (it reads frozen columns only).

## 5. Double-submit and concurrency UX

- On Confirm, the button locks immediately (single-flight). The API's idempotent semantics (CAS; second submit returns the recorded outcome, HTTP 200 — mechanism §3.3) mean the UI's recovery rule is simple: **whatever terminal record comes back is rendered as the truth**, with an explanatory banner when it differs from what the operator just pressed ("This action had already been {decided/invalidated} — no second execution occurred").
- Two operators/tabs racing: the loser's screen resolves to the winner's recorded outcome by the same rule. No error state, no retry prompt — convergence, not conflict dialogs.
- A second proposal against the same target/action type is refused at creation by the mechanism (partial unique index, §3.2); if an agent surfaces that refusal in chat, the message links to the existing pending action rather than describing a failure.

## 6. Chat boundary (restated from the C3 design)

Chat may display a proposal card (status, from the frozen payload) but never a Confirm control (`assistant-boundary-experience.md` §5). The pending-actions surface is the only place a decision can be made — one place to decide, one record of deciding.

## 7. Notifications

Proposal created / decided / invalidated / expiring-soon fan out as notification pointers (severity INFO; expiring-soon WARNING). Pointers only — the decision lives here.
