# Fixture Sprint — `rework-loop` (snapshot: after-rework)

Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py`
passes on a valid `needs-rework` state, with its dependents correctly
reverted to `blocked`. Not a real sprint. Part of a 3-snapshot sequence
(`before-rework` → `after-rework` → `after-fix`) demonstrating the rework
loop mechanically, per
`docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md` §7.
No production code was made defective to produce this fixture.

## Goal

A human decision reopens `implementation` to `needs-rework`. Both `audit`
and `test` — which directly list `implementation` in their `depends_on`
— mechanically revert to `blocked`, per `WORKFLOW.md`'s rework-loop rule.
