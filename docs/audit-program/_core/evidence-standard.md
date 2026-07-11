# Evidence Standard

Applies to every finding logged in every stage of this audit programme.

## Acceptable evidence types

Only these count as evidence. Nothing else does — not recollection, not
a prior document's assertion on its own, not "this looks wrong."

1. **Code reference** — an exact `file:line` (or `file:line-range`)
   citation of the current implementation, quoted or closely paraphrased.
2. **Test result** — output of an existing test, or a newly written test,
   run against the current codebase, with the command and result recorded.
3. **Database evidence** — output of a **read-only** query against a real
   or representative database, saved into the stage's `evidence/` folder.
4. **Controlled execution trace** — output/log from a deliberately run,
   non-production execution (e.g. a simulation script under `scripts/` or
   `backend/scripts/`, or a test harness run), saved into `evidence/`.

## Status ladder

Every finding is assigned exactly one status:

- **unconfirmed** — asserted, but no evidence attached yet. This is the
  default status for any newly raised suspicion, including ones sourced
  from a historical document (see below).
- **plausible** — at least one piece of evidence supports it, but it is
  not yet independently reproduced or is based on indirect evidence
  (e.g. a code reference alone, without a test or DB confirmation).
- **confirmed** — reproduced or directly demonstrated by at least one of
  the four evidence types above, cited by file path in the finding's
  `evidence` field.
- **rejected** — investigated and evidence shows the suspected defect
  does not exist, or is intended behaviour per `CLAUDE.md` or the
  business rules catalogue.

**A finding may not be marked `confirmed` without a citation into that
stage's `evidence/` folder or a direct `file:line` code reference.**

## Historical documents are not evidence on their own

`docs/analysis/`, `docs/audit/`, `docs/architecture/`, and any file under
`docs/Buisness Specs & Designs (Drifted)/` may motivate an investigation
but can never, by themselves, promote a finding past `unconfirmed`. They
must be reverified against current code, a test, or the database before
the finding can move to `plausible` or `confirmed`.

## Evidence file naming

Files dropped into a stage's `evidence/` folder use:

```
evidence/YYYY-MM-DD-<short-slug>.<ext>
```

Example: `evidence/2026-07-14-executor-fallback-callers.txt`. Findings cite
these files by relative path in their `evidence` field — evidence is never
pasted inline into `findings.md`.
