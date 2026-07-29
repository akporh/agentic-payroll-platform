# Decisions — `roadmap-split`

Append-only log, per `docs/sprints/WORKFLOW.md`'s Recording HITL Decisions schema. One entry per human decision, in the order made.

```yaml
- id: DEC-roadmap-split-01
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Authorises the roadmap relabelling work deferred under D-021
    (docs/programmes/product-traceability/decisions.md). D-021's stated
    precondition — "after the traceability layer is established" — is met:
    Phase 5 closed 2026-07-29 with docs/product/ at 157/157 and traceability
    wired into sprint closure. D-021 also states that any such relabelling
    "requires its own separate authorisation outside this programme,"
    because POLICY.md forbids the product-traceability programme from
    modifying docs/ROADMAP.md at all. This entry is that authorisation.
    The work is scoped as an ordinary docs-only sprint, not a programme —
    it is a single bounded change, not a phased effort with gates.
  reference: Direct chat instruction, 2026-07-29 ("we wanted to work on the
    roadmap clean up after PT ... the inconsistent roadmap issue"), followed
    by explicit scope confirmation ("yes, write the decision first then go
    ahead confirm scope").

- id: DEC-roadmap-split-02
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    The two jobs docs/ROADMAP.md currently performs — historical record of
    delivered work, and forward plan — are separated into two files. The
    HISTORICAL RECORD keeps the existing path, docs/ROADMAP.md, frozen in
    place with an added banner and no content altered. Forward planning moves
    to a new docs/PLAN.md.

    Decisive reason for this direction rather than the reverse (history moved
    out, ROADMAP.md kept as the forward file): 46 rows in
    docs/product/STORY-REGISTRY.md cite docs/ROADMAP.md as an evidence
    source, and for 10 of them (Sprint 0, and Sprints 1-6, which predate the
    per-sprint test-report convention) it is the ONLY source — SOURCE-INDEX.md
    states this explicitly. Freezing in place means zero citations move and
    zero can break.

    The reverse direction was considered and rejected on a specific hazard:
    validate_registry.py:275-287 checks that a cited path EXISTS, not that it
    still contains what was cited. Had history been moved to a new file while
    docs/ROADMAP.md survived as a forward-planning document, the validator
    would have passed while all 46 citations silently pointed at a file no
    longer holding the evidence — routing around the exact check written to
    prevent citation rot.
  reference: AskUserQuestion answer, 2026-07-29, "Which file keeps the name
    ROADMAP.md?" -> "The diary keeps it".

- id: DEC-roadmap-split-03
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    The single consistent labelling scheme applies to NEW forward items only.
    No historical item code is rewritten anywhere — every legacy code
    (A1-A10, Track A-Y, P0/P1/P2, FIX-*, PH-*, GAP-*, WI-*, M*, S*, Q*,
    TM-*, EMP-*, SPRINT-A-*, RULE-VER-* and the rest of the 25+ prefixes)
    survives verbatim, and is preserved as origin_code on the corresponding
    story. This is a direct restatement of D-021's own ruling ("Old item
    codes are never rewritten") and of its rationale: a retrospective
    relabel would break citations across docs/product/, docs/audit-program/,
    docs/programmes/agentic-architecture-review/, and every sprint story
    file and test report simultaneously.
  reference: AskUserQuestion answer, 2026-07-29, "Does the labelling scheme
    apply to old items too?" -> "New items only".

- id: DEC-roadmap-split-04
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Resolves the sprint's OQ-2. STORY-0161 corrects two stale
    programme-state statements, one of which (docs/product/ID-ALLOCATION.md's
    "Phase 5 ... is not yet authorised") sits inside the
    product-traceability programme's owned tree. That programme is in steady
    state, under which "adding stories is routine sprint work needing no
    decision" but changing the SHAPE of the tree still requires a programme
    phase. A staleness correction is neither: it adds no story and changes no
    shape, so it falls outside both rules. Recorded here explicitly rather
    than assumed, so the edit is authorised before it is made and not
    back-filled afterwards. Scope of the correction is limited to making the
    two statements factually true as of 2026-07-29; no other content in
    either file changes.
  reference: Scope confirmation, 2026-07-29 — STORY-0161 was presented with
    this open question attached and the scope was confirmed as presented.

- id: DEC-roadmap-split-05
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: pm
  decision_type: activate
  reason: >
    Scope increase, accepted mid-sprint and recorded as such rather than
    folded in silently. STORY-0176 is added: a traceability-drift detector
    that flags code commits carrying no story_ref.

    Prompted by the question "what happens if ad-hoc items come in and I
    don't call /pm?" The honest answer was: nothing catches it at the time.
    /pm allocating early is a convenience; the only enforcement is /retro's
    Close Gate, which fires solely if a sprint is formally closed. Work done
    without a workspace, or a workspace never closed, is invisible. This is
    not hypothetical — D-026 records three sprints found missing from the
    inventory after its 2026-07-15 horizon, and dev-levy-rule-pct's own
    state.md records `roadmap` and `pm` being run retroactively.

    Why it became urgent in THIS sprint specifically: STORY-0160 strengthened
    ID-ALLOCATION.md's claim to "an item absent from this table is an item no
    known evidence records," and extended it to forward work. That claim is
    only as true as the last sprint that closed properly. Un-tracked ad-hoc
    work no longer merely goes unrecorded — it makes the file assert
    something false. A silent wrong answer is worse than the honest gap it
    replaced, so this sprint created the exposure and should close it.

    Detect, do not gate. Three options were put up; blocking the push was
    explicitly rejected on the grounds that the first emergency fix would be
    pushed with --no-verify and the gate would become decoration. The
    detector warns loudly and exits 0.
  reference: Direct chat instruction, 2026-07-29 ("yes add option 2 to scope,
    then finish the sprint"), answering an explicitly-flagged scope-increase
    question.

- id: DEC-roadmap-split-06
  date: 2026-07-29
  decision_owner: Claude (implementation-stage design call, recorded for review)
  stage: implementation
  decision_type: activate
  reason: >
    The drift detector ships as a SEPARATE script,
    docs/product/check_traceability_drift.py, rather than as a new check
    inside validate_registry.py. validate_registry.py asserts one thing —
    that docs/product/ is internally consistent — and it is deterministic:
    same files in, same answer out. Reading git state would make its result
    depend on branch position and upstream configuration, so a PASS would
    no longer mean what it means today, and the existing 46-citation
    guarantee would become entangled with unrelated VCS state. Two scripts,
    two claims, two independent failure modes.
  reference: No human decision required; recorded because it departs from
    the "extend validate_registry.py" wording in the option as presented,
    and a reader comparing DEC-05 to the shipped code would otherwise see
    an undocumented divergence.

- id: DEC-roadmap-split-07
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: architecture
  decision_type: not-applicable
  reason: >
    architecture recorded not-applicable for this sprint. Docs and doc-tooling only. No data contract, enum, status field, migration, shared type or cross-service boundary is touched.

    Compensating control for all five not-applicable stages: this sprint's
    evidence is mechanical rather than review-based — validate_registry.py
    (bidirectional consistency across five registry files), a git-level
    additions-only proof on the frozen file, and the drift detector
    exercised against real commit history. See state.md's `test` stage.
  reference: Scope confirmation 2026-07-29, which accepted the stage-
    applicability table in CONTEXT.md as presented. Split into one entry per
    stage after the retro Close Gate (lint_sprint_state.py E064) rejected a
    single bundled ruling — a decision's `stage` field must name the stage
    that cites it.

- id: DEC-roadmap-split-08
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: arch-council
  decision_type: not-applicable
  reason: >
    arch-council recorded not-applicable for this sprint. None of the global CLAUDE.md mandatory triggers fire: no status/state/enum field, no DB constraint, no API response field meaning, no migration, no cross-workspace endpoint, no shared type or service contract. The one structural change this sprint makes to a governed tree — adding FEAT-42 — went instead through the product-traceability programme's own phase-plus-decision rule (Phase 6, D-030).

    Compensating control for all five not-applicable stages: this sprint's
    evidence is mechanical rather than review-based — validate_registry.py
    (bidirectional consistency across five registry files), a git-level
    additions-only proof on the frozen file, and the drift detector
    exercised against real commit history. See state.md's `test` stage.
  reference: Scope confirmation 2026-07-29, which accepted the stage-
    applicability table in CONTEXT.md as presented. Split into one entry per
    stage after the retro Close Gate (lint_sprint_state.py E064) rejected a
    single bundled ruling — a decision's `stage` field must name the stage
    that cites it.

- id: DEC-roadmap-split-09
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: verification
  decision_type: not-applicable
  reason: >
    verification recorded not-applicable for this sprint. No API-to-frontend boundary is touched; there is no running behaviour to observe.

    Compensating control for all five not-applicable stages: this sprint's
    evidence is mechanical rather than review-based — validate_registry.py
    (bidirectional consistency across five registry files), a git-level
    additions-only proof on the frozen file, and the drift detector
    exercised against real commit history. See state.md's `test` stage.
  reference: Scope confirmation 2026-07-29, which accepted the stage-
    applicability table in CONTEXT.md as presented. Split into one entry per
    stage after the retro Close Gate (lint_sprint_state.py E064) rejected a
    single bundled ruling — a decision's `stage` field must name the stage
    that cites it.

- id: DEC-roadmap-split-10
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: security
  decision_type: not-applicable
  reason: >
    security recorded not-applicable for this sprint. No route, input handler, auth flow or sensitive-data path touched. The one script added reads git metadata and repo files and accepts no external input.

    Compensating control for all five not-applicable stages: this sprint's
    evidence is mechanical rather than review-based — validate_registry.py
    (bidirectional consistency across five registry files), a git-level
    additions-only proof on the frozen file, and the drift detector
    exercised against real commit history. See state.md's `test` stage.
  reference: Scope confirmation 2026-07-29, which accepted the stage-
    applicability table in CONTEXT.md as presented. Split into one entry per
    stage after the retro Close Gate (lint_sprint_state.py E064) rejected a
    single bundled ruling — a decision's `stage` field must name the stage
    that cites it.

- id: DEC-roadmap-split-11
  date: 2026-07-29
  decision_owner: Michael Emedo
  stage: audit
  decision_type: not-applicable
  reason: >
    audit recorded not-applicable for this sprint. No calculation, statutory rule, or monetary path touched.

    Compensating control for all five not-applicable stages: this sprint's
    evidence is mechanical rather than review-based — validate_registry.py
    (bidirectional consistency across five registry files), a git-level
    additions-only proof on the frozen file, and the drift detector
    exercised against real commit history. See state.md's `test` stage.
  reference: Scope confirmation 2026-07-29, which accepted the stage-
    applicability table in CONTEXT.md as presented. Split into one entry per
    stage after the retro Close Gate (lint_sprint_state.py E064) rejected a
    single bundled ruling — a decision's `stage` field must name the stage
    that cites it.
```

## Reading this file

- DEC-01 through DEC-04 were all recorded **before** any file in scope was touched. This is deliberate: `feedback_governance_before_execution` records that the previous session hit back-filled authorisation twice (D-028, D-029), and D-021's own rationale is that the roadmap's problem arose precisely from decisions becoming permanent by default rather than by choice.
- This sprint deliberately does **not** open a programme. D-021's follow-up says "scope a separate piece of work," and the work is a single bounded change with one human gate (scope confirmation) — a programme's phase/gate machinery would be heavier than the change warrants.
