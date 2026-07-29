# Product Hierarchy — `docs/product/`

The durable product-traceability layer for the Agentic Payroll Platform. It exists to answer, at any time, without relying on a single person's memory:

- What outcomes are we pursuing?
- Which capabilities support them, and which features belong to those capabilities?
- Which stories make up each feature — *by name*, not just by count?
- Which have been delivered, in which sprint, with what evidence?
- Given an old sprint code, which story is that now?
- How much of what we've built is actually recorded here?

## Which file answers what

| File | Answers |
|---|---|
| `OUTCOMES.md` | The five durable business results the platform exists to deliver |
| `CAPABILITIES.md` | The twelve lasting product areas, each serving one outcome |
| `FEATURES.md` | The 41 features — **and which stories each one contains** |
| `STORY-REGISTRY.md` | Every story with a **full record** (all 157) |
| `ID-ALLOCATION.md` | Every **known item** (157) with a reserved ID and feature assignment — the coverage map |
| `SOURCE-INDEX.md` | **Reverse lookup**: given a legacy code or source file, which story is it? |
| `stories/` | One file per migrated story |
| `validate_registry.py` | Consistency checks across all of the above |

**`ID-ALLOCATION.md` vs `STORY-REGISTRY.md`** — the first answers *"what exists?"*, the second *"what is recorded?"* The gap between them was the migration backlog. **As of 2026-07-29 (D-027) that gap is zero: 157 of 157.** Both files are kept, because they answer different questions and will diverge again the moment a new item is allocated ahead of being written up.

## Status

Approved as a complete hierarchy on **2026-07-28** (D-023), defined top-down across the whole inventory.

Before that, the hierarchy was built bottom-up: the Phase 4A pilot (D-015, 2 stories) and the Phase 4B confirmed batch (D-016, 19 stories from capability area A1+A2) each created only the rows needed to hold their own stories, so `OUT-3`, `CAP-3` and `FEAT-3`/`4`/`5` existed because 19 Onboarding stories needed a home. Nobody had seen the intended shape. Phase 3B (D-022) closed that gap.

**Migration is complete as of 2026-07-29 (D-027, Phase 4D): 157 of 157.** All four Phase 4 batches have run — 4A (2 stories), 4B (19), 4C (33, the whole Execution Engine) and 4D (the remaining 103, in one batch). Phase 4 is closed and there is no further migration authorisation to give.

**What that changes for a reader.** While the registry was partial, an absent story meant either "not yet migrated" or "no such work" and you could not tell which. Now it means the second. Treat a gap here as evidence, and if you find delivered work with no story, that is a defect in this layer — capture it rather than assume it was excluded.

**What can still make this wrong.** The discovery inventory behind these 157 items has a **2026-07-15 horizon**, and three sprints were already found missing from it (D-024, D-026). Work delivered after that date registers here only if someone captures it at migration time. Wiring traceability into sprint closure is Phase 5 and is **not yet authorised** — until it is, the completeness above decays with every sprint that closes.

Adding a new item: allocate the next free `STORY-<nnnn>` in `ID-ALLOCATION.md` (never renumber, never reuse), add the registry row and story file, extend `SOURCE-INDEX.md`, and run `python3 docs/product/validate_registry.py`.

## Story identifiers (D-019, D-020)

`STORY-<nnnn>`. **The identifier encodes nothing** — no programme name, no capability area, no feature, no sprint, no date.

That is deliberate. The predecessor scheme, `PT-<area>-<nn>`, encoded the `product-traceability` programme's own name and a position in a one-off retro inventory — two temporary things baked into a permanent identifier. More fundamentally, this hierarchy allows a story's feature assignment to be revised, so any ID encoding a relationship eventually becomes a lie. Readability comes from `title` and the display-name columns; chronology from `sprint_refs` and `ID-ALLOCATION.md`'s section headings, which sort.

Allocation:

1. The seed pass ran **once**, in chronological delivery order, across all known items.
2. Forward allocation is **strictly sequential on entry**, regardless of date.
3. **Never renumber, never reuse.** A later-discovered historical item takes a high number despite being early — correct, and harmless; the date fields carry the truth.
4. A merge or split (human approval required) **retires** an ID rather than reusing it.
5. Every legacy code lives in the mandatory **`origin_code`** field. `grep -r PT-A1-22 docs/product/` finds `STORY-0102`.

*The 21 stories migrated under D-015/D-016 were re-keyed once, on 2026-07-28, under D-020 — an explicit, recorded, one-time exception. The rule above binds absolutely from that point forward.*

## Acceptance criteria (D-018)

Ownership depends on how a story came into existence:

- **Retro-migrated** — the authoritative criteria stay in the original sprint story file. The record here summarises and links; it does not duplicate. The source is closed and frozen, so two copies would only drift.
- **Forward-authored** — the criteria live **here**, authoritatively, because there is no prior file to point at.

A retro record is therefore deliberately not standalone-complete; a forward record is. `STORY-REGISTRY.md`'s `ac_owner` column states which applies, per story.

*This resolves a genuine contradiction: `POLICY.md` stated "Story records own story definition and authoritative acceptance criteria" without naming which story records, which read as contradicting D-009's pointer-only rule.*

## Reference paths

```text
Written from stories/STORY-0102-….md:

  ../FEATURES.md                  ✔  inside docs/product/  → relative
  docs/stories/sprint-17-…​.md     ✔  outside               → repo-root-relative
  ../../stories/sprint-17-…​.md    �’  outside via ../..     → never
  /Users/…/docs/stories/…​.md      ✗  absolute              → never
```

| Reference | Style | Why |
|---|---|---|
| Within `docs/product/` | Relative | Survives moving the whole tree; short and readable |
| Outside `docs/product/` | Repo-root-relative | A `../../` chain is unreadable, ungreppable, and breaks whenever a file moves *within* `docs/product/` — the opposite failure. Matches every other programme's convention. |
| Absolute, or `~/` | Never | Machine-specific |

The residual risk — relocating `docs/product/` itself — is handled by `validate_registry.py`'s link-existence check, which fails loudly so the fix is one mechanical pass. There is precedent: the architecture-review programme was moved to `docs/programmes/` on 2026-07-15 and left stale citations behind.

## Structure (Model A — flat registries, D-008)

```text
docs/product/
├── README.md
├── OUTCOMES.md
├── CAPABILITIES.md
├── FEATURES.md
├── STORY-REGISTRY.md
├── ID-ALLOCATION.md
├── SOURCE-INDEX.md
├── stories/
│   ├── TEMPLATE.md
│   └── STORY-<nnnn>-<slug>.md
└── validate_registry.py
```

Relationships are held as stable-ID columns, not nested folders. A story's ID never changes even if its feature assignment is later revised.

## Source-of-truth rules (D-009, amended by D-018)

- **This hierarchy** owns long-lived intent, outcome/capability/feature relationships, and cumulative story status. It does **not** own execution-stage state (that stays in `../sprints/<sprint>/state.md`).
- Acceptance criteria: per the retro/forward split above.
- **`../ROADMAP.md` continues to serve forward planning and open backlog.** This hierarchy is a historical and current-state record, not a replacement planning surface.
- Nothing in `../ROADMAP.md`, `../stories/`, `../sprints/`, `../audit/`, `../audit-program/`, `../programmes/agentic-architecture-review/`, `../security/`, `../test-reports/` or `../retro-reports/` is ever rewritten to make this hierarchy appear to have existed earlier than it did. This is why `SOURCE-INDEX.md` exists rather than back-references written into old story files.

## Validation

`validate_registry.py` is dependency-free (standard library only). Run after any manual edit:

```bash
python3 docs/product/validate_registry.py
```

It checks: story-file ↔ registry-row correspondence both ways; every parent ID resolves; every display name matches its parent's current name; no duplicate or ambiguous IDs; **`origin_code` present on every story**; **`FEATURES.md`'s `stories` column round-trips against `STORY-REGISTRY.md`'s `feature_id`**; **no live `PT-*` identifier survives outside an `origin_code`**; **every referenced path exists on disk**; every migrated story appears in `SOURCE-INDEX.md`.

## Governing programme

A controlled output of `../programmes/product-traceability/`. See `PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `hierarchy-proposal.md`, the `critic-review*` files and `runs/`.
