# Phases — Agentic Architecture Review Programme

All three phases are defined here in advance for planning visibility. **Only `review-execution` is authorised.** No later phase may begin without a recorded human decision in `decisions.md` authorising it.

These are **programme phases**, not review stages. The 13 review stages all live inside Phase 1 and are governed by `WORKFLOW.md` and tracked in `review-state.md` — this file never duplicates stage-level state.

---

## Phase 1 — `review-execution`

**Status:** authorised and in flight (registered retrospectively by D-001, 2026-07-15 — the review began before programme registration; registration changes nothing about its stage governance). Stage position at registration: Stages 01–04 gated-closed, Stage 05 awaiting human review, Stages 06–13 not started. Authoritative stage state: `review-state.md`.

**Purpose:** Run review Stages 01–13 to gated completion under the review's own `WORKFLOW.md`, ending with Stage 13 (`approved-roadmap`) gated-closed.

**Allowed paths (read-write):**
```text
docs/programmes/agentic-architecture-review/
```

**Forbidden paths (read-only inputs; no writes):**
```text
backend/
frontend/
migrations/
docs/ROADMAP.md
docs/audit-program/
docs/product/
docs/sprints/
docs/stories/
docs/audit/
docs/security/
docs/test-reports/
docs/retro-reports/
docs/programmes/product-traceability/
~/.claude/ (user-home skills)
requirements.txt, package.json, and all lockfiles
```
All paths not explicitly listed under "Allowed paths" are implicitly forbidden for writes.

**Required inputs:** the system under review (backend/frontend/migrations, read-only), `docs/audit-program/` confirmed findings (citable per stage `CONTEXT.md` rules), git history, and each stage's declared inputs.

**Required outputs:** each stage's `findings.md`, `decisions.md`, and `outputs/` per `WORKFLOW.md`; gate records in `_core/HUMAN-DECISIONS.md`; `review-state.md` kept current at every stage transition.

**Human gate:** **per stage** — every stage gate is an explicit human approval (`HD-GATE-*`). Phase 1 completes when Stage 13 is gated-closed.

**Executor responsibilities:** investigate and record findings to the evidence standard; never open a stage early; keep `review-state.md` truthful; do not begin Phase 2.

---

## Phase 2 — `roadmap-consolidation`

**Status:** not authorised

**Purpose:** Cross-reference the Stage 13 approved roadmap with the audit programme's Stage 13 backlog (S0/S1 release gate + 8 sequenced remediation programmes) and `docs/ROADMAP.md`, producing a single reconciled build order plus a decision pack for every genuine conflict or sequencing choice. Nothing from either source may be dropped silently — every item is explicitly placed, deferred, or surfaced as a decision.

**Allowed paths:** to be defined at authorisation time — expected to remain within this programme's folder (consolidation is a document, not an edit to either input).

**Forbidden paths:** `docs/audit-program/` (never rewritten), `docs/ROADMAP.md` (input only at this phase), production code, all completed history.

**Required inputs:** Stage 13 outputs of this review; `docs/audit-program/13-consolidated-remediation-backlog/` and `audit-state.md`; `docs/ROADMAP.md`.

**Required outputs / validations / critic arrangements:** to be defined at authorisation time.

**Human gate:** **after** — the reconciled build order and decision pack go to the human; nothing is adopted in this phase.

---

## Phase 3 — `adoption`

**Status:** not authorised

**Purpose:** Adopt the approved build order into the product hierarchy (`docs/product/` — forward-looking initiatives/epics/features under the product-traceability programme's conventions) and update `docs/ROADMAP.md` to match, with traceability from each adopted item back to the review/audit finding(s) justifying it.

**Allowed paths:** to be defined at authorisation time — expected to include `docs/product/` and `docs/ROADMAP.md`, which are currently forbidden and would require an explicit re-scoping decision, coordinated with the product-traceability programme (whose own Phase 5 owns sprint-workflow integration).

**Forbidden paths:** production code, `docs/audit-program/`, all completed sprint/story/audit history.

**Required inputs:** Phase 2's approved build order.

**Required outputs / validations / critic arrangements:** to be defined at authorisation time.

**Human gate:** **before and after** — explicit authorisation of the exact allowed-path expansion before any file is written; human review of the adopted structure before the programme closes.

---

## Cross-phase note

Phases 2–3 are placeholders for planning visibility only. Their "Allowed paths," "Required outputs," and validation sections are deliberately left as "to be defined at authorisation time," so that authorising a phase is always an explicit, current decision — not a rubber stamp of a scope written before Phase 1's findings were known.
