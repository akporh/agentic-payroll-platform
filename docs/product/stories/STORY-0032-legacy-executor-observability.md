# `STORY-0032` — Legacy executor observability — deprecation warning and metrics

**Origin code(s):** `PT-A7-04` · `G12`
**Outcome:** `OUT-1` — Governed, auditable payroll execution
**Capability:** `CAP-1` — Correctness, Audit & Snapshot
**Feature:** `FEAT-28` — Legacy executor observability
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; auditor

## Problem addressed

Two executor paths exist, and only one produces a component trace. Without signalling, a caller could silently fall back to the legacy path and produce results that cannot be audited — with nothing recording that it had happened.

## Delivered behaviour

The legacy executor logs a deprecation warning and emits metrics when used, making fallback visible rather than silent.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` capability areas A7–A10, item G12.

## Implementation evidence

`backend/domain/payroll/executor.py` — the legacy fallback path, used when `component_metadata` is `None`.

## Test / review evidence

None dedicated — Sprints 1–6 predate the per-sprint test-report convention.

## Decision references

Recorded in `CLAUDE.md`'s Executor Paths section: the sequential executor is the production path; the legacy executor does not produce `component_trace_jsonb` and all callers are to be migrated off it.

## Dependencies

`STORY-0031` — the trace the legacy path fails to produce.

## Delivery sprint(s)

Sprints 1–6 (Core MVP).

## Delivery history

- Sprints 1–6 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report exists for this period. Whether every caller has since been migrated off the legacy path is not established by this record.
