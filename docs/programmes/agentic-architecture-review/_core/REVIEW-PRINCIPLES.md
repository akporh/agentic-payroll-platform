# Review Principles

Binding for the entire review. Read before any stage begins.

## 1. Separate current implementation, intended design, and identified gap

These are three distinct fields, always. A finding that blends them ("the system should do X but doesn't, which is bad") is not acceptable — it must be decomposed into:

- **Current implementation**: what happens today, cited to evidence (code, data, logs, screenshots)
- **Intended design**: what was meant to happen, cited to a spec, ticket, `CLAUDE.md` rule, or an explicit statement from the human reviewer logged in `decisions.md`
- **Identified gap**: the delta, stated neutrally

If intended design is unknown or was never documented, say so explicitly — do not infer intent from the current implementation itself (that's circular).

## 2. No finding is a fact until it is confirmed

A draft finding is a hypothesis, not a fact. It must never be cited by another stage, by Stage 12 (Target Direction), or by Stage 13 (Approved Roadmap) unless and until it has been promoted to confirmed status under `EVIDENCE-STANDARD.md` and `FINDING-SCHEMA.md`.

## 3. Evidence over inference

Prefer reading the actual code, actual data, or actual running behavior over inferring from documentation, naming, or memory of prior sprints. Memory files and `CLAUDE.md` rules are useful pointers to where to look — they are not themselves evidence.

## 4. Stage independence with sequential gating

Each stage answers its own questions and does not assume the conclusions of a later stage. Later stages may build on confirmed findings from earlier stages, but earlier stages are not rewritten to accommodate what a later stage discovers — a later discovery that contradicts an earlier confirmed finding is logged as a new finding with a note, not a silent retcon.

## 5. Human decision points are explicit and logged

Any point where the review requires a judgment call, a scope decision, a severity call, or an approval to proceed is logged in `_core/HUMAN-DECISIONS.md` and the relevant stage's `decisions.md`. The review does not make binding calls on behalf of the human reviewer.

## 6. No production code, configuration, or data changes

This review is read-only with respect to the production system. Findings may recommend future changes; the review itself does not implement them.

## 7. Neutral language

Findings are stated in neutral, falsifiable terms ("X does Y under condition Z, per evidence E") rather than evaluative language ("X is broken," "X is bad practice") unless a severity rating from `SEVERITY-MODEL.md` is explicitly attached with justification.
