# Test Report — `roadmap-split`

**Date:** 2026-07-29
**Sprint:** `roadmap-split` (`docs/sprints/roadmap-split/`)
**Stories:** `STORY-0158`, `STORY-0159`, `STORY-0160`, `STORY-0161`, `STORY-0176`
**Verdict:** **PASS** — 6 checks green, 0 failed.

This sprint changes documentation and one doc-tooling script. It touches no application code, so the meaningful evidence is registry consistency and a proof that the frozen file was not altered — not runtime behaviour. `pytest` and `tsc` are reported to demonstrate *absence* of change, not to demonstrate the sprint worked.

---

## T1 — Registry consistency

```
$ python3 docs/product/validate_registry.py
PASS — docs/product/ registries are internally consistent (235 total content row(s) checked).
```

Covers, in both directions: every `feature_id` in `STORY-REGISTRY.md` exists in `FEATURES.md` **and** that feature's `stories` column lists the story back; every cited path exists on disk; every registry row has a story file and every story file has a row; no live `PT-*` identifier survives outside `origin_code`; every story appears in `SOURCE-INDEX.md`.

**AC covered:** `STORY-0160` (validator passes), `STORY-0158` (46 citations still resolve).

## T2 — Freeze guarantee: additions only

```
$ git diff --numstat docs/ROADMAP.md
50	0	docs/ROADMAP.md
```

**50 insertions, 0 deletions.** This is the load-bearing check of the sprint: 46 registry rows cite `docs/ROADMAP.md` as evidence and 10 have no other source, so any altered line would silently invalidate an evidence claim.

Proved twice, independently: a `difflib` comparison inside the editing script reported 0 removed-or-altered pre-existing lines, and `git` — which never saw that script — agrees.

**AC covered:** `STORY-0158` ("no existing line altered, reordered or deleted").

## T3 — Drift detector, against real history

Exercised against actual repository commits, not a fixture:

| Case | Expected | Result |
|---|---|---|
| `38e9323` — `frontend/src/.../Navigation.tsx`, no story ref | flagged | **flagged** ✓ |
| `frontend/public/architecture-audit.html` in that same commit | ignored | **ignored** ✓ |
| `40c33cd..818de2b` — docs-only range | silent | **silent** ✓ |
| Active sprint declaring `story_refs` | suppressed | **suppressed** ✓ |
| Exit code, every case | `0` (never blocks) | **0** ✓ |

**AC covered:** `STORY-0176`, all five criteria.

## T4 — Counts agree across the tree

| Source | Count |
|---|---|
| `STORY-REGISTRY.md` rows | 176 |
| `ID-ALLOCATION.md` rows | 176 |
| `docs/product/stories/*.md` | 176 (177 on disk; `TEMPLATE.md` is not a story) |

Up from 157. **+14** forward items previously carrying no identifier (`STORY-0162`–`0175`), **+5** sprint stories (`STORY-0158`–`0161`, `STORY-0176`).

**AC covered:** `STORY-0160` ("ID-ALLOCATION and STORY-REGISTRY report the same count").

## T5 — Backend suite (regression, expect no change)

```
$ python3.10 -m pytest -q
327 passed, 1 skipped, 48 warnings in 5.94s
```

Unchanged from the pre-sprint baseline, as expected. Confirms no behavioural change reached the engine.

> **Note for `CLAUDE.md`:** that file states the suite is "306 passed, 1 intentional Phase-2 skip". The true figure is **327 passed, 1 skipped**, confirmed here. Stale, not dangerous — raised in the retro, not fixed in this sprint (out of scope).

## T6 — Frontend typecheck

```
$ cd frontend && npx tsc --noEmit
(clean)
```

## T7 — Sprint workspace lint

```
$ python3 scripts/lint_sprint_state.py
PASS — roadmap-split
  stages checked : 10   decisions checked : 11
```

Found 2 real defects on first run and both were fixed before close — see *Not covered* and the retro.

---

## Not covered by machine

**The item-by-item mapping from `ROADMAP.md` to `PLAN.md` was done by reading, not by a script.** Nothing mechanically proves that every open item reached `PLAN.md` and that none was dropped or duplicated. The validator checks that references *resolve*; it cannot check that a judgement about which items were open was correct.

This is the residual risk in the sprint. Two mitigations, neither a substitute for a checker:

- Both stale markers found during the sweep (`S7`, `Q1` — delivered but still shown open) are annotated in the frozen file and reconciled in `PLAN.md`, which is evidence the sweep was done attentively rather than mechanically.
- `ROADMAP.md` is frozen, so the source set cannot drift underneath the mapping. Any omission is recoverable by re-reading a file that will never change.

**Two `evidence:` values in `state.md` are not path-shaped** and therefore rest on this report rather than on a durable artefact of their own: the `git diff --numstat` output (T2) and the drift-detector runs (T3). Both are reproducible by re-running the commands quoted above.
