# Stage 03 → Stage 06 Handoff (Compliance & Controls)

**The 15-capability portfolio is approved (D-03-01, 2026-07-12), including C11's detect/compare/propose-only restriction and C12's split as a separate capability — both binding, not open questions.**

## Primary compliance question: Statutory-Rule Change Management (C12)

Per D-02-04, statutory-rule change management is a separate deterministic platform/compliance capability, independent of Compliance Monitoring (C11). Stage 06 is the natural owner for designing:

- The approval workflow for any statutory-rule change (who approves, what evidence is required, what audit trail is created)
- Whether/how this differs for AI-detected (via C11) vs. human-detected changes — the workflow should very likely be the same regardless of source, but this stage did not adjudicate that
- How this interacts with the existing `(country_code, effective_from)` uniqueness invariant (Stage 01 F-01-45) and the platform-level (not workspace-scoped) nature of `statutory_rule`

## Compliance Monitoring (C11) — external-source trust, freshness, and provenance

C11 is restricted (D-02-04) to detect/compare/propose only — it must never author, execute, or deploy a migration. Before this capability can be considered safe to build, Stage 06 should define:

- What counts as an authoritative external source for FIRS/PenCom regulatory changes (a legal-risk question this review explicitly does not adjudicate)
- Freshness requirements (how current must the monitored source be)
- Provenance/citation requirements for any proposal C11 drafts, so a human reviewer can verify the claim against the actual regulatory text, not just C11's summary of it

## Compliance question about the architecture document itself

D-02-01 confirmed the source architecture document's "NEEDS REVISION" status remains open, and this review is the formal revision path. Stage 06 does not need to separately chase this — it's resolved. No action needed here beyond awareness.

## Audit requirements for the tool portfolio

Every tool in `outputs/tool-portfolio-matrix.md` has a "required audit record" column, currently marked at the level of "tool-call log" without a defined retention period or content spec. Stage 06 should confirm what audit standard applies (the source document's `agent_session_log` design proposes 7-year retention for the chat session log specifically — Stage 06 should confirm whether tool-call-level logging needs the same retention, and what fields are mandatory).

## What Stage 06 should NOT re-derive

Whether Y1/C11 should be allowed to apply migrations directly — already decided (no) by D-02-04.
