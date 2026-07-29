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
- ~~Create the final `docs/product/` structure.~~ **Superseded 2026-07-15 by Phase 3 / D-014**, which authorised exactly this, scope-limited to `docs/product/`. Retained here as history, not as a live prohibition. The live constraint is the per-phase `allowed paths` list in `PHASES.md`.
- Classify tentative items as confirmed without evidence.
- Merge or split historical stories as a final decision.
- Re-key, renumber or reuse a story identifier without an explicit recorded decision (added 2026-07-28 under D-022; the one-time re-key of the 21 Phase 4A/4B stories is authorised by D-020 and by nothing else).
- Modify user-home skills (`~/.claude/**`).
- Add dependencies (no `requirements.txt`, `package.json`, or lockfile changes).
- Expand the authorised file scope beyond what `PHASES.md` grants the active phase.
- Write a free-form next-run prompt.
- Execute a later phase.
- Treat its own recommendation as human approval.

## Human approval required for

- The hierarchy terminology and model (e.g. Outcome→Epic→Feature→Story vs. Outcome→Capability→Feature→Story vs. hybrid).
- The repository information architecture (Model A vs. Model B vs. an alternative).
- **The story identifier scheme** — its format, what it does and does not encode, and the allocation rules. Added 2026-07-28 under D-022. *Why this was added:* this item was absent from the list, so the discovery document's deliberately **provisional** `PT-*` identifiers were carried into `docs/product/` by Phase 4A/4B and became permanent by default rather than by decision, despite `STORY-REGISTRY.md` itself flagging re-keying as a pending human choice. An identifier scheme is a long-lived, expensive-to-change commitment and is now an explicit human gate. Current scheme: `STORY-<nnnn>`, fixed by D-019.
- **The complete outcome/capability/feature set** — not merely the model, but the actual populated hierarchy, approved as a whole rather than accreted batch by batch. Added 2026-07-28 under D-022 (see D-017).
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
- Story records own story definition and acceptance criteria — **with the retro/forward split fixed by D-018 (2026-07-28)**:
  - **Retro-migrated stories** (already delivered before this programme existed): the *sprint* story file under `docs/stories/` or `docs/sprints/` holds the authoritative acceptance criteria. The product-hierarchy record summarises and links to it; it does **not** duplicate the criteria. This is D-009's rule, unchanged.
  - **Forward-authored stories** (written into the product hierarchy by the PM, with no pre-existing sprint story file): the **product-hierarchy story record** holds the acceptance criteria natively and authoritatively — **and is written by `pm`, at scope confirmation, not by `retro` at close (D-031, 2026-07-29).** `pm` populates the intent fields (actor, problem, intended behaviour, acceptance criteria, out of scope, priority, parent IDs, dependencies, source and decision references) with `status: backlog`; `retro` populates the evidence fields (implementation, test/review, confidence, delivery sprint), flips status and appends the delivery-history line. Sprint `CONTEXT.md` cites `STORY-<nnnn>` and **links** to the record for criteria; it does not restate them.
  - *Amendment note (D-031):* the forward branch previously left the record to `retro`, so `pm` wrote the criteria into `CONTEXT.md` and `retro` transcribed them. That transcription drifted on all five forward-authored stories produced under it — two in criterion count, one dropping a quantified figure — meaning `tester` verified one text while the registry published another with that evidence attached. D-018 had already identified this hazard for retro-migrated stories and fixed it there; the forward case carried the same hazard with both copies live. The retro-migrated branch above is unaffected.
  - *Amendment note:* this bullet previously read "Story records own story definition and authoritative acceptance criteria" without naming which story records, which reads as contradicting D-009 and caused a reviewer to reasonably expect acceptance criteria on migrated stories and find none. The ambiguity was unintentional; D-018 resolves it.
- Sprint `CONTEXT.md` owns selected execution scope for that sprint.
- Sprint `state.md` owns workflow-stage state.
- Sprint `decisions.md` owns HITL routing and skip decisions.
- Sprint evidence and stage outputs own delivery proof.
- Completed sprint history must not be rewritten to make the new model appear to have existed earlier.

This boundary list may only be changed by explicit human approval recorded in `decisions.md`.
