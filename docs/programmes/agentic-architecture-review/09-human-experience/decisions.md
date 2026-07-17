# Stage 09: Human Experience — Decisions

Stage-local log of human decisions made during this stage. Master log: `_core/HUMAN-DECISIONS.md`. Format matches `_core/HUMAN-DECISIONS.md`.

## Gate

- **Stage opened**: 2026-07-17 (context-ready on Stage 08 closure; executor pass same day)
- **Stage closed**: pending critic

## Human decisions log

_None — no blocking human decisions arose. Every choice below is design execution within binding inputs (D-03-01 portfolio/surfaces, Stage 04 outcome definitions, Stage 08 mechanisms, CG/SG gates, `docs/design/ui-decisions.md`), classified per `CRITIC.md` as implementation-specification, not human decisions. DQ-005 — the one genuine product choice this stage touches — was already classified `non-blocking-forwarded-decision` by the Stage 05 critic and remains queued with a recorded recommendation (`outputs/stage-11-handoff.md` §1), not decided here._

## Executor design conclusions (DEC-09-01 … DEC-09-14)

Recorded for downstream traceability; each is grounded in a binding input, not a new policy call.

| ID | Conclusion | Grounding |
|---|---|---|
| DEC-09-01 | Exceptions and Pending Actions are two separate sidebar entries (problems-to-resolve vs proposals-to-decide), both using the existing badge pattern; one exception queue serves all sources | Stage 04 "one workflow, not three"; F-09-04; different action grammars |
| DEC-09-02 | Prioritisation display uses named signals (severity badge + cutoff proximity) with a deterministic sort — no composite priority score | Stage 08 handoff item 3 (prioritisation display delegated); facts-not-conclusions discipline |
| DEC-09-03 | Resolution actions map 1:1 to Stage 08 resolution codes; corrections happen on the owning data surface via deep-link; the queue never edits data | `event-audit-foundation-design.md` §6; no second write path to financial data |
| DEC-09-04 | Notification panel is navigation-only; page banners derive from live entity state, never notification rows | Stage 08 §4 pointer semantics; Sprint 23 two-sources-of-truth lesson |
| DEC-09-05 | C3 refusals render as boundary answers (not errors) with fixed copy patterns per the five conditions; cross-workspace copy is byte-identical to not-found | Portfolio map §3; P5 no-existence-disclosure |
| DEC-09-06 | Chat answers deep-link to owning surfaces instead of reproducing UI data; no proactive chat; grounding footer chips map 1:1 to logged tool calls | Stage 04 anti-chat-burying constraint; P7 |
| DEC-09-07 | C10 proposal cards in chat carry status only — the confirm control exists solely on the authenticated pending-actions surface; cards render exclusively from frozen `payload_jsonb` | T7/SG-10; `confirmation-protocol-design.md` §4 |
| DEC-09-08 | Double-submit/concurrency UX: render whatever terminal record returns as truth, with an explanatory banner — no conflict dialogs | CAS idempotency (§3.3) makes convergence the correct UI model |
| DEC-09-09 | C12 is a platform-level area reached from bureau chrome (dashboard entry + user menu), PLATFORM_ADMIN-only; C11 has no separate surface — detections are proposals in the same list | SG-12; control §6 one-workflow; Stage 03 coherence gap resolved in the IA |
| DEC-09-10 | The step-up modal is invoked at the decision moment and submits immediately on success, consuming the 5-minute freshness window in seconds | `auth-foundation-design.md` §1.5; Stage 08 handoff item 1 |
| DEC-09-11 | C13/C14 is a staged full-page flow extending `NativeUploadFlow`/`ColumnMappingPanel`, preserving the Upload/Enroll separation; commit is hash-gated client-side (convenience) and server-side (guarantee) | Portfolio §7; standing Sprint 22 rule; `dry-run-mechanism-design.md` §3.6 |
| DEC-09-12 | Per-field mapping confidence renders as 3-level chips with low-confidence-first attention ordering; every mapping requires operator confirmation regardless of confidence | Stage 04 handoff; D-03-01 C13 disposition (proposal-only) |
| DEC-09-13 | Dry-run results are visually unmistakable for real runs: persistent banner, no Runs-list presence, distinct page identity | DQ-004 (no `payroll_run` row); financial-evidence integrity |
| DEC-09-14 | Pre-epoch labelling ships as one shared actor-display component applied to every audit surface (chip not tooltip, present in exports); notification read-state's shared-read limitation is accepted for single-operator v1 and forwarded as a multi-operator scope boundary | Threat-model §6; Stage 08 §4 schema; DQ-007 operational context; `stage-11-handoff.md` §3 |

## Next action

**Independent critic per `CRITIC.md`.**
