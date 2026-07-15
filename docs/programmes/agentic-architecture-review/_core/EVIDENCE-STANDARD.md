# Evidence Standard

Defines what counts as evidence sufficient to promote a finding from draft to confirmed. Binding for every stage.

## What counts as evidence

Acceptable evidence types, in descending order of strength:

1. **Direct code/config read** — an actual excerpt of the source file, with path and line numbers, saved into the stage's `evidence/` folder or cited with a precise path:line reference.
2. **Direct data read** — an actual query result or data export from a real (non-production-mutating) read against the system, saved into `evidence/`.
3. **Direct observed behavior** — a screenshot, log excerpt, or transcript of the system actually running, saved into `evidence/`.
4. **Primary documentation** — a spec, ticket, ADR, or `CLAUDE.md` rule that is dated and attributable, cited with path and section.
5. **Human reviewer statement** — an explicit statement from the human reviewer, logged in `decisions.md` with a timestamp, used only for facts that cannot be independently observed (e.g. client intent, business constraints).

## What does not count as evidence

- Memory files (`~/.claude/.../memory/*`) — these are pointers to where to look, not evidence themselves. If a memory claims a fact, it must be re-verified against current source before being cited.
- Inference from naming conventions alone (e.g. "the function is called `validate_x` so it must validate X").
- Prior sprint summaries, retro notes, or roadmap documents, unless independently re-verified against current code/data.
- Assumptions carried over from a different stage without re-statement and re-citation in the current stage.
- Unverified claims from the AI agent's own prior output in the same session.

## Evidence storage

Every confirmed finding cites at least one artifact. Where the artifact is a file excerpt or query output, save it into the stage's `evidence/` folder (e.g. `evidence/01-sequential-executor-excerpt.md`) and reference it by filename in `findings.md`. Where the evidence is a precise, stable path:line reference into the live codebase, citing the reference directly is sufficient — duplication into `evidence/` is not required for pure code citations, but is required for anything transient (query output, screenshot, log line) that could change or disappear.

## Re-verification rule

If a memory file, prior document, or earlier stage's finding is used as a starting hypothesis, it must be re-verified against current state before the corresponding finding can be confirmed. "The memory says X" is a draft finding, not a confirmed one — see `_core/REVIEW-PRINCIPLES.md` §2.

## Confidence is not a substitute for evidence

A finding held with high confidence by the reviewing agent, but without a citable artifact, remains draft. Confidence and evidentiary strength are tracked separately in the finding schema.
