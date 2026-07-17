# Stage 07 Output: Tool-Layer Security Pattern

Resolves Stage 03's Condition 14 / specification question 7 (`03-agent-portfolio/outputs/stage-08-handoff.md`): **one** concrete enforcement pattern for independent workspace-ownership verification, applied uniformly to all 11 tools in `tool-portfolio-matrix.md` (the original 10 plus the C13 workspace-catalog tool). Requirements level: the pattern's mandatory properties and its verification standard. Stage 08 implements it.

## 1. The pattern: a single shared tool-guard wrapper with declarative scoping

Every tool is registered through one shared wrapper (decorator/middleware — Stage 08's structural choice), never invoked bare. The wrapper owns four responsibilities; individual tool bodies own none of them:

1. **Verified context in** — the wrapper receives the verified principal and active `workspace_id` from the session's token (C1). Tool parameters supplied by the LLM **never include workspace identity**; the model cannot ask for a workspace, only for resources, which the wrapper checks against the session's workspace. (This kills tool-parameter tampering as a cross-tenant vector by construction — see `agent-layer-threat-model.md` §2.)
2. **Declarative ownership check** — each tool *declares* its scoping anchor as registration config rather than hand-rolling a check: the owning table and how to resolve ownership from the tool's parameters (e.g. `get_employee`: `employee.workspace_id` via `employee_id`; `get_run_results`: through `payroll_run.workspace_id` via `run_id`; `get_enrollment_status`: through `employee.workspace_id` since `employee_contract` carries no workspace column, per the matrix). The wrapper executes the declared check with its own query before the tool body runs. Declarative-not-procedural is what makes uniformity *verifiable* (§3) — ad hoc per-tool checks are exactly the drift risk F-03-07 named.
3. **Explicit platform-level declaration** — a tool over platform-level data (`get_statutory_rules`) declares `scoping: platform-level` affirmatively. The wrapper still runs (audit, refusal handling, serialization rules); nothing is exempt from registration, and "no declaration" is a startup error, never a silent pass-through (**fail closed**).
4. **Uniform refusal + audit out** — ownership failure produces the tool matrix's 404-style refusal (no existence disclosure), logged as a first-class `refused` outcome per the agent/tool audit standard (SC-3, `agent-tool-audit-standard.md` §3). Success paths apply the serialization rules on exit: PII stripping per the versioned rule-set, Decimals as strings (Stage 03 cross-cutting rules 3 and the matrix's PII column).

## 2. Mandatory properties (the checklist Stage 08 builds against)

| # | Property |
|---|---|
| P1 | No tool callable except through the wrapper; registration is the only path into the tool runtime |
| P2 | Workspace identity from the verified session only; never a tool parameter, never LLM-supplied |
| P3 | Every tool declares scoping config (ownership anchor or explicit `platform-level`); missing config fails startup |
| P4 | Ownership check executes independently of the underlying repository function's own scoping (D-02-02 defence-in-depth — the wrapper's query, not trust in the repo) |
| P5 | Refusals: 404-style, uniform, logged as `refused` with the attempted parameters (SC-3) |
| P6 | Output side: versioned PII sanitizer applied; Decimal-as-string; `component_trace_jsonb = null` and similar nullable dependencies handled per the matrix's explicit-null rules |
| P7 | Every invocation writes the SC-3 audit record (verified identities, tool+version, params, outcome class, result digest, PII rule-set version) |
| P8 | Blocked tools (`get_reconciliation` until D-02-02 preconditions clear) are not registered at all — absence from the registry, not a disabled flag |

## 3. Verification standard (Condition 14 "applied consistently" — proven, not asserted)

1. **Uniformity test**: a test enumerates the tool registry and asserts every registered tool has scoping config and that the set of registered tools equals the approved portfolio list (11 minus blocked). A 12th tool without config cannot ship green.
2. **Per-tool negative-path test**: for each workspace-scoped tool, a cross-workspace fixture (resource in Workspace B, session in Workspace A) must produce the refusal outcome and the `refused` audit record — the tool-layer mirror of the route-table standard in `tenant-isolation-verification-standard.md` §3.2.
3. **Wrapper-independence test**: for at least one tool whose repository function is deliberately stubbed to *not* filter by workspace, the wrapper still refuses — demonstrating P4 is real, not inherited (this is the test form of "the function already works for its current caller was true and irrelevant," Stage 05's framing).
4. **Fail-closed test**: registering a tool without scoping config raises at startup.

## 4. Scope notes

- The wrapper pattern binds the 5 LLM-touching capabilities' tools (C3, C5, C7-narration, C11, C13). Deterministic capabilities (C6, C12, C14) act through ordinary authenticated routes, covered by the route-layer standard instead — same guarantees, different chassis.
- Contract details per tool (fields, bounds, null semantics) remain Stage 08's specification work (`03-agent-portfolio/outputs/stage-08-handoff.md` items 3, 4, 8); nothing here pre-empts them beyond the security properties.
