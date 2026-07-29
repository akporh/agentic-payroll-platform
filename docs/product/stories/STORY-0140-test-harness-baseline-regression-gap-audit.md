# `STORY-0140` — Test harness baseline and regression-gap audit

**Origin code(s):** `PT-A7-11`
**Outcome:** `OUT-2` — Sustainable delivery process
**Capability:** `CAP-10` — Delivery Infrastructure
**Feature:** `FEAT-37` — Test harness & regression coverage
**Classification:** `technical enabler`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

engineer; auditor

## Problem addressed

The suite's actual coverage against the platform's known historical bugs was unmeasured, so 'the tests pass' carried an unknown amount of information.

## Delivered behaviour

A baseline of the suite plus an audit of regression coverage against the record of known bugs, documenting where coverage does and does not exist.

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/test-reports/test-harness/test-harness-checklist.md`.

## Implementation evidence

`tests/` baseline; the checklist document itself.

## Test / review evidence

`docs/test-reports/2026-07-11-test-harness-baseline.md`, `docs/test-reports/test-harness/test-harness-checklist.md`.

## Decision references

The standing rule recorded in `CLAUDE.md` follows from this work: every bug fix ships with a regression test named for the invariant it protects, and no sprint closes with a red suite.

## Dependencies

`STORY-0139` — the fixture scaffold; `STORY-0141`, `STORY-0142` — the suites being measured.

## Delivery sprint(s)

Sprint 30 / 2026-07-11.

## Delivery history

- 2026-07-11 — baseline and gap audit delivered.
- 2026-07-29 — migrated into `docs/product/` in the Phase 4D remainder batch (D-027).

## Unresolved questions

**The audit documents an open gap and it is not closed here:** the `overrides_json` destruction path — where a component-override PATCH without `overrides_json` in the payload destroys the workspace's NHF, health-insurance and development-levy rates — has zero test coverage. It is a known, recorded hazard with no regression test standing over it.
