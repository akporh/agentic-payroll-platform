# `STORY-0083` — SEC-S1 — generic client message plus server-side log for `_wpc_err`

**Origin code(s):** `PT-S-01` · `SEC-S1`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-2` — Security & Compliance Hardening
**Feature:** `FEAT-34` — Input validation & enum guards
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `strongly inferred`

## Actor

engineer; attacker (negatively)

## Problem addressed

A workspace-payroll-config error path returned the raw exception string to the client. Database constraint violations expose table names, column names and constraint names verbatim.

## Delivered behaviour

The raw exception is logged server-side and a generic human-readable message is returned to the client.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track S security register, SEC-S1; `docs/stories/sprint-13-track-m3-m5-track-s-security.md`.

## Implementation evidence

Exception handling in the workspace-payroll-config route.

## Test / review evidence

None dedicated — covered within the Sprint 13 security track scope.

## Decision references

This item is the origin of the standing prohibition recorded in `CLAUDE.md`: **never return `str(e)` in an HTTP response.** The rule has had to be re-applied in Sprint 10 and Sprint 17 since, which is why it is recorded as standing rather than as a one-off fix.

## Dependencies

`STORY-0085` — the logging import fix that made server-side logging work on this path.

## Delivery sprint(s)

Sprint 13 (Track S).

## Delivery history

- Sprint 13 — delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

No dedicated test report isolates the Track S items in this sprint.
