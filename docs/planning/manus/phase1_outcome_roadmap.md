# Phase 1 Outcome-Based Roadmap: AI-Ready Payroll Bureau Platform

**Author:** Manus AI (Senior Product Strategist & Delivery Architect)

## 🎯 Context

This roadmap outlines the strategic delivery for Phase 1 of an AI-ready Payroll Bureau platform. The system is architected for future agentic workflows but will be operationally manual in its initial execution, with a strong focus on correctness, auditability, and state control. Manual compliance reporting is a key characteristic of this phase.

## 🔒 Phase 1 Scope Constraints

**Must include:**

- Single payroll bureau

- Single client

- Monthly payroll only

- Salaried staff only

- Lagos (LIRS) + Federal tax logic

- Pension deduction logic

- Salary component configuration

- Payroll state transitions (Draft → Calculated → Approved → Locked)

- Immutable audit logging

- Manual compliance report generation (system produces data, human files)

**Must NOT include:**

- Autonomous AI agents

- Auto-filing to LIRS/FIRS

- Multi-client scaling logic in workflows

- Self-healing payroll

- Automated anomaly resolution

- Event-driven distributed architecture beyond structural readiness

## 🧠 Objective

To produce a Risk-Ordered, Outcome-Based Roadmap that defines what must be true for Phase 1 to be considered complete, what risks are eliminated at each milestone, what operational capabilities are unlocked, and what trust guarantees are achieved. This is an outcome roadmap, not a feature roadmap.

## 1️⃣ Define Phase 1 Success Criteria

Phase 1 will be considered successful when the following measurable outcomes are consistently achieved:

- **End-to-End Payroll Cycle Completion:** A full monthly payroll cycle for the single client can be initiated, processed, and finalized entirely within the system, eliminating reliance on external spreadsheets for calculation and data management.

- **Traceable Calculations:** Every calculated gross component, deduction, and net pay amount on a payslip can be directly traced back to the specific versioned rules (statutory, salary definition, custom) and employee inputs used at the time of calculation, as recorded in the `PAYROLL_RESULT.calculations_snapshot_jsonb`.

- **Immutable Payroll Records:** Once a `PAYROLL_RUN` reaches a `LOCKED` status, no associated `PAYROLL_RESULT` can be altered or deleted. Any corrections require a new, distinct correction run, preserving the integrity of historical data.

- **Comprehensive Audit Logging:** All significant data modifications (e1.g., employee data updates, rule changes) are automatically captured in an immutable `AUDIT_LOG`, detailing who, what, when, and the old/new values, verifiable via CDC.

- **Manual Compliance Report Generation:** The system can reliably generate all necessary data for LIRS and Federal compliance reports (e.g., PAYE, Pension summaries) in a structured format, enabling manual submission without requiring recalculation or manual data aggregation.

- **Configurable Payroll Logic:** The system can successfully process payroll using client-specific salary structures and custom rules defined as metadata, demonstrating the flexibility of the `RulesEngine`.

- **Strong Tenant Isolation (Structural):** The underlying database schema (Schema-per-Tenant) is proven to enforce logical separation of client data, even though only one client is active in Phase 1.

## 2️⃣ Identify Core Risk Categories

For a payroll bureau, managing risk is paramount. Phase 1 is designed to systematically eliminate or mitigate the most critical risks from day one.

### Calculation Risk

- **Why it matters:** Incorrect calculations lead to underpayment or overpayment of employees, financial penalties from regulatory bodies, employee dissatisfaction, and reputational damage. In a payroll bureau, calculation errors for one client can quickly escalate to many.

### Compliance Risk

- **Why it matters:** Failure to adhere to statutory requirements (e.g., PAYE, Pension, NHF) results in significant fines, legal action, and loss of operating license. Payroll bureaus are legally responsible for their clients' compliance.

### Data Integrity Risk

- **Why it matters:** Corrupted, inconsistent, or lost payroll data can halt operations, lead to incorrect payments, and compromise audit trails. Inaccurate historical data makes dispute resolution impossible.

### Operational Risk

- **Why it matters:** Manual, spreadsheet-driven processes are prone to human error, time-consuming, and lack scalability. High operational overhead impacts profitability and service delivery speed.

### Audit & Trust Risk

- **Why it matters:** Lack of transparent, immutable audit trails erodes trust with clients and employees, makes dispute resolution contentious, and fails to meet regulatory scrutiny. The inability to explain"why" a calculation occurred is a major business liability.

### Future Scalability Risk

- **Why it matters:** Building a system that cannot scale beyond a single client without a major redesign is a waste of investment. The architecture must be future-proof to support the business goal of becoming a multi-tenant SaaS platform.

## 3️⃣ Define Milestones as Risk Elimination Phases

Phase 1 is structured into four sequential milestones, each designed to eliminate critical risks and unlock essential operational capabilities, building trust and preparing the platform for future expansion.

### Milestone 1: Foundational Data Integrity & Core Configuration

- **Outcome Achieved:** Secure and structured storage for core employee data and foundational payroll rules. The system can store all necessary inputs for a payroll run in a controlled, versioned, and auditable manner.

- **Risks Reduced:**
  - **Data Integrity Risk:** Mitigated by enforcing schema validation for JSONB fields and establishing clear data models for `EMPLOYEE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, and `PayrollRule`.
  - **Calculation Risk (Initial):** Reduced by defining a structured, metadata-driven approach for rules, ensuring they are consistently stored and retrievable.

- **Capabilities Unlocked:**
  - Ability to define and store employee PII securely (encrypted JSONB).
  - Ability to define system-owned statutory rules (PAYE, Pension, NHF) with effective dates.
  - Ability to define client-specific salary structures and custom payroll rules as versioned metadata.
  - Manual provisioning of a single `Account` and `WORKSPACE`.

- **Business Impact:** Establishes the single source of truth for all payroll inputs, significantly reducing manual data entry errors and ensuring a consistent, auditable basis for all future calculations. This is the bedrock of trust.

- **What is still not possible:** Running a full payroll calculation for any employee.

- **What is Deferred:** Automated data ingestion (beyond manual JSON scripts), full payroll processing, any UI.

### Milestone 2: Deterministic Payroll Calculation Engine

- **Outcome Achieved:** A fully functional, metadata-driven payroll engine that can accurately and deterministically calculate gross pay, statutory deductions, and net pay for a single employee based on configured rules.

- **Risks Reduced:**
  - **Calculation Risk (Core Logic):** Significantly reduced by proving the correctness and consistency of the `RulesEngine` against manual calculations for a single employee.
  - **Compliance Risk (Statutory Deductions):** Mitigated by demonstrating accurate application of LIRS and Federal tax logic, and pension deduction rules.

- **Capabilities Unlocked:**
  - Ability to perform end-to-end payroll calculations for an individual employee.
  - Generation of a `PAYROLL_RESULT` record, including the comprehensive `calculations_snapshot_jsonb` for full explainability.
  - Emission of `EmployeeProcessed` events to the `EventStore` (append-only).

- **Business Impact:** Proves the core computational integrity of the platform, enabling verification of correctness against manual calculations and building confidence in the system's ability to handle complex payroll logic. This is where the system starts to deliver on its promise of accurate payments.

- **What is still not possible:** Processing a full payroll run for all employees in a batch, managing the lifecycle of a `PAYROLL_RUN`.

- **What is Deferred:** Batch processing for multiple employees, payroll run management workflows, automated payslip generation.

### Milestone 3: End-to-End Payroll Run & Immutability

- **Outcome Achieved:** A complete payroll run can be initiated, processed for all employees of the single client, and finalized, with all results immutably stored and comprehensively audit-logged. The system can manage the full lifecycle of a payroll run.

- **Risks Reduced:**
  - **Operational Risk (Manual Calculation):** Eliminated for the single client by automating the entire calculation process for all employees, drastically reducing processing time and human error.
  - **Data Integrity Risk (Post-Calculation Alteration):** Mitigated by enforcing immutability of `PAYROLL_RESULT` records once a `PAYROLL_RUN` is `LOCKED`.
  - **Audit & Trust Risk (Lack of Immutable Records):** Reduced by ensuring all significant data changes are captured by the `CDCMechanism` into the `AUDIT_LOG` and all payroll processing steps are recorded in the `EventStore`.

- **Capabilities Unlocked:**
  - Ability to manage a `PAYROLL_RUN` lifecycle (Draft → Calculated → Approved → Locked).
  - Generation of all `PAYROLL_RESULT`s for all employees for a given period.
  - Enforcement of the `rules_context_snapshot` for compliance locking, ensuring consistent rule application throughout a run.

- **Business Impact:** Eliminates spreadsheet reliance for the entire payroll calculation process for the initial client, significantly reducing processing time and human error. Provides a tamper-proof, verifiable record of all payroll decisions, building foundational trust with the client.

- **What is still not possible:** Automated reporting, external integrations, user-facing UI for payroll management.

- **What is Deferred:** Automated external filing, multi-client operations, user-facing reporting dashboards.

### Milestone 4: Explainable Payroll & Compliance Readiness

- **Outcome Achieved:** The system can generate all necessary data for required compliance reports and provide detailed, verifiable explanations for any payroll result, ensuring full auditability and transparency.

- **Risks Reduced:**
  - **Compliance Risk (Reporting):** Mitigated by providing all necessary aggregated data for LIRS and Federal reports, reducing the risk of manual errors during report preparation.
  - **Audit & Trust Risk (Explainability):** Eliminated by demonstrating the ability to trace every calculation step and rule application, making payroll results fully transparent and defensible.

- **Capabilities Unlocked:**
  - Ability to extract aggregated data for LIRS/Federal reports from `PAYROLL_RESULT`s.
  - Ability to retrieve and interpret detailed `calculations_snapshot_jsonb` for dispute resolution and forensic analysis.
  - Demonstration of the `rules_context_snapshot` to prove which specific rules were applied for any historical payroll run.

- **Business Impact:** Provides the necessary outputs for regulatory compliance and builds profound trust through transparent, verifiable payroll calculations. This milestone ensures the bureau can confidently stand behind every payslip and report generated by the system.

- **What is still not possible:** Automated external filing, multi-client operations, user-facing reporting dashboards.

- **What is Deferred:** User-facing reporting dashboards, advanced analytics, any UI for audit or compliance reporting.

## 4️⃣ Connect Milestones to Architecture

This section explicitly links each milestone to the underlying architectural components, demonstrating how the roadmap leverages the designed ERD and workflows.

### Milestone 1: Foundational Data Integrity & Core Configuration

- **Tables Becoming Active:**
  - `Account`: Manually provisioned for the payroll bureau.
  - `WORKSPACE`: Manually provisioned for the single client.
  - `EMPLOYEE`: Populated via manual JSON ingestion.
  - `STATUTORY_RULE`: Populated via manual JSON ingestion for Nigerian compliance.
  - `TAX_BAND`: Populated as part of `STATUTORY_RULE` definition.
  - `SALARY_DEFINITION`: Populated via manual JSON ingestion for client-specific structures.
  - `PayrollRule`: Populated via manual JSON ingestion for client-specific rules.
  - `AUDIT_LOG`: Begins receiving entries via `CDCMechanism` for all `INSERT` operations on the above tables.

- **Workflows Becoming Usable:**
  - **Business Process 1: Workspace Setup & Configuration** (Manual steps for `Account`, `WORKSPACE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`).
  - **Business Process 2: Employee Onboarding / Management** (Manual JSON ingestion for `EMPLOYEE`).

- **State Transitions Enforced:** None directly on `PAYROLL_RUN` yet, but `is_active` flags on rules become relevant.

- **Validations Becoming Mandatory:**
  - JSON Schema validation for `SALARY_DEFINITION.components_jsonb`, `STATUTORY_RULE.calculation_logic_jsonb`, `PayrollRule.rule_definition_json`.
  - Uniqueness constraints on `employee_number` within a `WORKSPACE`.
  - Effective date validation for rules (`effective_from`, `effective_to`).

### Milestone 2: Deterministic Payroll Calculation Engine

- **Tables Becoming Active:**
  - `PAYROLL_RUN`: Single record created with `status: DRAFT`.
  - `PAYROLL_RESULT`: Single record created for one employee.
  - `EventStore`: Begins receiving `EmployeeProcessed` events (append-only).

- **Workflows Becoming Usable:**
  - **Partial Business Process 3: Payroll Calculation & Processing** (Specifically, the calculation logic for a single employee, triggered via API).

- **State Transitions Enforced:** `PAYROLL_RUN` transitions from `DRAFT` to `CALCULATING` and then to `CALCULATED` (for a single employee context).

- **Validations Becoming Mandatory:**
  - Validation of `PAYROLL_RUN.rules_context_snapshot` population upon initiation.
  - Validation of `RulesEngine` logic against `SALARY_DEFINITION`, `STATUTORY_RULE`, `TAX_BAND`, and `PayrollRule`.
  - JSONB structure validation for `PAYROLL_RESULT.gross_components_jsonb`, `PAYROLL_RESULT.deductions_jsonb`, and `PAYROLL_RESULT.calculations_snapshot_jsonb`.

### Milestone 3: End-to-End Payroll Run & Immutability

- **Tables Becoming Active:** All tables are active, with `PAYROLL_RUN` and `PAYROLL_RESULT` being fully populated for all employees.

- **Workflows Becoming Usable:**
  - **Full Business Process 3: Payroll Calculation & Processing** (Batch processing for all employees in a `WORKSPACE`).

- **State Transitions Enforced:** Full `PAYROLL_RUN` lifecycle: `DRAFT` → `CALCULATING` → `CALCULATED` → `APPROVED` → `LOCKED`. Immutability enforced on `PAYROLL_RESULT` records once `PAYROLL_RUN` is `LOCKED`.

- **Validations Becoming Mandatory:**
  - Enforcement of `PAYROLL_RUN.rules_context_snapshot` for all employee calculations within a run.
  - Application-level prevention of `UPDATE`/`DELETE` on `PAYROLL_RESULT` for `LOCKED` runs.
  - Append-only enforcement for `EventStore` and `AUDIT_LOG`.

### Milestone 4: Explainable Payroll & Compliance Readiness

- **Tables Becoming Active:** All tables are actively queried for reporting and audit purposes.

- **Workflows Becoming Usable:**
  - **Business Process 4: Payslip Generation & Distribution** (Manual distribution).
  - **Business Process 5: Compliance Reporting (LIRS + Federal)** (Manual submission).
  - **Workflow 7: Audit Retrieval** (Manual query of `AUDIT_LOG` and `PAYROLL_RESULT`).

- **State Transitions Enforced:** `PAYROLL_RUN` status `LOCKED` is a prerequisite for generating final reports.

- **Validations Becoming Mandatory:**
  - Data consistency checks between `PAYROLL_RESULT` aggregates and `PAYROLL_RUN` totals.
  - Verification of `calculations_snapshot_jsonb` content for audit trails.

## 5️⃣ Define Phase 1 Completion Gate

Phase 1 will be declared complete when the following conditions are met and demonstrated for the single client:

1. **End-to-End Payroll Execution:** A full monthly payroll cycle, from employee data ingestion to final `PAYROLL_RESULT` generation, can be successfully executed for all salaried employees of the single client, without reliance on external spreadsheets for calculation.

1. **Rule-Driven Calculation:** All gross pay components and statutory deductions (LIRS + Federal tax, Pension) are calculated solely based on the metadata stored in `SALARY_DEFINITION`, `STATUTORY_RULE`, `TAX_BAND`, and `PayrollRule` tables.

1. **Immutability Enforced:** Once a `PAYROLL_RUN` transitions to `LOCKED` status, no `PAYROLL_RESULT` records associated with that run can be altered or deleted. Any corrections require a new, distinct correction run.

1. **Comprehensive Auditability:** All `INSERT` and `UPDATE` operations on core data tables (`EMPLOYEE`, `SALARY_DEFINITION`, `STATUTORY_RULE`, `PayrollRule`, `PAYROLL_RUN`, `PAYROLL_RESULT`) are captured in the `AUDIT_LOG` via CDC, providing a verifiable trail of changes.

1. **Explainable Results:** For any `PAYROLL_RESULT`, the `calculations_snapshot_jsonb` field contains a complete, traceable breakdown of all inputs, rules, and intermediate steps that led to the final net pay, enabling clear explanation and dispute resolution.

1. **Compliance Report Data Generation:** The system can produce accurate, aggregated data (e.g., total PAYE, total Pension) from `PAYROLL_RESULT` records, which can be used to manually generate and submit LIRS and Federal compliance reports.

1. **Architectural Validation:** The core architectural patterns (metadata-driven rules, append-only Event Store, CDC-based audit, Schema-per-Tenant structure) are implemented and proven to function as designed, laying a solid, non-throwaway foundation for future phases.

## 6️⃣ Explicitly Separate “Agentic Ready” from “Agentic Enabled”

Phase 1 is meticulously designed to be **Agentic-Ready**, meaning it provides the foundational architecture and data structures necessary for future AI and agentic patterns. However, it is explicitly **not Agentic-Enabled**; no autonomous decision-making or AI-driven automation will be present in this phase.

### What Makes the System Agentic-Ready in Phase 1?

- **Rule Engine Abstraction:** The `RulesEngine` is a distinct, pluggable component that interprets metadata-driven rules. This abstraction allows future AI agents to interact with and even generate/validate rules without needing to understand core application code.

- **Structured Calculation Dependency Storage:** The `SALARY_DEFINITION.components_jsonb` and `STATUTORY_RULE.calculation_logic_jsonb` explicitly define calculation steps and dependencies. This structured data is ideal for AI agents to analyze, understand, and even optimize calculation flows.

- **Explicit State Transitions:** The clear lifecycle of a `PAYROLL_RUN` (Draft → Calculated → Approved → Locked) provides well-defined boundaries for agent intervention. Agents can be designed to trigger or validate transitions based on specific conditions.

- **Deterministic Calculation Engine:** The `RulesEngine`, combined with the `rules_context_snapshot` in `PAYROLL_RUN`, ensures that payroll calculations are deterministic and repeatable. This is crucial for AI agents that need to verify or predict outcomes.

- **Immutable Audit Event History (****`AUDIT_LOG`**** & ****`EventStore`****):** The comprehensive, append-only `AUDIT_LOG` (via CDC) and `EventStore` provide a rich, historical dataset of all system activities and domain events. This data is invaluable for training AI agents for anomaly detection, compliance checking, and predictive analytics.

- **Modular Service Boundaries:** The microservices-oriented logical architecture (e.g., `PayrollProcessingService`, `PayrollConfigService`) creates clear separation of concerns. This allows AI agents to be integrated as specialized services that interact with specific domains without disrupting the entire system.

- **Explainable Payroll Results (****`calculations_snapshot_jsonb`****):** Each `PAYROLL_RESULT` is self-contained with a detailed breakdown of its calculation. This provides a "reasoning trace" that AI agents can use to understand *why* a particular result was reached, enabling them to perform validation, explain outcomes, or even suggest improvements.

### No Autonomous Decision-Making in Phase 1

It is critical to reiterate that despite being Agentic-Ready, Phase 1 will feature **no autonomous decision-making by AI agents**. All triggers, validations, and approvals will be manual or system-driven based on predefined, explicit logic. AI integration is a future capability that this foundational phase enables, but does not implement.

## 7️⃣ Gap Analysis: Prompt vs. Final Roadmap

This section provides a clear analysis of how the final roadmap aligns with the provided prompt, highlighting additional considerations and deferred items.

### Alignment (What I've Considered that is Specified)

- **Outcome-Based Roadmap:** The roadmap is structured around outcomes and risk elimination, not features, as requested.

- **Phase 1 Scope Constraints:** All `Must include` and `Must NOT include` constraints from the prompt have been strictly followed.

- **Core Risk Categories:** The roadmap identifies and addresses the specified risk categories.

- **Milestones as Risk Elimination:** The roadmap is structured into milestones that explicitly define outcomes, risks reduced, and capabilities unlocked.

- **Architectural Alignment:** Each milestone is connected to the specific tables, workflows, and validations that become active, aligning with the ERD.

- **Completion Gate:** A clear, testable set of completion criteria for Phase 1 is defined.

- **Agentic-Ready vs. Agentic-Enabled:** The distinction is explicitly made, detailing what makes the system ready for AI without implementing any autonomous features.

### Additional Considerations (What I've Considered that was Not Explicitly Specified)

These are items I included in the architecture and roadmap to enhance robustness and mitigate future risks, based on best practices for financial systems:

- **`rules_context_snapshot`**** in ****`PAYROLL_RUN`****:** This is a critical architectural decision I introduced to ensure payroll locking and prevent mid-month rule changes from affecting in-progress runs. It provides a concrete mechanism for achieving the "No payroll can be altered after lock" success criterion.

- **`EventStore`**** as a "Flight Recorder":** I have explicitly defined the `EventStore`'s role in Phase 1 as an append-only log. This aligns with the "Event-driven distributed architecture beyond structural readiness" constraint while ensuring the data needed for future phases is captured from day one.

- **`personal_details_encrypted`**** in ****`EMPLOYEE`****:** I specified that the JSONB field for personal details should be encrypted. This is a critical security consideration for handling PII that was not explicitly mentioned in the prompt but is essential for a payroll system.

- **Schema Versioning in JSONB fields:** I included `schema_version` in `SALARY_DEFINITION` and `PayrollRule` to support the future evolution of the JSON structures. This is a key governance mechanism to prevent "JSON Chaos" and ensure long-term maintainability.

### Deferred Items (What You Specified that is Not in Phase 1)

All items specified in the prompt's `Must NOT include` section have been deferred. The roadmap clearly marks these as out of scope for Phase 1. For clarity:

- **Approval Workflow:** While the `Approved` state is part of the `PAYROLL_RUN` lifecycle, the implementation of a multi-level, user-driven approval workflow is **Deferred: Phase 3**.

- **Automated Anomaly Resolution & Self-Healing Payroll:** These are advanced agentic capabilities and are **Deferred: Phase 4**.

- **Multi-Client Workflows:** All operational aspects of managing multiple clients are **Deferred: Phase 2**.

- **Auto-Filing to LIRS/FIRS:** All external API integrations for automated filing are **Deferred: Phase 3** or later.

This roadmap provides a robust, compliant, and future-proof foundation for Phase 1, with the additional considerations serving to strengthen the architecture and mitigate future risks.

