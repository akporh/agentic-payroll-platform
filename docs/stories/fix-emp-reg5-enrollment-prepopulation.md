# Fix — EMP-REG-5 · Enrollment slide-over field pre-population

**Fixes:** EMP-REG-5 (Sprint 23 — Auto-suggest enrollment by grade group)
**Reported:** 2026-06-13
**Status:** ✅ Fixed

---

## Problem

After a group upload, the system correctly groups not-enrolled employees by imported grade/designation label (the grouping feature from EMP-REG-5 works). However, when an operator clicked **"Select →"** on a group or **"Enroll →"** on an individual employee inside a group, the BulkEnrollSlideOver and EnrollSlideOver opened with all fields blank — including grade, designation, and salary definition — even though the system had already detected those values to build the groups.

The operator had to manually re-enter information the system already knew.

## Root Cause

The matching logic in EMP-REG-5 used `toUpperCase()` only:

```
sd.code.toUpperCase() === group.key  // "GENERAL_MANAGER" !== "GENERAL MANAGER"
```

Import files frequently have spaces where configured codes use underscores (e.g., `"General Manager"` in the file vs `"GENERAL_MANAGER"` as the grade code). The match failed silently, leaving `matchedGrade = null` and `matchedDef = null`. Nothing was passed to the slide over as a preset.

The same bug affected the `EnrollSlideOver` useEffect (individual enrollment path) and the `autoMatchSalaryDef` helper used to auto-select salary definitions.

The native upload path also stored grades/designations as raw strings (e.g., `"General Manager"`) rather than normalising them to `"GENERAL_MANAGER"`, making the mismatch worse for that path.

## Fix

### `normalizeCode` helper (module-level, `Employees.tsx`)

```ts
const normalizeCode = (s: string) => s.trim().toUpperCase().replace(/[\s-]+/g, '_');
```

Applied on both sides of every grade/designation/salary-def comparison.

### Changes made

| Location | Change |
|---|---|
| `autoMatchSalaryDef` | Uses `normalizeCode` on both sides of salary def code comparison |
| `EnrollSlideOver` useEffect | `normalizeCode` matching for grade and designation against configured codes |
| `suggestedGroups` | `normalizeCode` for grade, designation, and salary def matching |
| "Select →" button handler | Falls back to `rawGradeLabel` / `rawDesigLabel` when no configured code matches — slide over shows imported label as `(from import)` option rather than leaving field blank |
| `BulkEnrollSlideOver` dropdowns | If preset value is not in configured options, it is injected as `{ value, label: '${value} (from import)' }` so the field visibly shows what was detected |
| `parseNativeRows` | Normalises grade/designation on ingest to match template-upload behaviour |

## Updated Acceptance Criteria (replaces original EMP-REG-5 AC)

**Normalised matching — spaces, hyphens, case**

Given `imported_grade_label = "General Manager"` and a grade code / salary def code of `"GENERAL_MANAGER"`,
Then the match is found — normalization: trim → UPPER → spaces or hyphens → `_`.

**"Select →" pre-fills grade and designation**

Given I click "Select →" on a group (no salary def match),
Then BulkEnrollSlideOver opens with:
- `salary_definition_code` empty (operator must choose),
- `grade` pre-filled with the matched configured code if a normalised match exists,
- If no configured code matches, the grade field shows the imported label marked `(from import)` so the operator can confirm or override.

**Individual "Enroll →" pre-fills all fields**

Given I expand a group and click "Enroll →" on a single employee,
Then EnrollSlideOver opens with:
- `grade` pre-filled from `imported_grade_label` (normalised match against configured codes),
- `designation` pre-filled from `imported_designation_label` (same),
- `salary_definition_code` auto-matched from the resolved grade and designation.

## Out of Scope (unchanged)

- Fuzzy prefix matching (`STEP_1B → STEP_1`) — still deferred. Wrong match in payroll is worse than no match.
- Auto-enrolling without user confirmation.
