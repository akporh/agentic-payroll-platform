# Stage 13 — Consolidated Remediation Backlog

**Status:** complete
**Opened:** 2026-07-13
**Closed:** 2026-07-13

This is a backlog/design stage. No application code, migration, test, script, or data was changed. Every item below is a synthesis of Stages 01–12's already-committed findings — no new investigation was performed; where this document states a fact, it is sourced from a specific prior-stage finding ID, cited inline.

---

## 1. Executive remediation summary

The Phase 1 MVP payroll calculation engine is arithmetically sound and well-tested (306 passing tests, deterministic; `04-001`'s statutory-divergence defect and `05-001`'s silent-failure gap are both remediated and regression-protected). **The platform cannot be used with live/production payroll data in its current state for one reason above all others: there is no authentication, account membership, or authorization anywhere in the application (`09-000`).** Every other confirmed security finding (`09-001` through `09-008`, `06-007`) is a direct or structural consequence of that single gap. This is the dominant, backlog-topping item.

Beyond security, the remaining confirmed gaps are bounded and well-understood: two data-integrity hardening items (`08-001` nullable `employee_number`, `08-002` missing immutability window before `PAID`), one approved-but-unimplemented observability design (Stage 10's execution-trace package), one background-failure edge case (`07-003`), one live product-policy question (`03-004`), one legacy-code disposition already decided (`01-004`), a handful of frontend contract-drift bugs (`06-001`–`06-006`, Stage 12's `PayrollRunStatus` finding), and a bounded set of low-risk code-simplification quick wins (Stage 12).

**Nothing found in this audit programme indicates the calculation engine itself produces wrong payroll numbers today** (`04-001` is fixed; `04-004` is structurally rejected; every financial arithmetic/invariant scenario in Stage 11 passed). The risk profile is entirely about *who can reach the system and do what*, and about *observability/auditability* of what happens — not about whether the sums are right.

**Recommended sequencing headline:** Programme 1 (authentication/tenancy/RBAC foundation) must complete before Programme 2 (route ownership closure) and before any live/production-data use. Programmes 3–4 (error/export/audit hardening, data-integrity corrections) can proceed in parallel with Programme 1 since they are independent of authentication. Programme 5 (execution trace) splits into an auth-independent schema/write-side half and an auth-dependent query half. Programmes 6–8 (statutory policy, legacy-executor transition, frontend completeness, simplification) are lower urgency and can trail the security programme.

---

## 2. Canonical finding-to-backlog crosswalk

| Finding | Stage | One-line description | Disposition | Backlog item |
|---|---|---|---|---|
| `01-002` | 01 | Second ORM repository directory (`backend/infra/db/repositories/`) | retain, rename+document | B-8.1 |
| `01-004` | 01/12 | Legacy executor fallback reachable from live route | implement (phased) | B-6 |
| `02-002` | 02/07/10 | Retry writes zero `execution_trace` rows | implement (Stage 10 design) | B-2 |
| `02-009` | 02 | `export_payroll_register_csv` shape mismatch, zero callers | defer (Stage 13 backlog, low priority) | B-10.5 |
| `03-002` | 03 | Retry re-resolved live statutory rule instead of frozen snapshot | **remediated** (`04-001`) | closed |
| `03-003` | 03/05 | `employee_contract_snapshot.components_jsonb` dead column | implement (`05-002`) | B-8.2 |
| `03-004` | 03/08/09 | Statutory-component disablement policy undecided | **policy decision required** | B-5 |
| `04-001` | 04 | Original-run/retry statutory divergence | **remediated, closed** | closed |
| `04-002` | 04/05/10 | No per-result statutory-rule identity | implement (Stage 10 design) | B-2 |
| `04-004` | 08 | Retry/reconciliation temporal overlap | **rejected, no action** | closed |
| `05-001` | 05 | Snapshot-creation failure could leave a run stuck silently | **remediated, closed** | closed |
| `05-002` | 05 | `employee_contract_snapshot.components_jsonb` dead, safe to remove | implement | B-8.2 |
| `05-003` | 05 | `payroll_result.salary_inputs_snapshot` write-only | **retain intentionally** | closed |
| `05-004` | 05 | Snapshot immutability inconsistent across tables | implement | B-4C |
| `05-005` | 05/12 | Duplicated statutory-rate extraction logic, still live post-`04-001` | implement (low risk) | B-8.3 |
| `06-001` | 06 | `FAILED` status/`error_message` not surfaced in frontend | implement | B-7A |
| `06-002` | 06/08 | `pay_cycle.definition_json` unavailable for post-onboarding view/edit | implement | B-4D |
| `06-003` | 06 | Dead `FULL_RUN` retry-strategy UI option | implement (small) | B-7B |
| `06-004` | 06 | `ActionPanel` has no `FAILED` branch, falls through to `null` | implement (same package as `06-001`) | B-7A |
| `06-005` | 06 | Salary-definition edit UX friction | optional polish, not required | deferred, low priority |
| `06-006` | 06 | `timesheet/audit/{employee_id}` — missing UI feature (resolved: not intentionally API-only) | implement | B-7C |
| `06-007` | 06/09/11/12 | Legacy unscoped reconciliation routes, insecure, zero callers | implement (quick win) | B-1E |
| `07-001` | 07/09/11 | 21 sites returning raw exception text; 10 structurally unsafe, 11 currently safe | implement | B-1F |
| `07-002` | 07/08 | Reconciliation create/resolve has no unified `audit_log`/`event_store` entry | implement | B-1G |
| `07-003` | 07/11 | Outer background-task failure remains log-only; no safe test seam exists | implement | B-3 |
| `07-004` | 07/12 | Stray module-level `print()` in `paye.py` | implement (trivial) | B-8.4 |
| `07-005` | 07/10 | Retry trace parity decision — resolved: minimal subset | **decided**, implement via Stage 10 design | B-2 |
| `08-001` | 08/11 | `employee_number` nullable due to swallowed migration exception | implement | B-4A |
| `08-002` | 08 | `payroll_run` totals/period not DB-immutable before `PAID` | implement | B-4B |
| `08-003` | 08/09/10 | Disabled statutory components leave no trace/guard signal | implement (visibility: Stage 10 design; guard: tied to `03-004`) | B-2, B-5 |
| `09-000` | 09/11 | No authentication anywhere in the application | **implement — S0 blocker** | B-1A |
| `09-001` | 09/11 | `GET /workspaces` enumerates all tenants unauthenticated | implement | B-1D |
| `09-002` | 09/11 | Retry/approve/lock/pay/legacy-reconcile unscoped, no ownership check | implement | B-1D, B-1E |
| `09-004` | 09/11 | Reconciliation routes accept but discard `workspace_id` | implement | B-1D |
| `09-005` | 09/10/11 | Timeline route accepts but discards `workspace_id` | implement (Stage 10 design + auth) | B-1D, B-2 |
| `09-006` | 09/11 | Legacy-executor-stats leaks global cross-tenant data | implement | B-1D, B-1E |
| `09-007` | 09/11 | Unauthenticated admin/operator dashboards | implement | B-1E |
| `09-008` | 09/11 | CSV/formula injection in exports | implement | B-1H |
| Stage 10 package | 10/11 | Retry trace, statutory identity, excluded-component visibility, tenant-safe timeline — approved design | implement | B-2 |
| Stage 11 — 8 permanent-test recs | 11 | Tenant-ownership, `employee_number` NOT NULL, run immutability, exclusion trace, fault-injection, retry trace/identity, export sanitization, migration smoke tests | implement, embedded in each package's acceptance criteria | B-9 |
| Stage 12 — `PayrollRunStatus` duplication/drift | 12 | Two frontend types, both wrong relative to backend enum | implement (bundle with `06-001`) | B-7A |
| Stage 12 — cleanup candidates | 12 | Repository rename, dead column, shared helper, print removal, script rename, stale docs | implement (quick wins) | B-8 |

---

## 3. Deduplicated backlog register — see Programme sections (§7) for full item specifications

Consolidation notes applied per this stage's own principles:
- `05-005` and `05-002` each appear once, even though observed across Stages 03/05/12 — cross-references preserved above, not restated as separate items.
- `08-003` appears in two backlog items (`B-2` for the visibility half, `B-5` for the guard/policy half) because Stage 10 explicitly separated "can we see it happened" (design-ready, policy-neutral) from "should it be allowed at all" (`03-004`, still undecided) — these are not the same remediation and must not be merged into one item, per this stage's own instruction not to conflate visibility with permission policy.
- `09-005` appears in both the security programme (`B-1D`, the ownership-check half) and the trace programme (`B-2`, the schema/query half) because Stage 10's own design split it exactly this way — the schema change is auth-independent and can ship early; the actual authorization check is auth-dependent.
- `06-007` and `09-002` are the same underlying route pair, described from two different angles (UI-wiring absence vs. security risk) — one backlog item (`B-1E`), not two.

---

## 4. S0/S1 production-release gate

**No live or production-data payroll processing may begin until all of the following are complete:**

| # | Gate item | Source | Severity |
|---|---|---|---|
| G1 | Authentication foundation implemented and enforced on every route | `09-000` | S0 |
| G2 | Account/workspace membership and RBAC implemented | `09-000` (tenancy model) | S0 |
| G3 | Every route in `09-001`/`09-002`/`09-004`/`09-005`/`09-006` verifies workspace ownership server-side, not merely accepts a path parameter | `09-001`,`09-002`,`09-004`,`09-005`,`09-006` | S0 |
| G4 | Legacy unscoped reconciliation route pair removed or secured | `06-007` | S1 |
| G5 | Admin/operator dashboards protected by authentication+role | `09-007` | S1 |
| G6 | Raw exception disclosure fixed for all 10 Group A sites | `07-001` | S1 |
| G7 | CSV/formula-injection sanitizer applied to all exports | `09-008` | S2 (gate as S1-adjacent given export data sensitivity) |
| G8 | `employee_number` genuinely `NOT NULL` in production (post-inventory/pre-check) | `08-001` | S2 |

**Everything else in this backlog (execution-trace package, `07-003`, `08-002`/`05-004` broader immutability, `03-004` policy, legacy-executor transition, frontend completeness, code simplification) is valuable but does not block the release gate above** — it is sequenced as post-foundation hardening (Programmes 3–8), per this stage's principle that maintainability/observability work must never be promoted above production blockers, and conversely that a large security programme must not be used as an excuse to delay independently-shippable lower-risk fixes indefinitely.

---

## 5. Security programme specification (Programme 1)

### B-1A — Authentication foundation (`09-000`)

- **Source findings:** `09-000`
- **Severity / release gate:** S0 / must complete before any live/production-data use
- **Scope:** Choose and implement an authentication mechanism (session or token-based; a managed identity provider is a reasonable option given this is a small-team bureau tool, but the specific choice is an implementation decision, not re-litigated here). Add user/account identity storage, backend `current_user` dependency applied to every route, frontend login/session handling, a `401` contract for unauthenticated requests, removal of the permissive `ALLOWED_ORIGINS="*"` CORS default in production configuration, and secure secret handling for whatever credential/token mechanism is chosen.
- **Explicit non-scope:** Does not include RBAC role definitions (B-1C) or workspace membership (B-1B) — this item is "does a request have a verified identity at all," not "what can that identity do."
- **Dependencies:** None — this is the foundation everything else in Programme 1–2 depends on.
- **Migration/API/UI impact:** New identity/session tables; every existing route gains an auth dependency (additive at the route-decorator level, not a rewrite of business logic); frontend gains a login flow and auth-token/session propagation on every API call.
- **Acceptance criteria:** every route returns `401` with no valid identity, verified by an automated test hitting a representative sample of each route family; no route bypasses the dependency (verified by a static/lint check enumerating all registered routes and asserting each has the auth dependency — this closes exactly the class of gap `09-004`/`09-005` demonstrated, where a dependency was assumed but not actually wired); CORS is restricted to known frontend origins in production configuration.
- **Required tests:** unauthenticated-access-denied test across every route family (Stage 11 permanent-test rec #1, reused here).
- **Rollback:** feature-flag the auth requirement during rollout if a phased cutover is preferred; standard migration downgrade for any new tables.
- **Owner/discipline:** backend + security-focused review.
- **Sprint/package:** Programme 1, first item.
- **Effort:** L — new subsystem, touches every route.

### B-1B — Account/workspace membership and tenancy

- **Source findings:** `09-000` (tenancy model, resolved 2026-07-12)
- **Severity / release gate:** S0 / must complete before any live/production-data use
- **Scope:** Implement the approved model — one bureau account manages multiple client workspaces via explicit membership rows (not inferred from a caller-supplied UUID). Schema: account, user, account-membership, workspace-entitlement tables. Membership model must be extensible to future direct-client users without redesign (per the approved decision), even though direct-client users are out of current scope.
- **Explicit non-scope:** Direct-client user onboarding itself (deferred feature) — only the extensibility of the data model is in scope now.
- **Dependencies:** requires B-1A (an authenticated principal to attach membership to).
- **Migration/API/UI impact:** new tables; workspace-listing and workspace-scoped routes change their query to filter by the caller's actual entitlements rather than returning/accepting any workspace_id.
- **Acceptance criteria:** `GET /workspaces` (currently `09-001`'s enumeration bug) returns only workspaces the caller has membership in; a caller with no membership in workspace B cannot reach any workspace-B-scoped route regardless of the `workspace_id` they supply.
- **Required tests:** workspace-enumeration-is-scoped test (Stage 11 rec #1, applied here specifically).
- **Rollback:** standard migration downgrade; no data loss since membership rows are additive.
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 1, second item, immediately after B-1A.
- **Effort:** M.

### B-1C — RBAC (role-based access control) — includes Decision D4 RESOLVED

- **Source findings:** `09-000` (role model, resolved 2026-07-12)
- **Severity / release gate:** S0 / must complete before any live/production-data use
- **Scope:** Implement the 5 approved minimum roles (platform administrator, bureau administrator, payroll operator, payroll approver, read-only auditor/viewer) with a role matrix covering: workspace discovery, employee/contract/configuration changes, payroll creation/retry, approval, lock, mark-paid, reconciliation create/resolve, exports, traces/audit-log access, admin/diagnostic access.
- **Decision D4 (approved at Stage 13 close): soft separation of duties with explicit audit flagging**, between payroll operator and approver. A user may hold both roles. Same-person approval of a run they created or last retried is **permitted but must be visibly flagged**: the approval action writes a distinct audit/event record containing creator/retrier identity, approver identity, timestamps, and a `same_actor_approval` boolean indicator; the UI displays a warning before confirmation when the approver is also the run's creator/last-retrier, and this flag is surfaced in the run's audit history, not only at the moment of approval; reporting/audit views must allow these same-actor approvals to be filtered and reviewed as a distinct category. The role model must be built so a later upgrade to hard separation (rejecting same-actor approval outright) requires only a policy-check change, not a schema/role redesign — this decision does not foreclose that future option.
- **Explicit non-scope:** this item does not implement hard separation — D4 explicitly rejected it for now, given Sandy's small-team operational reality; the door is left open architecturally, not built now.
- **Dependencies:** requires B-1A, B-1B.
- **Migration/API/UI impact:** new role/permission tables or an equivalent in-code policy table, plus a `same_actor_approval` field on the approval audit record; every mutating route gains a role check in addition to the ownership check (B-1D); frontend gains role-aware UI (hide/disable actions the current role cannot perform, backed by server-side enforcement — never UI-only, per Stage 09's explicit rule that UI hiding is not authorization) plus the D4 same-actor warning UI.
- **Acceptance criteria:** each of the 10 listed operation categories has a defined, server-enforced role requirement; a caller with a role lacking permission for an action receives a `403` (not merely a hidden button); platform-administrator access is logged/audited distinctly from ordinary role-based access; a same-actor approval succeeds (not blocked) but produces a `same_actor_approval=true` audit record and a UI warning at confirmation time; a different-actor approval produces `same_actor_approval=false` with no warning.
- **Required tests:** lifecycle-actions-denied-for-wrong-role test; platform-admin-access-explicit/audited test (Stage 11 recs); same-actor-approval-flagged test (new, per D4).
- **Rollback:** standard migration downgrade.
- **Owner/discipline:** backend + frontend (D4's warning UI) + product input on the role matrix.
- **Sprint/package:** Programme 1, third item.
- **Effort:** M.

### B-1D — Mandatory ownership checks (`09-001`, `09-002`, `09-004`, `09-005`, `09-006`)

- **Source findings:** `09-001`, `09-002`, `09-004`, `09-005`, `09-006`
- **Severity / release gate:** S0 / must complete before any live/production-data use
- **Scope:** Implement the one reusable authorization chain specified in the CONTEXT.md (`authenticated principal → bureau account/role → workspace entitlement → parent resource ownership → child resource ownership → workspace-scoped repository query`) as a shared dependency/decorator applied consistently, not ad hoc per route — directly closing the pattern Stage 09/12 named ("path declares `workspace_id`, handler discards it"). Apply to every route family: `GET /workspaces` (via B-1B), retry/approve/lock/pay (currently unscoped — these routes must be **rewired to accept `workspace_id`**, not just gain a check, since they currently have no path segment to check against at all), reconciliation (currently decorative — wire the already-present `workspace_id` parameter into the actual query), timeline (same), legacy-executor stats (must become genuinely workspace-filtered, not just gain a check on an unfiltered query), exports (already has the correct pattern — extend the same shared dependency here for consistency, low risk since the underlying query is already correct), payroll results/inputs/audit routes (verify each explicitly, not assumed correct by analogy).
- **Explicit non-scope:** the legacy unscoped reconciliation route's removal (that's B-1E) — this item is about the *routes that must remain and be secured*, not the one that should simply be deleted.
- **Dependencies:** requires B-1A, B-1B, B-1C.
- **Migration/API/UI impact:** retry/approve/lock/pay routes change path shape (`/payroll/run/{run_id}/retry` → `/{workspace_id}/payroll/runs/{run_id}/retry`), requiring frontend caller updates; response contract for cross-workspace requests changes to non-disclosing `404` (per the approved Stage 10 concealment policy, reused here as the general pattern) rather than returning identical data as today.
- **Acceptance criteria:** every route in this list denies cross-workspace access with `404`; the underlying query for each uses a real `WHERE workspace_id = :wid` predicate on the table being queried directly (not solely via a join, per the Stage 10 design rationale for `execution_trace.workspace_id` — the same reasoning applies here: a direct column is safer against exactly this recurring failure class than a join that can be silently bypassed).
- **Required tests:** cross-workspace-run/reconciliation/timeline-access-denied (Stage 11 rec, now made a permanent regression test rather than a one-off manual proof); lifecycle-actions-denied-for-wrong-workspace.
- **Rollback:** the route path changes are the main risk to rollback — recommend an additive transition (new scoped routes ship first, old routes marked deprecated, removed only after frontend cutover confirmed, per B-1E's phased pattern).
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 2, first item (depends on all of Programme 1).
- **Effort:** L — touches the most security-critical routes in the application.

### B-1E — Route cleanup and admin restriction (`06-007`, `09-002`, `09-007`)

- **Source findings:** `06-007`, `09-002`, `09-007`
- **Severity / release gate:** S1 / must complete before live/production-data use (admin restriction); the legacy-reconciliation removal is a release-gate item (G4) but is independently shippable sooner
- **Scope:** Three distinct sub-items, deliberately kept separate:
  1. **Immediate removal** of the legacy unscoped reconciliation GET/POST pair, after a final check for any undocumented external integration (email/Slack/partner API reference) — Stage 09/11/12 found zero internal callers across three independent investigations; this is the lowest-risk, highest-confidence deletion in the entire backlog.
  2. **Creation and rewiring of secure scoped lifecycle routes** (retry/approve/lock/pay) before retiring the currently-active unscoped versions — sequenced as part of B-1D above, not this item; listed here only to make explicit that the *legacy reconciliation pair* and the *active lifecycle routes* must not be treated identically (one is dead code, the other is load-bearing and requires a redesign+migration, not a deletion).
  3. **Authentication/RBAC protection for `/admin`, `/admin/onboarding`, `/admin/payroll`** — apply B-1A/B-1C to these routes; if they retain genuine operator value (plausible, per Stage 09's own assessment), gate them behind `platform_administrator` or `bureau_administrator` role rather than removing them.
- **Dependencies:** sub-item 1 is independent (can ship immediately); sub-item 3 requires B-1A/B-1C.
- **Migration/API/UI impact:** sub-item 1 removes two routes (no frontend impact, confirmed zero callers); sub-item 3 adds auth middleware to the admin router registration in `main.py`.
- **Acceptance criteria:** legacy reconciliation routes return `404 Not Found` (route no longer registered) or are confirmed removed from the OpenAPI schema; admin dashboards require authentication and the correct role.
- **Required tests:** admin-dashboards-protected (Stage 11 rec); legacy-stats-scoped (covered by B-1D).
- **Rollback:** trivial for sub-item 1 (re-add the route file if a legitimate integration is discovered post-removal — extremely unlikely given the evidence, but the rollback path is simply reverting one commit).
- **Owner/discipline:** backend.
- **Sprint/package:** sub-item 1 — independent quick win, can ship in Programme 0/1 alongside foundation work; sub-item 3 — Programme 2.
- **Effort:** XS (sub-item 1), S (sub-item 3).

### B-1F — Exception sanitization (`07-001`)

- **Source findings:** `07-001`
- **Severity / release gate:** S1 / must complete before live/production-data use (the 10 Group A sites specifically; Group B/C sites are already safe and lower urgency)
- **Scope:** For the 10 confirmed Group A sites (broad `except Exception` wrapping writes, in `workspace.py`): replace `detail=str(e)` with a generic, safe, human-readable message; log the full exception server-side via `_log.error(...)`, per `CLAUDE.md`'s existing standing rule (already documented, now enforced for the third confirmed time in this codebase's history). For the 11 Group B/C sites (narrow `ValueError`/custom exceptions): confirm and preserve the existing developer-authored-message pattern — these do not need the same fix, only confirmation they remain narrow (a lint/review rule preventing a future broadening back to `except Exception` is a reasonable defence-in-depth addition, optional).
- **Explicit non-scope:** does not include building a new error-handling framework — this is a per-site fix using the pattern `CLAUDE.md` already prescribes.
- **Dependencies:** independent of authentication work; can ship in parallel with Programme 1.
- **Migration/API/UI impact:** HTTP response bodies for the 10 Group A sites change from raw exception text to a generic message — frontend error-display code should already handle a generic string (verify, do not assume); no migration impact.
- **Acceptance criteria:** none of the 10 sites returns raw DB/schema/constraint/stack detail under any tested failure condition; server logs contain the full exception for each.
- **Required tests:** representative Group A route tests asserting sanitized response + logged detail (Stage 11 rec).
- **Rollback:** trivial — pure code change, no schema/data impact.
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 3 (independent of the auth foundation, can run in parallel with Programme 1).
- **Effort:** S — 10 sites, mechanical fix per `CLAUDE.md`'s existing prescribed pattern.

### B-1G — Audit/event completeness (`07-002` and security-sensitive actions)

- **Source findings:** `07-002`
- **Severity / release gate:** S2 / post-foundation hardening
- **Scope:** Add `audit_log`/`event_store` entries for: reconciliation create/resolve (currently local-fields-only, per `07-002`); retry completion and run transition (this is naturally delivered by Stage 10's design, §6 below — not duplicated as separate work here); configuration changes, especially statutory-component enable/disable (ties to `03-004`/B-5 — the audit entry is required regardless of which policy option is chosen); platform-administrator access (ties to B-1C).
- **Dependencies:** the retry/run-transition portion is delivered by B-2 (Stage 10 package); the configuration-change portion depends on B-5's policy resolution for exactly what "statutory component disabled" audit entry should contain, but the *mechanism* (a generic audit-log write on configuration change) is not itself blocked by that decision.
- **Migration/API/UI impact:** no schema change (tables already exist); application code gains additional write calls at the identified action points.
- **Acceptance criteria:** reconciliation create/resolve, configuration changes, and admin access each produce a queryable `audit_log` row.
- **Required tests:** audit-entry-present-after-action tests for each named action.
- **Rollback:** trivial — additive writes only.
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 3.
- **Effort:** S.

### B-1H — CSV formula-injection fix (`09-008`)

- **Source findings:** `09-008`
- **Severity / release gate:** S2, gated as part of the release-gate list (G7) given export-data sensitivity
- **Scope:** One reusable export-cell sanitizer applied to every CSV export (bank-upload, PAYE, pension, full-detail) — prefix any string beginning with `=`, `+`, `-`, or `@` with a neutralizing character (e.g. a leading `'` or explicit quoting that spreadsheet applications respect) before writing to the CSV row. Apply at the single shared write point if one exists, or at each of the four export functions if not (recommend consolidating the four export functions' row-writing into one shared helper as part of this fix — a natural pairing with the CSV sanitizer itself, avoiding a fifth near-duplicate implementation).
- **Dependencies:** independent of authentication; can ship in parallel with Programme 1.
- **Migration/API/UI impact:** none — pure output-encoding change, transparent to any consumer that doesn't specifically expect unescaped formula characters (which would itself be a defect in the consumer).
- **Acceptance criteria:** Stage 11's exact synthetic proof (`=1+1` as a name field) no longer reaches the output cell unescaped, verified by an automated test using that same fixture.
- **Required tests:** CSV-export-sanitization test (Stage 11 rec #7, now the acceptance test).
- **Rollback:** trivial.
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 3.
- **Effort:** XS–S.

### B-1I — Security regression suite

- **Source findings:** Stage 11's coverage-gap analysis (zero tenant/security tests exist today)
- **Severity / release gate:** S1 / must exist before the release gate (§4) can be considered satisfied — a fix without a permanent regression test does not close the gate
- **Scope:** One new test module (or a small family of modules) covering, at minimum: unauthenticated access denied (every route family); workspace enumeration correctly scoped; cross-workspace run/reconciliation/timeline access denied; lifecycle actions denied for wrong workspace/role; admin dashboards protected; legacy-executor stats correctly scoped; authorized read-only auditor access succeeds; platform-admin access is explicit/logged; a design-level (not necessarily executable yet) test scaffold for future direct-client-user extensibility; raw-exception sanitization for representative Group A/B routes; export formula-sanitization.
- **Dependencies:** each sub-test depends on its corresponding implementation item (B-1A through B-1H) landing first — this item is delivered incrementally alongside each, not as one big bang at the end.
- **Acceptance criteria:** the full suite (this new module plus the existing 306) remains green; every item in §4's release gate has at least one corresponding permanent test.
- **Owner/discipline:** backend + test authoring.
- **Sprint/package:** distributed across Programmes 1–3, one test increment per implementation increment.
- **Effort:** M in total, but delivered incrementally (each increment is XS–S).

---

## 6. Trace/auditability package specification (Programme 5)

### B-2 — Execution-trace and per-result auditability package

- **Source findings:** `02-002`, `04-002`, `07-005`, `08-003` (visibility half), `09-005` (schema half), Stage 10's full approved design, Stage 12's trace event-code consolidation recommendation.
- **Severity / release gate:** S1 (observability/auditability, not a financial-correctness gap) — the schema/write-side portion is post-foundation hardening (Programme 5); the query-authorization portion is part of the S0 release gate (folded into G3, since `09-005` is one of the routes G3 requires).
- **Scope — exactly as approved in Stage 10, unmodified here:**
  - `execution_trace` schema additions: `workspace_id` (NOT NULL, backfilled), `event_code`, `operation_type`, `invocation_id`, `employee_id`, `actor_id`, `metadata_jsonb`, `error_class`.
  - Retry event model: invocation/preflight events → one terminal event per retried employee → final transition events, sharing one `invocation_id` per retry call.
  - Additive-only event-code taxonomy (Stage 10 §4), retrofitted onto the 9 existing free-text step names via a one-time backfill mapping; Stage 12's consolidation recommendation (one canonical constants module) is folded into this same implementation work, not a separate later cleanup.
  - `payroll_result.statutory_rule_id`/`statutory_version` (nullable, populated from the frozen `rules_context_snapshot` going forward, no backfill of legacy rows).
  - `component_trace_jsonb`'s `outcome` discriminator (`executed`/`skipped_eligibility`/`excluded_by_configuration`) plus one run-level `COMPONENT_EXCLUDED_BY_CONFIGURATION` event per distinct excluded component per run.
  - Timeline API: additive query filters (invocation, operation type, employee, event code, status, time range), deterministic `(created_at, id)` ordering, cursor pagination, a derived retry-invocation-summary endpoint.
  - Trace-write failure containment (unchanged from today's `except Exception: pass` principle) plus a **new** structured server-side log line on trace-write failure — this is the one behavioural addition to the existing failure-containment principle, not a weakening of it.
  - The actual tenant-ownership check on the timeline route is delivered by B-1D, once B-1A–B-1C exist — **this package does not itself implement authentication**, it only makes the schema/query *capable* of enforcing it the moment auth exists (Stage 10's own explicit sequencing note, preserved unchanged here).
- **Explicit non-scope:** does not re-litigate any Stage 10 design decision (resource-concealment policy, event taxonomy, migration sequence) — all of that is inherited verbatim as the canonical specification.
- **Dependencies:** schema/write-side/API portions — independent, can ship in Programme 5 ahead of or parallel with Programme 1; the query-authorization portion — requires B-1A–B-1D.
- **Migration/API/UI impact:** one migration (additive columns on `execution_trace` and `payroll_result`, per Stage 10 §14's exact sequence, including the guarded `ADD COLUMN`/backfill/`SET NOT NULL` steps for `workspace_id`); additive API response fields; frontend UI grouping work per Stage 10 §12 (attempt grouping, preflight failure display, statutory-identity display, excluded-component indicators) — scoped as its own frontend task, sequenced after the backend/API portions ship.
- **Acceptance criteria:** all 12 of Stage 10 §15's acceptance criteria; all 12 of Stage 11's regression scenarios (§16 of that stage) executed as real automated tests rather than manual proofs.
- **Required tests:** the full Stage 10/11 regression scenario set — this is the single largest test-authoring item in the backlog, matching the scale of the feature itself.
- **Rollback:** standard migration downgrade (drop added columns); application rollback reverts to today's zero-retry-trace behaviour, no data loss since all additions are additive/nullable.
- **Owner/discipline:** backend + frontend (UI portion) + migration author.
- **Sprint/package:** Programme 5 for the schema/write-side/API/UI work; the authorization half folds into Programme 2 (B-1D).
- **Effort:** L — this is Stage 10's full design, now being scheduled for implementation.

---

## 7. Background-failure reliability package (Programme 3)

### B-3 — Outer background-task failure handling (`07-003`)

- **Source findings:** `07-003`
- **Severity / release gate:** S1 / post-foundation hardening (Programme 3), independent of authentication
- **Scope:** For the outer (post-snapshot, pre-per-employee-batch) background-task failure path identified in Stage 07: persist a terminal `FAILED` status where the failure occurs before any partial results are safely attributable; populate a safe (non-`str(e)`) `error_message`; create an audit/event/trace signal (naturally delivered by B-2's Group C event model if the failure occurs within that scope, or a dedicated event otherwise); preserve any already-committed per-employee outcomes rather than discarding them; avoid overwriting a more specific terminal state if one was already reached (e.g. don't downgrade a `PARTIAL` run to a generic `FAILED` if per-employee failures already explain the state more precisely); add an explicit fault-injection seam (a dependency-injectable hook or monkeypatch target) so this path becomes testable without editing production source, closing the exact gap Stage 11 documented as blocking; add the permanent regression test Stage 11 specified.
- **Explicit interaction with `05-001`:** the two handlers must not conflict — `05-001`'s remediation already makes *snapshot-creation* failure fail visibly; `07-003` is about failures *after* snapshot creation but *before* per-employee processing completes. The scope boundary between the two is: `05-001` = snapshot phase, `07-003` = orchestration phase between snapshot completion and batch start/completion. Implementation must confirm these are genuinely non-overlapping code regions (a quick verification step at the start of this item, not a new open question) before writing the fix.
- **Dependencies:** independent of Programme 1; can ship in parallel.
- **Migration/API/UI impact:** none beyond the existing `error_message`/`FAILED` status already added by the `04-001`/`05-001` remediation — this reuses that same terminal-state machinery for a different failure trigger point.
- **Acceptance criteria:** a run reaching this failure point ends in `FAILED` with a populated, safe `error_message`, an audit/event/trace row, and no orphaned/half-committed results.
- **Required tests:** the fault-injection test Stage 11 specified as blocked, now unblocked by the new seam.
- **Rollback:** trivial — additive failure handling, no schema change.
- **Owner/discipline:** backend.
- **Sprint/package:** Programme 3.
- **Effort:** M — requires careful boundary verification against `05-001`'s existing handler.

---

## 8. Data-integrity hardening package (Programme 4)

### B-4A — `employee_number` NOT NULL correction (`08-001`)

- **Source findings:** `08-001`
- **Severity / release gate:** S2 / release gate item G8
- **Scope:** A production-data pre-check (count and list any NULL `employee_number` rows in the target environment — **do not assume the local dev ratio of 11/4,673 represents production**, per this stage's explicit constraint); a remediation policy for any found NULL rows (assign a corrected value, or exclude from payroll processing until corrected — a decision for whoever executes the migration, informed by what the pre-check finds); a corrective migration using a **precise guard** (e.g. a pre-check `DO $$` block that raises a clear, actionable error if NULL rows remain, never `EXCEPTION WHEN others THEN NULL`); verification that the column is genuinely `NOT NULL` post-migration (a direct `\d employee` check, not merely "the migration ran without error"); a correction to `c9d0e1f2a3b4`'s stale docstring (which currently claims a guarantee it doesn't provide); a migration upgrade/downgrade test; a schema regression test asserting the constraint holds.
- **Dependencies:** independent of Programme 1.
- **Migration/API/UI impact:** one migration; if any production NULL rows are found, employee-record UI/API may need a one-time data-correction workflow (scope depends on the pre-check's findings — not fully specifiable until that check runs).
- **Acceptance criteria:** `employee.employee_number` is `NOT NULL` in the schema, verified directly, in every environment including production.
- **Required tests:** migration upgrade/downgrade smoke test (Stage 11 rec #8, applied here specifically); a schema assertion test (Stage 11 rec #2).
- **Rollback:** the migration's downgrade path drops the constraint (standard); any data-correction workflow's rollback depends on what that workflow turns out to be.
- **Owner/discipline:** backend + migration author + whoever owns the production-data pre-check.
- **Sprint/package:** Programme 4.
- **Effort:** S–M depending on pre-check findings.

### B-4B — `payroll_run` immutability window (`08-002`) — Decision D2 RESOLVED

- **Source findings:** `08-002`
- **Severity / release gate:** S2 / post-foundation hardening
- **Decision (approved at Stage 13 close):** financially relevant run totals and period fields become DB-immutable at **`APPROVED`**, aligned with the existing approved-run/result invariant already documented in `CLAUDE.md`. `LOCKED` was rejected as one lifecycle stage too late — permitting run totals/period identity to change between `APPROVED` and `LOCKED` would make the approved result set and its own run header inconsistent.
- **Scope:** DB-level (trigger) protection for the exact columns `payroll_run.total_gross_pay`, `total_deduction`, `total_net_pay`, `total_tax`, `period_start`, `period_end`, applied from `APPROVED` onward. Allowed system-owned transitions (the retry-driven totals recomputation that legitimately occurs while still `PARTIAL`) are explicitly excluded from the new trigger's guard, mirroring the existing `payroll_result` trigger's `PARTIAL`-exclusion pattern Stage 08 already confirmed as the correct precedent. Lock, reconciliation, and payment must consume the `APPROVED` values as read-only facts, never rewrite them — verify each of those three lifecycle stages' code paths only reads these columns from this point forward, as part of implementation.
- **Dependencies:** independent of Programme 1; benefits from B-4A's precise-guard discipline as a direct pattern to follow.
- **Migration/API/UI impact:** one migration adding the trigger; no API/UI impact (this is a defence-in-depth DB-level protection — Stage 08 already confirmed no *application* code path currently attempts this mutation, so no functional behaviour changes for any legitimate caller).
- **Acceptance criteria:** a direct SQL `UPDATE` attempt against any of the six protected columns on an `APPROVED`, `LOCKED`, or `PAID` run is rejected by the trigger; the same `UPDATE` against a `PARTIAL` run (retry's legitimate recomputation) succeeds; migration downgrade cleanly removes the trigger.
- **Required tests:** direct-SQL immutability regression tests at `APPROVED`, `LOCKED`, and `PAID` (Stage 11 rec #3, applied here, now with all three post-approval states explicitly covered per D2's review requirement).
- **Rollback:** standard trigger-drop downgrade.
- **Owner/discipline:** backend + migration author.
- **Sprint/package:** Programme 4.
- **Effort:** S.

### B-4C — Snapshot immutability harmonisation (`05-004`)

- **Source findings:** `05-004`
- **Severity / release gate:** S2 / post-foundation hardening, lowest urgency within Programme 4
- **Scope:** Audit and, where a genuine gap exists, add DB-level immutability triggers for component-metadata snapshots, client-component-metadata snapshots, employee-contract snapshots, and any uncovered `payroll_result` fields — extending the same trigger pattern already proven on `payroll_run.rules_context_snapshot` and `payroll_result.calculations_snapshot_json`. Any Stage 10-added trace/identity fields (`statutory_rule_id`/`statutory_version`) should be confirmed covered by the *existing* `payroll_result` mutation-prevention triggers (Stage 10 §7 already noted these fall under existing generic row-level guards automatically — this item's job is to verify that holds true once the columns actually exist, not to design new protection).
- **Dependencies:** independent of Programme 1; the `statutory_rule_id`/`statutory_version` verification sub-item depends on B-2 (Stage 10 package) shipping first.
- **Migration/API/UI impact:** additive triggers only, no application code change, per Stage 05's own finding that no current update path mutates these tables.
- **Acceptance criteria:** every snapshot table has DB-level protection consistent with the two tables that already do; no existing protection is weakened.
- **Required tests:** immutability regression test per snapshot table.
- **Rollback:** standard trigger-drop downgrade.
- **Owner/discipline:** backend + migration author.
- **Sprint/package:** Programme 4, lower priority within it.
- **Effort:** M — multiple tables, careful to avoid over-triggering a table that has a legitimate future write path.

### B-4D — Pay-cycle definition configurability (`06-002`)

- **Source findings:** `06-002`
- **Severity / release gate:** S2 / post-foundation hardening
- **Scope:** Expose `pay_cycle.definition_json`'s current value in a read API; allow validated post-onboarding updates where policy permits (a product-scope question about whether pay-cycle definition should ever change post-onboarding — if the answer is "no, it's immutable by design," this item becomes "expose read-only value + document why," a much smaller scope; this stage does not assume either answer); make precedence between this JSON field and any dedicated pay-cycle columns explicit in both code comments and API documentation; add UI support for whichever scope is chosen; preserve historical run snapshots unaffected (this field's mutability, if allowed, must not retroactively change what a past run's snapshot recorded); add consistency tests.
- **Dependencies:** independent of Programme 1.
- **Migration/API/UI impact:** depends on scope decision above — read-only exposure is API+UI only, no migration; allowing edits would need validation logic and possibly a migration if new dedicated columns are preferred over continued JSON storage.
- **Acceptance criteria:** the current value is at minimum visible via API/UI post-onboarding (the confirmed minimum fix); if edits are allowed, changes are validated and do not corrupt historical run snapshots.
- **Required tests:** consistency test between `definition_json` and any dedicated columns.
- **Rollback:** read-only exposure is trivially reversible (UI/API change only); edit-support rollback depends on final scope.
- **Owner/discipline:** backend + frontend + product input on the edit-vs-read-only scope.
- **Sprint/package:** Programme 4, or Programme 7 if treated as primarily a frontend item — recommend Programme 4 since the backend exposure is the higher-value minimum fix.
- **Effort:** S (read-only exposure) to M (if edits are in scope).

---

## 9. Statutory-policy decision pack (Programme 6) — Decision D1 (`03-004`) — RESOLVED

**Decision (approved at Stage 13 close): forbid disablement of mandatory statutory components entirely.** Re-enable the currently-commented-out `D-ARCH-2` guard in `patch_component_override`.

**Implementation requirements:**
- Define mandatory statutory component codes/classes by supported jurisdiction (today: PAYE, pension, NHF, health insurance, development levy for NG).
- Reject attempts to set them inactive through every supported path — API, UI, onboarding, override, or any other direct configuration route.
- Retain and rely on eligibility/applicability rules (already a first-class mechanism in this codebase's rule-evaluation engine) for legitimate employee-level exemptions or zero liability — e.g. an expatriate employee genuinely exempt from a specific Nigerian statutory scheme is modeled as an eligibility condition evaluating false, not as a workspace-level disable switch.
- Distinguish "not applicable under the statutory rule" (an eligibility outcome, `skipped_eligibility` per Stage 10's `component_trace_jsonb` discriminator) from "disabled by configuration" (now rejected outright) — these remain two different, both-visible states, not conflated.
- Audit rejected configuration attempts where appropriate — an operator's *attempt* to disable a mandatory component is itself worth logging, even though the attempt is rejected.
- Preserve Stage 10's omitted-component visibility design unchanged for non-mandatory components and for legacy evidence (runs that predate this guard's re-enablement).
- Add server-side, DB/configuration, and UI regression tests confirming the guard rejects every disablement path.

**Rationale (approved):** mandatory legal obligations should be controlled by statutory applicability logic, not by a workspace-level off switch. A privileged-disable option (the rejected option (b)) would create unnecessary compliance risk and make configuration authority responsible for overriding law. If a future jurisdiction has a genuine exemption, it is modeled explicitly in the statutory rule/eligibility layer rather than permitted as blanket disablement.

**Explicit note, preserved unchanged:** this item is kept separate from `08-003`'s visibility work (B-2) — the trace/visibility mechanism (§6/§8 of Stage 10's design) ships unchanged by this decision and applies regardless.

---

## 10. Legacy-executor transition plan (Programme 6)

### B-6 — Legacy executor migration-and-removal programme (`01-004`)

This item is **already decided** (Stage 12 close) — this section converts that decision into the phased backlog form the CONTEXT.md requires, without re-opening the decision itself.

1. Correct the stale "old CLI callers" comment in `executor.py` — **independent quick win, ship immediately, no dependency on anything else.**
2. Add stable fallback telemetry with workspace/run/country context — naturally delivered by B-2's event-code taxonomy (the fallback gets a real `event_code` instead of the current string-matched `'legacy_executor_fallback'` step name); sequence alongside B-2, not before it, since duplicating a temporary telemetry mechanism ahead of B-2 would be wasted work.
3. Inventory production/environment dependency — **requires production-data access this audit programme did not have; this is an operational task for whoever has that access, not something Stage 13 can execute.** Explicitly: do not use the Stage 11 dev-DB 9.3% figure as this inventory's answer.
4. Classify each occurrence (missing seed/config, deliberately disabled metadata, or legitimate historical dependency) — depends on step 3's actual data.
5. Migrate/repair active workspace metadata — depends on step 4's classification.
6. Observe zero fallback usage for new runs over an agreed window — **Decision D3 (resolved, see below): two consecutive full production payroll cycles with zero firings, counted only once every active workspace's configuration is confirmed migrated and telemetry is live and reliable; any firing during the window resets the count.**
7. Hard-fail new runs on empty metadata with an actionable configuration error — depends on step 6's observation window passing cleanly.
8. Remove the default fallback path — depends on step 7 being live and stable.
9. Isolate replay-only compatibility, only if a genuine historical-replay requirement is confirmed during step 3/4 — not built speculatively.

**Dependencies:** step 1 — independent; step 2 — bundle with B-2; steps 3–9 — sequential, each gated on the prior step's findings, and steps 3 onward require production access/operational coordination outside this repository's normal audit/implementation cadence.

**Acceptance criteria (Stage 12's 7, restated here as this backlog item's criteria):** comment corrected; stable event code with context; production inventory completed before any behaviour change ships; every active workspace has non-empty effective component metadata post-migration; automated tests cover correctly-configured/empty-metadata/replay/telemetry cases; the cutover has a rollback plan; no removal claim is made from dev-DB percentages alone.

**Owner/discipline:** backend + whoever has production environment access for steps 3–5.
**Sprint/package:** Programme 6.
**Effort:** step 1 — XS; steps 2 — bundled with B-2 (M); steps 3–9 — L overall, but mostly operational/coordination effort rather than code complexity.

---

## 11. Frontend/API repair package (Programme 7)

### B-7A — `FAILED` run support, including the `PayrollRunStatus` type duplication (`06-001`, `06-004`, Stage 12 finding)

- **Source findings:** `06-001`, `06-004`, Stage 12's `PayrollRunStatus` duplication/drift finding
- **Severity / release gate:** S2 / post-foundation hardening (this is a UI-completeness gap, not a security or financial-correctness issue — `FAILED` runs are already correctly computed and stored by the backend, per the `04-001`/`05-001` remediation; the gap is purely that the frontend cannot display them correctly)
- **Scope:** Consolidate to **one** canonical `PayrollRunStatus` frontend type (retain `types/payroll.ts`'s location, since it types the real API field); add the missing `'FAILED'` value; fix `design-system/components/Status.tsx`'s incorrect `'PENDING'` literal (either by removing its duplicate declaration in favor of importing the canonical one, or correcting it to `'DRAFT'` if a separate declaration is retained for design-system package-boundary reasons); add `FAILED`-branch handling to `StatusBadge` styling and `ActionPanel` (currently falls through to `null` for `FAILED` runs, per `06-004`); add error-message display surfacing `payroll_run.error_message`; add API contract tests (or a generated/shared-contract check) so this specific class of drift cannot silently recur.
- **Dependencies:** none — purely frontend + already-existing backend fields.
- **Migration/API/UI impact:** frontend-only change; no backend/migration impact (the backend fields already exist from the `04-001`/`05-001` remediation).
- **Acceptance criteria:** a `FAILED` run displays a distinct status badge, a visible `error_message`, and appropriate recovery guidance (e.g. "this run failed before calculation began — contact support" or similar, matching whatever UX the team decides, not specified further by this audit); TypeScript's `PayrollRunStatus` type cannot be satisfied by `'PENDING'` anywhere in the codebase (i.e., that literal is fully removed).
- **Required tests:** frontend status/role/route test (Stage 11 rec #7, Stage 9's own list); a type-level check (e.g. a small test asserting the frontend type's values exactly match the backend enum's values, preventing silent future drift).
- **Rollback:** trivial — frontend-only.
- **Owner/discipline:** frontend.
- **Sprint/package:** Programme 7, first item (highest-value frontend fix, directly closes a already-confirmed defect, not merely polish).
- **Effort:** S–M.

### B-7B — Retry-strategy UI correction (`06-003`)

- **Source findings:** `06-003`
- **Severity / release gate:** S3 / cleanup
- **Scope:** Remove `FULL_RUN` as a selectable frontend option, since the backend's CHECK constraint permanently disables it (`PER_EMPLOYEE` is the only legal value); prevent future drift by driving the option list from a single source (ideally the backend's own allowed-values list via an API-exposed enum, rather than a second hardcoded frontend list) rather than just deleting the dead option today and leaving the same drift risk for any future value.
- **Dependencies:** none.
- **Migration/API/UI impact:** frontend-only.
- **Acceptance criteria:** the UI offers only `PER_EMPLOYEE`; a frontend test asserts the option list matches the backend's allowed values.
- **Owner/discipline:** frontend.
- **Sprint/package:** Programme 7.
- **Effort:** XS.

### B-7C — Timesheet audit UI (`06-006`)

- **Source findings:** `06-006`
- **Severity / release gate:** S2 / post-foundation hardening (this is a missing-feature gap for a core bureau-operator workflow, per Stage 06's resolved decision, not a defect in existing behaviour)
- **Scope:** Expose the existing, already-correct backend `GET /workspaces/{workspace_id}/timesheet/audit/{employee_id}` route in an operator-facing UI workflow (per Stage 06's resolution: this belongs alongside the already-wired timesheet upload, payroll-result trace, reconciliation, and audit-history surfaces). Access control under the new RBAC model (B-1C) — likely `payroll_operator` and above.
- **Dependencies:** benefits from B-1C existing first so the access-control question has a real role model to attach to, but the UI work itself can begin in parallel.
- **Migration/API/UI impact:** frontend-only (new page/panel); backend route already exists and is correctly scoped (confirmed by Stage 09, not itself part of the decorative-scoping problem).
- **Acceptance criteria:** an operator can view timesheet-interpretation-into-payroll-input audit data for a given employee through the UI, gated by the appropriate role once RBAC exists.
- **Owner/discipline:** frontend + UX input (this was flagged by `ux-designer` review criteria in the project's own workflow, per `CLAUDE.md`'s standing skill-usage rules — recommend invoking that review when this item is actually scoped for implementation, not during this audit stage).
- **Sprint/package:** Programme 7.
- **Effort:** M.

### B-7D — Salary-definition edit UX (`06-005`)

- **Source findings:** `06-005`
- **Severity / release gate:** optional polish, explicitly not required — per the CONTEXT.md's own instruction, do not elevate above confirmed defects.
- **Scope:** Not specified further here; recommend Stage 13's consolidated backlog carry this as a low-priority backlog entry for opportunistic inclusion in a Programme 7 sprint if capacity allows, not as a scheduled, gated item.
- **Sprint/package:** Programme 7, lowest priority within it, or deferred indefinitely.
- **Effort:** unspecified — not scoped in detail since it is optional.

---

## 12. Simplification package (Programme 8)

Reusing Stage 12's own dependency classification verbatim — no re-derivation:

| Item | Classification | Effort |
|---|---|---|
| Rename/document `backend/infra/db/repositories/` | independent quick win | XS |
| Remove `employee_contract_snapshot.components_jsonb` (migration) | independent quick win | S |
| Extract shared statutory-rate-extraction helper (`05-005`) | independent quick win | S |
| Remove `paye.py` stray `print()` | independent quick win | XS |
| Rename/manual-label `backend/scripts/test_*.py` (6 files) | independent quick win | XS |
| Remove legacy unscoped reconciliation pair | independent quick win (= B-1E sub-item 1, not duplicated) | XS |
| Correct stale comments/docstrings (`executor.py`, `c9d0e1f2a3b4`) | bundled with B-6 step 1 and B-4A respectively | XS each |
| Centralize trace event-code constants | bundled with B-2 | (included in B-2's effort) |
| Optional shared error-to-HTTP helper | bundled with B-1F | (included in B-1F's effort) |

**Intentional retentions, preserved unchanged, no action:** `payroll_result.salary_inputs_snapshot` (`05-003`); the differing retry/original-run context-construction code paths (different lifecycle semantics, correctly not merged); the operational load/simulation/backfill scripts (`load_*.py`, `simulate_payroll.py`, `backfill_rule_set_snapshots.py`); `docs/wrapper-command/` (reference-only history, decision 01-013). `03-004`'s underlying mechanism is now implemented per Decision D1 (forbid disablement) rather than retained pending a decision — see §9.

---

## 13. Test/CI acceptance matrix

| Test | Embedded in | Stage 11 rec # |
|---|---|---|
| Tenant-ownership tests (every workspace-scoped route) | B-1D, B-1I | #1 |
| `employee_number` NOT NULL migration test | B-4A | #2 |
| `payroll_run` post-approval immutability direct-SQL test | B-4B | #3 |
| Statutory-component-exclusion trace test | B-2 | #4 |
| Background-task fault-injection test | B-3 | #5 |
| Retry trace / statutory-identity tests | B-2 | #6 |
| Export sanitization test | B-1H | #7 |
| Migration upgrade/downgrade smoke test (generic, reusable) | B-4A initially, then a standing CI check | #8 |

**Additional programme-level checks required beyond the 8 above** (per this stage's own instruction): a full regression run of the complete current suite (306 tests) as a standing gate on every subsequent PR in this remediation programme — not a one-off, but the existing pre-push hook (confirmed operational per Stage 11/12's own commit logs in this session) already provides this mechanically; frontend status/role/route tests (B-7A, B-1C); the security regression suite (B-1I) as its own growing module rather than scattered ad hoc tests.

**Explicit constraint honored:** no item above is a generic "add tests later" task — every test is embedded in the specific backlog item whose acceptance criteria it verifies.

---

## 14. Dependency graph (textual)

```
B-1A (auth foundation)
 └─▶ B-1B (membership/tenancy)
      └─▶ B-1C (RBAC)
           └─▶ B-1D (mandatory ownership checks) ──▶ [G3 release gate]
                └─▶ B-1E sub-item 3 (admin restriction)
                └─▶ B-2's authorization half (tenant-safe timeline)

B-1E sub-item 1 (remove legacy reconcile routes) — independent, ships anytime
B-1F (exception sanitization) — independent
B-1G (audit completeness) — depends loosely on B-2 (retry/transition events) and B-5 (config-change semantics)
B-1H (CSV sanitization) — independent
B-1I (security test suite) — incremental, tied to each B-1x item landing

B-2's schema/write-side/API half (trace package) — independent, can ship in Programme 5 ahead of/parallel to Programme 1
B-2's UI half — depends on the schema/API half

B-3 (background-failure reliability) — independent, but must be scoped against B-2/05-001's existing handlers to avoid overlap

B-4A (employee_number) — independent
B-4B (run immutability) — independent, benefits from B-4A's guard-pattern precedent
B-4C (snapshot immutability) — independent, one sub-item depends on B-2 shipping first
B-4D (pay-cycle config) — independent

B-5 (statutory policy decision) — independent of code, but gates B-1G's config-change-audit sub-item and the eventual guard implementation once decided

B-6 (legacy executor) — step 1 independent; step 2 depends on B-2; steps 3-9 sequential, gated on production-access/operational work outside this repo

B-7A (FAILED support) — independent
B-7B (retry-strategy UI) — independent
B-7C (timesheet audit UI) — benefits from B-1C but not hard-blocked
B-7D — optional, unscheduled

Programme 8 (simplification) — each item independent per its own row in §12
```

---

## 15. Recommended sprint sequence

The CONTEXT.md's suggested Programme 0–8 order is **adopted as-is**, with one clarification and no substantive deviation:

- **Programme 0 (keep `04-001`/`05-001` green):** ongoing, not a scheduled sprint — enforced by the existing pre-push hook and full-suite regression requirement on every subsequent change in this programme.
- **Programme 1 (auth/tenancy/RBAC foundation):** B-1A → B-1B → B-1C, strictly sequential.
- **Programme 2 (mandatory ownership + security closure):** B-1D, B-1E sub-item 3, B-1D's authorization contribution to B-2's timeline route.
- **Programme 3 (error/export/audit hardening):** B-1F, B-1G, B-1H, B-3 — **can run in parallel with Programme 1**, since none of these four items depends on authentication existing. This is the one point worth calling out explicitly: **Programmes 1 and 3 are independent and should be scheduled concurrently if team capacity allows**, rather than strictly serially, since Programme 3's items are release-gate-adjacent (G6, G7) and there is no reason to delay them behind the (larger, riskier) authentication work.
- **Programme 4 (data-integrity corrections):** B-4A, B-4B, B-4C, B-4D — independent of Programmes 1–3, can also run concurrently.
- **Programme 5 (execution trace):** B-2's schema/write-side/API portion — independent, can start as early as team capacity allows; its authorization-dependent portion folds into Programme 2's timeline of B-1D.
- **Programme 6 (statutory policy + legacy-executor transition):** Decision D1 is resolved (forbid disablement) — implement B-5 directly against that decision, no further policy gate; B-6 steps 1 (immediate) and 2 (bundle with B-2), then steps 3-9 (operational, gated on production access) whenever that access is available, observing Decision D3's two-cycle threshold — not necessarily blocking the rest of the programme's completion.
- **Programme 7 (frontend completeness):** B-7A first (highest confirmed-defect value), then B-7B, B-7C, B-7D — can start once the relevant backend contracts exist (B-2 for trace-related UI, B-1C for role-aware UI), independent of Programmes 1–2's completion for the non-role-dependent parts.
- **Programme 8 (simplification):** distributed opportunistically — most items are XS/S and can be picked up alongside whichever programme happens to be touching the adjacent code, rather than scheduled as a dedicated late-stage sprint.

---

## 16. Migration register

| Migration | Item | Type |
|---|---|---|
| `execution_trace` schema additions | B-2 | additive columns + backfill + `SET NOT NULL` on `workspace_id` |
| `payroll_result.statutory_rule_id`/`statutory_version` | B-2 | additive, nullable, no backfill |
| `employee_number` corrective migration | B-4A | precise-guarded `SET NOT NULL`, replaces the swallow-all pattern |
| `payroll_run` immutability trigger | B-4B | additive trigger |
| Snapshot immutability triggers (multiple tables) | B-4C | additive triggers |
| `employee_contract_snapshot.components_jsonb` removal | Programme 8 | destructive (column drop), guarded, zero-reader-confirmed |
| Auth/membership/RBAC tables | B-1A, B-1B, B-1C | new tables, additive |
| Re-enabled `D-ARCH-2` guard in `patch_component_override` | B-5 | code-only change per Decision D1 (forbid disablement) — no new configuration table required |

Every migration above must follow `CLAUDE.md`'s standing conventions: 12-hex revision ID, duplicate-ID check before writing, matching downgrade, `DO $$ ... EXCEPTION WHEN duplicate_column THEN NULL` guard for ADD COLUMN, precise (never swallow-all) guards for destructive steps, `jsonb_typeof()` cast where the column type is `json` not `jsonb`.

---

## 17. API/UI impact register

| Change | Backend routes affected | Frontend impact |
|---|---|---|
| Auth requirement on every route | all | new login/session flow, every API call gains auth header/cookie |
| Retry/approve/lock/pay path change | 4 routes gain `{workspace_id}` in path | frontend API client callers updated |
| Reconciliation/timeline routes | query now actually uses `workspace_id` | cross-workspace requests now `404` instead of returning data — no impact on correctly-scoped legitimate frontend usage |
| Legacy-executor-stats | becomes genuinely filtered | any legitimate consumer must supply a real, authorized `workspace_id` |
| Legacy reconciliation route removal | 2 routes removed | none (zero confirmed callers) |
| Admin dashboards | gain auth requirement | operator must log in to reach them |
| CSV exports | output encoding change only | transparent to legitimate consumers |
| Exception responses (10 sites) | response body text changes | frontend error display should already handle a generic string — verify, don't assume |
| Trace/timeline API | additive fields + filters | new UI grouping/display work (B-2's UI half) |
| `PayrollRunStatus` type | n/a (frontend-only) | one canonical type, `FAILED` added |
| Retry-strategy option list | n/a (frontend-only) | dead option removed |
| Timesheet audit UI | n/a (route already exists) | new UI surface |
| Pay-cycle definition | new/changed read (and possibly write) API | new UI surface, scope depends on Decision on edit-vs-read-only |

---

## 18. Rollback and operational-readiness register

Every backlog item above states its own rollback path inline (§5–§11); the cross-cutting operational-readiness points are:

- **Authentication rollout (B-1A–B-1D):** recommend a feature-flagged or staged cutover rather than a single big-bang deploy, given the scale of route changes involved — this is an implementation-time decision, not specified further here, but the *option* to stage it should be preserved architecturally (e.g. auth dependency added as a no-op-by-default flag during development, flipped to enforcing before the release gate is declared satisfied).
- **Legacy-executor cutover (B-6):** explicitly has its own rollback plan requirement baked into its acceptance criteria (step 6's observation window, step 8's "remove only after verification") — this is the one item in the backlog where "rollback" really means "don't proceed to the next step until the prior step's evidence is in," not a post-hoc revert.
- **Migration rollbacks:** every migration in §16 has a downgrade path per `CLAUDE.md`'s standing convention; none of the proposed migrations are destructive except the one confirmed-safe column drop (`employee_contract_snapshot.components_jsonb`), which has zero readers confirmed across three independent stages (03/05/12).
- **No item in this backlog requires a data-loss-risking rollback** — every schema change is additive except the one confirmed-dead column, and every behavioural change (auth enforcement, route path changes, exception sanitization) is reversible by reverting application code without needing a data migration to undo.

---

## 19. Deferred/retained/rejected register

| Item | Disposition |
|---|---|
| `04-001` | remediated, closed — do not reopen without contradictory evidence |
| `05-001` | remediated, closed — do not reopen without contradictory evidence |
| `04-004` | rejected, no action required, not reclassified as open |
| `05-003` (`salary_inputs_snapshot`) | retained intentionally — stated future audit-surface purpose |
| Retry/original-run context construction duplication | retained intentionally — different lifecycle semantics, correctly not consolidated |
| Operational load/simulation/backfill scripts | retained intentionally — legitimate ad hoc tooling |
| `docs/wrapper-command/` | retained as reference-only history, non-authoritative (decision 01-013) |
| `03-004`'s underlying mechanism | **resolved** — Decision D1: forbid disablement entirely, `D-ARCH-2` guard re-enabled (B-5) |
| `06-005` (salary-definition edit UX) | deferred, optional polish, not elevated above confirmed defects |
| `02-009` (`export_payroll_register_csv` shape mismatch) | deferred — zero production callers, low priority, not part of any release gate |

---

## 20. Residual-risk statement

Even after every item in this backlog ships, the following residual risks remain and should be named explicitly rather than implied as "fully solved":

- **Authentication mechanism choice is not specified by this audit programme** — the specific provider/protocol (e.g. session cookies vs. JWT vs. a managed identity service) is an implementation decision for whoever builds B-1A, not adjudicated here. Different choices carry different residual risks (token theft/replay, session fixation, etc.) that a future security review should assess once the mechanism is chosen.
- **Production-environment inventory (B-6 step 3, and implicitly relevant to B-4A's pre-check) has not been performed by this audit programme** — every dev-DB figure cited throughout Stages 01–13 (the 9.3% legacy-fallback rate, the 11/4,673 nullable-employee-number ratio) is explicitly not confirmed representative of production. This is a genuine, named gap in this audit's own knowledge, not a risk this backlog can close on its own.
- **Separation-of-duties enforcement (Decision D4: soft separation with flagging) is a business-process choice made for Sandy's current small-team reality** — if the team grows or internal-control requirements tighten, the flagging-only approach may need to become hard separation; the role model was deliberately built to allow that upgrade without redesign, but the upgrade itself is not implemented now and remains a future decision point, not a residual defect.
- **The statutory-component policy decision (D1: forbid disablement entirely) assumes no genuine, currently-unknown-to-this-audit business need for controlled disablement exists in Sandy's actual client base.** If such a need surfaces later (e.g. a genuinely exempt employee category not well-modeled by the existing eligibility-rule mechanism), the correct response is to extend the eligibility/statutory-rule layer to model that case explicitly, not to reopen the disablement switch — this is stated so that a future request to "just let us disable it for this one client" is recognized as a request to revisit D1, not a small configuration tweak.
- **This audit programme is a point-in-time review** — new code written during the implementation of this very backlog could reintroduce any of the defect classes found here (e.g. a new route added without the shared ownership-check dependency, a new `except Exception: str(e)` site). The permanent regression tests (B-1I, and each item's own acceptance tests) are the primary defence against this, but they only cover what this audit found, not future code by construction.

---

## 21. Programme completion criteria

The consolidated remediation programme (all of Programmes 1–8) is complete only when:

- Every item in §4's S0/S1 release gate is implemented, tested, and green.
- The full existing test suite (306 tests) plus every new permanent test added by this programme remains green on every merge (enforced by the existing pre-push hook / CI workflow).
- `03-004` (Decision D1, resolved: forbid disablement entirely) is implemented in B-5 exactly as specified in §9 — the `D-ARCH-2` guard re-enabled, mandatory component codes/classes enumerated, rejection applied across every configuration path, eligibility-rule distinction preserved.
- `08-002`'s immutability trigger (Decision D2, resolved: `APPROVED`) is implemented in B-4B exactly as specified — all six protected columns, `PARTIAL`-exclusion preserved, tested at `APPROVED`/`LOCKED`/`PAID`.
- The legacy-executor transition (Decision D3, resolved: two consecutive clean production payroll cycles) has real production evidence behind B-6's steps 3–9, not dev-DB extrapolation — the observation window has actually run and passed before step 7's hard-fail cutover ships.
- Separation-of-duties (Decision D4, resolved: soft separation with flagging) is implemented in B-1C exactly as specified — `same_actor_approval` audit field, UI warning, filterable reporting, and an architecture that permits a future hard-separation upgrade without redesign.
- No item from §19's deferred/retained/rejected register has been silently implemented or silently dropped without an explicit decision to do so.
- The residual-risk statement (§20) has been reviewed and, where any residual risk is judged unacceptable, converted into a new backlog item rather than left implicit.

---

## Decision handling — all four decisions RESOLVED at Stage 13 close (2026-07-13)

### D1 — `03-004`: statutory-component disablement policy — RESOLVED

**Decision: forbid disablement of mandatory statutory components entirely.** Full implementation requirements and rationale in §9. Legitimate exemptions are modeled through statutory applicability/eligibility rules, never through a configuration disable switch.

### D2 — `08-002`: exact lifecycle point for `payroll_run` DB immutability — RESOLVED

**Decision: financially relevant run totals and period fields become DB-immutable at `APPROVED`**, aligned with the existing approved-run/result invariant already documented in `CLAUDE.md`. Exact protected columns, permitted system-owned transitions, and the lock/reconciliation/payment interaction are specified in B-4B (§8, updated below). `LOCKED` was rejected as one lifecycle stage too late — it would allow the approved result set and its run header to become inconsistent between `APPROVED` and `LOCKED`.

### D3 — Legacy-executor observation-window/cutover evidence threshold — RESOLVED

**Decision: require zero new-run fallback firings across two consecutive full production payroll cycles after configuration migration is complete.** The observation window starts only once every active workspace has been inventoried, missing/invalid metadata has been repaired, and fallback telemetry is live and reliable. Any fallback firing during the window resets the two-cycle count and requires investigation/classification before the window restarts. Dev-database percentages (Stage 11's 9.3% figure) must never be used as cutover evidence — this was already stated in B-6's acceptance criteria and is reaffirmed, not altered, by this decision.

### D4 — Separation of duties between payroll operator and approver — RESOLVED

**Decision: soft separation with explicit audit flagging.** A user may hold both operator and approver roles. Same-person approval of a run they created or last retried is permitted but must be visibly flagged: a distinct audit/event record records creator/retrier, approver, timestamps, and a `same_actor_approval` indicator; the UI displays the warning before confirmation and surfaces it in the run's audit history; reporting must allow these approvals to be filtered/reviewed. The role model (B-1C) must permit a later upgrade to hard separation without redesign — this decision does not foreclose that future option, it only avoids implementing it now given Sandy's small-team operational reality.

---

## Evidence references

This document synthesizes, without re-deriving, the findings and evidence of:
- `docs/audit-program/01-system-inventory/` through `12-code-simplification/`, all `findings.md` and `evidence/` directories.
- `docs/audit-program/remediation/04-001-05-001/summary.md` and `verification.md`.
- `docs/audit-program/_core/human-decisions.md` (full decision history).
- `docs/audit-program/audit-state.md` (stage-by-stage handoff summaries).

No new evidence-gathering (grep, `psql`, live execution) was performed in Stage 13 — every cited fact traces to a specific prior-stage finding ID, per this document's own crosswalk (§2).

---

## Stage 13 close — final review and closure summary, and audit-programme closure

No new investigation or code/migration/test/data change occurred during close review, per this stage's own constraints. All four decisions (D1–D4) presented during the initial backlog were **approved exactly as recommended**, with no revision to their content — only their status changed, from "recommended, pending confirmation" to "approved, final." Every backlog item that referenced a pending decision (`B-5`/§9 for D1, `B-4B` for D2, `B-6` for D3, `B-1C` for D4) has been updated in place to reflect the approved decision as implementation-ready specification, not a restated recommendation.

Review requirements verified at closure:

1. Every Stage 01–12 finding retains exactly one canonical disposition in §2's crosswalk — none was left with two conflicting dispositions.
2. Overlapping findings (`08-003` split across B-2/B-5; `09-005` split across B-1D/B-2; `06-007`/`09-002` merged into one item, B-1E) retain all source references without duplicate backlog items, unchanged from the initial submission.
3. D1–D4 are now reflected consistently across the backlog items, dependency graph (§14 — unchanged, since none of the four decisions altered any dependency relationship, only resolved what was previously a branch point), release gates (§4 — unaffected, since none of D1–D4 are S0/S1 release-gate items), tests (each item's acceptance criteria and required-tests rows updated in place), the residual-risk statement (§20, updated to reflect resolved-but-still-worth-naming residual considerations rather than open questions), and programme completion criteria (§21, updated to require *implementation matching the approved decision*, not confirmation of the decision itself).
4. D1 explicitly preserves legitimate statutory eligibility/exemption modelling via the existing eligibility-rule mechanism — confirmed unchanged in §9 and the residual-risk statement.
5. D2 protects the exact six named run-level financial/period fields at `APPROVED`, not a vaguer "totals" description — confirmed in B-4B.
6. D3 starts only after production configuration migration and reliable telemetry are confirmed live — confirmed in B-6 and the resolved decision text, with the reset-on-firing rule preserved.
7. D4 creates an explicit, queryable audit signal (`same_actor_approval`) rather than a silent same-person approval — confirmed in B-1C.
8. Every S0/S1 item retains its implementation scope, tests, rollback, and release gate from the initial submission — none were weakened or removed during close review.
9. All eight Stage 11 permanent-test recommendations remain embedded in their related items (§13, unchanged).
10. No implementation work or data change occurred in Stage 13, at either the initial submission or this close review — confirmed by `git status` showing only `docs/audit-program/` changes throughout.

### The 13-stage audit programme is now complete

Stages 01 through 13 are all `complete`. The programme's net position: the payroll calculation engine is sound and well-tested; the platform's readiness for live/production data is gated entirely on the security foundation (Programme 1) and its direct dependents (Programme 2), not on any financial-correctness defect; a fully sequenced, dependency-aware, test-embedded remediation backlog now exists covering every confirmed finding from Stages 01–12; and all four decisions this backlog surfaced as requiring Michael's judgment have been resolved. **Next action: implementation planning for Programme 1 — Authentication and tenancy foundation** — this happens outside `docs/audit-program/`'s read-only remit, under `CLAUDE.md`'s normal sprint workflow, exactly as this audit programme's own `WORKFLOW.md` anticipated for post-audit remediation.
