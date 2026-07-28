# Stage 09 Independent Critic Review

- **Critic pass**: 2026-07-17, fresh context per D-004, contract `CRITIC.md`
- **Reviewing**: Stage 09 executor pass (commit `525d41c`, evidence pinned at `7d36020`)
- **Verdict**: **PASS** — with three non-blocking corrections for controller application pre-closure (none blocks advancement; none changes a conclusion, finding disposition, or handoff)

## 1. Scope reviewed

- `CONTEXT.md` (execution contract), `findings.md` (F-09-01..04), `decisions.md` (DEC-09-01..14), `evidence/09-frontend-grounding-excerpts.md`, all 9 outputs, and the shared-state updates (`review-state.md`, `decision-queue.md` DQ-005 row, `_inputs/source-register.md`).
- Independent re-verification of every load-bearing frontend citation against the working tree (confirmed diff-identical to `7d36020` for `frontend/`, `backend/`, `migrations/` — `git diff --stat 7d36020 525d41c` on those paths is empty).
- Consistency re-read of the binding inputs: `portfolio-boundary-map.md` §§3/7; Stage 04's `stage-09-handoff.md`, `exception-resolution-outcome.md` (eight stages), `measurement-framework.md` (C3 volume prohibition); Stage 08's `stage-09-handoff.md` items 1–8 and the mechanism designs it references (`auth-foundation-design.md`, `event-audit-foundation-design.md` §§4/6, `confirmation-protocol-design.md`, `statutory-change-mechanism-design.md`, `dry-run-mechanism-design.md`, `anomaly-detection-design.md` §4, `tool-contracts.md` §§1/3.5/3.11); `docs/design/ui-decisions.md`; repo CLAUDE.md Upload/Enroll rule; Stage 08's own `stage-10-handoff.md` (for handoff mutual consistency).
- Authority check: `git show --stat 525d41c` — all 16 changed files inside `docs/programmes/agentic-architecture-review/`; no production or unrelated working-tree changes.

## 2. Strengths

1. **Citation accuracy is excellent.** Every load-bearing code citation re-verified exact: `MainLayout.tsx:61` (navigate-only switch); `Navigation.tsx:4-11` (DD-1 header), `:111-123` (picker), `:158-171` (user menu incl. `userName` avatar), `:215/238/244/306-311` (badge pattern, 99+ cap at :311); `PayrollResults.tsx:5` (DD-2 four tabs), `:63` (TabKey), `:1171-1178` (`actor: e.performed_by` at :1174); `RunPayroll.tsx:45/48` (state types), options at :200-203 and :233-242 (executor's `~199–202`/`~235–240` approximations are honestly marked); `router.tsx` (no platform-level routes). I additionally re-verified the backend halves of F-09-02 that the executor carried from prior stages: `payroll.py:76` `_VALID_RUN_TYPES` includes `CORRECTION`; `:83` `_VALID_RETRY_STRATEGIES = {"PER_EMPLOYEE"}`. Both hold.
2. **Mechanism fidelity.** Each output names the mechanism it renders and I found **no invented statuses, codes, fields, or lifecycle steps**: exception statuses and the three operator resolution codes match `event-audit-foundation-design.md` §6 and the handoff; the "Re-check failed" presentation explicitly avoids inventing a status; C10 renders all four terminal states with the mechanism's required INVALIDATED message and both-states display; the C12 chip set matches the nine-state machine exactly; the null-trace refusal text is the §3.5 contract text verbatim; shadow-mode exclusion, frozen-`evidence_jsonb` rendering, pointer-only notifications, hash-gate two-layer semantics, and at-decision-moment step-up consumption are all preserved as stated.
3. **The C11→C12 coherence answer is strong**: one surface, origin as a chip — structurally incapable of reading as two systems, and consistent with control §6's origin-is-a-field-not-a-fork.
4. **Binding UX constraints carried faithfully**: five refusal conditions with §3's content requirements (including "platform limitation, not permission-denial" and byte-identical cross-workspace/not-found copy per P5); suggested-vs-fact separation; anti-chat-burying rules; volume-metric prohibition restated in both handoffs; Upload/Enroll separation restated as a design constraint with `grade_code` never forwarded.
5. **Grounded restraint**: findings that are grounding rather than defects are rated Informational with inline justification (F-09-01/03/04); F-09-02's Medium is justified against the severity model (loud failure, no data harm, consistent with Stage 05's classification) and its evidence was genuinely re-read this session rather than carried over.
6. **DQ-005 handled exactly as the contract required**: a substantive recommendation (context-launched correction-run CTA with/after C12, not generic dropdown exposure) grounded in re-verified evidence, recorded in `stage-11-handoff.md` §1 and in the queue row, and correctly left open for Stage 11's joint disposition rather than closed unilaterally.

## 3. Required corrections (non-blocking — controller may apply pre-closure; no re-critic needed)

| # | Correction | Affected files |
|---|---|---|
| RC-1 | **Consumer count is wrong: `NativeUploadFlow` has three page consumers, not two.** `PayrollResults.tsx` also imports and renders it (`:53`, `:443` — the reconciliation old-system comparison upload), alongside `Employees.tsx:1610` and `PayrollInputsBulkUpload.tsx:513`. The error direction strengthens the "live shared component" conclusion, but the third consumer is regression surface for any C13 change to the shared components and belongs in Stage 11's sizing row. | `evidence/09-frontend-grounding-excerpts.md` §5; `findings.md` F-09-04 (current-implementation field); `outputs/onboarding-flow-experience.md` §1; optionally `outputs/stage-11-handoff.md` §3 |
| RC-2 | **Platform-level notification delivery is a mechanism seam the outputs use without naming.** `workspace_notification.workspace_id` is NOT NULL (`event-audit-foundation-design.md` §4) and the bell is scoped to the session's active workspace, yet `statutory-approval-experience.md` §7 and `notification-experience.md` §3 promise statutory/C11 pointers reaching `PLATFORM_ADMIN` operators. How those rows are delivered (per-affected-workspace fan-out with `operator_id` targeting? visible only in the admin's active workspace's bell?) is unspecified — and non-admin workspace operators must not receive pointers to a surface that uniform-404s them (P5). Add an explicit note naming this as an open implementation-specification item for the Phase 3 build (or specify the fan-out rule); do not leave it implicit. | `outputs/notification-experience.md` §3; `outputs/statutory-approval-experience.md` §7 |
| RC-3 | **"Badge-refresh on poll" misdescribes the existing pattern.** `MainLayout.tsx:19-36` refreshes badges on route change plus `employees-changed`/`payroll-inputs-changed` window events — event-driven, not polling (the only polling in the cited surfaces is PayrollResults' 5s CALCULATING poll, DD-18). One-line precision fix; the design point (non-interruptive count refresh, no push) stands. | `outputs/notification-experience.md` §5 |

## 4. Non-blocking observations (no correction required)

- **DD-5 empty-state deviation is cited as compliance.** The exception queue's empty state deliberately drops DD-5's third element (specific CTA) with sound reasoning (system-created list; empty is the good state) — but the text reads "per ui-decisions DD-5" rather than "extending DD-5". Phase 3 should record the system-generated-list extension in `docs/design/ui-decisions.md` when the queue is built.
- **`SUPERSEDED`** (the fourth resolution code, `event-audit-foundation-design.md` §6) is not an operator action — the three-action mapping is correct against the handoff — but Closed-history rows carrying it will need a display treatment. Implementation-specification for Phase 3.
- **"Expiring-soon" pending-action notifications** (`confirmation-experience.md` §7) imply a pre-expiry consumer emission that Stage 08 §3.1 specifies only as the post-expiry sweep. The notification `type` vocabulary is open (VARCHAR, not an enum), so nothing is contradicted, but Phase 3 should note the extra consumer job.
- F-09-01/F-09-03 as Informational is defensible: the "gap" in each is against a future Stage 08 mechanism, not a defect in current intended design, and rating them higher would double-count Stage 05's platform-wide auth headline. Justifications are inline per the severity model.

## 5. Decision classification (per `CRITIC.md`)

| Open question | Classification |
|---|---|
| DQ-005 (CORRECTION UI exposure) | `non-blocking-forwarded-decision` — recommendation recorded, correctly remains with Stage 11; queue row updated without silent closure |
| Multi-operator workspace posture (notification read-state, assignment/escalation) | `non-blocking-forwarded-decision` — a Stage 11 scope boundary, correctly forwarded in `stage-11-handoff.md` §3; **not** a hidden risk acceptance (read-state is explicitly non-audit-class in the Stage 08 schema, so no CG/SG property attaches) |
| Platform-level notification delivery (RC-2) | `implementation-specification` — a Phase 3 build question the outputs must name, not a human choice |
| SUPERSEDED rendering; expiring-soon emission; DD-5 extension | `implementation-specification` |
| NativeUploadFlow consumer count (RC-1) | `evidence-gap` — trivially closed by the correction |
| The 14 DEC-09-* conclusions | `not-a-decision` (design execution) — each verified grounded in a binding input (D-03-01 surfaces, Stage 04 outcome/measurement rules, Stage 08 mechanisms, SG-10/SG-12/P5–P7, threat-model §6, ui-decisions, Sprint 22/23 standing rules); none is a product, risk, or compliance choice with multiple evidence-inseparable options |

**No blocking human decisions found.** The executor's zero-human-decisions claim survives scrutiny; no artificial approval gates were created, and none is warranted by this review.

## 6. Evidence-quality assessment

Meets the standard. All confirmed findings carry direct path:line citations plus committed excerpts pinned to a named commit (`7d36020`), and the pin is verifiable (production paths diff-identical through `525d41c`). Prior-stage claims reused as load-bearing (Stage 05's FULL_RUN/CORRECTION mismatches) were re-verified against current code this session rather than carried over — the re-verification rule honoured where it mattered most (F-09-02 feeds the DQ-005 recommendation). One factual error found (RC-1), contained to a grounding claim whose conclusion it does not weaken. Source register updated correctly (Stage 09 re-read note; no new external sources).

## 7. Consistency assessment

- **Against Stage 08 mechanisms**: consistent throughout; no mechanism silently modified. The one unaddressed seam is RC-2, which is a specification omission, not a contradiction.
- **Against Stage 04**: all eight outcome stages map to named interface regions; one-workflow, single-owner, evidence-alongside, suggestion-vs-fact, and the volume-metric prohibition all carried.
- **Against Stage 03**: five refusal conditions rendered with the §3 required behaviours; chat confined to C3; §7's non-chat surfaces designed as recommended (C13 anchored in the existing upload UI; C11's "comparison view" satisfied inside the proposal detail — a legitimate execution of control §6's one-workflow rule, not a deviation).
- **Against security/compliance constraints**: T7/SG-10 (no confirm in chat; frozen-payload rendering), SG-12 (platform-level, PLATFORM_ADMIN-only), P5 (uniform 404 copy, byte-identical), threat-model §6 (mechanical, non-collapsible pre-epoch labelling incl. exports) — all preserved; no CG/SG gate weakened.
- **Handoffs**: `stage-10-handoff.md` complements Stage 08's without overlap or contradiction (item 23 correctly extends the epoch fixture to the presentation layer); `stage-11-handoff.md` is consistent with the outputs, F-09-02, and the DQ-005 queue row. `review-state.md`, `CONTEXT.md` status, and `decisions.md` are mutually consistent.
- **CONTEXT.md completion**: Q1–Q9 each have a design answer (Q9 via the recorded recommendation); every required output exists; finding discipline and the frontend-verification requirement were followed.

## 8. Advancement recommendation

**Close Stage 09 and open Stage 10** once the controller applies RC-1–RC-3 (all mechanical/precision-level; mirrors the Stage 07/08 pre-closure pattern — no executor re-run or re-critic warranted). No blocking human decision remains; DQ-005 correctly stays open for Stage 11, and DQ-006/007/008 are untouched as required.

---

## Controller disposition (2026-07-17)

**PASS + no blocking decision → close Stage 09 automatically per D-003/`RUNBOOK.md`.** All three corrections applied pre-closure, same day:

- **RC-1**: third `NativeUploadFlow` consumer (`PayrollResults.tsx:443`) independently re-verified by the controller, then corrected in `evidence/09-frontend-grounding-excerpts.md` §5, `findings.md` F-09-04, `outputs/onboarding-flow-experience.md` §1, and `outputs/stage-11-handoff.md` §3 (three-surface regression obligation added to the C13 sizing row).
- **RC-2**: platform-level notification delivery named as an explicit open implementation-specification item in `outputs/notification-experience.md` §3 and cross-referenced from `outputs/statutory-approval-experience.md` §7, with the P5 constraint (no pointers to non-admins) stated.
- **RC-3**: badge-refresh description corrected to the event-driven pattern (`MainLayout.tsx:19-36`) in `outputs/notification-experience.md` §5.

The four non-blocking observations (§4) are Phase 3 implementation specifications; the DD-5 extension and `SUPERSEDED` display treatment are noted for the Phase 3 frontend sprints via the standing ui-decisions workflow, and the expiring-soon consumer emission is carried implicitly in `confirmation-experience.md` §7's design (an extra consumer job, vocabulary-compatible). No decision-queue changes required beyond the DQ-005 row already updated by the executor.
