# Fixture Sprint — `bad-decision-ref`

Synthetic sprint workspace used only to prove `scripts/lint_sprint_state.py`
fails loudly on decision-integrity defects. Not a real sprint.

## Goal

Exercise: an orphaned `decision_ref` (cited in `state.md`, no matching
`decisions.md` entry), and a duplicate decision ID that also references an
unknown stage.
