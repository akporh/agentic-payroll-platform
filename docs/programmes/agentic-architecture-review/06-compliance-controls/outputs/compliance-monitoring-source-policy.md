# Stage 06 Output: Compliance-Monitoring Source Policy (C11) — Requirements Level

Defines the authoritative-source, freshness, and provenance policy any C11 (Compliance Monitoring) proposal must satisfy before it can enter C12's approval workflow. C11 remains restricted to detect/compare/propose only (D-02-04, D-03-01 — binding, not revisited).

**Scope boundary honoured (stage context, explicitly):** this stage defines the *policy structure* — the tiers, the required fields, the freshness discipline. It does **not** adjudicate which specific external sources are legally sufficient for FIRS/PenCom compliance; that residual legal question is escalated (DQ-006), and its resolution belongs to the human reviewer with professional legal/tax advice.

## 1. Source-authority tiers (policy structure)

| Tier | Definition | Permitted use by C11 |
|---|---|---|
| **Primary** | The regulatory instrument itself or its official publisher: the Act/regulation text as gazetted, official FIRS/PenCom publications, circulars, and public notices issued by the body with statutory authority | The **only** tier that can ground a proposal's operative claim ("rate X changes to Y effective Z") |
| **Secondary** | Professional advisories from recognised firms, professional-body summaries (e.g. chartered tax institute guidance) | Corroboration and detection lead only — may trigger C11 to *look for* a primary source; may never be the sole basis of a proposal |
| **Tertiary** | News coverage, blogs, aggregator sites, social media | Detection lead only; must never appear as the citation supporting an operative claim |

Policy rules:

1. A proposal whose operative claim cannot be traced to a Tier-1 source **must not be presented for approval** — it may exist only as a monitoring alert ("possible change detected, primary source not yet located"), clearly labelled as unverified. This directly implements the compliance-outcome-chain's step-2 requirement that C11 "must never present a low-confidence or unverified signal as though it were confirmed."
2. The concrete allowlist of Tier-1 sources (exact publications, domains, document types) is a configuration artefact that requires human sign-off at C11 build time, informed by DQ-006's resolution — the platform ships the tier mechanism; the human decides the membership.
3. Precedent note: the platform has already experienced the cost of a source-verification failure — the original NG PAYE seed encoded old PITA bands under a Nigeria Tax Act 2025 label and required a correcting migration (`de1f2a3b4c5d`, evidence file §6). The tier policy exists to prevent exactly this class of error entering through C11.

## 2. Provenance / citation requirements (per proposal)

Every C11 proposal must carry, as structured fields (not prose):

1. **Source identity** — publisher, document title, document/circular reference number where one exists
2. **Publication date** of the source document (the source's own date, not the retrieval date)
3. **Locator** — URL and/or official gazette/document reference sufficient for a human to retrieve the same document
4. **Verbatim excerpt** of the operative text (the specific rates/bands/thresholds and the commencement provision), so the approver verifies against the regulation's own words — never only C11's summary of it (Stage 03 handoff requirement, implemented here)
5. **Retrieval timestamp** and, where feasible, a stored snapshot/hash of the retrieved document — external web content is mutable; the approval record must be able to prove what was actually seen
6. **Interpretation delta** — where the proposal's structured values (e.g. band thresholds as numbers) are derived from the excerpt by interpretation (LLM or human), the mapping must be stated so the approver can check each derived value against the excerpt

## 3. Freshness requirements

- Every proposal states the **as-of date** of the monitored source set. A proposal computed against a source snapshot older than the monitoring cadence must be re-verified before presentation.
- Monitoring cadence itself is a product calibration (how often FIRS/PenCom publish changes vs. cost of checking) — an implementation/product-tuning question for Stage 08/11, not fixed here. What is fixed: the cadence must be explicit, recorded, and alert-on-failure (a silently stalled monitor is a compliance failure mode, not a degraded feature — it recreates today's "noticed manually or not at all" baseline while appearing to cover it).
- The **effective-date clock matters more than the detection clock**: a change detected after its effective date has passed must be flagged as retrospective (affected runs may already have executed with outdated rules) and the proposal must say so — this feeds C12's correction path rather than its normal forward-dated path (`statutory-change-control-design.md` §5).

## 4. The residual legal question — escalated, not decided

Which sources are *legally authoritative* for Nigerian statutory payroll compliance — and whether relying on them without professional review meets the bureau's professional-duty obligations to its clients — is a legal-risk determination this review does not have the authority or expertise to make (stage context: "escalate; do not decide").

Recorded as **DQ-006** in `decision-queue.md`: non-blocking for this review's progression (C11 is not being built now; it is conditionally ready at best per Stage 05), but a **hard gate before C11 build authorisation**. Recommended resolution path: the human reviewer confirms the Tier-1 allowlist with professional tax/legal advice, and that confirmation is itself recorded as a programme-level human decision.

## 5. What this policy binds

- **C11 (build-time)**: the proposal schema must include §2's fields as mandatory; the tier mechanism of §1 must be enforced in code (a Tier-2/3-only proposal cannot reach `awaiting-approval` state).
- **C12**: the approval record preserves the citation exactly as presented (`statutory-change-control-design.md` §4).
- **Stage 08**: mechanism design for source snapshotting/hashing and the monitoring-stall alert.
- **Stage 11**: commercial framing — C11's value claim ("you won't miss a statutory change") is only as strong as the Tier-1 allowlist and cadence; do not market beyond the policy's actual guarantee.
