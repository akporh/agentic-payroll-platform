# Stage 09 Output: Notification Experience (Q2)

Designs how `workspace_notification` reaches the operator. **Mechanism rendered**: the notification table and its pointer semantics (`08-technical-architecture/outputs/event-audit-foundation-design.md` §4 — "notifications are pointers to records, never the record of anything"; written by the C2 consumer from `NOTIFICATION` outbox rows; in-app only, C15 email deferred).

## 1. Surface: a TopBar bell, workspace-scoped

A **bell icon with unread count** in the existing TopBar (NAV-1: logo | workspace picker | user menu — evidence file §1), placed between the workspace picker and the user menu. Rationale: notifications are workspace-scoped rows (`workspace_id NOT NULL`), and the TopBar is the one persistent chrome element across every workspace page; a sidebar entry would bury an attention signal below the fold on collapsed sidebars.

- Unread count = rows for the active workspace with `read_at IS NULL`, capped 99+ (existing badge convention).
- Clicking opens a **dropdown panel** (most recent first): severity badge (INFO/WARNING/CRITICAL — color + text per ui-decisions), `message`, relative time, and the linked entity as the click target.
- Panel footer: **Mark all read** and a **View all** link to a simple full-page list (same rows, filter by severity/read state) for history beyond the dropdown's recent window.

## 2. Read-state behaviour

- Clicking a notification navigates to its target **and** sets `read_at` (mutable by design — not audit-class, ordinary retention).
- Read rows render muted in the panel; they are never deleted by the UI (no delete affordance — the mechanism has none).
- **v1 constraint, stated**: `read_at` lives on the notification row, and `operator_id IS NULL` rows broadcast to all workspace operators — so one operator's read marks the row read for everyone. Acceptable for the current single-operator bureau reality (the same operational context as DQ-007); it becomes a real limitation the moment two operators share a workspace. Forwarded to Stage 11 as a multi-operator scope implication (`stage-11-handoff.md` §3) — **not** silently redesigned here, per the mismatches-go-back-as-findings rule; this is a known v1 posture, not a defect.

## 3. Pointer, not duplicate (the Stage 08 fixed relationship)

**UX-critical invariant: the panel offers navigation only.** No resolve, dismiss, assign, confirm or approve action exists in the notification surface. Every notification is a pointer:

| `type` class | Click target |
|---|---|
| Exception created/updated (`exception_id` set) | The exception detail in the queue (`exception-queue-experience.md` §3) |
| Pending action proposed/decided/invalidated | The pending-action record (`confirmation-experience.md`) |
| Statutory proposal awaiting approval (platform-admin operators) | The C12 proposal detail (`statutory-approval-experience.md`) |
| Run lifecycle (calculated, reconciliation mismatch) | The run detail tab (existing `PayrollResults` surface) |

Rationale: the moment a notification can *do* something, it becomes a second working surface competing with the queue — the exact duplication Stage 08 closed by fixing notifications as pointers. Dismissing a notification must never be confusable with dismissing the underlying exception.

## 4. Relationship to page banners

CRITICAL conditions may additionally surface as an `AlertBanner` on the relevant page (existing pattern — e.g. the INACTIVE-with-live-contract banner). **Design rule**: banners derive from **live entity state** (the open exception, the run status), never from notification rows. Two sources of truth for one signal is the Sprint 23 stale-selection lesson generalised: the notification row is delivery history; the entity is the truth. A read notification therefore never suppresses a banner, and a banner never marks anything read.

## 5. What is deliberately absent in v1

- No notification preferences/muting (single operator; no volume evidence yet — calibrate after C7 shadow mode produces real volume data).
- No toast/push interruptions: exceptions arrive through the C2 consumer asynchronously; the bell count updating on poll (the existing `MainLayout` badge-refresh pattern) is sufficient. Interruptive delivery is an escalation decision that should follow evidence of missed-critical incidents, not precede it.
- No email (C15 deferred — the mechanism's own boundary).
