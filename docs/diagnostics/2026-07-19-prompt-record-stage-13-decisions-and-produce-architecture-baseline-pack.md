# Casper Prompt — Record Stage 13 Decisions and Produce Architecture Baseline Pack

You are working in:

`docs/programmes/agentic-architecture-review/`

## Objective

Update the Stage 13 decision record with the human decisions made so far, then produce a consolidated Architecture Baseline Pack for human review.

Do not close Stage 13, supersede the existing architecture document, approve the roadmap finally, or authorise implementation.

---

## 1. Record the human decisions

Record the following decisions accurately in the appropriate Stage 13 and `_core` decision/state files.

### DP-1 — Statutory approval controls

Approved:

- The same authorised operator may propose and approve a statutory rule change for v1.
- Password re-authentication is required at approval.
- MFA is deferred and is not a v1 launch gate.
- The design must remain compatible with introducing MFA later.

Use the decision-pack terminology:

- Part A: **A1**
- Part B: **B2**

Do not describe this as A2.

### DP-2 — Source-document disposition

Status: **Pending human review**

Do not supersede or retire:

`docs/architecture/agent-layer-architecture.html`

or its frontend mirror.

The decision remains open until the consolidated Architecture Baseline Pack has been produced and reviewed.

### DP-3 — Product direction

Approved:

- Continue with the **single-bureau, SaaS-ready** direction.
- Optimise the current platform for Sandy’s bureau operations.
- Preserve a credible future path to multi-bureau SaaS.
- Do not place full SaaS capabilities on the current critical path.
- Active SaaS expansion requires separate commercial evidence and human authorisation.

### DP-4 — Professional advice engagement

Approved:

Initiate, at the appropriate point, a Nigerian payroll, tax, legal or regulatory advisory engagement to validate:

- authoritative statutory-monitoring sources and required monitoring cadence;
- statutory and data-protection retention obligations.

This is preparatory work only and does not authorise implementation.

### DP-5 — Audit-tamper residual risk

Noted:

- Accept the documented residual audit-tamper risk for the current single-bureau managed-PostgreSQL deployment.
- Revisit it only when one of the existing review triggers occurs, including a material deployment change, SaaS expansion, regulatory demand or suspected tampering.

### DP-6 — Statutory-rule uniqueness change

Noted:

- The proposed widening of the `statutory_rule` uniqueness constraint will be handled through the normal architecture-council and implementation governance process when C12 is authorised.
- No implementation is authorised now.

### DP-7 — Onboarding measurement evidence

Resolved with an amended evidence approach:

- The timing of the next live client onboarding is currently unknown.
- A future live onboarding is not the only acceptable evidence opportunity.
- Create a controlled onboarding benchmark using representative historical client information or appropriately synthetic data based on previous onboarding cases.
- Measure the existing/manual process and the platform-supported process consistently.
- Include time, effort, interventions, errors, completeness and other relevant onboarding measures.
- Collect evidence from a future live onboarding opportunistically when available.
- Ensure test or replay data is isolated, governed and safely removed or retained according to the agreed evidence protocol.

Do not describe the simulated onboarding as proof of live operational performance. Label it clearly as controlled benchmark evidence.

### DP-8 — Commercial-demand evidence

Approved:

- Distinguish validated platform capability from validated market demand.
- External claims may describe capabilities where supported by evidence.
- Do not describe demand, willingness to pay, adoption or SaaS commercial viability as validated without customer or market evidence.
- SaaS expansion remains subject to that evidence and separate human approval.

### DP-9 — Roadmap approval

Status: **Pending final human confirmation**

The roadmap may be treated as the current proposed implementation sequence, but it is not finally approved.

Final approval depends on human review of the Architecture Baseline Pack and confirmation that:

- the target architecture is understood and accepted;
- the roadmap implements that accepted architecture;
- roadmap sequencing, dependencies and definitions of done remain appropriate.

---

## 2. Produce the Architecture Baseline Pack

Create a consolidated, navigable architecture pack from the evidence and decisions already produced across the programme.

Do not invent a new target architecture.

Synthesize the approved and proposed direction from the Stage 08–13 outputs, existing architecture documentation, decisions, findings, capability maps and roadmap.

The pack must clearly distinguish:

- confirmed current state;
- approved target direction;
- proposed but not yet finally approved items;
- deferred capabilities;
- rejected capabilities;
- blocked capabilities;
- assumptions and evidence gaps.

### Required architecture views

#### A. Executive architecture summary

Provide a concise explanation of:

- the current architecture;
- the reason for change;
- the target architectural direction;
- the role of deterministic payroll services;
- the permitted and prohibited role of AI;
- the major transition implications.

#### B. System context

Show:

- operators and administrators;
- payroll bureau;
- client companies;
- employees;
- regulatory or statutory information sources;
- external services;
- payroll platform boundary;
- AI and model-provider boundary where relevant.

Clearly show which parties and systems are inside and outside the platform boundary.

#### C. Current-state architecture

Represent the current or previously proposed architecture accurately, including the existing Track P, V, W, X and Y model where relevant.

Identify:

- retained elements;
- weaknesses;
- ambiguities;
- unimplemented intent;
- assumptions invalidated by the review.

Do not present unverified historical intent as implemented behaviour.

#### D. Target logical architecture

Show the main logical capabilities and their relationships, including as applicable:

- identity and access;
- workspace and tenancy;
- payroll readiness;
- payroll calculation;
- deterministic rules;
- statutory-rule management;
- approvals and control workflows;
- snapshots and evidence;
- audit and event foundations;
- reconciliation;
- dry-run validation;
- operator assistant;
- trace explanation;
- anomaly detection;
- compliance monitoring;
- onboarding assistance.

Clearly distinguish deterministic platform capabilities from AI-assisted capabilities.

#### E. Data architecture

Show the principal information domains and ownership boundaries, including:

- workspace and tenancy data;
- employee and employment data;
- payroll inputs;
- salary and component definitions;
- statutory rules and versions;
- payroll runs and results;
- snapshots;
- audit records;
- events;
- reconciliations;
- AI interaction evidence where approved.

Explain immutability, versioning and evidence boundaries at a high level.

#### F. Execution architecture

Show the principal runtime flows, including:

- normal payroll execution;
- approval and lock flow;
- retry and correction flow;
- statutory-rule change flow;
- AI-assisted explanation or analysis flow;
- anomaly detection flow;
- compliance-monitoring flow where proposed.

Make the control boundary explicit:

- AI may explain, analyse, identify, summarise or recommend within approved capabilities.
- AI must not calculate payroll values authoritatively.
- AI must not mutate payroll state.
- AI must not approve changes.
- AI must not bypass deterministic controls.

#### G. Agent and AI architecture

Show:

- which AI capabilities are approved;
- which are blocked, deferred or rejected;
- available tools or read paths;
- prohibited write paths;
- deterministic validation boundaries;
- human decision points;
- evidence and audit capture;
- model-provider boundary;
- failure and fallback behaviour at a conceptual level.

Avoid depicting autonomous agents where the review rejected autonomous operation.

#### H. Security and control architecture

Show:

- authentication;
- authorisation and roles;
- tenant isolation;
- step-up password re-authentication;
- future MFA compatibility;
- statutory change controls;
- audit boundaries;
- secrets and model-provider boundaries;
- human approval points;
- residual risks.

Reflect the DP-1 decision exactly.

#### I. Current-to-target comparison

Create a direct mapping that shows for every major current architecture element whether it is:

- retained;
- revised;
- replaced;
- removed;
- blocked;
- rejected;
- deferred;
- newly introduced.

Include the reason and the evidence or decision source.

#### J. Capability-to-roadmap alignment

Map each target capability to:

- proposed tranche;
- prerequisite capabilities;
- relevant decisions;
- required evidence;
- launch or implementation gates.

This is a validation view, not final roadmap approval.

Highlight any roadmap item that cannot be justified by the target architecture or any target capability absent from the roadmap.

#### K. Decision and evidence traceability

For every significant architecture component or boundary, provide traceability to:

- programme stage;
- decision ID;
- finding or evidence;
- capability-map entry;
- roadmap item;
- unresolved evidence gap where applicable.

A reviewer should be able to answer:

- Why does this component exist?
- Why is this boundary present?
- Which review output supports it?
- Has it been approved, proposed, deferred or rejected?

#### L. Supersession assessment

Provide a recommendation on whether the existing architecture document should be:

- superseded in full;
- superseded with selected sections retained;
- amended rather than replaced.

List exactly what should be preserved, rewritten, archived or marked historical.

This is a recommendation only. Do not execute supersession or remove the existing document.

---

## 3. Presentation requirements

The output should be suitable for review by both technical and non-technical stakeholders.

Use:

- Mermaid diagrams where maintainable;
- concise explanatory text;
- clear legends;
- consistent terminology;
- direct links to source evidence;
- explicit status labels.

Avoid producing another long narrative-only document.

The pack should allow a reviewer to compare the current and target architecture without opening every Stage 08–13 file.

Where one diagram would become unreadable, create separate focused views rather than one oversized diagram.

---

## 4. Validation

Before presenting the pack:

- run a terminology and traceability consistency check;
- verify every target capability against the Stage 12 direction outputs;
- verify every roadmap mapping against the Stage 13 proposed roadmap;
- verify all human decisions against the wording above;
- identify contradictions rather than silently resolving them;
- ensure no build authorisation is implied;
- ensure DP-2 and DP-9 remain open.

Have the programme critic review the Architecture Baseline Pack for:

- fidelity to the review evidence;
- missing architecture views;
- invented architecture;
- misleading current-state claims;
- unclear AI boundaries;
- broken traceability;
- premature closure or authorisation.

Address documentary defects where permitted, but do not make new human decisions.

---

## 5. Stop condition

Stop and return for human review once:

- the decisions have been recorded;
- the Architecture Baseline Pack has been produced;
- the critic review has completed;
- any permitted documentary corrections have been made;
- DP-2 remains pending;
- DP-9 remains pending;
- Stage 13 remains open.

Return:

- files created or updated;
- commit SHA;
- critic outcome;
- unresolved contradictions or evidence gaps;
- the exact next human decisions required;
- confirmation that no implementation, supersession or programme closure was authorised.
