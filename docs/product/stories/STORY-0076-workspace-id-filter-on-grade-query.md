# `STORY-0076` — SEC-S4 — `workspace_id` filter on the grade query, closing cross-workspace leakage

**Origin code(s):** `PT-S-04` · `SEC-S4`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-35` — Workspace isolation & data scoping
**Classification:** `compliance story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

bureau setup admin; every workspace's data subjects

## Problem addressed

A grade query ran without a workspace filter, so one client's grades could be returned in another client's context — a tenant-isolation breach in a multi-client bureau platform.

## Delivered behaviour

The grade query is workspace-scoped at the query level, not merely filtered in the route.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S4.

## Implementation evidence

Grade query in `backend/infra/repositories/` — `workspace_id` predicate added.

## Test / review evidence

`docs/security/2026-05-02-sprint-11-security-review.md`, `docs/test-reports/2026-05-02-sprint-11.md`.

## Decision references

Closes a violation of the standing rule in `CLAUDE.md`: workspace scoping is mandatory on every DB query, enforced at the query level rather than at the route.

## Dependencies

None.

## Delivery sprint(s)

Sprint 11.

## Delivery history

- Sprint 11 — found and closed.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

None.
