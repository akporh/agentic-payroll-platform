# Stage 10: Evaluation & Assurance — Findings

Schema: `_core/FINDING-SCHEMA.md`. Draft and confirmed findings are kept in separate sections below — never merge them.

## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

_None._

---

## Confirmed Findings

(meet the evidence standard in `_core/EVIDENCE-STANDARD.md` — safe to cite from later stages)

### F-10-01: No frontend test harness exists — none of Stage 09's 25 UX behaviours is automatable today

- **Current implementation**: `frontend/package.json` has no `test` script and no test framework or testing library in `devDependencies`; no vitest/jest config exists; zero `*.test.*`/`*.spec.*` files exist under `frontend/src` (find count = 0). CI's only frontend job is `tsc --noEmit` (`.github/workflows/tests.yml`, `frontend-typecheck` job). The absence is previously known and deliberate: the test-harness workstream parked T4.5 ("`grade_code` null on bulk upload") on exactly this ground — "frontend-only rule, no frontend harness exists; separate decision with Michael" (`docs/test-reports/test-harness/test-harness-checklist.md` §4).
- **Intended design**: Stage 09 hands Stage 10 twenty-five UX-testable behaviours whose failure would break a designed guarantee (`09-human-experience/outputs/stage-10-handoff.md`), the majority of which are component/DOM-level assertions; the repo's standing rule is that every bug fix ships a regression test named for its invariant (`CLAUDE.md` Test Harness section) — currently unsatisfiable for frontend-only rules.
- **Identified gap**: There is no mechanism to automate any UI-layer behaviour. Without a component-test harness, ~18 of the 25 behaviours fall to scripted manual checks (recurring per-release cost, weaker evidence), and behaviour 21 (Upload/Enroll `grade_code` separation) remains permanently unprotected — the T4.5 park becomes indefinite. Establishing a minimal frontend harness is therefore an assurance prerequisite, planned in `outputs/ux-verification-plan.md` §1 as part of the first frontend-touching build item (C1).
- **Evidence**: `frontend/package.json` (scripts + devDependencies, full read); `.github/workflows/tests.yml:49-68`; find count and checklist excerpt in `evidence/10-ci-and-harness-excerpts.md` §2. Read at commit `e4ad484`.
- **Severity**: Medium — meaningful assurance/technical debt: no current behaviour is broken, but a whole layer of designed guarantees has no automated enforcement path, and one standing repo rule (T4.5) is already unenforceable because of it.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 10 (verification-infrastructure grounding)

### F-10-02: CI has no scheduled-job seam — push/PR triggers only

- **Current implementation**: `.github/workflows/tests.yml` triggers on `push`/`pull_request` to `uat`/`main` only; no `schedule:` (cron) trigger and no `workflow_dispatch:` exists (grep count 0). The backend job runs the full pytest suite against a fresh `alembic upgrade head` database (fresh-DB rule confirmed in the workflow file itself, not just documentation).
- **Intended design**: n/a — grounding for assurance design, not a gap claim against any prior specification. Stage 10's standing-controls design (Q3) requires periodic/scheduled controls (LLM eval refresh, chain-completeness sweeps) in a form runnable without a standing human panel (`CONTEXT.md` Q2/Q3).
- **Identified gap**: None against current requirements (informational). Consequence recorded: the first scheduled assurance control to land must add a `schedule:` trigger (or equivalent runner) — `outputs/standing-assurance-controls.md` §5 assigns this to the same build item as the first Class B control it serves.
- **Evidence**: `.github/workflows/tests.yml:3-7` (triggers), full-file excerpt summary in `evidence/10-ci-and-harness-excerpts.md` §1. Read at commit `e4ad484`.
- **Severity**: Informational — the current CI shape is correct for the current platform; recorded as the concrete seam the assurance framework extends.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 10 (verification-infrastructure grounding)

### F-10-03: Documented suite size is stale — 328 tests collect at `e4ad484` vs the documented 306

- **Current implementation**: `python -m pytest --collect-only -q` collects 328 tests; a full run this session passed 327 with 1 skip (~7s, local dev DB — corroboration; CI remains the arbiter per the fresh-DB rule).
- **Intended design**: `CLAUDE.md` Test Harness section states "306 passed, 1 intentional Phase-2 skip" (dated 2026-07-12); `docs/test-reports/test-harness/test-harness-checklist.md` §5 records the same 306 figure.
- **Identified gap**: Documentation currency only — the suite has grown by ~21 tests since the harness workstream closed; the enforcement machinery (pre-push hook + CI) is unchanged and the suite is green. No behavioural gap.
- **Evidence**: command outputs duplicated in `evidence/10-ci-and-harness-excerpts.md` §3 (transient — duplicated per the evidence standard). Read/run at commit `e4ad484`.
- **Severity**: Low — cosmetic/doc currency; noted because Stage 10's evidence register treats "the committed suite" as an enforcement spine and its documented description should track reality.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 10 (verification-infrastructure grounding)

---

## Parked / Rejected

_None._

## Next action

**None — stage closed 2026-07-18 on critic PASS (zero required corrections; all three findings' citations independently reproduced by the critic).**
