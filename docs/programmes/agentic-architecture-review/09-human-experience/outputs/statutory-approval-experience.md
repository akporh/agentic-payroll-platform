# Stage 09 Output: Statutory Approval Experience — C12, including C11→C12 coherence (Q5)

Designs the approval experience for statutory-rule changes. **Mechanism rendered**: proposal/approval state machine, evidence set, Validator, impact preview, correction mechanics (`08-technical-architecture/outputs/statutory-change-mechanism-design.md` §§2–8). **Security constraints bound**: `PLATFORM_ADMIN`-only, platform-level surface (SG-12); step-up with 5-minute freshness (DEC-07-03); mandatory rejection reasoning; correction proposals show the consumed-runs statement. Resolves Stage 03's forwarded coherence gap: C11 (detect/propose) and C12 (approve/apply) must read as **one workflow** to the operator.

## 1. Placement: a platform-level area, not a workspace page

A new **Statutory Changes** area at a platform-level route (`/platform/statutory-changes`, matching the mechanism's route family §7), reached from the **bureau level**: an entry on the bureau dashboard and in the TopBar user menu, visible only to `PLATFORM_ADMIN` operators. It is deliberately **not** in any workspace sidebar — statutory rules are country-level platform data; placing the surface inside a workspace would visually contradict its blast radius (SG-12's platform-level requirement made spatial). No platform area exists in today's router (evidence file §6) — this is the first, and its chrome should make the context switch visible (distinct header: "Platform — Statutory Changes", no workspace sidebar).

## 2. C11→C12 as one workflow (the Stage 03 gap, resolved in the IA)

**C11 has no separate surface.** A C11 detection *is* a proposal row (`origin = C11` — mechanism §2.1: origin is a field, not a fork). The operator experience is one continuous path:

> Notification: "Statutory change detected for NG — proposal awaiting review" → proposal detail (evidence, diff, validation, impact) → approve with step-up → apply.

The "comparison view" Stage 03 §7 recommended for C11 **is** the proposal detail's diff region (§3) — not a second screen. Human-originated proposals (`origin = HUMAN`) enter the same list, same detail, same states; the origin chip is the only visible difference. This is the strongest possible answer to the coherence question: the operator cannot experience C11 and C12 as separate systems because there is only one surface.

## 3. Proposal list and detail

**List**: status chip per state-machine state (Draft / Submitted / Validated / Awaiting approval / Approved / Applied / Rejected / Failed validation / Withdrawn), origin chip (Detected (C11) / Manual), country, `change_kind` (New rule / Correction), proposed effective date, proposer. Default filter: awaiting my review (`AWAITING_APPROVAL`).

**Detail — the full §3 evidence set, four fixed regions in reading order:**

1. **Source citation**: `source_name`, `source_reference` (external link, opens in new tab), `publication_date`, the **verbatim excerpt** rendered as a quoted block (visually unmistakable as quoted external text, never paraphrase), snapshot hash shown collapsed ("source snapshot ✓ recorded"). The `effective_basis` (the regulation's own commencement statement) sits with the proposed effective date.
2. **Deterministic diff**: current vs proposed per component — old / new / delta columns (the platform already renders old/new/diff comparison tables in the run-detail comparison view; same presentation grammar). Tax-band changes render as a band table diff. **UX-critical invariant**: the diff is the Validator's computed diff (`validation_results_jsonb` era — mechanism §4.4), never C11's advisory text; advisory prose, if shown at all, is collapsed under the citation region and labelled advisory.
3. **Validation results**: the Validator's named checks as a pass/fail list (shape, duplicate/conflict, effective-date, diff computed). `FAILED_VALIDATION` proposals show named errors and offer no approval path.
4. **Impact preview**: affected workspaces, affected periods, and the representative before/after per component (amounts as strings — mechanism §5), with `impact_computed_at` timestamped visibly ("computed 2h ago"); stale previews (>24h re-validation guard) show as refreshing.

**Corrections additionally show, above the decision bar**: the `correction_statement_jsonb` region — what was wrong, the **consumed-runs statement** (the enumerated list of runs that consumed the faulty values), and the recalculation question as an explicit, required decision input on approval: the approver must select "recalculation/adjustment runs required" or "no recalculation required" with a reasoning line — this is the mechanism's "approver's recorded decision" (§6) surfaced as a form control, not free text buried in notes.

## 4. The decision bar: approve with step-up, reject with reasoning

- **Approve →** opens the **step-up modal** (`auth-and-audit-surfaces.md` §4): "Approving a statutory change requires re-entering your password." On success the approval submits immediately with the returned `step_up_event_id` — the modal is invoked *at the decision moment* so freshness (5 min) is consumed in seconds, and a fresh prompt on expiry/consumption failure (403 → re-prompt with "your confirmation expired — re-enter your password") is the designed recovery, not an error dead-end.
- **Reject** requires reasoning text (non-empty validation; the mechanism makes it NOT NULL on rejection). The form states where the reasoning goes: "recorded permanently on the approval record."
- **What was approved is what was shown**: the mechanism freezes `payload_as_presented_jsonb` + hash at approval (§2.2). The UI must therefore submit the rendered evidence set with the decision — a build-time contract for Phase 3: the approval call carries the presented payload, not a reference the server re-derives later.
- Segregation: `approver_id != proposer_id` is enforced server-side (pending DQ-007's waiver). The UI shows own-proposal rows with the approve control disabled and the reason stated ("you proposed this change — a different approver is required"), rather than a surprise 403.

## 5. Approved → Applied

Application is a separate step (mechanism §3), immediate in the happy path: after approval success, the same screen offers **Apply now**. If application's re-validation halts on material state change (new workspace in country, new run in an affected period), the UI shows the return to `AWAITING_APPROVAL` with a fresh preview and the plain explanation: "the platform changed since this was approved — review the updated preview and approve again." Approval is of a specific diff against a specific state, never a blank cheque — the copy carries the principle.

## 6. History and provenance

- The proposal list's history filter is the append-only record: every proposal, decision, reasoning, and application, with actors (verified principals — display names via join) and timestamps.
- Wherever current statutory rules are displayed (this area's "Current rules" reference view, and any future rule display), rows carry provenance: rules with `applied_change_id` link to their approval; rows without it are labelled **"migration-seeded (pre-C12)"** (mechanism §2.3), and pre-epoch actors follow the standard identity-unverified labelling (`auth-and-audit-surfaces.md` §5). A corrected row renders with its superseding version adjacent ("superseded by v2, same effective date") — resolution semantics (date + version) stay visible, not implied.

## 7. Notifications

C11 detections and state transitions fan out as notification pointers to `PLATFORM_ADMIN` operators (CRITICAL for detected changes with near effective dates, WARNING otherwise). Pointers only; the decision lives here. **How platform-level rows travel through the workspace-scoped notification table is an open implementation-specification item** (`notification-experience.md` §3, per critic RC-2) — whatever fan-out rule Phase 3 picks, pointers to this surface reach admins only.
