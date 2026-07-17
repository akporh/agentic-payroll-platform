# Independent Critic Review — Stage 06: Compliance & Controls

- **Critic pass date**: 2026-07-17
- **Independence**: this critic pass was run in a fresh session, independent of the Stage 06 executor session, from repository state alone (per D-004). No executor conversational context was available or used.
- **Contract**: `docs/programmes/agentic-architecture-review/CRITIC.md` (10 review checks, verdict rules, decision-classification taxonomy)
- **Code verification basis**: all spot-checks were run against git commit `265db103cfb6a6b490c8655d5ceb4b776303e6fe` (the commit the stage's evidence pins), via `git show`/`git grep`, plus the current working tree for state-file and unrelated-change checks.

## Verdict

**REVISE**

Three correctable gaps exist (listed under Required Corrections). None of them changes any finding's conclusion, any output's requirements, any gate, or any handoff — every substantive claim I spot-checked resolved correctly against source. No blocking human decision exists. The corrections are narrow; a targeted re-check rather than a full re-review is sufficient afterwards.

## Scope reviewed

- **Contract and programme context**: `CRITIC.md`, `POLICY.md`, `RUNBOOK.md`, `review-state.md`, `state.md`, `decision-queue.md`, `_core/HUMAN-DECISIONS.md`, `_core/FINDING-SCHEMA.md`.
- **Stage 06 material**: `CONTEXT.md`, `findings.md` (F-06-01..05), `decisions.md` (incl. executor judgment calls E-06-1..5), `evidence/06-attribution-and-audit-integrity-excerpts.md`, and all 9 outputs (statutory-change-control-design, compliance-monitoring-source-policy, agent-tool-audit-standard, audit-expansion-requirements, attribution-identity-requirements, tenant-isolation-control-assessment, control-gate-register, stage-07-handoff, stage-08-handoff).
- **Upstream consistency**: `03-agent-portfolio/outputs/stage-06-handoff.md`, `03-agent-portfolio/outputs/tool-portfolio-matrix.md` ("Required audit record" column), `04-outcome-discovery/outputs/compliance-outcome-chain.md` (steps 2 and 6), `05-platform-readiness/outputs/stage-06-handoff.md`, Stage 05 `findings.md` (field-pattern precedent), `_inputs/source-register.md` (S-08 entry).
- **Source-code spot-checks at commit `265db10`** (citation → resolved?):
  1. `backend/api/routes/payroll.py` — `X-Performed-By` header defaulting to `"admin@internal"` on retry/approve/lock (cited :1146/:1173/:1193) — **resolved** (definitions present at the cited region at the pinned commit; note they have since drifted ~34 lines at HEAD `b398c72`, which is acceptable because the evidence pins the commit).
  2. `payroll.py` — body `actor_id` default `"system@internal"` on pay; free-text body `resolved_by` on reconciliation resolution — **resolved**.
  3. `payroll.py:958/:975` — `performed_by="system"` / `"admin@internal"` literals — **resolved**.
  4. `backend/application/payroll_approval_service.py:44,114,187` and `payroll_retry_service.py:497,508,680` — hardcoded `performed_by: str = "admin@internal"` defaults — **resolved**.
  5. `payroll_approval_service.py:88–102` — `db.commit()` followed by post-commit `save_audit_log`/`save_event`, comment verbatim — **resolved**.
  6. `backend/infra/repositories/audit_log_repo.py` — `save_audit_log` opens its own `SessionLocal()`, INSERTs, commits, closes — **resolved**.
  7. Trigger sweep — `git grep "CREATE TRIGGER"` over `migrations/versions/` at `265db10` — **conclusion resolved, enumeration wrong** (see RC-1): the grep returns **10** migration files, not the 4 the evidence names; I checked all 10 individually and **none references `audit_log` or `event_store`** — the operative claim of F-06-03 is correct.
  8. Retention/purge sweep — `retention|purge|DELETE FROM audit_log|DELETE FROM event_store` over `backend/` + `migrations/versions/` (excluding tests) — **resolved** (zero matches, as claimed).
  9. `ea05e71efbd7` header — "We intentionally do NOT constrain event_store or audit_log payloads" — **resolved**.
  10. `backend/infra/db/models/statutory_rule.py` — full column list exactly as claimed; no `created_at`/`updated_at`/citation/approval fields — **resolved**; `a0b1c2d3e4f5` covers exactly `grade, designation, salary_definition, payroll_rule, pay_cycle` and not `statutory_rule` — **resolved**.
  11. `de1f2a3b4c5d` — destructive `DELETE FROM tax_band` + re-INSERT; Act citation and old values only in docstring/`_OLD_BANDS` — **resolved**.
  12. `backend/domain/payroll/audit_events.py` — `entity_type`/`aggregate_type` hardcoded `"PAYROLL_RUN"` — **resolved**.
  13. `docs/architecture/agent-layer-architecture.html` lines 496, 938, 1150–1151 — the three quoted design statements — **resolved verbatim**.
  14. Baseline `5aa34350e00f` `audit_log`/`event_store` schemas — **resolved** (matches evidence §3; `performed_by` is a plain String, no FK).

## Strengths

1. **Evidence discipline is genuinely strong on substance.** Fourteen of fourteen substantive citation checks resolved against the pinned commit, including the verbatim architecture-document quotes and the absence claims duplicated into the evidence file per the standard. The commit-pinning practice (`265db10`) protected the citations against the line drift that has already occurred at HEAD.
2. **Boundary discipline is exemplary.** Every output consistently separates the control *requirement* (fixed here) from the *mechanism* (Stage 07/08), the *legal parameter* (escalated), and the *product calibration* (Stage 08/11). The stage was explicitly instructed not to adjudicate the legal source-authority question and did not — DQ-006 is escalated with a recommended resolution path, exactly as the context demanded. E-06-3 cleanly separates "align tool-call retention with the source document's own design" (a derivation, within authority) from "is 7 years the legally correct number" (escalated as DQ-008).
3. **Transparent executor judgment log.** `decisions.md`'s E-06-1..5 section pre-declares every judgment call for the critic to challenge — including deliberately contestable line-drawing (E-06-5, not upgrading F-05-11). This is the right way to satisfy CRITIC checks 8/9, and on review each call holds: E-06-1's "one workflow regardless of source" genuinely follows from D-02-04's containment logic plus Stage 03's own anticipation; a human gate there would have been artificial.
4. **The classification contribution of F-06-05 is real analysis, not restatement.** The "false attestation" framing (a control that appears to exist defeats review as well as isolation) and the control-failure vs control-environment-failure vs control-weakness three-way split give Stage 07 and Stage 13 something Stage 05's technical severity did not already carry — while explicitly not re-rating F-05-03's severity (no double-counting).

## Required corrections

### RC-1 — Evidence file misreports the trigger-sweep result (factual inaccuracy in a confirmed finding's evidence)
- **Files**: `06-compliance-controls/evidence/06-attribution-and-audit-integrity-excerpts.md` §4; `06-compliance-controls/findings.md` (F-06-01 unaffected; **F-06-03** "Current implementation" repeats the enumeration).
- **Defect**: the evidence states the CREATE TRIGGER sweep found triggers "only for" four migrations (`0daab4ac893b`, `3da637afb11b`, `4907cf6eb08f`, `9901bc4ed0c5`). The same grep at the pinned commit returns **ten** migration files, including live protections absent from the list: `d9828ee962a2` (`trg_prevent_paid_run_update` on `payroll_run` — cited as live by `pay_run`'s own docstring), `f45614d5aa92` (salary_definition paid-lock), `a1b2c3d4e5f6`/`fe0bad282b7d` (snapshot immutability), `e2f3a4b5c6d7`, `f1a2b3c4d5e6`.
- **Impact**: the operative conclusion — no trigger references `audit_log`/`event_store` — is **correct** (I verified all ten files individually), and the misstatement *understates* the platform's existing immutability precedent, so no output or gate changes. But the evidence record is the permanent citable artefact, and a Stage 07 threat model consuming it as a DB-protection inventory would be misinformed. Correct the sweep report to the full result set (or reword to "10 trigger-bearing migrations, all on payroll/config tables; none references the audit tables").

### RC-2 — Findings file claims a schema it does not follow
- **File**: `06-compliance-controls/findings.md` (all five findings).
- **Defect**: the file header claims "Schema: `_core/FINDING-SCHEMA.md`, extended with the Stage 05 field pattern per this stage's `CONTEXT.md` finding discipline," and `CONTEXT.md`'s finding-discipline section mandates the extended fields (consequence / classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner — as Stage 05's findings actually carry). No F-06-* finding carries those fields; they satisfy only the core schema.
- **Impact**: the content mostly exists but is scattered (closure evidence in the CG register, owners in the handoffs, remediation in the outputs) — later stages citing F-06-* by ID will not get the per-finding remediation/closure/owner fields the programme's own precedent set. **Preferred fix**: add the extended fields to F-06-01..05 (the material is already written elsewhere; this is consolidation, not new investigation). Acceptable alternative: amend the header and the CONTEXT discipline claim to the core schema — but that weakens the citable record and I do not recommend it.

### RC-3 — `state.md` is stale against POLICY's truthful-update duty
- **File**: `docs/programmes/agentic-architecture-review/state.md`.
- **Defect**: "Blocked or outstanding decisions" still says the queue holds "DQ-001–003" (it now holds DQ-001–008, including this stage's three), and "Next permitted action" still names the Stage 06 primary-executor pass as the next loop action (it is complete; the stage is `awaiting-critic`).
- **Impact**: `review-state.md` and `decision-queue.md` — the authoritative files — are correct, and `state.md` explicitly defers to them for stage position, so the session-independence risk is low. But POLICY requires `state.md` be updated truthfully, and D-004 makes stale persisted state a close-out defect. Mechanical fix.

**Not a correction (informational):** line-number citations into `backend/api/routes/payroll.py` have drifted at HEAD (`b398c72` added ~34 lines above the cited routes). No action needed — the evidence pins commit `265db10` and resolves there — but Stage 07, which is directed to "start from" F-06-01's evidence, should re-resolve line numbers at its own commit.

## Decision classification

Per the CRITIC.md taxonomy, every open question raised by or through this stage:

| Item | Classification | Assessment |
|---|---|---|
| DQ-006 — Tier-1 authoritative-source allowlist (legal sufficiency for FIRS/PenCom) | `non-blocking-forwarded-decision` | **Correct.** Genuine legal-risk determination requiring professional advice; correctly framed as a hard gate on C11 *build authorisation*, not on review progression. Not artificial — the stage context explicitly ordered escalate-don't-decide. |
| DQ-007 — single-operator segregation-of-duties waiver for C12 | `non-blocking-forwarded-decision` | **Correct.** A real risk-appetite choice with two reasonable options (compensating controls vs held segregation); only the human reviewer can make it; correctly sequenced pre-C12-build. |
| DQ-008 — legal basis of the 7-year retention figure | `non-blocking-forwarded-decision` | **Correct.** The source document asserts 7 years without basis; statutory minimum and data-protection maximum both need professional confirmation. The "keep-at-least-7y working floor, build no deletion mechanism yet" interim posture is the right conservative default and does not pre-empt the decision. |
| E-06-1 — one workflow regardless of C11-vs-human source | `not-a-decision` | **Concur.** Resolved by D-02-04's containment logic + absence of any evidence forcing a distinction; Stage 03 anticipated the same answer. A human gate here would have been an artificial approval gate, which the contract requires me to reject. |
| E-06-2 / impact-preview computation placement (Stage 04's boundary question) | `implementation-specification` | **Concur.** The control constraint is fixed (deterministic, live-state, C12-side authoritative); single-vs-shared implementation is Stage 08 design freedom. |
| E-06-3 — tool-call retention aligned to `agent_session_log`'s 7 years | `not-a-decision` (derivation), with the legal parameter split out as DQ-008 | **Concur.** `tool_calls_jsonb` is a column of `agent_session_log` in the source design (verified, line 938) — the alignment formalises existing intent rather than making a new compliance choice. |
| Historical audit rows with self-asserted identity — remediate or cut-over epoch | `implementation-specification` (forwarded to Stage 07/08 in stage-07-handoff) | **Concur.** The past cannot be re-attributed; the epoch treatment is the only plausible shape and needs mechanism design, not a human risk call. |
| R5 — step-up auth vs live-session check for C12 approvals | `implementation-specification` (Stage 07 design choice within a fixed control requirement) | **Concur.** |
| C11 monitoring cadence | `implementation-specification` / product calibration (Stage 08/11) | **Concur** — the control-relevant part (explicit, recorded, alert-on-stall) is fixed; the number is calibration. |
| RC-1..3 above | `evidence-gap` (RC-1) / mechanical corrections (RC-2, RC-3) | Correctable within the stage; none is a human decision. |

**No blocking human decisions exist.** No artificial approval gates were created; the three forwarded decisions are all genuine product/legal/risk choices that evidence cannot settle.

## Evidence-quality assessment

- **Substantive accuracy: high.** All fourteen citation spot-checks resolved at the pinned commit, including the load-bearing negatives (no triggers on audit tables, no retention mechanism, no provenance columns on `statutory_rule`). Absence claims were correctly duplicated into the evidence file as grep-sweep records rather than left as bare assertions.
- **One defect: RC-1.** The trigger-sweep enumeration misreports its own grep result (4 files named, 10 returned). The conclusion survives; the record does not, as written. This is the only place where the stage's evidence text and the repository diverge.
- **Separation of current / intended / gap: clean throughout.** F-06-04's "intended design: undocumented" is exactly right (no spec claims DB-resident provenance today; the requirement is established by this stage's own design plus D-02-04 — the finding says so rather than inferring intent). F-06-05 correctly labels itself as classification-of-consumed-facts, not new technical fact, and avoids re-rating Stage 05's severities.
- **No overclaiming detected.** Severity ratings are deliberately conservative with recorded reasoning (F-06-01 High-not-Critical to avoid double-counting F-05-01; F-06-02 Medium as an edge-condition gap; F-06-04 Medium with the Critical trigger correctly relocated to CG-12). Consumed Stage 05 facts are consistently marked "not re-verified here, per stage context" — the consume-don't-re-derive instruction was followed, and the stage's *new* claims all have fresh code reads behind them.

## Consistency assessment

- **Findings ↔ outputs ↔ handoffs: consistent.** F-06-01→R1/R3 and the stage-07 handoff; F-06-02/03→audit-expansion properties 2–3 and the stage-08 handoff's outbox/trigger items; F-06-04→control-design §5 and the stage-08 schema item; F-06-05→tenant assessment→CG-1/CG-8. CG-12's gate list matches control-design §9 item-for-item; CG-8 matches tenant assessment §3; SC-4 matches the DQ-008 interim posture.
- **Upstream handoffs answered.** Stage 03's four asks (C12 workflow, C11-vs-human question, UNIQUE-invariant interaction, tool-audit retention/fields) and Stage 05's four handoff items are each traceably resolved in the outputs. The tool-portfolio-matrix's "Stage 06 to confirm retention requirement" is resolved (verified the column text exists as described), including C10's "Stage 06 to confirm requirements" flag (CG-10). The compliance-outcome-chain quotes used to ground the mandatory human gate are verbatim (verified steps 2 and 6).
- **Binding decisions preserved.** D-02-04 (C11 detect/compare/propose only; no migration authoring — restated, not reopened), D-03-01 (15-capability portfolio; all dispositions preserved: C4 blocked, C8 blocked, C9 rejected, C11 restricted, C15 deferred), D-02-02/03 (CG-8 restates rather than weakens), D-04-01 (CG-7 keeps the exception-resolution hard gate). No output weakens a gate to a documentation warning; the register states the anti-weakening rule explicitly.
- **Stage-tracking files**: `review-state.md`, `CONTEXT.md` status, `findings.md`, `decisions.md`, and `decision-queue.md` all agree (5 confirmed findings, 0 draft, 0 parked, 9 outputs, DQ-006/007/008). **Exception**: `state.md` is stale (RC-3).
- **Scope and authority**: all Stage 06 writes are inside `docs/programmes/agentic-architecture-review/` (stage files, `_inputs/source-register.md` S-08 entry, `decision-queue.md`, `review-state.md`). The working tree's other modifications (`docs/ROADMAP.md` phase renumbering, `docs/sprints/CURRENT.md`, test-harness file moves, `docs/ux-design-brief/`) were inspected and are unrelated delivery-workstream changes not claimed by, or attributable to, Stage 06 — check 10 passes. The stage made no mechanism, security, UI, or commercial decisions; the one place it touches Stage 11 (marketing claim bounded by the source policy) is a boundary flag, not a decision.

## Advancement recommendation

**Do not close Stage 06 yet.** Return RC-1, RC-2 and RC-3 to the executor as named corrections:

1. RC-1 — correct the trigger-sweep enumeration in the evidence file §4 and F-06-03 (conclusion stands; only the reported sweep result changes).
2. RC-2 — add the extended Stage 05 field pattern to F-06-01..05 (preferred), consolidating content that already exists in the outputs.
3. RC-3 — refresh `state.md`'s decision-queue reference and next-action line.

None of these requires re-investigation, changes any conclusion, gate, requirement, or handoff, or raises a human decision. After the corrections, a **narrow re-critic pass confined to the three corrected items** is sufficient; on confirmation, the expected disposition is PASS with no blocking human decision, upon which the controller may close Stage 06 and open Stage 07 automatically per `RUNBOOK.md`. DQ-006/007/008 remain correctly queued as non-blocking forwarded decisions and do not hold the stage.

---

# Re-critic addendum (2026-07-17)

Narrow re-critic pass confined to RC-1/RC-2/RC-3 per the advancement recommendation above. Same independence basis: fresh read of repository state; verification re-run against the unchanged evidence pin (commit `265db10`). The rest of the stage was not re-reviewed and its prior assessment stands.

## Per-correction verification

- **RC-1 — VERIFIED.** `evidence/06-attribution-and-audit-integrity-excerpts.md` §4 now reports the trigger sweep as **10** trigger-bearing migrations, naming each; the list matches my own `git grep "CREATE TRIGGER"` result at `265db10` exactly (`0daab4ac893b`, `3da637afb11b`, `4907cf6eb08f`, `9901bc4ed0c5`, `a1b2c3d4e5f6`, `d9828ee962a2`, `e2f3a4b5c6d7`, `f1a2b3c4d5e6`, `f45614d5aa92`, `fe0bad282b7d`). The operative conclusion ("none references `audit_log` or `event_store`") is stated accurately and matches my independent per-file check of all ten from the original pass. A dated correction note preserves the audit trail of the change, and F-06-03's "Current implementation" enumeration was updated to match. The fuller list strengthens, not weakens, F-06-03's existing-precedent point — as the correction note itself observes.
- **RC-2 — VERIFIED.** All five findings (F-06-01..05) now carry the extended Stage 05 field pattern: consequence / classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner. I checked each added field against the outputs it consolidates from: remediation and closure items trace to `attribution-identity-requirements.md` (R1, cut-over epoch), `audit-expansion-requirements.md` §3, `stage-07-handoff.md`/`stage-08-handoff.md`, `tenant-isolation-control-assessment.md` §3, `statutory-change-control-design.md` §5/§9, and the CG register (CG-1/2/8/12, SC-1/3/4). No new claims, no severity changes, no silent conclusion changes; the "required human decision" fields correctly reference only the already-queued DQ-007/DQ-008 as non-blocking and mark the cut-over epoch as an implementation specification, consistent with the stage's prior classification. One note, not a defect: attaching DQ-007 to F-06-04's decision field is a slightly broad placement (DQ-007 concerns the approval workflow rather than the provenance schema specifically), but it is consistent with CG-12's existing gate list and introduces nothing new.
- **RC-3 — VERIFIED.** `state.md` is cured: last-updated stamped 2026-07-17; the outstanding-decisions line now reads DQ-001–008 and names Stage 06's DQ-006/007/008; the next-action line defers to `review-state.md` as authoritative and truthfully reflects the REVISE → corrections-applied → narrow re-critic position. The staleness identified in the original report no longer exists.

## Final verdict

**PASS**

## Blocking human decisions

**None.** DQ-006 (Tier-1 source allowlist legal sign-off), DQ-007 (single-operator segregation waiver), and DQ-008 (retention legal basis) remain correctly classified as non-blocking forwarded decisions gating future C11/C12/retention-mechanism builds — none blocks Stage 06 closure or Stage 07 opening. Per `RUNBOOK.md`, the controller may close Stage 06 and open Stage 07 automatically.
