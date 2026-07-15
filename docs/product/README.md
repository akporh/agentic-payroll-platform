# Product Hierarchy — `docs/product/`

This directory is the durable product-traceability layer for the Agentic Payroll Platform. It exists to answer, at any time, without relying on a single person's memory:

- What outcomes are we pursuing?
- Which capabilities support those outcomes?
- Which features belong to those capabilities?
- Which stories make up each feature?
- Which stories have been delivered, in which sprint, and with what evidence?

## Status

This scaffold was created empty in Phase 3 (`structure implementation`), authorised by decision D-014 in `docs/programmes/product-traceability/decisions.md`. Two bounded migration batches have since populated it:

- **Phase 4A pilot** (D-015, 2026-07-15): exactly **two** historical stories — `PT-A4-31` (AUD-1/Q1, `component_source` trace field) and `PT-A4-32` (SEC-S7, timesheet upload size guard).
- **Phase 4B confirmed-batch** (D-016, 2026-07-15): **19 confirmed-only** stories from capability area A1+A2 (Onboarding & Workforce Setup) — see `docs/programmes/product-traceability/runs/historical-migration-confirmed-batch-run-001.md`. This batch also introduced the human-readable parent-name display convention (below).

**Full Phase 4 (`historical migration`) of the remaining discovery-document items — other capability areas' confirmed items, and every strongly-inferred/tentative/requires-human-classification item everywhere — remains unauthorised.** Neither batch's completion auto-authorises the next.

Do not add any further content row to any registry file, or any further story file to `stories/`, without a separate, recorded Phase 4 (broader-batch) authorisation decision in `docs/programmes/product-traceability/decisions.md`.

## Human-readable names alongside stable IDs (D-016)

Every parent reference in `CAPABILITIES.md`, `FEATURES.md`, and `STORY-REGISTRY.md` carries **both** a stable ID column (authoritative — e.g. `outcome_id`, `capability_id`, `feature_id`) and a human-readable display-name column (`outcome_name`, `capability_name`, `feature_name` respectively) so a reviewer can understand a relationship without opening another file. IDs remain the only authoritative reference for identity and relationships — never resolve or infer a relationship from a display name. A parent rename must update every duplicated display-name field in the same controlled change; `validate_registry.py` rejects any row whose display name has drifted from its parent's actual current name, or is missing.

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

- Every story ID listed in `STORY-REGISTRY.md`'s table has exactly one corresponding file in `stories/` (no missing file, no ambiguous match against more than one file).
- Every file in `stories/` (other than `TEMPLATE.md`) has exactly one corresponding row in `STORY-REGISTRY.md`.
- Every `FEATURES.md` row references a capability ID that exists in `CAPABILITIES.md`.
- Every `CAPABILITIES.md` row references an outcome ID that exists in `OUTCOMES.md`.
- No duplicate ID within any single registry.
- Every display-name field (`outcome_name`, `capability_name`, `feature_name`) exactly matches its referenced parent's current authoritative name, and is present (not blank).

Run it with:

```bash
python3 docs/product/validate_registry.py
```

On the current empty scaffold, it passes trivially (zero rows, zero cross-reference checks to fail). It becomes load-bearing once Phase 4 populates real content — run it after any manual edit to a registry file or `stories/` folder.

## Governing programme

This directory is a controlled output of the `product-traceability` programme. See `docs/programmes/product-traceability/` for the full governance trail: `PROGRAMME.md`, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`, `decision-pack.md`, `critic-review*.md`, and `runs/`.
