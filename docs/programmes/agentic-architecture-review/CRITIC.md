# Independent Critic Contract

The critic is a separate review pass from the primary executor. Its purpose is to challenge quality and gate readiness, not to produce a second architecture review.

## Review scope

Check:

1. Stage `CONTEXT.md` is fully populated and consistent with prior decisions and handoffs.
2. Investigation stayed within stage scope and authorised paths.
3. Current implementation, intended design and gap are separated.
4. Confirmed findings cite adequate authoritative evidence.
5. Conclusions follow from the evidence without overclaiming.
6. Required outputs and downstream handoffs are complete and mutually consistent.
7. Blocked/rejected/deferred capabilities remain correctly classified.
8. Human decisions are genuine choices rather than routine execution questions.
9. Material decisions have not been made by the executor without authority.
10. No production or unrelated working-tree changes were included.

## Required verdict

Return exactly one disposition:

- **PASS** — stage may advance if no blocking human decision remains.
- **REVISE** — correctable gaps exist; list each required correction and affected file.
- **STOP** — evidence, scope, safety or authority issue cannot be resolved within the stage.

## Decision classification

For every open question classify it as:

- `blocking-human-decision`
- `non-blocking-forwarded-decision`
- `implementation-specification`
- `evidence-gap`
- `not-a-decision`

The critic must actively reject artificial approval gates for formatting, naming, routine evidence gathering, mechanical file updates or questions already resolved by binding decisions.

## Output

Save the report as `<stage>/outputs/critic-review.md` with:

- verdict
- scope reviewed
- strengths
- required corrections
- decision classification
- evidence-quality assessment
- consistency assessment
- advancement recommendation

The critic may recommend corrections but must not silently edit the executor's findings or decisions.
