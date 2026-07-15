# Programme — Agentic Architecture Review

## Programme ID

`agentic-architecture-review`

## Objective

Carry the 13-stage agentic architecture review to gated completion, then turn its output into an adopted build order for the Phase 2 agentic platform:

1. Complete the evidence-backed, stage-gated review (Stages 01–13, ending in an approved roadmap at Stage 13).
2. Cross-reference that approved roadmap with the audit programme's independently produced remediation backlog (`docs/audit-program/` Stage 13 — S0/S1 release gate plus 8 sequenced remediation programmes) and `docs/ROADMAP.md`, producing **one** reconciled build order rather than three competing ones.
3. Adopt the reconciled build order into the product hierarchy (`docs/product/`) and `docs/ROADMAP.md`, so agentic-capability delivery starts under the organised structure — not alongside it.

## Scope

In scope:

- Programme governance controls (this file, `POLICY.md`, `PHASES.md`, `state.md`, `decisions.md`, `exceptions.md`).
- The review workspace itself (Stages 01–13, `_core/`, `_inputs/`, `review-state.md`, `WORKFLOW.md`), which this programme now physically contains.
- Phase 2 and Phase 3 as **placeholders only** — each requires its own explicit human authorisation before any work begins.

Out of scope:

- Modifying production code (`backend/`, `frontend/`, `migrations/`) — the review is read-only with respect to the system under review, and consolidation/adoption phases produce documents and decisions, not code.
- Executing any remediation programme or building any agentic capability. Delivery happens under the ICM sprint workflow (`docs/sprints/`), traced through `docs/product/` — never inside this programme.
- Modifying `docs/audit-program/` (a closed, read-only record this programme cites as input).

## Current phase

`review-execution` (Phase 1)

## Status

`active`

## Intended phases

1. **review-execution** — run Stages 01–13 to gated completion under the review's own `WORKFLOW.md`. *Authorised (the review was begun before programme registration; D-001 registers it without altering its stage governance). In flight: Stages 01–04 gated-closed, Stage 05 awaiting human review, Stages 06–13 not started — see `review-state.md`.*
2. **roadmap-consolidation** — cross-reference the Stage 13 approved roadmap with the audit programme's 8 remediation programmes and `docs/ROADMAP.md`; produce a single reconciled build order and a decision pack for human approval. *Not authorised.*
3. **adoption** — adopt the approved build order into `docs/product/` (initiatives/epics/features per the product-traceability conventions) and `docs/ROADMAP.md`. *Not authorised.*

Each phase after Phase 1 requires an explicit human authorisation recorded in `decisions.md` before it may begin.

## Governance split — two state files, no overlap

| File | Owns |
|---|---|
| `review-state.md` | **Stage-level** state of the 13 review stages — unchanged, still the single source of truth for "where is the review" |
| `state.md` (this programme) | **Phase-level** state — which programme phase is authorised/active/complete, and the current human gate |
| `WORKFLOW.md` | Stage sequence, gating rules, finding lifecycle — unchanged by programme registration |
| `_core/HUMAN-DECISIONS.md` | Review-internal human decisions (HD-*) — unchanged |
| `decisions.md` (this programme) | Programme-level decisions (D-*): registration, phase authorisations, scope changes |

Programme registration changes **nothing** about how stages run, gate, or record findings.

## Success criteria

- The review reaches Stage 13 `gated-closed` with every stage gate explicitly passed per `WORKFLOW.md`.
- The consolidation phase (when authorised) accounts for **every** item in the audit programme's Stage 13 crosswalk and the Stage 13 approved roadmap — nothing dropped silently; conflicts surfaced as decisions, not resolved by executor fiat.
- The adoption phase (when authorised) leaves `docs/product/` and `docs/ROADMAP.md` telling the same story, with traceability from each adopted initiative back to the review finding(s) and/or audit finding(s) that justify it.
- The programme does not authorise its own continuation — each phase boundary is a recorded human decision.

## Relationship to other governance structures

- **Audit programme (`docs/audit-program/`)** — closed, read-only input. Its Stage 13 backlog is a primary input to Phase 2. The two efforts already converge on the same headline: authentication/tenancy (audit Programme 1, ROADMAP Track P) gates everything agentic.
- **Product-traceability programme (`docs/programmes/product-traceability/`)** — owns the `docs/product/` hierarchy conventions. Phase 3 of this programme writes *into* that structure under its rules; forward-looking initiative/epic modelling will be coordinated between the two programmes at Phase 3 authorisation time.
- **ICM sprint workflow (`docs/sprints/`)** — owns delivery execution. This programme ends where sprints begin: its final output is an adopted, prioritised build order that sprints then consume.
