# Fixture Sprint — `rework-loop` (snapshot: after-fix)

Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py`
passes on the resolution of a rework loop: the reopened stage returns to
`complete` under a second attempt, and its dependents become `eligible`
again. Not a real sprint. Final snapshot of the 3-snapshot sequence
(`before-rework` → `after-rework` → `after-fix`), per
`docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md` §7.
No production code was made defective to produce this fixture.

## Goal

`implementation` returns to `complete` with `attempt: 2` and new
evidence. `audit` and `test` — previously reverted to `blocked` in
`after-rework` — become `eligible` again now that their dependency is
terminal.
