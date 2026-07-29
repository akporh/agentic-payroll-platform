# `STORY-0171` — EMP-REG-5-FIX — enrollment slide-over pre-population

**Origin code(s):** `EMP-REG-5-FIX`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-4` — Employee Lifecycle Management
**Feature:** `FEAT-8` — Enrollment & payroll readiness
**Classification:** `user-facing story`
**Status:** `backlog`
**Confidence:** `requires human classification`

## Actor

payroll administrator

## Problem addressed

After a bulk import, the enrollment slide-over does not pre-fill grade and designation from the imported labels, because the imported values differ from the stored codes by formatting alone (spaces versus underscores). The operator re-keys values the system already holds.

## Delivered behaviour

**Not delivered.** Recorded here because the item was open in `docs/ROADMAP.md` and carried no `STORY-<nnnn>`.

## Acceptance criteria

**This item is not delivered.** It is recorded so that an allocated identifier exists and its absence from the delivered set is explicit rather than silent. If it is ever scheduled, criteria are written in the sprint that takes it.

## Source reference

`docs/ROADMAP.md` Sprint 27 story index, EMP-REG-5-FIX — 🔜 open.

## Implementation evidence

None — not implemented.

## Test / review evidence

None — not implemented.

## Decision references

Allocated by the `roadmap-split` sprint under `STORY-0160` (`docs/sprints/roadmap-split/CONTEXT.md`), which closed the forward-coverage gap: `ID-ALLOCATION.md` claims that an item absent from it is an item no known evidence records, and that property held for delivered work but not for open work — only 6 of 20 open roadmap items carried an identifier. Classified `backlog` following the D-011 precedent.

## Dependencies

The Upload/Enroll separation established in Sprint 22 — any fix must respect it: `grade_code` is a payroll-setup field assigned only via the Enroll flow, never forwarded from the Excel grade column during upload.

## Delivery sprint(s)

Not scheduled.

## Delivery history

- Sprint 23 — EMP-REG-5 shipped; pre-population defect surfaced.
- Sprint 27 — the fix scoped as EMP-REG-5-FIX. Still open.
- 2026-07-29 — allocated and recorded by the `roadmap-split` sprint (`STORY-0160`).

## Unresolved questions

Not delivered. Normalised matching (spaces→underscores) is the roadmap's stated approach; whether normalisation is the right fix or masks a data-entry inconsistency upstream is not settled on record.
