# Stage 07 Output: Agent-Layer Threat Model

Threat model for the 5 LLM-touching capabilities the approved portfolio retains — C3 (operator assistant), C5 (trace explanation), C7 (anomaly narration, optional), C11 (compliance monitoring, narrowed), C13 (onboarding mapping) — plus C10's confirmation protocol. Requirements level; per-capability control gates land in `security-gate-register.md`. The architecture is proposal-only/read-only by prior binding decisions (D-02-04, Stage 03 matrix) — this document treats those boundaries as *security controls to be enforced*, not descriptions to be trusted.

## 1. Untrusted-input inventory (where injection enters)

The LLM's context is assembled from sources of differing trust. Anything not authored by the platform is an injection carrier:

| Source | Reaches | Trust | Notes |
|---|---|---|---|
| Operator chat messages | C3, C5 | Authenticated operator — trusted identity, untrusted content | Operator can be socially engineered to paste hostile text |
| Workspace data via tools (names, notes, free-text fields) | C3, C5, C7 | **Untrusted** | DB-sourced ≠ safe: employee names, notes, resolution free-text are operator- or import-supplied and may carry instructions |
| Uploaded spreadsheet headers/content | **C13** | **Untrusted, externally authored** | The core C13 input is exactly the attacker-controllable channel — a client-provided file |
| External regulatory source text | **C11** | **Untrusted, highest exposure** | Fetched web/document content is the classic injection vector; C11 reads it *by design* |
| Tool results structure (JSON) | all | Platform-controlled shape, untrusted string values | Serializer must not let string values break out of their data role (no instruction-bearing framing) |

## 2. Threats and their bounding controls

### T1 — Prompt injection → tool misuse
Hostile text induces the model to call tools for exfiltration or mischief. **Bounding controls:** (a) the session's tool registry is capability-scoped — C5's session has no reason to hold `get_employees`; minimal tool sets per capability are a launch-gate item; (b) the tool-guard wrapper (P2) makes workspace identity non-negotiable regardless of what the model asks for — injected instructions cannot name another workspace; (c) read-only tools throughout (no mutating tool exists in the portfolio); (d) rate limiting (W3, already "non-negotiable" per the source document) bounds volume.

### T2 — Tool parameter tampering
The model supplies manipulated parameters (another run's UUID, oversized limits). **Bounding controls:** wrapper-enforced ownership check on every resource parameter (P4 — a guessed foreign UUID gets a 404-style refusal, logged); parameter schema validation with bounds (row limits per the tool matrix); refusals logged as `refused` (SC-3) so probing is visible in the audit trail, not silent.

### T3 — Cross-workspace exfiltration via tool outputs
Model context contains data that leaks across tenant boundaries. **Bounding controls:** one session = one workspace (P6 session lock, `identity-architecture-requirements.md` §2) — context never mixes workspaces by construction; PII-stripped serialization (versioned rule-set, SC-3 logs which version applied); max-exposure bounds per tool (matrix rows). Residual: within-workspace data shown to the workspace's own operator is not a leak.

### T4 — Exfiltration via *outputs of* the model (C11/C13 specifics)
Injected instructions make the model embed sensitive context in a place the attacker can later read (e.g. a C11 proposal quoting workspace data, a C13 mapping proposal echoing another employee's row). **Bounding controls:** C11 sessions hold **no workspace tools** — its inputs are external sources and platform-level `get_statutory_rules` only; there is no tenant data in its context to exfiltrate. C13's proposals render only to the uploading operator's own session/workspace. Proposal records are workspace-scoped records like any other.

### T5 — Hostile content laundered into evidence/proposals (C11's defining risk)
Injected external text produces a plausible but false statutory-change proposal ("FIRS announces 40% band…"). **Bounding controls (all pre-existing, restated as security controls):** Tier-1 source allowlist — content is fetched only from allowlisted authorities (DQ-006 gates the list itself); mandatory provenance fields (source identity, date, verbatim excerpt) per `compliance-monitoring-source-policy.md`; the deterministic C12 validator computes the authoritative diff/impact — LLM text never becomes operative data; the mandatory human approval gate (D-02-04) with R4/R5 protections is the final boundary. C11's worst compromise yields a *rejected proposal*, and SG-11 keeps it that way.

### T6 — Model output treated as executable or authoritative
**Bounding controls:** LLM output is never executed (no code/SQL paths exist in the portfolio design); numeric values in C5 narration must be trace-sourced with programmatic provenance checking (CG-5's zero-hallucination eval); C7's detector is deterministic — the LLM narrates *already-flagged* anomalies and cannot flag or unflag; any write anywhere goes through C10's structured confirmation showing deterministically-fetched record/field/value — never the model's restatement (the confirmation UI renders from the pending-action record, not from chat text).

### T7 — Confirmation-protocol subversion (C10)
An attacker (or injected content) tries to get a mutation confirmed that the operator didn't understand. **Bounding controls:** payload-as-presented frozen at proposal time (`approval-security-design.md` §4); confirmation is a distinct authenticated UI action, never a chat reply (source document's own rule, kept); idempotent execution; R4-grade records of every proposal/confirmation/rejection/expiry (CG-10).

## 3. Cross-cutting requirements added by this threat model

1. **Capability-scoped tool registries** — each capability's session exposes its minimum tool set (per the capability matrix's "required tools" rows), enforced at session construction, not by prompt. New gate item in SG-3/5/7/11/13.
2. **C11 context isolation** — no workspace-scoped tool is ever registered in a C11 session (formalises T4's control). New gate item in SG-11.
3. **Injection test evidence at launch** — each LLM capability launches with a committed adversarial test set exercising T1/T2 (and T5 for C11, header-borne injection for C13), demonstrating refusal/containment. Verification design belongs to Stage 10 (`stage-10-handoff.md`); the *existence* of the evidence is a security gate.
4. **Untrusted-data framing in serialization** — the tool serializer renders DB string values as data (quoted/delimited), never interpolated into instruction-position text. Stage 08 mechanism; stated here as a requirement.

## 4. What this model does not cover (explicitly)

Model-supply-chain risk (provider compromise), denial-of-wallet/cost abuse beyond W3 rate limiting, and multi-operator collusion are out of scope at this deployment scale; none is portfolio-blocking. Availability of the LLM provider is an operational concern (the source document's GPT-4o fallback), not a security gate.
