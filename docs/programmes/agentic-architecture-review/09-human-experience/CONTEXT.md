# Stage 09: Human Experience — Context

## Status

closed (2026-07-17 — independent critic **PASS**, `outputs/critic-review.md`; three non-blocking corrections RC-1–3 applied by the controller pre-closure; zero blocking human decisions; automatic closure per D-003)

## Objective

Design the operator-facing experience for the approved 15-capability portfolio at the **surface/flow/IA level** (not visual design, which belongs to Phase 3 sprints under the repo's standing `/ux-designer`→`/ui-designer` workflow): the exception queue and its resolution workflow, the notification surface, the C3 chat boundary UX (including the five pre-specified refusal conditions), the C10 confirmation component, the C12 approval experience, the C13/C14 onboarding mapping + dry-run flow, auth/session/workspace-switch/step-up surfaces, and audit-history presentation (including pre-epoch identity labelling). Stage 08's mechanisms fix what the surfaces render and what actions exist; this stage designs how a human operator experiences them coherently.

## Binding decisions inherited from Stage 03 (pre-scope — do not re-litigate)

Recorded 2026-07-12, full detail in `_core/HUMAN-DECISIONS.md` HD-6 (D-03-01) and `03-agent-portfolio/outputs/portfolio-boundary-map.md` §3/§7:

- The revised 15-capability portfolio is **approved** — UX work should design for these 15 capabilities and their approved dispositions, not the source document's original tracks/agents.
- **Condition 5**: C3 (Operator Assistant) launches current-state only and must explicitly refuse historical-outcome questions — this stage should design the actual refusal UX/copy for that boundary (5 refusal conditions are pre-specified in `portfolio-boundary-map.md` §3: missing facts, historical-reconstruction request, cross-workspace request, ambiguous tool result, null trace).
- Chat is the approved primary surface for exactly one capability (C3); every other retained capability has a recommended non-chat surface already proposed in `portfolio-boundary-map.md` §7 (readiness panel, exception queue, evidence drawer, comparison view, approval panel, configuration-mapping workspace) — this stage should design those surfaces, not default to chat.
- Two missing-handoff UX gaps were identified and forwarded here: the exception queue's resolution workflow (C7 — dismiss/correct/escalate, undefined) and ensuring C11→C12's compliance handoff reads as one coherent workflow to the operator even though they are separate backend capabilities.

## Binding decisions inherited from Stages 04–08 (pre-scope — do not re-litigate)

- **Stage 04** (`04-outcome-discovery/outputs/stage-09-handoff.md`): the exception-resolution workflow is the primary UX design task — one shared interface for three exception sources; single accountable owner designed-in; evidence shown alongside every exception; AI-suggested next actions visually distinct from verified facts. C3 must not be measured or designed to maximise chat volume; C13 should surface per-field mapping confidence.
- **Stage 08** (`08-technical-architecture/outputs/stage-09-handoff.md` — the primary mechanism input, items 1–8): auth/session surfaces (login with membership selection, switch-as-new-session, 8h expiry re-login, step-up modal with 5-minute freshness); mechanical pre-epoch `identity unverified` labelling on every audit surface; the exception queue over `exception_record`'s eight-stage lifecycle with resolution codes; C10 confirmation rendering **exclusively from the frozen `payload_jsonb`** with all terminal states presented; C12 approval showing the full §3 evidence set with step-up and mandatory rejection reasoning; the C13→C14 hash-gated flow (mapping review → dry-run results → commit gated on the dry run of exactly those rows); C7 flags arriving only as exception records; DQ-005 (CORRECTION run_type UI exposure) owned here with Stage 11.
- **Security/compliance constraints that bind UX choices**: confirmation is an authenticated UI action distinct from chat (T7/SG-10); the C12 surface is `PLATFORM_ADMIN`-only and platform-level (SG-12); refusals are uniform 404-style without existence disclosure (P5); no UI may present pre-epoch actors as verified (threat-model §6). Gate registers CG-1–15/SG-1–15 are not restated here — nothing this stage designs may weaken one.
- **Standing repo rule**: `docs/design/ui-decisions.md` binds any Phase 3 frontend work; this stage's outputs must not contradict it (read it as an input).

## Confirmed platform facts to consume (do not re-verify)

- The Stage 08 mechanism designs (all 10 outputs, critic-passed) — schemas, state machines, and surfaces listed in its Stage 09 handoff.
- F-04-01 (exception workflow is the highest-leverage missing outcome), the eight-stage outcome definition, and the C7 outcome policy's operator framing ("decide in seconds whether it's real").
- Stage 05's UI-relevant facts: the existing frontend surface inventory (`frontend-backend-alignment.md`) — design against what exists, not a blank slate.

## Required inputs

Read: `README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`; all files under `_core/`; the two stage-09 handoffs (Stage 04, Stage 08); `03-agent-portfolio/outputs/portfolio-boundary-map.md` §§3/7; `04-outcome-discovery/outputs/exception-resolution-outcome.md` + `measurement-framework.md`; the Stage 08 mechanism designs as needed per surface; `05-platform-readiness/outputs/frontend-backend-alignment.md`; `docs/design/ui-decisions.md` (standing UI decisions log — binding); the existing frontend page inventory under `frontend/src/pages/` for grounding. Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. **Exception queue + resolution workflow**: the shared interface for C6/C7/(future C8) — queue IA, prioritisation display, ownership assignment, evidence presentation, the dismiss/correct/escalate resolution flow (Stage 03's forwarded gap), verification/closure states.
2. **Notification surface**: how `workspace_notification` reaches the operator (badge/inbox/banners), read-state behaviour, relationship to the exception queue (pointer vs duplicate — Stage 08 fixed notifications as pointers).
3. **C3 chat boundary UX**: refusal copy/patterns for the five pre-specified conditions; how tool-fact grounding is surfaced ("based on…"); how the UI avoids burying one-glance information behind chat.
4. **C10 confirmation component**: rendering of the frozen payload, terminal-state UX (executed/rejected/expired/invalidated), double-submit behaviour, where pending actions live in the IA.
5. **C12 approval experience**: proposal list/detail IA, evidence-set presentation (citation, diff, validation, impact preview), step-up moment, rejection-reasoning capture, correction proposals' consumed-runs statement — and the C11→C12 coherent-workflow question forwarded by Stage 03.
6. **C13/C14 onboarding flow**: mapping-proposal review with per-field confidence, dry-run results presentation (per-employee results + traces), the hash-gate re-run moment, integration with the existing Upload/Enroll separation (do not conflate — standing rule).
7. **Auth surfaces**: login/workspace selection, switch-as-context-change, session expiry, the step-up modal pattern.
8. **Audit-history presentation**: actor display (UUID→name), pre-epoch labelling, provenance labels for pre-C12 statutory rows.
9. **DQ-005**: recommend (with Stage 11) whether `run_type = CORRECTION` gets UI exposure — or explicitly re-forward with reasoning.

## Required outputs

Create under `outputs/`: `exception-queue-experience.md`, `notification-experience.md`, `assistant-boundary-experience.md` (C3), `confirmation-experience.md` (C10), `statutory-approval-experience.md` (C12, incl. C11→C12 coherence), `onboarding-flow-experience.md` (C13/C14), `auth-and-audit-surfaces.md` (Q7+Q8), `stage-10-handoff.md` (UX-testable behaviours), `stage-11-handoff.md` (surface-level scope/sequencing implications, DQ-005 recommendation). Update: `findings.md` (F-09-*), `decisions.md`, `review-state.md`, `decision-queue.md`, `_inputs/source-register.md` as required. (`outputs/critic-review.md` is the critic's.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` with the extended field pattern. Claims about the existing frontend must be verified against code (`frontend/src/`), not prior descriptions; committed evidence pinned to a named commit.

## Explicitly out of scope

- Visual/pixel design, component styling, design tokens (Phase 3 sprints under `/ui-designer`)
- implementing anything; changing any mechanism Stage 08 fixed (surfaces render mechanisms — mismatches go back as findings, not silent redesigns)
- evaluation methodology (Stage 10); commercial sequencing (Stage 11); roadmap (Stage 13)
- re-litigating closed decisions or weakening any CG/SG gate; starting Stage 10

## Constraints

- Read-only with respect to production code; writes stay inside `docs/programmes/agentic-architecture-review/`.
- Every experience design must name the mechanism (Stage 08 §) it renders and any UX-critical invariant it must preserve (e.g. render-from-frozen-payload).
- Do not create artificial human decisions; classify genuine choices per `CRITIC.md`.

## Completion criteria

Ready for the critic only when: every Q1–Q9 has a design answer or explicitly-classified open item; every output names its binding mechanism/gate references; Stage 10/11 handoffs are complete and consistent; decisions recorded and classified; non-blocking questions queued.

## Completion procedure (D-003 lifecycle)

1. Mark Stage 09 `awaiting-critic` in `review-state.md` and this file.
2. Independent critic per `CRITIC.md` → `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, close and open Stage 10 automatically per `RUNBOOK.md`.

## Next action

**None — stage closed. Stage 10 (Evaluation & Assurance) is open; see `10-evaluation-assurance/CONTEXT.md`.**
