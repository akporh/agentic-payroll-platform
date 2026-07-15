# Policy — Product Traceability Programme

This is the fixed execution policy for the `product-traceability` programme. The executor must not weaken it. Any change to this file requires human approval and is itself a consequential decision under `decisions.md`.

## Autonomy mode

`phase-autonomous-with-exception-escalation`

The executor may complete the entire authorised phase without requesting intermediate confirmation, but may not authorise its own continuation into a later phase, and must stop immediately on any defined stop condition.

## Executor may

- Inspect repository evidence (source code, migrations, tests, docs) read-only.
- Read git history.
- Create programme-control and discovery documents under the approved paths (see `PHASES.md`).
- Create provisional classifications with explicit confidence levels.
- Run read-only searches and validation commands.
- Correct formatting and mechanical defects within the approved files.
- Commit and push authorised discovery-phase outputs.
- Continue through the discovery phase without intermediate confirmation.

## Executor may not

- Modify production code (`backend/`, `frontend/src/`, `migrations/`, etc.).
- Modify frontend or backend application code of any kind.
- Modify existing sprint history (`docs/sprints/**`, `docs/stories/**`, `docs/test-reports/**`, `docs/audit/**`, `docs/retro-reports/**`, `docs/security/**`).
- Modify `docs/ROADMAP.md`.
- Modify existing historical story files.
- Create the final `docs/product/` structure.
- Classify tentative items as confirmed without evidence.
- Merge or split historical stories as a final decision.
- Modify user-home skills (`~/.claude/**`).
- Add dependencies (no `requirements.txt`, `package.json`, or lockfile changes).
- Expand the authorised file scope beyond what `PHASES.md` grants the active phase.
- Write a free-form next-run prompt.
- Execute a later phase.
- Treat its own recommendation as human approval.

## Human approval required for

- The hierarchy terminology and model (e.g. Outcome→Epic→Feature→Story vs. Outcome→Capability→Feature→Story vs. hybrid).
- The repository information architecture (Model A vs. Model B vs. an alternative).
- Source-of-truth changes (any change to the ownership model fixed in `PROGRAMME.md`/this prompt).
- Ambiguous story classification (any item the executor could not classify even provisionally, or classified as `requires human classification`).
- Merges or splits of historical stories.
- Migration scope (what gets reconstructed into the new structure, and in what order).
- Any production-code or user-home-skill changes.
- Authorisation to begin the next phase.

## Stop conditions

Stop and record an exception in `exceptions.md` only when:

- Authoritative sources materially contradict one another (e.g. `docs/ROADMAP.md` marks an item ✅ but no corresponding test or code evidence can be found, and the contradiction cannot be resolved by reading further).
- Sensitive or personal information is discovered.
- The phase cannot be completed within the authorised paths.
- A destructive or irreversible change would be required.
- The requested evidence cannot be accessed.
- More than 10% of identified items cannot be classified even provisionally.
- Validation fails and cannot be corrected within scope.

Routine naming, formatting, evidence collection, and provisional classification questions are **not** stop conditions — the executor proceeds and records confidence levels instead of stopping.

## Source-of-truth boundaries (fixed for this programme)

- Product hierarchy owns long-lived intent, relationships and status.
- Story records own story definition and authoritative acceptance criteria.
- Sprint `CONTEXT.md` owns selected execution scope for that sprint.
- Sprint `state.md` owns workflow-stage state.
- Sprint `decisions.md` owns HITL routing and skip decisions.
- Sprint evidence and stage outputs own delivery proof.
- Completed sprint history must not be rewritten to make the new model appear to have existed earlier.

This boundary list may only be changed by explicit human approval recorded in `decisions.md`.
