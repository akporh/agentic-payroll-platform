# Stage 07: Security & Identity — Findings

Schema: `_core/FINDING-SCHEMA.md`, extended with the Stage 05/06 field pattern per this stage's `CONTEXT.md` finding discipline. Draft and confirmed findings are kept in separate sections below — never merge them.

All code evidence read at git commit `ea1590a37b626545022470e709107e30bcf45f66` (branch `uat`, 2026-07-17) — committed state only; no working-tree observations were used.

## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

_None._

---

## Confirmed Findings

(meet the evidence standard in `_core/EVIDENCE-STANDARD.md` — safe to cite from later stages)

### F-07-01: Decorative workspace scoping extends beyond reconciliation — two further routes accept and discard `workspace_id`
- **Affected capability(ies)**: C1 (route-hardening scope), C8 (closure-evidence bar), every consumer of the isolation control statement
- **Current implementation**: an exhaustive sweep of all 72 `{workspace_id}` routes (evidence file §1) found five — not three — routes whose `workspace_id` appears only in path and signature: the F-05-03 reconciliation trio (re-resolved at `ea1590a` to `payroll.py:1327/1336/1352`) **plus** `get_run_timeline` (`payroll.py:1372` → `get_trace_steps(run_id)`, `execution_trace_repo.py:102` filters on `run_id` only) and `legacy_executor_stats` (`payroll.py:1378` → `get_legacy_executor_stats()`, no parameters — platform-wide aggregates including other workspaces' `run_id` values in its `by_run` breakdown, `execution_trace_repo.py:45-58`). Spot-checks confirmed the remaining low-occurrence routes thread `workspace_id` through.
- **Intended design**: sibling routes in the same file enforce `WHERE payroll_run_id = :rid AND workspace_id = :wid` (Stage 05's contrast set); the path shape itself asserts workspace scoping. No documented intent permits a workspace-pathed route to ignore the parameter.
- **Identified gap**: any caller can read any run's execution-trace steps (step names, error messages, durations) cross-workspace, and platform-wide run statistics under a workspace-scoped path — the same false-attestation pattern Stage 06 classified as control-failure-shaped (F-06-05), now confirmed as a recurring scaffolding habit rather than a reconciliation one-off.
- **Evidence**: `evidence/07-route-scoping-and-identity-excerpts.md` §§1–3
- **Severity**: Medium — cross-tenant exposure is operational/trace metadata (step names, error text, run IDs, aggregate counts), not payroll amounts or PII; the pattern significance (a third and fourth instance of decorative scoping) exceeds the data sensitivity of these two routes.
- **Classification**: control weakness on these two routes (no client-payroll data exposed); pattern-level confirmation that the per-route verification standard must be exhaustive and mechanized, not enumerated by hand.
- **Minimum remediation**: enforce token-derived workspace on both routes (R2 path); `legacy_executor_stats` additionally either scopes its aggregates to the caller's workspace or moves to an explicit platform-ops surface — it must not remain both platform-wide and workspace-pathed (`tenant-isolation-verification-standard.md` §3.3).
- **Closure evidence**: the route-table isolation test (`tenant-isolation-verification-standard.md` §3.2) green with these routes enforced or allowlisted; invariant-named regression tests for both.
- **Confidence**: High
- **Required human decision**: none — remediation shape follows from R2 and the existing standard.
- **Downstream owner**: Stage 08 (fix, with the R2 enforcement work — `outputs/stage-08-handoff.md` item 3); SG-8/SS-1 gates.
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 07, tenant-isolation investigation (§2 of `CONTEXT.md`)

### F-07-02: `workspace_info()` is a live, reachable route; its arbitrary-workspace pick affects only the legacy admin template
- **Affected capability(ies)**: C1 (route hardening); the F-05-11 fix-before-wrapping gate (unchanged)
- **Current implementation**: `GET /workspace/info` (`workspace.py:133-146`) selects an arbitrary workspace via `LIMIT 1`. Caller check (the question Stage 05 forwarded): the React frontend declares `getInfo` (`frontend/src/api/workspace.ts:12`) but **no frontend code consumes it**; the only live consumer is the legacy admin template (`backend/api/templates/payroll.html:30`, served by `admin.py:26-27`); no backend Python callers exist.
- **Intended design**: undocumented — the route predates multi-workspace support; no spec claims it is workspace-correct.
- **Identified gap**: in a multi-workspace deployment the legacy admin page displays an arbitrary client's name and active-employee count — wrong today for that page, not merely wrong-if-tool-wrapped. The modern React frontend is unaffected. F-05-11's "not safe under any circumstances to wrap" stands unchanged.
- **Evidence**: `evidence/07-route-scoping-and-identity-excerpts.md` §4
- **Severity**: Low — the exposed data is workspace name + headcount on an internal legacy page; the deployment currently operates with a single primary client workspace. Rated on present impact; the wrap-risk is already carried by F-05-11.
- **Classification**: control weakness (stale surface); answers the Stage 05/CONTEXT question — it *is* producing wrong results in principle, but the blast radius is confined to the legacy template.
- **Minimum remediation**: retire the route with the legacy admin template, or require explicit token-derived workspace identity (post-C1); the `LIMIT 1` form must not survive C1 (SG-1).
- **Closure evidence**: route removed or token-scoped with a test; `frontend/src/api/workspace.ts` dead declaration removed.
- **Confidence**: High
- **Required human decision**: none.
- **Downstream owner**: Stage 08 (`outputs/stage-08-handoff.md` item 8).
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 07, tenant-isolation investigation — `workspace_info()` caller check (§2 of `CONTEXT.md`)

### F-07-03: CORS origin allowlist defaults to `*` with the production-tightening intent documented but unenforced
- **Affected capability(ies)**: C1 (deployment surface)
- **Current implementation**: `backend/api/main.py:36-45` — `ALLOWED_ORIGINS` env var defaults to `*`; `allow_credentials=False`; all methods/headers allowed. The code comment states "Defaults to `*` for UAT/preview. Tighten to the Vercel URL in production."
- **Intended design**: the comment itself — wildcard is a UAT convenience, production pins origins. No mechanism enforces the production posture.
- **Identified gap**: nothing distinguishes a production deployment from UAT at the CORS layer; the tightening relies on an operator remembering an env var. With header-borne bearer tokens (the C1 direction) and `allow_credentials=False`, wildcard origins do not enable cookie CSRF — the exposure is that any web origin can call the API, which matters once tokens exist to steal/replay from browser contexts.
- **Evidence**: `evidence/07-route-scoping-and-identity-excerpts.md` §7
- **Severity**: Low — no authentication exists yet (F-05-01 dominates every network-surface concern); this becomes meaningful exactly at C1 launch, which is why it is gated there rather than rated higher now.
- **Classification**: hardening requirement, attached to C1's launch gate rather than the current posture.
- **Minimum remediation**: production origin pinning as a mandatory C1 deployment-checklist item with deployed-config closure evidence (SG-1; `identity-architecture-requirements.md` §7).
- **Closure evidence**: deployed production config inspection showing pinned origins, recorded at C1 launch.
- **Confidence**: High
- **Required human decision**: none.
- **Downstream owner**: Stage 08/C1 build (deployment checklist).
- **Status**: confirmed
- **Date**: 2026-07-17
- **Raised by**: Stage 07, identity-architecture investigation (§1 of `CONTEXT.md`)

---

## Parked / Rejected

_None._

## Next action

**Stage 07 marked `awaiting-critic` — run the independent critic per `CRITIC.md`.**
