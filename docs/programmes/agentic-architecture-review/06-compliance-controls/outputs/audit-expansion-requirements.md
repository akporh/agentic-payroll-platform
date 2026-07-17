# Stage 06 Output: Audit-Expansion Requirements for Compliance Evidence

Specifies the minimum audit coverage the platform must add — beyond today's `PAYROLL_RUN`-transition-only scope (F-01-40, reconfirmed by Stage 05's `audit-coverage-assessment.md`) — for compliance evidence to exist at all. **Requirements only; Stage 08 owns the mechanism** (schema, outbox, generalisation approach).

## 1. The four required audit domains

| # | Domain | What must be recorded | Why it is compliance evidence | Current coverage |
|---|---|---|---|---|
| 1 | **Domain-configuration change audit** | Create/update/deactivate on financially-consequential configuration: `salary_definition`, `pay_cycle`, `payroll_rule`, employee contract changes, component-metadata overrides — old value, new value, verified actor, timestamp | Configuration state at run time determines pay; explaining or defending any historical run requires knowing who changed what config when (also the gate on Stage 04's "operational reporting" outcome, F-04-06) | None (zero call sites outside payroll_run transitions — Stage 05) |
| 2 | **Statutory-change approval audit** | The full C12 approval record per `statutory-change-control-design.md` §4 | The platform's highest-blast-radius change class; currently unrecordable — the mechanism *cannot* hold it (builders hardcode `entity_type="PAYROLL_RUN"`, `audit_events.py:34,60`) | None |
| 3 | **Exception-resolution lifecycle audit** | Creation, ownership, evidence links, resolution and closure of exceptions (once the workflow exists — F-04-01); **immediately**: reconciliation resolution events | Exception-resolution records are compliance evidence per D-04-01's framing; reconciliation resolution is the live case today — `resolve_reconciliation` writes only `resolved_by`/`resolved_at` columns on the row, no durable cross-entity-queryable event (Stage 05 called this the single highest-value addition) | None |
| 4 | **Agent/tool invocation audit** | Per `agent-tool-audit-standard.md` §3 | The evidence chain for every LLM-mediated interaction; forward-looking (no agent layer exists yet) but binding on the first tool shipped | N/A yet — must exist before any tool ships |

## 2. Mechanism-generalisation requirement

The audit mechanism must accept arbitrary entity types. Today both payload builders hardcode `entity_type`/`aggregate_type = "PAYROLL_RUN"` (`backend/domain/payroll/audit_events.py:34,60`) and all 6+6 call sites are payroll-run transitions (Stage 05 re-verified list). Whether this is a signature generalisation or parallel builders is Stage 08's choice; the requirement is that domains 1–4 all become recordable.

## 3. Integrity properties every audit domain must satisfy

These four properties are requirements on the *mechanism*, verified against current code (evidence file `evidence/06-attribution-and-audit-integrity-excerpts.md`):

1. **Attributable** — actor identity on every record is a verified principal, never a caller-supplied string. Today `performed_by` arrives via an `X-Performed-By` header defaulting to `"admin@internal"`, a request-body `actor_id` defaulting to `"system@internal"`, or free-text `resolved_by` (F-06-01). Genuine system actions use named service principals, distinguishable from "identity unknown."
2. **Reliably written** — the audit record's persistence must be coupled to the state change it records. Today `save_audit_log`/`save_event` run post-commit in their own sessions, fire-and-forget (F-06-02): a failed audit write leaves a committed state change with no record and no alarm. The transactional-outbox direction the architecture document already commits to for events (its own Blocking Condition 3) satisfies this; the requirement here is that **audit records get the same guarantee, not just notification events**.
3. **Immutable / append-only** — no UPDATE/DELETE on audit records under normal operation, enforced at the DB layer (trigger or permissions), matching the protection already given to `payroll_result` rows for PAID runs (`3da637afb11b`). Today `audit_log`/`event_store` have no such protection (F-06-03).
4. **Retained** — per the retention baseline in `agent-tool-audit-standard.md` §2: 7-year working floor for payroll-relevant evidence, pending DQ-008's legal confirmation; today no retention policy exists in either direction (nothing purges, but nothing guarantees or protects either — F-06-03).

## 4. Sequencing note (aligned with Stage 05, not duplicating it)

Nothing in this document expands Stage 05's blocker register; it specifies *what the audit expansion must deliver* when Stage 08 designs it. The dependency order is unchanged: C1 (verified identity) precedes meaningful attribution anywhere; the outbox/consumer work (C2) is the natural vehicle for property 2; domains 1–3 need no agent layer and should not wait for one.
