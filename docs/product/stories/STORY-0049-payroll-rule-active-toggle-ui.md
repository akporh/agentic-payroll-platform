# `STORY-0049` — WC-8: Payroll rule active/inactive control via UI

**Origin code(s):** `PT-A1-10` · `WC-8`
**Outcome:** `OUT-3` — Operationally usable payroll administration
**Capability:** `CAP-3` — Onboarding & Workspace Setup
**Feature:** `FEAT-3` — Post-onboarding configuration management
**Classification:** `user-facing story`
**Status:** `delivered`
**Confidence:** `confirmed`

## Actor

Payroll operator who needs to stop applying a bonus/allowance/deduction rule to future runs without deleting its configuration.

## Problem addressed

There was no UI path to suspend a payroll rule (e.g. a bonus that should stop applying) short of editing raw rule data; and once `payroll_rule.is_active` resolution became fully date-driven (Sprint A, see this repository's standing rule that `is_active` alone was never sufficient to mean "currently in effect"), an earlier two-way Activate/Deactivate toggle became actively misleading — it implied a live effective/non-effective switch that no longer matched how rule resolution actually works.

## Delivered behaviour

`WorkspaceConfig.tsx`'s Payroll Rules table originally shipped a two-way Activate/Deactivate toggle (Track J, WC-8): a confirmation dialog, an optimistic status-badge update, and a dismissible banner explaining that changes take effect only after the rule set is re-published. **This was superseded on 2026-07-05** (commit `0a2702d`) by a one-way "Withdraw" action, reusing the existing Custom Allowances delete pattern: withdrawing a rule sets `is_active = false` but the row stays visible with a `WITHDRAWN` status badge rather than disappearing or being re-activatable from this screen, and the Status tooltip now describes the real date-driven resolution model instead of the old "current effective state" framing. The commit message states the reason directly: "The Activate/Deactivate toggle implied is_active means 'currently in effect,' which stopped being true once rule resolution became fully date-driven."

## Acceptance criteria

Owned by the **source story file**, not by this record — this is a retro-migrated story, so its authoritative acceptance criteria stay where they were written and are not duplicated here (D-018). Follow the Source reference below. Forward-authored stories carry their criteria natively in this section instead.

## Source reference

`docs/ROADMAP.md` Track J item 40 (`WC-8/WC-9`); original acceptance criteria in `docs/stories/track-j-workspace-config-management.md`, section "WC-8 — Toggle a Payroll Rule Active / Inactive". Superseding behaviour recorded in the `0a2702d` commit message and `docs/ROADMAP.md`'s payroll-rule `is_active` semantics note (see this repository's `CLAUDE.md` "Known Data Contract Rules" — `payroll_rule.is_active` means "not withdrawn," never "currently in effect").

## Implementation evidence

- `frontend/src/pages/WorkspaceConfig.tsx` — `StatusBadge status={r.is_active ? 'ACTIVE' : 'WITHDRAWN'}` (lines ~2418, 2486) and the Withdraw confirm-dialog flow (lines ~2113–2118, ~2877–2890), confirmed present by direct inspection during this migration pass.
- Original toggle: commit `db17ef9` (2026-04-22, Track J batch).
- Superseding one-way Withdraw refactor: commit `0a2702d` ("refactor: replace payroll rule active/inactive toggle with one-way Withdraw", 2026-07-05) — isolated via `git log -1` on that commit.

## Test / review evidence

- `docs/test-reports/2026-04-21-track-j.md` — WC-8 (original toggle) verified **PASS**/PASS: "Optimistic update, ConfirmDialog, dismissible banner ✓."
- No dedicated test report was found for the 2026-07-05 Withdraw refactor specifically — it is documented only via the commit message and a `docs/ROADMAP.md` diff (24 lines changed per `git show 0a2702d --stat`); not independently re-verified live in this pass beyond direct code inspection confirming the `WITHDRAWN` badge and one-way action exist as described.

## Decision references

- None specific to WC-8 beyond the general Track J arch-council decisions (`docs/stories/track-j-workspace-config-management.md`).
- `D-016` (`docs/programmes/product-traceability/decisions.md`) — authorises this story's migration into `docs/product/` as part of the Phase 4B confirmed-batch.

## Dependencies

None. The 2026-07-05 refactor is a UI/semantics correction to this same story's feature, not a dependency on another story in this batch.

## Delivery sprint(s)

Track J (Gate 6 / Sprint 8 parallel track) for the original toggle, 2026-04-22 (commit `db17ef9`); superseded by a one-way Withdraw action in a later, unnamed maintenance change, 2026-07-05 (commit `0a2702d`).

## Delivery history

- 2026-04-21/22 — Track J — two-way Activate/Deactivate toggle delivered (commit `db17ef9`); verified PASS per `docs/test-reports/2026-04-21-track-j.md`.
- 2026-07-05 — replaced with a one-way "Withdraw" action + `WITHDRAWN` status badge, correcting the toggle's implication that `is_active` meant "currently in effect" (commit `0a2702d`); no dedicated test report found for this specific change in this pass.
- 2026-07-15 — Phase 4B confirmed-batch migration into `docs/product/` (D-016).

## Unresolved questions

The discovery document's title for this item ("Payroll rule active/inactive toggle via UI") describes the original Track J behaviour, which has since been replaced by a one-way Withdraw action — re-activation from this screen is no longer possible. This story's "Delivered behaviour" section describes the current, correct state rather than the superseded toggle, per the template's instruction to describe what actually exists/works now. The 2026-07-05 refactor itself was not independently re-verified against a dedicated test report in this pass — only direct code inspection.
