# `PT-A1-38` — Enrollment pre-population normalisation fix (fixes EMP-REG-5)

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-4` (see `../FEATURES.md`)
**Classification:** `defect/remediation`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator enrolling not-yet-enrolled employees after a bulk upload, using the grade-grouping feature introduced by EMP-REG-5.

## Problem addressed

After a group upload, EMP-REG-5's grouping logic correctly grouped not-enrolled employees by imported grade/designation label, but clicking "Select →" on a group or "Enroll →" on an individual employee opened the enrollment SlideOvers with grade, designation, and salary definition fields all blank — even though the system had already detected those values to build the groups. Root cause: the matching logic used `toUpperCase()` only, so an imported label like `"General Manager"` (with a space) never matched a configured code like `"GENERAL_MANAGER"` (with an underscore) — the match failed silently and nothing was passed to the SlideOver as a preset.

## Delivered behaviour

A module-level `normalizeCode` helper (`s.trim().toUpperCase().replace(/[\s-]+/g, '_')`) is applied on both sides of every grade/designation/salary-def comparison across `autoMatchSalaryDef`, the `EnrollSlideOver` useEffect, and `suggestedGroups`. Where no configured code matches even after normalisation, the "Select →" and dropdown paths fall back to showing the imported raw label marked `(from import)`, so the operator sees what was detected rather than a blank field. `parseNativeRows` also normalises grade/designation on ingest to match template-upload behaviour.

## Source reference

`docs/stories/fix-emp-reg5-enrollment-prepopulation.md` — full root-cause analysis, fix description, and updated acceptance criteria (replacing the original EMP-REG-5 AC).

## Implementation evidence

- `docs/stories/fix-emp-reg5-enrollment-prepopulation.md` — lists the exact changed locations: `autoMatchSalaryDef`, `EnrollSlideOver` useEffect, `suggestedGroups`, "Select →" button handler, `BulkEnrollSlideOver` dropdowns, `parseNativeRows` (all in `frontend/src/pages/Employees.tsx`).
- `normalizeCode` helper confirmed present in `frontend/src/pages/Employees.tsx` by `git log -S "normalizeCode"`, which isolates commit `98f2100`.
- Commit `98f2100` ("feat(sprint-27+28+fix): smart native upload, error visibility, workspace activation CTA, idempotent bulk inputs", 2026-06-15) — this fix is bundled into a larger commit alongside Sprint 27/28 and the `PT-A1-39` workspace-activation-CTA fix; not isolated to an EMP-REG-5-fix-only diff.

## Test / review evidence

- The story file itself states "Status: ✅ Fixed" and documents the updated acceptance criteria the fix must satisfy (normalised matching for spaces/hyphens/case; "Select →" pre-fills grade with a matched or `(from import)`-marked label; individual "Enroll →" pre-fills all three fields). No separately named test report was found verifying these specific acceptance criteria live; the fix is bundled into the same commit as the Sprint 27/28 work, which does have a test report (`docs/test-reports/2026-06-15-sprint-27-28.md`), but this pass did not find that report calling out EMP-REG-5's fix by name.

## Decision references

- None recorded beyond routine execution.
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Fixes a defect in EMP-REG-5 (Sprint 23, `PT-A1-...` not itself in this batch — EMP-REG-5's grouping feature is the pre-existing behaviour this story corrects, not a dependency this batch tracks as a separate row).

## Delivery sprint(s)

Fix sprint, 2026-06 (commit `98f2100`, dated 2026-06-15).

## Delivery history

- 2026-06-15 — fix sprint — `normalizeCode` matching applied across enrollment pre-population paths, fixing EMP-REG-5's silent blank-field regression (commit `98f2100`); story file marked "✅ Fixed."
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

This pass did not locate a test report calling out this specific fix's acceptance criteria by name, though it is bundled into the same commit as the Sprint 27/28 work which does have `docs/test-reports/2026-06-15-sprint-27-28.md`. The fix's own story file states "✅ Fixed" but that status is self-reported in the story file rather than independently confirmed against a dedicated test-report entry in this pass.
