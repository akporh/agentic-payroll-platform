# Sprint — `roadmap-split`

**Status:** scope confirmed 2026-07-29 (DEC-01 through DEC-04, recorded before any in-scope file was touched). **Scope increased mid-sprint** by DEC-05 — `STORY-0176` added.
**Role:** Executes the follow-up D-021 deferred — retiring `docs/ROADMAP.md`'s dual role now that the traceability layer exists to own delivered history. Docs and doc-tooling only — no application code, migration, data contract or UI. `STORY-0176` (added mid-sprint) touches `.githooks/pre-push` and adds one script under `docs/product/`; neither is on a runtime path.

---

## Goal

`docs/ROADMAP.md` stops being two documents at once.

It currently performs two jobs that pull against each other:

1. **Historical record** — what was built, sprint by sprint, and whether it worked. Roughly 98% of the file's 1011 lines. Must never change: 46 rows in `docs/product/STORY-REGISTRY.md` cite it as evidence, and for 10 of them it is the only evidence they have.
2. **Forward plan** — what has not been built. About 20 items scattered across 8 disconnected sections between lines 56 and 799, plus the wholly-forward Phase 2 (Agent Layer) and Phase 3 (Platform Scale) sections. Must change: that is what a plan is for.

Every edit to job 2 mutates a file 46 story records treat as fixed. And because the file grew by accretion, job 1 was written three different ways at three different times — by capability area (Sprints 0–1b), by Track (Phase 1 Priority Order), then by Sprint with per-sprint Story Index (Sprint 14 onward) — carrying 25+ ID prefixes, several colliding (`B` denotes both Track B "Schema Foundations" and Sprint 17's Track B items; `P1`/`P2` serve as both item prefixes and phase names).

After this sprint: history is frozen at its current path, forward planning lives in `docs/PLAN.md` under one scheme, and every forward item carries a `STORY-<nnnn>`.

## Source item

`D-021` — `docs/programmes/product-traceability/decisions.md:198`. Its stated precondition ("after the traceability layer is established") was met 2026-07-29 when Phase 5 closed with `docs/product/` at 157/157. D-021 requires separate authorisation outside that programme, since `POLICY.md` forbids it from modifying `docs/ROADMAP.md` — that authorisation is `decisions.md` DEC-01 in this folder.

## PM decisions (Michael, 2026-07-29 — see `decisions.md` DEC-01 through DEC-04)

- **`docs/ROADMAP.md` keeps its path** and freezes in place as the historical record. Content unchanged; banner added. All 46 citations stay valid, nothing moves. (DEC-02)
- **`docs/PLAN.md` is new** and holds forward planning only. (DEC-02)
- **The labelling scheme applies to new items only.** No historical code is rewritten. (DEC-03)
- **The `ID-ALLOCATION.md` staleness fix is authorised** despite sitting in the product-traceability tree — it neither adds a story nor changes the hierarchy's shape, so neither steady-state rule covers it. (DEC-04)

## Scoping finding — forward coverage gap

`STORY-REGISTRY.md` holds exactly **6** `status: backlog` rows (`STORY-0150`–`0155`) against **20** open roadmap items. The Phase 4 migration captured *delivered* work exhaustively and open work only incidentally. So roughly **14 open items have no `STORY-<nnnn>` at all**.

This matters because `ID-ALLOCATION.md` claims a specific property — "an item absent from this table is an item no known evidence records." That property holds for delivered work and quietly does not hold for forward work. `STORY-0160` closes it.

## In-scope stories

### STORY-0158 — Freeze `docs/ROADMAP.md` as the historical record (P2)

> As the maintainer of the product record, I want the roadmap's delivered history closed and marked as closed, so that the 46 story records citing it rest on something that cannot silently change underneath them.

**Acceptance criteria**
- `docs/ROADMAP.md` carries a banner at the top stating it is a frozen historical record, the date it froze, and that forward planning lives in `docs/PLAN.md`.
- **No existing line of content is altered, reordered, or deleted.** Verified by `git diff` showing additions only.
- All 46 citations resolve unchanged — `python docs/product/validate_registry.py` passes.
- Open-item markers (`⬜`/`🔜`/`🔮`) remaining in the frozen file are annotated as carried to `PLAN.md` rather than removed, so the frozen file stays internally honest about what it froze mid-flight.

### STORY-0159 — Create `docs/PLAN.md` with one labelling scheme (P2)

> As Michael planning the next sprint, I want a single short document listing only what isn't built, so that I can see the forward position without reading 1011 lines of history.

**Acceptance criteria**
- `docs/PLAN.md` exists and contains **only** not-yet-delivered work: the 20 open items, plus Phase 2 (Agent Layer, Tracks P/V/W/X/Y) and Phase 3 (Platform Scale).
- A stated labelling scheme for new items, with the rule written into the file's own header so the next person adding an item cannot guess wrong.
- Every carried item shows its **original code verbatim** (`S6`, `Q3`, `N1`, `O5`, `PH-12`, `EMP-REG-5-FIX` …). No historical code is rewritten.
- No delivered work appears in `PLAN.md`; no open work is left reachable only from `ROADMAP.md`.

### STORY-0160 — Reconcile open items against the story registry (P2)

> As the owner of the traceability layer, I want every forward item to carry a `STORY-<nnnn>`, so that "absent from the registry means it doesn't exist" is true for planned work and not just for delivered work.

**Acceptance criteria**
- Each of the 20 open items either matches an existing backlog row (`STORY-0150`–`0155`) or receives a newly allocated ID.
- Every `PLAN.md` entry shows its `story_ref`.
- New rows are written `status: backlog`, `confidence: requires human classification` — matching the D-027 precedent exactly, never as delivered.
- `validate_registry.py` passes; `ID-ALLOCATION.md` and `STORY-REGISTRY.md` report the same count.

### STORY-0176 — Traceability drift detector (P2 — added mid-sprint, DEC-05)

> As an engineer, I want to be told when I'm about to push code that carries no `story_ref`, so that ad-hoc work cannot silently make the registry's completeness claim false.

Added after a scoping question exposed a real hole: `/pm` allocating an ID is a convenience, and the only enforcement is `/retro`'s Close Gate, which fires solely when a sprint is formally closed. Work with no workspace — or a workspace never closed — is invisible. D-026 already records three sprints lost this way.

`STORY-0160` is what made it urgent: it strengthened `ID-ALLOCATION.md`'s claim to cover forward work, so untracked work now makes the file *assert something false* rather than merely omit something.

**Acceptance criteria**
- `docs/product/check_traceability_drift.py` flags to-be-pushed commits touching `backend/`, `frontend/src/` or `migrations/versions/` with no `STORY-<nnnn>`.
- Not flagged: a `STORY-<nnnn>` in the commit message, or an active sprint declaring `story_refs`. Docs-only, test-only and `frontend/public/` changes are ignored.
- **Never blocks.** Exits 0 unconditionally; the hook calls it with `|| true`.
- Degrades silently when no sensible commit range exists.
- Wired into `.githooks/pre-push`.

### STORY-0161 — Clear the two stale programme-state statements (P3)

> As anyone orienting from the docs, I want programme state to say what is actually true, so that I don't plan against a phase that closed a week ago.

**Acceptance criteria**
- `docs/programmes/README.md`'s product-traceability register row reflects Phase 5 closed / steady state (it currently reads "Phase 4 … remainder not authorised").
- `docs/product/ID-ALLOCATION.md`'s "Phase 5 … is not yet authorised" statement is corrected.
- No other content in either file changes.

## Out of scope

- **Relabelling any historical item.** D-021 deferred this and argued against it; DEC-03 keeps it deferred.
- **Renaming or moving `docs/ROADMAP.md`.** Explicitly decided against in DEC-02 — it keeps its path so the 46 citations hold.
- **Re-pointing any of the 46 citations.** Nothing moves, so nothing needs re-pointing.
- **Classifying the confidence of newly created backlog rows.** They enter as `requires human classification`; deciding them is separate work.
- **Re-prioritising, re-scoping, or deciding the fate of any open item.** This sprint moves items and gives them IDs. It does not judge them.
- **`docs/Buisness Specs & Designs (Drifted)/`** (stale since 11 June; two untracked `.mmd` files), the **local DB drift**, and `docs/ux-ui-design-brief/11-drift-log.md`. All separate open items.
- **Arch-review Stage 13 (DP-2, DP-9).** Untouched — still the longest-open decision.
- **Attributing individual commits to individual stories.** `STORY-0176` closes the "no sprint at all" hole; ad-hoc work *during* an open sprint is still suppressed. Tightening it needs a commit-message convention that does not exist yet — recorded as a known limitation, not solved.

## Stage applicability

Docs-only, so most gates are not applicable rather than skipped by choice:

| Stage | Applies | Why |
|---|---|---|
| `roadmap`, `pm` | yes | done this session |
| `architecture`, `arch-council` | **no** | no data contract, enum, migration, shared type or service boundary touched |
| `implementation` | yes | five stories |
| `verification` | **no** | no API-to-frontend boundary; nothing to run |
| `security` | **no** | no route, no input handler |
| `audit` | **no** | no calculation, no statutory rule |
| `test` | yes | `validate_registry.py`, the `git diff` additions-only proof, and the drift detector exercised against real history |
| `retro` | yes | mandatory |
