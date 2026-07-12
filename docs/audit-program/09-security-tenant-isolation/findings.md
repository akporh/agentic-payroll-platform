# Stage 09 — Security and Tenant Isolation: Findings

**Status:** complete
**Opened:** 2026-07-12
**Closed:** 2026-07-12
**Evidence:** `docs/audit-program/09-security-tenant-isolation/evidence/01-auth-and-tenant-scoping.txt`

---

## 0. Headline architectural finding (reframes the whole stage)

**09-000 — No authentication mechanism exists anywhere in the application.**

- **current implementation:** `backend/api/main.py` registers every router (`admin`, `health`, `onboarding`, `onboarding_validation`, `payroll`, `payroll_input`, `workspace`, `employees`) with no authentication middleware and no `Depends(...)` auth dependency anywhere. A repo-wide search for `jwt`, `Authorization`, `Bearer`, `current_user`, `authenticate`, `api_key` in `backend/` returns zero matches. `CORSMiddleware` defaults `allow_origins` to `["*"]` when `ALLOWED_ORIGINS` is unset (`allow_credentials=False`). The frontend has no login screen, no token storage, and no auth-related code (`frontend/src`-wide search for `login`/`auth`/`token` returns only unrelated CSS-token and comment matches). `workspaceId` in the frontend is read directly from the URL route param (`useParams`), not from any authenticated session.
- **intended behaviour:** not documented anywhere in `CLAUDE.md`, `README.md`, or `WORKFLOW.md`. No authentication architecture is described in any prior stage's findings or in `docs/wrapper-command/` (already ruled non-authoritative, decision 01-013).
- **suspected or confirmed defect:** the application has no concept of a caller identity. Every route — including payroll-run creation, approval, locking, payment, reconciliation, exports, and the `/admin*` operator dashboards — is reachable by any network client that can reach the API, with only the URL path/body as input. `workspace_id` is not a security boundary; it is a plain, caller-supplied string. This is the root cause underlying nearly every other question this stage was asked to answer (IDOR, tenant isolation, privileged-operation authorization, admin exposure) — those questions are secondary to this one, because there is no identity to authorize in the first place.
- **evidence:** `backend/api/main.py:1-60`; repo-wide grep (evidence file, section "No auth mechanism anywhere"); `frontend/src/pages/WorkspaceDashboard.tsx:133`.
- **status:** confirmed
- **severity:** S0
- **related invariant:** none documented — this is a missing invariant, not a broken one.

This is Phase 1 MVP, deterministic engine, delivered to a single family-business bureau client per `Clients/Sandy/CLAUDE.md`. It is plausible the current deployment relies entirely on network-level access control (e.g., not publicly routable, or fronted by something outside this repository) rather than application-level authentication. No such control is visible in this repository, and none is referenced by any file read in this stage. This is recorded as a human decision below rather than assumed either way.

---

## 1. Route security catalogue

All routes are mounted under `/api/v1` except `/admin*` and `/static` (mounted at root) and `/health*`. No route in the catalogue below has an authentication or authorization dependency. "Workspace/account identifier source" is always "client-supplied path or body param," never a derived session/token claim, for every route in this application.

| Domain | Method & path | Router | Auth dep | Resource-ownership check | Frontend caller | Security status |
|---|---|---|---|---|---|---|
| Workspace setup | `POST /workspace` | workspace.py:51 | none | n/a (creates) | yes | no auth (09-000) |
| Workspace list | `GET /workspaces` | workspace.py:98 | none | **none — returns all workspaces, all tenants** | yes | cross-tenant disclosure (09-001) |
| Workspace info | `GET /workspace/info` | workspace.py:133 | none | none — hardcoded `LIMIT 1`, first workspace only | unclear | low-value info leak |
| Workspace transition | `POST /{workspace_id}/transition` | workspace.py:167 | none | SQL predicate not verified this stage | yes | not fully investigated |
| Employees list/create | `GET/POST /{workspace_id}/employees` | workspace.py:194,280 | none | SQL predicate present (spot-checked pattern) | yes | scoped-but-unauthenticated |
| Employee detail/patch | `GET/PATCH /{workspace_id}/employees/{employee_id}` | employees.py:119,131 | none | **positive control** — `WHERE workspace_id=:wid AND employee_id=:eid` (employee_repo.py:76-77) | yes | scoped-but-unauthenticated |
| Employee contracts | `POST .../contracts`, `PATCH .../employee-contracts/{contract_id}` | employees.py:159,223 | none | scoped via employee FK per `employee_repo.py:417` comment | yes | scoped-but-unauthenticated |
| Salary defs / grades / designations | `GET/POST/PATCH .../salary-definitions`, `/grade`, `/designation` | workspace.py:773-1507 | none | not fully re-verified this stage (spot-checked in Stage 01/03) | yes | scoped-but-unauthenticated |
| Payroll rules | `POST/PATCH/DELETE /{workspace_id}/payroll-rule[/{rule_id}]` | workspace.py:992,1603,1643 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Component metadata/overrides | `POST .../component-metadata`, `PATCH .../component-overrides/{code}` | workspace.py:1045,1270 | none | see §6 | yes | scoped-but-unauthenticated |
| Pay cycle | `POST/PATCH /{workspace_id}/pay-cycle` | workspace.py:855,1377 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Payroll config / rate codes / holidays / attendance | `/workspaces/{workspace_id}/payroll-config`, `/rate-codes`, `/public-holidays`, `/attendance-codes`, `/attendance-policies` | workspace.py:1696-2027 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Payroll input codes/inputs | `GET/POST/PATCH/DELETE /{workspace_id}/payroll/input-codes`, `/inputs[/{input_id}]` | payroll_input.py:95-501 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Payroll run creation (unscoped) | `POST /payroll/run` | payroll.py:44 | none | takes `workspace_id` in body, not verified against anything | unclear | not fully investigated |
| Payroll run creation (scoped) | `POST /{workspace_id}/payroll/run` | payroll.py:889 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Payroll run list/detail/results | `GET /{workspace_id}/payroll/runs[/{run_id}[/results]]` | payroll.py:1002,1036,1070 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| **Retry** | `POST /payroll/run/{run_id}/retry` | payroll.py:1145 | none | **no `workspace_id` in path at all; service derives workspace from the run row itself, not from any caller-verified context** | yes | **09-002: unscoped lifecycle route** |
| **Approve** | `POST /payroll/run/{run_id}/approve` | payroll.py:1172 | none | same as above | yes | **09-002** |
| **Lock** | `POST /payroll/run/{run_id}/lock` | payroll.py:1192 | none | same as above | yes | **09-002** |
| **Pay** | `POST /payroll/run/{run_id}/pay` | payroll.py:1212 | none | same as above; `actor_id` self-declared in body, defaults to `"system@internal"` | yes | **09-002** |
| **Reconcile (unscoped, legacy)** | `POST/GET /payroll/run/{run_id}/reconcile` | payroll.py:1236,1264 | none | same as above | superseded, no current caller found | **09-003 (=06-007), see §4** |
| **Reconcile (nominally scoped)** | `GET/POST/PATCH /{workspace_id}/payroll/runs/{run_id}/reconciliation` | payroll.py:1293,1302,1318 | none | **`workspace_id` accepted in path but never passed to or used by the underlying service call** | yes | **09-004: decorative scoping, see §4** |
| **Timeline/trace (nominally scoped)** | `GET /{workspace_id}/payroll/runs/{run_id}/timeline` | payroll.py:1337 | none | **`workspace_id` accepted but unused; `get_trace_steps(run_id)` takes no workspace param** | yes | **09-005: decorative scoping** |
| Legacy executor stats | `GET /{workspace_id}/payroll/ops/legacy-executor-stats` | payroll.py:1344 | none | **`workspace_id` accepted but unused; returns global stats across every workspace's runs, including per-run breakdown** | unclear | **09-006: cross-tenant disclosure** |
| Run audit | `GET /{workspace_id}/payroll/runs/{run_id}/audit` | payroll.py:1362 | none | not fully re-verified this stage | yes | not fully investigated |
| Exports (bank/PAYE/pension/full-detail) | `GET /{workspace_id}/payroll/runs/{run_id}/exports/*` | payroll.py:1455-1679 | none | **positive control** — `_guard_locked_or_paid` checks `WHERE payroll_run_id=:rid AND workspace_id=:wid` (payroll.py:1417-1420) | yes | scoped-but-unauthenticated; see §9 for CSV-injection note |
| Timesheet upload/derive/approve/status | `POST/GET /workspaces/{workspace_id}/timesheet/*` | payroll.py:1679-1725 | none | not fully re-verified this stage | yes | scoped-but-unauthenticated |
| Timesheet audit | `GET /workspaces/{workspace_id}/timesheet/audit/{employee_id}` | payroll.py:1725 | none | not fully re-verified this stage | no (06-006) | scoped-but-unauthenticated, no UI caller |
| Onboarding upload/preview/commit | `POST /onboarding/*` | onboarding.py:45,90,146 | none | `workspace_id` typically in body; not re-verified this stage | yes | not fully investigated |
| Onboarding validation | `POST /onboarding/validate` | onboarding_validation.py:148 | none | not fully re-verified this stage | yes | not fully investigated |
| **Admin dashboards** | `GET /admin`, `/admin/onboarding`, `/admin/payroll` | admin.py:9,17,24 | none | n/a — server-rendered HTML shells; underlying data fetched client-side from the same unauthenticated API | unknown reachability outside this repo | **09-007: unauthenticated operator surface, see §8** |
| Health | `GET /health*` | health.py | none | n/a, no sensitive data expected | n/a | not investigated — low risk by convention |

Full route enumeration (all `@router.get/post/patch/put/delete` decorators) is preserved in the evidence file. Rows marked "not fully re-verified this stage" reuse the workspace-scoping pattern confirmed correct at the SQL layer in Stages 01, 03, 06, and 08 spot checks (e.g. `employee_contract` joins, per `feedback_employee_contract_workspace_scope` project memory); this stage did not re-derive each one line-by-line given the scale of the finding at §0/§2/§4 that supersedes the value of that exercise. This is recorded explicitly as a scope limitation, not silently assumed.

---

## 2. Authentication architecture summary

- **Mechanism in use:** none. No token issuance, no session, no password, no API key.
- **Token/session validation location:** n/a.
- **Current-user object:** does not exist anywhere in the codebase.
- **Account/workspace membership representation:** none. `workspace_id` is a UUID the caller supplies; the backend treats it as authoritative input, not as a claim to be verified against an identity.
- **Unauthenticated development bypasses:** the entire application is an unauthenticated bypass; there is no authenticated mode to bypass.
- **Consistency across route modules:** fully consistent — every module (admin, onboarding, payroll, payroll_input, workspace, employees) applies zero authentication, uniformly.
- **Admin/operator routes stronger checks:** no. `/admin*` routes have identical (zero) protection to ordinary workspace routes.
- **Frontend route protection:** none found. No route guard, no redirect-to-login, no protected-route wrapper in `frontend/src` was located in this stage's searches (§0 evidence). Any UI-level restriction, if present, would be cosmetic only, since the backend enforces nothing.

**status:** confirmed | **severity:** S0 | **finding id:** rolls into 09-000.

---

## 3. Tenant-isolation audit

The `request identity → membership check → resource lookup → service/repo → SQL predicate` chain required by this stage's investigation section cannot be evaluated past its first link: **there is no request identity**, so there is no membership check to trace. From the second link onward, the picture is mixed:

- **Where the SQL layer does enforce a `workspace_id` predicate** (e.g. `employee_repo.get_employee_with_contract_history`, `_guard_locked_or_paid` for exports), a caller who supplies the *correct* `workspace_id` for a *given* `run_id`/`employee_id` cannot read another workspace's row through that specific route — but nothing prevents the caller from supplying any `workspace_id`, including one harvested from `GET /workspaces` (§1, `09-001`).
- **Where the service layer does not accept a `workspace_id` at all** (retry/approve/lock/pay, and the nominally-scoped reconciliation/timeline/stats routes), the SQL-predicate defense doesn't exist even in principle — the operation is keyed on `run_id` alone, globally, across all workspaces. See §4 and `09-002`/`09-004`/`09-005`/`09-006`.

IDOR risk by resource type, given the above:

| Resource | IDOR risk without valid auth | Notes |
|---|---|---|
| workspace_id | n/a — enumerable via `GET /workspaces` | 09-001 |
| employee_id | low, *if* the correct workspace_id is also supplied (positive control confirmed) | requires workspace_id anyway |
| payroll-run_id | **high on retry/approve/lock/pay/reconcile/timeline/stats** — workspace_id not required or not enforced | 09-002/09-004/09-005/09-006 |
| payroll-result_id | not directly addressable by ID in any route found | lower priority |
| reconciliation_id | not directly addressable; keyed by run_id, same exposure as run_id | 09-004 |
| salary-definition/grade/designation IDs | not fully re-verified this stage | see §1 |
| rule-set/statutory-rule IDs | not fully re-verified this stage | see §1 |
| audit/trace identifiers | run-keyed, same exposure as run_id where scoping is decorative | 09-005 |

This section is a synthesis across findings `09-002`, `09-004`, `09-005`, and `09-006` below, each of which carries its own single status. Rows in §1 marked "not fully re-verified this stage" are explicitly out of scope for this stage rather than classified either way.

---

## 4. `09-002` — Unscoped run-lifecycle routes (retry/approve/lock/pay/reconcile)

- **current implementation:** `POST /payroll/run/{run_id}/retry`, `/approve`, `/lock`, `/pay`, and the legacy `/payroll/run/{run_id}/reconcile` (GET+POST) take only `run_id` — no `workspace_id` anywhere in the path. Each calls into an application-service function (`retry_failed_payroll_employees`, `approve_payroll_run`, `lock_payroll_run`, `mark_payroll_run_paid`, `reconcile_payroll_run`) whose *own* signature also has no `workspace_id` parameter; each derives `workspace_id` internally with `SELECT workspace_id, status FROM payroll_run WHERE payroll_run_id = :run_id` (`payroll_approval_service.py:62,135,210`; `payroll_retry_service.py:538`) purely to use it downstream for its own SQL joins (e.g. resolving that workspace's rules) — never to check it against anything the caller asserted.
- **intended behaviour:** given `CLAUDE.md`'s "workspace scoping enforced at the query level" rule, some verification that the caller is entitled to act on this specific workspace's run is implied, even if the exact mechanism (auth) is undefined.
- **suspected or confirmed defect:** any caller who can obtain or guess a `run_id` (UUID; harvestable via the scoped `GET /{workspace_id}/payroll/runs` list once `workspace_id` is known from `09-001`, or via the unscoped `POST /payroll/run` creation path) can retry, approve, lock, or pay that run regardless of which workspace they "belong to" — there being no workspace membership concept to belong to in the first place. This is a strict superset of `06-007`'s already-confirmed unscoped-reconciliation-route finding: it is not one legacy route pair, it is five of the six most consequential lifecycle-transition endpoints in the entire payroll engine (only run *creation* and *results-view* have any `workspace_id` in their path at all among the lifecycle family).
- **evidence:** `payroll.py:1145-1277`; `payroll_approval_service.py:62-73,135-146,210-221`; `payroll_retry_service.py:538-549`; evidence file.
- **status:** confirmed
- **severity:** S0 (financially consequential lifecycle transitions — approve/lock/pay — reachable without any tenant check)
- **related invariant:** extends `06-007`; supersedes it in scope. `payroll_run.status = 'APPROVED'` immutability invariant is about *field* mutation, not *who* may trigger the transition — this finding is that "who" has no gate at all.

**`06-007` final classification (this stage's required deliverable):** the legacy unscoped `/payroll/run/{run_id}/reconcile` pair is **insecure/tenant-bypass risk**, not "secure but obsolete." It is registered, reachable (confirmed present in `main.py`'s router include, no conditional gating), has no frontend caller (superseded by the `/{workspace_id}/...` reconciliation family per Stage 06), and duplicates strictly weaker logic than its replacement — except its replacement (`09-004` below) turns out to share the identical underlying weakness, so "duplicates weaker logic" is more precisely "duplicates logic with the same root defect, via a different route shape."

---

## 5. `09-004`/`09-005`/`09-006` — Decorative `workspace_id` in nominally-scoped routes

- **current implementation:** `GET/POST/PATCH /{workspace_id}/payroll/runs/{run_id}/reconciliation` (payroll.py:1293,1302,1318), `GET /{workspace_id}/payroll/runs/{run_id}/timeline` (payroll.py:1337), and `GET /{workspace_id}/payroll/ops/legacy-executor-stats` (payroll.py:1344) all declare `workspace_id: str` as a path parameter but **never pass it to the function they call**: `get_reconciliation_status(run_id)`, `reconcile_payroll_run(run_id, ...)`, `resolve_reconciliation(run_id, ...)`, `get_trace_steps(run_id)`, and `get_legacy_executor_stats()` (no args at all) — confirmed by reading every one of those five function signatures (`reconciliation_service.py:21,78,83`; `execution_trace_repo.py:45,102`), none of which accept a `workspace_id` parameter.
- **intended behaviour:** the `/{workspace_id}/...` URL shape strongly signals — to both a developer reading the route table and a frontend engineer wiring a caller — that the resource is being verified against that workspace. `CLAUDE.md`'s "workspace scoping enforced at the query level, not just the route" rule states the opposite of what is implemented here: this is scoping enforced at *neither* the route nor the query level, despite the route's own shape implying it is.
- **suspected or confirmed defect:** three concrete consequences:
  1. `09-004` (reconciliation): a caller who knows any `run_id` can read, create, or resolve a reconciliation record by supplying an arbitrary `workspace_id` in the path — the path segment is accepted but discarded before it reaches any query.
  2. `09-005` (timeline/trace): `get_run_timeline` returns another workspace's full execution-trace step list under any `workspace_id` prefix, given only the `run_id`.
  3. `09-006` (legacy executor stats): `legacy_executor_stats` doesn't merely fail to scope — it structurally cannot, since the query it calls (`get_legacy_executor_stats()`) takes no filter argument and returns **global** aggregate and per-run statistics across every workspace's runs regardless of the `workspace_id` path segment supplied. This is a direct cross-tenant disclosure of other tenants' run identifiers and legacy-fallback activity, reachable by any caller regardless of which (or whether a real) `workspace_id` they supply.
- **evidence:** `payroll.py:1293-1360`; `reconciliation_service.py:21,78,83`; `execution_trace_repo.py:45,102`; evidence file.
- **status:** confirmed
- **severity:** S1 for `09-004`/`09-005` (data exposure/mutation, gated behind knowing a `run_id`, which is itself trivially obtainable per `09-001`/`09-002`); S1 for `09-006` (no gating at all — the `run_id` isn't even needed, only reachability of the route).
- **related invariant:** none pre-existing; this is a new pattern class ("path-shape implies scoping that the implementation does not perform") worth naming explicitly for Stage 12/13 remediation guidance, since it is easy to reintroduce even after `09-002` is fixed if the fix is applied inconsistently.

---

## 6. `09-001` — Cross-tenant workspace enumeration

- **current implementation:** `GET /workspaces` (`workspace.py:98-130`) executes an unfiltered `SELECT ... FROM workspace w LEFT JOIN employee e ...` with no `WHERE` clause at all, returning every workspace's `workspace_id`, `name`, `country_code`, `base_currency`, `status`, and active-employee count to any caller.
- **intended behaviour:** undocumented; plausibly intended as a "pick your workspace" landing list for a single authenticated operator who is allowed to see all workspaces they belong to. In a single-tenant-per-operator model this would be a defect; the underlying membership model does not exist to say.
- **suspected or confirmed defect:** this route is the practical enabler of every other finding in this stage — it converts "guess a UUID" into "call one unauthenticated endpoint and receive the full list." It is also a standalone disclosure: workspace name, country, currency, and active headcount for every client of this platform are visible to any caller.
- **evidence:** `workspace.py:98-130`; evidence file.
- **status:** confirmed
- **severity:** S0 (this is the single highest-leverage finding in the stage — every other IDOR/cross-tenant finding depends on this one being reachable, and it requires zero prior knowledge to exploit).
- **related invariant:** none pre-existing.

---

## 7. `09-007` — Unauthenticated admin/operator dashboards

- **current implementation:** `admin.py` registers `GET /admin`, `/admin/onboarding`, `/admin/payroll` at the application root (not under `/api/v1`, not behind any auth dependency), rendering Jinja2 templates (`dashboard.html`, `onboarding.html`, `payroll.html`) that are thin shells — the templates themselves (18-74 lines each) contain no server-rendered sensitive data directly, but are designed to call the same unauthenticated `/api/v1/...` routes client-side.
- **intended behaviour:** undocumented as an operator surface anywhere in `CLAUDE.md`/`README.md`/`WORKFLOW.md`.
- **suspected or confirmed defect:** these are operator-facing dashboards with zero authentication, mounted at predictable, undocumented-but-guessable paths (`/admin`, `/admin/onboarding`, `/admin/payroll`), reachable by anyone who can reach the deployment. Whether this constitutes a materially *distinct* risk beyond `09-000` depends entirely on deployment reachability (internal network vs. public internet), which is outside this repository's visibility.
- **evidence:** `admin.py:1-29`; `main.py:50`; `backend/api/templates/`.
- **status:** confirmed — the routes exist, are registered, and are unauthenticated. Whether they are reachable from the public internet in the current deployment is a separate, infrastructure-level question this repository cannot answer; it does not change the code-level finding and is called out in the defect text above rather than in the status field.
- **severity:** S1 (rolls up into S0 `09-000` if reachability is public; recorded as S1 standalone because the specific "admin at a predictable path" pattern is worth naming for infra hardening even if `09-000` is fixed first).

---

## 8. `07-001` — 21-site raw exception disclosure: risk classification

Reused and extended from Stage 07's confirmed parent finding (not reopened, not reclassified — see `_core/human-decisions.md` for the still-open priority decision).

| Group | Sites | Exception type | Risk classification |
|---|---|---|---|
| A — Broad catch-all, DB writes in scope | `workspace.py:93,180,663,768,1452,1477,1502,1598` (8 sites), `workspace.py:1841,2027` (2 sites) = 10 sites | `except Exception as e/exc` | **Structurally capable of disclosure.** These wrap operations that include repository writes (confirmed for `workspace.py:2020-2027` in Stage 07 — a raw repository DB write; the other 9 follow the identical pattern of a broad catch immediately around a service/repo call). A DB constraint violation, type-mismatch, or connection-level error raised inside the `try` block is returned to the client verbatim via `str(e)`, exposing table/column/constraint names by construction — not merely by developer oversight in a specific case. |
| B — Custom/narrow domain exception | `workspace.py:1020 (RuleSetLockedError)`, `1774,1787,1828 (ValueError)` = 4 sites | narrow, developer-authored | **Currently safe developer-authored exception only.** These are raised explicitly by application code with a controlled message, not by an underlying driver/DB exception propagating up. |
| C — `ValueError`-only, payroll.py | `payroll.py:342,845,1159,1182,1202,1226,1332` = 7 sites | `except ValueError as exc` | **Currently safe developer-authored exception only**, on the same basis as Group B — `ValueError` in this codebase's service layer is consistently used as the controlled-message channel (confirmed pattern across `payroll_approval_service.py`, `reconciliation_service.py`, `payroll_retry_service.py` — every `raise ValueError(...)` found in this stage's reading carried a hand-written message, never a re-raised driver exception). |
| D — Dead/unreachable | none identified | — | no sites in this category |

Net: **10 of 21 sites (Group A) are structurally capable of leaking raw DB/schema detail; 11 of 21 (Groups B+C) are currently safe** because the exception classes they catch are exclusively raised with developer-controlled messages in this codebase today. Group A's risk is not hypothetical — Stage 07 already confirmed one concrete instance (`workspace.py:2020-2027`) wrapping a raw repository write; the other 9 Group-A sites share the identical `except Exception` shape around similar write/read operations and are classified by the same structural reasoning, not re-verified line-by-line against a live-triggered exception in this stage (would require the controlled-execution work explicitly deferred to Stage 13 per `07-001`'s still-open priority decision).

**status:** confirmed — the Group A/B/C boundaries and site counts above are all verified against the code. **severity:** carries forward `07-001`'s S1; no new child finding warranted — the existing systemic finding already captures this at the correct granularity, per this stage's own finding-rule instruction to only split where a materially distinct risk exists. Group A's DB-leak capability is the "materially distinct risk" and is now explicitly named rather than left implicit.

---

## 9. Configuration/statutory-control authorization assessment (`03-004`/`08-003`)

- **current implementation:** `patch_component_override` (component-override PATCH route, `workspace.py:1270`) has no role or auth check of any kind — any caller who can reach the workspace-scoped route (i.e., any caller, per `09-000`) can disable a statutory deduction component, exactly as `08-003` already described mechanically. There is no distinct "privileged" code path for this operation versus any other workspace configuration write; all configuration routes share the same (absent) authorization model.
- **intended behaviour:** undocumented; `03-004`'s human decision (still open) is about the *product policy* of whether this should be possible at all, which this stage does not resolve, per its own constraints.
- **suspected or confirmed defect:** access control for this specific action is identical to every other route in the system — none — so there is no *additional* privilege-escalation risk specific to statutory-component disablement beyond the general `09-000` finding. The distinct question this stage was asked ("who can perform that action") has a flat answer: anyone who can reach the API at all, with no role distinction existing anywhere in the codebase to make "anyone" a meaningful subset of a larger population.
- **auditability:** the disable action itself writes to `client_component_metadata` with no accompanying `audit_log`/`event_store` row (confirmed absent in Stage 08's `08-003`); this stage adds no new evidence on that point, only confirms no authorization gate exists around the unaudited write.
- **evidence:** `workspace.py:1270-1377` (component-override PATCH block); cross-referenced against `08-003`/`03-004`.
- **status:** confirmed — no role/auth distinction exists for this or any configuration route. The separate, still-open product-policy question ("should this be possible at all") remains logged under `03-004`'s own `human decision required` status in `_core/human-decisions.md`; this finding does not duplicate that status, only the access-control fact.
- **severity:** S1 (rolls into `09-000`; no standalone escalation since it is not qualitatively different from every other unauthenticated write in the system).

---

## 10. Privileged lifecycle-operation role matrix

| Operation | Role distinction exists? | Enforced server-side? |
|---|---|---|
| Create run | no | no |
| Retry | no | no |
| Approve | no | no |
| Lock | no | no |
| Mark paid | no | no |
| Reconcile / resolve mismatch | no | no |
| Export (bank/PAYE/pension/full-detail) | no | no |
| View audit logs/traces | no | no |

Every operation is reachable by "any authenticated workspace member" in the sense that CLAUDE.md's domain language implies distinct roles might exist — but since no authentication exists at all, the honest answer is **any caller, full stop**, not merely "any authenticated member without further role gating." Recorded as human-decision-required (below) rather than invented, per this stage's finding rules.

**status:** confirmed | **severity:** rolls into `09-000`.

---

## 11. Export and report security (`§9` of the investigation brief)

- **Cross-workspace run ID access:** blocked by the SQL-level `_guard_locked_or_paid` predicate (positive control, `payroll.py:1417-1420`) — but only if the caller supplies the *correct* `workspace_id`, which is trivially obtainable per `09-001`.
- **Unnecessary personal/payroll data:** bank-upload export includes `account_number` and `bank_name` (payroll.py:1470-1478) — appropriate for its stated purpose, not excessive relative to a bank-file export's function, but notable given the complete absence of any access gate beyond "know the workspace_id + run_id, both enumerable."
- **CSV/formula injection risk:** `employee_name` and other employee-controlled free-text fields are written directly into CSV rows via `_csv.writer` with no leading-character sanitization (`payroll.py:1470-1521` and siblings). A field value beginning with `=`, `+`, `-`, or `@` would be interpreted as a formula by Excel/Sheets when the exported CSV is opened. `employee_name` is entered via onboarding/employee-management routes, not directly by the export's own caller, but it is still employee-controlled input reaching an export designed for bank/regulator submission.
- **Filename/header leakage:** filenames use `run_id[:8]` only (e.g. `bank_upload_{run_id[:8]}.csv`) — no additional identifier leakage beyond the truncated run ID already known to the caller.
- **Content-type/download handling:** not fully re-verified this stage (`_streaming_csv` helper not read in full).
- **Auditability of export actions:** no `audit_log`/`event_store` write found accompanying any export route in the code read this stage — consistent with `07-002`'s already-confirmed general audit-coverage gap for non-lifecycle actions.

**New finding — `09-008`, CSV/formula injection in payroll exports:**
- **status:** confirmed — the absence of any leading-character sanitization before writing employee-controlled text into CSV output is verified directly in the code. Real-world exploitability depends on whether onboarding validation already restricts `full_name` content (not verified this stage) and is noted as a caveat on severity, not on status.
- **severity:** S2
- **evidence:** `payroll.py:1470-1521`; onboarding employee-name validation not re-read this stage.

---

## 12. Audit/trace/error-data exposure matrix

| Surface | Exposure found | Notes |
|---|---|---|
| `error_message` (`payroll_run`, from 05-001 remediation) | not directly returned by any route read this stage in raw form | not fully re-verified |
| `component_trace_jsonb` | readable via results route once `workspace_id`+`run_id` known | same access-control profile as the rest of the results family |
| `execution_trace` / timeline | **cross-tenant readable regardless of `workspace_id` supplied** | `09-005` |
| `audit_log`/`event_store` | not directly exposed via any route read this stage | no dedicated audit-read route found |
| Reconciliation notes | readable/writable cross-tenant via `09-004` | |
| Timesheet audit output | scoped route exists, no frontend caller (06-006); not re-verified for internal scoping this stage | |

Rows marked in the table above carry their own status implicitly via their cross-referenced finding (`09-005` for the timeline row); rows marked "not fully re-verified" or "not directly exposed" in the table are explicitly out of scope for this stage, recorded as a scope limitation rather than assumed safe.

---

## 13. Logging, CORS, and secret-handling assessment

- **Secrets in repository:** none found. Repo-wide search for `SECRET_KEY=`, `api_key=`, `password=` literals (excluding `.example` files, `os.environ` reads, and docstrings) returned zero matches. Only `.env.example`/`.env.production.example` files are tracked, both templates.
- **Database URL:** `backend/infra/db/session.py:9` defaults `DATABASE_URL` to a local dev connection string (`postgresql+psycopg2://michaelemedo@localhost:5432/payroll_dev`) when the env var is unset — a local-only fallback, not a production credential; acceptable as a development convenience, not a disclosure.
- **CORS:** `ALLOWED_ORIGINS` defaults to `"*"` with `allow_credentials=False` (`main.py:36-45`). Because `allow_credentials=False`, browsers will not attach cookies to cross-origin requests even under a wildcard origin — but since this application uses no cookies/session at all (`09-000`), that mitigation is moot; the wildcard origin means any website can script a browser into calling this API directly, and the API will answer, because nothing about origin or credential state gates any route regardless.
- **`print()` of sensitive state:** `07-004`'s already-confirmed `print("Loaded PAYE from:", __file__)` in `paye.py:11` prints a filesystem path on every import — low sensitivity, already logged in Stage 07, not reclassified here.
- **Logged personal/payroll data:** not exhaustively re-audited this stage; no new instance found in the files read.

**status:** confirmed (no committed secrets; permissive CORS by default) | **severity:** S2 standalone (CORS default), rolls into `09-000` for practical impact (auth absence dominates).

---

## 14. Cross-workspace relational consistency (security-impact extension of Stage 08)

Stage 08 found no schema-permitted cross-workspace referential defect in its targeted spot checks. This stage's investigation did not identify a *new* schema/FK-level cross-workspace linkage beyond what Stage 08 already covered — the cross-tenant risk identified in this stage is uniformly an **application/route-layer** gap (missing or decorative `workspace_id` checks), not a data-model defect. No child finding is warranted here beyond referencing `08`'s existing register; the security impact of that register is that route-layer gaps (`09-002`/`09-004`/`09-005`/`09-006`) are the operative risk, not the relational schema itself, which continues to model tenancy correctly where routes choose to enforce it.

**status:** rejected (no new relational-schema cross-workspace defect found; existing Stage 08 register stands) | **severity:** n/a.

---

## 15. Positive-control register (correctly isolated / structurally sound elements)

- `employee_repo.get_employee_with_contract_history` and `update_employee`: correct compound `WHERE workspace_id = :wid AND employee_id = :eid` predicate (employee_repo.py:76-77, 393).
- `employee_contract` updates: scoped via the employee FK join, matching `feedback_employee_contract_workspace_scope`'s documented pattern.
- `_guard_locked_or_paid` / `_guard_calculated_or_later` (export guards): correct compound `WHERE payroll_run_id = :rid AND workspace_id = :wid` predicate (payroll.py:1417-1420).
- No committed secrets or credentials anywhere in the tracked repository.
- `payroll_reconciliation`'s CHECK constraints (already confirmed in Stage 08) remain the strongest DB-level invariant enforcement found anywhere in this audit programme, and are orthogonal to (unaffected by) this stage's route-layer findings.
- Employee-record read/write is the one route family in this audit where "workspace_id present in the path" was verified to *actually reach the query*, in contrast to the reconciliation/timeline/stats routes in §5.

---

## Summary of new/extended findings this stage

| ID | Summary | Status | Severity |
|---|---|---|---|
| 09-000 | No authentication mechanism exists anywhere in the application | confirmed | S0 |
| 09-001 | `GET /workspaces` enumerates every tenant unauthenticated | confirmed | S0 |
| 09-002 | Retry/approve/lock/pay/reconcile(legacy) take no `workspace_id`, service layer never verifies tenant ownership (extends/finalizes `06-007`) | confirmed | S0 |
| 09-004 | Nominally-scoped reconciliation routes accept but discard `workspace_id` | confirmed | S1 |
| 09-005 | Nominally-scoped timeline/trace route accepts but discards `workspace_id` | confirmed | S1 |
| 09-006 | Legacy-executor-stats route returns global cross-tenant data regardless of `workspace_id` | confirmed | S1 |
| 09-007 | Unauthenticated admin/operator HTML dashboards at predictable paths | confirmed | S1 |
| 09-008 | CSV/formula injection risk in payroll exports (no sanitization of employee-controlled text fields) | confirmed | S2 |
| `06-007` | Final classification: **insecure/tenant-bypass risk**, not secure-but-obsolete | confirmed | rolls into S0 09-002 |
| `07-001` | 21 sites grouped: 10 structurally disclosure-capable (Group A), 11 currently safe (Groups B+C) | confirmed | S1 (unchanged) |
| `03-004`/`08-003` | No role/auth distinction for statutory-component disablement — same (absent) model as every other route | confirmed | rolls into S0 |
| §14 | No new cross-workspace relational-schema defect | rejected | n/a |

## Handoff notes for Stages 10–13

- **Stage 10** (execution-trace remediation design): must account for `09-005` — any redesigned trace-read route must include a real `workspace_id` verification, not just accept the parameter.
- **Stage 11** (scenario testing): should include a scenario exercising `09-001`→`09-002` end-to-end (enumerate workspace, harvest a run_id, transition it) as a documented, evidence-backed regression scenario once remediation is designed — not executed destructively in this audit stage.
- **Stage 12** (code simplification): the "path declares `workspace_id`, handler ignores it" pattern (`09-004`/`09-005`/`09-006`) is exactly the kind of latent defect a simplification/consistency pass should catch by convention (e.g. a lint rule or code-review checklist item: every `{workspace_id}` path param must be threaded into the query), independent of whether authentication (`09-000`) is fixed first.
- **Stage 13** (consolidated backlog): `09-000` (no authentication) is the dominant, backlog-topping item — nearly every other finding in this audit programme's tenant-isolation dimension is downstream of it. `07-001`'s Group A (10 sites) should be prioritized for the `str(e)` fix ahead of Groups B/C. `09-008` (CSV injection) is a low-cost, independent fix candidate. The still-open `03-004` product-policy decision and `09-007`'s admin-dashboard reachability both need input from Michael that is outside this repository's visibility (deployment/infra facts, and the intended access-control model going forward).

## Human decisions — resolved at Stage 09 close (2026-07-12)

### Decision 1 — application authentication

`09-000` is confirmed an **unrecognized S0 production blocker**, not an intentionally accepted network-only architecture.

- Application-level authentication and server-side authorization are mandatory before any live or production-data use.
- Network, VPN, reverse-proxy, firewall, or private-subnet controls may be retained as defence in depth, but they do not replace application identity, membership, and authorization checks.
- Development environments may support an explicit, disabled-by-default local bypass, but production must fail closed when authentication configuration is absent.

### Decision 2 — tenancy and role model

The intended operating model:

- one **bureau account** can manage multiple client **workspaces**;
- every user is authenticated and belongs to an account;
- access to workspaces is explicit through membership, not inferred from a caller-supplied UUID;
- the current product scope is bureau-operated, not direct client self-service;
- the model must remain extensible to workspace-scoped client users later without redesigning tenancy.

Minimum roles for backlog/design purposes:

1. **Platform administrator** — platform-wide operational administration; not an ordinary payroll user.
2. **Bureau administrator** — account/workspace membership, configuration, and user administration across permitted workspaces.
3. **Payroll operator** — employee/input maintenance, run creation, retry, reconciliation preparation, and exports for assigned workspaces.
4. **Payroll approver** — approve, lock, resolve reconciliation where permitted, and authorize payment-state transitions; separation from preparation should be supported.
5. **Read-only auditor/viewer** — results, traces, audit history, and reports without mutations.

A single person may hold multiple roles in the initial client deployment, but the system must enforce permissions as roles rather than hard-code a single-operator assumption. Direct client-workspace users are out of the current MVP scope, but future membership must be constrainable to one or more explicit workspaces.

Both decisions are also recorded in `_core/human-decisions.md`, marked resolved.

---

## Stage 09 close — final review conclusions and remediation-sequencing handoff

All findings raised during the initial investigation are reaffirmed at closure, with no severity or status changes:

- `09-000` confirmed S0 — no application authentication or caller identity exists.
- `09-001` confirmed S0 — unauthenticated `GET /workspaces` enumerates all tenants and enables downstream attacks.
- `09-002` confirmed S0 — retry, approve, lock, pay, and legacy reconcile use a global `run_id` with no caller/workspace authorization.
- `09-004` confirmed S1 — scoped reconciliation routes accept but discard `workspace_id`.
- `09-005` confirmed S1 — timeline/trace accepts but discards `workspace_id`.
- `09-006` confirmed S1 — legacy executor stats returns global cross-workspace data.
- `09-007` confirmed S1 — predictable admin dashboards are unauthenticated; infrastructure reachability may affect real-world exposure but not the code-level finding.
- `09-008` confirmed S2 — employee-controlled text reaches CSV exports without spreadsheet-formula sanitization.
- `06-007` finalized: **insecure/tenant-bypass risk**, a Stage 12 removal candidate once secure replacement paths exist.
- `07-001` remains S1: 10 of 21 sites structurally capable of raw DB/schema disclosure (Group A); 11 currently catch only controlled developer-authored exceptions (Groups B+C).
- Positive controls reaffirmed: no committed secrets; correctly scoped employee-record and export guards (`employee_repo`, `_guard_locked_or_paid`).
- `03-004` remains an open product-policy decision, unchanged by this stage — Stage 09 confirms only that currently anyone reaching the API can modify the statutory-component control, and that no role model or audit trail protects it.

### Required backlog/design handoff (Stage 13, sequenced)

Stage 13 must treat security remediation as a sequenced programme, not isolated route patches:

1. Introduce authentication and account/workspace membership.
2. Introduce centralized authorization dependencies/policies and the role model above.
3. Make workspace ownership checks mandatory for every child resource and lifecycle operation.
4. Replace or remove unscoped/decoratively scoped routes.
5. Restrict `/admin*` and diagnostics to platform-admin/operator roles and deployment controls.
6. Sanitize Group A raw exceptions and log full details server-side.
7. Add security audit events for privileged changes and lifecycle transitions.
8. Add CSV-injection protection.
9. Add regression scenarios for cross-workspace enumeration, reads, mutations, exports, and lifecycle transitions.

Do not authorize production/live-data use merely because individual tenant predicates exist on some routes. The platform remains unsafe until caller identity, membership, and authorization are enforced consistently.

### Handoff to Stage 10 (updated at close)

Stage 10 (execution-trace remediation design) must additionally treat `09-005` as a required input: any redesigned trace-read route must include a real `workspace_id` ownership check as part of its design, not merely carry the parameter forward decoratively.
