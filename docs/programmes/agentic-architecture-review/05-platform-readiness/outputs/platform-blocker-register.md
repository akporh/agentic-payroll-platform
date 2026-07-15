# Stage 05 Output: Platform Blocker Register

Consolidated register of every blocker this stage confirmed, by severity. Cross-references the detailed assessment each blocker is drawn from.

## Critical severity

| Blocker | Finding | Status | Blocks |
|---|---|---|---|
| No authentication mechanism exists anywhere | New framing of a pre-existing gap, `event-notification-readiness.md` | Confirmed, unremediated | C1 itself, and transitively nearly every other capability |
| Event/notification/exception-tracking foundation entirely unbuilt | `event-notification-readiness.md` | Confirmed, unremediated | C2, C3, C6's surfacing, C7 (via D-04-01's binding condition), the exception-resolution workflow (F-04-01) |
| `payroll_reconciliation` workspace scoping — repo-level gap, plus decorative "scoped" routes | F-01-33, worsened per `reconciliation-scoping-assessment.md` | Confirmed, unremediated, one dimension newly identified as worse | C8, any `get_reconciliation` tool |
| Statutory-rule change-management mechanism entirely unbuilt | F-02-12, `statutory-change-platform-readiness.md` | Confirmed, unremediated | C12, and transitively C11's actionability |

## High severity

| Blocker | Finding | Status | Blocks |
|---|---|---|---|
| `salary_definition` edit-lock only at PAID, no DB-level in-progress lock | F-01-27, `historical-reproducibility-assessment.md` | Confirmed, unremediated | C4, C8 |
| D-ARCH-1 lock check has dead branches, status-vocabulary drift | F-01-38, `historical-reproducibility-assessment.md` | Confirmed, unremediated | C4, C8 |
| C12 required before C11 is actionable | F-02-12, `statutory-change-platform-readiness.md` | Confirmed sequencing dependency | C11 |
| C14 required before C13 (binding condition) | D-02, `onboarding-platform-readiness.md` | Confirmed, C14 lower-cost than feared | C13 |

## Medium severity

| Blocker | Finding | Status | Blocks |
|---|---|---|---|
| `component_trace_jsonb` null-guard missing at data-access layer (HTTP layer already fixed) | New, `tool-readiness-baseline.md` | Newly identified, narrow scope | Any future tool reading `payroll_result` directly |
| `load_inputs_for_run` has no workspace_id parameter | New, `tool-readiness-baseline.md` | Newly identified | Any future tool wrapping this function directly |
| `workspace_info()` picks an arbitrary workspace with no scoping | New, `tool-readiness-baseline.md` | Newly identified | Any future tool wrapping this function; possibly existing non-tool callers too |

## Low severity / narrowed since Stage 01

| Item | Finding | Status |
|---|---|---|
| `component_trace_jsonb` dual fallback-precedence ambiguity | F-01-29, `historical-reproducibility-assessment.md` | Confirmed unreachable in production (no live caller of the ambiguous function) — downgraded from Stage 01's framing |
| `employee.status` no DB CHECK constraint | Stage 01, `frontend-backend-alignment.md` | Unchanged, still low severity |
| `FULL_RUN` retry option still in UI | Stage 01/02, `frontend-backend-alignment.md` | Unchanged, launch-risk not blocker |
| `run_type` CORRECTION not in UI | Stage 01, `frontend-backend-alignment.md` | Unchanged, usability gap not blocker |

## Genuine progress since Stage 01 (not blockers — recorded for completeness)

| Item | Evidence |
|---|---|
| Retry statutory-rule source now snapshot-first, hard-fails instead of silently diverging | `snapshot-retry-integrity-assessment.md` — commit `68e9307`, regression-tested |
| `component_trace_jsonb` null handling fixed at the HTTP/UI surface | `tool-readiness-baseline.md`, `frontend-backend-alignment.md` |
| Dry-run mechanism has a proven, reusable pure-compute foundation (`simulate_payroll.py`) even though no product feature exists yet | `onboarding-platform-readiness.md` |

## Severity distribution

4 Critical, 4 High, 3 Medium, 4 Low-or-narrowed, plus 3 confirmed genuine improvements. The Critical items are dominated by foundational infrastructure (auth, event/notification, exception tracking) rather than by narrow bugs — this is the core message for Stage 06/07/08/11 to carry forward.
