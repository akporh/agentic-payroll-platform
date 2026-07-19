# Stage 13 Output: Baseline & Near-Term Plan (Q4)

The calendar-bound, low-cost actions that must be placed **explicitly so none is lost** — captured now, or pinned to a sprint-planning trigger, or flagged to a standing workflow. These correspond to Tranche 0 in `proposed-roadmap.md` §1 and to the Q7 near-term list (`sequencing-economics.md` §5; Stage 11→13 handoff §3; Stage 12 handoff §4). **None requires Phase 2/3 authorisation to schedule; none authorises a build.** No dates or capacity are invented — where timing depends on a fact only Michael has, it is an explicit ask (EG-004).

---

## 1. Capture now — the retrospective baselines (B3, B5)

**The cheapest lines on the whole roadmap, and the first two "measured, not asserted" artifacts** the positioning story can cite (Stage 12 handoff §4 — the direction adds urgency here: these are the first artifacts of the compliance and onboarding narratives, demonstrable *before any new capability ships*).

| Baseline | What it measures | How captured now (W5, near-zero cost) | Anchors |
|---|---|---|---|
| **B3** — time-to-go-live | Historical onboarding elapsed time under the current flow | Retrospectively from engagement records + `payroll_run` history | K2 onboarding story; C14 launch (ET-6) |
| **B5** — statutory time-to-apply | Elapsed time from a statutory change's publication to its application | NTA 2025 publication/commencement date vs the PAY-TAX-1 migration deploy evidence | K1 compliance story; C12 (apply half) + C11 (comparison) (ET-6) |

**Action:** capture both as dated ET-6 baseline artifacts now. They de-risk two launch-gate ET-6 rows immediately and produce the first two demonstrable baseline artifacts (W5; `evidence-chain-and-baselines.md` B§3). *These are measurement/evidence-capture actions inside the programme's authority — not production-code changes.*

---

> **DP-7 amendment (2026-07-19, HD-14) — read this section in that light.** The human reviewer resolved EG-004 with an **amended evidence approach**: the next live onboarding is **no longer the only acceptable B1/B2 source**, and the "unrecoverable window" is no longer a hard dependency. B1/B2 may be captured via a **controlled onboarding benchmark** built from representative historical client information or appropriately synthetic data based on previous onboarding cases — measuring the existing/manual process and the platform-supported process consistently (time, effort, interventions, errors, completeness, and other relevant measures) — with live-onboarding evidence collected **opportunistically** when available. Replay/test data must be isolated, governed, and safely removed or retained per the agreed evidence protocol, and simulated onboarding must be **labelled clearly as controlled benchmark evidence, never as proof of live operational performance**. The "unrecoverable window (W2)" language below is retained as originally written pending DP-9 (roadmap not yet finally approved — not rewritten here); read it as superseded by this amendment for evidence-capture purposes. Master record: `_core/HUMAN-DECISIONS.md` HD-14; queue rows EG-001/EG-002/EG-004.

## 2. Ask now — EG-004 (the scheduling fact the unrecoverable window hinges on)

**EG-004 — next-onboarding timing:** whether/when Sandy expects the next new payroll client. Only Michael can supply it (evidence type 5; never invented). This is the single fact the **unrecoverable B1/B2 window (W2)** depends on.

**Action:** ask Michael at the approval touchpoint (surfaced as DP-7 in `final-decision-pack.md`). If an onboarding is plausible within the C13/C14 horizon, the **B1/B2 observation protocol must be armed *ahead of it***, regardless of C13's build order:

| Baseline | What it measures | Capture constraint |
|---|---|---|
| **B1** — mapping time / error rate | Onboarding mapping effort under the *current* (pre-C13) flow | Requires a real onboarding under the current flow; **unrecoverable** if the next onboarding lands after C13 ships (W2) |
| **B2** — parallel-run agreement rate | Agreement between the new setup and the prior process on a real onboarding | Same real-onboarding dependency as B1 |

**Protocol readiness:** the one-page timing sheet + comparison sheet (per `evidence-chain-and-baselines.md` B§2) should be ready *before* the onboarding happens. If B1/B2 are missed, C13's improvement claims are permanently anchorless — K2 then reports absolute values only, labelled (`direction-kpis.md` §3).

---

## 3. Pin to sprint-planning triggers — the observation-window baselines (B6, B4)

Both are cheap, calendar-bound, and **easily forgotten** because they must *start* at sprint-planning time, not at ship time.

| Baseline | Trigger to start | Window before ship | Anchors |
|---|---|---|---|
| **B6** — support-question tally | **C3 sprint-planning** | 4-week operator tally before C3's launch (W3) | C3 support-question-reduction claim; framework metric |
| **B4** — time-to-detection observation | **C6 sprint-planning** | 3-cycle observation before C6 ships (W4) | C6 time-to-detection claim (ET-6) |

**Action:** record B6 and B4 as sprint-planning entry conditions for C3 (Tranche 3 Item 3.2) and C6 (Tranche 3 Item 3.1) respectively — the tally/observation begins when the capability *enters* planning, so the window closes before launch.

---

## 4. Initiate now — the professional-advice engagement (DQ-006 + DQ-008)

Bundled into a single Nigerian tax/legal engagement (same domain, same adviser; DEC-11-05). **Initiate at/immediately after approval** — external-adviser lead time is the risk, not cost.

- **DQ-006** must conclude **before any C11 sprint** (Tranche 5); starting now gives it the longest runway.
- **DQ-008**'s answer should arrive **before anyone is tempted to build retention tooling** (O9); "keep at least 7 years, no purge" is the working floor meanwhile (Posture P-C).

Full logistics and the decision framing are in `final-decision-pack.md` DP-4. *Initiation is a non-build lead-time action; the decisions themselves are the human reviewer's + professional adviser's.*

---

## 5. Flag to standing maintenance — FULL_RUN dead-option removal

**FULL_RUN dead-option removal** (Stage 09 handoff §2; `sequencing-economics.md` §5.6): a trivial frontend fix — the disabled `FULL_RUN` retry option should be removed from the UI (`payroll_retry_request.retry_strategy` is `PER_EMPLOYEE`-only by migration; the UI still offers the dead option).

**This is outside this programme's write authority** (it touches `frontend/src/`). **Action:** carry it as a handoff item to the repo's **standing maintenance workflow** — a normal maintenance slot, no Phase 3 machinery required. Recorded here so it is not lost; **not executed by this stage.**

---

## 6. Optional — browser-e2e automation line (safe to defer)

**Optional cost line** (`sequencing-economics.md` §5.5; Stage 10 handoff §4): browser-e2e automation for the two scripted-manual UX behaviours that the Vitest+RTL harness cannot cover. Cheap to include **with the Tranche 1 frontend-harness work**; safe to defer.

**Action:** flag as an optional add-on to Item 1.1's harness scope — a placement decision for sprint planning, not a required roadmap line. Placed here explicitly so the option is not silently dropped.

---

## 7. Near-term plan summary (nothing lost)

| # | Item | Timing | Authority | Where owned |
|---|---|---|---|---|
| 1 | Capture B3, B5 retrospectives | **Now** (W5) | Programme (evidence capture) | This plan §1 |
| 2 | Ask EG-004; ready B1/B2 protocol | **At approval touchpoint** | Human (Michael) | §2; `final-decision-pack.md` DP-7 |
| 3 | Pin B6 to C3 planning; B4 to C6 planning | **At those sprints' planning** | Future sprint | §3 |
| 4 | Initiate DQ-006/DQ-008 engagement | **At/after approval** | Human + professional | §4; `final-decision-pack.md` DP-4 |
| 5 | FULL_RUN removal | **Standing maintenance slot** | Repo maintenance (outside this programme) | §5 |
| 6 | Optional browser-e2e line | **With Tranche 1 harness, or defer** | Future sprint (optional) | §6 |

Every Q7 near-term item is placed. Items 1–4 have explicit triggers; items 5–6 are flagged to their owning workflow so neither is silently dropped.
