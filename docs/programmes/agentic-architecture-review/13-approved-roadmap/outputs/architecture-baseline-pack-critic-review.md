# Independent Critic Review — Architecture Baseline Pack (Stage 13)

**Reviewer**: independent programme critic (separate pass from the baseline-pack executor)
**Date**: 2026-07-19
**Artifact under review**: `13-approved-roadmap/outputs/architecture-baseline-pack.md`
**Governing criteria**: prompt-record `docs/diagnostics/2026-07-19-prompt-record-stage-13-decisions-and-produce-architecture-baseline-pack.md` §4; `CRITIC.md`

---

## Verdict

**PASS** — with one non-blocking documentary tidy recommended (does not gate advancement).

The pack is a faithful synthesis of the Stage 08–13 outputs. It invents no architecture, does not close Stage 13, does not supersede the source document, implies no build authorisation, and reflects DP-1 = A1 + B2 and DP-2 / DP-9 pending correctly and consistently across every view and every decision-record file. All twelve views are present and substantive; all nine Mermaid blocks are well-formed; scope hygiene is clean.

---

## Scope reviewed

Read in full and cross-checked (not merely skimmed):

- The prompt-record (§1 decision wording, §2 required views, §4 validation criteria).
- `CRITIC.md` (verdict values, decision taxonomy, output structure).
- The pack itself (all 12 views A–L, §0 legend, validation report, contradictions list).
- Decision records: `_core/HUMAN-DECISIONS.md` HD-8…HD-16; `13-approved-roadmap/decisions.md` (HD table + DEC-13-01…06); `review-state.md`; `decision-queue.md`; the DP-7 note in `baseline-and-near-term-plan.md`.
- Upstream sources for independent verification: `12-target-direction/outputs/capability-end-state-map.md`; `13-approved-roadmap/outputs/proposed-roadmap.md` (tranches, constraint audit §4, held positions §3).
- `git status --short` and `git diff --stat` for scope hygiene.

## What I independently verified (not just read)

1. **DP-1 = A1 + B2, never A2 — everywhere.** Confirmed in HD-8 (verbatim "recorded as A1 + B2 — explicitly not A2"), the decisions.md table, decision-queue.md DQ-007 row, and review-state.md. In the pack itself: §0 (line 38), View F.3 diagram + caption, View H (SEG/STEP nodes + the explicit "*This is A1 + B2 — not A2*" line 449), View J (C12 row), View K (C12 + step-up rows). No A2 leakage; the A2 consequence (multi-operator prerequisite) is correctly stated as NOT applying.
2. **DP-2 and DP-9 PENDING — everywhere.** §0 "Two decisions are still open" block; View I rows 21 (source doc) and the roadmap row; View K rows for source-document disposition and roadmap approval; View L header and body; the closing footer. Matches HD-9 and HD-16, decisions.md, decision-queue.md, and review-state.md. No surface treats either as resolved.
3. **DP-7 amended controlled-benchmark approach.** HD-14 wording matches the prompt-record §1 verbatim (controlled benchmark from historical/synthetic data; consistent manual-vs-platform measurement; opportunistic live evidence; isolated/governed replay data; "labelled as controlled benchmark evidence, never proof of live operational performance"). The pack applies it in §0, View E, View J (C13 row), View K (C13 row), and honestly surfaces — rather than silently resolves — the residual lag in `proposed-roadmap.md`/`direction-kpis.md` (contradiction item #1). The `baseline-and-near-term-plan.md` DP-7 note is present and correctly labelled.
4. **Every target capability traces to Stage 12.** Cross-read all 15 capabilities in `capability-end-state-map.md` against Views D/G/I/J: 5 AI (C3, C5, C7, C11, C13), deterministic (C1, C2, C6, C10, C12, C14), C15 deferred, C4/C8 blocked, C9 rejected — reproduced one-for-one with dispositions intact (D-03-01). No capability invented, none dropped.
5. **View J matches the roadmap.** Tranche placements (C1/C2 T1; C12/C14 T2; C6/C3/C5 T3; C7 T4; C11 T5; C13 T6; C10 on-demand), prerequisites, gates (DQ-007/DQ-006/W1/B1-B2) and the O1–O9 / W1–W6 zero-departure audit all reconcile with `proposed-roadmap.md` §§1–4. Held positions match §3.
6. **View C is not misleading.** C.2 explicitly labels the source-doc Track P/V/W/X/Y model "STATED INTENT — mostly unimplemented," draws it with dashed nodes, and C.4 lists "that the tracks describe built behaviour (they do not)" as an invalidated assumption. Current-state (no auth, body `workspace_id`, hardcoded `performed_by`, write-only event store) matches Stage 01/05 confirmed findings and is labelled CONFIRMED CURRENT. No historical intent is presented as implemented behaviour.
7. **AI control boundary (Views F/G/H) correct.** The MAY (explain/analyse/identify/summarise/recommend) vs MUST NOT (calculate authoritatively / mutate / approve / bypass deterministic controls) split matches the prompt-record verbatim. No write tools on any LLM capability; every AI proposal passes a deterministic gate (C13→C14; C11→C12; C7 detector deterministic). View G states no autonomous agents — max autonomy is C11 drafting into C12's human-approved workflow — consistent with the review's rejection of autonomy.
8. **Traceability spot-checks resolve.** View K citations checked against real records: C7 → HD-7/D-04-01/DEC-08-12 (HD-7 confirmed in the log); C5 → Blocking Condition #4; C12 → DEC-08-09 + DP-1 A1+B2; RR-1 → DP-5/HD-12; source-doc → DP-2 PENDING; roadmap → DP-9 PENDING. View I dispositions map to the end-state map and confirmed findings.
9. **No premature closure/authorisation.** Header, footer, and every status surface state Stage 13 OPEN (`awaiting-human-decision`), Phase 1 not complete, source HTML + mirror not superseded (View L recommendation-only), no implementation authorised. Confirmed the working tree contains no edit to `docs/architecture/agent-layer-architecture.html` or its `frontend/public/` mirror.
10. **Mermaid validity.** 9 ```mermaid blocks, 18 fences total — balanced (9 open / 9 close). Each block has a valid header (`flowchart TB/LR`), quoted labels wherever they contain `/`, `(`, `·`, `—` or `<br/>`, quoted edge labels, and consistent `classDef`/`class` usage. Ampersand fan-out (`C2 --> C6 & C3 & …`) and nested subgraphs are valid constructs. No syntax faults found.
11. **Scope hygiene clean.** `git status --short`: 5 modified + 1 new file, **all** under `docs/programmes/agentic-architecture-review/`. No production, migration, frontend, or unrelated working-tree changes. `git diff --stat` confirms edits limited to decisions.md, baseline-and-near-term-plan.md, HUMAN-DECISIONS.md, decision-queue.md, review-state.md; the pack is the untracked new file.

---

## Strengths

- **Decision fidelity is exact.** The A1+B2-not-A2 discipline is enforced in five separate surfaces; the pending pair is unambiguous everywhere. This was the highest-risk area and it is clean.
- **Honest contradiction surfacing.** The pack does not paper over the roadmap/KPI "unrecoverable window" lag against the DP-7 amendment — it flags it (item #1) and correctly declines to rewrite the roadmap pre-DP-9. Evidence gaps DQ-006/DQ-008/EG-005 and the carried-forward Tech Decisions currency flag are surfaced, not resolved.
- **Current vs stated-intent separation is disciplined.** View C's dashed-node treatment and invalidated-assumptions list directly satisfy the "do not present unverified historical intent as implemented" criterion.
- **Navigable and reviewer-ready.** Consistent status legend, per-view source map, colour-coded diagrams, and a traceability matrix (View K) that lets a reviewer answer "why does this exist / which output supports it / approved-proposed-deferred-rejected" without opening every stage file — the stated objective.

---

## Required corrections

**None blocking.** One optional documentary tidy:

- **`13-approved-roadmap/decisions.md`, DEC-13-05 (and the DEC-13-02 line quoting "B1/B2 pre-C13 on a real onboarding (W2, unrecoverable)").** These executor synthesis conclusions record the roadmap as assembled on 2026-07-18, before the DP-7 amendment. The same file now records HD-14 (controlled benchmark) in its human-decisions table, so a reader sees the pre-amendment "unrecoverable real onboarding" framing and the post-amendment decision side by side without a cross-pointer. `baseline-and-near-term-plan.md` and `decision-queue.md` both received an explicit "amended by DP-7/HD-14" note; DEC-13-02's line did not.
  - **Fix (optional)**: append a one-line pointer to DEC-13-02 (e.g. "B1/B2 window framing amended by DP-7/HD-14 — see the controlled-benchmark note in `baseline-and-near-term-plan.md`; roadmap text not rewritten pre-DP-9"). This mirrors the treatment already given to the sibling files and removes an intra-file inconsistency.
  - **Why non-blocking**: the framing is defensible under the standing "do not rewrite the roadmap before DP-9" discipline, and the pack itself surfaces the broader version of this lag as contradiction #1. It is a tidiness item, not an evidence, safety, or authority defect.

---

## Decision classification

| Open item in the pack | Classification |
|---|---|
| DP-2 source-document disposition | `blocking-human-decision` (correctly PENDING; closes with DP-9) |
| DP-9 final roadmap approval | `blocking-human-decision` (correctly PENDING; closes Phase 1) |
| DQ-006 Tier-1 source legal sufficiency | `evidence-gap` (advisory approved to initiate, not concluded) |
| DQ-008 retention legal basis | `evidence-gap` (same engagement) |
| EG-005 commercial-demand evidence | `evidence-gap` (approach approved; no evidence registered) |
| Tech Decisions currency (DEC-12-05) | `evidence-gap` (flagged currency assumption, Phase 3 re-validation) |
| CI-schedule-seam host (C6 vs C3); C10 build trigger | `implementation-specification` (DEC-13-04 — correctly not gated) |
| DEC-13-02/05 DP-7 cross-pointer | `not-a-decision` (documentary tidy) |

No artificial approval gate detected. The executor made zero human decisions; HD-8…HD-16 are transcriptions of the reviewer's stated decisions.

## Evidence-quality assessment

High. Every load-bearing claim I spot-checked resolved to a real stage output, finding, decision ID, or roadmap row. Capability set, dispositions, tranche mappings, constraint audit, and residual-risk set all reconcile with their cited sources. No overclaiming: capability-vs-demand discipline (DP-8) is honoured throughout, and the pack repeatedly restates the accepted-residual boundary (RR-1…5) so no view assumes a stronger property than was accepted.

## Consistency assessment

Strong. Terminology (C1–C15, O1–O9/W1–W6, P-A…P-H, RR-1…5, B1–B6, ET-1…6, DP-1…9) is used uniformly with the source outputs. Status labels applied consistently per the §0 legend. The only intra-corpus inconsistency is the DEC-13-02 DP-7 framing lag noted above — defensible and non-blocking. No contradiction was silently resolved; the pack lists six open contradictions/gaps for the human reviewer.

## Advancement recommendation

**Advance to the human touchpoint.** The pack is fit for human review of DP-2 and DP-9. Stage 13 must remain OPEN; the source architecture document and its frontend mirror must remain live until DP-2 is decided; Phase 1 must not be marked complete until DP-9 is recorded. The optional DEC-13-02 tidy may be applied at the same time the roadmap is finally approved (when the roadmap text is eligible to be rewritten), or now as a one-line pointer — either is acceptable and neither blocks advancement.
