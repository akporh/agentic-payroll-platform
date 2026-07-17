# Stage 08 Output: Statutory-Change Mechanism Design (C12)

Answers Stage 08 Q5 within the fixed control requirements of `06-compliance-controls/outputs/statutory-change-control-design.md` (roles/segregation §2, evidence set §3, approval record §4, append-only history + corrections §5, one-workflow §6, impact placement §7) and the security constraints DEC-07-03 (step-up), SG-12, and the audit foundation (`event-audit-foundation-design.md`). D-02-04 holds throughout: no LLM anywhere in this mechanism; C11 proposals enter as data. Evidence pinned at `573be0d`.

## 1. Grounding fact (new this stage — F-08-01)

The run-time statutory resolution query already resolves by `WHERE sr.effective_from <= :as_of_date ORDER BY sr.effective_from DESC, sr.version DESC LIMIT 1` (`backend/api/routes/payroll.py:272-282`). The `version DESC` tie-break is written but today unreachable for a single country because `uq_statutory_rule_country_effective (country_code, effective_from)` (`statutory_rule.py:9-11`) forbids two rows at the same date. This existing tie-break is what makes the correction mechanics in §6 the natural choice.

## 2. Schema

### 2.1 `statutory_change_proposal`

| Column | Notes |
|---|---|
| `proposal_id` UUID PK | |
| `origin` | `C11` / `HUMAN` (control §6 — one workflow; origin is a field, not a fork) |
| `proposer_id` UUID FK → operator | human proposer's verified identity, or the `svc:compliance-monitor` principal for C11 |
| `country_code` VARCHAR(10) NOT NULL | |
| `proposed_effective_from` DATE NOT NULL | with `effective_basis` TEXT (the regulation's own commencement date statement — control §3.2) |
| `change_kind` | `NEW_RULE` / `CORRECTION` (correction is a first-class change type — control §5) |
| `corrects_statutory_rule_id` UUID NULL | required when `change_kind = CORRECTION` |
| `proposed_rules_jsonb` JSONB | complete proposed `rules_jsonb` (full target state, not a patch — diffing is the Validator's job, removing any ambiguity about patch application order) |
| `proposed_tax_bands_jsonb` JSONB NULL | |
| **Source citation** (control §3.1) | `source_name`, `source_reference` (URL/document ref), `publication_date`, `verbatim_excerpt` TEXT, `source_snapshot_hash` (hash of the fetched source document — C11 supplies it from its snapshot; human proposers upload the document to get one) — all NOT NULL for both origins |
| `status` | state machine §3 |
| `validation_results_jsonb` | Validator output, written at VALIDATED |
| `impact_preview_jsonb` + `impact_computed_at` | §5 |
| `correction_statement_jsonb` NULL | for corrections: what was wrong, which runs consumed the wrong values (computed run list), whether recalculation is required (control §5) |
| `created_at` | |

Immutable after submission except the status machine (trigger-enforced immutable columns — `event-audit-foundation-design.md` §5). A changed proposal is a new proposal.

### 2.2 `statutory_change_approval` (the §4 approval record)

`approval_id` UUID PK · `proposal_id` FK · `approver_id` UUID FK (verified principal) · `decision` (`APPROVED`/`REJECTED`) · `decided_at` TIMESTAMPTZ DEFAULT now() (DB clock) · `decision_session_id` UUID (auth context) · `step_up_event_id` UUID FK NOT NULL (DEC-07-03) · `payload_as_presented_jsonb` (the proposal content + validation results + impact preview **exactly as rendered to the approver**, frozen) · `payload_hash` · `reasoning` TEXT (NOT NULL on rejection, nullable on approval per control §4) · `applied_rule_ids` UUID[] NULL + `applied_at` (linkage to rows written). Append-only; written through the persistence facade with a domain-2 `audit_log` row in the same transaction.

### 2.3 `statutory_rule` provenance additions (F-06-04 closure)

Add to `statutory_rule` (and mirror on `tax_band` via the rule FK): `created_at TIMESTAMPTZ DEFAULT now()`, `applied_change_id UUID NULL FK → statutory_change_approval` (NULL for pre-C12 rows — the migration-seeded era; consumers label these "provenance: migration-seeded (pre-C12)" analogous to the auth epoch), `superseded_by_rule_id UUID NULL` (annotation set on a corrected row — metadata only, never read by resolution, which stays purely date+version-driven).

## 3. Proposal state machine

```
DRAFT → SUBMITTED → VALIDATED → AWAITING_APPROVAL → APPROVED → APPLIED
              │           │                │            └→ REJECTED
              │           └→ FAILED_VALIDATION            
              └────────────── WITHDRAWN (any pre-APPROVED state)
```

- **SUBMITTED → VALIDATED** is the deterministic Validator (§4) — an automated step no role can waive (control §2). It re-runs automatically if the proposal sits >24h in `AWAITING_APPROVAL` (stale-validation guard), and always re-runs at application (§5).
- **Segregation**: `approver_id != proposer_id` enforced in code at the approval endpoint (pending DQ-007's waiver decision — the check ships; the waiver, if granted, adds the compensating-control path *then*, not now). Approvers require `role = PLATFORM_ADMIN`; the C12 surface is platform-level, not workspace-scoped, gated by that role.
- **APPROVED → APPLIED** is a separate step (may be immediate in the UI): re-validate against live state; if material state changed since approval (new workspace in an affected country, a run created in an affected period — control §7), application halts and the proposal returns to `AWAITING_APPROVAL` with a fresh preview — approval is of a specific diff against a specific state, never a blank cheque.

## 4. The Validator (deterministic, pre-emptive — F-05-04 closure)

Runs entirely in platform code:

1. **Shape validation**: `proposed_rules_jsonb` against a per-component required-key schema registry (`pension: {employee_rate, employer_rate}`, `nhf: {employee_rate}`, `health_insurance: {employee_amount}`, `development_levy: {amount | percentage}`, …) — closing the silent-Python-default exposure (F-01-46 territory); tax-band shape checks (contiguous bands, non-negative rates, ordered thresholds).
2. **Duplicate/conflict**: pre-emptive check against `(country_code, effective_from)` — and for corrections, against §6's version rule — so the approver never sees a proposal that would fail the DB constraint (control §5); the constraint remains the last line of defence.
3. **Effective-date checks**: `NEW_RULE` effective dates earlier than any existing run's `statutory_effective_date` for that country are flagged (retroactive change ⇒ must be a `CORRECTION` with its consumed-runs statement).
4. **Deterministic diff**: current-vs-proposed values computed against live `statutory_rule`/`tax_band` state (control §3.3) — the authoritative diff, whatever C11's advisory text said.
5. **Impact preview** (§5).

Output persisted to `validation_results_jsonb`; any failure → `FAILED_VALIDATION` with named errors.

## 5. Impact preview (control §7 — placement resolved)

**Placement: implemented once, C12-side, invoked by the Validator; C11 may call the same function for its advisory summary** (the design freedom control §7 left open — one implementation eliminates the stale-advisory divergence risk). Computation, all deterministic:

- Affected workspaces: `workspace.country_code = proposal.country_code`.
- Affected periods: open/future pay cycles whose `statutory_effective_date` resolution would select the proposed rule (re-using the §1 resolution query with the proposal hypothetically inserted).
- Representative before/after: for each affected rule component, one real employee profile per affected workspace (highest-paid enrolled employee as the default profile — deterministic selection rule) run through the **pure executor path** (`run_sequential_payroll` — same engine, no persistence; the same mechanism as C14's dry run, `dry-run-mechanism-design.md`), once with current rules, once with proposed. Output: component-level deltas as strings.
- Computed at review time (`impact_computed_at`); recomputed at application per §3.

## 6. Correction mechanics (control §5's open choice — resolved)

**Choice: same-date replacement row with `version + 1`; the faulty row is never mutated.**

- Mechanism: a `CORRECTION` writes a **new** `statutory_rule` row with the *same* `effective_from` and `version = corrected.version + 1` (plus new `tax_band` rows). The resolution query (§1) already prefers it via its existing `version DESC` tie-break — zero change to resolution semantics. The faulty row remains intact: **pre-correction values are DB-recoverable by construction**, not by a recovered-values sidecar. `superseded_by_rule_id` is stamped on the old row as annotation.
- Required constraint change: `uq_statutory_rule_country_effective` becomes `(country_code, effective_from, version)`. This is a deliberate, arch-council-visible **data-contract change** to a pinned invariant ("no duplicate effective dates") — recorded as such for Phase 3 build governance (per this repo's standing `/arch-council` gate); the invariant's *intent* (no ambiguous resolution) is preserved because resolution is total-ordered by `(effective_from, version)`.
- Why not supersede-in-place: prohibited by control §5 once any run consumed the row — and choosing a second mechanism for the not-yet-consumed case would create two correction paths (drift risk) for no benefit; the replacement-row path is uniform.
- Runs that consumed the faulty row: enumerated deterministically (`payroll_run.statutory_effective_date` resolution replay) into `correction_statement_jsonb`; whether recalculation/adjustment runs are required is the approver's recorded decision on the correction proposal. Existing run outputs are never touched by C12 (snapshot-first retry integrity, F-05-08, is unaffected).
- Rollback of an approved-but-future-dated rule = normal `WITHDRAWN`-style workflow action via a new proposal that supersedes the pending row (same replacement-row mechanics, `change_kind = CORRECTION`); rollback of a consumed rule *is* a correction (control §5 — enforced by the Validator's §4.3 check).

## 7. Routes (platform-admin surface)

`POST /platform/statutory-changes` (create draft) · `POST .../{id}/submit` · `POST .../{id}/validate` (idempotent re-run) · `POST .../{id}/approve` (requires `step_up_event_id`; §8) · `POST .../{id}/reject` · `POST .../{id}/apply` · `GET` list/detail. All under `get_current_principal` + `PLATFORM_ADMIN` role; **not** workspace-scoped routes; none of these are LLM tools (C12 acts through ordinary authenticated routes — tool-layer-security-pattern §4).

## 8. Step-up integration (DEC-07-03)

The approve endpoint requires a `step_up_event_id` that is: (a) owned by the approver's operator and current session, (b) `created_at` within the **5-minute freshness window** (`auth-foundation-design.md` §1.5), (c) unconsumed — consumed atomically (`consumed_by = approval_id` compare-and-set in the approval transaction; one approval per step-up event). Failure of any check → 403 with a fresh step-up prompt; the failed attempt is an `auth_event`. Method `PASSWORD` is the floor; `TOTP` slot activates with MFA enrollment (decided with DQ-007 — the mechanism does not pre-empt that decision).

## 9. Requirements satisfaction and verification (CG-12/SG-12 closure evidence)

| Gate item | Satisfied by | Verification |
|---|---|---|
| Verified-identity approvals (CG-12.1) | C1 dependency + §2.2 | Approval without auth/step-up rejected (tests) |
| Generalised audit persists §4 record (CG-12.2) | §2.2 via facade | Approval writes approval row + domain-2 audit row atomically (forced-failure test) |
| Deterministic validation incl. graceful UNIQUE conflict (CG-12.3) | §4 | Duplicate-proposal fixture → named validation error pre-approval; DB constraint intact as backstop |
| Impact preview at approval (CG-12.4) | §5 | Preview-presence assertion in `payload_as_presented_jsonb`; recompute-on-apply test |
| Append-only + recoverable corrections (CG-12.5) | §6 | Correction test: faulty row still readable post-correction; resolution returns v+1; `superseded_by_rule_id` stamped |
| Step-up with freshness + single-use (SG-12) | §8 | Expired/reused/foreign step-up event all rejected |
| One workflow regardless of origin (control §6) | §2.1 `origin` field only | C11-origin and human-origin fixtures traverse identical states |
| Date-driven resolution only (Stage 06 constraint) | §1/§6 — no "current rule" shortcut introduced | Grep/contract check: resolution always via `effective_from <= date` ordering |
| DQ-007 not pre-empted | §3 segregation enforced pending waiver | — |
| DQ-008 not pre-empted | no retention/purge mechanism anywhere in §2 | Design-review absence check |
