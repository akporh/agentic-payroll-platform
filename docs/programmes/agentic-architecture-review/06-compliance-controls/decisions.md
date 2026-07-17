# Stage 06: Compliance & Controls — Decisions

Stage-local log of decisions during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Under D-003 this stage runs decision-gated continuous: no per-stage human gate; blocking decisions would stop the loop, non-blocking ones go to `decision-queue.md`.

## Gate

- **Stage opened**: 2026-07-15 (automatic, D-003 lifecycle — `context-ready` → `in-progress`)
- **Stage closed**: not yet (awaiting critic)

## Executor judgment calls (not human decisions — recorded for the critic per `FINDING-SCHEMA.md`'s promotion rule and `CRITIC.md` §8/9)

### E-06-1: C11-vs-human workflow identity resolved from inherited principles, not raised as a human decision
The stage question "is the workflow identical regardless of change source" is answered **yes** (`outputs/statutory-change-control-design.md` §6). Reasoning recorded there: the controlled risk is the write, not the detection; D-02-04's containment logic requires an unconditional gate; no evidence forces a distinction. Stage 03's handoff already anticipated this ("should very likely be the same regardless of source"). Classified `not-a-decision` under `CRITIC.md`'s classification — creating a human gate here would be artificial.

### E-06-2: Stage 04's impact-assessment boundary question resolved at control level only
The control requirement is fixed (deterministic, computed against the exact proposed change and live state at review time, re-validated at application); the mechanism placement (C11-side advisory reuse) is forwarded to Stage 08 as `implementation-specification`. This does not adjudicate the product question Stage 04 declined to — it constrains any answer to satisfy the control.

### E-06-3: Tool-call log retention aligned to 7 years by derivation from the source document's own design
`agent_session_log` already embeds `tool_calls_jsonb`, so the document's 7-year proposal always covered tool calls; the resolution (`outputs/agent-tool-audit-standard.md` §2) formalises rather than invents. The *legal basis* of the 7-year figure is separately escalated (DQ-008) — the alignment decision and the legal-parameter question are deliberately kept apart.

### E-06-4: Severity calls on F-06-01 (High) and F-06-04/02/03 (Medium)
One-line justifications are inline in each finding per `SEVERITY-MODEL.md`. The judgment call worth flagging: F-06-01 is rated High rather than Critical to avoid double-counting F-05-01's systemic Critical framing — the two findings describe one root cause (no identity) at two layers (no enforcement / polluted records).

### E-06-5: F-05-11 deliberately NOT upgraded to control-failure classification
`outputs/tenant-isolation-control-assessment.md` §4: internal functions safe via caller discipline, on no attesting surface — kept at "weakness, fix-before-wrapping." Recorded so the critic can challenge the line-drawing.

## Human decisions raised by this stage

None blocking. Three non-blocking forwarded decisions added to `decision-queue.md`:

- **DQ-006** — Tier-1 authoritative-source allowlist for FIRS/PenCom requires human + professional legal/tax sign-off (stage context instructed escalate-don't-decide). Hard gate before C11 build authorisation; does not block review progression.
- **DQ-007** — single-operator segregation-of-duties waiver for C12 approvals (proposer ≠ approver may be impossible for a small bureau; compensating controls option stated). Must be resolved before C12 build authorisation.
- **DQ-008** — legal confirmation of the retention period (source document asserts 7 years without cited basis; statutory minimum and any data-protection maximum both need professional confirmation). Gates any retention-*enforcing* mechanism, not this review.

## Next action

**Independent critic review per `CRITIC.md`.**
