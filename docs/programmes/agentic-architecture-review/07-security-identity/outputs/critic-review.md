# Stage 07 Independent Critic Review — Security & Identity

*Saved verbatim by the controller from the independent critic's report, 2026-07-17. The critic ran read-only in a separate agent session against commit `ea1590a` (code evidence) / `6b56b87` (stage docs). Controller disposition follows at the end of this file.*

## Verdict

**PASS** — no blocking human decision remains; one non-blocking evidence-precision correction is recommended (route-sweep denominator), but it changes no finding, severity, or downstream decision.

## Scope reviewed

CRITIC.md contract (10 checks); CONTEXT.md (objective, D-02-02/D-03-01/Condition 14, R1–R6, completion criteria, constraints); findings.md (F-07-01..03); decisions.md (DEC-07-01..05); evidence/07-route-scoping-and-identity-excerpts.md; all 9 outputs; upstream sources (06 stage-07-handoff + attribution-identity-requirements R1–R6 + control-gate-register; 05 handoffs; 03 capability/tool matrices; decision-queue; review-state). Independent code verification performed at commit ea1590a (and docs-only stage commit 6b56b87 against HEAD).

## Independent citation verification (re-ran, not trusted)

Confirmed against source code at ea1590a:
- **Five decorative routes** — get_reconciliation_scoped (payroll.py:1327), submit_reconciliation_scoped (:1336), resolve_reconciliation_scoped (:1352), get_run_timeline (:1372), legacy_executor_stats (:1378): all accept `workspace_id` and discard it; verified handler bodies directly. get_trace_steps filters on `run_id` only (execution_trace_repo.py); get_legacy_executor_stats takes no parameters and its `by_run` breakdown spans all runs/workspaces. CONFIRMED.
- **workspace_info()** — LIMIT 1 pick (workspace.py:133); `getInfo` (frontend/src/api/workspace.ts:12) declared with **no other consumer** (repo-wide grep returns only the declaration); payroll.html:30 fetches /api/v1/workspace/info; served by admin.py admin_payroll. CONFIRMED.
- **load_inputs_for_run** — signature `load_inputs_for_run(payroll_run_id)` filters run_id only; sole caller payroll_retry_service.py:606; entry point retry_failed_payroll_employees (:510) derives workspace_id from the run row (SELECT workspace_id ... FOR UPDATE, ~539). CONFIRMED.
- **Audit-actor lines** — X-Performed-By defaults at payroll.py:1180/1207/1227; body actor_id default "system@internal" at 1255-1259; free-text resolved_by at 1356-1365; hardcoded performed_by="system" at 992 and "admin@internal" at 1009. CONFIRMED.
- **CORS** — main.py ALLOWED_ORIGINS defaults to "*", allow_credentials=False, methods/headers "*". CONFIRMED.
- **Absence claims** — no OAuth2/HTTPBearer/APIKey/jwt machinery in backend/ (only get_current_contract, a domain fn); no operator table in models or migrations (all "operator" hits are op.drop_table alembic calls). CONFIRMED.
- **Stage commit** — 6b56b87 is docs-only (16 files, all under docs/); no production or unrelated working-tree changes. CONFIRMED.

## Strengths

1. Genuine new discovery under scope: the sweep found two additional decorative routes (get_run_timeline, legacy_executor_stats) unknown to Stages 01–06, correctly framed as pattern confirmation (F-06-05 is a scaffolding habit, not a reconciliation one-off) and — crucially — turned into a *mechanized* route-table verification standard so the pattern fails CI by default rather than being re-enumerated by hand. Right structural fix, not just a bug list.
2. R1–R6 each carry an explicit, end-to-end satisfaction path (identity-architecture-requirements §4–6), and every security requirement names its verification method — the CONTEXT constraint "a requirement without closure evidence is not complete" is honoured throughout.
3. The tool-guard wrapper resolves Condition 14 concretely (declarative scoping, fail-closed registration, P1–P8, wrapper-independence test proving defence-in-depth is real not inherited) for all 11 tools; blocked tools are absent from the registry rather than flag-disabled — the stronger form.
4. Severity discipline: F-07-01 Medium (trace/ops metadata) below F-05-03 Critical (client financials) with reasoning; F-07-02 rated on present impact with the wrap-risk explicitly not double-counted against F-05-11 — consistent with SEVERITY-MODEL.md and Stage 06's non-re-rating practice.

## Required corrections

None blocking.

**Recommended (non-blocking) — reconcile the route-sweep denominator.** Evidence §1 and tenant-isolation-verification-standard.md §2 both state the sweep covered "72 `{workspace_id}` routes." My independent count across all route files is **70** (payroll.py 19, employees.py 4, payroll_input.py 8, workspace.py 39; no other route file contains a `{workspace_id}` decorator). The discrepancy is 2 and does not affect the finding: the five decorative routes are individually verified and correct, and the sweep method is sound. Correct the stated denominator to 70 (or show the two additional routes I could not locate) in evidence/07-route-scoping-and-identity-excerpts.md §1 and tenant-isolation-verification-standard.md §2. Classified `evidence-gap`, minor.

## Decision classification (open questions found)

- **Route count 72 vs 70** — `evidence-gap` (non-blocking; conclusion unaffected).
- **MFA as a hard C12 launch gate** — `non-blocking-forwarded-decision`. Correctly folded into DQ-007 as a context amendment rather than absorbed; the executor set the password-only floor and left the hard-gate risk-appetite call to the human. Proper.
- **Audit-store residual risk (DEC-07-04: DB-superuser tampering; no crypto signing; no external anchoring)** — `non-blocking-forwarded-decision`. I checked the authority question specifically: Stage 06 R4 explicitly states "full cryptographic signing is not required at requirements level ... Stage 07 decides whether stronger mechanisms are warranted." The executor acted inside delegated authority, kept cheap forward hooks (DB-clock timestamps, hash-chain-compatible record shape), and flagged the residual for human visibility at Stage 10/13. Not a usurped human choice.
- **R5 → step-up re-auth (DEC-07-03)** — `not-a-decision` for the critic to reopen: precisely the choice Stage 06's handoff delegated ("step-up auth vs live-session check is Stage 07's design choice"). The reasoning that a live-session check cannot meet R5's own stated control requirement ("a hijacked idle session must not be sufficient") is sound and does not overreach.
- **DEC-07-02 membership model** — `not-a-decision` (executor conclusion). Track P is "design under review, not authority"; the bureau multi-workspace shape is an established Stage 06 business-context fact; the correction contradicts no prior human decision and retains P6's single-active-workspace-per-token property, so R2 enforcement shape is unchanged. No human choice usurped.

No artificial approval gates were created for formatting, naming, or mechanical updates.

## Evidence-quality assessment

High. All code claims pinned to a named commit, committed-state-only, working-tree observations explicitly excluded. Line numbers re-resolved at ea1590a with drift from Stage 06's 265db10 pins explained (one intervening feature commit b398c72; two docs-only commits). Every one of the ~15 load-bearing citations I spot-checked resolved exactly, with the single 70-vs-72 denominator exception noted above. Findings carry the full extended Stage 05/06 field pattern (closure evidence, confidence, downstream owner, classification). Draft/confirmed/parked sections kept separate and empty where claimed.

## Consistency assessment

- **Binding decisions preserved, not weakened.** D-02-02 two-layer requirement restated and both layers made verification-gated (SS-1/SS-2, SG-8). Condition 14 resolved concretely for all 11 tools. D-02-04's mandatory human approval gate carried into the agent-layer model (T5) and approval design. C4/C8/C9 remain blocked/rejected in the security-gate register (SG-4 "define when unblocked", SG-8 blocked, SG-9 "no gates").
- **CG register not subtracted from.** SG register explicitly additive ("stricter reading governs"; "SG gates add to CG gates"); no CG-1–15 gate restated in weakened form.
- **Handoffs mutually consistent.** Stage 08 handoff items 1–10 map cleanly to the outputs' security constraints and do not reopen DQ-001–005; Stage 10 handoff hands verification *standards* (not eval design), respecting the stage boundary. Both consistent with findings F-07-01..03 and the DEC log.
- **Completion criteria (CONTEXT §"Completion criteria")** — all met: R1–R6 satisfaction paths explicit; two-layer + route-exhaustive verification standard defined including both F-05-11 functions and the answered workspace_info() caller question; tool pattern resolves Condition 14 for 11 tools; audit threat model covers F-06-02/03 and disposes of the cut-over epoch (confirmed + 2 hardenings); R5 resolved with reasoning; agent-layer model covers all 5 LLM capabilities + C10; every one of the 15 capabilities has an SG entry; decisions classified and the non-blocking question is in decision-queue.

## Advancement recommendation

**Advance.** Stage 07 meets its completion criteria, its evidence is sound and independently reproduced, all binding decisions are preserved, and no blocking human decision was raised. Per D-003 the controller may close Stage 07 and open Stage 08. I recommend the executor correct the "72 → 70" route-sweep denominator as a mechanical fix — it need not gate closure. Two forwarded items the human reviewer should see at their next decision point (not blockers now): the DQ-007 MFA-hard-gate amendment, and the DEC-07-04 audit-tamper residual-risk acceptance, both correctly flagged by the executor.

---

## Controller disposition (2026-07-17)

**PASS + no blocking human decision → Stage 07 closed automatically per D-003.** The recommended denominator correction was verified by the controller's own recount (4+8+19+39 = 70) and applied same-day to `evidence/07-route-scoping-and-identity-excerpts.md` §1, `outputs/tenant-isolation-verification-standard.md` §2, and `findings.md` F-07-01 before closure — no other content changed. The two visibility items (DQ-007 MFA amendment; DEC-07-04 residual-risk acceptance) are recorded in `decision-queue.md` and this stage's `decisions.md` for the human reviewer's next decision point. Stage 08 opened `context-ready`.
