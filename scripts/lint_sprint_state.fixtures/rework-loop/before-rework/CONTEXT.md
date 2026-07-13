# Fixture Sprint — `rework-loop` (snapshot: before-rework)

Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py`
passes on a valid `complete` state, immediately before a rework event.
Not a real sprint. Part of a 3-snapshot sequence (`before-rework` →
`after-rework` → `after-fix`) demonstrating the rework loop mechanically,
per `docs/diagnostics/2026-07-13-icm-follow-up-validation-pilot-scope.md`
§7. No production code was made defective to produce this fixture.

## Goal

`implementation` and its dependent `audit` and `test` are all in a
consistent, terminal-or-blocked state — the baseline the next snapshot
reopens.
