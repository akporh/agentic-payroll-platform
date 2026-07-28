# Stage 10 Output: Launch-Gate Evidence Register (Q1)

One auditable register: for every CG/SG/SS gate row and every Stage 08 mechanism hook, the **concrete closure-evidence artifact** that makes "done" checkable rather than asserted. Phase 3 build items close gates only by producing the named artifact; this register is the checklist Stage 13 sequences against and Phase 3 marks off.

Gates themselves are fixed (Stage 06/07 registers, binding); this register adds evidence form only — nothing here weakens, waives, or re-scopes any gate.

## 1. Evidence-type taxonomy (DEC-10-01)

Every evidence artifact in this register is one of six types:

| Type | Definition | Standing form |
|---|---|---|
| **ET-1 committed test** | A named test in the repo suite, green in CI against the fresh-DB build (`alembic upgrade head` — standing rule). Named for the invariant/gate it protects. | Permanent CI gate (Class A, `standing-assurance-controls.md`) |
| **ET-2 design-absence check** | A recorded verification that a mechanism does **not** exist (no purge path, no peer-comparison code, no LLM in a detection path) — grep/enumeration sweep committed as a test where mechanizable, otherwise a dated review note in the build item's close-out | Re-checked on migration/`/arch-council` review (Class D) |
| **ET-3 deployed-config inspection** | A dated record of the deployed environment's actual configuration (CORS origin pinning, DB role privileges), captured at launch and on config-affecting deploys | Event-triggered (Class D) |
| **ET-4 eval report** | A committed report artifact from an LLM evaluation run per `llm-evaluation-framework.md` (corpus version, model/prompt version, pass/fail per criterion) | Re-run on defined triggers (Class B) |
| **ET-5 maintained document** | A living artifact whose currency is itself checked (isolation control statement, this register) — must cite its standing proof so it cannot drift from code | Periodic review (Class C) |
| **ET-6 measured baseline** | A dated baseline measurement artifact per `evidence-chain-and-baselines.md` Part B — captured **before** the corresponding capability launches | Point-in-time, retained |

## 2. Standing controls (apply to every capability row)

| Control | Evidence artifact | Type | Build item | Source |
|---|---|---|---|---|
| SC-1 verified identity + token-derived workspace | Route-enumeration auth test (every route authenticated or literal-allowlisted); R1 grep-clean check (no caller-supplied actor inputs); per-mutating-route audit-actor tests | ET-1 | C1 | `auth-foundation-design.md` §6; `tenant-isolation-verification-standard.md` §3.2 |
| SC-2 independent tool-layer workspace check | Tool-registry uniformity test + per-tool negative-path tests + wrapper-independence test + fail-closed startup test | ET-1 | Tool layer (with C2) | `tool-layer-security-pattern.md` §3; `tool-contracts.md` §5 |
| SC-3 agent/tool audit standard | Registry uniformity test asserting every wrapper invocation writes a `tool_call_log` row with all SC-3 fields incl. sanitizer version | ET-1 | C2 + tool layer | `event-audit-foundation-design.md` §§7–8 |
| SC-4 7-year retention floor | Design-absence check: no purge/deletion mechanism exists anywhere (DQ-008 honoured — no retention-enforcing mechanism until legal basis confirmed) | ET-2 | C2 | `event-audit-foundation-design.md` §8 ("Retained" row) |
| SS-1 two-layer tenant isolation | **Route-table-generated isolation test**: every `{workspace_id}` route gets a mismatched-token rejection + cross-workspace 404 assertion, list generated from `app.routes` at test time; unscoped-surface allowlist asserted | ET-1 | C1 + remediations | `tenant-isolation-verification-standard.md` §3.2–3.3 |
| SS-2 tool-guard wrapper pattern | Same artifact set as SC-2 (the four tests) | ET-1 | Tool layer | `tool-layer-security-pattern.md` §3 |
| SS-3 audit-store integrity | UPDATE/DELETE rejection test per protected table; forced-failure outbox atomicity test; epoch-labelling fixture test | ET-1 | C2 | `audit-integrity-threat-model.md` §7 |
| SS-4 capability-scoped tool registries | Per-capability session-registry test: session construction exposes exactly the approved minimum tool set (set equality, in CI); quarterly conformance review re-checks the approved lists against the capability matrix | ET-1 + ET-5 | Tool layer, per capability launch | `agent-layer-threat-model.md` §3.1; `standing-assurance-controls.md` §4 |

## 3. Per-capability gate evidence

Blocked/rejected/deferred rows (C4, C8, C9, C15) carry their classification as the evidence requirement — no launch evidence is definable until their status changes (C8's remediation evidence is listed because its *fixes* proceed regardless of the capability's blocked status).

### C1 — Identity & Auth Foundation (CG-1 / SG-1)

| Gate item | Evidence artifact | Type |
|---|---|---|
| 100% of routes authenticate (CG-1, SG-1/T4) | Route-enumeration auth test iterating `app.routes`; allowlist is a literal constant asserted in the test | ET-1 |
| Zero surfaces accept caller-supplied workspace identity (CG-1) | R1 grep-clean check (`X-Performed-By`, `actor_id`, actor defaults) committed as a test; per-route negative-path tests (cross-workspace → 404) | ET-1 |
| Audit actor cut-over epoch (CG-1) | Epoch-labelling fixture test (pre-epoch row renders `identity_unverified`, post-epoch row carries verified principal); epoch persisted as data (`platform_metadata`) asserted by the same test | ET-1 |
| Token claims/lifetime/revocation posture (SG-1) | Token tamper/expiry/revocation unit tests | ET-1 |
| Membership model live (SG-1) | Membership fixture test: one operator, two workspaces via separate sessions; non-member → 404 | ET-1 |
| Auth events audited (SG-1/T6) | Auth-event write asserted per auth-flow test | ET-1 |
| Step-up hook present (SG-1/T5) | Step-up freshness + single-consumption tests (mechanism exists even before C12 consumes it) | ET-1 |
| Production CORS origin pinning (SG-1/F-07-03) | Dated deployed-config inspection at C1 launch, repeated on CORS-affecting deploys | ET-3 |
| `workspace_info()` `LIMIT 1` retired or token-scoped (SG-1/F-07-02) | Committed test on the surviving form, or removal confirmed by route-enumeration test (absent = allowlist-checked) | ET-1 |

### C2 — Event/Tool/Notification Foundation (CG-2 / SG-2)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Audit writes outbox-coupled, not fire-and-forget (CG-2/SG-2/F-06-02) | Forced-failure atomicity test: audit/outbox insert failure rolls back the state change | ET-1 |
| PII sanitizer versioned, version logged (CG-2/SG-2) | Test asserting every `tool_call_log` row carries the sanitizer version constant | ET-1 |
| Untrusted strings rendered as data (SG-2) | Serialization property test (no DB string interpolated into instruction-position text) | ET-1 |
| Event completeness (Stage 05 closure) | Per-event emission tests for the four new events | ET-1 |
| Consumer discipline | Two-instance single-worker (advisory lock) test; consumer idempotency (redelivery) test | ET-1 |
| Append-only floor (SS-3) | UPDATE/DELETE rejection per protected table; step-up `consumed_by` single-transition exception test; no-purge design-absence check | ET-1 + ET-2 |
| Exception-workflow substrate (D-04-01 dependency) | Create/own/resolve/verify/close end-to-end test; domain-3 audit row per transition asserted | ET-1 |

### C3 — Operator Assistant (CG-3 / SG-3)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Tool-call logging live before first use (CG-3) | SC-3 uniformity test green for C3's five tools | ET-1 |
| Refusals logged first-class (CG-3) | Per-tool negative-path test asserts the `REFUSED` audit record | ET-1 |
| D-02-03 boundary enforced, refusals testable (CG-3) | C3 launch eval report: refusal-correctness on the historical/out-of-scope/cross-workspace corpus, ~100% bar on the historical class | ET-4 |
| Injection test set committed and passing (SG-3/T1/T2) | C3 injection corpus + eval report per `llm-evaluation-framework.md` §2/§4 | ET-1 (corpus) + ET-4 (report) |
| Session registry = five tools only (SG-3/SS-4) | Session-registry set-equality test | ET-1 |
| Rate limiting live (SG-3/W3) | Committed test or deployed-config inspection (per where limiting is implemented) | ET-1 / ET-3 |
| Support-question baseline exists pre-launch | Baseline B6 artifact | ET-6 |
| UX behaviours 1–4 verified | Per `ux-verification-plan.md` rows 1–4 | ET-1 / ET-4 |

### C4 — Historical Explanation (CG-4/SG-4): **blocked (D-02-03)** — evidence requirement = the block itself; define rows when unblocked.

### C5 — Trace Explanation (CG-5 / SG-5)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Null-trace refusal implemented and logged (CG-5) | Committed test: legacy-executor result → verbatim `TRACE_UNAVAILABLE` contract text + logged refusal; UX behaviour 1 (null-trace row) | ET-1 |
| Zero-hallucination provenance check (CG-5, doubles as SG-5/T6) | Serialization property test: every numeric token in `explain_component_trace` output exists in the source trace — code-enforced, so the committed test *is* the evidence; eval report covers narration refusal quality only | ET-1 + ET-4 |
| Trace fields logged for evidence-linking (CG-5) | SC-3 field-presence test on the C5 tool path | ET-1 |
| Session registry = `get_run_results` path only (SG-5) | Session-registry set-equality test | ET-1 |

### C6 — Readiness Service (CG-6 / SG-6)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Notifications via C2's reliable path (CG-6) | Emission test for readiness events through the outbox | ET-1 |
| Named service principal for scheduled execution (SG-6/R3) | Committed test: scheduled run's audit rows carry the service principal, never a placeholder | ET-1 |
| Time-to-detection baseline exists pre-launch | Baseline B4 artifact | ET-6 |

### C7 — Input Anomaly Detection (CG-7 / SG-7)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Exception workflow live first (CG-7, D-04-01 hard gate) | C2's exception end-to-end test green **before** C7's launch (sequencing asserted in the build order; register check: C7 row may not close before C2 row) | ET-1 (sequenced) |
| Threshold changes versioned/auditable (CG-7) | Test: threshold change creates a new version row + domain-1 audit event, prior versions retained | ET-1 |
| Shadow-mode results retained as calibration evidence (CG-7) | Shadow-mode exclusion test (INFO severity + `shadow: true`, excluded from operator counts — UX behaviour 13); calibration-metric queries return values on fixture data | ET-1 |
| Detector deterministic (SG-7/T6) | Determinism property test; formula fixtures pinning R_high/R_low/median/min-window (the 400-vs-42 worked example) | ET-1 |
| No LLM in detection path (SG-7) | Registry/import test: C7 detection path imports no LLM client; if narration ships: narration injection corpus + eval report | ET-1 (+ ET-4 if narration) |
| Calibration governance operating | Shadow-exit decision record + first calibration report per `calibration-governance.md` §§2, 6 | ET-5 |

### C8 — Reconciliation Investigation (CG-8 / SG-8): **blocked (D-02-02 + D-02-03)** — but its remediation evidence proceeds:

| Item | Evidence artifact | Type |
|---|---|---|
| Reconciliation workspace-scoping fix (F-01-33) | Cross-workspace reconciliation regression test (invariant-named) | ET-1 |
| Five decorative routes fixed (F-05-03/F-07-01) | Route-table isolation test green (SS-1) — proves the pattern dead platform-wide, not just per-route | ET-1 |
| Isolation control statement (CG-8 list item) | Maintained one-page statement citing the route-table test as its standing proof | ET-5 |

### C9 — Trace Agent: **rejected** — evidence = design-absence: no standalone C9 capability/session registry may exist (checked by the SS-4 uniformity test's approved-list equality). ET-2.

### C10 — Structured Confirmation Protocol (CG-10 / SG-10)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Every proposal/confirmation/rejection/expiry is an SC-3-grade audit record (CG-10) | Terminal-record field assertions on all four terminal states; sweep test + event-invalidation test assert records exist | ET-1 |
| Attributable per R4 (CG-10) | Field-presence assertions incl. verified principal, auth-context ref, DB-clock timestamp, payload-as-presented | ET-1 |
| Payload freezing (SG-10) | Write-once/trigger mutation-rejection test; UX behaviour 5 (card renders payload values only) | ET-1 |
| Idempotent execution (SG-10/DQ-002) | Double-confirm CAS test: one mutation, second returns recorded outcome; UX behaviour 7 | ET-1 |
| Run-state invalidation (DQ-002) | propose → run APPROVED → confirm → `INVALIDATED`, no mutation | ET-1 |
| Conflict handling (DQ-002) | Concurrent-proposal refusal test (partial unique index) | ET-1 |
| Confirmation is authenticated UI action distinct from chat (SG-10/T7) | UX behaviour 4 (no confirm control in chat — DOM assertion) + route auth test | ET-1 |

### C11 — Compliance Monitoring (CG-11 / SG-11)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Source policy enforced in code (CG-11) | Committed test: non-Tier-1 source → no operative claim; provenance fields mandatory (insert without them fails) | ET-1 |
| DQ-006 resolved pre-build | Human decision record (legal sign-off) — register row cannot close without it | human decision |
| Monitoring-stall alerting (CG-11) | Committed test: stalled monitor produces a notification via C2 | ET-1 |
| C12 exists or ships together (CG-11) | Register sequencing check (C11 row may not close before C12 row) | sequencing |
| Context isolation — no workspace-scoped tool (SG-11) | Session-registry test: C11 session registry contains zero workspace-scoped tools | ET-1 |
| T5 hostile-source injection set (SG-11) | C11 hostile-source corpus + eval report | ET-1 + ET-4 |
| Every proposal carries provenance (SG-11) | Field-presence test on proposal creation | ET-1 |
| Time-to-apply baseline exists pre-launch | Baseline B5 artifact | ET-6 |

### C12 — Statutory-Rule Change Management (CG-12 / SG-12)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Verified-identity approvals (CG-12.1) | Approval without auth/step-up rejected (tests) | ET-1 |
| Approval record persisted atomically (CG-12.2) | Forced-failure test: approval row + domain-2 audit row atomic | ET-1 |
| Deterministic validation incl. graceful UNIQUE conflict (CG-12.3) | Duplicate-proposal fixture → named validation error pre-approval; DB constraint backstop intact | ET-1 |
| Impact preview at approval (CG-12.4) | Preview-presence assertion in `payload_as_presented_jsonb`; recompute-on-apply test; UX behaviour 8 | ET-1 |
| Append-only + recoverable corrections (CG-12.5) | Correction test: faulty row readable post-correction, resolution returns v+1, `superseded_by_rule_id` stamped; UX behaviour 11 | ET-1 |
| Step-up freshness + single-use (SG-12/DEC-07-03) | Expired/reused/foreign step-up rejected; step-up event referenced from approval record; UX behaviour 9 | ET-1 |
| One workflow regardless of origin (control §6) | Origin-equivalence test: C11-origin and human-origin fixtures traverse identical states | ET-1 |
| Date-driven resolution only (Stage 06 constraint) | Grep/contract check: resolution always `effective_from <= date` ordered; no "current rule" shortcut | ET-1/ET-2 |
| DQ-007 resolved pre-build (segregation waiver + MFA hard-gate question) | Human decision record — register row cannot close without it | human decision |
| Rejection requires reasoning; own-proposal state | UX behaviours 10, 12 | ET-1 |

### C13 — Onboarding Mapping Assistant (CG-13 / SG-13)

| Gate item | Evidence artifact | Type |
|---|---|---|
| C14 live first (CG-13 binding) | Register sequencing check (C13 row may not close before C14 row) | sequencing |
| Every proposed mapping + correction logged (CG-13) | SC-3 test on the mapping-proposal tool path; correction stream queryable (it is both audit evidence and the eval baseline) | ET-1 |
| No direct writes — proposals only (CG-13) | Committed test: no mapping commits without operator confirmation (UX behaviour 18) | ET-1 |
| Header-borne injection fixtures (SG-13) | C13 hostile-header corpus + eval report | ET-1 + ET-4 |
| Proposals render only to uploader's session (SG-13) | Session-scoping test | ET-1 |
| Catalog tool under SS-2 (SG-13) | Covered by SC-2 uniformity/negative-path artifacts | ET-1 |
| Mapping-time/error baseline exists pre-launch | Baseline B1 artifact | ET-6 |

### C14 — Deterministic Import Validation & Dry-Run (CG-14 / SG-14)

| Gate item | Evidence artifact | Type |
|---|---|---|
| Dry-run retained as pre-commit evidence linked to commit (CG-14) | Commit-gate hash test: missing/mismatched/failed `dry_run_id` rejected; UX behaviour 20 | ET-1 |
| Commit attributable (CG-14/SC-1) | Audit-actor test on the commit action | ET-1 |
| Identity/scoping (SG-14/R1/R2) | Cross-workspace dry-run → 404; artifact rows carry verified principal | ET-1 |
| Production-state separation (DQ-004) | **Non-mutation test**: row-count snapshots of `payroll_run`/`payroll_result`/`payroll_input.payroll_run_id`/`event_store` identical before/after — the load-bearing closure evidence; UX behaviour 19 | ET-1 |
| Real-path fidelity (DQ-003) | Equivalence test: same fixture through dry run and real run → identical per-employee results | ET-1 |
| Input non-consumption | Unclaimed rows remain unclaimed after dry run | ET-1 |
| Parallel-run agreement + time-to-go-live baselines pre-launch | Baselines B2, B3 artifacts | ET-6 |

### C15 — Email Notifications (CG-15 / SG-15): **deferred** — evidence rows (no-PII-in-subject test; no magic-link session bypass test) defined when scheduled; both are ET-1 at that point.

## 4. Remediation evidence (Stage 08 §§1–8, beyond the C8 rows above)

| Remediation | Evidence artifact | Type |
|---|---|---|
| `load_inputs_for_run` closure (F-05-11) | Workspace-parameter filter test, or non-exposure enforcement check | ET-1 |
| `component_trace_jsonb` null guard | Repo-layer guard test | ET-1 |
| `salary_definition` edit-lock (D-ARCH-1 family) | In-progress-run PATCH rejection test | ET-1 |
| D-ARCH-1 dead branches / status drift | Enum-iteration status-classification test | ET-1 |

## 5. Register maintenance (DEC-10-02)

- **"Done" rule**: a Phase 3 build item claiming to close a gate is complete only when this register's corresponding rows point at merged, CI-green artifacts (or dated ET-2/3/5/6 records). Sprint close cites the register row; the register is updated in the same commit.
- **Ratchet rule**: evidence requirements may be tightened without ceremony; any weakening (removing/downgrading an artifact) requires a recorded human decision — the same rule the gate registers carry.
- **Ownership**: this programme until Phase 3 adoption, then the repo's sprint workflow (the `/tester`/`/retro` loop) inherits it.
- **Sequencing checks are register properties**: C7-after-C2, C13-after-C14, C11-with-C12 are enforced as row-closure preconditions here, mirroring (not restating) the gate registers.
