# `STORY-0176` — Traceability drift detector — warn when code ships with no `story_ref`

**Origin code(s):** — (forward-authored; this story has no legacy code)
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-11` — Programme Governance & Assurance
**Feature:** `FEAT-42` — Product record & roadmap structure
**Classification:** `technical enabler`
**Status:** `in-flight`
**Confidence:** `requires human classification` — set at close by `/retro`.

## Actor

engineer

## Problem addressed

`docs/product/ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records. `STORY-0160` extended that claim to forward work. The claim is only as true as the last sprint that closed properly.

The sprint workflow's only enforcement point is `/retro`'s Close Gate, which hard-stops on an unresolved `story_ref` — but it fires solely when a sprint is formally closed. Work done with no sprint workspace, or in a workspace never closed, is invisible to it. `/pm` allocating an ID early is a convenience, not a control.

This is not hypothetical. D-026 records three sprints found missing from the inventory after its 2026-07-15 horizon, and `dev-levy-rule-pct`'s own `state.md` records `roadmap` and `pm` being run retroactively after the work began.

The consequence changed with this sprint. Before, untracked work merely went unrecorded. Now it makes the registry **assert something false** — and a silent wrong answer is worse than the honest gap it replaced.

## Delivered behaviour

In flight — completed by `/retro` at sprint close.

## Acceptance criteria

- `docs/product/check_traceability_drift.py` exists and, given the commits about to be pushed, flags any that touch `backend/`, `frontend/src/` or `migrations/versions/` while carrying no `STORY-<nnnn>`.
- Attributable work is not flagged: a `STORY-<nnnn>` in the commit message, or an active sprint whose `state.md` declares `story_refs`.
- Docs-only, test-only and `frontend/public/` commits are not flagged — a warning that fires on noise trains the reader to ignore it.
- **It never blocks.** `main()` returns 0 unconditionally, and the pre-push hook calls it with `|| true` so `set -e` cannot promote a warning into a failed push.
- It degrades silently when no sensible commit range exists (a fresh branch with no remote counterpart) rather than flagging all of history.
- Wired into `.githooks/pre-push` after the existing pytest and `tsc` gates.

## Source reference

`docs/sprints/roadmap-split/CONTEXT.md`; decision `roadmap-split` `DEC-05`.

## Implementation evidence

`docs/product/check_traceability_drift.py`; `.githooks/pre-push`.

## Test / review evidence

To be completed by `/retro`. Verified this session against real history: commit `38e9323` (`frontend/src/design-system/components/Navigation.tsx`, no story ref) is flagged; the `frontend/public/` file in the same commit is correctly excluded; a docs-only range is silent; an active sprint with `story_refs` suppresses.

## Decision references

- `roadmap-split` `DEC-05` — authorises the scope increase; detect, do not gate. Blocking was explicitly rejected: the first emergency fix would be pushed with `--no-verify`, after which the gate is decoration.
- `roadmap-split` `DEC-06` — ships as a separate script rather than inside `validate_registry.py`, so that validator's deterministic "internally consistent" claim does not become entangled with git state.

## Dependencies

`STORY-0160` — this protects the property that story established.

## Delivery sprint(s)

`roadmap-split` (opened 2026-07-29).

## Delivery history

- 2026-07-29 — added mid-sprint as an accepted scope increase (`DEC-05`).

## Unresolved questions

**Known limitation, accepted not solved.** An active sprint declaring any `story_refs` suppresses *all* warnings for the push. So ad-hoc work done *during* an open sprint — the `dev-levy-rule-pct` pattern, where a reconciliation query turned into unplanned code — is still invisible. Tightening this means attributing individual commits to individual stories, which needs a commit-message convention that does not exist yet. The detector closes the "no sprint at all" hole, which is the larger one; the in-sprint hole remains open and is deliberately recorded here rather than left for someone to discover.
