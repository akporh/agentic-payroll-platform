# Fixture Sprint — `illegal-parallel`

Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py`
fails loudly on a `may_run_with` pairing the registry forbids. Not a real
sprint.

## Goal

Exercise: `implementation` and `audit` declared as `may_run_with` each
other, which `STAGE-REGISTRY.md` (both real and this fixture's synthetic
copy) explicitly prohibits — "must never run concurrently."
