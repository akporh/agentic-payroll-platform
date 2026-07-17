# Phase 3 Inputs — Product Traceability Programme

Factual parameters only, compiled at the close of Phase 2 (`hierarchy approval`) for the human's future Phase 3 authorisation decision. This file does not authorise Phase 3, does not redefine policy, does not weaken stop conditions, and does not contain a free-form continuation prompt. It exists so that when the human decides to authorise Phase 3, the scope is already factually specified rather than invented at that moment.

---

**Proposed Phase 3 ID:** `structure-implementation`

**Approved hierarchy (from D-008, `decisions.md`):**

```text
Outcome → Capability → Feature → Story
```

Where Capability is a durable product construct (roughly matching `docs/ROADMAP.md`'s A1–A10 areas) and Epic (a delivery construct — sprint/track bundles) is retained as a secondary tag on stories/features rather than a separate hierarchy level, per the hybrid framing in Section 6 of the discovery document.

**Approved repository model (from D-008):** Model A — flat registries plus a flat `stories/` folder:

```text
docs/product/
├── README.md
├── OUTCOMES.md
├── CAPABILITIES.md
├── FEATURES.md
├── STORY-REGISTRY.md
└── stories/
    └── <story-id>.md
```

**Approved source-of-truth rules (from D-009, adopting Section 10 of the discovery document as written):**

- The product hierarchy (`docs/product/`) owns long-lived intent, outcome/capability/feature relationships, and cumulative story status. It does not own execution-stage state (stays in `docs/sprints/<sprint>/state.md`) or acceptance-criteria authorship for stories still in flight (stays in the sprint's own story file until the sprint closes).
- A story's authoritative acceptance criteria live in exactly one place at a time: pre-delivery, in the sprint's story file; post-delivery, the product hierarchy's story record summarises but links to, rather than duplicates, the original story file or sprint workspace as the evidence source.
- `docs/ROADMAP.md` continues to serve forward planning and open backlog (🔜/⬜/🔮 items) — the product hierarchy is a historical/current-state record of delivered and in-flight status, not a replacement planning surface.

**Proposed allowed path (not granted):**

```text
docs/product/   (new tree only)
```

**Proposed outputs (not authorised to be created yet):**

- Empty hierarchy/registry scaffold matching the structure above (no historical story content — that is Phase 4).
- A short `README.md` explaining the registry files and how they relate to `docs/ROADMAP.md` and `docs/stories/`.
- A validation script or documented manual check confirming every `STORY-REGISTRY.md` row has a corresponding file in `stories/` and vice versa (per the discovery document's Section 9 "automated validation" criterion).

**Proposed forbidden paths:**

```text
backend/
frontend/
migrations/
docs/ROADMAP.md
docs/stories/          (existing files — read-only input, never rewritten)
docs/sprints/
docs/audit/
docs/audit-program/
docs/agentic-architecture-review/
docs/security/
docs/test-reports/
docs/retro-reports/
~/.claude/
```

**Proposed validation commands:**

```bash
git diff --check
git status --short
find docs/product -type f | sort
# confirm every STORY-REGISTRY.md row resolves to a file in docs/product/stories/, and vice versa
```

**Unresolved Phase 3 authorisation decision:** whether and when to authorise Phase 3 to begin. This is a distinct decision from D-007–D-013 above and has not been made. No Phase 3 work — including creation of `docs/product/` — may begin until it is.
