# Stage 10: Evaluation & Assurance — Context

## Status

closed (2026-07-18 — critic PASS, zero required corrections, `outputs/critic-review.md`; D-003 automatic closure. Executor pass complete 2026-07-18; was context-ready 2026-07-17.)

## Objective

Design the evaluation and assurance framework for the approved 15-capability portfolio: how every launch gate's closure evidence is defined and kept true over time, how the LLM capabilities are evaluated (adversarial/injection corpora, refusal quality, pass criteria, refresh cadence), how C7's calibration is governed, how Stage 09's UX-testable behaviours are verified, how evidence-chain integrity is checked, and how accepted residual risks are registered and reviewed. Stages 07–09 fixed *what* must be proven (gates, verification hooks, testable behaviours); this stage designs *how it is proven at build time and kept proven afterwards* — methodology, cadence, ownership, and evidence form. It does not re-open any gate, mechanism, or surface design.

## Binding decisions inherited (pre-scope — do not re-litigate)

- **D-02-01–04, D-03-01** (portfolio, dispositions, launch conditions), **D-04-01** (layered C7 calibration, gated on the exception workflow; the three governance metrics are fixed — this stage designs their cadence/reporting, not their definition).
- **Stage 06/07 gate registers**: CG-1–15, SG-1–15, SS-1–4 are fixed requirements. Nothing this stage designs may weaken, waive, or re-scope a gate — it defines closure-evidence methodology per gate.
- **Stage 08 mechanisms** (all critic-passed): the per-mechanism verification hooks and committed-test closure-evidence lists in `08-technical-architecture/outputs/stage-10-handoff.md` are the concrete seams to design against — not re-derived.
- **Stage 09 surfaces** (critic-passed): the 25 UX-testable behaviours in `09-human-experience/outputs/stage-10-handoff.md` are the behaviour inventory to verify — their design is closed; mismatches discovered while designing verification go back as findings.
- **Standing repo discipline**: all closure tests run against CI's `alembic upgrade head` database (fresh-DB rule — local dev DB is drifted; CI is the arbiter); every bug fix ships with a regression test named for its invariant.
- **Measurement framework prohibitions** (Stage 04): chat/usage volume is never a success metric; dry-run-pass and client-validated accuracy are never collapsed; "number of changes detected" is never C11 success.

## Confirmed platform facts to consume (do not re-verify)

- The three stage-10 handoffs: `07-security-identity/outputs/stage-10-handoff.md` (standing verification artifacts as assurance controls; security-adjacent eval requirements; carried facts incl. the empirically recurrent decorative-scoping habit), `08-technical-architecture/outputs/stage-10-handoff.md` (per-mechanism hooks; assurance-framework inputs 1–5), `09-human-experience/outputs/stage-10-handoff.md` (25 UX behaviours + carried context).
- `04-outcome-discovery/outputs/measurement-framework.md` (per-capability success/safety/harmful-incentive metrics; baseline-data gaps) and the EG-001–003 evidence gaps in `decision-queue.md`.
- The accepted residuals: DEC-07-04 (audit-tamper residual — **explicitly flagged for review at this stage**, `decision-queue.md` visibility item), trigger-only append-only floor, dry-run retention posture pending DQ-008.

## Required inputs

Read: `README.md`, `WORKFLOW.md`, `review-state.md`, `decision-queue.md`; all files under `_core/`; the three stage-10 handoffs above; `04-outcome-discovery/outputs/measurement-framework.md` + `anomaly-detection-outcome-policy.md`; the Stage 06/07 gate registers (`06-compliance-controls/outputs/control-gate-register.md`, `07-security-identity/outputs/security-gate-register.md`) and Stage 08 mechanism designs as needed per evidence item; the repo's existing test-harness conventions (`docs/test-reports/test-harness/test-harness-checklist.md`, `.github/workflows/tests.yml`) for grounding assurance design in the platform's real CI reality. Record any new source in `_inputs/source-register.md`.

## Questions this stage must answer

1. **Launch-gate evidence register**: for every CG/SG/SS row and Stage 08 mechanism hook, what is the concrete closure-evidence artifact (committed test, design-absence check, deployed-config inspection, eval report) — consolidated into one auditable register mapped to build items, so Phase 3 "done" is checkable, not asserted.
2. **LLM capability evaluation methodology** (C3, C5, C7-narration, C11, C13): corpus construction (incl. the fixed injection families — T1/T2 general, T5 hostile-source for C11, header-borne for C13), refusal-*correctness* evaluation (not just rate; the audit trail's `REFUSED` records as data source), pass criteria and their evolution, refresh cadence, and who/what runs them (single-operator reality — evals must be runnable as CI jobs or scripted sessions, not standing human panels).
3. **Standing assurance controls vs point-in-time evidence**: which verification artifacts become permanent CI gates (route-table-generated tests, registry uniformity, serialization property tests), which are periodic reviews (session-scope conformance/SS-4 drift, PII-ruleset currency), and the cadence/trigger for each.
4. **C7 calibration governance**: shadow-mode duration and exit criteria, the three D-04-01 metrics' review cadence and decision rules (when does a threshold change), threshold-change audit flow, detector-version replay discipline.
5. **UX-behaviour verification plan**: disposition of Stage 09's 25 behaviours — automated (component/e2e) vs scripted manual, which are launch gates vs post-launch monitors, and how they slot into the repo's existing test-harness conventions.
6. **Evidence-chain integrity**: chain-completeness checks over `session_ref` / `pending_action_id` / `approval_id` / `step_up_event_id` linkages (Stage 08 assurance input 1); epoch-boundary discipline for any assurance reporting over historical audit data.
7. **Baseline instrumentation plan**: concrete measurement design for the named baseline gaps (EG-001–003 + measurement-framework's five gaps) that must precede capability launches — what is emitted, from where (Stage 09's flow stage boundaries), and the minimal reporting.
8. **Residual-risk register**: consolidate the accepted residuals into one register with owners and review triggers; perform the DEC-07-04 review this stage owes (dispose: reaffirm acceptance, or escalate as a human decision with options).
9. **Handoffs**: Stage 11 (assurance cost/dependency implications for sequencing) and Stage 12 (assurance posture summary as target-direction input).

## Required outputs

Create under `outputs/`: `launch-gate-evidence-register.md` (Q1), `llm-evaluation-framework.md` (Q2), `standing-assurance-controls.md` (Q3), `calibration-governance.md` (Q4), `ux-verification-plan.md` (Q5), `evidence-chain-and-baselines.md` (Q6+Q7), `residual-risk-register.md` (Q8), `stage-11-handoff.md`, `stage-12-handoff.md`. Update: `findings.md` (F-10-*), `decisions.md`, `review-state.md`, `decision-queue.md`, `_inputs/source-register.md` as required. (`outputs/critic-review.md` is the critic's.)

## Finding discipline

Per `_core/FINDING-SCHEMA.md` with the extended field pattern. Claims about the existing test/CI infrastructure must be verified against the repo (workflow files, conftest, test tree), not prior descriptions; committed evidence pinned to a named commit.

## Explicitly out of scope

- Building any test, eval, or instrumentation (Phase 3); changing any gate, mechanism, or surface design (mismatches → findings)
- commercial sequencing (Stage 11); target direction (Stage 12); roadmap (Stage 13)
- re-litigating closed decisions; re-opening D-04-01's metric definitions or the measurement framework's prohibitions; starting Stage 11

## Constraints

- Read-only with respect to production code; writes stay inside `docs/programmes/agentic-architecture-review/`.
- Every evidence/eval design must name the gate or hook it closes (CG/SG/SS row, Stage 08 hook, Stage 09 behaviour number) — no free-floating assurance activity.
- Do not create artificial human decisions; classify genuine choices per `CRITIC.md`. The DEC-07-04 review (Q8) is the one place a genuine risk-acceptance choice may surface — if reaffirmation is not clearly supportable, classify it `blocking-human-decision` with options rather than deciding.

## Completion criteria

Ready for the critic only when: every Q1–Q9 has a design answer or explicitly-classified open item; every output names its gate/hook/behaviour references; Stage 11/12 handoffs are complete and consistent; decisions recorded and classified; non-blocking questions queued.

## Completion procedure (D-003 lifecycle)

1. Mark Stage 10 `awaiting-critic` in `review-state.md` and this file.
2. Independent critic per `CRITIC.md` → `outputs/critic-review.md`.
3. On `PASS` with no blocking human decision, close and open Stage 11 automatically per `RUNBOOK.md`.

## Next action

**None — stage closed 2026-07-18 on critic PASS. Stage 11 is context-ready.**
