# Stage 08: Technical Architecture — Decisions

Stage-local log. Master log of human decisions: `_core/HUMAN-DECISIONS.md`. Entries below are **executor design conclusions from evidence and inherited principles** (per the stage constraint: no artificial human decisions where inheritance already resolves the issue), except where marked otherwise. Under D-003 this stage runs decision-gated continuous — no per-stage human gate.

## Decisions log

| ID | Date | Decision | Basis |
|---|---|---|---|
| DEC-08-01 | 2026-07-17 | **Revocation posture (T3)**: 8-hour signed JWTs + server-side `auth_session` check on every request (immediate revocation); no refresh tokens in v1 | T3 required a stated posture; single-Postgres deployment makes the session lookup cheap; `auth-foundation-design.md` §1.3 |
| DEC-08-02 | 2026-07-17 | **Step-up freshness window = 5 minutes**; one approval per event via `consumed_by` compare-and-set | DEC-07-03 delegated the value ("minutes, not hours"); §1.5 of the auth design |
| DEC-08-03 | 2026-07-17 | **Audit reliability mechanism**: unit-of-work persistence facade — audit rows written in the state-change transaction; outbox (same transaction) carries event projection + notification delivery; `event_store` becomes projection-only | Satisfies "reliably written" in the strongest form; grounded in F-08-02; `event-audit-foundation-design.md` §2 |
| DEC-08-04 | 2026-07-17 | **Audit generalisation = signature generalisation** (one entity-typed builder with a registered entity-type enum), not parallel builders | Stage 06 left the choice open; parallel builders re-create the divergence problem; §3 of the event/audit design |
| DEC-08-05 | 2026-07-17 | **Immutability enforcement = triggers only** (role separation deferred); residual risk already accepted as DEC-07-04 | Threat model §4 allows it explicitly with the residual recorded; single-role deployment gains nothing else from role separation now |
| DEC-08-06 | 2026-07-17 | **Wrapper shape = decorator-registered `ToolRegistry`** (not middleware); workspace-parameter models rejected at startup; blocked tools absent from registry | Stage 07 left decorator-vs-middleware to this stage; fail-closed at import time is the stronger form of P3; `tool-contracts.md` §1 |
| DEC-08-07 | 2026-07-17 | **C5 null-trace behaviour = clean refusal** (`TRACE_UNAVAILABLE`), no degraded generic explanation (resolves F-03-15) | A generic explanation of a specific result is the exact ungrounded-output failure C5's constraint design exists to prevent; `tool-contracts.md` §3.5 |
| DEC-08-08 | 2026-07-17 | **C10 parameters**: TTL ceiling 7 days per action type; one live proposal per (target, action_type) — second proposal refused, not superseded; invalidation = eager event-driven + mandatory execution-time re-check (resolves DQ-002) | `confirmation-protocol-design.md` §3; silent supersession rejected on T7 grounds |
| DEC-08-09 | 2026-07-17 | **C12 correction mechanics = same-date replacement row with `version + 1`**; UNIQUE widens to `(country_code, effective_from, version)` — flagged as a Phase 3 arch-council data-contract change; supersede-in-place rejected | Grounded in F-08-01 (resolution tie-break pre-exists); control §5's recoverability satisfied by construction; `statutory-change-mechanism-design.md` §6 |
| DEC-08-10 | 2026-07-17 | **Impact preview implemented once, C12-side**, invoked by the Validator; C11 may call the same function for advisory summaries | Control §7's design freedom; one implementation removes advisory-divergence risk; §5 of the C12 design |
| DEC-08-11 | 2026-07-17 | **Dry run = real executor path; creates no `payroll_run` row**; results persist to a new workspace-scoped `dry_run_execution` artifact with input-hash commit linkage (resolves DQ-003/DQ-004, F-02-10) | Stage 05 feasibility evidence + the enum-overload prohibition; `dry-run-mechanism-design.md` §§1–3 |
| DEC-08-12 | 2026-07-17 | **C7 parameters (resolves DQ-001)**: median-ratio test, R_high 3.0 (CRITICAL at 10×), R_low ⅓, trailing window ≤ 6 periods, minimum history 3 nonzero periods; launch absolute ceilings incl. OT 100h; missing/zero-when-expected assigned to C6 | Within D-04-01's approved shape; small-n robustness reasoning in `anomaly-detection-design.md` §3 |
| DEC-08-13 | 2026-07-17 | **`legacy_executor_stats` moves to the platform-ops surface** (`PLATFORM_ADMIN`); `workspace_info()` + legacy admin HTML routes retired at C1 cut-over | Stage 07 handoff item 3's either/or and F-07-02's disposition; `remediation-designs.md` §§2, 4 |
| DEC-08-14 | 2026-07-17 | **Salary-definition edit-lock = application-layer check derived from the canonical status enum**, no duplicate DB trigger | Two independently-maintained status lists is the D-ARCH-1 drift pattern itself; `remediation-designs.md` §7 |
| DEC-08-15 | 2026-07-17 | **Retention (DQ-008 constraint honoured)**: no deletion/archival/purge mechanism designed in any Stage 08 schema; keep-at-least-7y posture throughout | Q9 answer; verified by absence across all outputs |

## Human decisions raised by this stage

**None.** No new blocking or non-blocking human decisions were created. DQ-006/007/008 remain queued unchanged (DQ-008's mechanism constraint honoured per DEC-08-15). DEC-08-09's data-contract change is a build-time governance item (arch-council at Phase 3), not a review-phase decision — the review only records that the change is required and deliberate.

## Next action

**Stage complete pending critic** — see `review-state.md`.
