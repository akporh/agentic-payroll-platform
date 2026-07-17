# Stage 08 — Independent Critic Review

Produced by the independent critic pass (read-only agent, fresh context) on 2026-07-17, per `CRITIC.md`. Report reproduced verbatim below; controller disposition follows at the end.

---

**Reviewer:** Independent critic pass per `docs/programmes/agentic-architecture-review/CRITIC.md`
**Date:** 2026-07-17 · **Executor commit reviewed:** `2e9af8d` (evidence pinned at `573be0d`; the single intervening commit is documentation-only, so the working tree's code is identical to the pinned commit)

## Verdict

**PASS**

Zero blocking corrections. Two non-blocking evidence-precision/housekeeping items are listed below for the controller to apply at its discretion pre-closure (Stage 07 precedent: the route-denominator recount).

## Scope reviewed

- Contract and governing docs: `CRITIC.md`, `RUNBOOK.md`, `review-state.md`, `decision-queue.md`, stage `CONTEXT.md`, `findings.md`, `decisions.md`, `evidence/08-code-grounding-excerpts.md`.
- All 10 executor outputs under `08-technical-architecture/outputs/`.
- Binding upstream constraints re-read in full: Stage 07 `stage-08-handoff.md` (items 1–10), `identity-architecture-requirements.md` (T1–T7, R1/R2, DEC-07-02), `tool-layer-security-pattern.md` (P1–P8 + §3 verification), `audit-integrity-threat-model.md` (§4 floor, §6 epoch), `approval-security-design.md` (R4/R5, DEC-07-03), `security-gate-register.md` (SG-1–15, SS-1–4); Stage 06 `stage-08-handoff.md`, `statutory-change-control-design.md` (§§2–9), `audit-expansion-requirements.md` (domains 1–4, properties 1–4), `agent-tool-audit-standard.md` (SC-3, DQ-008); Stage 05 `stage-08-handoff.md`, `readiness-closure-plan.md`; Stage 03 `stage-08-handoff.md`, `tool-portfolio-matrix.md`; Stage 04 `anomaly-detection-outcome-policy.md` (D-04-01).
- Independent code re-verification against the working tree (details below).
- `git show --stat 2e9af8d`: **17 files changed, all under `docs/programmes/agentic-architecture-review/`** — no production code, test, or migration touched. Working tree clean.

## Strengths

1. **Every load-bearing code citation survives independent re-verification.** I re-read each cited site myself rather than trusting the excerpts: the statutory resolution query with `ORDER BY effective_from DESC, version DESC` (`payroll.py:270-282`), the UNIQUE constraint making the tie-break currently unreachable per country (`statutory_rule.py:9-11`), the four-plus independent transactions in the persister (`payroll_run_persister.py:68-105` calling per-repo `SessionLocal()`/`commit()` in `audit_log_repo.py`/`event_store_repo.py` — confirmed by direct read), hardcoded `PAYROLL_RUN` at `audit_events.py:34,60`, all seven caller-supplied-actor sites (`payroll.py:992/1009/1180/1207/1227/1257/1359-1365` plus `payroll_retry_service.py:510`), the reconciliation trio at `payroll.py:1327/1336/1352` with `get_run_timeline` at `1371` and `legacy_executor_stats` at `1378`, the legacy unscoped route at `1270`, the sibling guard pattern at `1071-1087` (`WHERE payroll_run_id = :rid AND workspace_id = :wid` → 404), the trigger precedent `3da637afb11b`, the executor purity docstring (`executor.py:10`), `run_sequential_payroll` at `sequential_executor.py:650`, `load_inputs_for_run` at `payroll_input_repo.py:82` (no workspace parameter — confirmed), `workspace_info()` at `workspace.py:133-134`, and `backend/scripts/simulate_payroll.py` (exists). F-08-01 and F-08-02 are genuinely load-bearing, correctly evidenced, and correctly classified.
2. **F-08-01 is exactly the kind of finding a design stage should produce**: a pre-existing, committed, currently-unreachable code property (the `version DESC` tie-break) turned into the evidence-grounded basis for the correction mechanism, with the required data-contract change surfaced explicitly rather than smuggled in.
3. **Discipline on inherited constraints is exemplary.** Every design opens by naming its binding requirements and closes with a requirements-satisfaction table naming the verification method — the stage's own completion criterion, met uniformly across all seven mechanism designs plus per-item closure evidence in the remediation design. The DQ-008 answer-by-absence (DEC-08-15) is verified: no TTL, purge, or archival mechanism appears in any schema in any output.
4. **The dry-run design (DEC-08-11) is the strongest single answer in the stage**: the reuse-vs-bypass table, the no-`payroll_run`-row reasoning grounded in the platform's own enum-overload prohibition and consumer inventory (`is_first_paid_month` at `payroll.py:245-260` — verified), and the input-hash commit linkage that converts C13's safety gate from workflow convention into checkable evidence.

## Required corrections

**None blocking.** Two non-blocking items:

1. **[evidence precision — non-blocking]** `outputs/tool-contracts.md` §3.4 cites "the HTTP-layer coercion at `payroll.py:1129` (which coerces to `[]`)". Line 1129-1131 is the `component_trace_jsonb` column in the SELECT; the actual coercion expression `r[7] or []` is at `payroll.py:1163`. The claim's substance is verified true; only the line pointer is imprecise (carried verbatim from Stage 05's handoff citation). Controller may correct pre-closure.
2. **[mechanical housekeeping — non-blocking, explicitly not a gate]** `_inputs/source-register.md` carries re-read entries for Stages 05 and 06 but none for Stages 07/08, and its trailing "next action" line is stale ("then Stage 07"). The codebase source is already registered (S-01/S-06/S-08) and Stage 08's snapshot basis (`573be0d`, clean tree, branch, date) is fully stated in its own evidence file, so provenance is not actually degraded — this is register hygiene inherited from Stage 07's pass, flagged for the controller, not a revision gate per CRITIC.md's artificial-gate rule.

## Decision classification

| Item | Classification | Assessment |
|---|---|---|
| DQ-001 (C7 formulas) | implementation-specification — **resolved** | Correctly resolved by `anomaly-detection-design.md` §§2–3 within D-04-01's delegated freedom ("final formulas, thresholds, min-window are Stage 08's to set"). Layering not re-opened; launch values remain tunable via the versioned threshold table. |
| DQ-002 (C10 rules) | implementation-specification — **resolved** | Correctly resolved by `confirmation-protocol-design.md` §3; the security constraints from approval-security §4 (freezing, expiry records, idempotency) are all designed in, and rejection-not-supersession is justified on T7 grounds. |
| DQ-003/DQ-004 (dry run) | implementation-specification — **resolved** | Correctly resolved by `dry-run-mechanism-design.md` §§1–2; matches the Stage 05 critic's classification of DQ-004. |
| DQ-005 (CORRECTION in UI) | non-blocking-forwarded-decision | Correctly untouched; forwarded to 09/11 and referenced in the Stage 09 handoff item 8. |
| DQ-006/007/008 | non-blocking-forwarded-decision (human-gated pre-build) | Untouched, as required. DQ-007 not pre-empted (segregation check ships; waiver path added only if granted; TOTP slot exists without hard-gating MFA). DQ-008's mechanism constraint honoured by absence. |
| DEC-08-01–15 | executor design conclusions within delegated freedoms | Verified each against its delegating document: T3 posture (delegated, "no stated posture is not acceptable"), 5-min freshness (DEC-07-03: "Stage 08 sets the value"), decorator-vs-middleware (07 handoff item 4), triggers-only (threat model §4: "acceptable with §5's residual recorded" — residual already accepted as DEC-07-04), correction mechanics (06 handoff: "free choice within recoverability + attribution"), impact-preview placement (control §7 design freedom), `legacy_executor_stats` either/or (07 handoff item 3), edit-lock trigger-or-app-layer (closure plan's own either/or). **No material product/risk/compliance decision was taken without authority.** |
| DEC-08-09's UNIQUE widening to `(country_code, effective_from, version)` | implementation-specification with named build-time governance — **informational note for the human reviewer** (not a gate item) | This changes a pinned invariant in the repo's CLAUDE.md data-contract table ("no duplicate effective dates"). The executor's handling is correct: the change is required by the delegated correction-mechanics choice, its intent-preservation is argued (resolution stays total-ordered), and it is explicitly flagged for Phase 3 arch-council rather than silently decided. The human reviewer should simply be aware Stage 08's design commits Phase 3 to proposing this contract change. |
| Missing/zero-when-expected → C6 boundary | not-a-decision (executor conclusion answering a question Stage 04 explicitly forwarded to Stage 08) | Correctly resolved in `anomaly-detection-design.md` §1 with reasoning; would have been slightly tidier as a DEC entry, but it is clearly documented and within authority. |
| EG-001–003 | evidence-gap, non-blocking | Unchanged, correctly held. |

No artificial approval gates were created; "Human decisions raised by this stage: None" is accurate.

## Evidence-quality assessment

**Strong.** All three findings meet the evidence standard: committed evidence, pinned commit, direct-read excerpts in a dedicated evidence file, draft/confirmed separation maintained (zero drafts). F-08-03's citation-currency sweep is itself independently confirmed — I found no drift between the cited line numbers and the working tree at any load-bearing site. The one imprecision found (correction 1) is in a consumed Stage 05 citation inside a design document, not in a finding, and does not affect any conclusion. Conclusions follow from evidence without overclaiming: F-08-01 carefully states the tie-break is "unreachable for a single country today" (correct — the UNIQUE constraint forbids same-date pairs per country), and F-08-02 correctly generalises F-06-02 rather than re-litigating it.

## Consistency assessment

**Consistent throughout.** Verified specifically:

- **All 9 CONTEXT questions answered**: Q1–Q7 by the seven named designs; Q8's full item list (reconciliation five-item fix, five decorative routes, `load_inputs_for_run`, `workspace_info()`, append-only choice, salary-def edit-lock, D-ARCH-1 drift, plus the trace null-guard) each has a design with closure evidence in `remediation-designs.md` §§1–8; Q9 answered by DEC-08-15 and verified by absence.
- **Tool coverage**: all 11 matrix tools have contracts; `get_reconciliation` unregistered per P8/D-02-02 (both-layers precondition preserved — remediation §1 + wrapper-independence test); registered set = 10; capability-scoped registries match SS-4; C11's registry is `get_statutory_rules` only; C7-narration has no tools.
- **Cross-output parameter coherence**: 5-minute freshness identical in auth §1.5 and C12 §8; `consumed_by` CAS identical in both; the audit entity-type enum in event-audit §3 covers every type used by other designs (`STATUTORY_CHANGE`, `PENDING_ACTION`, `DRY_RUN`, `TOOL_CALL`, `EXCEPTION`, `AUTH`); the append-only trigger list covers every table other designs declare protected (and correctly excludes mutable `outbox`, `workspace_notification`, `exception_record` — the latter with explicit reasoning); C12's impact preview reuses C14's pure-path mechanism as claimed.
- **Binding decisions preserved, none weakened**: D-02-02 (both layers, tool absent until both proven), D-02-03 (no C4/C8 design produced — correct per stage context), D-02-04 (no LLM anywhere in C12; C11 enters as data), D-03-01 (portfolio/tool list consumed, not re-derived), D-04-01 (layers additive, peer-pattern absent, exception-workflow hard gate, shadow-first, versioned thresholds), DEC-07-02 (membership relation, single-active-workspace token), DEC-07-03 (step-up with freshness + one-per-event), P1–P8 (each individually addressed in tool-contracts §1), append-only floor + no-purge, cut-over epoch as data, SC-3 field set (verified field-by-field against `tool_call_log`).
- **Handoffs**: Stage 09 handoff surfaces every UI-relevant mechanism (auth/switcher/step-up, epoch labelling, notification + exception queue, C10 render-from-frozen-payload, C12 evidence set, C13/C14 hash-gated flow, C7-as-exception-records, DQ-005) and stays at surfaces-not-screens. Stage 10 handoff consolidates exactly the verification hooks the designs name, references Stage 07's test standards without restating, and correctly carries the residual-risk items (DEC-07-04, triggers-only, DQ-008 posture).
- **Queue and state files**: `decision-queue.md` resolution entries match the design sections and DEC IDs; `review-state.md` and stage CONTEXT status agree (`awaiting-critic`); `state.md` defers to `review-state.md` as designed.

## Advancement recommendation

**PASS — close Stage 08 and open Stage 09 per D-003 automatic closure.** No blocking human decision remains: DQ-006/007/008 stay correctly queued as pre-build gates surfacing at Stages 11/13, not stage-advancement blockers. Recommend the controller: (a) apply the `payroll.py:1163` line-pointer correction in `tool-contracts.md` §3.4 pre-closure, (b) add the Stage 07/08 codebase re-read note and refresh the stale next-action line in `_inputs/source-register.md`, and (c) carry the DEC-08-09 informational note (UNIQUE-constraint contract change committed for Phase 3 arch-council) into the next human-reviewer touchpoint so it is seen before build authorisation. None of these gates closure.

---

## Controller disposition (2026-07-17)

**Verdict accepted: PASS with zero blocking corrections and no blocking human decision → Stage 08 closed automatically per D-003; Stage 09 opened.** Actions taken on the critic's three recommendations, all pre-closure:

1. **(a) applied** — `tool-contracts.md` §3.4 line pointer corrected to `payroll.py:1163` (`r[7] or []`), verified by direct read before editing.
2. **(b) applied** — `_inputs/source-register.md` gained the Stage 07/08 codebase re-read notes and a refreshed next-action line.
3. **(c) recorded** — DEC-08-09's data-contract change (UNIQUE `(country_code, effective_from)` → `(country_code, effective_from, version)`) added as a visibility item in `decision-queue.md` for the next human-reviewer touchpoint (pre-Phase-3 build authorisation), alongside the existing DEC-07-04 visibility item.

Report saved verbatim above; no critic finding was edited. Stage 08 status → `closed` in `review-state.md`; Stage 09 `CONTEXT.md` populated per the controller loop.
