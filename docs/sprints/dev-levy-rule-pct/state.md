# State — `dev-levy-rule-pct`

Authoritative per-stage status, per `WORKFLOW.md`. Stage IDs and dependency shapes are drawn from `STAGE-REGISTRY.md`. Mutated in place — `decisions.md` is the append-only log.

```yaml
sprint: dev-levy-rule-pct
status: complete

stages:
  roadmap:
    status: complete
    note: >
      Orientation done retroactively (2026-07-15/16) rather than at
      session start, since this sprint originated from an ad-hoc
      reconciliation investigation, not a /roadmap-first session.
      Confirmed by grep against docs/ROADMAP.md: neither story is
      currently tracked there. Flagged for the next /roadmap sync
      (mirrors the sec-s7 precedent of surfacing a stale-ROADMAP note
      rather than silently fixing it mid-sprint).

  pm:
    status: complete
    evidence: CONTEXT.md, decisions.md DEC-01 through DEC-09
    note: >
      Scope + AC drafted; three PM decisions via AskUserQuestion
      (2026-07-15), one cadence correction via chat (2026-07-16, DEC-04),
      and four further decisions resolving all arch-council open
      questions (2026-07-16, DEC-06 through DEC-09: arrears, INACTIVE
      edge case, rename, zero-override). Human gate (explicit scope
      confirmation) now fully satisfied, including the revised AC set
      that drops the original 184-employee reconciliation criterion.

  architecture:
    status: complete
    note: >
      Structural questions surfaced during arch-council review (cadence
      signal source -- per_employee_context_json vs contract dates;
      prorate_on_hire adoption for Story 2) resolved in the plan
      revision rather than a dedicated pre-plan /architect pass:
      is_first_paid_month computed via NOT EXISTS over prior
      payroll_result rows, threaded through the existing
      per_employee_context_json mechanism; prorate_on_hire: true
      adopted for Story 2. Both design decisions are recorded in
      ~/.claude/plans/steady-petting-orbit.md (revision of 2026-07-16).

  arch-council:
    status: complete
    evidence: architecture.md
    note: >
      Two-stage review run 2026-07-15 against the pre-revision plan
      draft. Interim combined verdict NEEDS REVISION (decisions.md
      DEC-05). Verbatim agent output was lost to a context compaction
      before persistence existed for it -- architecture.md is a
      reconstruction from surviving notes, flagged as such. All 4 open
      human decisions resolved (DEC-06 through DEC-09, 2026-07-16), and
      the plan file (~/.claude/plans/steady-petting-orbit.md) revised
      the same day to incorporate every one of the 9 ranked findings:
      deploy-order sequencing (code before migrations), ANNUAL cadence
      default, is_first_paid_month via per_employee_context_json,
      merge-not-replace PATCH semantics, PATCH validation, annual_amount
      rename, explicit zero-override support, prorate_on_hire adoption,
      BASIC save-time validation, dropped 184-employee AC, e2e test
      pinning. Judged mechanical enough not to warrant a second
      /arch-council pass for a verbatim record -- proceeding to
      ExitPlanMode. Re-open this stage (needs-rework, via a new
      decisions.md entry) if implementation surfaces a finding the
      revision missed.

  implementation:
    status: complete
    depends_on: [architecture, arch-council]
    evidence: plan.md, git diff (uncommitted), tests/test_sequential_executor.py, tests/test_rule_evaluator.py
    note: >
      Both dependencies terminal (architecture: complete, arch-council:
      complete). Plan approved 2026-07-16 (decisions.md DEC-10) via
      direct chat confirmation -- ExitPlanMode itself was unavailable
      since plan mode had already exited earlier in the session. Plan
      copied verbatim into plan.md per D5. All execution-order steps
      1-5 done: backend cadence handler + is_first_paid_month threading,
      migrations A+B, workspace.py PATCH validation/merge, frontend
      WorkspaceConfig.tsx (override field + PERCENTAGE_OF_BASIC), test
      housekeeping. Status was left stale at "eligible" after the work
      actually finished -- corrected here retroactively (2026-07-17)
      once the retro gate caught the discrepancy; not a retro-skill
      write, a bookkeeping catch-up by the implementation stage itself.

  verification:
    status: complete
    depends_on: [implementation]
    evidence: docs/sprints/dev-levy-rule-pct/evidence/verification/ (11 screenshots)
    note: >
      PASS. Live browser verification via Playwright (chromium, driven
      through the real Vite dev server + running backend + payroll_dev
      DB) — no MCP browser tool was available in-session, so a
      throwaway Playwright npm install in the scratchpad drove Chromium
      directly. Confirmed: (1) Add Payroll Rule slideover — Calculation
      Method dropdown shows "Percentage of Basic (%)", no
      PERCENTAGE_OF_GROSS; selecting it renders the percent field with
      correct copy; submitting with rate=7 saved successfully (a
      same-name/date collision on the first attempt correctly surfaced
      a 409 error banner live, confirming that path too). (2) Deductions
      tab -- Edit Override slideover for DEVELOPMENT_LEVY renders
      "Amount Override" with placeholder "Leave blank to use the
      statutory default (₦100/year)" (confirms annual_amount
      rename, DEC-08); entering 250 and saving persisted
      {"annual_amount": 250} to client_component_metadata.overrides_json
      via the real PATCH call -- verified directly against the DB, not
      just the UI. Zero console/page errors across both flows.
      Mid-session scope question from Michael (Percentage of Gross
      should remain a distinct, real option) was correctly deferred to
      a new backlog item (dream_catcher.md) rather than implemented
      ad hoc -- out of this sprint's scope. One pre-existing (2026-06-15,
      commit 57bf3181, unrelated to this sprint's diff) cosmetic bug
      surfaced and logged: Payroll Rules list table's RATE/AMOUNT column
      shows raw decimal with ₦ prefix for percentage_of_sum rules
      instead of a percentage -- backlogged, not a blocker.

  security:
    status: complete
    evidence: docs/security/2026-07-16-dev-levy-rule-pct-security-review.md
    note: >
      PASS. Reviewed patch_component_override + list_platform_components
      diff. One Medium hardening item logged (merge-not-replace increases
      persistence of an unvalidated overrides_json key injection) — not a
      blocker, follow-up story recommended. No auth-on-API gap is
      pre-existing repo-wide, noted but out of this sprint's scope.

  audit:
    status: complete
    evidence: docs/sprints/dev-levy-rule-pct/audit.md, docs/audit/2026-07-16-dev-levy-rule-pct-audit-review.md
    note: >
      PASS. CRITICAL finding caught and fixed this session: Story 2's
      percentage_of_sum rule-injected components (PERCENTAGE_OF_BASIC)
      were silently excluded from GROSS_PAY/NET_PAY by
      build_runtime_component_registry's Source-2 whitelist
      (sequential_executor.py:250 omitted "percentage_of_sum" — only
      unit_multiplier/fixed_amount/ot_multiplier were synthesised into
      the registry). component_trace_jsonb showed "status": "applied"
      with the correct amount, but the amount never reached
      results{}/gross_components_jsonb/NET_PAY. Confirmed by live
      reproduction against _run_sequential before and after the fix.
      Fixed: "percentage_of_sum" added to the whitelist tuple at
      sequential_executor.py:250; two new full-pipeline regression
      tests in tests/test_sequential_executor.py
      (TestBuildRuntimeComponentRegistry::test_percentage_of_sum_rule_added_as_earning,
      TestRuleInjectedEarningInGrossPay::test_percentage_of_sum_rule_injected_earning_included_in_gross_pay).
      Full suite re-verified green: 327 passed, 1 skipped (up from 325
      passed). tsc --noEmit clean. Story 1 (Development Levy cadence)
      was already correct and auditable; one non-blocking Observation
      logged for a future pass (is_first_paid_month not a named
      _period_context header field) — not a blocker.

  test:
    status: complete
    evidence: docs/test-reports/2026-07-16-dev-levy-rule-pct.md, docs/sprints/dev-levy-rule-pct/evidence/test/
    note: >
      PASS. 8 LIVE + 2 CODE REVIEW checks. Live-verified Story 1 both
      cadence branches (January-triggers, non-January/non-first-paid-
      month not-applied) plus PATCH override set/validate/null-delete,
      all via the real running API against the dev DB. Live-verified
      Story 2's fixed AC end-to-end: created HAZARD_ALLOWANCE
      (percentage_of_sum, base_components=["BASIC"], prorate_on_hire)
      via the actual rule-creation API using the exact payload shape
      the UI emits, ran a new period, confirmed it landed in both
      component_trace_jsonb AND gross_components_jsonb/net_pay — the
      exact path the /auditor CRITICAL finding had blocked. Full suite
      327 passed/1 skipped, tsc clean. Two items deferred (documented,
      not blockers): mid-month-hire proration for PERCENTAGE_OF_BASIC
      not live-exercised (covered by existing isolated unit test +
      code review of unmodified executor.py proration logic); Story 2
      SlideOver browser interaction not driven live (frontend dev
      server not started this session) — the API/DB behavior it drives
      was live-verified with the identical payload.

  retro:
    status: complete
    evidence: chat transcript 2026-07-17; skill/workflow updates below
    note: >
      Sprint Workspace Close Gate ran first: Part A (decision-integrity)
      clean, no discrepancies. Part B (terminal-status gate) initially
      FAILED — implementation (eligible) and verification (not-started)
      were stale; corrected in place (see those stages' notes) before
      retro proceeded, per the gate's explicit protocol (retro itself
      does not write other stages' statuses; the correction was made as
      each stage's own bookkeeping catch-up). 3 lessons captured, each
      closed with a concrete skill/workflow update: (1) auditor SKILL.md
      Check #13 — registry-synthesis reachability for new arbitrary-named
      rule-injected components (the CRITICAL finding's root class).
      (2) docs/sprints/WORKFLOW.md — new rule requiring state.md status
      to flip terminal in the same turn a stage's work finishes, not
      deferred. (3) pm SKILL.md — new checklist item: a "bug fix" that
      also removes a currently-selectable UI option is two decisions,
      not one; surface the capability-removal question explicitly
      (direct response to the mid-session Percentage-of-Gross pushback).
      Memory written: feedback_dev_levy_rule_pct_retro.md.
```

## Reading this file

- This sprint's entry point was unusual: it began mid-investigation, not at `/roadmap`. `roadmap` and `pm` were run retroactively rather than sequentially-first — recorded honestly here rather than reordered to look conventional.
- `arch-council` and `architecture` are both now `complete` — the plan revision (2026-07-16) closed every open finding and decision. `implementation`, `verification`, `security`, `audit`, and `test` are all now `complete` (2026-07-17) — `implementation` and `verification` were caught stale at `eligible`/`not-started` by the retro Sprint Workspace Close Gate and corrected in place, per the gate's own protocol, before retro proceeded.
- The compaction that lost the original verbatim arch-council output is the direct reason this workspace exists — see `architecture.md`'s provenance note.
