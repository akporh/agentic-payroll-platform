# Stage 10 Output: Standing Assurance Controls (Q3)

Which verification artifacts are **permanent CI gates**, which are **periodic reviews**, and the cadence/trigger for each — so launch evidence stays true over time instead of decaying into point-in-time claims. Grounded in the repo's real CI (fresh-DB pytest + frontend typecheck on push/PR, no schedule seam — F-10-02, evidence file §1).

## 1. Classification model (DEC-10-07)

| Class | Definition | Runs |
|---|---|---|
| **A — permanent CI gate** | Committed test in the default suite; red blocks merge/push (pre-push hook + CI) | Every push/PR |
| **B — triggered/scheduled job** | Scripted job outside the default suite (cost, network, or nondeterminism) | On defined triggers + schedule |
| **C — periodic scripted review** | Bounded human review over scripted output | Calendar cadence |
| **D — event-triggered inspection** | Dated record captured when a named event occurs | On event |

Class A is the default; a control is only placed lower with a stated reason. Anything that *can* be a deterministic committed test *must* be (this is why Stage 07 made the isolation test route-table-generated: the platform's decorative-scoping habit is empirically recurrent — five routes across two rounds, F-05-03/F-07-01 — so hand-enumerated checks are assumed to decay).

## 2. Class A — permanent CI gates

All run against CI's fresh `alembic upgrade head` database (standing rule). Each enters CI with its named build item and never leaves.

| Control | Gate/hook it keeps closed | Enters with |
|---|---|---|
| Route-enumeration auth test (generated from `app.routes`) | CG-1/SG-1/T4 — "100% of routes authenticate" stays true for every future route | C1 |
| Route-table isolation test (mismatched token + cross-workspace 404 per `{workspace_id}` route; allowlist asserted) | SS-1; F-05-03/F-07-01 cannot recur silently | C1 + remediations |
| R1 grep-clean check (caller-supplied actor inputs) | CG-1/R1 — prevents parallel actor-path drift | C1 |
| Token tamper/expiry/revocation; membership negative paths; step-up freshness/single-consumption | SG-1/T1-T5 | C1 |
| Epoch-labelling fixture test | CG-1; audit threat model §6 | C1 |
| Forced-failure outbox atomicity; per-event emission; advisory-lock single-worker; consumer idempotency | CG-2/SG-2 | C2 |
| Append-only UPDATE/DELETE rejection per protected table | SS-3/F-06-03 | C2 |
| Exception-workflow end-to-end (create→…→close, audit row per transition) | CG-7 dependency; D-04-01 | C2 |
| Tool-registry uniformity + per-tool negative-path + wrapper-independence + fail-closed | SC-2/SS-2; Condition 14 for every future tool | Tool layer |
| Serialization property tests (Decimal-as-string; no PII field names; numeric-token provenance for C5) | SG-2; CG-5 | Tool layer |
| Session-registry set-equality per capability | SS-4 | Each capability launch |
| C10 protocol tests (CAS double-confirm, invalidation, conflict, terminal-record fields, payload freeze) | CG-10/SG-10; DQ-002 | C10 |
| C12 mechanism tests (validator, origin-equivalence, step-up rejection matrix, correction recoverability, date-driven resolution check) | CG-12/SG-12 | C12 |
| C14 non-mutation + equivalence + hash-gate + non-consumption tests | CG-14/SG-14; DQ-003/004 | C14 |
| C7 determinism + formula fixtures + shadow-exclusion + threshold-versioning tests; no-LLM-import check | CG-7/SG-7 | C7 |
| Invariant-named regression tests (existing 328-test suite + every remediation's named test) | Standing repo rule; remediation rows (register §4) | already live / per fix |
| Frontend component tests for the automatable UX behaviours | Stage 09 behaviours (disposition in `ux-verification-plan.md`) | Frontend harness (with C1) — F-10-01 prerequisite |
| Chain-linkage fixture assertions (linkage fields NOT NULL + resolvable, per mechanism) | Stage 08 assurance input 1 | Each mechanism's build |

## 3. Class B — triggered/scheduled jobs

| Control | Why not Class A | Triggers | Artifact |
|---|---|---|---|
| LLM eval suite (`llm-evaluation-framework.md`) | API cost, network, nondeterminism | Model/prompt/contract change; incident; quarterly; capability launch | ET-4 eval report, committed |
| Chain-completeness sweep (`evidence-chain-and-baselines.md` Part A §2 — the six orphan queries) | Runs against the deployed/production database, not fixtures | Each production release; monthly | Dated sweep record; zero-orphan assertion; nonzero → incident + exception record |
| Calibration report (C7 three metrics + dismiss-without-review) | Production data query | Per payroll cycle during shadow/early GA, then quarterly (`calibration-governance.md` §3) | Committed calibration report |

First Class B control to land adds the missing `schedule:`/`workflow_dispatch:` CI seam (F-10-02) in the same build item.

## 4. Class C — periodic scripted reviews

| Review | Content | Cadence |
|---|---|---|
| SS-4 conformance review | The set-equality tests (Class A) prove registry == approved list in code; this review checks the *approved lists themselves* still match the capability matrix and D-03-01 conditions — drift between document and constant is what no functional test catches (Stage 07 handoff §2) | Quarterly |
| PII-sanitizer ruleset currency | Ruleset reviewed against current tool outputs/schema additions; version bumped if rules change (which triggers eval re-run, framework §6) | Quarterly |
| Production refusal-record sample | ~20 `REFUSED`/refusal-class records reviewed against outcome classes (framework §3.3); interesting cases promoted to corpus | Monthly (LLM capabilities live) |
| Isolation control statement currency | The ET-5 statement re-checked: tables/enforcement points current; it must still cite the route-table test as standing proof | Each release that adds routes/tables |
| Residual-risk register review | Per `residual-risk-register.md` §4 | Annually + triggers |
| Evidence-register currency | Register rows vs reality spot-check (are cited tests still present/green) | Each sprint close touching a gated capability (the "done" rule, register §5) |

## 5. Class D — event-triggered inspections

| Inspection | Event | Record |
|---|---|---|
| CORS origin pinning (SG-1/F-07-03) | C1 launch; any deploy touching CORS/env config | Dated deployed-config record |
| DB role/privilege review (supports RR-2, append-only floor) | Any infrastructure change (new DB principals, provider migration) | Dated record |
| No-purge design-absence re-check (SC-4/DQ-008) | Every migration review touching audit/evidence tables — added to the repo's standing `/arch-council` migration checklist at Phase 3 adoption | Review note in the sprint record |
| Epoch integrity (single `auth_cutover_epoch` value, unchanged) | Any migration touching `platform_metadata` | Covered by Class A fixture test + migration review note |

## 6. Ownership and operating reality

Single operator (the platform operator) owns every cadence; all Class B/C items are scripted so each is a bounded session (< 1 hour), and every one produces a committed artifact — if it isn't committed, it didn't happen (the same evidence discipline this programme runs on). Calendar total in steady state: one monthly session (refusal sample + sweep when due), one quarterly session (SS-4 + PII + eval refresh), plus event-triggered items. This is the deliberate ceiling — a cadence that assumes more operator time than exists is an assurance fiction.
