# Agentic Payroll Platform — Forward Plan

**This file holds only what has not been built.** Delivered history lives in `docs/ROADMAP.md`, which was frozen on 2026-07-29 and is never edited again. Per-story detail lives in `docs/product/`.

Created 2026-07-29 by the `roadmap-split` sprint (`STORY-0159`), executing the follow-up deferred under D-021.

---

## The labelling scheme

**New items get no code of their own. They are identified by their `STORY-<nnnn>`.**

That is the whole scheme, and it is deliberately subtractive. `docs/ROADMAP.md` accumulated 25+ ID prefixes across three organising principles, several of them colliding — `B` denotes both Track B "Schema Foundations" and Sprint 17's Track B items; `P1`/`P2` serve as both item prefixes and phase names. Inventing a 26th scheme would repeat the mistake in tidier handwriting. `STORY-<nnnn>` already exists, is unique, is never reused or renumbered, and resolves to a full record.

Three rules:

1. **A new item is added here only with its `STORY-<nnnn>` already allocated.** `/pm` allocates from `docs/product/ID-ALLOCATION.md` when scope is agreed. An item without one is not yet a plan item.
2. **Legacy codes are shown, never rewritten.** Every item carried over from the frozen roadmap keeps its original code verbatim in the *Legacy* column. Those codes are load-bearing — they appear in sprint files, test reports and audit records that are themselves frozen history.
3. **When an item is delivered, it leaves this file.** Its record in `docs/product/` becomes the history. Nothing is marked "done" here and left in place — that is the accretion habit that made the roadmap two documents.

Status is binary: an item is here, or it is delivered. There is no ✅ in this file.

---

## Phase 1 — open items

Everything below was open in `docs/ROADMAP.md` at the freeze. `Legacy` is the code it carried there.

### Correctness, audit & snapshot

| Story | Legacy | Item | Note |
|---|---|---|---|
| `STORY-0167` | `N1` · `WI-08` | Merge `_rule_trace` into `component_trace_jsonb`; add `rate_basis` | **`/arch-council` required** — extends a schema contract with live downstream consumers |
| `STORY-0164` | — | Expose snapshot content with a structured UI renderer | The audit trail exists and is unreadable outside the DB |
| `STORY-0165` | `P4-2` | Replay a run using its frozen snapshot | Recorded in both Phase 1b and Phase 3; which phase owns it was never settled |

### Execution engine

| Story | Legacy | Item | Note |
|---|---|---|---|
| `STORY-0168` | `N2` · `WI-03` | `ot_multiplier` rate-base reconstruction | **May already be fixed.** Sprint 14's ordering change resolved this item's sibling; nothing on record confirms whether it also resolved this half. Verify before scheduling. |
| `STORY-0169` | `O5` · `NEW-GAP11` | LTA anniversary trigger — auto-inject `paye_only` input | **Blocker cleared.** Deferred pending M2, which shipped as `STORY-0079`. The roadmap's stated reason for deferral is stale. |

### Governance & rule versioning

| Story | Legacy | Item | Note |
|---|---|---|---|
| `STORY-0162` | `P3-2` | View applicable statutory rules — read endpoint + UI | Must resolve date-driven (`effective_from <= date`), never by `is_active` — the Sprint A defect class |
| `STORY-0163` | `P3-2` | Statutory rule management UI for bureau operators | **`/arch-council` required** — writes a financially critical table under a UNIQUE constraint. Ship `STORY-0162` first. |

### Security

| Story | Legacy | Item | Note |
|---|---|---|---|
| `STORY-0166` | `S6` · `SEC-S5` | `proration_strategy` DB CHECK constraint | Partial: the API guard shipped. The DB half is the residual; the migration must pre-check for existing invalid rows. |

Track S is otherwise closed. `S7` and `S8`: `S7` was **delivered** (`STORY-0146`, ICM pilot sprint `sec-s7-timesheet-upload-guard`) — the frozen roadmap still shows it ⬜, which is one of two stale markers found at freeze. `S8` is backlogged as `STORY-0154`.

### Employee lifecycle

| Story | Legacy | Item | Note |
|---|---|---|---|
| `STORY-0171` | `EMP-REG-5-FIX` | Enrollment slide-over pre-population — normalised grade/designation matching | Must respect the Sprint 22 Upload/Enroll separation |
| `STORY-0170` | `EMP-VERIFY-1` | Browser verification of the auto-suggest banner | Verification debt from Sprint 23, against the Sprint 17 "PASS requires live execution" standard |

### Audit observations (Track Q)

| Story | Legacy | Item |
|---|---|---|
| `STORY-0151` | `Q2` · `AUD-2` | `period_type` on `payroll_run`, passed to retry context |
| `STORY-0152` | `Q3` · `AUD-3` | Simulate script — explicit `Decimal(str(...))` conversion |
| `STORY-0153` | `Q7` · `AUD-16-1` | `approved_by` actor identity on timesheet transitions |

`Q1` was **delivered** (`STORY-0145`, ICM pilot sprint `aud-q1-trace-source`) — the frozen roadmap still shows it 🔜. The second of the two stale markers. `Q5`, `Q6`, `Q8` are closed.

### Onboarding

| Story | Legacy | Item |
|---|---|---|
| `STORY-0150` | `PH-12` · `SHIFT2/3/4` · `O4` | Client 3 shift allowance onboarding (`basic_daily` base) — blocked on a stable Client 3 workspace identifier |

### Technical debt

| Story | Legacy | Item |
|---|---|---|
| `STORY-0154` | `S8` | Pin `python-multipart==0.0.28` |
| `STORY-0155` | — | Two deferred `/simplify` items — shared date utilities, shared rule loader |

---

## Phase 2 — Agent Layer

Reserved exclusively for the AI Agent Layer. **Not authorised.** Phase 1 must be delivered and closed first, per the project's `CLAUDE.md`.

| Track | Scope |
|---|---|
| `P` | Authentication — prerequisite for everything below |
| `V` | Agent foundation (after `P`) |
| `W` | Operator chat agent — Phase 2A (after `V`) |
| `X` | Proactive agents — Phase 2B (after `W`) |
| `Y` | Autonomous agents — Phase 2C |

**These carry no `STORY-<nnnn>`, deliberately.** `CAP-12` Agent Layer is held at **zero stories** by design under D-023/OQ-6, "retained so the unbuilt Phase 2 agentic work is visible as a named absence rather than an unstated one." Allocating IDs here would populate a capability whose emptiness is the point. Rule 1 above is suspended for Phase 2 until that decision is revisited.

Binding architecture decisions already exist for this phase (arch-council, 2026-06-11): 5 blocking conditions and the track structure `P`/`V`/`W`/`X`/`Y`. They gate any Phase 2 work.

**Also blocking:** the `agentic-architecture-review` programme is open at Stage 13 (`awaiting-human-decision`) with `DP-2` and `DP-9` pending since 2026-07-18. Phase 1 of that review is not complete, and no Phase 2 implementation is authorised until it is. Tracked as `STORY-0148`.

---

## Phase 3 — Platform Scale

Deferred until Phase 1 (including Tracks K–O) and Phase 2 are complete and a second client is onboarded. These sit outside the Phase 1 boundary, which keeps upstream data prep and downstream bank/tax/remittance work manual.

| Story | Legacy | Item |
|---|---|---|
| `STORY-0172` | `P4-1` | Employee payslip PDF generation and distribution |
| `STORY-0173` | `P4-3` | Life insurance — full employer cost reporting |
| `STORY-0174` | `P4-6` | Multi-tenant bureau scaling — a heading, not yet a scoped item |
| `STORY-0175` | — | Automated payroll scheduling (pay cycle scheduler) |

`STORY-0175` is worth a note. The **gap** — "`pay_cycle.definition_json` stored but unused in execution scheduling" — is recorded at the very top of the frozen roadmap as a Sprint 0 partial. The **fix** is recorded at the very bottom, in the Phase 3 list, under a different organising principle and with no link between them. That single item is the clearest illustration of why the roadmap's dual role was worth retiring.

---

## Known platform drift — not yet scheduled

Carried across several sessions; no story allocated, because each needs a decision before it needs a plan.

| Item | State |
|---|---|
| `docs/Buisness Specs & Designs (Drifted)/` | Stale since 11 June 2026. Two `.mmd` files there remain the repo's only untracked files — deliberately, since whether they are tracked is part of the decision. |
| Local dev DB drift | Drifted from migration truth (registry activation flips, missing constraints). CI is the arbiter — it builds fresh from `alembic upgrade head`. |
| `docs/ux-ui-design-brief/11-drift-log.md` | `DRIFT-1..n` open. |

---

## How to add an item

1. Run `/pm` to scope it. It allocates the next free `STORY-<nnnn>` from `docs/product/ID-ALLOCATION.md`.
2. Add a row to the right section here: `story_ref`, legacy code (`—` if forward-authored), one-line item, note if it carries a gate or a blocker.
3. When it ships, `/retro` completes its registry row and **the row is deleted from this file**.

Do not add a code prefix. Do not mark anything complete here. Do not edit `docs/ROADMAP.md`.
