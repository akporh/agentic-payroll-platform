# Outcomes Registry

Top-level product outcomes. An outcome is a durable business result the platform exists to deliver — it does not change with every sprint and is not itself a unit of delivered work.

**Approved as a complete set 2026-07-28 (D-023).** Unlike the Phase 4A/4B rows, which were created one migration batch at a time to hold that batch's stories, this registry now holds the full outcome set, approved top-down as a whole. See `../programmes/product-traceability/hierarchy-proposal.md`.

## Identifier collision with the discovery document — permanent decode

`OUT-1`, `OUT-2` and `OUT-3` mean **different things** in this registry and in `../diagnostics/2026-07-15-retrospective-product-story-and-hierarchy-discovery.md` §5. Two documents that cite each other, using the same identifiers for different outcomes. Resolved by D-023: **this registry's numbering is authoritative; the discovery document's is superseded and historical.** Never resolve an outcome by the discovery document's numbering.

| This registry | Discovery document §5 | Outcome |
|---|---|---|
| `OUT-1` | `OUT-3` | Governed, auditable payroll execution |
| `OUT-2` | `OUT-4` | Sustainable delivery process |
| `OUT-3` | `OUT-2` | Operationally usable payroll administration |
| `OUT-4` | `OUT-1` | Accurate, compliant statutory payroll calculation |
| `OUT-5` | `OUT-5` | AI-assisted payroll operations *(the one identifier that happens to agree)* |

## Schema

| Column | Meaning |
|---|---|
| `outcome_id` | Stable identifier, format `OUT-<n>`. Never reused, never renumbered. |
| `name` | Short name of the outcome. |
| `description` | One or two sentences describing the durable business result. |
| `status` | `active` \| `achieved` \| `deprecated` \| `planned`. |
| `capabilities` | Comma-separated list of `capability_id`s that serve this outcome (see `CAPABILITIES.md`). |
| `evidence_notes` | Free text — where the case for this outcome's existence is documented. |

## Registry

| `outcome_id` | `name` | `description` | `status` | `capabilities` | `evidence_notes` |
|---|---|---|---|---|---|
| `OUT-1` | Governed, auditable payroll execution | Execution and audit-trail data must let an auditor verify how a stored value was derived, not just what the value is — without needing to re-query live DB state. | `active` | `CAP-1`, `CAP-7`, `CAP-8` | Discovery document §5 (as its `OUT-3`). Evidenced by the Track Q rolling audit register (`../ROADMAP.md`) and the closed audit reports `../audit/2026-05-01-sprint-10-audit-review.md`, `../audit/2026-05-02-sprint-11-audit-review.md`, `../audit/2026-07-12-aud-q1-trace-source-audit-review.md`. |
| `OUT-2` | Sustainable delivery process | Security, audit, and delivery-process discipline that does not itself ship a user-visible payroll feature but is the reason later features can be trusted. | `active` | `CAP-2`, `CAP-10`, `CAP-11` | Discovery document §5 (as its `OUT-4`). Evidenced by the Track S security rolling register (`../ROADMAP.md`) and the ICM sprint-workflow's own gate mechanics (`../sprints/STAGE-REGISTRY.md`, `../sprints/WORKFLOW.md`). |
| `OUT-3` | Operationally usable payroll administration | Onboarding, workspace configuration, and employee-lifecycle management must be usable by a bureau operator through a UI, not just theoretically possible via raw data entry. | `active` | `CAP-3`, `CAP-4`, `CAP-5`, `CAP-9` | Discovery document §5 (as its `OUT-2`). Evidenced by `../ROADMAP.md` capability areas A1+A2 and A3, and the Track UI design-system gates. |
| `OUT-4` | Accurate, compliant statutory payroll calculation | Gross-to-net calculation, statutory deductions and proration must be correct to the naira and defensible against the governing Act — the platform's core reason to exist. | `active` | `CAP-6` | Discovery document §5 (as its `OUT-1`) — proposed there but never adopted, so it had **no home in this registry at all** until D-023. The single largest cluster of delivered work: capability area A4 plus Tracks K/L/M. |
| `OUT-5` | AI-assisted payroll operations | Agentic assistance over payroll operations — Phase 2. | `planned` | `CAP-12` | Discovery document §5. **Zero delivered stories.** Retained deliberately (D-023, OQ-6) so the unbuilt agentic work is visible as a named gap rather than an unstated absence. Tracks P/V/W/X/Y in `../ROADMAP.md`. |
