# Stage 06 Output: Statutory-Rule Change Control Design (C12) — Requirements Level

Defines the control workflow that must govern any change to `statutory_rule`/`tax_band` before C12 is built. Requirements only — Stage 08 owns the mechanism (schema, routes, state machine); Stage 09 owns the UI. Baseline: C12 is entirely greenfield (F-05-04, consumed per stage context — not re-verified here).

Binding boundaries inherited and preserved: C12 is a deterministic, compliance-owned capability separate from C11; C11 may only detect/compare/propose and must never author, execute, or deploy a production migration (D-02-04, D-03-01).

## 1. Why this workflow carries the platform's highest control weight

`statutory_rule` is **platform-level, not workspace-scoped** (F-01-45's decoupling migration). A single wrong approved change alters statutory deductions for **every workspace on the platform simultaneously** — the blast radius is every client of every bureau tenant. The control design below is deliberately heavier than the platform's workspace-scoped configuration changes; this asymmetry is intentional and must not be "simplified" away during implementation.

The current maintenance path demonstrates the risk concretely: the NG PAYE bands were seeded wrong (old PITA rates under an NTA-2025 label) and corrected only by a second developer-authored migration (`de1f2a3b4c5d`), which destructively replaced the bands with the correction's provenance recorded solely in a code docstring (evidence file §6). Under the current path there was no independent validation step to catch the original error before it took effect, and no database-resident record of either the error or the correction (F-06-04).

## 2. Roles and segregation of duties

Three distinct roles, with a hard segregation rule:

| Role | Responsibility | May be automated? |
|---|---|---|
| **Proposer** | Assembles the change: what changes, effective when, citing what source | Yes — C11 (proposal drafting only, D-02-04) or a human |
| **Validator** | Deterministic pre-checks: schema shape, duplicate/conflict detection, impact preview generation | Yes — must be deterministic platform code, never an LLM |
| **Approver** | A compliance-responsible human who reviews the proposal + validation results + impact preview and explicitly approves or rejects | **Never** — mandatory human gate (D-02-04; compliance-outcome-chain step 6: "not optional, not bypassable regardless of C11's confidence level") |

Segregation requirements:

- **Proposer ≠ Approver** for human-originated changes: the human who drafts a change must not be the same verified identity that approves it, *unless* the platform operator formally accepts single-operator risk (see §8 — this is a real constraint for a small bureau and is escalated, not silently decided).
- The Validator is not a role a person holds — it is a mandatory automated step that cannot be waived by either the proposer or the approver.
- The Approver must be a **verified identity** (see `attribution-identity-requirements.md`). An approval attributed to a caller-supplied string has no evidentiary value; C12 therefore hard-depends on C1 (auth) — consistent with Stage 05's readiness matrix, which already sequences C12 behind foundational identity work.

## 3. Required evidence per change (what the approver must see)

Every proposal, regardless of source, must carry all of the following before it can be presented for approval:

1. **Source citation** — per `compliance-monitoring-source-policy.md`: source identity, publication/gazette date, document reference or URL, and a verbatim excerpt of the operative regulatory text. For human-originated changes the same fields are mandatory (a human proposer is not exempt from citing the regulation).
2. **Effective date** — explicit `effective_from`, with the proposer's stated basis for it (the regulation's own commencement date, not an assumption).
3. **Exact rule diff** — the precise current-vs-proposed values (rates, bands, keys), computed deterministically against the live `statutory_rule`/`tax_band` state, not restated by hand or by an LLM.
4. **Impact preview** — which workspaces/pay periods would be affected, and a representative before/after calculation for at least one real (or realistic) employee profile per affected rule component. Stage 05 confirmed no code computes this today (F-05-04); it is a required deliverable of the C12 build, not optional.
5. **Validation results** — the deterministic Validator's output: duplicate/conflict check against the `(country_code, effective_from)` UNIQUE invariant, `rules_jsonb` shape/required-key validation (the platform's silent-Python-default behaviour on missing keys — Stage 01 F-01-46 territory — makes key validation a compliance control, not a nicety).

## 4. The approval record (mandatory content)

An approval (or rejection) must create a durable, immutable record containing, at minimum:

- proposal ID and full proposal content (or an immutable reference to it), including the source citation and impact preview *as shown to the approver at decision time*
- the approver's **verified** identity and the decision timestamp
- decision outcome (approved / rejected) and free-text reasoning (mandatory on rejection, recommended on approval)
- for approved changes: linkage to the resulting `statutory_rule`/`tax_band` rows actually written, and the write timestamp
- proposal origin: `C11` or `human`, with the proposer's verified identity when human

This record is compliance evidence and falls under the audit-expansion requirements (`audit-expansion-requirements.md`, domain 2) and the 7-year retention baseline (`agent-tool-audit-standard.md` §4). Today's audit mechanism cannot hold it: `audit_log` builders hardcode `entity_type = "PAYROLL_RUN"` (F-01-40, reconfirmed by Stage 05) — generalising that mechanism is a prerequisite for C12, owned by Stage 08.

## 5. Interaction with effective-dating and the UNIQUE invariant

- **Append-only rule history.** An approved change always creates a **new** `statutory_rule` row with a new `effective_from` (and its own `tax_band` rows where applicable). In-place mutation of an existing rule's values is prohibited once that rule has been used by any payroll run — the run's correctness evidence depends on the rule row it read. (The platform's own retry hardening already moved to snapshot-first reads, F-05-08; the control requirement here protects the same property from the write side.)
- **Corrections** (the `de1f2a3b4c5d` case — an existing rule row is discovered to be wrong) are a distinct change type: they must go through the same proposal/validation/approval workflow, and the record must state what was wrong, what runs (if any) consumed the wrong values, and whether recalculation/adjustment action is required. Whether a correction rewrites the faulty row or supersedes it with a same-date replacement is a Stage 08 mechanism question — but the control requirement is fixed: **the pre-correction values must remain durably recoverable from the database's own records** (not solely from git), and the correction must be attributable.
- **Pre-emptive duplicate validation.** The `(country_code, effective_from)` UNIQUE constraint stays as the last line of defence, but the Validator must check for conflicts *before* the approval step, so the approver never approves a change that then fails at the DB layer (Stage 05 confirmed no pre-emptive validation exists — the constraint is currently the only protection).
- **Effective-date resolution stays date-driven.** Consistent with the platform's hard-learned `payroll_rule.is_active` lesson (project rule: resolution must always pair `effective_from <= date` ordering; "active" flags never mean "current"), C12 must not introduce any "current rule" shortcut that bypasses date-driven resolution.
- **Rollback** of an approved-but-not-yet-effective change (effective date still in the future) is a normal workflow action: a new approval that withdraws the pending row, recorded like any other decision. Rollback of a change that has already been consumed by a payroll run is **not** a rollback — it is a correction (above), because run outputs already depend on it.

## 6. One workflow regardless of source (C11 vs human) — resolved, with reasoning

**Requirement: the workflow is identical regardless of whether the change was detected by C11 or by a human.** The only difference is the value of the proposal-origin field and the provenance attached to it.

Reasoning (recorded per the stage context's instruction to record it either way):

1. The risk being controlled is the *write to platform-level statutory data*, and that risk is identical whatever noticed the change first. A lighter path for human-noticed changes would simply become the bypass route around C11's controls.
2. D-02-04's containment argument (the compliance-outcome-chain's "why the separation matters": C11's worst failure is contained by C12's mandatory gate) only holds if C12's gate is unconditional. A source-dependent workflow reintroduces the coupling D-02-04 removed.
3. Evidence requirements don't meaningfully differ: a human proposer must still cite the regulation; C11 must still cite the regulation. The approval record needs the same fields either way.

No evidence surfaced during this stage that forces a distinction; none of the inherited decisions suggests one. This is recorded as an executor conclusion from inherited principles, not a new human decision (see stage `decisions.md`).

## 7. Impact assessment placement (Stage 04's open boundary question) — control requirement fixed, mechanism left open

Stage 04 forwarded the question of whether "assess affected clients/runs" belongs to C11 (in the proposal) or C12 (in the application workflow). At the **control level** this stage resolves what must be true, without adjudicating the mechanism split:

- The impact preview shown to the approver (§3.4) must be **computed deterministically against the exact proposed change and the live platform state at review time** — never an LLM restatement, and never only a stale assessment computed at detection time.
- If C11 includes an impact summary in its proposal, that summary is advisory context only; the authoritative preview the approver relies on is the Validator's (C12-side) computation.
- If material platform state changed between approval and application (e.g. new workspaces onboarded, a run created in an affected period), the application step must re-validate before writing — approval is of a specific diff against a specific state, not a blank cheque.

Whether the deterministic preview computation is *implemented* once and called from both sides is a Stage 08 design freedom. Forwarded as an implementation specification in `stage-08-handoff.md` — not a human decision.

## 8. Residual human decisions raised by this design

Two genuine choices are escalated (recorded in `decision-queue.md`, non-blocking for this stage):

- **DQ-007 — single-operator segregation waiver**: for a small bureau, requiring proposer ≠ approver may be operationally impossible on day one. Options: accept single-operator approval with compensating controls (mandatory cooling-off delay, second-channel notification), or hold the segregation rule and accept slower changes. A risk-appetite call only the human reviewer can make; must be resolved before C12 build authorisation, does not block this review's progression.
- **DQ-006 — authoritative-source adjudication** (see `compliance-monitoring-source-policy.md`): which external sources are *legally sufficient* is escalated, not decided.

## 9. Launch gate summary for C12

C12 may not launch until (register: `control-gate-register.md`, CG-12):

1. verified-identity approvals are possible (C1 shipped) — placeholder identity approvals are worse than none (the architecture document's own principle for `agent_session_log`, applied here to approvals)
2. the generalized audit mechanism can persist the §4 approval record
3. deterministic validation (duplicate/conflict + `rules_jsonb` shape) exists with test coverage, including a test that a UNIQUE-invariant conflict is rejected gracefully pre-approval
4. impact preview exists and is shown at approval time
5. append-only/correction handling (§5) is implemented, with the pre-correction-values-recoverable property tested
6. DQ-007 (segregation waiver) is resolved by the human reviewer
