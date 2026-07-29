# Source Index — reverse lookup

**Given a source file or a legacy code, find the story.** The forward direction (story → source) is in each story file's *Source reference* section; this file supplies the direction that was missing.

`POLICY.md` forbids this programme from modifying anything under `docs/stories/`, `docs/sprints/`, `docs/test-reports/`, `docs/audit/` or `docs/security/` — history is a read-only input, never rewritten. So the reverse link cannot be a back-reference written into the old story file; it lives here instead.

**Covers all 157 stories** as of 2026-07-29 (D-027, Phase 4D). There are no unmigrated items left, so a legacy code that does not appear here belongs to no known item.

## `CAP-6` Execution Engine — Phase 4C batch (D-025, D-026)

Migrated 2026-07-28. Legacy codes for this capability come from nine schemes: the discovery inventory's `PT-A4-*`, Phase-1 item refs (`P0-*`/`P1-*`/`P2-*`/`SR9`), Sprint 7's `FIX-*` and `PH-*`, Track K's `K1`–`K3` and `GAP-*`/`WI-*`, Track M's `M1`–`M5` and `NEW-GAP*`, Sprint A's `SPRINT-A-*`, Track Q's `AUD-2`/`Q2`, and the two ICM sprint codes.

| Legacy code | Story |
|---|---|
| `PT-A4-01` | `STORY-0004` |
| `PT-A4-02` | `STORY-0005` |
| `PT-A4-03` | `STORY-0006` |
| `PT-A4-04` | `STORY-0007` |
| `PT-A4-05` · `P1-7` | `STORY-0018` |
| `PT-A4-06` · `P2-7` | `STORY-0019` |
| `PT-A4-07` · `P0-2` · `P1-1` | `STORY-0020` |
| `PT-A4-08` · `P2-3` | `STORY-0021` |
| `PT-A4-09` · `P1-6` | `STORY-0022` |
| `PT-A4-10` · `SR9` | `STORY-0023` |
| `PT-A4-11` · `GAP-2` · `K1` | `STORY-0065` |
| `PT-A4-12` · `GAP-5` · `K2` | `STORY-0066` |
| `PT-A4-13` · `WI-04a` · `K3` | `STORY-0067` |
| `PT-A4-14` · `FIX-1`–`FIX-5` | `STORY-0034` |
| `PT-A4-15` · `PH-2` · `PH-9` | `STORY-0037` |
| `PT-A4-16` · `PH-3` · `PH-4` | `STORY-0038` |
| `PT-A4-17` · `PH-5` | `STORY-0039` |
| `PT-A4-18` · `PH-10` · `PH-11` | `STORY-0040` |
| `PT-A4-19` · `WI-04b` | `STORY-0073` |
| `PT-A4-20` | `STORY-0074` |
| `PT-A4-21` · `NEW-GAP14` · `M1` | `STORY-0078` |
| `PT-A4-22` · `NEW-GAP15` · `M2` | `STORY-0079` |
| `PT-A4-23` · `NEW-GAP6` · `M3` | `STORY-0080` |
| `PT-A4-24` · `GAP-10-FIX` · `M4` | `STORY-0081` |
| `PT-A4-25` · `NEW-GAP7` · `M5` | `STORY-0082` |
| `PT-A4-26` | `STORY-0086` |
| `PT-A4-28` · `SPRINT-A-1` | `STORY-0133` |
| `PT-A4-29` · `SPRINT-A-2` | `STORY-0134` |
| `PT-A4-30` · `SPRINT-A-3` | `STORY-0135` |
| `PT-Q-02` · `AUD-2` · `Q2` | `STORY-0151` — **backlog, not delivered** |
| `PAY-TAX-1` | `STORY-0131` |
| `DEV-LEVY-1` | `STORY-0156` |
| `RULE-PCT-1` | `STORY-0157` |

| Source / evidence file | Stories |
|---|---|
| `docs/test-reports/2026-04-14-sprint-7.md` | `STORY-0034`, `STORY-0037`, `STORY-0038`, `STORY-0039`, `STORY-0040` |
| `docs/audit/2026-05-01-sprint-10-audit-review.md` | `STORY-0065`, `STORY-0066`, `STORY-0067` |
| `docs/audit/2026-05-02-sprint-11-audit-review.md` | `STORY-0073`, `STORY-0074` |
| `docs/test-reports/2026-05-03-sprint-12-m1-m2.md` | `STORY-0078`, `STORY-0079`, `STORY-0080` |
| `docs/stories/sprint-14-hire-proration-configurable.md` | `STORY-0086` |
| `docs/test-reports/2026-06-20-sprint-pay-tax-1.md` | `STORY-0131` |
| `docs/test-reports/2026-07-04-sprint-a-rule-versioning-integrity.md` | `STORY-0133`, `STORY-0134`, `STORY-0135` |
| `docs/sprints/dev-levy-rule-pct/` | `STORY-0156`, `STORY-0157` |

**Items with no dedicated evidence file** — `STORY-0004`, `0005`, `0006`, `0007` (Sprint 0, pre-sprint tracking) and `STORY-0018`, `0019`, `0020`, `0021`, `0022`, `0023` (Sprints 1–6, before the per-sprint test-report convention began). Their source is `docs/ROADMAP.md` alone; confidence is `tentative` or `strongly inferred` accordingly, never `confirmed`.

## By legacy identifier

Every code any of this work has been known by. All of these also appear in the `origin_code` field of the story itself, so a plain `grep` across `docs/product/` finds them too.

| Legacy code | Story | Scheme it came from |
|---|---|---|
| `AUD-1` / `Q1` | `STORY-0145` | Track Q audit register |
| `D-ARCH-2` | `STORY-0052` | Track J arch-council decision |
| `EMP-01+` | `STORY-0099` | Retrospective increment |
| `EMP-B1` | `STORY-0101` | Sprint 17 Track B |
| `EMP-B2` | `STORY-0102` | Sprint 17 Track B |
| `EMP-REG-5` | `STORY-0129` | Sprint 26 fix |
| `EMP-UX-1` | `STORY-0106` | Sprint 17 UX track |
| `NEW-GAP4` / `NEW-GAP13` | `STORY-0071` | Sprint 11 gap register |
| `NEW-GAP12` | `STORY-0072` | Sprint 11 gap register |
| `PT-A1-07` | `STORY-0046` | Discovery inventory (provisional) |
| `PT-A1-08` | `STORY-0047` | Discovery inventory (provisional) |
| `PT-A1-09` | `STORY-0048` | Discovery inventory (provisional) |
| `PT-A1-10` | `STORY-0049` | Discovery inventory (provisional) |
| `PT-A1-11` | `STORY-0050` | Discovery inventory (provisional) |
| `PT-A1-15` | `STORY-0051` | Discovery inventory (provisional) |
| `PT-A1-16` | `STORY-0052` | Discovery inventory (provisional) |
| `PT-A1-17` | `STORY-0053` | Discovery inventory (provisional) |
| `PT-A1-18` | `STORY-0054` | Discovery inventory (provisional) |
| `PT-A1-19` | `STORY-0071` | Discovery inventory (provisional) |
| `PT-A1-20` | `STORY-0072` | Discovery inventory (provisional) |
| `PT-A1-21` | `STORY-0101` | Discovery inventory (provisional) |
| `PT-A1-22` | `STORY-0102` | Discovery inventory (provisional) |
| `PT-A1-25` | `STORY-0106` | Discovery inventory (provisional) |
| `PT-A1-28` | `STORY-0099` | Discovery inventory (provisional) |
| `PT-A1-38` | `STORY-0129` | Discovery inventory (provisional) |
| `PT-A1-39` | `STORY-0130` | Discovery inventory (provisional) |
| `PT-A1-41` | `STORY-0089` | Discovery inventory (provisional) |
| `PT-A1-42` | `STORY-0088` | Discovery inventory (provisional) |
| `PT-A4-31` | `STORY-0145` | Discovery inventory (provisional) |
| `PT-A4-32` | `STORY-0146` | Discovery inventory (provisional) |
| `PT-Q-01` | `STORY-0145` | Track Q register — **duplicate** of `PT-A4-31`, resolved D-024 |
| `PT-S-07` | `STORY-0146` | Track S register — **duplicate** of `PT-A4-32`, resolved D-024 |
| `SEC-S7` | `STORY-0146` | Track S security register |
| `TM-1` | `STORY-0088` | Sprint 16 timesheet layer |
| `TM-7` | `STORY-0089` | Sprint 16 timesheet layer |
| `WC-1` | `STORY-0046` | Track J workspace-config |
| `WC-2` / `WC-3` / `WC-4` / `WC-5` | `STORY-0047` | Track J workspace-config |
| `WC-6` / `WC-7` | `STORY-0048` | Track J workspace-config |
| `WC-8` | `STORY-0049` | Track J workspace-config |
| `WC-10` | `STORY-0050`, `STORY-0052` | Track J workspace-config |
| `WC-11` | `STORY-0050` | Track J workspace-config |
| `WS-ACTIVATE-1/2/3` | `STORY-0130` | 2026-06 fix sprint |

Nine distinct legacy schemes are represented above. `docs/ROADMAP.md` carries 25+ such prefixes overall — rationalising them is deferred (D-021) precisely because this index makes it unnecessary to rewrite history in order to navigate it.

## By source file

| Source file | Stories |
|---|---|
| `docs/stories/track-j-workspace-config-management.md` | `STORY-0046`, `STORY-0047`, `STORY-0048`, `STORY-0049`, `STORY-0050`, `STORY-0051`, `STORY-0052`, `STORY-0053`, `STORY-0054` |
| `docs/stories/sprint-11-track-o-employee-schema-shift-lta.md` | `STORY-0071`, `STORY-0072` |
| `docs/stories/sprint-16-timesheet-layer.md` | `STORY-0088`, `STORY-0089` |
| `docs/stories/employee-page-enhancements.md` | `STORY-0099` |
| `docs/stories/sprint-17-employee-crud.md` | `STORY-0101`, `STORY-0102` |
| `docs/stories/sprint-17-employee-ux.md` | `STORY-0106` |
| `docs/stories/fix-emp-reg5-enrollment-prepopulation.md` | `STORY-0129` |
| `docs/stories/fix-workspace-activation-cta.md` | `STORY-0130` |
| `docs/sprints/aud-q1-trace-source/` | `STORY-0145` |
| `docs/sprints/sec-s7-timesheet-upload-guard/` | `STORY-0146` |

## By evidence file

| Evidence file | Stories |
|---|---|
| `docs/test-reports/2026-04-21-track-j.md` | `STORY-0046`–`STORY-0054` |
| `docs/audit/2026-05-02-sprint-11-audit-review.md` | `STORY-0071`, `STORY-0072` |
| `docs/test-reports/2026-05-13-sprint-16.md` | `STORY-0088`, `STORY-0089` |
| `docs/test-reports/2026-05-27-sprint-17-full.md` | `STORY-0101`, `STORY-0102`, `STORY-0106` |
| `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md` | `STORY-0145` |
| `docs/test-reports/2026-07-12-aud-q1-trace-source.md` | `STORY-0145` |
| `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` | `STORY-0146` |
| `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md` | `STORY-0146` |


## Phase 4D remainder batch (D-027) — the other 103 items

Migrated 2026-07-29, completing the index at **157 of 157**. Every legacy code below also appears in the `origin_code` field of the story itself, so a plain `grep` across `docs/product/` finds them too. Items marked **not delivered** hold an identifier under D-011 and describe work that does not exist — never cite them as capability.

| Legacy code | Story |
|---|---|
| `PT-A3-01` | `STORY-0001` |
| `PT-A3-02` | `STORY-0002` |
| `PT-A3-03` | `STORY-0003` |
| `PT-A5-01` | `STORY-0008` |
| `PT-A5-02` | `STORY-0009` |
| `PT-A6-01` | `STORY-0010` |
| `PT-A1-03` · `P3-7` | `STORY-0011` |
| `PT-A1-04` · `P1-8` | `STORY-0012` |
| `PT-A1-05` · `PC4` | `STORY-0013` |
| `PT-A1-06` · `P3-1` | `STORY-0014` |
| `PT-A1-12` · `P3-5` | `STORY-0015` |
| `PT-A3-04` · `INP10` | `STORY-0016` |
| `PT-A3-05` · `P3-3` | `STORY-0017` |
| `PT-A5-03` · `P0-1` | `STORY-0024` |
| `PT-A5-04` · `P2-1` | `STORY-0025` |
| `PT-A5-05` · `G7` | `STORY-0026` |
| `PT-A6-02` · `P0-4` · `P0-5` | `STORY-0027` |
| `PT-A6-03` · `RC5` | `STORY-0028` |
| `PT-A7-01` · `P2-4` · `P2-7` | `STORY-0029` |
| `PT-A7-02` · `P2-6` | `STORY-0030` |
| `PT-A7-03` · `P2-4` | `STORY-0031` |
| `PT-A7-04` · `G12` | `STORY-0032` |
| `PT-A3-06` · `INP10` | `STORY-0033` |
| `PT-A1-01` · `PH-1`…`PH-11` | `STORY-0035` |
| `PT-A1-02` · `PH-7` | `STORY-0036` |
| `PT-A5-06` · `P2-2` | `STORY-0041` |
| `PT-A7-09` · `PH-9` | `STORY-0042` |
| `PT-A7-10` · `FIX-5` | `STORY-0043` |
| `PT-UI-01` | `STORY-0044` |
| `PT-UI-02` | `STORY-0045` |
| `PT-UI-06` | `STORY-0055` |
| `PT-UI-03` | `STORY-0056` |
| `PT-UI-04` | `STORY-0057` |
| `PT-A6-07` · `S9-1` · `S9-2` | `STORY-0058` |
| `PT-A1-13` · `PH-8` · `WI-05` | `STORY-0059` |
| `PT-A1-43` · `WI-06` · `H2` | `STORY-0060` |
| `PT-A1-44` · `WI-12` | `STORY-0061` |
| `PT-A1-45` · `WI-01` | `STORY-0062` |
| `PT-A1-46` · `WI-02` | `STORY-0063` |
| `PT-A1-47` · `WI-05` | `STORY-0064` |
| `PT-A6-04` · `P0-3` | `STORY-0068` |
| `PT-A6-05` · `P1-4` | `STORY-0069` |
| `PT-A6-06` · `P1-5` | `STORY-0070` |
| `PT-A7-05` · `AUD-4` · `Q4` | `STORY-0075` |
| `PT-S-04` · `SEC-S4` | `STORY-0076` |
| `PT-S-05` · `SEC-S5` | `STORY-0077` |
| `PT-S-01` · `SEC-S1` | `STORY-0083` |
| `PT-S-02` · `SEC-S2` | `STORY-0084` |
| `PT-S-03` · `SEC-S3` | `STORY-0085` |
| `PT-S-06` · `SEC-S6` | `STORY-0087` |
| `PT-A3-07` · `TM-2` | `STORY-0090` |
| `PT-A3-08` · `TM-3` | `STORY-0091` |
| `PT-A3-09` · `TM-4` | `STORY-0092` |
| `PT-A3-10` · `TM-5` | `STORY-0093` |
| `PT-A3-11` · `TM-6` | `STORY-0094` |
| `PT-A3-12` · `C1` | `STORY-0095` |
| `PT-A3-13` · `C2` | `STORY-0096` |
| `PT-A7-06` · `AUD-16-3` · `Q5` | `STORY-0097` |
| `PT-UI-05` · `UI-NAV-1` · `UI-NAV-2` · `UI-NAV-3` | `STORY-0098` |
| `PT-A1-29` | `STORY-0100` |
| `PT-A1-23` · `EMP-B3` | `STORY-0103` |
| `PT-A1-24` · `EMP-B0a` | `STORY-0104` |
| `PT-A1-24` · `EMP-B0b` | `STORY-0105` |
| `PT-A1-26` · `EMP-UX-3` | `STORY-0107` |
| `PT-A1-27` · `EMP-UX-4` | `STORY-0108` |
| `PT-A1-40` · `EMP-BULK-1` · `EMP-BULK-2` · `EMP-BULK-3` | `STORY-0109` |
| `PT-A1-30` · `EMP-UX-5` | `STORY-0110` |
| `PT-A7-07` · `Q6-FIX` | `STORY-0111` |
| `PT-A7-08` · `Q8-FIX` | `STORY-0112` |
| `BADGE-RT-1` | `STORY-0113` |
| `BADGE-RT-2` | `STORY-0114` |
| `EMP-TABLE-1` | `STORY-0115` |
| `EMP-TABLE-2` | `STORY-0116` |
| `EMP-TABLE-3` | `STORY-0117` |
| `PT-A1-31` · `EMP-ENROLL-AUTODEF-1` | `STORY-0118` |
| `PT-A1-32` · `EMP-REG-1` | `STORY-0119` |
| `PT-A1-33` · `EMP-EDIT-1` | `STORY-0120` |
| `PT-A1-34` · `EMP-STATUS-1` | `STORY-0121` |
| `PT-A1-35` · `EMP-BADGE-1` | `STORY-0122` |
| `PT-A1-36` · `EMP-ICONS-1` · `EMP-PAYROLL-ACTIONS-1` | `STORY-0123` |
| `PT-A1-37` · `EMP-NATIVE-1` | `STORY-0124` |
| `PT-A3-14` · `INP-NATIVE-1` | `STORY-0125` |
| `PT-A3-15` · `INP-MULTI-1` | `STORY-0126` |
| `PT-A3-17` · `PAY-RECON-1` | `STORY-0127` |
| `PT-A3-16` · `UPLOAD-SKIP-1` | `STORY-0128` |
| `PT-A5-07` · `RULE-VER-1` · `RULE-VER-2` · `RULE-VER-3` | `STORY-0132` |
| `PT-A5-08` · `B-UI-1` · `B-UI-2` · `B-UI-3` | `STORY-0136` |
| `PT-UI-07` · `B-UI-4` · `B-UI-5` | `STORY-0137` |
| `PT-X-01` · `PIPE-1` · `PIPE-2` · `PIPE-3` | `STORY-0138` |
| `PT-X-02` · `HARN-1` | `STORY-0139` |
| `PT-A7-11` | `STORY-0140` |
| `PT-A7-12` · `TEST-A1` | `STORY-0141` |
| `PT-A7-13` | `STORY-0142` |
| `PT-X-03` | `STORY-0143` |
| `PT-A7-14` · `TF-3`–`TF-7` | `STORY-0144` |
| `PT-M-01` | `STORY-0147` |
| `PT-M-02` | `STORY-0148` |
| `PT-M-03` | `STORY-0149` |
| `PT-A1-14` · `SHIFT2` · `SHIFT3` · `SHIFT4` | `STORY-0150` — **not delivered** |
| `PT-Q-03` · `AUD-3` · `Q3` | `STORY-0152` — **not delivered** |
| `PT-Q-07` · `AUD-16-1` · `Q7` | `STORY-0153` — **not delivered** |
| `PT-S-08` · `S8` | `STORY-0154` — **not delivered** |
| `PT-X-04` | `STORY-0155` — **not delivered** |

### By source / evidence file — Phase 4D batch

| Source / evidence file | Stories |
|---|---|
| `docs/ROADMAP.md` | `STORY-0001`, `STORY-0002`, `STORY-0003`, `STORY-0008`, `STORY-0009`, `STORY-0010`, `STORY-0011`, `STORY-0012`, `STORY-0013`, `STORY-0014`, `STORY-0015`, `STORY-0016`, `STORY-0017`, `STORY-0024`, `STORY-0025`, `STORY-0026`, `STORY-0027`, `STORY-0028`, `STORY-0029`, `STORY-0030`, `STORY-0031`, `STORY-0032`, `STORY-0045`, `STORY-0110`, `STORY-0111`, `STORY-0112`, `STORY-0136`, `STORY-0137`, `STORY-0150`, `STORY-0152`, `STORY-0153`, `STORY-0154`, `STORY-0155` |
| `docs/audit-program/_core/human-decisions.md` | `STORY-0147` |
| `docs/audit/2026-05-02-sprint-11-audit-review.md` | `STORY-0075` |
| `docs/programmes/agentic-architecture-review/_core/HUMAN-DECISIONS.md` | `STORY-0148` |
| `docs/security/2026-05-02-sprint-11-security-review.md` | `STORY-0076`, `STORY-0077` |
| `docs/security/2026-05-13-sprint-14-16-security-review.md` | `STORY-0087` |
| `docs/sprints/STAGE-REGISTRY.md` | `STORY-0149` |
| `docs/stories/sprint-13-track-m3-m5-track-s-security.md` | `STORY-0083`, `STORY-0084`, `STORY-0085` |
| `docs/stories/sprint-25-badge-realtime-update.md` | `STORY-0113`, `STORY-0114` |
| `docs/stories/sprint-25a-employees-table-ux-fixes.md` | `STORY-0115` |
| `docs/stories/sprint-25b-no-longer-active-ux.md` | `STORY-0116` |
| `docs/stories/sprint-25d-register-employee-contract-dates.md` | `STORY-0117` |
| `docs/stories/sprint-29-pipeline.md` | `STORY-0138` |
| `docs/stories/sprint-30-test-harness.md` | `STORY-0139` |
| `docs/stories/sprint-31-financial-engine-tests.md` | `STORY-0141` |
| `docs/stories/sprint-32-api-migration-tests.md` | `STORY-0142` |
| `docs/stories/sprint-9-full-detail-export.md` | `STORY-0058` |
| `docs/test-reports/2026-04-14-sprint-7.md` | `STORY-0033`, `STORY-0035`, `STORY-0036`, `STORY-0041`, `STORY-0042`, `STORY-0043` |
| `docs/test-reports/2026-04-15-gate3-gate4.md` | `STORY-0056`, `STORY-0057` |
| `docs/test-reports/2026-04-21-sprint-7-wc12-wc13.md` | `STORY-0035`, `STORY-0042` |
| `docs/test-reports/2026-04-21-track-j.md` | `STORY-0055` |
| `docs/test-reports/2026-05-01-sprint-10.md` | `STORY-0059`, `STORY-0060`, `STORY-0061`, `STORY-0062`, `STORY-0063`, `STORY-0064`, `STORY-0068`, `STORY-0069`, `STORY-0070` |
| `docs/test-reports/2026-05-02-sprint-11.md` | `STORY-0075`, `STORY-0076`, `STORY-0077` |
| `docs/test-reports/2026-05-13-sprint-16.md` | `STORY-0090`, `STORY-0091`, `STORY-0092`, `STORY-0093`, `STORY-0094`, `STORY-0095`, `STORY-0096`, `STORY-0097`, `STORY-0098` |
| `docs/test-reports/2026-05-26-nav-ux.md` | `STORY-0100` |
| `docs/test-reports/2026-05-27-sprint-17-full.md` | `STORY-0103`, `STORY-0104`, `STORY-0105`, `STORY-0107`, `STORY-0108` |
| `docs/test-reports/2026-06-08-sprint-22.md` | `STORY-0109` |
| `docs/test-reports/2026-06-11-sprint-26.md` | `STORY-0118`, `STORY-0119`, `STORY-0120`, `STORY-0121`, `STORY-0122`, `STORY-0123` |
| `docs/test-reports/2026-06-15-sprint-27-28.md` | `STORY-0124`, `STORY-0125`, `STORY-0126`, `STORY-0127`, `STORY-0128` |
| `docs/test-reports/2026-06-21-payroll-rule-versioning.md` | `STORY-0132` |
| `docs/test-reports/test-harness/test-harness-checklist.md` | `STORY-0140`, `STORY-0143`, `STORY-0144` |
| `docs/ux-ui-design-brief/07-screen-inventory.md` | `STORY-0044` |

**Items whose only source is `docs/ROADMAP.md`.** Sprint 0 and Sprints 1–6 predate the per-sprint test-report convention; Sprint 24 and Sprint B-UI have roadmap entries but no dedicated report; the five backlog items describe work that was never done. Their records carry `tentative` or `strongly inferred` confidence — or `backlog` status — accordingly, and none of them may be cited as evidence of verified behaviour.

## Maintenance

Every migration batch must extend all three tables above in the same change that adds its story rows. `validate_registry.py` checks that every migrated story appears at least once here, so an omission fails validation rather than going unnoticed.
