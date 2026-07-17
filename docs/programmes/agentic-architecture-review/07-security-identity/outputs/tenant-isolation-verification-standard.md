# Stage 07 Output: Tenant-Isolation Enforcement & Verification Standard

Defines the two-layer enforcement standard (D-02-02) and — the heart of this document — the **verification standard that proves it**, extending Stage 06's control-evidence set (`tenant-isolation-control-assessment.md` §3) with this stage's own route-sweep evidence. New facts here: the decorative-scoping pattern is confirmed to extend beyond reconciliation (F-07-01), and the `workspace_info()` caller question is answered (F-07-02).

## 1. The two-layer enforcement standard (restated, not re-derived)

Per D-02-02 (binding, HD-3):

- **Layer 1 — repository/query level**: every workspace-owned table's read/write path filters by `workspace_id` at the query itself (the project's existing standing rule), with the `workspace_id` sourced per R2 (token claim, never caller input).
- **Layer 2 — tool layer**: every agent tool independently verifies workspace ownership before serialising results (`tool-layer-security-pattern.md`), regardless of Layer 1's correctness. Neither layer substitutes for the other.

Beneath both layers, C1 provides the enforcement floor (F-05-01/F-06-05: without verified identity, both layers only constrain honest callers).

## 2. Why the verification standard must be route-exhaustive: the pattern recurred

Stage 06 required "a negative-path check for every route that presents as workspace-scoped" (§3.3) on the strength of the three reconciliation routes. This stage's exhaustive sweep of all 72 `{workspace_id}` routes (evidence file §1) found **two further routes** that accept and discard `workspace_id`:

- `get_run_timeline` (`payroll.py:1372`) — returns any run's execution-trace steps cross-workspace (evidence §2)
- `legacy_executor_stats` (`payroll.py:1378`) — returns **platform-wide** run statistics including other workspaces' run IDs, under a workspace-scoped path (evidence §3)

Neither was known to Stages 01–06. This confirms the false-attestation pattern (F-06-05) is a *scaffolding habit*, not a one-off — reconciliation-only remediation would have shipped the control statement with two silent counterexamples. Recorded as F-07-01.

## 3. The verification standard (what "proven" means)

Isolation is **proven** when all five hold, as committed code/tests — not plans:

1. **Invariant-named regression tests** for every fixed gap (project standing rule): cross-workspace request with Workspace A's token against Workspace B's resource → 404, asserted per invariant.
2. **Per-route negative-path test, exhaustively**: for **every** route whose path contains `{workspace_id}`, a test asserts a mismatched token-vs-path request is rejected and a cross-workspace resource ID under a matching path returns 404. The route list is generated from the app's route table at test time (FastAPI exposes it), so a newly scaffolded route without enforcement **fails CI by default** rather than joining the decorative set silently. This mechanization is this stage's addition to Stage 06's per-route requirement — the sweep in evidence §1 is exactly the check, run once by hand; the standard is that it runs on every commit.
3. **Unscoped-surface allowlist**: routes intentionally not workspace-scoped (platform-level: `get_statutory_rules` data, health, login) are enumerated in the isolation control statement; the route-table test asserts every route is either workspace-enforced or on the allowlist. `legacy_executor_stats` must end up on one side deliberately: either scoped to the caller's runs, or moved to an explicit platform-ops surface — it may not remain both platform-wide and workspace-pathed.
4. **Isolation control statement** (Stage 06 §3.4): the one-page maintained artefact — which tables carry workspace scoping, which are platform-level by design, where enforcement lives (dependency layer + query layer + tool layer). This stage adds: the statement must cite the route-table test (item 2/3) as its standing proof, so the document cannot drift from the code.
5. **F-05-11 function closures**:
   - `load_inputs_for_run` — caller-discipline safety re-verified at `ea1590a` (evidence §5; the retry path derives workspace from the run row). Closure per Stage 05: add a `workspace_id` parameter and filter (preferred), or enforce non-exposure. It must never be tool-wrapped as-is.
   - `workspace_info()` — **caller question answered** (evidence §4): live route; consumed only by the legacy admin template (`payroll.html:30` via `admin.py:26-27`); declared but unused in the React API client (`frontend/src/api/workspace.ts:12`); no backend callers. In a multi-workspace deployment the legacy admin page would display an arbitrary client's name and headcount — wrong today, not just wrong-if-wrapped, but confined to an internal legacy page (F-07-02, Medium). Closure: the route requires an explicit workspace identity derived from the token (post-C1) or is retired with the legacy template; the `LIMIT 1` form must not survive C1.

## 4. Ordering (consistent with Stage 05's closure plan)

The three decorative reconciliation routes remain the most urgent fix (false attestation on bureau-client financial data, F-05-03 Critical). The two new routes join the same remediation class at lower data sensitivity (F-07-01, Medium — trace/ops metadata, not payroll amounts). Route-enforcement fixes (no schema change needed) precede the `payroll_reconciliation` column work, per Stage 05's own sequencing. All of it lands under CG-8/SG-8 gating for C8, and item 2's route-table test is the mechanism that keeps the fixed state fixed.
