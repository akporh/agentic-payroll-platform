# `PT-A1-25` — Split Edit vs Change Grade/Salary row action (EMP-UX-1, Sprint 17)

**Outcome:** `OUT-3` (see `../OUTCOMES.md`)
**Capability:** `CAP-3` (see `../CAPABILITIES.md`)
**Feature:** `FEAT-4` (see `../FEATURES.md`)
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Workspace administrator editing employee records on the Employees page.

## Problem addressed

The pre-Sprint-17 `EditSlideOver` conflated name/status edits with grade/designation/contract-end-date changes in one form. After Sprint 17 introduced the append-only contract model (`PT-A1-21`), changing grade creates a new, irreversible contract row — an operator fixing a typo in a name could accidentally trigger a contract change by sharing the same form.

## Delivered behaviour

The single conflated "Edit" row action is replaced with two distinct, clearly labelled actions: "Edit" opens `EditEmployeeSlideOver`, scoped to `full_name` and `status` only (saves via `PATCH /{wid}/employees/{eid}` — no contract row touched); "Change Grade / Salary" opens `ChangeContractSlideOver`, scoped to `salary_definition_id` (searchable dropdown), `start_date` (required), and `change_reason` (required) — this path creates a new contract row via `POST /{wid}/employees/{eid}/contracts`.

## Source reference

`docs/stories/sprint-17-employee-ux.md`, "EMP-UX-1 · Split employee row actions — Edit Details vs Change Grade/Salary."

## Implementation evidence

- `docs/stories/sprint-17-employee-ux.md` — full EMP-UX-1 scope, field lists for both SlideOvers, and the rationale ("Data integrity prerequisite for Sprint 17 append-only contract model").
- `frontend/src/pages/Employees.tsx` — the pre-existing conflated `EditSlideOver` this story replaces was at lines 116–161 per the story file's "Current state" section.
- Commit `0ed5bfb` (2026-05-27) — same commit as `PT-A1-21`/`PT-A1-22`; this UX story shipped together with the Track B CRUD API it depends on ("Must ship with sprint-17-employee-crud.md").

## Test / review evidence

- `docs/test-reports/2026-05-27-sprint-17-full.md` — B3 row in the Check breakdown table: "12 PASS (TypeScript + wiring)" plus "1 BLOCKED (browser)" — the static/compile-level checks for the split-action UI passed, but full browser UAT for the SlideOvers was recorded as BLOCKED ("B3 browser SlideOvers... BLOCKED"), i.e. not live-exercised in a browser in that pass.

## Decision references

- None beyond the Sprint 17 arch-council gate ("APPROVED WITH CONDITIONS").
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

Depends on `PT-A1-21` (the employee CRUD API and `POST .../contracts` endpoint this UI calls) — "Must ship with sprint-17-employee-crud.md" per the story file itself.

## Delivery sprint(s)

Sprint 17 (UX Track), delivered 2026-05-27 (commit `0ed5bfb`).

## Delivery history

- 2026-05-27 — Sprint 17 — Edit vs Change Grade/Salary split-action rework delivered (commit `0ed5bfb`); 12/12 static/compile checks PASS, browser UAT BLOCKED (not executed) per `docs/test-reports/2026-05-27-sprint-17-full.md`.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The discovery document separately lists a closely related item, `PT-A1-23` ("Employees.tsx split-action rework: Edit/Change Grade/View Contracts"), as `tentative` because its browser UAT was recorded BLOCKED — and it is correctly excluded from this batch for that reason. This story (`PT-A1-25`, the EMP-UX-1-specific split, confirmed per the discovery document) shares the same underlying BLOCKED-browser-UAT limitation: the split-action UI's TypeScript/wiring is verified PASS, but a live browser click-through of the two SlideOvers was not independently exercised in the cited test report. This is carried forward honestly rather than silently upgraded to "fully live-verified."

**Overlap disclosure (added following the Phase 4B critic review, `critic-review-phase-4b-confirmed-batch.md`):** `PT-A1-23` and this story both describe the same Sprint 17 Track B3 delivery increment and rest on the identical evidence base — `docs/test-reports/2026-05-27-sprint-17-full.md`'s B3 section, where every row-action/SlideOver check is code-level PASS and the only recorded gap is "Browser testing: NOT executed." The discovery document gave these two overlapping descriptions of what appears to be the same underlying feature two different confidence labels (`PT-A1-23` `tentative`; this story `confirmed`) without reconciling the overlap — it is not clear from the discovery document alone whether they are the same delivered item described at two different granularities (a broader "full rework" framing vs. this story's narrower EMP-UX-1-specific framing) or genuinely distinct scopes. This does not change this story's migration status: its own EMP-UX-1 acceptance criteria (Edit scoped to `full_name`/`status` only; Change-Grade SlideOver with required `change_reason`; row-action visibility rules) are independently code-level verified in the cited test report, regardless of how `PT-A1-23` is eventually reconciled. A future migration pass considering `PT-A1-23` should treat this overlap as a genuine open question, not assume the two are unrelated.
