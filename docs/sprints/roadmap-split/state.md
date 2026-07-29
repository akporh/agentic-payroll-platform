# State — `roadmap-split`

Authoritative per-stage status, per `WORKFLOW.md`. Stage IDs and dependency shapes are drawn from `STAGE-REGISTRY.md`. Mutated in place — `decisions.md` is the append-only log.

```yaml
sprint: roadmap-split
status: complete

stages:
  roadmap:
    status: complete
    note: >
      Orientation done at session start from the handoff note and D-021.
      This sprint's source item is D-021 itself
      (docs/programmes/product-traceability/decisions.md:198), whose stated
      precondition — "after the traceability layer is established" — was met
      2026-07-29 when Phase 5 closed with docs/product/ at 157/157.
      Note the recursion: this sprint's source item lives in a programme
      decision log rather than in docs/ROADMAP.md, which is itself an
      instance of the problem being fixed.

  pm:
    status: complete
    evidence: CONTEXT.md, decisions.md DEC-01 through DEC-04
    story_refs: [STORY-0158, STORY-0159, STORY-0160, STORY-0161, STORY-0176]
    note: >
      Scope + AC drafted; four decisions recorded BEFORE any in-scope file
      was touched (DEC-01 authorisation, DEC-02 which file keeps the path,
      DEC-03 new-items-only labelling, DEC-04 the ID-ALLOCATION.md staleness
      ruling that resolves the sprint's OQ-2). Human gate — explicit scope
      confirmation — satisfied 2026-07-29 ("yes, write the decision first
      then go ahead confirm scope"). Scoping surfaced one finding that
      became STORY-0160: only 6 of 20 open roadmap items have a STORY id,
      so ID-ALLOCATION.md's "absent means non-existent" property holds for
      delivered work but not for forward work.

  architecture:
    status: not-applicable
    reason: >
      Docs and doc-tooling only. No data contract, enum, status field, migration, shared type or cross-service boundary is touched.
    decision_owner: Michael Emedo
    decision_ref: DEC-roadmap-split-07
    date: 2026-07-29
    compensating_control: >
      validate_registry.py enforces consistency across five registry files in both directions; the frozen file is proved unaltered at git level.
    note: >
      Docs-only. No data contract, enum, status field, migration, shared
      type or cross-service boundary is touched.

  arch-council:
    status: not-applicable
    reason: >
      None of the global CLAUDE.md mandatory triggers fire: no status/state/enum field, no DB constraint, no API response field meaning, no migration, no cross-workspace endpoint, no shared type or service contract.
    decision_owner: Michael Emedo
    decision_ref: DEC-roadmap-split-08
    date: 2026-07-29
    compensating_control: >
      The one structural change this sprint makes to a governed tree — adding FEAT-42 — went through the product-traceability programme's own phase-plus-decision rule (Phase 6, D-030) rather than through arch-council.
    note: >
      Same reason as architecture. None of the global CLAUDE.md mandatory
      triggers fire: no status/state/enum field, no DB constraint, no API
      response field meaning, no migration, no cross-workspace endpoint,
      no shared type or service contract.

  implementation:
    status: complete
    depends_on: [architecture, arch-council]
    evidence: docs/PLAN.md, docs/ROADMAP.md (banner + annotations),
      docs/product/ (5 files, 19 story files), docs/product/check_traceability_drift.py,
      .githooks/pre-push, docs/programmes/README.md
    note: >
      Both dependencies terminal (not-applicable). Five stories. STORY-0160
      resolved first so STORY-0159 could print story_refs into PLAN.md;
      STORY-0158 and STORY-0161 independent; STORY-0176 added mid-sprint
      under DEC-05. Also fixed while wiring the hook: the pre-push script's
      `cd frontend && npx tsc` left the shell in frontend/ for anything
      appended after it — now a subshell, so the drift check runs from repo
      root. Pre-existing latent bug, not introduced here.

  verification:
    status: not-applicable
    reason: >
      No API-to-frontend boundary is touched; there is no running behaviour to observe.
    decision_owner: Michael Emedo
    decision_ref: DEC-roadmap-split-09
    date: 2026-07-29
    compensating_control: >
      Mechanical evidence replaces live observation: validator PASS, additions-only git proof, and the drift detector exercised against real commit history rather than a fixture.
    note: >
      No API-to-frontend boundary is touched; there is no running behaviour
      to observe. The equivalent evidence for this sprint is the
      validate_registry.py run recorded under `test`.

  security:
    status: not-applicable
    reason: >
      No route, input handler, auth flow or sensitive-data path touched. The one script added reads git metadata and repo files; it accepts no external input.
    decision_owner: Michael Emedo
    decision_ref: DEC-roadmap-split-10
    date: 2026-07-29
    compensating_control: >
      The script never executes untrusted input and cannot fail a push by construction (exits 0 unconditionally; hook calls it with || true).
    note: No route, input handler, auth flow or sensitive-data path touched.

  audit:
    status: not-applicable
    reason: >
      No calculation, statutory rule, or monetary path touched.
    decision_owner: Michael Emedo
    decision_ref: DEC-roadmap-split-11
    date: 2026-07-29
    compensating_control: >
      pytest 327 passed / 1 skipped confirms no behavioural change reached the engine.
    note: No calculation, statutory rule, or monetary path touched.

  test:
    status: complete
    depends_on: [implementation]
    evidence: docs/test-reports/2026-07-29-roadmap-split.md
    note: >
      PASS — 6 checks, all green.
      T1 validate_registry.py PASS, 235 content rows — proves the 46
      ROADMAP.md citations still resolve and the 19 new rows are well-formed
      in both directions (registry<->FEATURES<->SOURCE-INDEX).
      T2 git diff --numstat docs/ROADMAP.md = "50 0" — 50 insertions, ZERO
      deletions. This is the freeze guarantee, proved by git independently of
      the script that made the edit; a difflib check inside that script
      agreed (0 removed/altered lines).
      T3 drift detector exercised against REAL history, not a fixture:
      commit 38e9323 (frontend/src/.../Navigation.tsx, no story ref) is
      correctly FLAGGED; the frontend/public/ file in that same commit is
      correctly IGNORED; a docs-only range is silent; an active sprint with
      story_refs suppresses. Exit code 0 in every case.
      T4 counts agree: 176 registry rows = 176 ID-ALLOCATION rows = 176 story
      files (177 on disk, of which TEMPLATE.md is not a story).
      T5 pytest 327 passed / 1 skipped / 0 failed — unchanged, as expected
      for a sprint that touches no application code.
      T6 tsc --noEmit clean.
      NOT verified by machine: that every open roadmap item reached PLAN.md
      and none was dropped. That mapping was done by reading, and is the
      residual risk in this sprint — see the retro.

  retro:
    status: complete
    depends_on: [test]
    evidence: docs/test-reports/2026-07-29-roadmap-split.md; this file; decisions.md
    note: >
      Close Gate run first and it FAILED twice before passing — both real
      defects in this sprint's own records, both fixed before close.
      Part A / lint_sprint_state.py E034: the five not-applicable stages
      carried prose notes but none of the four required decision fields
      (reason, decision_owner, decision_ref, date) and cited no decision at
      all. Fixed by recording the rulings properly.
      Then E064: the first fix pointed all five stages at ONE bundled
      decision, which the linter rejected — a decision's `stage` field must
      name the single stage that cites it. Split into DEC-07..DEC-11.
      Part D: the `test` stage was marked complete citing state.md itself,
      with no docs/test-reports/ file. "No application code changed" is not
      an exemption from the artefact. Written as
      docs/test-reports/2026-07-29-roadmap-split.md.
      Part C: all five story_refs completed to delivered/confirmed with real
      evidence paths; validator PASS at 235 rows.
      3 lessons captured, each closed with a concrete skill/workflow update.
```

## Reading this file

- Six of the ten stages are `not-applicable` rather than `skipped`. This is a docs-only sprint — the gates were never eligible, as opposed to being judged unnecessary. `CONTEXT.md`'s stage-applicability table gives the per-stage reason.
- `test` here does not mean pytest. The suite is unaffected by this sprint (no code changes), so the meaningful evidence is the registry validator plus an additions-only diff proof on the frozen file.
