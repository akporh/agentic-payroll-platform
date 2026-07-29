# `STORY-0158` — Freeze `docs/ROADMAP.md` as the historical record

**Origin code(s):** — (forward-authored; this story has no legacy code)
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-11` — Programme Governance & Assurance
**Feature:** `FEAT-42` — Product record & roadmap structure
**Classification:** `discovery or architecture item`
**Status:** `delivered`
**Confidence:** `confirmed` — set at close by `/retro` from this sprint's own test report (`docs/test-reports/2026-07-29-roadmap-split.md`, PASS, 6 checks).

## Actor

maintainer of the product record

## Problem addressed

`docs/ROADMAP.md` performs two jobs that pull against each other: it is the historical record of delivered work (~98% of its 1011 lines, cited as evidence by 46 story records and as the *only* evidence by 10) and it is the forward plan (~20 open items scattered across 8 sections). Every edit to the plan mutates a file the record treats as fixed. Because the file grew by accretion it also runs three organising principles in sequence — capability area, then Track, then Sprint — carrying 25+ ID prefixes, several colliding.

This story is one of four executing the follow-up deferred under D-021, whose stated precondition (a traceability layer that owns delivered history) was met when Phase 5 closed on 2026-07-29.

## Delivered behaviour

Delivered 2026-07-29. See the sprint test report for the checks that verified it.

## Acceptance criteria

Forward-authored, so criteria live here natively (D-018):

- `docs/ROADMAP.md` carries a banner at the top stating it is a frozen historical record, the date it froze, and that forward planning lives in `docs/PLAN.md`.
- **No existing line of content is altered, reordered, or deleted.** Verified by `git diff` showing additions only.
- All 46 citations resolve unchanged — `python3 docs/product/validate_registry.py` passes.
- Open-item markers (`⬜`/`🔜`/`🔮`) remaining in the frozen file are annotated as carried to `PLAN.md` rather than removed, so the frozen file stays honest about what it froze mid-flight.
- Two markers that were already stale — `S7` and `Q1`, delivered by the ICM pilot sprints as `STORY-0146` and `STORY-0145` — are annotated as delivered rather than corrected in place, preserving the additions-only guarantee.

## Source reference

`D-021` — `docs/programmes/product-traceability/decisions.md`. Sprint scope and full context: `docs/sprints/roadmap-split/CONTEXT.md`.

## Implementation evidence

`docs/sprints/roadmap-split/` — `CONTEXT.md` (scope + AC), `decisions.md` (DEC-01–DEC-11), `state.md` (per-stage record).

## Test / review evidence

`docs/test-reports/2026-07-29-roadmap-split.md` — **PASS**, 6 checks. `architecture`, `arch-council`, `verification`, `security` and `audit` were `not-applicable` (DEC-07–DEC-11); the compensating control is mechanical evidence in place of review.

## Decision references

- `D-021` — deferred the roadmap relabelling until the traceability layer existed.
- `roadmap-split` `DEC-01` — authorises this work outside the product-traceability programme, which is forbidden from touching `docs/ROADMAP.md`.
- `roadmap-split` `DEC-02` — `docs/ROADMAP.md` keeps its path and freezes in place; `docs/PLAN.md` is new.
- `roadmap-split` `DEC-03` — the labelling scheme applies to new items only.
- `D-030` — authorises Phase 6, adding `FEAT-42` to hold these four stories.

## Dependencies

`STORY-0160` resolves before `STORY-0159` can print `story_ref`s into `PLAN.md`. `STORY-0158` and `STORY-0161` are independent.

## Delivery sprint(s)

`roadmap-split` (opened 2026-07-29).

## Delivery history

- 2026-07-29 — scoped, allocated, delivered and closed in the `roadmap-split` sprint.

## Unresolved questions

None open. The four decisions above were all recorded before any in-scope file was written.
