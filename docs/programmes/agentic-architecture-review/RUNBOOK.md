# Runbook — Agentic Architecture Review Programme

## Roles

- **Controller:** reads programme/review state, opens the next eligible stage, invokes executor and critic, and advances or stops.
- **Primary executor:** performs the stage investigation from `CONTEXT.md` and produces findings, evidence, outputs and handoffs.
- **Independent critic:** reviews the completed stage against `CRITIC.md`; it does not silently rewrite the executor's conclusions.
- **Human reviewer:** resolves material decisions and approves the final Stage 13 roadmap and later programme phases.

## Continuous Phase 1 loop

1. Read `POLICY.md`, `state.md`, `review-state.md`, `WORKFLOW.md` and `decision-queue.md`.
2. Identify the current or next eligible stage.
3. Populate the stage `CONTEXT.md` from prior confirmed findings, decisions and handoffs if it is still a template.
4. Validate the context contains objective, binding inputs, scope, exclusions, outputs and completion criteria.
5. Run the primary executor.
6. Mark the stage `awaiting-critic`.
7. Run an independent critic using `CRITIC.md` and save its report under the stage `outputs/critic-review.md`.
8. Controller disposition:
   - `PASS + no blocking decision`: close the stage and continue.
   - `PASS + blocking decision`: mark `awaiting-human-decision` and stop.
   - `REVISE`: return named corrections to the executor, then re-run the critic.
   - `STOP`: record an exception and stop.
9. Carry non-blocking questions into `decision-queue.md` and the appropriate later-stage handoff.
10. Never begin Phase 2 automatically.

## Automatic progression requirements

The controller may close and advance a stage only when:

- every required output exists
- findings are confirmed, parked or rejected with no ambiguous drafts informing later stages
- confirmed findings meet the evidence standard
- binding prior decisions are preserved
- the critic returns `PASS`
- no blocking human decision remains
- writes remain inside authorised paths
- `review-state.md` and handoffs are consistent

## Human stop points

Stop for the human reviewer when:

- a product, risk, compliance or scope choice has more than one reasonable option and evidence cannot choose between them
- accepting residual risk is required
- a prior binding decision may need reversal
- programme policy or authorised paths must change
- the critic and executor materially disagree after one revision cycle
- Stage 13 final approval is ready
- Phase 2 or Phase 3 authorisation is requested

## Session independence (D-004)

Every loop iteration must be executable from repository state alone:

- Persist all resume-relevant state (stage status, findings disposition, handoffs, open questions, critic reports) to the state files **before** ending a session or closing a stage — never leave it only in conversation.
- Prefer a fresh session per stage or per critic pass; the loop must not assume the previous iteration's conversational context is available.
- If resuming a stage requires information that is not in the state files, treat that as a close-out defect of the previous iteration: strengthen the persisted state, do not patch over it from session memory.

## Approval permissions

Routine repository reads, searches and writes inside this programme folder are pre-authorised by programme policy. Production code, migrations, external programme records, roadmap/product adoption, destructive actions and phase changes always remain outside automatic execution.
