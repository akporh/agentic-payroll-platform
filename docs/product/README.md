# Product Hierarchy — `docs/product/`

This directory is the durable product-traceability layer for the Agentic Payroll Platform. It exists to answer, at any time, without relying on a single person's memory:

- What outcomes are we pursuing?
- Which capabilities support those outcomes?
- Which features belong to those capabilities?
- Which stories make up each feature?
- Which stories have been delivered, in which sprint, and with what evidence?

## Status

**This scaffold is empty of historical content.** It was created in Phase 3 (`structure implementation`) of the `product-traceability` programme, authorised by decision D-014 in `docs/programmes/product-traceability/decisions.md`. Phase 4 (`historical migration`) — which populates these registries with the 148 candidate items reconstructed in `docs/diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` — has **not** been authorised and has not begun. Every registry file below currently contains only its schema (column headers and usage notes), zero content rows.

Do not add content rows to any registry file, or story files to `stories/`, without a recorded Phase 4 authorisation decision in `docs/programmes/product-traceability/decisions.md`.

## Structure (Model A — flat registries, per D-008)

```text
docs/product/
├── README.md              (this file)
├── OUTCOMES.md            (top-level outcome registry)
├── CAPABILITIES.md        (durable capability + delivery epic registry)
├── FEATURES.md            (feature registry, one level below capability)
├── STORY-REGISTRY.md      (flat index of every story — the primary traceability table)
├── stories/
│   └── TEMPLATE.md        (template for one story record — copy this, do not edit in place)
└── validate_registry.py   (dependency-free validation script — see below)
```

Relationships between outcomes, capabilities, features, and stories are maintained through stable IDs and metadata columns in the registry tables — not through nested folders. A story's ID never changes even if its feature assignment is later revised. See the discovery document's Section 9 for the full rationale (Model A vs. Model B evaluation) and Section 10 for the adopted source-of-truth rules (below).

## Source-of-truth rules (adopted as written — D-009)

- **This product hierarchy** owns long-lived intent, outcome/capability/feature relationships, and cumulative story status. It does **not** own execution-stage state (that stays in `docs/sprints/<sprint>/state.md`) or acceptance-criteria authorship for stories still in flight (that stays in the sprint's own story file until the sprint closes).
- A story's authoritative acceptance criteria live in exactly one place at a time: pre-delivery, in the sprint's story file (`docs/stories/*.md` or `docs/sprints/<sprint>/`); post-delivery, this hierarchy's story record **summarises but links to**, rather than duplicates, the original story file as the evidence source.
- **`docs/ROADMAP.md` continues to serve forward planning and open backlog** (🔜/⬜/🔮 items). This product hierarchy is a historical/current-state record of delivered and in-flight status, not a replacement planning surface, unless a future human decision changes this.
- Nothing in `docs/ROADMAP.md`, `docs/stories/`, `docs/sprints/`, `docs/audit/`, `docs/audit-program/`, `docs/agentic-architecture-review/`, `docs/security/`, `docs/test-reports/`, or `docs/retro-reports/` is ever rewritten to make this hierarchy appear to have existed earlier than it did.

## Validation mechanism

`validate_registry.py` is a dependency-free Python script (standard library only) that checks internal consistency of this directory:

- Every story ID listed in `STORY-REGISTRY.md`'s table has a corresponding file in `stories/`.
- Every file in `stories/` (other than `TEMPLATE.md`) has a corresponding row in `STORY-REGISTRY.md`.
- Every `FEATURES.md` row references a capability ID that exists in `CAPABILITIES.md`.
- Every `CAPABILITIES.md` row references an outcome ID that exists in `OUTCOMES.md`.

Run it with:

```bash
python3 docs/product/validate_registry.py
```

On the current empty scaffold, it passes trivially (zero rows, zero cross-reference checks to fail). It becomes load-bearing once Phase 4 populates real content — run it after any manual edit to a registry file or `stories/` folder.

## Governing programme

This directory is a controlled output of the `product-traceability` programme. See `docs/programmes/product-traceability/` for the full governance trail: `PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`, `decision-pack.md`, `critic-review*.md`, and `runs/`.
