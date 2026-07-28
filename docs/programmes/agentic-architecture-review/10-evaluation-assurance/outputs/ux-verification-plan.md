# Stage 10 Output: UX-Behaviour Verification Plan (Q5)

Disposition of Stage 09's 25 UX-testable behaviours (`09-human-experience/outputs/stage-10-handoff.md` — numbering preserved): how each is verified, whether it is a launch gate or a post-launch monitor, and how it slots into the repo's real test conventions. The behaviours' *designs* are closed (Stage 09, critic-passed); mismatches found while building verification go back as findings, not silent design edits.

## 1. Verification infrastructure reality (F-10-01)

The repo has **no frontend test harness** — no test script, no framework, zero test files; CI's frontend job is typecheck only (evidence file §2). The backend harness is strong (328 tests, fresh-DB CI, pre-push gate).

**Plan consequence (DEC-10-11)**: a minimal frontend component-test harness is an **assurance prerequisite**, built as part of the first frontend-touching build item (C1 — its auth surfaces carry behaviours 22–25). Recommended shape: Vitest + React Testing Library (matches the existing Vite toolchain — an implementation specification, not a decision; Phase 3 confirms tooling via the repo's conventions), plus a `frontend-test` CI job beside the existing typecheck. This retires the T4.5 park: behaviour 21 becomes the harness's first standing regression test.

Until the harness exists, no behaviour classified "component" below is closable — the register rows that cite them depend on the harness landing (a sequencing fact carried to Stage 11).

## 2. Disposition of the 25 behaviours

Verification forms: **component** (DOM/render assertion in the frontend harness), **backend** (pytest, fresh-DB rules), **e2e-scripted** (one-page manual script producing a dated artifact — used where automation cost exceeds value at launch), **eval** (LLM corpus, `llm-evaluation-framework.md`). Gate class: **LG** = launch gate for the named capability; **PM** = post-launch monitor.

| # | Behaviour (short) | Verification | Gate class | Notes / gate refs |
|---|---|---|---|---|
| 1 | Five-condition refusal rendering | eval (refusal classes incl. ~100% historical) + component (boundary presentation, verbatim null-trace text) | LG C3 | CG-3/CG-5; framework §3 |
| 2 | No existence disclosure — byte-identical shapes | backend fixture-pair (API response equality) + component (copy identity) | LG C3 | P5; framework wrong-basis class |
| 3 | Grounding footer 1:1 with `tool_call_log` | component (mocked session) + backend (chip source = logged calls) | LG C3 | SC-3 |
| 4 | No confirm control in chat | component DOM assertion | LG C3/C10 | T7/SG-10 |
| 5 | Frozen-payload rendering (card = `payload_jsonb` only) | component fixture (chat text deliberately diverges) | LG C10 | SG-10 payload freeze |
| 6 | All four terminal states render; INVALIDATED dual-state; EXPIRED "nothing executed" | component (one fixture per state) | LG C10 | CG-10 |
| 7 | Double-submit convergence (two tabs → one execution + loser banner) | backend CAS test (the execution half — already ET-1, register C10) + e2e-scripted (the two-tab render half) | LG C10 (backend) / PM (UI race) | Automating a genuine two-tab race needs browser e2e infra that doesn't exist; the safety property is backend-enforced, the UI presentation is monitored |
| 8 | Approve unreachable until full evidence set rendered | component (field-presence gating) | LG C12 | CG-12.4 |
| 9 | Step-up moment (modal, expired/consumed re-prompt, no partial submit) | component + backend rejection matrix (register C12) | LG C12 | SG-12 |
| 10 | Rejection requires reasoning (client + server) | component + backend | LG C12 | CG-12 |
| 11 | Correction proposals: consumed-runs statement + recalculation decision control | component | LG C12 | CG-12.5 |
| 12 | Own-proposal approve disabled with reason | component | LG C12 | Pending DQ-007 — if the waiver changes the rule, the test changes with the recorded decision, not silently |
| 13 | Shadow-mode records excluded from badge/counts; visible only under toggle | component + backend count-query test | LG C7 | CG-7; calibration integrity |
| 14 | `recommended_action` never inside evidence region | component DOM assertion | LG C7 | Suggested-vs-fact separation |
| 15 | Frozen evidence (source correction ≠ rendered `evidence_jsonb` change) | backend (evidence immutability) + component render | LG C7 (backend) / PM (render) | Exception-record integrity |
| 16 | Dismiss friction (evidence re-presented before confirm) | component | LG C7 | Backs dismiss-without-review metric |
| 17 | Notifications are pointers only; read-state independence | component | LG C2-notifications | v1 single-operator posture — no multi-operator assertions (Stage 09 carried context) |
| 18 | No mapping commits without confirmation; low-confidence sort; original headers visible | component + backend (no-commit-without-confirm) | LG C13 | CG-13 |
| 19 | Dry-run results never in Runs list; no-payroll-created banner | backend (non-mutation test — already ET-1, register C14) + component (banner + list exclusion) | LG C14 | DQ-004 |
| 20 | Hash-gate UX (edit → Commit disabled; server rejection renders same state) | component + backend hash-mismatch (register C14) | LG C14/C13 | Two-layer agreement |
| 21 | Committed import sends no `grade_code` | component (payload assertion on `createEmployee` call) | LG C13 + standing regression immediately at harness landing | **Retires parked T4.5**; standing Upload/Enroll rule |
| 22 | Workspace switch tears down state (no stale data post-switch) | e2e-scripted at C1 launch; component teardown-unit test where feasible | LG C1 (scripted) / PM (automated later) | P6; full-surface stale-data sweep is a browser e2e concern |
| 23 | Pre-epoch labelling on every audit surface incl. exports | backend (export path fixture test) + component (surface labelling) | LG C1 | Extends the epoch ET-1 to presentation; F-09-03's adapter seam |
| 24 | Uniform 404 (member vs non-member deep link) | backend fixture-pair + component copy identity | LG C1 | P5 at route layer |
| 25 | Uniform login errors (wrong-password vs unknown-email) | component fixture-pair + backend response-equality | LG C1 | Credential-probe hygiene |

Tally: 21 behaviours fully automatable once the harness exists (component and/or backend); 2 split (7, 15 — safety half automated at launch, presentation half monitored); 2 scripted-manual at launch with automation deferred (22 full-sweep; 7's UI race). No behaviour is left unverified.

## 3. Scripted-manual protocol (the e2e-scripted entries)

One-page scripts, versioned beside the corpus fixtures; each execution produces a dated artifact (checklist + screenshots) retained as the ET-1-substitute launch evidence and referenced from the register row. Two scripts at launch: **S-22** (workspace-switch teardown sweep: switch mid-view on each major page; assert no previous-workspace data renders) and **S-7b** (two-tab confirmation race: both tabs converge on recorded outcome; loser shows the explanatory banner). Scripted-manual is a launch bridge, not a destination — each script's automation lands with the first browser-e2e infrastructure any later sprint introduces (carried to Stage 11 as an optional cost line).

## 4. Conventions (binding for the Phase 3 implementer)

- Backend halves follow the existing rules: fresh-DB compatible fixtures, registry pin/restore via `tests/registry_state.py`, unused statutory `effective_from` dates, tests named for the behaviour (`test_b09_21_bulk_import_sends_no_grade_code`-style — the number makes the register mapping greppable).
- Component tests assert **DOM/copy contracts, not implementation**: presence/absence of controls, rendered values vs fixture values, copy-identity pairs. Fixture-pair equality patterns (behaviours 2, 24, 25) compare rendered output of two cases, never hardcode the copy itself (copy is Phase 3 `/ux-copywriter` territory; the *identity* of the two renderings is the invariant).
- Every behaviour test cites its behaviour number in a comment — the register's UX rows are checkable by grep.

## 5. Gate mapping

Behaviours are the UI face of their capability's CG/SG rows (noted per row above); the register (§3) cites this plan for all "UX behaviour n" evidence entries. Launch-gate behaviours block their capability's register row; PM entries are reviewed in the standing cadence (`standing-assurance-controls.md` §4's evidence-register currency check).
