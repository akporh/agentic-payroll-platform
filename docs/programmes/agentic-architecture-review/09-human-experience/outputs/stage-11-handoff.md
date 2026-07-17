# Stage 09 → Stage 11 Handoff (Commercial & Product Strategy)

Surface-level scope and sequencing implications of the Stage 09 designs, plus the DQ-005 recommendation this stage owns jointly with Stage 11.

## 1. DQ-005 recommendation: `run_type = CORRECTION` UI exposure

**Stage 09 recommendation: do not expose CORRECTION in the generic Run Payroll dropdown; introduce it later as a context-launched action.** Reasoning:

- Verified at `7d36020`: the dropdown still offers `REGULAR`/`ADJUSTMENT` only, and the API still accepts `CORRECTION` (Stage 05 classification "usability gap", unchanged — F-09-02).
- A correction run is never a blank-slate decision — it corrects *something specific* (a consumed faulty statutory rule per C12's consumed-runs statement, or a specific defective run). The natural UX is a **"Create correction run" CTA launched from the correction context** (the C12 correction approval screen naming affected runs; potentially a run-detail action later), which can pre-fill period/type and carry the linkage — matching how the C10/C12 surfaces now give corrections a home (Stage 08 handoff item 8's observation).
- Exposing CORRECTION as a third dropdown option would put the platform's most semantically loaded run type one click from routine use, with no context, no linkage to what it corrects, and no guardrail — the cheap option is the wrong one.
- **Sequencing implication (Stage 11's half)**: this means CORRECTION UI exposure lands *with or after* the C12 build, not before; until then the API-only state persists deliberately. If Stage 11 finds a commercial need for standalone correction runs earlier, that is a scope decision to surface to the human reviewer with this reasoning attached — the queue entry stays open until Stage 11 disposes of it.

## 2. Immediate cheap fix, independent of the portfolio

The Run Payroll page still offers `FULL_RUN` retry, which the backend and DB always reject (re-verified at `7d36020`, F-09-02; Stage 05 classification "launch-risk"). Removing the dead radio option is a trivial frontend-only fix requiring no Phase 3 machinery — worth a maintenance slot whenever the page is next touched, and it should not wait for any capability build.

## 3. Surface-driven scope/sequencing facts

| Fact | Implication for sequencing/scope |
|---|---|
| Every designed surface assumes C1 auth (login, memberships, session, principals for actor display) | UI build order mirrors the mechanism order: auth surfaces first; nothing else ships before them (`remediation-designs.md` §9's C1-first, now true of the UX too) |
| Exception queue + notifications + pending actions are **three chrome additions** (two sidebar entries + TopBar bell) riding existing patterns (badge, SlideOver, AlertBanner) | Moderate frontend scope, no new design-system primitives required — the design deliberately reuses the existing component grammar; Phase 3 sprints stay in the standing `/ux-designer` → `/ui-designer` pipeline |
| C12 is the platform's **first platform-level area** (route family, chrome, PLATFORM_ADMIN gating — no platform area exists in today's router, evidence file §6) | One-off structural frontend cost beyond the C12 screens themselves; worth scoping as its own story so the platform-chrome work isn't hidden inside "statutory UI" |
| C13/C14 extend existing components (`NativeUploadFlow`, `ColumnMappingPanel`) rather than adding a wizard | Lower marginal UI cost than a greenfield onboarding product; the flow's stage boundaries also provide the EG-001/EG-003 baseline timestamps for free if emitted as events from day one — instrument the baseline **before** C13 ships (Stage 04's recommendation, now costed at near-zero) |
| Single-operator v1 posture is load-bearing in two designs: notification read-state (row-level `read_at`, broadcast rows — `notification-experience.md` §2) and exception ownership (assign-to-me against a membership list of one) | Multi-operator workspaces are a **scope boundary**, not a toggle: crossing it needs per-operator read state and real assignment/escalation flows. Stage 11 should treat "multi-operator bureau" as a distinct product increment with UX cost, not an account-settings change |
| Chat is one capability's surface (C3), gated behind refusal/grounding behaviours; everything else is queue/panel/approval surfaces | The commercial story is "a payroll platform with an assistant," not "a chat product" — consistent with Stage 02 Principle 8; demo/marketing sequencing should lead with the queue and approval surfaces where the auditable-AI differentiation is visible |

## 4. Deferred-by-design items (so Stage 11 doesn't re-open them as gaps)

- No notification preferences/muting, no toasts, no email (C15 deferred) — escalation-on-evidence posture (`notification-experience.md` §5).
- No recurring-error reporting UI (product-opportunity area 15) — the closed-exception history is the substrate; reporting is a later increment.
- No parallel-run comparison UI in the C13/C14 flow — EG-002's persist-ReconSlideOver-output first step remains a separate, cheap instrumentation item.
- No in-app escalation recipient model (exception Escalate is free-text in v1) — becomes real with multi-operator scope.
