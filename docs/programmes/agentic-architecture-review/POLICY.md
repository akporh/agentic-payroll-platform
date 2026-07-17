# Policy — Agentic Architecture Review Programme

Fixed execution policy for the `agentic-architecture-review` programme. The executor and critic must not weaken it. Any change requires human approval and a programme decision.

## Autonomy mode

`decision-gated-continuous` (Phase 1) / `phase-gated` (Phases 2–3)

Phase 1 may progress continuously through review stages after an independent critic returns `PASS`, provided no blocking human decision or stop condition remains. Phases 2 and 3 may not begin without explicit human authorisation.

## Roles

- Primary executor: performs the stage review from `CONTEXT.md`.
- Independent critic: validates evidence, scope, completeness and decision classification under `CRITIC.md`.
- Controller: advances, revises or stops according to `RUNBOOK.md`.
- Human reviewer: resolves material decisions and approves Stage 13 and later phases.

## Executor/controller may

- Populate the next eligible stage `CONTEXT.md` from confirmed prior findings, decisions and handoffs.
- Investigate the currently eligible stage.
- Read repository evidence read-only.
- Write within `docs/programmes/agentic-architecture-review/` only.
- Record/promote findings under the binding evidence rules.
- Run the independent critic and apply named corrections.
- Close and advance a stage automatically after critic `PASS` when no blocking decision remains.
- Update `review-state.md`, `state.md` and `decision-queue.md` truthfully.

## Executor/controller may not

- Modify production code, migrations, configuration or data.
- Modify `docs/audit-program/`, `docs/ROADMAP.md`, `docs/product/`, `docs/sprints/**`, `docs/stories/**` or any path outside this programme until explicitly authorised in a later phase.
- Resolve a material product, risk, compliance or residual-risk choice without the human reviewer.
- Begin Phase 2 or Phase 3.
- Treat critic `PASS` as final Stage 13 roadmap approval.
- Weaken `_core/` standards, alter this policy or expand authorised paths.
- Modify user-home skills or add dependencies.

## Human approval required for

- material product, risk, compliance, scope or residual-risk decisions where evidence does not determine one answer
- reversal of a binding prior decision
- policy, programme-scope or authorised-path changes
- unresolved executor/critic disagreement after one correction cycle
- final Stage 13 roadmap approval
- authorisation of Phases 2 and 3
- conflicts in Phase 2 that evidence cannot resolve

Routine stage transitions do not require approval.

## Stop conditions

Stop and record an exception when:

- authoritative sources materially contradict one another and further investigation cannot resolve it
- required evidence cannot be accessed
- a required write falls outside authorised paths
- a destructive or irreversible change would be required
- sensitive/personal information is discovered
- a genuine blocking human decision exists
- the critic returns `STOP`

Routine naming, formatting, context population, evidence collection, documentation updates and forwarded implementation specifications are not stop conditions.

## Source-of-truth boundaries

- `review-state.md`: stage-level state
- `state.md`: phase-level state and current programme gate
- `decision-queue.md`: unresolved decision/specification/evidence queue
- `_core/HUMAN-DECISIONS.md`: review-internal material decisions and final approval records
- `decisions.md`: programme-level decisions
- `outputs/critic-review.md` in each stage: independent gate-quality record
- `docs/audit-program/audit-state.md`: read-only audit truth
- `docs/product/`: writable only under a Phase 3 grant

These boundaries may only be changed by explicit human approval.
