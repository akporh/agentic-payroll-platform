# Stage 11 Output: Sequencing Economics (Q2 + Q7)

One consolidated, costed picture of every binding sequencing constraint the prior stages have produced, plus the calendar-bound near-term items. **This is the constraint set Stage 13 sequences within — not a roadmap.** Nothing here weakens a gate; a gate may only be weakened by a recorded human decision (register ratchet rule, DEC-10-02).

## 1. Hard ordering constraints (binding, with sources)

| # | Constraint | Source (binding) |
|---|---|---|
| O1 | C1 before everything — zero auth exists; no capability, surface, or claim launches without it | Stage 05 readiness matrix; Stage 09 (every designed surface assumes C1) |
| O2 | C2 before C3/C6-surfacing/C7/C11-alerting and before the exception workflow | Stage 05; capability-readiness matrix |
| O3 | C1/C2 are deterministic platform engineering, sequenced/staffed separately from AI-capability work | D-03-01 condition 12 |
| O4 | C7 after the exception-resolution workflow (hard gate, not preference) — register enforces C7's row may not close before C2's | D-04-01; launch-gate register §5 |
| O5 | C11 with-or-after C12 — register row-closure precondition | D-03-01 conditions 9–11; register §5 |
| O6 | C13 never ahead of C14 — register row-closure precondition | D-03-01; register §5 |
| O7 | C4/C8 remain blocked until their named preconditions close (D-02-02/D-02-03) — no commercial timeline may assume they unblock | D-02-01–04 |
| O8 | DQ-006 resolved before C11 build authorisation; DQ-007 resolved before C12 build authorisation (register rows cannot close without the recorded decisions) | Stage 06; register CG-11/CG-12 rows |
| O9 | No retention-enforcing mechanism before DQ-008 resolves (7-year keep-at-least floor meanwhile) | Stage 06 (agent-tool-audit-standard §2); SC-4 |

## 2. Calendar-bound windows (the items a Gantt chart can get irreversibly wrong)

| # | Window | Consequence of missing it | Source |
|---|---|---|---|
| W1 | **C7 GA lags its deploy by ≥ 3 full payroll cycles AND ≥ 20 terminal exception records** (shadow exit, both conditions) | Any claim of C7 value in month one is wrong by construction; plan shadow entry ≥ one quarter before claimed GA | DEC-10-08, `calibration-governance.md` §2 |
| W2 | **B1/B2 baselines need a real client onboarding under the *current* flow, before C13 ships** | **Unrecoverable** — if the next onboarding lands after C13, C13's improvement claims are permanently anchorless | Stage 10 handoff §2.2; EG-001/EG-002 |
| W3 | **B6 needs a 4-week operator tally before C3's launch window** | C3's support-question-reduction claim has no anchor; start the tally when C3 enters sprint planning, not when it ships | Stage 10 handoff §2.3; B6 design |
| W4 | **B4 needs a 3-cycle observation window before C6 ships** | C6's time-to-detection claim has no anchor | `evidence-chain-and-baselines.md` B §2 |
| W5 | **B3/B5 retrospectives are capturable now** (engagement records + `payroll_run` history; NTA 2025 publication → PAY-TAX-1 deploy) at near-zero cost | Not a risk — an opportunity: two launch-gate ET-6 rows de-riskable immediately | `evidence-chain-and-baselines.md` B §3 |
| W6 | **DQ-006/DQ-008 need professional (legal/tax) input with engagement lead time**; DQ-007 is an internal risk-appetite call decidable at Stage 13 | A C11 or C12 sprint that starts before its decision resolves stalls at the register row; see `pre-build-decision-logistics.md` | Stage 06; Stage 10 handoff §2.5 |

## 3. One-off structural costs (pay once, with the right build item)

| Cost | Lands with | Consequence of deferring | Source |
|---|---|---|---|
| Frontend test harness (Vitest + RTL + CI job) | **C1** (first frontend-touching build) | Converts a small fixed cost into a permanent per-release manual-testing tax (~18 of 25 Stage 09 behaviours fall to scripted-manual); leaves behaviour 21 unprotected | F-10-01; Stage 10 handoff §1 |
| LLM eval infrastructure (corpus format, runner, report convention) | **C3** (first LLM capability) | Later AI capabilities each re-pay setup; corpus authorship (~70 cases/capability) is the real recurring cost either way | Stage 10 handoff §1 |
| Scheduled-job CI seam (workflow triggers) | First Class B control | Trivial either way — just don't forget it | F-10-02 |
| Platform-level frontend area (route family, chrome, PLATFORM_ADMIN gating) | **C12** (first platform-level surface) | Hidden inside "statutory UI" if not scoped as its own story | Stage 09 handoff §3 |
| Exception-workflow substrate | With C2 | C7 cannot launch (O4); C6/C7 flag-without-resolution value multiplier lost | F-04-01; D-04-01 |

## 4. Recurring obligations (steady-state costs any timeline inherits)

- **Standing assurance cadence is capped**: one monthly + one quarterly scripted operator session (`standing-assurance-controls.md` §6). Any proposal that grows it must displace something — a real constraint on how many AI capabilities can be *operated* concurrently by a single-operator bureau, independent of build capacity.
- **Three-surface regression obligation on C13-adjacent changes**: `NativeUploadFlow`/`ColumnMappingPanel` have three consuming pages; C13 work re-tests all three (Stage 09 RC-1).
- **Corpus maintenance and eval re-runs** per `llm-evaluation-framework.md` triggers (Class B) for each live LLM capability.
- **DEC-08-09**: C12's statutory UNIQUE widening goes through the repo's standing `/arch-council` gate at Phase 3 — budget the review; do not re-decide it.

## 5. Near-term commercial actions (Q7 — concrete "do before X" items for Stage 13)

Ordered by urgency-to-value ratio; none requires Phase 2/3 authorisation to *schedule*:

1. **Capture B3 and B5 retrospectives now** (near-zero cost, W5): time-to-go-live table from engagement records + `payroll_run` history; NTA 2025 time-to-apply from the Act's commencement date vs the PAY-TAX-1 migration deploy evidence. De-risks two launch gates and produces the first two "measured baseline" artifacts the positioning story can cite.
2. **Establish the next-onboarding fact (EG-004)**: whether/when Sandy expects the next new payroll client is the single scheduling fact W2 hinges on. If an onboarding is plausible in the next two quarters, the B1/B2 observation protocol (one-page timing sheet, comparison sheet) must be ready *before* it happens — regardless of when C13/C14 are built.
3. **Initiate the DQ-006/DQ-008 professional-advice engagement early** (see `pre-build-decision-logistics.md`): both need the same Nigerian tax/legal domain; lead time is the risk, not cost.
4. **Package DQ-007 (+ MFA hard-gate question) into the Stage 13 decision pack** — internal risk-appetite call; C12 is early in every plausible sequence, so this is the earliest human gate a build plan will hit.
5. **Start B6's 4-week tally at C3 sprint-planning time** and **B4's 3-cycle observation at C6 sprint-planning time** — cheap, calendar-bound, easily forgotten.
6. **FULL_RUN dead-option removal** (Stage 09 handoff §2): trivial frontend fix, no Phase 3 machinery — flag for a normal maintenance slot via the repo's standing workflow (outside this programme's write authority; carried as a handoff item, not executed here).

## 6. The consolidated dependency picture

```
[now]  B3/B5 retrospectives ── capturable immediately (W5)
       EG-004 next-onboarding fact ── determines W2 scheduling
       DQ-006/007/008 logistics ── start lead-time clocks (W6)

C1 (auth + frontend harness) ──► C2 (events/outbox/exceptions + tool layer)
                                    │
        ┌───────────────┬───────────┼──────────────────┐
        ▼               ▼           ▼                  ▼
   C6 (B4 first)   C12 (DQ-007   C14 (B2/B3        C3 (B6 first;
        │           first; +      at launch)        eval infra)
        │           platform        │                  │
        │           chrome)         ▼                  ▼
        ▼               │        C13 (B1/B2 must   C5 (null-guard
   C7 shadow ≥3         ▼         pre-exist; 3-     first)
   cycles + ≥20     C11 (DQ-006   surface regression)
   records → GA      first; with/
   (needs exception  after C12)
   workflow live)
        
C4/C8: blocked until D-02-02/D-02-03 preconditions close (no timeline may assume them)
C10: designed when a write-capable consumer needs it; C15: after C2 proven in production
```
