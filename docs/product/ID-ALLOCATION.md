# ID Allocation & Coverage Map

Every known item of delivered (or explicitly backlogged) work, with its reserved `STORY-<nnnn>` identifier and feature assignment. **157 items.**

This file answers *"what exists, and how much of it is recorded?"* — `STORY-REGISTRY.md` answers *"what has a full record?"* An item here with no registry row has a reserved identifier and a feature assignment and nothing else: **migrating it is Phase 4 work and remains unauthorised.**

Created 2026-07-28 under D-023/D-024. Extended to 157 by D-026.

## How IDs were allocated (D-019)

The identifier is a **handle, not a sort key** — it encodes nothing. Chronology lives in the `sprint_refs` column of `STORY-REGISTRY.md` and in the section headings below, and sorts independently.

1. The seed pass ran once, in **chronological delivery order**, across every known item.
2. Ties within a delivery bucket break by capability area, then by original inventory ID.
3. Forward allocation is strictly sequential on entry, regardless of date.
4. **Never renumber, never reuse.** A later-discovered historical item takes a high number despite being early — that is correct, and the date fields carry the truth.
5. A merge or split (human approval required) **retires** an identifier rather than reusing it.

Bucket ordering within June 2026 is approximate — several fix sprints carry only a month, not a day. This is a documented convenience, not a claim about exact sequence.

## Legend

**●** migrated, has a story file · **○** allocated only
Confidence: `C` confirmed · `S` strongly inferred · `T` tentative · `B` backlog, not delivered

---

## Sprint 0 — Foundation
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0001` | `PT-A3-01` | List valid/unclaimed input codes; delete staged input; download template | `FEAT-12` | T | ● |
| `STORY-0002` | `PT-A3-02` | Stage input against specific past month / period-agnostic | `FEAT-12` | T | ● |
| `STORY-0003` | `PT-A3-03` | Block future inputs from being claimed | `FEAT-12` | T | ● |
| `STORY-0004` | `PT-A4-01` | Claim variable inputs at run time; canonical component execution order | `FEAT-18` | T | ● |
| `STORY-0005` | `PT-A4-02` | Prorate pay for partial-period employees | `FEAT-20` | T | ● |
| `STORY-0006` | `PT-A4-03` | Freeze period context at run start; Decimal precision | `FEAT-18` | T | ● |
| `STORY-0007` | `PT-A4-04` | PAYE computed on taxable income not gross | `FEAT-19` | T | ● |
| `STORY-0008` | `PT-A5-01` | State-machine enforcement, forward-only progression, initial DRAFT | `FEAT-29` | T | ● |
| `STORY-0009` | `PT-A5-02` | Dedup runs by idempotency key/period; dedup per-employee results | `FEAT-29` | T | ● |
| `STORY-0010` | `PT-A6-01` | Reconciliation status view | `FEAT-32` | T | ● |

## Sprints 1–6 — Core MVP
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0011` | `PT-A1-03` · `P3-7` | Workspace creation + country-code statutory-rule validation | `FEAT-6` | S | ● |
| `STORY-0012` | `PT-A1-04` · `P1-8` | Component overrides update endpoint | `FEAT-3` | S | ● |
| `STORY-0013` | `PT-A1-05` · `PC4` | Active pay-cycle guard, one active per workspace | `FEAT-6` | S | ● |
| `STORY-0014` | `PT-A1-06` · `P3-1` | Payroll rules as a standalone form, not raw JSON | `FEAT-3` | S | ● |
| `STORY-0015` | `PT-A1-12` · `P3-5` | Salary definition effective-date enforcement at run time | `FEAT-3` | S | ● |
| `STORY-0016` | `PT-A3-04` · `INP10` | Single payroll input negative-quantity guard | `FEAT-12` | S | ● |
| `STORY-0017` | `PT-A3-05` · `P3-3` | Bulk upload inputs with dedup guard | `FEAT-14` | S | ● |
| `STORY-0018` | `PT-A4-05` · `P1-7` | Run payroll with period_type / working_days_override / retry_strategy UI | `FEAT-18` | S | ● |
| `STORY-0019` | `PT-A4-06` · `P2-7` | Historical input-rate resolution with fallback flagging | `FEAT-22` | S | ● |
| `STORY-0020` | `PT-A4-07` · `P0-2`/`P1-1` | Retry failed employees; full-run retry; retry recalculates totals | `FEAT-23` | S | ● |
| `STORY-0021` | `PT-A4-08` · `P2-3` | Retry writes to audit_log + event_store | `FEAT-23` | S | ● |
| `STORY-0022` | `PT-A4-09` · `P1-6` | Execution trace / timeline view | `FEAT-25` | S | ● |
| `STORY-0023` | `PT-A4-10` · `SR9` | NHF key fix, employee_rate | `FEAT-19` | S | ● |
| `STORY-0024` | `PT-A5-03` · `P0-1` | Approve / Lock / Mark-paid UI buttons | `FEAT-29` | S | ● |
| `STORY-0025` | `PT-A5-04` · `P2-1` | Read run audit trail + event store history | `FEAT-30` | S | ● |
| `STORY-0026` | `PT-A5-05` · `G7` | Statutory rule effective_from UNIQUE constraint | `FEAT-31` | S | ● |
| `STORY-0027` | `PT-A6-02` · `P0-4`/`P0-5` | Reconciliation gated to LOCKED/PAID; duplicate 409 not 500 | `FEAT-32` | S | ● |
| `STORY-0028` | `PT-A6-03` · `RC5` | Correct a MISMATCH — RESOLVED status + PATCH | `FEAT-32` | S | ● |
| `STORY-0029` | `PT-A7-01` · `P2-4`/`P2-7` | Component-level calculation trace in UI; rule trace | `FEAT-1` | S | ● |
| `STORY-0030` | `PT-A7-02` · `P2-6` | rule_set effective_from UNIQUE; cross-period rule set access | `FEAT-26` | S | ● |
| `STORY-0031` | `PT-A7-03` · `P2-4` | Per-employee calculation steps snapshot, component_trace_jsonb | `FEAT-1` | S | ● |
| `STORY-0032` | `PT-A7-04` · `G12` | Legacy executor observability — deprecation warning + metrics | `FEAT-28` | S | ● |

## Sprint 7 — including Track A defect fixes
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0033` | `PT-A3-06` · `INP10` | Quantity ≥ 0 DB CHECK constraint on `payroll_input` | `FEAT-12` | S | ● |
| `STORY-0034` | `PT-A4-14` · `FIX-1`–`FIX-5` | Track A mandatory defect fixes | `FEAT-24` | S | ● |
| `STORY-0035` | `PT-A1-01` · `PH-1`…`PH-11` | Workspace-configurable public-holiday engine | `FEAT-7` | S | ● |
| `STORY-0036` | `PT-A1-02` · `PH-7` | Rate code registry + OT multiplier seeding | `FEAT-7` | S | ● |
| `STORY-0037` | `PT-A4-15` · `PH-2`/`PH-9` | expected_hours / expected_days computed PH-aware | `FEAT-21` | S | ● |
| `STORY-0038` | `PT-A4-16` · `PH-3`/`PH-4` | OT3 3.25× calculation flowing into GROSS_PAY/PAYE | `FEAT-21` | T | ● |
| `STORY-0039` | `PT-A4-17` · `PH-5` | Manual OT3 adjustment with floor validation | `FEAT-21` | S | ● |
| `STORY-0040` | `PT-A4-18` · `PH-10`/`PH-11` | PH count-mismatch warnings + pre-flight check | `FEAT-21` | S | ● |
| `STORY-0041` | `PT-A5-06` · `P2-2` | X-Performed-By header read on approve/lock/retry routes | `FEAT-30` | T | ● |
| `STORY-0042` | `PT-A7-09` · `PH-9` | Snapshot expected_days / ph_dates_used / ph_source in trace header | `FEAT-1` | S | ● |
| `STORY-0043` | `PT-A7-10` · `FIX-5` | Retry context carries OT/PH keys from snapshot | `FEAT-26` | S | ● |

## Track UI — Gates 1–2 (April 2026)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0044` | `PT-UI-01` | Gate 1 — UX/UI design brief, 18 decisions, 45-component inventory | `FEAT-15` | S | ● |
| `STORY-0045` | `PT-UI-02` | Gate 2 — Design system tokens + 45 React components | `FEAT-15` | S | ● |

## Track J / Gate 6 — Post-onboarding config (2026-04-21)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0046` | `PT-A1-07` · `WC-1` | Pay-cycle post-setup update endpoint | `FEAT-3` | C | ● |
| `STORY-0047` | `PT-A1-08` · `WC-2/3/4/5` | Grade / designation add + edit via UI | `FEAT-3` | C | ● |
| `STORY-0048` | `PT-A1-09` · `WC-6/7` | Salary definition add + edit via UI | `FEAT-3` | C | ● |
| `STORY-0049` | `PT-A1-10` · `WC-8` | Payroll rule active/inactive control via UI | `FEAT-3` | C | ● |
| `STORY-0050` | `PT-A1-11` · `WC-10/11` | Statutory component override edit/toggle via UI | `FEAT-3` | C | ● |
| `STORY-0051` | `PT-A1-15` | `client_component_metadata` add is_active + proration_strategy | `FEAT-3` | C | ● |
| `STORY-0052` | `PT-A1-16` · `D-ARCH-2` | Statutory component hard reject on override PATCH | `FEAT-3` | C | ● |
| `STORY-0053` | `PT-A1-17` | Extend `/configuration` GET with IDs / is_active / proration_strategy | `FEAT-3` | C | ● |
| `STORY-0054` | `PT-A1-18` | WorkspaceConfig.tsx full interactive overhaul (Gate 6) | `FEAT-3` | C | ● |
| `STORY-0055` | `PT-UI-06` | Gate 6 — Post-onboarding config management overhaul (frontend) | `FEAT-16` | C | ● |
| `STORY-0056` | `PT-UI-03` | Gate 3 — Operator journey, 6 screens + 6 amendments | `FEAT-16` | S | ● |
| `STORY-0057` | `PT-UI-04` | Gate 4 — Bureau / workspace-setup journey, 8 pages | `FEAT-16` | T | ● |

## Sprint 9 — Client B
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0058` | `PT-A6-07` · `S9-1/2` | Export full payroll detail | `FEAT-33` | S | ● |

## Sprint 10 — Client B fixes, exports, onboarding integration
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0059` | `PT-A1-13` · `PH-8`/`WI-05` | ot_multiplier rules onboarding via Excel/JSON | `FEAT-7` | S | ● |
| `STORY-0060` | `PT-A1-43` · `WI-06`/`H2` | WorkspacePayrollConfig onboarding integration, 7th Excel sheet | `FEAT-6` | S | ● |
| `STORY-0061` | `PT-A1-44` · `WI-12` | PH_ADDITIVE removed from UI, fallback to LEAVE_ABSORBS_PH | `FEAT-7` | S | ● |
| `STORY-0062` | `PT-A1-45` · `WI-01` | OT multiplier seed correction — closed by confirming a non-defect | `FEAT-7` | T | ● |
| `STORY-0063` | `PT-A1-46` · `WI-02` | ot_code → rate_code normalisation | `FEAT-7` | S | ● |
| `STORY-0064` | `PT-A1-47` · `WI-05` | Excel ot_multiplier rule-type parsing | `FEAT-7` | S | ● |
| `STORY-0065` | `PT-A4-11` · `K1` | GAP-2: remove double-subtraction of PH days in AUTOMATIC mode | `FEAT-24` | C | ● |
| `STORY-0066` | `PT-A4-12` · `K2` | GAP-5: PAYE CUSTOM annualization ×12 fix | `FEAT-24` | C | ● |
| `STORY-0067` | `PT-A4-13` · `K3`/`WI-04a` | fixed_amount component_source fallback fix | `FEAT-24` | C | ● |
| `STORY-0068` | `PT-A6-04` · `P0-3` | Export net pay for bank upload | `FEAT-33` | C | ● |
| `STORY-0069` | `PT-A6-05` · `P1-4` | Export PAYE remittance schedule | `FEAT-33` | C | ● |
| `STORY-0070` | `PT-A6-06` · `P1-5` | Export pension contribution schedule | `FEAT-33` | C | ● |

## Sprint 11 — Employee schema & shift gating
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0071` | `PT-A1-19` · `NEW-GAP4/13` | Employee schema: shift_type, state_of_tax, skill_level | `FEAT-4` | C | ● |
| `STORY-0072` | `PT-A1-20` · `NEW-GAP12` | Grade percentage structure | `FEAT-4` | C | ● |
| `STORY-0073` | `PT-A4-19` · `WI-04b` | Shift-gated OT rule; shift_type threaded per employee | `FEAT-21` | C | ● |
| `STORY-0074` | `PT-A4-20` | Retry-path input / rate-code fixes | `FEAT-23` | C | ● |
| `STORY-0075` | `PT-A7-05` · `AUD-4`/`Q4` | shift_type / salary_basis added to `_period_context` | `FEAT-1` | C | ● |
| `STORY-0076` | `PT-S-04` · `SEC-S4` | workspace_id filter on grade query, cross-workspace leakage fix | `FEAT-35` | C | ● |
| `STORY-0077` | `PT-S-05` · `SEC-S5` | shift_type / state_of_tax / skill_level enum + length guards | `FEAT-34` | C | ● |

## Sprint 12
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0078` | `PT-A4-21` · `NEW-GAP14`/`M1` | Non-taxable component class | `FEAT-19` | C | ● |
| `STORY-0079` | `PT-A4-22` · `NEW-GAP15`/`M2` | PAYE-only additions path, input_category | `FEAT-19` | C | ● |

## Sprint 13
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0080` | `PT-A4-23` · `NEW-GAP6`/`M3` | Check-off dues handler, percentage_of_sum | `FEAT-19` | C | ● |
| `STORY-0081` | `PT-A4-24` · `GAP-10-FIX`/`M4` | Life insurance flat-amount handler | `FEAT-19` | S | ● |
| `STORY-0082` | `PT-A4-25` · `NEW-GAP7`/`M5` | NSITF / ITF employer-cost handlers, threshold-gated | `FEAT-19` | S | ● |
| `STORY-0083` | `PT-S-01` · `SEC-S1` | Generic message + server-side log for `_wpc_err!s` | `FEAT-34` | S | ● |
| `STORY-0084` | `PT-S-02` · `SEC-S2` | Allowlist validation for workspace_payroll_config enums | `FEAT-34` | S | ● |
| `STORY-0085` | `PT-S-03` · `SEC-S3` | Module-level logging import fix | `FEAT-34` | S | ● |

## Sprint 14
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0086` | `PT-A4-26` · `P1` | Workspace-configurable hire / termination proration | `FEAT-20` | C | ● |
| `STORY-0087` | `PT-S-06` · `SEC-S6` | proration_strategy enum validation, API guard — DB constraint still open | `FEAT-34` | T | ● |

## Sprint 15 (design) / Sprint 16 (delivery) — Timesheet layer
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0088` | `PT-A1-42` · `TM-1` | Workspace timesheet configuration + attendance code seeding | `FEAT-5` | C | ● |
| `STORY-0089` | `PT-A1-41` · `TM-7` | Attendance code + policy configuration, CRUD + immutability | `FEAT-5` | C | ● |
| `STORY-0090` | `PT-A3-07` · `TM-2` | Timesheet upload — parsing, matching, code validation, PH header | `FEAT-13` | C | ● |
| `STORY-0091` | `PT-A3-08` · `TM-3` | Timesheet derivation — three-step cap formula | `FEAT-13` | C | ● |
| `STORY-0092` | `PT-A3-09` · `TM-4` | Manual OT override, source=MANUAL_OT | `FEAT-13` | C | ● |
| `STORY-0093` | `PT-A3-10` · `TM-5` | Timesheet-to-pay-instruction flow, atomic approval + readiness gate | `FEAT-13` | C | ● |
| `STORY-0094` | `PT-A3-11` · `TM-6` | Timesheet audit trail — derivation summary, policy snapshot, per-day grid | `FEAT-13` | C | ● |
| `STORY-0095` | `PT-A3-12` · `C1` | Per-employee expected_hours from shift_type | `FEAT-13` | C | ● |
| `STORY-0096` | `PT-A3-13` · `C2` | Timesheet completeness gate before link_inputs_to_run | `FEAT-13` | C | ● |
| `STORY-0097` | `PT-A7-06` · `AUD-16-3`/`Q5` | timesheet_source added to `_period_context` | `FEAT-1` | C | ● |
| `STORY-0098` | `PT-UI-05` · `UI-NAV-1/2/3` | Gate 5 — Navigation modernisation + Rate Codes page | `FEAT-17` | C | ● |

## 2026-05-26 — Retrospective delivery increment
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0099` | `PT-A1-28` · `EMP-01+` | Employee page enhancements: contract dates, colour-coded warnings | `FEAT-11` | C | ● |
| `STORY-0100` | `PT-A1-29` | Nav reorder + employee-mismatch badge | `FEAT-17` | S | ● |

## Sprint 17 — Employee lifecycle refactor (2026-05-27)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0101` | `PT-A1-21` · `EMP-B1` | Employee CRUD API + D-ARCH-1 run-lock / backdating guard | `FEAT-4` | C | ● |
| `STORY-0102` | `PT-A1-22` · `EMP-B2` | Unified employee creation path via employee_repo | `FEAT-4` | C | ● |
| `STORY-0103` | `PT-A1-23` · `EMP-B3` | Employees.tsx split-action rework — browser UAT BLOCKED | `FEAT-11` | T | ● |
| `STORY-0104` | `PT-A1-24` · `EMP-B0a` | Fix LATERAL join in readiness service for multi-contract employees | `FEAT-8` | C | ● |
| `STORY-0105` | `PT-A1-24` · `EMP-B0b` | Fix LATERAL join in timesheet derivation — multi-contract verification BLOCKED | `FEAT-13` | T | ● |
| `STORY-0106` | `PT-A1-25` · `EMP-UX-1` | Split Edit vs Change Grade/Salary row action | `FEAT-11` | C | ● |
| `STORY-0107` | `PT-A1-26` · `EMP-UX-3` | Mid-period hire warning in AddEmployeeSlideOver | `FEAT-11` | S | ● |
| `STORY-0108` | `PT-A1-27` · `EMP-UX-4` | Payroll Inputs issues badge | `FEAT-17` | S | ● |

`STORY-0104` and `STORY-0105` are the two halves of `PT-A1-24`, split under D-023 (OQ-8) because the item carried mixed confidence — B0a confirmed, B0b's multi-contract verification blocked. Both retain `PT-A1-24` as an origin code. The split is vindicated by the halves belonging to different features.

## Sprint 22 — Bulk upload / enroll separation
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0109` | `PT-A1-40` · `EMP-BULK-1/2/3` | Bulk upload / bulk enroll separation | `FEAT-10` | S | ● |

## Sprint 24 — Enrollment UX clarity + audit fixes
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0110` | `PT-A1-30` · `EMP-UX-5` | AlertBanner + nav badge when canEnroll=false | `FEAT-8` | S | ● |
| `STORY-0111` | `PT-A7-07` · `Q6-FIX` | Guard APPROVED timesheet re-upload | `FEAT-27` | C | ● |
| `STORY-0112` | `PT-A7-08` · `Q8-FIX` | proration_strategy frozen in snapshot — closed by confirming existing behaviour | `FEAT-26` | C | ● |

## Sprint 25 — Badge real-time update + Employees table UX (2026-06-10)
*Absent from the discovery inventory; captured 2026-07-28 under D-024.*

| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0113` | `BADGE-RT-1` | Payroll Inputs sidebar badge reflects live pending count on mutations | `FEAT-17` | C | ● |
| `STORY-0114` | `BADGE-RT-2` | Badge shows total pending inputs, not just issue inputs | `FEAT-17` | C | ● |
| `STORY-0115` | `EMP-TABLE-1` | Employees table UX: start/end dates visible, column alignment, inactive styling | `FEAT-11` | C | ● |
| `STORY-0116` | `EMP-TABLE-2` | "No longer active" state surfaced; contract end date editable | `FEAT-11` | C | ● |
| `STORY-0117` | `EMP-TABLE-3` | Register employee: contract start/end date fields in AddEmployeeSlideOver | `FEAT-4` | C | ● |

## Sprint 26 — Employee registration & status management (2026-06-11)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0118` | `PT-A1-31` · `EMP-ENROLL-AUTODEF-1` | Enrollment auto-suggest salary def from grade label | `FEAT-8` | S | ● |
| `STORY-0119` | `PT-A1-32` · `EMP-REG-1` | Register new employee full form | `FEAT-4` | S | ● |
| `STORY-0120` | `PT-A1-33` · `EMP-EDIT-1` | Edit employee — name / number / TIN / RSA / bank | `FEAT-4` | S | ● |
| `STORY-0121` | `PT-A1-34` · `EMP-STATUS-1` | Status toggle ACTIVE↔INACTIVE with payroll-exclusion warning | `FEAT-9` | S | ● |
| `STORY-0122` | `PT-A1-35` · `EMP-BADGE-1` | Per-row payroll readiness badge | `FEAT-8` | S | ● |
| `STORY-0123` | `PT-A1-36` · `EMP-ICONS-1` | Consistent icon set + payroll actions surfaced from row | `FEAT-9` | S | ● |

## Sprint 27 — Smart native upload
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0124` | `PT-A1-37` · `EMP-NATIVE-1` | Smart employee upload — alias header detection, mapping panel | `FEAT-10` | S | ● |
| `STORY-0125` | `PT-A3-14` · `INP-NATIVE-1` | Smart period-inputs upload — header parsing, @rate derivation, dedup | `FEAT-14` | S | ● |
| `STORY-0126` | `PT-A3-15` · `INP-MULTI-1` | Multi-row period input entry SlideOver | `FEAT-12` | S | ● |
| `STORY-0127` | `PT-A3-17` · `PAY-RECON-1` | Payroll reconciliation upload — mapping, comparison, mismatch filter | `FEAT-14` | S | ● |

## Sprint 28 — Upload error visibility
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0128` | `PT-A3-16` · `UPLOAD-SKIP-1` | Period-inputs bulk upload idempotency — IntegrityError → silent skip | `FEAT-14` | S | ● |

## 2026-06 — Fix sprints
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0129` | `PT-A1-38` · `EMP-REG-5` | Enrollment pre-population normalisation fix | `FEAT-8` | C | ● |
| `STORY-0130` | `PT-A1-39` · `WS-ACTIVATE-1/2/3` | Workspace activation CTA reachable from 3 landing points | `FEAT-8` | C | ● |

## Sprint PAY-TAX-1 — NG PAYE bands NTA 2025 (2026-06-20)
*Absent from the discovery inventory; captured 2026-07-28 under D-024.*

| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0131` | `PAY-TAX-1` | NG PAYE thresholds and rates corrected to the NTA 2025 schedule (migration `de1f2a3b4c5d`) | `FEAT-19` | C | ● |

## Sprint RULE-VER-1 (2026-06-21)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0132` | `PT-A5-07` · `RULE-VER-1/2/3` | Payroll rule versioning: effective_from, auto-publish, UNIQUE | `FEAT-31` | C | ● |

## Sprint A — Rule versioning integrity (2026-07-04)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0133` | `PT-A4-28` | Date-aware payroll-input-codes-by-date endpoint | `FEAT-22` | S | ● |
| `STORY-0134` | `PT-A4-29` | Legacy-workspace historical fallback in cross-period prefetch | `FEAT-22` | C | ● |
| `STORY-0135` | `PT-A4-30` | Date cap + DISTINCT ON on legacy current-period rule loader | `FEAT-22` | C | ● |

## Sprint B-UI — Rule versioning copy cleanup
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0136` | `PT-A5-08` · `B-UI-1/2/3` | WITHDRAWN status badge + one-way withdraw action | `FEAT-31` | C | ● |
| `STORY-0137` | `PT-UI-07` · `B-UI-4/5` | Stale copy / banner cleanup on Payroll Rules tab | `FEAT-17` | C | ● |

## Sprints 29–32 — Delivery infrastructure
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0138` | `PT-X-01` · `PIPE-1/2/3` | Dead branch cleanup, CI gate on merge, branch protection | `FEAT-38` | S | ● |
| `STORY-0139` | `PT-X-02` · `HARN-1` | Test-fixture scaffold: conftest, db / workspace / employee fixtures | `FEAT-37` | S | ● |
| `STORY-0140` | `PT-A7-11` | Test harness baseline + regression-gap audit | `FEAT-37` | C | ● |
| `STORY-0141` | `PT-A7-12` · `TEST-A1` | Financial-engine unit test suite, all 6 calculation methods | `FEAT-37` | S | ● |
| `STORY-0142` | `PT-A7-13` | API / migration integration tests, workspace-isolation assertions | `FEAT-37` | S | ● |

## Test harness workstream (2026-07-11/12)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0143` | `PT-X-03` | Pre-push hook + CI workflow against fresh-migrated Postgres | `FEAT-38` | C | ● |
| `STORY-0144` | `PT-A7-14` · `TF-3`–`TF-7` | 4 stale async-contract e2e tests rewritten | `FEAT-37` | C | ● |

## ICM sprints (2026-07-12 / 07-13)
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0145` | `PT-A4-31` · `PT-Q-01` · `AUD-1/Q1` | component_source on fixed_amount trace fallback | `FEAT-1` | C | ● |
| `STORY-0146` | `PT-A4-32` · `PT-S-07` · `SEC-S7` | 10 MB server-side timesheet upload size guard | `FEAT-2` | C | ● |

## Programme-level meta-work
| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0147` | `PT-M-01` | `docs/audit-program/` — 13-stage Phase 1 audit, closed with 4 decisions | `FEAT-40` | C | ● |
| `STORY-0148` | `PT-M-02` | `agentic-architecture-review` — 13-stage Phase 2 review, in progress | `FEAT-40` | C | ● |
| `STORY-0149` | `PT-M-03` | ICM sprint-workflow model | `FEAT-41` | C | ● |

## ICM sprint `dev-levy-rule-pct` (2026-07-16)
*Absent from the discovery inventory, which has a 2026-07-15 horizon; captured 2026-07-28 under D-026. Forward-allocated per D-019 rule 2 — these take the next free numbers, not chronological positions.*

| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0156` | `DEV-LEVY-1` | Development Levy applied correctly — dual OR'd cadence triggers, `annual_amount` override key | `FEAT-19` | C | ● |
| `STORY-0157` | `RULE-PCT-1` | "Percentage of basic" earning rule configurable via UI; invalid method string fixed | `FEAT-18` | C | ● |

## Not delivered — backlog
Allocated identifiers so the tree is complete and these can never be mistaken for delivered work by omission. Classified backlog under D-011.

| ID | Origin | Title | Feature | | |
|---|---|---|---|---|---|
| `STORY-0150` | `PT-A1-14` · `SHIFT2/3/4` | Client 3 shift allowance onboarding | `FEAT-7` | B | ● |
| `STORY-0151` | `PT-Q-02` · `AUD-2/Q2` | period_type on payroll_run, passed to retry context | `FEAT-23` | B | ● |
| `STORY-0152` | `PT-Q-03` · `AUD-3/Q3` | simulate script `Decimal(str(...))` conversion | `FEAT-39` | B | ● |
| `STORY-0153` | `PT-Q-07` · `AUD-16-1/Q7` | approved_by actor identity on timesheet transitions — deferred to Track P | `FEAT-30` | B | ● |
| `STORY-0154` | `PT-S-08` · `S8` | Pin `python-multipart==0.0.28` | `FEAT-36` | B | ● |
| `STORY-0155` | `PT-X-04` | Two deferred `/simplify` items (shared date utils, shared rule loader) | `FEAT-39` | B | ● |

---

## Excluded from allocation

| Origin | Reason |
|---|---|
| `PT-A4-27` | Grouping row only — the discovery document states it is "grouped here only for capability-matrix completeness." Its constituent items are allocated individually under `FEAT-13`. |
| `PT-Q-01`, `PT-Q-04`, `PT-Q-05`, `PT-Q-06`, `PT-Q-08` | Explicit duplicates of `PT-A4-13`/`PT-A4-31`, `PT-A7-05`, `PT-A7-06`, `PT-A7-07`, `PT-A7-08`. The discovery document states these are "not double-counted in the 148 total." |
| `PT-S-07` | The same item as `PT-A4-32` — a duplicate-ID mapping open since the Phase 4A pilot, resolved here as one story (`STORY-0146`) carrying both codes. |
| `PT-M-04` | The `product-traceability` programme itself — "the artefact producing this inventory, not an inventoried item." |

## Coverage

| | Count |
|---|---|
| Allocated | **157** |
| — delivered | 151 |
| — backlog | 6 |
| Migrated (● — has a story file) | **157** (100%) |
| Remaining to migrate | **0** |

| Capability | Allocated | Migrated |
|---|---|---|
| `CAP-1` Correctness, Audit & Snapshot | 11 | 11 |
| `CAP-2` Security & Compliance Hardening | 8 | 8 |
| `CAP-3` Onboarding & Workspace Setup | 25 | 25 |
| `CAP-4` Employee Lifecycle Management | 23 | 23 |
| `CAP-5` Pay Events & Inputs | 18 | 18 |
| `CAP-6` Execution Engine | 33 | 33 |
| `CAP-7` Governance & Run State Machine | 9 | 9 |
| `CAP-8` Disbursement & Exports | 7 | 7 |
| `CAP-9` Design System & Navigation | 11 | 11 |
| `CAP-10` Delivery Infrastructure | 9 | 9 |
| `CAP-11` Programme Governance & Assurance | 3 | 3 |
| `CAP-12` Agent Layer | 0 | 0 |

**Migration is complete — 157 of 157** (Phase 4D, D-027, 2026-07-29). Every allocated identifier now has a full story record, and this table and `STORY-REGISTRY.md` give the same number for the first time.

`CAP-12` Agent Layer's `0 | 0` is **not** an unmigrated gap. It holds no items by design (D-023, OQ-6), retained so the unbuilt Phase 2 agentic work is visible as a named absence rather than an unstated one. It is the only row where zero is the correct answer.

**What this table now means.** While coverage was partial, a missing item could be either unmigrated or non-existent, and the two were indistinguishable. They no longer are: an item absent from this table is an item no known evidence records. That is the property the coverage map was built to produce, and it is only true from this batch forward — it is preserved solely by capturing each new sprint at closure. The inventory behind this table has a **2026-07-15 horizon** (D-026); three sprints were already found missing from it after that date. Phase 5 (`sprint-workflow integration`) is the durable fix and is not yet authorised.

### Coverage history

| Date | Phase | Migrated |
|---|---|---|
| 2026-07-15 | 4A pilot (D-015) | 2 |
| 2026-07-15 | 4B confirmed batch (D-016) | 21 |
| 2026-07-28 | 4C `CAP-6` batch (D-025/D-026) | 54 |
| **2026-07-29** | **4D remainder (D-027)** | **157 — complete** |
