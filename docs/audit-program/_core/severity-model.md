# Severity Model

Every finding is assigned exactly one severity, using both the code and the
label together (e.g. "S0 — Critical"), never one alone.

| Code | Label | Definition |
|---|---|---|
| **S0** | **Critical** | Statutory/financial miscalculation, cross-tenant data leak, silent data corruption, or violation of a `CLAUDE.md` data-contract invariant (e.g. a `MATCHED` reconciliation row with `actual_total != expected_total`, an `APPROVED` run with modified results). |
| **S1** | **High** | A silent failure that masks a real error — swallowed exception, unlogged fallback to a legacy path, `str(e)` leaking to a client, a retry that silently diverges from the original run without surfacing the divergence. |
| **S2** | **Medium** | A correctness risk that exists under specific or edge conditions not yet observed in production — e.g. an untested proration boundary, a config combination that hasn't been exercised. |
| **S3** | **Low** | Code quality, duplication, or simplification opportunity with no correctness impact — e.g. the `scripts/` vs `backend/scripts/` overlap, an unused parameter. |

## Escalation rule

Any **S0 — Critical** finding is logged into
`_core/human-decisions.md` the moment it reaches `plausible` or `confirmed`
status — it is not held until Stage 13.

## Severity is independent of confidence

Severity (impact if true) and status (`unconfirmed` / `plausible` /
`confirmed` / `rejected`, per `evidence-standard.md`) are separate axes. An
`unconfirmed` finding can still be provisionally labelled `S0` if the
hypothesis, were it true, would be critical — this ensures high-impact
suspicions aren't deprioritized just because they haven't been evidenced
yet. Stage 13 prioritizes primarily by status-then-severity: confirmed S0/S1
first, then plausible S0/S1, then the rest.
