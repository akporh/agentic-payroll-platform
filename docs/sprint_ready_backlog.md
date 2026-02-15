## 🚀 Sprint 0: Infrastructure & DevOps Foundation (Risk: Operational Readiness)

**Objective:** Establish a robust, secure, and automated development and deployment environment. This sprint eliminates the fundamental risks associated with operational stability, security, and developer productivity, ensuring a solid foundation for all subsequent domain development.

### 0.1 Technical Story: Repository Setup & Branching Strategy

- **Description:** Initialize the code repository, define the branching strategy (e.g., GitFlow, Trunk-Based Development), and set up initial repository access controls.

- **Acceptance Criteria:**
  - A Git repository is initialized and hosted (e.g., GitHub, GitLab, Bitbucket).
  - A clear branching strategy is documented and agreed upon by the team.
  - Basic access controls (e.g., read/write permissions) are configured for team members.

- **Definition of Done (DoD):** Repository created, branching strategy documented, and team access configured.

- **Technical Notes/Dependencies:** Requires choice of Git hosting provider.

- **Architectural Impact:** Establishes version control and collaboration framework.

- **Effort Estimate:** Low

- **Priority:** Critical

### 0.2 Technical Story: CI Pipeline for Code Quality & Build Automation

- **Description:** Implement a Continuous Integration (CI) pipeline to automate code quality checks, unit testing, and build processes for the backend services.

- **Acceptance Criteria:**
  - A CI pipeline is configured to trigger on code commits to feature branches and main/master.
  - The pipeline automatically runs linting, static analysis, and unit tests.
  - The pipeline successfully builds deployable artifacts (e.g., Docker images, executable JARs/Python packages).
  - Build status is reported back to the repository (e.g., GitHub Checks).

- **Definition of Done (DoD):** CI pipeline implemented, passing for a sample service, and integrated with the repository.

- **Technical Notes/Dependencies:** Requires choice of CI/CD tool (e.g., GitHub Actions, GitLab CI, Jenkins). Integrates with `0.1 Repository Setup`.

- **Architectural Impact:** Ensures code quality, consistency, and automated build processes.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 0.3 Technical Story: Database Provisioning & Migration Tooling

- **Description:** Automate the provisioning of PostgreSQL databases for development and staging environments, and integrate a database migration tool.

- **Acceptance Criteria:**
  - Scripts or Infrastructure as Code (IaC) templates exist to provision PostgreSQL instances.
  - A database migration tool (e.g., Flyway, Alembic) is integrated into the project.
  - Initial schema migrations can be applied automatically to a newly provisioned database.

- **Definition of Done (DoD):** Database provisioning automated, migration tool integrated, and initial schema applied successfully in a test environment.

- **Technical Notes/Dependencies:** Requires cloud provider (AWS RDS, Azure Database for PostgreSQL, GCP Cloud SQL) or local Docker setup. Integrates with `1.1 Setup Core Schema`.

- **Architectural Impact:** Provides managed, version-controlled database infrastructure.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 0.4 Technical Story: Environment Variable & Secret Management

- **Description:** Establish a secure and consistent method for managing environment variables and sensitive secrets (e.g., database credentials, API keys) across environments.

- **Acceptance Criteria:**
  - A clear strategy for environment variable usage is documented.
  - Sensitive secrets are stored and accessed securely (e.g., using a secrets manager like AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, or encrypted environment variables for MVP).
  - Application services can securely retrieve necessary secrets at runtime.

- **Definition of Done (DoD):** Secret management strategy documented, and a sample secret is securely injected into a test application.

- **Technical Notes/Dependencies:** Integrates with CI/CD pipeline and deployment process. Crucial for `1.4 PII Encryption`.

- **Architectural Impact:** Enhances security posture by protecting sensitive credentials.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 0.5 Technical Story: Centralized Logging Framework

- **Description:** Implement a centralized logging framework to capture application logs, system events, and errors from all services.

- **Acceptance Criteria:**
  - All application services are configured to emit structured logs (e.g., JSON format).
  - Logs are aggregated into a centralized logging system (e.g., ELK Stack, Splunk, cloud-native logging services).
  - Basic log filtering and searching capabilities are available.

- **Definition of Done (DoD):** Centralized logging configured, and logs from a sample service are successfully ingested and searchable.

- **Technical Notes/Dependencies:** Requires choice of logging aggregation tool. Integrates with `0.2 CI Pipeline`.

- **Architectural Impact:** Provides visibility into application behavior and aids debugging.

- **Effort Estimate:** Medium

- **Priority:** High

### 0.6 Technical Story: Error Monitoring & Alerting

- **Description:** Integrate an error monitoring solution to automatically detect, report, and alert on application errors and exceptions.

- **Acceptance Criteria:**
  - An error monitoring tool (e.g., Sentry, Datadog, New Relic, cloud-native monitoring) is integrated with application services.
  - Critical errors trigger alerts to the development team (e.g., via Slack, email).
  - Error reports include stack traces and relevant context.

- **Definition of Done (DoD):** Error monitoring configured, and a simulated error successfully triggers an alert.

- **Technical Notes/Dependencies:** Integrates with `0.5 Centralized Logging Framework`.

- **Architectural Impact:** Enables proactive identification and resolution of production issues.

- **Effort Estimate:** Medium

- **Priority:** High

### 0.7 Technical Story: Database Backup & Restore Strategy

- **Description:** Define and implement a strategy for regular database backups and a tested procedure for restoring data.

- **Acceptance Criteria:**
  - Automated daily backups of the PostgreSQL database are configured.
  - A documented procedure exists for performing a full database restore.
  - A test restore is successfully performed to verify the backup integrity.

- **Definition of Done (DoD):** Backup strategy documented, automated backups configured, and a successful test restore completed.

- **Technical Notes/Dependencies:** Leverages cloud provider database backup features or custom scripts. Crucial for disaster recovery.

- **Architectural Impact:** Ensures data durability and business continuity.

- **Effort Estimate:** Medium

- **Priority:** Critical

# Phase 1 Sprint-Ready Backlog: Trust Foundation MVP

**Author:** Manus AI (Senior Product Manager & Agile Delivery Lead)

## 🎯 Context

This document translates the Phase 1 User Story Map into a sprint-ready backlog, organized by risk-elimination milestones. Each story includes detailed acceptance criteria, definition of done, technical notes, and impact assessments to facilitate agile development and ensure alignment with the architectural vision.

## 🚀 Sprint 1: Foundation & Data Integrity (Risk: Schema & Ingestion)

**Objective:** Establish the core database schema, implement robust data validation for metadata, and set up foundational audit logging and security for PII. This sprint eliminates the primary risks associated with data integrity and chaotic rule definition.

### 1.1 Technical Story: Setup Core Schema and Database

- **Description:** Establish the foundational database schema for all core entities as per the finalized ERD, including all tables, columns, and relationships.

- **Acceptance Criteria:**
  - All tables (`Account`, `WORKSPACE`, `EMPLOYEE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, `PAYROLL_RESULT`, `AUDIT_LOG`, `EventStore`) are created in PostgreSQL.
  - All columns, including `JSONB` fields (e.g., `personal_details_encrypted`, `components_jsonb`, `calculation_logic_jsonb`, `rules_context_snapshot`, `calculations_snapshot_jsonb`), are correctly defined with appropriate data types.
  - Primary key and foreign key constraints are enforced as per the ERD.
  - Indexes are created for frequently queried columns (e.g., `workspace_id`, `employee_id`, `payroll_run_id`).

- **Definition of Done (DoD):** Database schema deployed to development environment and verified by a peer. All table and column definitions are documented.

- **Technical Notes/Dependencies:** Requires PostgreSQL database access and schema migration tools (e.g., Flyway, Alembic).

- **Architectural Impact:** Establishes the persistence layer, enabling all subsequent data storage and retrieval.

- **Compliance/Audit Impact:** Provides the structural foundation for data integrity and auditability.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 1.2 Technical Story: Implement JSON Schema Validation Framework

- **Description:** Develop a robust framework to define and enforce JSON Schemas for all `JSONB` fields that store metadata-driven rules and configurations.

- **Acceptance Criteria:**
  - A mechanism exists to define JSON Schemas for `SALARY_DEFINITION.components_jsonb`, `STATUTORY_RULE.calculation_logic_jsonb`, `PayrollRule.rule_definition_json`, and `EMPLOYEE.personal_details_encrypted`.
  - Any `INSERT` or `UPDATE` operation attempting to write invalid JSONB data (not conforming to its schema) to these fields is rejected at the API/service layer with a clear error message.
  - The framework supports schema versioning, allowing for future evolution of rule structures.

- **Definition of Done (DoD):** JSON Schema validation integrated into the API/service layer and unit/integration tested for all specified JSONB fields. Schema definitions are versioned and documented.

- **Technical Notes/Dependencies:** May involve using a JSON Schema library (e.g., `jsonschema` in Python) and integrating it into the data access layer or API validation.

- **Architectural Impact:** Enforces data consistency and structure for metadata-driven rules, preventing"JSON Chaos."

- **Compliance/Audit Impact:** Crucial for ensuring the integrity and reliability of payroll rules, directly impacting calculation accuracy and auditability.

- **Effort Estimate:** High

- **Priority:** Critical

### 1.3 Technical Story: Setup CDC for Audit Logging

- **Description:** Configure Change Data Capture (CDC) at the PostgreSQL database level to automatically stream all data modifications to core tables into an immutable `AUDIT_LOG` table.

- **Acceptance Criteria:**
  - CDC mechanism is configured to monitor `INSERT`, `UPDATE`, `DELETE` operations on `Account`, `WORKSPACE`, `EMPLOYEE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, `PAYROLL_RESULT`.
  - For each monitored operation, a corresponding entry is created in the `AUDIT_LOG` table with `entity_type`, `entity_id`, `action`, `old_value_jsonb`, `new_value_jsonb`, `performed_by`, and `performed_at`.
  - The `AUDIT_LOG` table is append-only; no `UPDATE` or `DELETE` operations are permitted on `AUDIT_LOG` records.

- **Definition of Done (DoD):** CDC is configured and tested. `AUDIT_LOG` entries are correctly generated for all CUD operations on monitored tables. Immutability of `AUDIT_LOG` is verified.

- **Technical Notes/Dependencies:** Requires PostgreSQL logical replication setup. `performed_by` will initially be a system user for manual JSON ingestion.

- **Architectural Impact:** Establishes a foundational, tamper-proof audit trail for all data changes.

- **Compliance/Audit Impact:** Provides the"gold standard" for auditability and compliance, especially for financial systems.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 1.4 Technical Story: Implement PII Encryption for Employee Data

- **Description:** Implement encryption-at-rest for sensitive employee Personal Identifiable Information (PII) stored in the `EMPLOYEE.personal_details_encrypted` JSONB field.

- **Acceptance Criteria:**
  - Data written to `EMPLOYEE.personal_details_encrypted` is encrypted before storage and decrypted upon retrieval by authorized services.
  - A secure key management strategy is defined (e.g., environment variables for MVP, KMS for later phases).
  - Encryption/decryption processes are robust and tested.

- **Definition of Done (DoD):** PII encryption/decryption implemented and unit/integration tested. Key management strategy documented.

- **Technical Notes/Dependencies:** Requires a cryptographic library (e.g., `cryptography` in Python). Initial key management can be simplified for MVP.

- **Architectural Impact:** Enhances data security and privacy for sensitive employee data.

- **Compliance/Audit Impact:** Addresses critical data protection requirements for PII, reducing compliance risk.

- **Effort Estimate:** Medium

- **Priority:** High

### 1.5 User Story: As a Payroll Admin, I can provision a new client workspace, so that I can begin configuring payroll for them.

- **Description:** Manually create the top-level `Account` and a `WORKSPACE` for the single client, linking it to the `Account`.

- **Acceptance Criteria:**
  - Given a valid `account_id` and `workspace_name`, a new `WORKSPACE` record is created in the database.
  - The `WORKSPACE` record is correctly linked to the `Account`.
  - The system confirms successful `WORKSPACE` creation.

- **Definition of Done (DoD):** Manual process for `Account` and `WORKSPACE` creation is documented. A `WORKSPACE` can be successfully created and linked to an `Account`.

- **Technical Notes/Dependencies:** Direct database insertion or a simple script for initial provisioning. Relies on `1.1 Setup Core Schema`.

- **Architectural Impact:** Establishes the tenant boundary for the MVP.

- **Compliance/Audit Impact:** `AUDIT_LOG` entries (via CDC) are generated for `Account` and `WORKSPACE` creation.

- **Effort Estimate:** Low

- **Priority:** Critical

### 1.6 User Story: As a Payroll Admin, I can define statutory rules (PAYE, Pension, NHF) for Nigeria, so that the system can correctly calculate mandatory deductions.

- **Description:** Manually ingest JSON files defining `STATUTORY_RULE`s (PAYE, Pension, NHF) and associated `TAX_BAND`s for the single client.

- **Acceptance Criteria:**
  - Given valid JSON for `STATUTORY_RULE` (e.g., PAYE) and associated `TAX_BAND`s, these records are successfully created in the database.
  - `STATUTORY_RULE.calculation_logic_jsonb` and `TAX_BAND` entries pass JSON Schema validation (from `1.2 Technical Story`).
  - `effective_from` and `effective_to` dates are correctly applied and validated.

- **Definition of Done (DoD):** All required Nigerian statutory rules and tax bands are successfully ingested and validated. JSON Schema definitions for these rules are complete.

- **Technical Notes/Dependencies:** Requires a script or direct database insertion for JSON file ingestion. Relies on `1.1 Setup Core Schema` and `1.2 Implement JSON Schema Validation Framework`.

- **Architectural Impact:** Populates the metadata-driven rules engine with core compliance logic.

- **Compliance/Audit Impact:** Directly addresses compliance with Nigerian tax and pension laws. `AUDIT_LOG` entries (via CDC) are generated for rule creation.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 1.7 User Story: As a Payroll Admin, I can define the client's salary structure, so that gross pay components are calculated according to their compensation policy.

- **Description:** Manually ingest JSON files defining the client-specific `SALARY_DEFINITION` for the single client.

- **Acceptance Criteria:**
  - Given valid JSON for `SALARY_DEFINITION`, a new record is successfully created for the `WORKSPACE`.
  - `SALARY_DEFINITION.components_jsonb` passes JSON Schema validation (from `1.2 Technical Story`) and dependency checks (e.g., no circular references).
  - `effective_from` and `effective_to` dates are correctly applied and validated.

- **Definition of Done (DoD):** Client's salary structure is successfully ingested and validated. JSON Schema definition for salary structure is complete.

- **Technical Notes/Dependencies:** Requires a script or direct database insertion for JSON file ingestion. Relies on `1.1 Setup Core Schema` and `1.2 Implement JSON Schema Validation Framework`.

- **Architectural Impact:** Populates the metadata-driven rules engine with client-specific compensation logic.

- **Compliance/Audit Impact:** Ensures accurate gross pay calculations based on client policy. `AUDIT_LOG` entries (via CDC) are generated for salary definition creation.

- **Effort Estimate:** Medium

- **Priority:** High

### 1.8 User Story: As a Payroll Admin, I can define custom payroll rules, so that client-specific allowances and deductions are applied correctly.

- **Description:** Manually ingest JSON files defining client-specific `PayrollRule`s (e.g., custom allowances/deductions) for the single client.

- **Acceptance Criteria:**
  - Given valid JSON for `PayrollRule`, a new record is successfully created for the `WORKSPACE`.
  - `PayrollRule.rule_definition_json` passes JSON Schema validation (from `1.2 Technical Story`).
  - `effective_from` and `effective_to` dates are correctly applied and validated.

- **Definition of Done (DoD):** All required client-specific custom rules are successfully ingested and validated. JSON Schema definition for custom rules is complete.

- **Technical Notes/Dependencies:** Requires a script or direct database insertion for JSON file ingestion. Relies on `1.1 Setup Core Schema` and `1.2 Implement JSON Schema Validation Framework`.

- **Architectural Impact:** Extends the metadata-driven rules engine with client-specific flexibility.

- **Compliance/Audit Impact:** Ensures accurate application of client-specific policies. `AUDIT_LOG` entries (via CDC) are generated for custom rule creation.

- **Effort Estimate:** Medium

- **Priority:** High

### 1.9 User Story: As a Payroll Admin, I can onboard employees, so that their master data is available for payroll processing.

- **Description:** Manually ingest JSON files containing `EMPLOYEE` master data for the single client.

- **Acceptance Criteria:**
  - Given valid JSON for `EMPLOYEE` records, new `EMPLOYEE` records are successfully created for the `WORKSPACE`.
  - `EMPLOYEE.personal_details_encrypted` passes JSON Schema validation (from `1.2 Technical Story`).
  - `employee_number` is unique within the `WORKSPACE`.
  - PII data in `personal_details_encrypted` is encrypted at rest (from `1.4 Technical Story`).

- **Definition of Done (DoD):** All initial employee data for the client is successfully ingested, validated, and encrypted.

- **Technical Notes/Dependencies:** Requires a script or direct database insertion for JSON file ingestion. Relies on `1.1 Setup Core Schema`, `1.2 Implement JSON Schema Validation Framework`, and `1.4 Implement PII Encryption for Employee Data`.

- **Architectural Impact:** Populates the core employee data for payroll processing.

- **Compliance/Audit Impact:** Ensures data privacy for PII and `AUDIT_LOG` entries (via CDC) are generated for employee creation.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 1.10 User Story: As a Payroll Admin, I can update employee data, so that changes to their information are reflected in the system.

- **Description:** Manually ingest JSON files to update existing `EMPLOYEE` records for the single client.

- **Acceptance Criteria:**
  - Given valid JSON for `EMPLOYEE` updates, existing `EMPLOYEE` records are successfully modified.
  - `EMPLOYEE.personal_details_encrypted` passes JSON Schema validation (from `1.2 Technical Story`).
  - The system confirms successful update.
  - PII data in `personal_details_encrypted` is encrypted at rest (from `1.4 Technical Story`).

- **Definition of Done (DoD):** Employee data can be successfully updated, validated, and encrypted.

- **Technical Notes/Dependencies:** Requires a script or direct database update for JSON file ingestion. Relies on `1.1 Setup Core Schema`, `1.2 Implement JSON Schema Validation Framework`, and `1.4 Implement PII Encryption for Employee Data`.

- **Architectural Impact:** Maintains the accuracy of employee data over time.

- **Compliance/Audit Impact:** Ensures data privacy for PII and `AUDIT_LOG` entries (via CDC) are generated for employee updates, including `old_value_jsonb` and `new_value_jsonb`.

- **Effort Estimate:** Medium

- **Priority:** High

## 🚀 Sprint 2: The Rules Engine & Deterministic Logic (Risk: Calculation)

**Objective:** Implement the core payroll calculation engine, ensuring it deterministically applies rules from the locked context to produce accurate and explainable payroll results. This sprint eliminates the primary risk of incorrect calculations.

### 2.1 Technical Story: Implement RulesEngine Core Scaffolding

- **Description:** Develop the core framework for interpreting and executing metadata-driven payroll rules, capable of loading and applying rules from the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - A core `RulesEngine` component exists that can load and interpret `STATUTORY_RULE.calculation_logic_jsonb`, `SALARY_DEFINITION.components_jsonb`, and `PayrollRule.rule_definition_json`.
  - The engine can resolve dependencies between components (e.g., calculate `HousingAllowance` as a percentage `of BasicSalary`).
  - The engine can apply `TAX_BAND`s for PAYE calculation based on the `rules_context_snapshot`.
  - The engine is deterministic: given the same inputs and rules context, it always produces the same output.

- **Definition of Done (DoD):** `RulesEngine` core logic implemented and unit-tested for all rule types. Test cases cover dependency resolution and tax band application.

- **Technical Notes/Dependencies:** This is the heart of the payroll system. Relies heavily on the JSON Schema definitions from Sprint 1. Will be integrated with the `PAYROLL_RUN` processing.

- **Architectural Impact:** Enables the metadata-driven calculation capabilities of the platform.

- **Compliance/Audit Impact:** Directly ensures the accuracy and consistency of payroll calculations, which is paramount for compliance.

- **Effort Estimate:** High

- **Priority:** Critical

### 2.2 User Story: As a Payroll Admin, I can initiate a payroll run for a specific period, so that the system prepares for calculation with locked rules.

- **Description:** Trigger an API call to create a new `PAYROLL_RUN` for a specific period and `WORKSPACE`, and automatically lock its rules context.

- **Acceptance Criteria:**
  - Given a `workspace_id`, `period_start`, `period_end`, and `pay_date`, a new `PAYROLL_RUN` record is created with `status: DRAFT`.
  - The `PAYROLL_RUN.rules_context_snapshot` is automatically populated with all active `STATUTORY_RULE`s, `TAX_BAND`s, `SALARY_DEFINITION`s, and `PayrollRule`s for the `pay_date` and `workspace_id`.
  - The system validates that all required rules are found for snapshotting; if not, the run fails with an appropriate error.
  - The system confirms successful run initiation.

- **Definition of Done (DoD):** API endpoint for `PAYROLL_RUN` initiation is functional. `rules_context_snapshot` is correctly populated and validated for a test run.

- **Technical Notes/Dependencies:** Requires API endpoint development. Relies on `1.1 Setup Core Schema` and the rule data ingested in Sprint 1.

- **Architectural Impact:** Implements the critical compliance locking mechanism, making payroll runs immutable from the start.

- **Compliance/Audit Impact:** Guarantees that payroll calculations use a fixed set of rules, essential for auditability and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` creation and `rules_context_snapshot` population.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.3 Technical Story: Develop State Machine for PAYROLL_RUN Lifecycle

- **Description:** Implement a state machine to enforce strict, valid transitions for `PAYROLL_RUN` records, preventing out-of-order operations.

- **Acceptance Criteria:**
  - A state machine is implemented that governs transitions: `DRAFT` → `CALCULATING` → `CALCULATED` → `APPROVED` → `LOCKED`.
  - Attempts to transition to an invalid state (e.g., `DRAFT` to `LOCKED` directly) are rejected with an error.
  - Associated business logic is triggered on state changes (e.g., `rules_context_snapshot` population on `DRAFT` creation, immutability enforcement on `LOCKED`).

- **Definition of Done (DoD):** State machine logic implemented and unit-tested. All valid and invalid state transitions are covered by tests.

- **Technical Notes/Dependencies:** Can be implemented within the `PayrollProcessingService`. Crucial for process integrity.

- **Architectural Impact:** Enforces process flow and data integrity for payroll runs.

- **Compliance/Audit Impact:** Provides a clear, auditable trail of a payroll run's progression. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.4 User Story: As a System, I can calculate an employee's gross pay, so that all salary components are correctly determined.

- **Description:** For a given employee and `PAYROLL_RUN`, the `RulesEngine` calculates all gross pay components based on the `SALARY_DEFINITION` within the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - Given an `EMPLOYEE` and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` (from `2.1 Technical Story`) successfully calculates all gross components.
  - The calculated gross components are stored in `PAYROLL_RESULT.gross_components_jsonb`.
  - Test cases cover various salary structures and component dependencies.

- **Definition of Done (DoD):** Gross pay calculation logic implemented and unit-tested. `gross_components_jsonb` is correctly populated for test employees.

- **Technical Notes/Dependencies:** This is a core function of the `PayrollProcessingService` utilizing the `RulesEngine`.

- **Architectural Impact:** Core calculation capability.

- **Compliance/Audit Impact:** Ensures accurate gross pay, a fundamental aspect of compliance.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.5 User Story: As a System, I can calculate an employee's statutory and custom deductions, so that all mandatory and client-specific deductions are correctly applied.

- **Description:** For a given employee and `PAYROLL_RUN`, the `RulesEngine` calculates all statutory (PAYE, Pension, NHF) and custom deductions based on rules within the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - Given an `EMPLOYEE`, calculated gross pay, and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` (from `2.1 Technical Story`) successfully calculates all statutory and custom deductions.
  - The calculated deductions are stored in `PAYROLL_RESULT.deductions_jsonb`.
  - Test cases cover various deduction scenarios, including PAYE tax band application.

- **Definition of Done (DoD):** Deduction calculation logic implemented and unit-tested. `deductions_jsonb` is correctly populated for test employees.

- **Technical Notes/Dependencies:** This is a core function of the `PayrollProcessingService` utilizing the `RulesEngine`. Requires the gross pay to be calculated first.

- **Architectural Impact:** Core calculation capability.

- **Compliance/Audit Impact:** Ensures compliance with tax and pension laws and accurate application of client-specific deductions. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RESULT` creation.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.6 User Story: As a System, I can generate a detailed calculation snapshot for each employee, so that every payroll result is fully explainable and auditable.

- **Description:** After gross and deductions are calculated, the system populates `PAYROLL_RESULT.calculations_snapshot_jsonb` with a detailed, immutable record of all inputs, rules (with versions), and intermediate steps used for that specific employee's calculation.

- **Acceptance Criteria:**
  - `PAYROLL_RESULT.calculations_snapshot_jsonb` contains a complete, understandable breakdown of all rules, inputs, and intermediate steps.
  - The structure of `calculations_snapshot_jsonb` conforms to its predefined JSON Schema.
  - Test cases verify the completeness and accuracy of the snapshot for various calculation scenarios.

- **Definition of Done (DoD):** `calculations_snapshot_jsonb` is correctly populated and validated for test employees. JSON Schema for `calculations_snapshot_jsonb` is complete.

- **Technical Notes/Dependencies:** This is part of the `PayrollProcessingService` and relies on the `RulesEngine`'s ability to provide detailed calculation traces.

- **Architectural Impact:** Implements the core explainability and auditability feature for individual payroll results.

- **Compliance/Audit Impact:** Provides irrefutable proof of how a payroll result was derived, crucial for audit, compliance, and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RESULT` creation.

- **Effort Estimate:** High

- **Priority:** Critical

## 🚀 Sprint 3: Lifecycle, Immutability & Approval (Risk: Process)

**Objective:** Implement the end-to-end payroll run process, enforcing immutability and providing a formal approval step. This sprint eliminates the primary risks associated with process integrity and unauthorized modifications.

### 3.1 User Story: As a Payroll Admin, I can run payroll for all employees of a client, so that the entire monthly payroll is processed efficiently.

- **Description:** Trigger an API call to initiate batch processing for a `PAYROLL_RUN` in `DRAFT` status, processing all active employees in the associated `WORKSPACE`.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `DRAFT` status, the system processes all active employees in the associated `WORKSPACE`.
  - For each employee, a `PAYROLL_RESULT` is generated (using logic from Sprint 2).
  - The `PAYROLL_RUN` status transitions from `DRAFT` to `CALCULATING` and then to `CALCULATED` (via `2.3 Technical Story: State Machine`).
  - `PAYROLL_RUN` totals (`total_gross_pay`, `total_deduction`, `total_net_pay`) are correctly aggregated and stored.
  - Errors during individual employee processing are handled gracefully (e.g., logging, skipping employee, or failing the run based on policy).

- **Definition of Done (DoD):** API endpoint for batch payroll processing is functional. A full payroll run for test data successfully transitions to `CALCULATED` status with correct aggregated totals.

- **Technical Notes/Dependencies:** Requires API endpoint development. Orchestrates the calculation logic from Sprint 2. Relies on `2.3 Technical Story: State Machine`.

- **Architectural Impact:** Implements the core batch processing capability for payroll runs.

- **Compliance/Audit Impact:** Automates a critical operational process, reducing manual errors. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates and `PAYROLL_RESULT` creation.

- **Effort Estimate:** High

- **Priority:** Critical

### 3.2 User Story: As a Payroll Reviewer, I can approve a calculated payroll run, so that it can proceed to finalization.

- **Description:** Trigger an API call to update a `PAYROLL_RUN`'s status from `CALCULATED` to `APPROVED`.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `CALCULATED` status, the Payroll Reviewer can trigger an approval action via API.
  - The `PAYROLL_RUN` status transitions to `APPROVED` (via `2.3 Technical Story: State Machine`).
  - The system validates that the user has the `PayrollReviewer` role.

- **Definition of Done (DoD):** API endpoint for payroll approval is functional. A `PAYROLL_RUN` can be successfully approved by an authorized user.

- **Technical Notes/Dependencies:** Requires API endpoint development and basic user role management (for `PayrollReviewer` role check).

- **Architectural Impact:** Introduces a formal checkpoint in the payroll lifecycle.

- **Compliance/Audit Impact:** Provides an auditable record of approval, crucial for compliance. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Low

- **Priority:** Critical

### 3.3 User Story: As a Payroll Admin, I can lock an approved payroll run, so that its results become immutable and tamper-proof.

- **Description:** Trigger an API call to update a `PAYROLL_RUN`'s status from `APPROVED` to `LOCKED`, enforcing immutability on associated `PAYROLL_RESULT`s.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `APPROVED` status, the Payroll Admin can trigger a lock action via API.
  - The `PAYROLL_RUN` status transitions to `LOCKED` (via `2.3 Technical Story: State Machine`).
  - The system validates that the user has the `PayrollAdmin` role.
  - Any subsequent attempt to `UPDATE` or `DELETE` `PAYROLL_RESULT` records associated with this `LOCKED` run is rejected by the system with an error.

- **Definition of Done (DoD):** API endpoint for payroll locking is functional. A `PAYROLL_RUN` can be successfully locked, and immutability enforcement on `PAYROLL_RESULT`s is verified through negative test cases.

- **Technical Notes/Dependencies:** Requires API endpoint development. Immutability enforcement logic needs to be implemented in the data access layer for `PAYROLL_RESULT`.

- **Architectural Impact:** Guarantees the integrity and immutability of payroll records, a cornerstone of the architecture.

- **Compliance/Audit Impact:** Provides the highest level of assurance for payroll data integrity, crucial for compliance and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Medium

- **Priority:** Critical

## 🚀 Sprint 4: Explainability & Compliance Output (Risk: Audit)

**Objective:** Enable the generation of payslips and compliance reports, and provide robust tools for audit and explanation. This sprint eliminates the primary risks associated with auditability and reporting.

### 4.1 User Story: As a Payroll Admin, I can generate payslips for a locked payroll run, so that employees receive their detailed earnings statements.

- **Description:** Retrieve all `PAYROLL_RESULT`s for a `LOCKED` `PAYROLL_RUN` and generate human-readable payslip documents (e.g., PDF).

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `LOCKED` status, the system can retrieve all associated `PAYROLL_RESULT`s.
  - For each `PAYROLL_RESULT`, a human-readable payslip document (e.g., PDF) is generated using data from `gross_components_jsonb`, `deductions_jsonb`, `net_pay`, and `calculations_snapshot_jsonb`.
  - The generated payslip accurately reflects the calculated values and breakdown.

- **Definition of Done (DoD):** Payslip generation functionality is implemented and tested. Sample payslips are generated correctly for test data.

- **Technical Notes/Dependencies:** Requires a reporting/PDF generation library. This is a read-only operation on `PAYROLL_RESULT`.

- **Architectural Impact:** Provides the final output artifact for employees.

- **Compliance/Audit Impact:** Fulfills legal and operational requirements for providing employees with pay statements.

- **Effort Estimate:** Medium

- **Priority:** High

### 4.2 User Story: As a Payroll Admin, I can extract data for LIRS and Federal compliance reports, so that I can manually file statutory obligations.

- **Description:** Aggregate required data from `PAYROLL_RESULT`s for a `LOCKED` `PAYROLL_RUN` and present it in a structured format suitable for manual filing with LIRS and Federal authorities.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `LOCKED` status, the system can aggregate required data (e.g., total PAYE, total Pension, total NHF per employee/per workspace) from `PAYROLL_RESULT`s.
  - The aggregated data is presented in a structured format (e.g., CSV, Excel) suitable for manual filing.
  - The aggregated totals match the sum of individual `PAYROLL_RESULT`s.

- **Definition of Done (DoD):** Compliance data extraction functionality is implemented and tested. Sample reports are generated correctly for test data.

- **Technical Notes/Dependencies:** This is a read-only operation on `PAYROLL_RESULT`. Requires understanding of LIRS and Federal reporting formats.

- **Architectural Impact:** Provides the necessary data for external compliance.

- **Compliance/Audit Impact:** Reduces manual data compilation effort and supports statutory reporting requirements.

- **Effort Estimate:** Medium

- **Priority:** High

### 4.3 User Story: As a Compliance Officer, I can retrieve audit logs, so that I can investigate changes and verify system actions.

- **Description:** Query the `AUDIT_LOG` (via API or direct DB access) to investigate specific changes to core entities.

- **Acceptance Criteria:**
  - Given search criteria (e.g., `entity_type`, `entity_id`, `action`, date range), the system returns relevant `AUDIT_LOG` entries.
  - Each entry includes `old_value_jsonb` and `new_value_jsonb` for data changes, allowing for a clear understanding of what changed.
  - The system validates user authorization for audit data access.

- **Definition of Done (DoD):** Audit log retrieval functionality is implemented and tested. Authorized users can query and view audit trails.

- **Technical Notes/Dependencies:** Requires API endpoint development for querying `AUDIT_LOG`. Relies on `1.3 Technical Story: Setup CDC for Audit Logging`.

- **Architectural Impact:** Provides the mechanism for forensic analysis and system verification.

- **Compliance/Audit Impact:** Enables comprehensive auditability, dispute resolution, and regulatory compliance by providing a tamper-proof record of all system activities.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 4.4 User Story: As a Compliance Officer, I can explain any payroll result, so that I can confidently address employee or regulatory inquiries.

- **Description:** Retrieve a `PAYROLL_RESULT` and analyze its `calculations_snapshot_jsonb` to understand the detailed breakdown of how the net pay was derived.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RESULT`, the `calculations_snapshot_jsonb` field contains a complete, understandable breakdown of all rules, inputs, and intermediate steps.
  - The Compliance Officer can use this information to articulate *how* the net pay was derived without needing to re-run calculations.
  - The system validates user authorization for payroll data access.

- **Definition of Done (DoD):** Documentation and/or a simple viewer (e.g., API response) for `calculations_snapshot_jsonb` is available and tested for clarity.

- **Technical Notes/Dependencies:** This is primarily a read-only operation on `PAYROLL_RESULT`. The clarity depends on the structure and content of `calculations_snapshot_jsonb` (from `2.6 User Story`).

- **Architectural Impact:** Implements the core explainability feature of the architecture.

- **Compliance/Audit Impact:** Provides full transparency and defensibility for every payroll calculation, building trust and simplifying dispute resolution.

- **Effort Estimate:** Low

- **Priority:** Critical

## 5.0 Gap Analysis: Prompt vs. Final Sprint-Ready Backlog

This section provides a clear analysis of how the final Sprint-Ready Backlog aligns with the provided prompt, highlighting additional considerations and deferred items. This ensures transparency and a shared understanding of the MVP scope.

### 5.1 Alignment (What I've Considered that is Specified)

All requirements explicitly stated in your prompt for Phase 1 have been addressed and translated into sprint-ready stories or technical enablers. This includes:

- **Single Client, Salaried Employees, Monthly Payroll, Nigerian Compliance:** The entire backlog is scoped to this initial context.

- **Manual JSON File Ingestion:** Explicit user stories and technical notes detail how JSON files will be used for initial data setup and updates.

- **No UI for Initial MVP:** The stories focus on API interactions and backend processes, with UI deferred.

- **Setup First Account and Workspace:** Covered by `1.5 User Story: As a Payroll Admin, I can provision a new client workspace`.

- **Parsing JSON to Correct Tables:** Covered by various user stories for defining rules and onboarding employees, supported by `1.2 Technical Story: Implement JSON Schema Validation Framework`.

- **Core Payroll Processing:** Covered extensively in Sprint 2 and 3, including calculation, approval, and locking.

- **Auditability:** Addressed by `1.3 Technical Story: Setup CDC for Audit Logging` and `4.3 User Story: As a Compliance Officer, I can retrieve audit logs`.

- **Immutability:** Enforced by `3.3 User Story: As a Payroll Admin, I can lock an approved payroll run`.

- **Metadata-Driven Rules:** Central to the design and implemented through various rule definition stories.

### 5.2 Additional Considerations (What I've Considered that was Not Explicitly Specified in this Prompt)

These are items I included in the architecture and translated into technical stories to enhance robustness, security, and future-proofing, based on best practices for financial systems and our previous architectural discussions. These were highlighted in previous gap analyses and remain crucial additions:

- **`rules_context_snapshot`**** in ****`PAYROLL_RUN`**: This critical architectural decision for compliance locking is explicitly reflected in `2.2 User Story: As a Payroll Admin, I can initiate a payroll run...` It ensures that rules are locked at the start of a run, preventing mid-month changes from affecting in-progress calculations.

- **JSON Schema Validation Framework**: This was a key mitigation strategy for the "JSON Chaos" risk. It's included as `1.2 Technical Story` to ensure all JSONB data conforms to predefined schemas, maintaining data integrity and agentic-readiness.

- **PII Encryption for Employee Data**: The `EMPLOYEE.personal_details_encrypted` field is explicitly designed for encryption at rest, addressing a crucial security and compliance requirement for sensitive PII. This is covered by `1.4 Technical Story`.

- **EventStore Append-Only Mechanism**: While the prompt mentioned audit logging, the explicit implementation of an append-only `EventStore` as a technical enabler (`Technical Story: Implement EventStore Append-Only Mechanism` - *Note: This was a technical enabler in the User Story Map, but not explicitly broken out as a separate sprint story in this backlog for brevity, as its setup is largely covered by **`1.1 Setup Core Schema`** and its usage by **`2.6 Generate detailed calculation snapshot`*). It ensures a robust, immutable historical record for future AI and deep audit, going beyond basic audit logs.

- **State Machine for ****`PAYROLL_RUN`**** Lifecycle**: This ensures strict process integrity and prevents out-of-order operations, which is vital for a financial system. This is covered by `2.3 Technical Story`.

### 5.3 Deferred Items (What You Specified that is Not in Phase 1)

All items explicitly marked as `Do NOT Include` in your prompt have been strictly adhered to and are implicitly deferred to later phases. No items from the `Must include` section of the prompt have been deferred; all are covered in Phase 1.

This comprehensive Sprint-Ready Backlog provides a detailed, actionable plan for Phase 1, ensuring that every piece of work contributes to a secure, compliant, and AI-ready payroll platform, while explicitly addressing the specific constraints and requirements you've outlined.

## 🚀 Sprint 2: The Rules Engine & Deterministic Logic (Risk: Calculation)

**Objective:** Implement the core payroll calculation engine, ensuring it deterministically applies rules from the locked context to produce accurate and explainable payroll results. This sprint eliminates the primary risk of incorrect calculations.

### 2.1 Technical Story: Implement RulesEngine Core Scaffolding

- **Description:** Develop the core framework for interpreting and executing metadata-driven payroll rules, capable of loading and applying rules from the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - A core `RulesEngine` component exists that can load and interpret `STATUTORY_RULE.calculation_logic_jsonb`, `SALARY_DEFINITION.components_jsonb`, and `PayrollRule.rule_definition_json`.
  - The engine can resolve dependencies between components (e.g., calculate `HousingAllowance` as a percentage `of BasicSalary`).
  - The engine can apply `TAX_BAND`s for PAYE calculation based on the `rules_context_snapshot`.
  - The engine is deterministic: given the same inputs and rules context, it always produces the same output.

- **Definition of Done (DoD):** `RulesEngine` core logic implemented and unit-tested for all rule types. Test cases cover dependency resolution and tax band application.

- **Technical Notes/Dependencies:** This is the heart of the payroll system. Relies heavily on the JSON Schema definitions from Sprint 1. Will be integrated with the `PAYROLL_RUN` processing.

- **Architectural Impact:** Enables the metadata-driven calculation capabilities of the platform.

- **Compliance/Audit Impact:** Directly ensures the accuracy and consistency of payroll calculations, which is paramount for compliance.

- **Effort Estimate:** High

- **Priority:** Critical

### 2.2 User Story: As a Payroll Admin, I can initiate a payroll run for a specific period, so that the system prepares for calculation with locked rules.

- **Description:** Trigger an API call to create a new `PAYROLL_RUN` for a specific period and `WORKSPACE`, and automatically lock its rules context.

- **Acceptance Criteria:**
  - Given a `workspace_id`, `period_start`, `period_end`, and `pay_date`, a new `PAYROLL_RUN` record is created with `status: DRAFT`.
  - The `PAYROLL_RUN.rules_context_snapshot` is automatically populated with all active `STATUTORY_RULE`s, `TAX_BAND`s, `SALARY_DEFINITION`s, and `PayrollRule`s for the `pay_date` and `workspace_id`.
  - The system validates that all required rules are found for snapshotting; if not, the run fails with an appropriate error.
  - The system confirms successful run initiation.

- **Definition of Done (DoD):** API endpoint for `PAYROLL_RUN` initiation is functional. `rules_context_snapshot` is correctly populated and validated for a test run.

- **Technical Notes/Dependencies:** Requires API endpoint development. Relies on `1.1 Setup Core Schema` and the rule data ingested in Sprint 1.

- **Architectural Impact:** Implements the critical compliance locking mechanism, making payroll runs immutable from the start.

- **Compliance/Audit Impact:** Guarantees that payroll calculations use a fixed set of rules, essential for auditability and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` creation and `rules_context_snapshot` population.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.3 Technical Story: Develop State Machine for PAYROLL_RUN Lifecycle

- **Description:** Implement a state machine to enforce strict, valid transitions for `PAYROLL_RUN` records, preventing out-of-order operations.

- **Acceptance Criteria:**
  - A state machine is implemented that governs transitions: `DRAFT` → `CALCULATING` → `CALCULATED` → `APPROVED` → `LOCKED`.
  - Attempts to transition to an invalid state (e.g., `DRAFT` to `LOCKED` directly) are rejected with an error.
  - Associated business logic is triggered on state changes (e.g., `rules_context_snapshot` population on `DRAFT` creation, immutability enforcement on `LOCKED`).

- **Definition of Done (DoD):** State machine logic implemented and unit-tested. All valid and invalid state transitions are covered by tests.

- **Technical Notes/Dependencies:** Can be implemented within the `PayrollProcessingService`. Crucial for process integrity.

- **Architectural Impact:** Enforces process flow and data integrity for payroll runs.

- **Compliance/Audit Impact:** Provides a clear, auditable trail of a payroll run's progression. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.4 User Story: As a System, I can calculate an employee's gross pay, so that all salary components are correctly determined.

- **Description:** For a given employee and `PAYROLL_RUN`, the `RulesEngine` calculates all gross pay components based on the `SALARY_DEFINITION` within the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - Given an `EMPLOYEE` and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` (from `2.1 Technical Story`) successfully calculates all gross components.
  - The calculated gross components are stored in `PAYROLL_RESULT.gross_components_jsonb`.
  - Test cases cover various salary structures and component dependencies.

- **Definition of Done (DoD):** Gross pay calculation logic implemented and unit-tested. `gross_components_jsonb` is correctly populated for test employees.

- **Technical Notes/Dependencies:** This is a core function of the `PayrollProcessingService` utilizing the `RulesEngine`.

- **Architectural Impact:** Core calculation capability.

- **Compliance/Audit Impact:** Ensures accurate gross pay, a fundamental aspect of compliance.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.5 User Story: As a System, I can calculate an employee's statutory and custom deductions, so that all mandatory and client-specific deductions are correctly applied.

- **Description:** For a given employee and `PAYROLL_RUN`, the `RulesEngine` calculates all statutory (PAYE, Pension, NHF) and custom deductions based on rules within the `rules_context_snapshot`.

- **Acceptance Criteria:**
  - Given an `EMPLOYEE`, calculated gross pay, and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` (from `2.1 Technical Story`) successfully calculates all statutory and custom deductions.
  - The calculated deductions are stored in `PAYROLL_RESULT.deductions_jsonb`.
  - Test cases cover various deduction scenarios, including PAYE tax band application.

- **Definition of Done (DoD):** Deduction calculation logic implemented and unit-tested. `deductions_jsonb` is correctly populated for test employees.

- **Technical Notes/Dependencies:** This is a core function of the `PayrollProcessingService` utilizing the `RulesEngine`. Requires the gross pay to be calculated first.

- **Architectural Impact:** Core calculation capability.

- **Compliance/Audit Impact:** Ensures compliance with tax and pension laws and accurate application of client-specific deductions. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RESULT` creation.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 2.6 User Story: As a System, I can generate a detailed calculation snapshot for each employee, so that every payroll result is fully explainable and auditable.

- **Description:** After gross and deductions are calculated, the system populates `PAYROLL_RESULT.calculations_snapshot_jsonb` with a detailed, immutable record of all inputs, rules (with versions), and intermediate steps used for that specific employee's calculation.

- **Acceptance Criteria:**
  - `PAYROLL_RESULT.calculations_snapshot_jsonb` contains a complete, understandable breakdown of all rules, inputs, and intermediate steps.
  - The structure of `calculations_snapshot_jsonb` conforms to its predefined JSON Schema.
  - Test cases verify the completeness and accuracy of the snapshot for various calculation scenarios.

- **Definition of Done (DoD):** `calculations_snapshot_jsonb` is correctly populated and validated for test employees. JSON Schema for `calculations_snapshot_jsonb` is complete.

- **Technical Notes/Dependencies:** This is part of the `PayrollProcessingService` and relies on the `RulesEngine`'s ability to provide detailed calculation traces.

- **Architectural Impact:** Implements the core explainability and auditability feature for individual payroll results.

- **Compliance/Audit Impact:** Provides irrefutable proof of how a payroll result was derived, crucial for audit, compliance, and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RESULT` creation.

- **Effort Estimate:** High

- **Priority:** Critical

## 🚀 Sprint 3: Lifecycle, Immutability & Approval (Risk: Process)

**Objective:** Implement the end-to-end payroll run process, enforcing immutability and providing a formal approval step. This sprint eliminates the primary risks associated with process integrity and unauthorized modifications.

### 3.1 User Story: As a Payroll Admin, I can run payroll for all employees of a client, so that the entire monthly payroll is processed efficiently.

- **Description:** Trigger an API call to initiate batch processing for a `PAYROLL_RUN` in `DRAFT` status, processing all active employees in the associated `WORKSPACE`.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `DRAFT` status, the system processes all active employees in the associated `WORKSPACE`.
  - For each employee, a `PAYROLL_RESULT` is generated (using logic from Sprint 2).
  - The `PAYROLL_RUN` status transitions from `DRAFT` to `CALCULATING` and then to `CALCULATED` (via `2.3 Technical Story: State Machine`).
  - `PAYROLL_RUN` totals (`total_gross_pay`, `total_deduction`, `total_net_pay`) are correctly aggregated and stored.
  - Errors during individual employee processing are handled gracefully (e.g., logging, skipping employee, or failing the run based on policy).

- **Definition of Done (DoD):** API endpoint for batch payroll processing is functional. A full payroll run for test data successfully transitions to `CALCULATED` status with correct aggregated totals.

- **Technical Notes/Dependencies:** Requires API endpoint development. Orchestrates the calculation logic from Sprint 2. Relies on `2.3 Technical Story: State Machine`.

- **Architectural Impact:** Implements the core batch processing capability for payroll runs.

- **Compliance/Audit Impact:** Automates a critical operational process, reducing manual errors. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates and `PAYROLL_RESULT` creation.

- **Effort Estimate:** High

- **Priority:** Critical

### 3.2 User Story: As a Payroll Reviewer, I can approve a calculated payroll run, so that it can proceed to finalization.

- **Description:** Trigger an API call to update a `PAYROLL_RUN`'s status from `CALCULATED` to `APPROVED`.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `CALCULATED` status, the Payroll Reviewer can trigger an approval action via API.
  - The `PAYROLL_RUN` status transitions to `APPROVED` (via `2.3 Technical Story: State Machine`).
  - The system validates that the user has the `PayrollReviewer` role.

- **Definition of Done (DoD):** API endpoint for payroll approval is functional. A `PAYROLL_RUN` can be successfully approved by an authorized user.

- **Technical Notes/Dependencies:** Requires API endpoint development and basic user role management (for `PayrollReviewer` role check).

- **Architectural Impact:** Introduces a formal checkpoint in the payroll lifecycle.

- **Compliance/Audit Impact:** Provides an auditable record of approval, crucial for compliance. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Low

- **Priority:** Critical

### 3.3 User Story: As a Payroll Admin, I can lock an approved payroll run, so that its results become immutable and tamper-proof.

- **Description:** Trigger an API call to update a `PAYROLL_RUN`'s status from `APPROVED` to `LOCKED`, enforcing immutability on associated `PAYROLL_RESULT`s.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `APPROVED` status, the Payroll Admin can trigger a lock action via API.
  - The `PAYROLL_RUN` status transitions to `LOCKED` (via `2.3 Technical Story: State Machine`).
  - The system validates that the user has the `PayrollAdmin` role.
  - Any subsequent attempt to `UPDATE` or `DELETE` `PAYROLL_RESULT` records associated with this `LOCKED` run is rejected by the system with an error.

- **Definition of Done (DoD):** API endpoint for payroll locking is functional. A `PAYROLL_RUN` can be successfully locked, and immutability enforcement on `PAYROLL_RESULT`s is verified through negative test cases.

- **Technical Notes/Dependencies:** Requires API endpoint development. Immutability enforcement logic needs to be implemented in the data access layer for `PAYROLL_RESULT`.

- **Architectural Impact:** Guarantees the integrity and immutability of payroll records, a cornerstone of the architecture.

- **Compliance/Audit Impact:** Provides the highest level of assurance for payroll data integrity, crucial for compliance and dispute resolution. `AUDIT_LOG` entries (via CDC) are generated for `PAYROLL_RUN` status updates.

- **Effort Estimate:** Medium

- **Priority:** Critical

## 🚀 Sprint 4: Explainability & Compliance Output (Risk: Audit)

**Objective:** Enable the generation of payslips and compliance reports, and provide robust tools for audit and explanation. This sprint eliminates the primary risks associated with auditability and reporting.

### 4.1 User Story: As a Payroll Admin, I can generate payslips for a locked payroll run, so that employees receive their detailed earnings statements.

- **Description:** Retrieve all `PAYROLL_RESULT`s for a `LOCKED` `PAYROLL_RUN` and generate human-readable payslip documents (e.g., PDF).

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `LOCKED` status, the system can retrieve all associated `PAYROLL_RESULT`s.
  - For each `PAYROLL_RESULT`, a human-readable payslip document (e.g., PDF) is generated using data from `gross_components_jsonb`, `deductions_jsonb`, `net_pay`, and `calculations_snapshot_jsonb`.
  - The generated payslip accurately reflects the calculated values and breakdown.

- **Definition of Done (DoD):** Payslip generation functionality is implemented and tested. Sample payslips are generated correctly for test data.

- **Technical Notes/Dependencies:** Requires a reporting/PDF generation library. This is a read-only operation on `PAYROLL_RESULT`.

- **Architectural Impact:** Provides the final output artifact for employees.

- **Compliance/Audit Impact:** Fulfills legal and operational requirements for providing employees with pay statements.

- **Effort Estimate:** Medium

- **Priority:** High

### 4.2 User Story: As a Payroll Admin, I can extract data for LIRS and Federal compliance reports, so that I can manually file statutory obligations.

- **Description:** Aggregate required data from `PAYROLL_RESULT`s for a `LOCKED` `PAYROLL_RUN` and present it in a structured format suitable for manual filing with LIRS and Federal authorities.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RUN` in `LOCKED` status, the system can aggregate required data (e.g., total PAYE, total Pension, total NHF per employee/per workspace) from `PAYROLL_RESULT`s.
  - The aggregated data is presented in a structured format (e.g., CSV, Excel) suitable for manual filing.
  - The aggregated totals match the sum of individual `PAYROLL_RESULT`s.

- **Definition of Done (DoD):** Compliance data extraction functionality is implemented and tested. Sample reports are generated correctly for test data.

- **Technical Notes/Dependencies:** This is a read-only operation on `PAYROLL_RESULT`. Requires understanding of LIRS and Federal reporting formats.

- **Architectural Impact:** Provides the necessary data for external compliance.

- **Compliance/Audit Impact:** Reduces manual data compilation effort and supports statutory reporting requirements.

- **Effort Estimate:** Medium

- **Priority:** High

### 4.3 User Story: As a Compliance Officer, I can retrieve audit logs, so that I can investigate changes and verify system actions.

- **Description:** Query the `AUDIT_LOG` (via API or direct DB access) to investigate specific changes to core entities.

- **Acceptance Criteria:**
  - Given search criteria (e.g., `entity_type`, `entity_id`, `action`, date range), the system returns relevant `AUDIT_LOG` entries.
  - Each entry includes `old_value_jsonb` and `new_value_jsonb` for data changes, allowing for a clear understanding of what changed.
  - The system validates user authorization for audit data access.

- **Definition of Done (DoD):** Audit log retrieval functionality is implemented and tested. Authorized users can query and view audit trails.

- **Technical Notes/Dependencies:** Requires API endpoint development for querying `AUDIT_LOG`. Relies on `1.3 Technical Story: Setup CDC for Audit Logging`.

- **Architectural Impact:** Provides the mechanism for forensic analysis and system verification.

- **Compliance/Audit Impact:** Enables comprehensive auditability, dispute resolution, and regulatory compliance by providing a tamper-proof record of all system activities.

- **Effort Estimate:** Medium

- **Priority:** Critical

### 4.4 User Story: As a Compliance Officer, I can explain any payroll result, so that I can confidently address employee or regulatory inquiries.

- **Description:** Retrieve a `PAYROLL_RESULT` and analyze its `calculations_snapshot_jsonb` to understand the detailed breakdown of how the net pay was derived.

- **Acceptance Criteria:**
  - Given a `PAYROLL_RESULT`, the `calculations_snapshot_jsonb` field contains a complete, understandable breakdown of all rules, inputs, and intermediate steps.
  - The Compliance Officer can use this information to articulate *how* the net pay was derived without needing to re-run calculations.
  - The system validates user authorization for payroll data access.

- **Definition of Done (DoD):** Documentation and/or a simple viewer (e.g., API response) for `calculations_snapshot_jsonb` is available and tested for clarity.

- **Technical Notes/Dependencies:** This is primarily a read-only operation on `PAYROLL_RESULT`. The clarity depends on the structure and content of `calculations_snapshot_jsonb` (from `2.6 User Story`).

- **Architectural Impact:** Implements the core explainability feature of the architecture.

- **Compliance/Audit Impact:** Provides full transparency and defensibility for every payroll calculation, building trust and simplifying dispute resolution.

- **Effort Estimate:** Low

- **Priority:** Critical

## 5.0 Gap Analysis: Prompt vs. Final Sprint-Ready Backlog

This section provides a clear analysis of how the final Sprint-Ready Backlog aligns with the provided prompt, highlighting additional considerations and deferred items. This ensures transparency and a shared understanding of the MVP scope.

### 5.1 Alignment (What I've Considered that is Specified)

All requirements explicitly stated in your prompt for Phase 1 have been addressed and translated into sprint-ready stories or technical enablers. This includes:

- **Single Client, Salaried Employees, Monthly Payroll, Nigerian Compliance:** The entire backlog is scoped to this initial context.

- **Manual JSON File Ingestion:** Explicit user stories and technical notes detail how JSON files will be used for initial data setup and updates.

- **No UI for Initial MVP:** The stories focus on API interactions and backend processes, with UI deferred.

- **Setup First Account and Workspace:** Covered by `1.5 User Story: As a Payroll Admin, I can provision a new client workspace`.

- **Parsing JSON to Correct Tables:** Covered by various user stories for defining rules and onboarding employees, supported by `1.2 Technical Story: Implement JSON Schema Validation Framework`.

- **Core Payroll Processing:** Covered extensively in Sprint 2 and 3, including calculation, approval, and locking.

- **Auditability:** Addressed by `1.3 Technical Story: Setup CDC for Audit Logging` and `4.3 User Story: As a Compliance Officer, I can retrieve audit logs`.

- **Immutability:** Enforced by `3.3 User Story: As a Payroll Admin, I can lock an approved payroll run`.

- **Metadata-Driven Rules:** Central to the design and implemented through various rule definition stories.

### 5.2 Additional Considerations (What I've Considered that was Not Explicitly Specified in this Prompt)

These are items I included in the architecture and translated into technical stories to enhance robustness, security, and future-proofing, based on best practices for financial systems and our previous architectural discussions. These were highlighted in previous gap analyses and remain crucial additions:

- **`rules_context_snapshot`**** in ****`PAYROLL_RUN`**: This critical architectural decision for compliance locking is explicitly reflected in `2.2 User Story: As a Payroll Admin, I can initiate a payroll run...` It ensures that rules are locked at the start of a run, preventing mid-month changes from affecting in-progress calculations.

- **JSON Schema Validation Framework**: This was a key mitigation strategy for the "JSON Chaos" risk. It's included as `1.2 Technical Story` to ensure all JSONB data conforms to predefined schemas, maintaining data integrity and agentic-readiness.

- **PII Encryption for Employee Data**: The `EMPLOYEE.personal_details_encrypted` field is explicitly designed for encryption at rest, addressing a crucial security and compliance requirement for sensitive PII. This is covered by `1.4 Technical Story`.

- **EventStore Append-Only Mechanism**: While the prompt mentioned audit logging, the explicit implementation of an append-only `EventStore` as a technical enabler (`Technical Story: Implement EventStore Append-Only Mechanism` - *Note: This was a technical enabler in the User Story Map, but not explicitly broken out as a separate sprint story in this backlog for brevity, as its setup is largely covered by **`1.1 Setup Core Schema`** and its usage by **`2.6 Generate detailed calculation snapshot`*). It ensures a robust, immutable historical record for future AI and deep audit, going beyond basic audit logs.

- **State Machine for ****`PAYROLL_RUN`**** Lifecycle**: This ensures strict process integrity and prevents out-of-order operations, which is vital for a financial system. This is covered by `2.3 Technical Story`.

### 5.3 Deferred Items (What You Specified that is Not in Phase 1)

All items explicitly marked as `Do NOT Include` in your prompt have been strictly adhered to and are implicitly deferred to later phases. No items from the `Must include` section of the prompt have been deferred; all are covered in Phase 1.

This comprehensive Sprint-Ready Backlog provides a detailed, actionable plan for Phase 1, ensuring that every piece of work contributes to a secure, compliant, and AI-ready payroll platform, while explicitly addressing the specific constraints and requirements you've outlined.

