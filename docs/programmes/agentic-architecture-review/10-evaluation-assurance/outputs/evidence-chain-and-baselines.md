# Stage 10 Output: Evidence-Chain Integrity & Baseline Instrumentation (Q6 + Q7)

Part A designs the chain-completeness checks over the audit linkage keys (Stage 08 assurance input 1) and the epoch-boundary discipline for assurance reporting. Part B designs the concrete baseline measurements for the named evidence gaps (EG-001–003 + the measurement framework's five gaps) that must precede capability launches.

---

## Part A — Evidence-chain integrity (Q6)

### 1. The chain, as designed by Stage 08

All stores are 7-year-floor, append-only. Linkage keys:

```
agent_session_log ──session_ref──▶ tool_call_log (SC-3 fields incl. sanitizer version)
tool_call_log / chat proposal ──pending_action_id──▶ C10 pending-action record ──▶ execution audit rows (outcome linkage)
statutory_change_proposal ──approval_id──▶ statutory_change_approval ──step_up_event_id──▶ step_up_event (consumed_by)
statutory_change_approval ──linkage──▶ applied statutory_rule version rows
exception_record transitions ──▶ domain-3 audit rows
```

A broken link converts evidence into assertion: a tool call with no resolvable session is unattributable narrative; an approval without its step-up event fails R4's record standard; an executed action without a terminal record is exactly the silence `approval-security-design.md` §4 forbids.

### 2. Two enforcement layers (DEC-10-12)

**Layer 1 — committed fixture tests (ET-1, per mechanism's build item):** every mechanism's tests assert its linkage fields are populated and resolvable on fixture data (already largely named in the register: terminal-record field assertions for C10, approval-record completeness for C12, SC-3 field-presence for tools). The chain-specific addition: cross-store resolvability assertions — e.g. the C12 approval fixture test resolves `step_up_event_id` to a `consumed_by`-consistent event, not merely asserts the column is non-null.

**Layer 2 — standing chain-completeness sweep (Class B, per release + monthly):** a scripted read-only query pack against the deployed database asserting **zero orphans** across six checks:

| # | Orphan check |
|---|---|
| 1 | `tool_call_log` rows whose `session_ref` resolves to no `agent_session_log` record |
| 2 | Pending actions in executed state with no terminal audit record (or terminal record with missing R4 fields) |
| 3 | `APPROVED` statutory proposals with no `statutory_change_approval` row |
| 4 | Approval rows whose `step_up_event_id` is dangling, or references an event not consumed by that approval |
| 5 | Consumed `step_up_event` rows referenced by ≠ 1 approval (single-consumption, the DB-level mirror of the SG-12 test) |
| 6 | `exception_record` rows in terminal states lacking their domain-3 transition audit rows |

Nonzero result → incident: an `exception_record` is opened (the platform's own workflow is the right container) and the cause dispositioned before the next release. The sweep record (dated, counts per check, DB identified) is committed per the Class B convention.

### 3. Epoch-boundary discipline for assurance reporting (DEC-10-13)

Single source: `platform_metadata.auth_cutover_epoch` (data, not prose — audit threat model §6 hardening 1).

- Any assurance query, report, or metric over historical audit data **must partition on the epoch**: pre-epoch rows are never counted as verified-identity evidence, never enter chain checks 2–5 (their linkage fields predate the mechanisms), and are labelled `identity unverified (pre-auth era)` in any report segment that includes them.
- Chain checks 1–6 therefore scope to post-epoch rows by construction — the sweep queries carry the epoch predicate from the single metadata source, not a hardcoded date.
- Every committed assurance report (sweep records, calibration reports, eval reports quoting audit data) states the epoch and its data source once in a header line.
- The presentation-layer counterpart is UX behaviour 23 (every audit surface incl. exports labels pre-epoch rows); the ET-1 epoch fixture test covers mechanics, behaviour 23 covers surfaces, this discipline covers *reports* — three layers, one epoch value.

---

## Part B — Baseline instrumentation plan (Q7)

### 1. Consolidated gap list

EG-001–003 and the measurement framework's five gaps overlap; consolidated to six distinct baselines. Per the measurement framework (binding): each must be measured **before** the corresponding capability ships, or improvement claims have no anchor. None is blocking today; each becomes blocking at its capability's launch (register ET-6 rows).

| ID | Baseline | Covers | Precedes launch of |
|---|---|---|---|
| B1 | Onboarding mapping time + error rate under `NativeUploadFlow` | EG-001; framework gap (C13) | C13 |
| B2 | Parallel-run agreement rate | EG-002; framework gap (C13/C14) | C13/C14 |
| B3 | Time-to-go-live for a new client | EG-003 | C13/C14 |
| B4 | Time-to-detection of readiness issues under the manual process | framework gap (C6) | C6 |
| B5 | Time-to-apply for a statutory change under the manual process | framework gap (C11/C12) | C11/C12 |
| B6 | Support/navigation question volume reaching a human | framework gap (C3) | C3 |

### 2. Capture design per baseline (DEC-10-14)

Pre-C2 reality: the event/notification foundation does not exist yet, so **manual observation protocols are the honest launch instrument** — lightweight, dated, artifact-producing. Instrumented (event-emitted) capture upgrades each baseline once C2's flow events exist; the protocol versions below are sufficient for launch gates.

- **B1 — mapping time/errors**: measured during each real onboarding (or bulk re-upload) that uses the current `NativeUploadFlow`, at Stage 09's flow boundaries (upload started → mapping panel opened → mapping confirmed → import committed — the Stage A/B/C boundaries of `onboarding-flow-experience.md`): wall-clock per boundary + count of mapping corrections made after first proposal. Protocol: one-page timing sheet per onboarding; artifact per observation. Post-C2: client flow events at the same boundaries replace the stopwatch.
- **B2 — parallel-run agreement**: for the next onboarding with a prior provider, compare the platform's first run (or C14 dry run, once it exists) against the incumbent's results for the same period: per-employee net-pay agreement rate + named causes for each disagreement. Artifact: comparison sheet. This baseline requires a real onboarding — it cannot be synthesized; scheduling around client intake is a Stage 11 sequencing note.
- **B3 — time-to-go-live**: engagement start date → first `APPROVED` run date. Computable retrospectively for existing Sandy clients from engagement records + `payroll_run` history; prospectively per new client. Artifact: one table, dates cited to sources.
- **B4 — readiness time-to-detection**: for each run over a 3-cycle window, record when a blocking condition (missing timesheet/inputs/config) was *first noticed* vs the run-creation attempt that surfaced it. Today's process finds these at run creation (Stage 04's qualitative baseline) — the protocol quantifies the lag: operator notes the discovery moment per incident; artifact per cycle. Zero-incident cycles are recorded as such (absence data is data).
- **B5 — statutory time-to-apply**: dates from official-change publication → rule live in production. **Retrospectively computable now for NTA 2025**: the Act's commencement/publication date vs the PAY-TAX-1 seed migration's deployment (git history + sprint records — the repo itself is the source). Plus prospective measurement of the next real statutory change under the manual process. Artifact: dated table citing the Act, the migration revision, and deploy evidence.
- **B6 — support-question volume**: 4-week operator tally (single-operator reality: a running note, categorised how-do-I / where-is / why-is-this-value) captured before C3's launch window. Artifact: the tally with week totals. Prohibition honoured: this baselines *questions reaching a human*; it never becomes a chat-usage success metric post-launch.

### 3. Reporting and register linkage

One **baseline register** table (this programme's folder until Phase 3 adoption): baseline ID | value | capture date(s) | artifact link | status (captured / pending / upgrade-to-instrumented). The evidence register's ET-6 rows point here; a capability's launch gate consumes the row's status. B5's retrospective portion and B3's retrospective portion are capturable immediately and are the cheapest first entries — noted to Stage 11 as near-zero-cost items that de-risk two launch gates early.
