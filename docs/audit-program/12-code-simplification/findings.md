# Stage 12 — Code Simplification: Findings

**Status:** complete
**Opened:** 2026-07-13
**Closed:** 2026-07-13
**Evidence:** `docs/audit-program/12-code-simplification/evidence/01-key-greps.txt`

This is a read-only audit/design stage. No backend, frontend, migration, test, or script file was modified. Findings below re-verify prior-stage handoffs (`01-002`, `01-004`, `05-002`, `05-003`, `05-005`, `06-007`, `07-004`, `08-001`) against the current codebase state and add new simplification candidates discovered this stage, most notably a frontend status-type duplication/drift finding that sharpens `06-001`/`06-004`.

---

## 1. Simplification candidate register

| # | Candidate | Location | Evidence of non-use/duplication | Classification |
|---|---|---|---|---|
| C1 | ORM-based `backend/infra/db/repositories/workspace_repo.py` | see §2 | Used only by 3 onboarding modules for read-only boolean checks | intentionally-separate, recommend rename+document |
| C2 | Legacy executor fallback (`component_metadata or None`) | `payroll.py:871`, `executor.py:95-120` | Fires on the live production route, 9.3% of dev-DB runs (caveat: dev DB confirmed drifted) | resolved at close: phased migrate-then-remove programme, see §3 |
| C3 | `employee_contract_snapshot.components_jsonb` | migration `b5c6d7e8f9a0` | Zero readers, confirmed 3 stages running (03/05/12) | independently safe cleanup |
| C4 | `payroll_result.salary_inputs_snapshot` | same migration | Write-only, but has a stated future audit-surface purpose | retain intentionally |
| C5 | Duplicated statutory-rate extraction logic | `payroll.py:263-280` vs `payroll_retry_service.py:184-197` | Verbatim-identical parsing/Decimal-conversion logic, confirmed still live post-`04-001` | independently safe cleanup (low risk, pure-function extraction) |
| C6 | `paye.py:11` module-level `print()` | `backend/domain/rules/paye.py` | Fires on every import, confirmed unchanged since Stage 07 (`07-004`) | independently safe cleanup |
| C7 | `backend/scripts/test_*.py` (6 files) | `backend/scripts/` | Misleadingly named like pytest tests but are manual DB-writing CLI scripts, excluded from pytest via `norecursedirs`; functionally superseded by the 306-test suite (Stage 11) | cleanup bundled with remediation (rename or archive, not silent deletion — see §10) |
| C8 | Legacy unscoped reconciliation routes | `payroll.py:1236,1264` | Reachable, insecure, superseded — reconfirmed live in Stage 11 | blocked by security architecture (see §5) |
| C9 | Unscoped retry/approve/lock/pay routes | `payroll.py:1145-1233` | No scoped replacement exists yet | blocked by security architecture — NOT a simple deletion candidate |
| C10 | Frontend `PayrollRunStatus` duplicated across two modules, both wrong in different ways | `types/payroll.ts:1-8`, `design-system/components/Status.tsx:27-35` | New this stage — see §7 | cleanup bundled with remediation (fix alongside `06-001`'s FAILED-surfacing work) |
| C11 | Free-text `ExecutionTracer.step()` names | 9 call sites, Stage 10 evidence | No stable event-code taxonomy exists yet | blocked by Stage 10 trace implementation |
| C12 | Two migrations using `EXCEPTION WHEN others` swallow-all | `c9d0e1f2a3b4`, `f9a0b1c2d3e4` | Confirmed bounded to exactly these two files, no others found | cleanup bundled with remediation (fix as part of `08-001`'s corrective migration) |
| C13 | `docs/wrapper-command/` | repo root | Already ruled non-authoritative (decision 01-013) | documentation authority label needed, not deletion |

---

## 2. Repository-layer duplication map and recommendation (`01-002`)

**Current state, re-verified:**
- `backend/infra/repositories/` — 13 files, raw SQL via `sqlalchemy.text()`, the documented canonical layer per `CLAUDE.md`'s architecture table.
- `backend/infra/db/repositories/workspace_repo.py` — 1 file, 44 lines, SQLAlchemy ORM (`db.query(Workspace).get(...)`), imported exclusively by three onboarding-domain modules (`hard_validator.py`, `onboarding_status.py`, `state_inference.py`).

**Overlap analysis:** none. All 6 functions in the ORM file (`get_workspace`, `has_pay_cycle`, `has_grade`, `has_designation`, `has_salary_definition`, `has_active_payroll_rule`, `has_component_metadata`) are simple existence checks used only to answer "has this workspace completed onboarding step X?" — a narrower, read-only responsibility that does not overlap with any raw-SQL repository's writes or business queries. Transaction ownership: none of these functions commit or mutate; they are pure reads.

**Recommendation:** **retain both with explicit bounded responsibilities and rename/document them** — not consolidation, not removal. Specifically:
- Rename the directory or add a module docstring making explicit that `backend/infra/db/repositories/` is the ORM-based, read-only onboarding-readiness-check layer, distinct in kind (not just location) from the raw-SQL business-repository layer.
- Update `CLAUDE.md`'s architecture table to list both, with their distinct responsibilities, rather than implying a single repository layer — this closes the ambiguity that made `01-002` a genuine open question for three stages.

**Risk of consolidation:** low value, moderate risk — converting these 6 functions to raw SQL would touch 3 onboarding modules for no functional gain, and mixing ORM-style existence checks into the raw-SQL layer's style would reduce clarity rather than increase it. Retaining-with-documentation is the lower-risk, higher-value option.

**Dependency classification:** independently safe cleanup (documentation-only change; no code path affected).

---

## 3. Legacy executor and fallback options (`01-004`)

**Re-verified this stage:** the empty-`component_metadata` fallback is reachable from the **live production route** (`POST /{workspace_id}/payroll/run`), not merely from "old CLI callers" as `executor.py`'s own comment claims — this is a documentation/comment inaccuracy worth correcting regardless of which option is chosen below. `component_metadata` becomes empty only when the platform-level `component_metadata` table has zero active rows for a country, or a workspace has disabled every configured component via overrides.

Stage 11's live query found this fallback firing on 9.3% of runs in the dev database — but the dev database is independently confirmed (memory: test-harness workstream) to be drifted from migration truth in several ways, including manually-flipped `component_metadata.is_active` rows. **This stage cannot confirm whether 9.3% is representative of production** — it may be substantially lower (or higher) in a correctly-seeded environment. This uncertainty is material to the decision below and is stated explicitly rather than silently assumed either way.

**Options, with consequences:**

| Option | Consequence |
|---|---|
| (a) Retain with explicit contract and telemetry | Lowest immediate risk; requires renaming/clarifying the misleading "old CLI callers only" comment, and (per Stage 10's approved design) giving the fallback a stable `event_code` rather than the current string-matched `'legacy_executor_fallback'` step name. Does not resolve whether firing this often is itself a configuration defect. |
| (b) Hard-fail on empty metadata | Highest correctness signal — would surface a misconfigured workspace/country immediately instead of silently degrading to a code path that produces no `component_trace_jsonb`. Risk: if any current production workspace legitimately relies on this fallback (unconfirmed, see above), this would break live payroll runs for that workspace without warning. |
| (c) Migrate legacy configuration then remove | Requires first confirming which workspaces (if any) in production actually depend on empty `component_metadata`, and populating their configuration before removing the fallback. Highest effort, cleanest end state. |
| (d) Retain only for historical replay, not new runs | Preserves the ability to recompute/audit old runs that used this path historically, while forcing all new runs through the sequential executor. Requires a way to distinguish "new run" from "historical replay" at the call site, which does not currently exist. |

**Resolved at Stage 12 close: option (c), migrate legacy configuration then remove — as a phased disposition, not an immediate hard-fail:**

1. Retain the fallback temporarily.
2. Add explicit telemetry using Stage 10's stable event-code design.
3. Inventory every environment/workspace that reaches the fallback.
4. Classify each occurrence as missing seed/configuration, deliberately disabled metadata, or a legitimate historical dependency.
5. Migrate/repair configuration for every active workspace.
6. Prove new-run fallback usage is zero over an agreed observation window.
7. Change new payroll runs to hard-fail on empty active component metadata with an actionable configuration error.
8. Remove the default fallback path after verification.

Historical-replay support must not keep the fallback active for new runs — if a genuine historical-replay requirement is confirmed, it must be isolated behind an explicit replay-only path or compatibility mode with its own telemetry, not the default run-creation path.

**Rationale:** immediate hard-fail (option b) is unsafe because actual production dependency is unknown; permanent retain-and-telemetry (option a) leaves a silent-degradation path in place indefinitely and continues masking invalid configuration; replay-only (option d) is not currently implementable because no new-run/historical-run distinction exists; migration-then-removal gives the cleanest target state while allowing dependency discovery and a controlled transition.

**Stage 13 acceptance criteria for this programme:**
1. The misleading "old CLI callers" comment is corrected immediately, independent of the rest of the phasing.
2. Fallback invocations use a stable event code and include workspace/run/country context.
3. A production-environment inventory is completed before any behaviour change ships.
4. Every active workspace has non-empty effective component metadata after migration.
5. Automated tests cover: correctly-configured workspaces using the sequential executor; empty metadata producing an actionable hard failure for new runs post-cutover; historical-replay compatibility only if explicitly retained; fallback telemetry during the transition period.
6. The removal/hard-fail cutover has a rollback plan.
7. No claim of removal readiness is made from dev-database percentages alone — Stage 11's 9.3% figure must not be cited as production evidence for step 6's observation window.

**Dependency classification:** resolved — phased programme carried to Stage 13, not a simple independently-safe cleanup item (spans telemetry, inventory, migration, and a behavioural cutover).

---

## 4. Snapshot dead-field and extraction-consolidation assessment (`05-002`, `05-003`, `05-005`)

- **`05-002`** (`employee_contract_snapshot.components_jsonb`) — re-verified dead (zero readers), unchanged across three stages of scrutiny. **Recommendation: safe dead-column removal.** No behavioural dependency found; removal requires only a migration dropping the column (with the standard guard/downgrade pair) and no application code change, since nothing reads it.
- **`05-003`** (`payroll_result.salary_inputs_snapshot`) — re-verified still write-only, but its migration docstring states an intended future audit-surface purpose distinct from `05-002`'s case. **Recommendation: retain intentionally**, not a cleanup candidate — flagged only so a future stage doesn't rediscover it as "another dead column" without checking this distinction.
- **`05-005`** (duplicated statutory-rate extraction) — **confirmed still fully live** after the `04-001` remediation shipped; the remediation changed *where* `rules_jsonb` comes from (frozen snapshot instead of a live query) but did not consolidate the *parsing* of that dict into a shared function. **Recommendation: extract a single pure helper**, e.g. `extract_statutory_rates(rules_jsonb: dict) -> StatutoryRates` (dataclass or dict), called identically from both `payroll.py`'s original-run path and `payroll_retry_service.py`'s retry path. This is low-risk (pure function, no I/O, no transactional semantics to reconcile) and directly reduces the risk of a third occurrence of `04-001`'s defect class (a future statutory field added to one extraction site but not the other).

**Dependency classification:** `05-002` — independently safe cleanup; `05-003` — retain intentionally; `05-005` — independently safe cleanup, low risk given its pure-function nature, but recommend bundling with the next sprint that touches either extraction site rather than a standalone migration-free PR, so the change is reviewed in context.

---

## 5. Legacy/superseded route removal matrix (`06-007` / `09-002`)

| Route | Reachable | Frontend caller | Script/test caller | Security risk | Canonical replacement | Removal prerequisite |
|---|---|---|---|---|---|---|
| `GET/POST /payroll/run/{run_id}/reconcile` (legacy, unscoped) | yes (reconfirmed live, Stage 11) | none found | none found | insecure/tenant-bypass (`06-007`, `09-002`) | `/{workspace_id}/payroll/runs/{run_id}/reconciliation` family | Stage 09's authentication/RBAC work must land first, or removal is safe *sooner* than that — since it has zero callers, it could be deleted today with no functional loss **once Stage 09/13 confirms no external/undocumented integration depends on it**. This is the one route in this set that could plausibly be removed *before* full auth lands, purely on dead-code grounds, independent of the security fix. |
| `POST /payroll/run/{run_id}/retry`, `/approve`, `/lock`, `/pay` (unscoped) | yes | **yes** — these are the live, actively-used lifecycle-transition routes | yes (existing test suite) | insecure (`09-002`), but **no scoped replacement route exists** | none yet — would require a new `/{workspace_id}/payroll/runs/{run_id}/{action}` family plus frontend rewiring | Per this stage's own constraint, these must **not** be recommended for removal without a secure replacement — they require security redesign (Stage 13, sequenced after Stage 09's auth work), not simple deletion. Recorded here only to distinguish them sharply from the legacy reconcile pair above, which has no such dependency. |
| `/admin`, `/admin/onboarding`, `/admin/payroll` | yes | n/a (server-rendered) | none found | unauthenticated operator surface (`09-007`) | none — no scoped admin route exists yet | Blocked by Stage 09's auth/RBAC work; not a deletion candidate, a security-redesign candidate (these dashboards likely have legitimate operator value once behind auth). |
| `GET /{workspace_id}/payroll/ops/legacy-executor-stats` | yes | not confirmed this stage | none found | discloses global cross-tenant data (`09-006`) | needs a genuinely workspace-filtered version | Blocked by Stage 09's auth work for the tenant-scoping half; the query itself could be fixed to accept and use a real filter independent of auth (a Stage 10-adjacent, lower-risk fix), but doing so without auth still leaves the route open to any caller supplying any workspace_id — low value until auth exists. |

**Key distinction this stage adds:** the legacy reconciliation route pair (`06-007`) is the **only** route in the entire unscoped-route family with zero callers and a fully-formed, already-shipped replacement — making it the one genuine "just delete it" candidate once cross-checked for undocumented external integrations. Every other unscoped route in `09-002`'s family is still load-bearing (has real frontend callers) and requires a security redesign, not a deletion, to close.

**Dependency classification:** legacy reconcile pair — independently safe cleanup (pending a final external-integration check, recommend as a Stage 13 quick-win ahead of the full auth work); retry/approve/lock/pay/admin/legacy-stats — blocked by security architecture.

---

## 6. Trace literal/event-taxonomy consolidation plan

Stage 10 already specified the target taxonomy (`event_code` values like `RUN_STATUS_TRANSITIONED`, `RETRY_INVOCATION_STARTED`, etc.) and an additive-only versioning rule. This stage's simplification-specific addition is the **migration path for existing literals**, not a new design:

- **Current state:** 9 free-text `step_name` values are scattered across 3 files (`payroll_run_service.py`, `payroll_run_persister.py`, `run_executor.py`) as inline string literals, plus one already-informally-stable string (`'legacy_executor_fallback'`) that `get_legacy_executor_stats()`'s SQL query depends on via string comparison.
- **Consolidation approach:** one canonical constants module (e.g. `backend/domain/payroll/trace_events.py`) defining every `event_code` as a named constant, with a separate mapping of `event_code → human_readable_label` for display purposes — decoupling the stable machine code from the human-facing string, which today are the same literal doing both jobs.
- **Legacy step-name mapping:** a single dict literal mapping each of the 9 existing free-text names to its new `event_code`, used only during the migration backfill (Stage 10 §14) — not a permanent runtime lookup.
- **`legacy_executor_fallback` statistics:** `get_legacy_executor_stats()`'s query must be updated to filter on the new `event_code` column instead of `step_name` string-matching, once the migration lands — this is a one-line query change, not a design change, and should be bundled with Stage 10's migration implementation rather than done separately.
- **Scattered string comparisons:** none found beyond the one query above — the free-text `step_name` values are otherwise write-only from the trace-producing side (no other code branches on their exact string value).

**Dependency classification:** blocked by Stage 10 trace implementation — this consolidation cannot happen before the schema migration Stage 10 designed exists; recorded here so the implementation work has a ready-made "what to consolidate" list rather than rediscovering it.

---

## 7. Backend/frontend enum and contract duplication register

| Concept | Backend source of truth | Frontend representation(s) | Drift found |
|---|---|---|---|
| Payroll run status | `backend/domain/payroll/status.py`'s `PayrollRunStatus` enum (8 values: DRAFT, FAILED, CALCULATING, CALCULATED, PARTIAL, APPROVED, LOCKED, PAID) | **Two separate frontend types, both named `PayrollRunStatus`:** (1) `frontend/src/types/payroll.ts:1-8` (7 values, **missing `FAILED`**, used to type the actual `PayrollRun.status` API field); (2) `frontend/src/design-system/components/Status.tsx:27-35` (8 values, but uses **`'PENDING'` instead of `'DRAFT'`**, not matching the backend at all) | **Confirmed, new finding this stage.** Neither frontend type is a correct mirror of the backend enum, and they disagree with each other. See detailed analysis below. |
| Reconciliation status | DB CHECK constraints (`MATCHED`/`MISMATCH`/`RESOLVED`) | `types/payroll.ts`, `Status.tsx` (`ReconciliationStatus = 'MATCHED' \| 'MISMATCH' \| 'RESOLVED'`) | Not independently re-verified for exact value parity this stage; no drift found by inspection, lower priority given no active defect symptom |
| Retry strategy | `payroll_run.retry_strategy` CHECK constraint, single allowed value `'PER_EMPLOYEE'` (`FULL_RUN` permanently disabled) | Not found hardcoded as a frontend enum/type — appears to not be surfaced as a user-facing choice, consistent with only one value being legal | No duplication risk — single-value constraint, nothing to drift |
| Component class | `component_class` column values (`standard`, `non_taxable`, `paye_addition`) | No hardcoded frontend type/list found | No duplication found |

### `PayrollRunStatus` duplication and drift — detailed finding

- **current implementation:** Two independently-maintained TypeScript type declarations both named `PayrollRunStatus`, in different modules, each incompletely/incorrectly mirroring the 8-value backend enum. `frontend/src/pages/PayrollRuns.tsx:307` renders `<StatusBadge status={run.status} />`, passing a value typed by `types/payroll.ts`'s (FAILED-missing) type into a component whose own prop type comes from `design-system/components/Status.tsx`'s (PENDING-instead-of-DRAFT) type — the mismatch is currently masked because `StatusBadge`'s actual prop type (`BadgeVariant`) is a wide union across multiple status-type members, and `'DRAFT'` happens to already be a valid `BadgeVariant` via `WorkspaceStatus`'s own `'DRAFT'` member, so TypeScript does not currently reject passing a real `DRAFT` run status through, even though the payroll-specific sub-type technically says `'PENDING'`.
- **intended behaviour:** one canonical status representation should exist per concept, ideally derived from (or checked against) the backend enum, not hand-duplicated in two frontend locations that can silently diverge, as they already have.
- **suspected or confirmed defect:** confirmed duplication and confirmed drift in both directions (one file is missing a real value, the other has a value the backend has never sent). This is a **root-cause-level explanation, not just a restatement,** of `06-001`/`06-004` (FAILED status not surfaced in the frontend, Stage 06): the canonical type used to type the actual API response field structurally cannot express `FAILED` without a cast, which is exactly the kind of gap that produces "the UI silently doesn't handle this status" bugs.
- **evidence:** `evidence/01-key-greps.txt` (full citations); `frontend/src/types/payroll.ts:1-8`; `frontend/src/design-system/components/Status.tsx:27-35`; `frontend/src/pages/PayrollRuns.tsx:307`.
- **status:** confirmed
- **severity:** S2 (contract-drift correctness risk with a demonstrated real consequence — `06-001`/`06-004` — not merely a hypothetical maintainability concern)
- **related invariant:** none pre-existing; recommend a new one: "frontend status/enum types mirroring a backend enum must be defined exactly once and kept in lockstep, ideally via a generated or shared-contract mechanism, not hand-duplicated."

**Recommendation:** consolidate to one `PayrollRunStatus` type (retain the `types/payroll.ts` location, since it types the actual API field), add `'FAILED'`, and either remove `design-system/components/Status.tsx`'s duplicate declaration (importing the canonical one instead) or fix its `'PENDING'` → `'DRAFT'` mismatch if a separate declaration is kept for design-system-package-boundary reasons. This should be **bundled with `06-001`'s remediation** (the frontend work to actually surface `FAILED` runs), not done as a separate standalone type-cleanup PR, since fixing the type without also building the UI to handle `FAILED` would leave the type correct but the behaviour still incomplete.

**Dependency classification:** cleanup bundled with remediation (`06-001`/`06-004`'s Stage 13 entry).

---

## 8. Business-rule/helper duplication register

| Duplicate logic | Locations | Assessment |
|---|---|---|
| Statutory-rate extraction | `payroll.py:263-280`, `payroll_retry_service.py:184-197` | Identical and consolidatable — see §4 (`05-005`) |
| Workspace/run ownership checks | Present correctly in `employee_repo.py`, `_guard_locked_or_paid`; **absent** in the reconciliation/timeline/stats service functions (`09-004`/`09-005`/`09-006`) | Not a duplication problem — an *absence* problem, already fully specified by Stage 09/10's remediation design; not re-litigated here |
| Error-to-HTTP translation | 34 `except Exception`/`except ValueError` sites across `backend/api/routes/*.py` (confirmed count this stage) | Already fully classified by Stage 09's `07-001` Group A/B/C analysis (10 structurally unsafe, 11 currently safe); a shared "safe exception translator" helper is a plausible consolidation, but `CLAUDE.md`'s own standing rule already prescribes the correct per-site behavior (log raw, return generic) — a helper would reduce repetition but is not required for correctness. Recommend as a Stage 13 quick-win alongside the `07-001` fix itself, not a separate cleanup. |
| Export row construction | Bank-upload/PAYE/pension/full-detail exports (`payroll.py:1455-1679`) | Not independently re-verified for duplication this stage; each export has a distinct column set, so full consolidation may not be appropriate — flagged as "requires closer look," not classified either way |
| Audit/event creation | `payroll_run_persister.py`'s "Save N audit entries"/"Save N events" steps | Single call site for original runs; retry has **no** equivalent call (already covered by Stage 10's design, which adds this as part of the approved trace package) — not a duplication problem, an absence already scheduled for remediation |
| Retry/original calculation context construction | `_build_shared_context` (retry) vs. inline construction in `payroll.py`'s run-creation route | Overlapping purpose but different lifecycle semantics (one reconstructs context for a subset of employees against a frozen snapshot, the other builds it fresh for all employees) — **not recommended for consolidation**, per this stage's own rule against merging code paths with different snapshot/lifecycle semantics |

**Dependency classification:** `05-005` — independently safe cleanup (§4); error-to-HTTP helper — cleanup bundled with `07-001`'s remediation; export row construction — requires further investigation (not classified); retry/original context construction — retain intentionally (different semantics).

---

## 9. Frontend dead-code/contract-drift register

- **`PayrollRunStatus` duplication/drift** — see §7, the primary finding of this investigation area.
- **No components found that always return `null`** in the files reviewed this stage beyond the already-known `ActionPanel` fall-through-to-`null` for `FAILED` runs (`06-004`, unchanged, not re-classified as a new dead-code finding since it's already a confirmed defect, not a simplification candidate).
- **No unused legacy admin/debug UI found** in `frontend/src` beyond the backend's own `/admin*` server-rendered pages (§5), which are not frontend React code and are already covered under route cleanup.
- **Deferred Stage 13 UI work** (e.g. the `timesheet/audit/{employee_id}` missing UI feature from `06-006`) is explicitly **not** classified as dead code here, per this stage's own instruction.

**Dependency classification:** the `PayrollRunStatus` finding — cleanup bundled with remediation (§7); no other frontend dead-code candidates identified with sufficient evidence this stage to classify further — recorded as not-exhaustively-investigated rather than "none exists."

---

## 10. Logging/debug/diagnostic cleanup register

| Item | Classification |
|---|---|
| `paye.py:11` module-level `print()` (`07-004`) | remove now — trivial, zero-risk, one-line change |
| `backend/scripts/test_*.py` (6 files, misleadingly named) | move to test/evidence tooling or rename — these are manual DB-writing verification scripts predating the pytest suite, now fully superseded by it (Stage 11: 306 passing tests cover calculation/persistence/export paths these scripts exercise manually). Recommend renaming with a non-`test_`-prefixed name (e.g. `manual_verify_*.py`) to stop the visual confusion with the real test suite, and adding a short header comment noting they are superseded manual tools, not regression tests. Not a "remove now" because they may still have ad hoc debugging value, but their current naming actively misleads. |
| `backend/scripts/load_*.py`, `backfill_rule_set_snapshots.py`, `simulate_payroll.py` | retain as operational diagnostic — legitimate one-off data-loading/simulation utilities; `simulate_payroll.py`'s lack of a proration step is a pre-existing known gap (memory: `project_simulation_scripts_no_proration`), not a Stage 12 cleanup item |
| Duplicate logging of the same exception | Not found as a distinct pattern this stage beyond the already-classified `07-001` sites (which log-then-translate, not duplicate-log) |
| Diagnostic endpoints superseded by tests | `GET /{workspace_id}/payroll/ops/legacy-executor-stats` is not superseded — it remains the only source of this specific aggregate, not redundant with any test |
| Stale developer comments | `executor.py:109-111`'s "old CLI callers" comment is confirmed stale/inaccurate (§3) — should be corrected regardless of which fallback option Stage 13 chooses |

**Dependency classification:** `paye.py` print — independently safe cleanup; `backend/scripts/test_*.py` rename — independently safe cleanup (naming-only, zero behavioural risk); stale comment correction — independently safe cleanup (bundle with §3's eventual fallback decision, since it touches the same code).

---

## 11. Migration hygiene register

- **Swallow-all `EXCEPTION WHEN others` pattern:** confirmed bounded to exactly two migrations — `c9d0e1f2a3b4` (upgrade path, `08-001`'s root cause) and `f9a0b1c2d3e4` (downgrade path only, already noted by Stage 08 as lower-risk since downgrades rarely run in production). No other migration in the full `migrations/versions/` tree uses this pattern.
- **Per this stage's explicit caution** (`08-001` as the primary example): any future migration hygiene pass must replace `EXCEPTION WHEN others` with a precise, narrower guard (e.g. `EXCEPTION WHEN duplicate_column THEN NULL` for ADD COLUMN, or an explicit pre-check for `SET NOT NULL`), never with a broader suppression — this is a corrective direction for `08-001`'s eventual fix, not a general rewrite recommendation for the rest of the migration history, which was not found to share this defect.
- **Migrations whose name/docstring no longer matches actual schema outcome:** `c9d0e1f2a3b4_employee_number_not_null.py` is the clearest example — its own name promises a `NOT NULL` constraint it does not actually enforce, due to the swallowed exception. Recommend the eventual corrective migration also update or superseding-reference this file's docstring so the name/outcome mismatch doesn't persist even after the constraint is properly enforced by a new migration.
- **Duplicate compatibility guards, dead downgrade branches, repeated helper patterns, multiple migrations implementing the same final constraint:** not found as distinct issues beyond the two files above, within the scope of this stage's review depth (a full line-by-line audit of every migration file was not performed given the size of the migration history and the absence of any specific prior-stage handoff pointing to a broader problem here).

**Dependency classification:** both swallow-all migrations — cleanup bundled with `08-001`'s remediation (the corrective migration is the natural place to also fix the docstring mismatch); no independent migration-hygiene cleanup found warranting separate action.

---

## 12. Documentation authority/staleness register

- **`docs/wrapper-command/`** — already resolved (decision 01-013): non-authoritative, `CLAUDE.md` is the sole governing source. No further action needed beyond what's already recorded; not re-litigated.
- **`executor.py`'s "old CLI callers" comment** — confirmed stale/inaccurate this stage (§3, §10); the fallback is reachable from the live production route.
- **`c9d0e1f2a3b4`'s migration docstring** — confirmed to overstate what the migration achieves (§11).
- **Completed audit-stage `CONTEXT.md`/`findings.md` files (Stages 01–11)** — these are historical record, not active operational instructions; no authority conflict found (they are self-contained per-stage documents, not referenced by application code or `CLAUDE.md` as runtime instructions). No archival action recommended — the audit programme's own structure already distinguishes historical stage output from `CLAUDE.md`'s live rules.
- **No other contradictions with `CLAUDE.md` found** within this stage's review depth.

**Dependency classification:** both stale comments/docstrings — cleanup bundled with their respective remediations (§3, §11); `docs/wrapper-command/` — already resolved, no action; audit-stage historical docs — retain as-is, no authority conflict.

---

## 13. Dependency-aware cleanup sequence

| Candidate | Classification |
|---|---|
| Rename/document `backend/infra/db/repositories/` (§2) | independently safe cleanup |
| Remove `employee_contract_snapshot.components_jsonb` (`05-002`) | independently safe cleanup (requires a migration, but no application code change) |
| Extract shared statutory-rate-extraction helper (`05-005`) | independently safe cleanup, low risk |
| Remove `paye.py:11` print() (`07-004`) | independently safe cleanup |
| Rename `backend/scripts/test_*.py` | independently safe cleanup |
| Correct `executor.py`'s stale "old CLI callers" comment | independently safe cleanup (bundle with §3's decision) |
| Legacy unscoped reconciliation route removal (`06-007`) | independently safe cleanup, pending a final external-integration check — the one genuine quick-win in the security-adjacent route family |
| Legacy executor fallback disposition (§3) | resolved — phased migrate-then-remove programme, carried to Stage 13 |
| Fix `PayrollRunStatus` duplication/drift (§7) | cleanup bundled with remediation (`06-001`/`06-004`) |
| Error-to-HTTP shared helper | cleanup bundled with remediation (`07-001`) |
| Correct `c9d0e1f2a3b4` docstring | cleanup bundled with remediation (`08-001`) |
| Trace event-code consolidation (§6) | blocked by Stage 10 trace implementation |
| Unscoped retry/approve/lock/pay/admin/legacy-stats routes | blocked by security architecture (Stage 09) |
| `03-004` statutory-disablement mechanism/guard | retain intentionally until Stage 13's policy decision |
| `payroll_result.salary_inputs_snapshot` (`05-003`) | retain intentionally |
| `backend/scripts/load_*.py`, `simulate_payroll.py`, `backfill_rule_set_snapshots.py` | retain intentionally (operational diagnostics) |
| Export row construction duplication | requires further investigation, not yet classified |

---

## 14. Positive-control register — apparently duplicate structures that are intentionally distinct

- **Two repository directories** (§2) — not a defect once documented; genuinely distinct responsibilities (raw-SQL business layer vs. ORM-based onboarding-readiness reads).
- **`05-003` vs. `05-002`** — both are write-only columns, but only one (`05-002`) is dead; `05-003` has a stated future purpose and must not be treated identically.
- **Retry vs. original-run context construction** — overlapping purpose, deliberately different lifecycle semantics (frozen-snapshot subset vs. fresh full-workspace build); correctly not consolidated.
- **Retry strategy's single legal value** (`PER_EMPLOYEE`) — not a duplication risk since `FULL_RUN` is DB-permanently-disabled and never represented as a live frontend choice.
- **`component_class` values** — not duplicated in the frontend as a hardcoded list; no drift risk found.

---

## Handoff to Stage 13

Stage 13 should sequence this stage's output as follows, using the dependency classification in §13 as the primary organizing structure:

1. **Immediate, independently-safe items** (no remediation dependency): rename/document the ORM repository layer; remove the dead snapshot column; extract the shared statutory-extraction helper; remove the stray `print()`; rename the misleadingly-named scripts; correct the two stale comments/docstrings; remove the legacy unscoped reconciliation route pair (pending a final external-integration check).
2. **Bundle with existing remediation items:** the `PayrollRunStatus` frontend fix bundles with `06-001`/`06-004`'s Stage 13 entry; the error-to-HTTP helper bundles with `07-001`'s fix; the `c9d0e1f2a3b4` docstring correction bundles with `08-001`'s corrective migration.
3. **Resolved legacy-executor fallback programme (§3):** migrate-then-remove, phased across 8 steps with 7 Stage 13 acceptance criteria — not a simple independently-safe item, spans telemetry, production inventory, configuration migration, and a behavioural cutover with a rollback plan.
4. **Structurally blocked, not simplification candidates:** the unscoped retry/approve/lock/pay/admin/legacy-stats routes (blocked by Stage 09's security architecture) and the trace event-code consolidation (blocked by Stage 10's unimplemented migration) — Stage 13 should not schedule these as "simplification" work; they are security/observability remediation that happens to also simplify code as a side effect.
5. **Retained intentionally, no action:** `05-003`, `03-004`'s mechanism, the operational diagnostic scripts, the retry/original-run context construction, `docs/wrapper-command/`.
6. **Not yet classified, needs further investigation:** export row construction duplication across the four export types.

## Human decisions

No decision remains open at close. The one human decision raised during the initial investigation (§3 — legacy executor fallback disposition) was resolved at Stage 12 close: **migrate legacy configuration, then remove the fallback for new payroll runs**, as an 8-step phased programme (§3), not an immediate hard-fail. Recorded as resolved in `_core/human-decisions.md`.

---

## Stage 12 close — final review and closure summary

No new human decision was required to close Stage 12 beyond resolving the one raised during the initial investigation. All review conclusions in the CONTEXT.md close-review instruction are confirmed against this document's own evidence, with no revision:

- Repository layers are intentionally distinct — rename/document the ORM onboarding-readiness layer (§2), not consolidation.
- `employee_contract_snapshot.components_jsonb` is a safe dead-column removal candidate (§4, `05-002`).
- `payroll_result.salary_inputs_snapshot` is retained intentionally (§4, `05-003`).
- Statutory-rate extraction should become one shared pure helper (§4, `05-005`) — confirmed still fully live post-`04-001`.
- The stray `paye.py` module-level `print()` should be removed (§10, `07-004`).
- The six `backend/scripts/test_*.py` utilities should be renamed/manually labeled, not silently deleted (§10).
- The legacy unscoped reconciliation GET/POST pair is a removal quick-win after a final undocumented-external-integration check (§5, `06-007`).
- Unscoped retry/approve/lock/pay routes and admin/diagnostic surfaces require security redesign, not deletion (§5).
- Frontend `PayrollRunStatus` duplication/drift is confirmed and should be fixed alongside `06-001`/`06-004` (§7).
- Error-to-HTTP consolidation belongs with `07-001`'s remediation (§8).
- Trace literal consolidation belongs with Stage 10's implementation (§6).
- Migration comment/docstring cleanup belongs with `08-001`'s remediation (§11).
- `03-004` remains open and unchanged — not resolved by this stage, per its own constraint.

### Carried to Stage 13

All independently-safe cleanup items, bundled-cleanup items, blocked items, retained-intentionally items, and the phased legacy-fallback programme (§3, with its 7 acceptance criteria) carry to Stage 13 exactly as classified in §13 and the Handoff section above. No item's classification changed at close review.
