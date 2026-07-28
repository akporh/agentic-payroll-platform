# Stage 09 Output: Exception Queue Experience (Q1)

Designs the shared operator interface over the exception workflow — Stage 04's highest-leverage missing outcome (F-04-01). **Mechanism rendered**: `exception_record` and its state machine (`08-technical-architecture/outputs/event-audit-foundation-design.md` §6); C7 flag lifecycle (`anomaly-detection-design.md` §4). **Binding workflow content**: the eight-stage outcome definition (`04-outcome-discovery/outputs/exception-resolution-outcome.md`). Surface/flow/IA level only — visual design is Phase 3 (`/ux-designer` → `/ui-designer` per standing workflow); nothing here overrides `docs/design/ui-decisions.md`.

## 1. Placement in the IA

A new workspace-sidebar entry **Exceptions**, in the Payroll section alongside Inputs and Runs, using the existing numeric-badge pattern (`Navigation.tsx:238/244`, 99+ cap — evidence file §1). One entry serves all three sources (C6 readiness, C7 anomalies, future C8 reconciliation) — Stage 04's "one workflow, not three" is an IA rule here, not just a schema rule: an operator has exactly one place to look for "things needing my attention," regardless of which capability flagged them.

- **Badge count** = open, non-terminal exceptions (`OPEN` + `ASSIGNED`), **excluding shadow-mode records** (`anomaly-detection-design.md` §4 — shadow records are excluded from operator-facing counts; UX-critical invariant).
- Pending actions (C10) are deliberately **not** in this queue — an exception is a *problem to resolve*; a pending action is a *proposal to decide*. Different mental models, different urgency semantics, separate entries (see `confirmation-experience.md` §1). Both may generate notifications; neither duplicates the other.

## 2. Queue view (list IA)

One list, filterable, defaulting to actionable work:

| Element | Content (all from `exception_record` columns) |
|---|---|
| Row identity | `exception_type` as plain language ("Anomalous overtime input", "Missing timesheet"), the affected entity (employee name via UUID→name display join — records store UUIDs), period |
| Source chip | `source` rendered as a typed chip: Readiness / Anomaly / Reconciliation — color + text per the status-badge convention (ui-decisions: never color alone) |
| Severity | `severity` badge (CRITICAL / WARNING / INFO) |
| Urgency signal | Cutoff proximity ("3 days to pay cutoff") computed from evidence fields where present (`evidence_jsonb` carries period context; Stage 08 assigns prioritisation display to this stage) |
| Owner | Owner's display name, or an explicit **Unassigned** state — visually prominent, because unowned exceptions are the "everyone's queue, no one's queue" failure mode Stage 04 names |
| Status | Lifecycle badge (Open / Assigned / Resolved / Verified / Closed) |

- **Sort (deterministic, no composite score)**: severity desc → cutoff proximity asc → `created_at` asc. The operator sees *named* signals (a severity badge and a days-to-cutoff figure), never an opaque priority number — an invented composite score would be a conclusion the evidence doesn't state, violating the facts-not-conclusions discipline.
- **Filters**: My exceptions / Unassigned / All open / Closed (history). Default: All open. A **Show shadow records** toggle (off by default) reveals C7 shadow-mode rows, each carrying an explicit "shadow — calibration only" marker; they never count toward badges or open-queue totals.
- **Empty state** per ui-decisions DD-5: icon + "No open exceptions" + no CTA (exceptions are system-created; there is nothing for the operator to add — the empty queue is the *good* state and should read as such).

## 3. Detail view (the resolution workspace)

Opens as a full detail panel (SlideOver for read/resolve — single-step per ui-decisions; the correction itself happens elsewhere, §4). Mapping the eight outcome stages to interface regions:

1. **Header**: type, entity, severity, source chip, status, created date. Ownership control: **Assign to me** (primary when unassigned) / reassign select (memberships list). Exactly one owner at any time — the UI never offers multi-assign.
2. **Evidence panel** — renders `evidence_jsonb` as labelled verified facts. For a C7 anomaly, exactly the fields the detector froze: entered value, history series, median, ratio, threshold row/version fired, layer(s), detector version (`anomaly-detection-design.md` §4) — e.g. "400 entered; 3-period median 42 (9.5×); absolute ceiling 100." Facts are presented as data, never paraphrased prose. **UX-critical invariant**: the evidence panel renders only frozen `evidence_jsonb` content — never a live re-query (the record must show what fired, even after the data is corrected).
3. **Suggested next step** — `recommended_action`, when present, in a **visually distinct container explicitly labelled as a suggestion** ("Suggested next step — generated from the facts above"), never interleaved with the evidence facts. This is the Stage 04 binding rule: an operator must never confuse "the system suggests X" with "the system confirmed X." If `recommended_action` is null, the region is absent (no filler text).
4. **Resolution actions** — mapped 1:1 to Stage 08's resolution codes; the operator picks what actually happened, in their own terms:

| Action label | Resolution code | Flow |
|---|---|---|
| **Data was wrong — I corrected it** | `CONFIRMED_ERROR_CORRECTED` | Links out to the owning data surface (the Inputs page for a C7 flag, the Timesheet page for a missing timesheet) — the exception record never edits data itself. On return, the operator records the resolution; verification is then automatic (§5) |
| **Data is correct — dismiss** | `CONFIRMED_CORRECT_DISMISSED` | Inline confirm step that re-shows the evidence summary before confirming ("Dismissing confirms this value is correct: 400 vs. median 42") — a deliberate friction point against the dismiss-without-review reflex the measurement framework tracks as an early-warning signal. Short-circuits to `CLOSED` (nothing to verify) |
| **Escalate** | `ESCALATED` | Required note naming who/what it goes to (v1: free text — there is no in-app recipient model yet; single-operator reality per DQ-007 context) |

  `resolution_note` optional on all three except escalation. Every transition writes its domain-3 audit row mechanically (facade) — the UI adds no separate "log this" step.

## 4. Correction happens at the source, verification closes the loop

The queue is a router to corrections, not a correction editor. Rationale: every data type an exception can point at already has an owning surface with its own validation, audit and locking rules (Inputs, Timesheet, Employees); duplicating edit capability inside the queue would create a second write path to financially load-bearing data. The **Correct** flow: deep-link with return context ("Back to exception") → operator edits on the owning surface → returns → records the resolution.

## 5. Verification and closure states

- `RESOLVED → VERIFIED` is the automatic re-check (`event-audit-foundation-design.md` §6 — e.g. the value no longer flags on re-evaluation, the timesheet now exists). The UI presents it as a system state, not an operator task: a "Verifying…" indicator on the resolved record, becoming **Verified** with the re-check timestamp, or flipping back to a visible **Re-check failed — still flagging** state that returns the exception to the owner's attention (it stays in their filtered view; the record itself stays `RESOLVED` with the failed re-check noted — no invented extra status).
- `CLOSED` records are permanent history (append-only discipline): the Closed filter shows full lifecycle timelines (created → assigned → resolved → verified → closed, with actors and timestamps from the audit rows). This history view is the substrate for the future recurring-error reporting outcome (product-opportunity area 15) — designed as a list now, no reporting UI in v1.

## 6. Relationship to notifications

Exception creation fans out a `workspace_notification` pointer (severity-matched). Notifications navigate here; they carry no resolution capability (`notification-experience.md` §3). The queue is the single working surface.

## 7. What this design must not do (gate/constraint check)

- No exception is ever presented chat-first — C7 flags arrive only as exception records (Stage 08 handoff item 7); C3 may *reference* an open exception in an answer but always links to this queue.
- Nothing here weakens CG/SG gates: the queue reads workspace-scoped data through authenticated routes (C1 dependency chain); no cross-workspace visibility exists in any view; evidence rendering introduces no PII beyond what the operator's workspace session already authorises.
- No new statuses, codes or lifecycle steps beyond Stage 08's — mismatches, if found in build, go back as findings, not silent UI-side extensions.
