# Severity Model

Applied only to confirmed findings (`F-` prefixed). Draft findings do not carry a severity rating — severity implies an established fact, and a draft is not yet established.

## Severity levels

| Level | Definition | Example class |
|---|---|---|
| **Critical** | Confirmed gap that creates financial, statutory, or data-integrity risk in current production use, or that breaks a documented data contract | Miscalculated statutory deduction; a status invariant violated in live data |
| **High** | Confirmed gap that will cause incorrect behavior or a broken workflow under realistic conditions, but is not yet observed causing live harm, or is contained to a non-financial path | A UI flow that silently drops data on save; a retry path that doesn't reproduce original results |
| **Medium** | Confirmed gap that degrades correctness, security posture, or usability under edge conditions, or represents meaningful technical debt | Missing workspace scoping on a low-traffic query path; inconsistent error handling |
| **Low** | Confirmed gap that is cosmetic, stylistic, or has negligible practical impact | Naming inconsistency; a redundant check that is harmless |
| **Informational** | Confirmed observation with no gap — recorded for completeness or to inform Stage 12/13 direction-setting | Current architecture choice that is intentional and working as designed |

## Severity is a judgment call, not a formula

Assigning severity requires the reviewer to weigh blast radius, likelihood, and reversibility. Where the severity assignment is not obvious from the finding's evidence alone, the reasoning is logged inline in the finding (a one-line justification) and, if contested or non-obvious, logged as a human decision in `_core/HUMAN-DECISIONS.md`.

## Severity does not set priority by itself

Severity describes the finding, not the roadmap response. Stage 13 (Approved Roadmap) is where severity, effort, and business priority are combined into an actual sequencing decision — that combination is a human decision, not an automatic function of severity alone.

## Consistency rule

The same severity level must mean the same thing across all stages. A stage must not invent a locally-scoped definition of "Critical" that differs from this table. If a stage believes this model doesn't fit a class of finding it's encountering, that is itself a human decision to log, not a silent local override.
