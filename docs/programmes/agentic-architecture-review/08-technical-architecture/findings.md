# Stage 08: Technical Architecture — Findings

Schema: `_core/FINDING-SCHEMA.md`, extended with the Stage 05/06 field pattern (consequence / classification / minimum remediation / closure evidence / confidence / required human decision / downstream owner) per the stage context. Evidence pinned at commit `573be0d` (2026-07-17). Draft and confirmed findings are kept in separate sections below — never merge them.

## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

_None._

---

## Confirmed Findings

(meet the evidence standard in `_core/EVIDENCE-STANDARD.md` — safe to cite from later stages)

### F-08-01: Statutory-rule resolution already tie-breaks by `version DESC` — the correction path's resolution semantics pre-exist

- **Current implementation**: the run-time statutory resolution query is `WHERE sr.effective_from <= :as_of_date ORDER BY sr.effective_from DESC, sr.version DESC LIMIT 1` (`backend/api/routes/payroll.py:272-282`). The `version DESC` tie-break is present in committed code but unreachable for a single country today because `uq_statutory_rule_country_effective (country_code, effective_from)` (`backend/infra/db/models/statutory_rule.py:9-11`) forbids two rows at one date. Test fixtures already rely on version-ordered resolution ("high version wins ORDER BY version DESC" — Stage 05's re-verified observation).
- **Intended design**: undocumented — no design document states why the tie-break exists ahead of any mechanism that could produce ties.
- **Identified gap**: none as a defect — recorded because it is load-bearing for design: same-date correction rows with `version + 1` resolve correctly with **zero change to resolution code**, making the replacement-row correction mechanics (`outputs/statutory-change-mechanism-design.md` §6) the evidence-grounded choice. The UNIQUE constraint must widen to `(country_code, effective_from, version)` — a deliberate data-contract change flagged for Phase 3 arch-council governance.
- **Evidence**: direct code read, paths/lines above, at `573be0d`; excerpt in `evidence/08-code-grounding-excerpts.md` §1.
- **Consequence / downstream owner**: C12 build (Phase 3); Stage 13 sequencing.
- **Severity**: Info (design-enabling fact). **Confidence**: high. **Required human decision**: none at this stage (the contract change is decided at build authorisation with arch-council per standing repo rules).
- **Status**: confirmed · **Date**: 2026-07-17 · **Raised by**: Stage 08 (C12 mechanism design)

### F-08-02: The run persister commits state, results, audit, and events in four-plus separate transactions

- **Current implementation**: `persist_payroll_run_execution` (`backend/application/payroll_run_persister.py:70-110`) calls `finalise_payroll_run` (`payroll_run_repo.py:94`), `save_payroll_results_bulk` (`payroll_result_repo.py:37`), then loops `save_audit_log` (`audit_log_repo.py:25-75`) and `save_event` (`event_store_repo.py:7-40`) — each repo opens its own `SessionLocal` and commits independently. The run header, its results, its audit rows, and its events are not atomic with each other.
- **Intended design**: the architecture document's own outbox direction (Blocking Condition 3) implies transactional coupling; Stage 06's "reliably written" property (audit-expansion §3.2) requires it.
- **Identified gap**: F-06-02 (fire-and-forget audit writes) is the audit-specific case of a broader pattern — the whole persistence layer is multi-transaction. Consequence: the C2 mechanism is a **rework of the persister layer onto a unit-of-work facade**, not an add-a-table patch; any design that kept per-repo sessions would fail the SG-2 forced-failure test by construction.
- **Evidence**: direct code read, paths/lines above, at `573be0d`; excerpt in `evidence/08-code-grounding-excerpts.md` §2.
- **Classification**: implementation-shaping fact. **Minimum remediation**: the facade design (`outputs/event-audit-foundation-design.md` §2). **Closure evidence**: the forced-failure atomicity test (SG-2). **Downstream owner**: C2 build (Phase 3).
- **Severity**: High (inherits F-06-02's severity basis; widens its scope statement). **Confidence**: high. **Required human decision**: none.
- **Status**: confirmed · **Date**: 2026-07-17 · **Raised by**: Stage 08 (C2 mechanism design)

### F-08-03: All load-bearing Stage 05/06/07 line citations re-resolve unchanged at `573be0d`

- **Current implementation**: re-verified by direct read/grep at `573be0d`: caller-supplied actor inputs at `payroll.py:992, 1009, 1180, 1207, 1227, 1257, 1359-1365`; hardcoded `entity_type`/`aggregate_type = "PAYROLL_RUN"` at `audit_events.py:34, 60`; unscoped reconciliation model/repo/service and the three decorative scoped routes now at `payroll.py:1327-1369` with `get_run_timeline` at `1371` and `legacy_executor_stats` at `1378`; `statutory_rule` model without provenance columns (`statutory_rule.py:7-23`); trigger precedent `3da637afb11b` unchanged.
- **Intended design**: n/a — citation-currency check required by the stage context ("re-resolve at this stage's own commit where needed").
- **Identified gap**: none — no drift between `ea1590a` and `573be0d` in any consumed citation (the two intervening commits were documentation-only).
- **Evidence**: direct code reads/greps at `573be0d`; excerpt in `evidence/08-code-grounding-excerpts.md` §3.
- **Severity**: Info. **Confidence**: high. **Required human decision**: none.
- **Status**: confirmed · **Date**: 2026-07-17 · **Raised by**: Stage 08 (context grounding pass)

---

## Parked / Rejected

_None._

## Next action

**Stage complete pending critic** — see `review-state.md`.
