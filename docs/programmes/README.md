# Programmes

Long-running, multi-phase governance efforts that sit **above** the ICM sprint workflow (`docs/sprints/`). A programme owns phased scope, explicit human gates between phases, and its own decision/exception record. Delivery execution never happens inside a programme — programmes produce structure, decisions, and build orders that sprints then consume.

## Register

| Programme | Purpose | Phase state | Current human gate |
|---|---|---|---|
| [`product-traceability`](product-traceability/PROGRAMME.md) | Durable product hierarchy (Outcome → Capability → Feature → Story) + retrospective migration of delivered work | Phase 4 (historical migration) — 4A pilot + 4B batch complete; remainder not authorised | Review batch quality; authorise further Phase 4 scope |
| [`agentic-architecture-review`](agentic-architecture-review/PROGRAMME.md) | 13-stage architecture review → consolidation with the audit backlog → adopted agentic build order | Phase 1 (review-execution) — decision-gated continuous per D-003; Stage 05 awaiting critic | None open — stops only on material decisions; final human approval at Stage 13 |

*Phase-state column is a convenience snapshot — each programme's `state.md` is authoritative. Update this row when a programme's phase or gate changes.*

## Conventions

Every programme folder carries the same control files, per the pattern established by `product-traceability`:

| File | Purpose |
|---|---|
| `PROGRAMME.md` | Objective, scope, intended phases, relationships to other structures |
| `POLICY.md` | Fixed execution policy: autonomy mode, may/may-not, stop conditions, source-of-truth boundaries |
| `PHASES.md` | All phases defined up front; later phases are placeholders until explicitly authorised |
| `state.md` | Phase-level state and the current human gate |
| `decisions.md` | Programme-level human decisions (D-*), append-only |
| `exceptions.md` | Stop-condition events, append-only |
| `runs/` | Run records, one per executed phase run (created with the first run) |

A programme may add operating-model files on top of the core set — e.g. `agentic-architecture-review`'s `RUNBOOK.md` (controller loop), `CRITIC.md` (independent critic contract), and `decision-queue.md` (non-blocking decisions), added by its D-003.

Two standing rules: a programme never authorises its own next phase, and completed history (closed run records, diagnostics, critic reviews — here or anywhere in `docs/`) is never rewritten.

## Note on the review's location (2026-07-15)

`agentic-architecture-review` lived at `docs/agentic-architecture-review/` until 2026-07-15, when it was registered as a programme and moved here (`git mv`, history preserved — see its `decisions.md` D-002). Historical records in `docs/diagnostics/` and closed product-traceability run records deliberately still cite the old path.
