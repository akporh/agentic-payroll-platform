# Phase 1 User Story Map: Trust Foundation MVP

**Author:** Manus AI (Senior Product Manager & Agile Delivery Lead)

## 🎯 Context

Phase 1 of the payroll bureau platform is focused on establishing a **Trust Foundation MVP**. It is designed to be agentic-ready but operationally manual, with a deterministic calculation engine, full audit logging, and manual compliance reporting. There is no autonomous decision-making or Maker-Critic runtime logic in this phase.

## 🧱 Objective

To create a user story map that aligns with the Phase 1 Outcome-Based Roadmap, eliminates payroll risk in the correct order, enables one complete end-to-end payroll cycle, and reflects architectural constraints (state transitions, immutability, audit-first). This document bridges Roadmap Milestones → Workflows → Stories → Build Sequencing.

## 1️⃣ Actors

This section identifies the key actors involved in Phase 1, detailing their goals, associated risks, and definitions of success.

### Actor: Payroll Admin
*   **Goals:**
    *   Accurately process monthly payroll for the single client.
    *   Ensure all employees are paid correctly and on time.
    *   Manage employee data and payroll configurations.
    *   Generate data for compliance reports.
*   **Risks:**
    *   **Calculation Risk:** Errors in input data or rule application leading to incorrect net pay.
    *   **Operational Risk:** Time-consuming manual processes, potential for human error during data entry or payroll run initiation.
    *   **Compliance Risk:** Incorrect application of statutory rules leading to penalties.
*   **Definition of Success:** A full monthly payroll cycle is completed without manual calculation, all employees receive correct net pay, and compliance data is readily available.

### Actor: Payroll Reviewer
*   **Goals:**
    *   Verify the accuracy of payroll calculations before finalization.
    *   Ensure compliance with statutory and client-specific rules.
    *   Approve payroll runs for payment and locking.
*   **Risks:**
    *   **Calculation Risk:** Missing errors in calculations that lead to incorrect payments.
    *   **Compliance Risk:** Approving a payroll run that violates statutory regulations.
    *   **Audit & Trust Risk:** Inability to trace or explain how a payroll result was derived.
*   **Definition of Success:** All payroll calculations are verified as accurate, all statutory and client rules are correctly applied, and the payroll run is confidently approved for finalization.

### Actor: Bureau Owner
*   **Goals:**
    *   Ensure the payroll bureau operates efficiently and profitably.
    *   Maintain client satisfaction and trust.
    *   Ensure compliance with all regulatory requirements.
    *   Reduce operational overhead and risk.
*   **Risks:**
    *   **Reputational Risk:** Errors in payroll processing leading to client dissatisfaction or regulatory penalties.
    *   **Financial Risk:** Penalties from non-compliance, loss of clients due to poor service.
    *   **Future Scalability Risk:** Investing in a system that cannot grow with the business.
*   **Definition of Success:** The payroll platform reliably processes payroll, maintains high accuracy, ensures compliance, and provides a foundation for future growth and client acquisition.

### Actor: Compliance Officer
*   **Goals:**
    *   Ensure all payroll processes and outputs adhere to Nigerian tax laws (LIRS, Federal) and pension regulations.
    *   Verify the integrity and immutability of audit trails.
    *   Facilitate regulatory audits and dispute resolution.
*   **Risks:**
    *   **Compliance Risk:** Unidentified breaches of statutory regulations, leading to fines or legal action.
    *   **Audit & Trust Risk:** Inability to produce verifiable audit trails or explain payroll calculations to regulators.
*   **Definition of Success:** The system provides irrefutable evidence of compliance for all payroll activities, and all audit logs are complete, accurate, and tamper-proof.

### Actor: System (Deterministic Engine, Not AI)
*   **Goals:**
    *   Execute payroll calculations accurately and deterministically based on configured rules.
    *   Maintain data integrity and enforce state transitions.
    *   Record all auditable events and process steps.
    *   Provide data for reporting and audit.
*   **Risks:**
    *   **Calculation Risk:** Bugs in the `RulesEngine` leading to incorrect outputs.
    *   **Data Integrity Risk:** Failure to enforce immutability or correctly store data.
    *   **Operational Risk:** Performance bottlenecks during payroll processing.
*   **Definition of Success:** All payroll calculations are performed correctly according to the active rules, data integrity is maintained, and all auditable actions are logged without failure.

## 2️⃣ Backbone (User Journey)

This section outlines the core user journey for completing a full payroll cycle in Phase 1, reflecting the operational workflow.

### Configure Client
*   **Description:** The process of setting up the initial client account and workspace within the system.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** None (initial setup).

### Configure Salary Components
*   **Description:** Defining the client-specific salary structures and custom payroll rules.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** Client configured.

### Onboard Employee
*   **Description:** Adding and managing employee master data for the configured client.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** Client configured.

### Prepare Payroll Period
*   **Description:** Initiating a new payroll run for a specific period and locking in the relevant rules.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** Employees onboarded, salary components configured.

### Run Payroll Calculation
*   **Description:** Executing the payroll engine to calculate gross pay, deductions, and net pay for all employees in the prepared payroll period.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** Payroll period prepared.

### Review Payroll Results
*   **Description:** Examining the calculated payroll results for accuracy and consistency.
*   **Actors:** Payroll Admin, Payroll Reviewer
*   **Dependencies:** Payroll calculation completed.

### Approve Payroll
*   **Description:** Formal approval of the payroll run, signifying readiness for finalization.
*   **Actors:** Payroll Reviewer
*   **Dependencies:** Payroll results reviewed.

### Lock Payroll
*   **Description:** Finalizing the payroll run, making all associated results immutable.
*   **Actors:** Payroll Admin, System
*   **Dependencies:** Payroll approved.

### Generate Compliance Data
*   **Description:** Extracting aggregated data necessary for statutory compliance reports.
*   **Actors:** Payroll Admin, Compliance Officer, System
*   **Dependencies:** Payroll locked.

### Retrieve Audit Logs
*   **Description:** Accessing the immutable audit trail to investigate changes or verify actions.
*   **Actors:** Payroll Admin, Compliance Officer, Bureau Owner, System
*   **Dependencies:** Any auditable action has occurred.

## 3️⃣ Task Breakdown Per Backbone

This section details the chronological and operational tasks within each backbone activity, including system validations, state changes, error states, and lock enforcement.

### Backbone: Configure Client
*   **Task 1.1: Provision Account**
    *   **Description:** Manually create the top-level `Account` for the payroll bureau.
    *   **Actor:** Payroll Admin
    *   **System Validations:** `Account` ID uniqueness.
    *   **State Changes:** New `Account` record created.
    *   **Error States:** Duplicate `Account` ID.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `Account` creation (via CDC).
*   **Task 1.2: Provision Workspace**
    *   **Description:** Manually create the `WORKSPACE` for the single client, linking it to the `Account`.
    *   **Actor:** Payroll Admin
    *   **System Validations:** `WORKSPACE` ID uniqueness, valid `account_id` reference.
    *   **State Changes:** New `WORKSPACE` record created.
    *   **Error States:** Duplicate `WORKSPACE` ID, invalid `account_id`.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `WORKSPACE` creation (via CDC).

### Backbone: Configure Salary Components
*   **Task 2.1: Define Statutory Rules**
    *   **Description:** Manually ingest JSON files defining `STATUTORY_RULE`s (PAYE, Pension, NHF) and associated `TAX_BAND`s.
    *   **Actor:** Payroll Admin
    *   **System Validations:** JSON Schema validation for `STATUTORY_RULE.calculation_logic_jsonb`, `TAX_BAND` consistency (non-overlapping, contiguous), `effective_from`/`effective_to` logic.
    *   **State Changes:** New `STATUTORY_RULE` and `TAX_BAND` records created.
    *   **Error States:** Invalid JSON, schema validation failure, date conflicts.
    *   **Audit Logs Generated:** `AUDIT_LOG` entries for `STATUTORY_RULE` and `TAX_BAND` creation (via CDC).
*   **Task 2.2: Define Client Salary Structure**
    *   **Description:** Manually ingest JSON files defining the client-specific `SALARY_DEFINITION`.
    *   **Actor:** Payroll Admin
    *   **System Validations:** JSON Schema validation for `SALARY_DEFINITION.components_jsonb`, component dependency validation (no circular refs, valid `of` references), `effective_from`/`effective_to` logic.
    *   **State Changes:** New `SALARY_DEFINITION` record created.
    *   **Error States:** Invalid JSON, schema validation failure, dependency errors.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `SALARY_DEFINITION` creation (via CDC).
*   **Task 2.3: Define Custom Payroll Rules**
    *   **Description:** Manually ingest JSON files defining client-specific `PayrollRule`s (e.g., custom allowances/deductions).
    *   **Actor:** Payroll Admin
    *   **System Validations:** JSON Schema validation for `PayrollRule.rule_definition_json`, `effective_from`/`effective_to` logic.
    *   **State Changes:** New `PayrollRule` record created.
    *   **Error States:** Invalid JSON, schema validation failure.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PayrollRule` creation (via CDC).

### Backbone: Onboard Employee
*   **Task 3.1: Ingest Employee Data**
    *   **Description:** Manually ingest JSON files containing `EMPLOYEE` master data.
    *   **Actor:** Payroll Admin
    *   **System Validations:** JSON Schema validation for `EMPLOYEE.personal_details_encrypted`, uniqueness of `employee_number` within `WORKSPACE`, valid `workspace_id` reference.
    *   **State Changes:** New `EMPLOYEE` records created.
    *   **Error States:** Invalid JSON, schema validation failure, duplicate `employee_number`, invalid `workspace_id`.
    *   **Audit Logs Generated:** `AUDIT_LOG` entries for `EMPLOYEE` creation (via CDC).
*   **Task 3.2: Update Employee Data**
    *   **Description:** Manually ingest JSON files to update existing `EMPLOYEE` records.
    *   **Actor:** Payroll Admin
    *   **System Validations:** JSON Schema validation for `EMPLOYEE.personal_details_encrypted`, `employee_id` existence, valid `workspace_id` reference.
    *   **State Changes:** Existing `EMPLOYEE` records updated.
    *   **Error States:** Invalid JSON, schema validation failure, `employee_id` not found.
    *   **Audit Logs Generated:** `AUDIT_LOG` entries for `EMPLOYEE` updates (via CDC).

### Backbone: Prepare Payroll Period
*   **Task 4.1: Initiate Payroll Run**
    *   **Description:** Payroll Admin triggers an API call to create a new `PAYROLL_RUN` for a specific period and `WORKSPACE`.
    *   **Actor:** Payroll Admin
    *   **System Validations:** Valid `workspace_id`, `period_start`, `period_end`, `pay_date`. `period_start` and `period_end` must define a valid monthly period. `pay_date` must be after `period_end`.
    *   **State Changes:** New `PAYROLL_RUN` record created with `status: DRAFT`.
    *   **Error States:** Invalid period dates, `workspace_id` not found.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` creation (via CDC).
*   **Task 4.2: Lock Rules Context**
    *   **Description:** System automatically populates `PAYROLL_RUN.rules_context_snapshot` with active rules for the `pay_date`.
    *   **Actor:** System
    *   **System Validations:** All required `STATUTORY_RULE`s, `TAX_BAND`s, `SALARY_DEFINITION`s, and `PayrollRule`s must be found for the given `pay_date` and `workspace_id`.
    *   **State Changes:** `PAYROLL_RUN.rules_context_snapshot` field populated.
    *   **Error States:** Missing active rules for the period, leading to `PAYROLL_RUN` status `FAILED`.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` update (via CDC).

### Backbone: Run Payroll Calculation
*   **Task 5.1: Process All Employees**
    *   **Description:** System iterates through all active employees in the `WORKSPACE` for the `PAYROLL_RUN`.
    *   **Actor:** System
    *   **System Validations:** `PAYROLL_RUN` status is `DRAFT` or `CALCULATING`.
    *   **State Changes:** `PAYROLL_RUN` status transitions to `CALCULATING`.
    *   **Error States:** `PAYROLL_RUN` not in valid state.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` status update (via CDC).
*   **Task 5.2: Calculate Employee Pay**
    *   **Description:** For each employee, the `RulesEngine` calculates gross pay, deductions, and net pay using the `rules_context_snapshot`.
    *   **Actor:** System
    *   **System Validations:** All inputs (employee data, rules from snapshot) are valid. Calculation logic executes without errors.
    *   **State Changes:** New `PAYROLL_RESULT` record created for the employee.
    *   **Error States:** Calculation error (e.g., division by zero, missing data), leading to `PAYROLL_RESULT` marked as `FAILED` (if such a status is introduced) or `PAYROLL_RUN` marked as `FAILED`.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RESULT` creation (via CDC). `EventStore` entry for `EmployeeProcessed`.
*   **Task 5.3: Finalize Run Calculation**
    *   **Description:** After all employees are processed, the system aggregates totals and updates `PAYROLL_RUN` status.
    *   **Actor:** System
    *   **System Validations:** All employees processed. Aggregated totals match individual `PAYROLL_RESULT`s.
    *   **State Changes:** `PAYROLL_RUN` status transitions to `CALCULATED`. Aggregated totals (`total_gross_pay`, `total_deduction`, `total_net_pay`) updated.
    *   **Error States:** Discrepancies in totals, unhandled employee calculation failures.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` update (via CDC).

### Backbone: Review Payroll Results
*   **Task 6.1: Retrieve Payroll Results**
    *   **Description:** Payroll Admin/Reviewer queries the system (via API) to retrieve all `PAYROLL_RESULT`s for a `CALCULATED` `PAYROLL_RUN`.
    *   **Actor:** Payroll Admin, Payroll Reviewer
    *   **System Validations:** `PAYROLL_RUN` status is `CALCULATED`.
    *   **State Changes:** None (read-only operation).
    *   **Error States:** `PAYROLL_RUN` not found or not in `CALCULATED` state.
    *   **Audit Logs Generated:** None (read-only operation).
*   **Task 6.2: Verify Calculations**
    *   **Description:** Payroll Admin/Reviewer manually reviews `PAYROLL_RESULT`s, potentially using `calculations_snapshot_jsonb` for detailed tracing.
    *   **Actor:** Payroll Admin, Payroll Reviewer
    *   **System Validations:** None (manual process).
    *   **State Changes:** None.
    *   **Error States:** Identified discrepancies require `PAYROLL_RUN` to be reset to `DRAFT` (if allowed) or a new correction run initiated.
    *   **Audit Logs Generated:** None.

### Backbone: Approve Payroll
*   **Task 7.1: Mark Payroll as Approved**
    *   **Description:** Payroll Reviewer triggers an API call to update `PAYROLL_RUN` status to `APPROVED`.
    *   **Actor:** Payroll Reviewer
    *   **System Validations:** `PAYROLL_RUN` status is `CALCULATED`. User has `PayrollReviewer` role.
    *   **State Changes:** `PAYROLL_RUN` status transitions to `APPROVED`.
    *   **Error States:** `PAYROLL_RUN` not in `CALCULATED` state, unauthorized user.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` status update (via CDC).

### Backbone: Lock Payroll
*   **Task 8.1: Finalize Payroll Run**
    *   **Description:** Payroll Admin triggers an API call to update `PAYROLL_RUN` status to `LOCKED`.
    *   **Actor:** Payroll Admin
    *   **System Validations:** `PAYROLL_RUN` status is `APPROVED`. User has `PayrollAdmin` role.
    *   **State Changes:** `PAYROLL_RUN` status transitions to `LOCKED`. Immutability enforced on `PAYROLL_RESULT`s.
    *   **Error States:** `PAYROLL_RUN` not in `APPROVED` state, unauthorized user.
    *   **Lock Enforcement:** Application logic prevents any `UPDATE` or `DELETE` on `PAYROLL_RESULT` records associated with this `PAYROLL_RUN`.
    *   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` status update (via CDC).

### Backbone: Generate Compliance Data
*   **Task 9.1: Extract LIRS/Federal Data**
    *   **Description:** Payroll Admin runs a script (via API) to extract aggregated data from `PAYROLL_RESULT`s for LIRS and Federal reports.
    *   **Actor:** Payroll Admin
    *   **System Validations:** `PAYROLL_RUN` status is `LOCKED`.
    *   **State Changes:** None (read-only operation).
    *   **Error States:** `PAYROLL_RUN` not found or not `LOCKED`.
    *   **Audit Logs Generated:** None.
*   **Task 9.2: Manual Report Filing**
    *   **Description:** Payroll Admin manually formats and submits the extracted data to government portals.
    *   **Actor:** Payroll Admin
    *   **System Validations:** None (external manual process).
    *   **State Changes:** None.
    *   **Error States:** None.
    *   **Audit Logs Generated:** None.

### Backbone: Retrieve Audit Logs
*   **Task 10.1: Query Audit Log**
    *   **Description:** Payroll Admin/Compliance Officer queries the `AUDIT_LOG` (via API or direct DB access) to investigate specific changes.
    *   **Actor:** Payroll Admin, Compliance Officer
    *   **System Validations:** User authorization for audit data access.
    *   **State Changes:** None (read-only operation).
    *   **Error States:** Unauthorized access, query errors.
    *   **Audit Logs Generated:** None.
*   **Task 10.2: Analyze Payroll Result Explanation**
    *   **Description:** Payroll Admin/Compliance Officer retrieves a `PAYROLL_RESULT` and analyzes its `calculations_snapshot_jsonb` for detailed explanation.
    *   **Actor:** Payroll Admin, Compliance Officer
    *   **System Validations:** User authorization for payroll data access.
    *   **State Changes:** None (read-only operation).
    *   **Error States:** Unauthorized access, `PAYROLL_RESULT` not found.
    *   **Audit Logs Generated:** None.

## 4️⃣ Convert to User Stories

This section translates the tasks into detailed user stories, each with clear acceptance criteria, validation logic, and architectural impacts.

### Milestone 1 – Foundational Data Integrity & Core Configuration

#### Technical Story: Setup Core Schema and Database
*   **Actor:** System
*   **Goal:** To establish the foundational database schema for all core entities.
*   **Business Value:** Provides the persistent storage layer for all payroll data, enabling data integrity and future scalability.
*   **Acceptance Criteria:**
    *   All tables (`Account`, `WORKSPACE`, `EMPLOYEE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, `PAYROLL_RESULT`, `AUDIT_LOG`, `EventStore`) are created with correct data types and relationships.
    *   `JSONB` fields are correctly defined (e.g., `personal_details_encrypted`, `components_jsonb`, `calculation_logic_jsonb`, `rule_definition_json`, `rules_context_snapshot`, `gross_components_jsonb`, `deductions_jsonb`, `calculations_snapshot_jsonb`, `event_payload`, `old_value_jsonb`, `new_value_jsonb`).
    *   Primary and foreign key constraints are enforced.
*   **Validation Logic Enforced:** Database schema validation.
*   **Tables Affected:** All tables in the ERD.
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None.

#### Technical Story: Implement JSON Schema Validation Framework
*   **Actor:** System
*   **Goal:** To ensure all JSONB data ingested into the system conforms to predefined schemas.
*   **Business Value:** Prevents "JSON Chaos," ensures data consistency, and reduces calculation errors, making the system more reliable and agentic-ready.
*   **Acceptance Criteria:**
    *   A framework exists to define and enforce JSON Schemas for `SALARY_DEFINITION.components_jsonb`, `STATUTORY_RULE.calculation_logic_jsonb`, `PayrollRule.rule_definition_json`, and `EMPLOYEE.personal_details_encrypted`.
    *   Any attempt to `INSERT` or `UPDATE` these JSONB fields with invalid data is rejected at the API/service layer.
*   **Validation Logic Enforced:** JSON Schema validation at the service layer before database persistence.
*   **Tables Affected:** `SALARY_DEFINITION`, `STATUTORY_RULE`, `PayrollRule`, `EMPLOYEE`.
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None.

#### Technical Story: Setup CDC for Audit Logging
*   **Actor:** System
*   **Goal:** To automatically capture all data modifications to core tables into an immutable audit log.
*   **Business Value:** Provides a tamper-proof, comprehensive audit trail for compliance, security, and dispute resolution from day one.
*   **Acceptance Criteria:**
    *   `CDCMechanism` is configured to monitor `INSERT`, `UPDATE`, `DELETE` operations on `Account`, `WORKSPACE`, `EMPLOYEE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, `PAYROLL_RESULT`.
    *   Corresponding entries are created in the `AUDIT_LOG` table with `entity_type`, `entity_id`, `action`, `old_value_jsonb`, `new_value_jsonb`, `performed_by`, and `performed_at`.
*   **Validation Logic Enforced:** `AUDIT_LOG` entries are immutable (append-only).
*   **Tables Affected:** `AUDIT_LOG` (writes), all other core tables (reads via CDC).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entries for all monitored CUD operations.

#### User Story: As a Payroll Admin, I can provision a new client workspace, so that I can begin configuring payroll for them.
*   **Actor:** Payroll Admin
*   **Goal:** To create a `WORKSPACE` for the single client.
*   **Business Value:** Enables the initial setup of the payroll system for the first client, allowing subsequent configuration.
*   **Acceptance Criteria:**
    *   Given a valid `account_id` and `workspace_name`, a new `WORKSPACE` record is created.
    *   The `WORKSPACE` record is linked to the `Account`.
    *   The system confirms successful `WORKSPACE` creation.
*   **Validation Logic Enforced:** `WORKSPACE` ID uniqueness, valid `account_id` reference.
*   **Tables Affected:** `Account` (read), `WORKSPACE` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `WORKSPACE` creation.

#### User Story: As a Payroll Admin, I can define statutory rules (PAYE, Pension, NHF) for Nigeria, so that the system can correctly calculate mandatory deductions.
*   **Actor:** Payroll Admin
*   **Goal:** To configure `STATUTORY_RULE`s and `TAX_BAND`s.
*   **Business Value:** Ensures compliance with Nigerian tax and pension laws, preventing penalties and legal issues.
*   **Acceptance Criteria:**
    *   Given valid JSON for `STATUTORY_RULE` (e.g., PAYE) and associated `TAX_BAND`s, these records are created.
    *   `STATUTORY_RULE.calculation_logic_jsonb` and `TAX_BAND` entries pass JSON Schema validation.
    *   `effective_from` and `effective_to` dates are correctly applied.
*   **Validation Logic Enforced:** JSON Schema validation, `TAX_BAND` consistency (non-overlapping, contiguous), effective date logic.
*   **Tables Affected:** `STATUTORY_RULE` (write), `TAX_BAND` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entries for `STATUTORY_RULE` and `TAX_BAND` creation.

#### User Story: As a Payroll Admin, I can define the client's salary structure, so that gross pay components are calculated according to their compensation policy.
*   **Actor:** Payroll Admin
*   **Goal:** To configure `SALARY_DEFINITION` for the client.
*   **Business Value:** Enables flexible compensation models, reducing manual calculation effort and ensuring accurate gross pay.
*   **Acceptance Criteria:**
    *   Given valid JSON for `SALARY_DEFINITION`, a new record is created for the `WORKSPACE`.
    *   `SALARY_DEFINITION.components_jsonb` passes JSON Schema validation and dependency checks.
    *   `effective_from` and `effective_to` dates are correctly applied.
*   **Validation Logic Enforced:** JSON Schema validation, component dependency validation (no circular refs, valid `of` references), effective date logic.
*   **Tables Affected:** `SALARY_DEFINITION` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `SALARY_DEFINITION` creation.

#### User Story: As a Payroll Admin, I can define custom payroll rules, so that client-specific allowances and deductions are applied correctly.
*   **Actor:** Payroll Admin
*   **Goal:** To configure `PayrollRule`s for the client.
*   **Business Value:** Allows clients to implement unique compensation policies beyond statutory requirements, increasing platform flexibility.
*   **Acceptance Criteria:**
    *   Given valid JSON for `PayrollRule`, a new record is created for the `WORKSPACE`.
    *   `PayrollRule.rule_definition_json` passes JSON Schema validation.
*   **Validation Logic Enforced:** JSON Schema validation.
*   **Tables Affected:** `PayrollRule` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `PayrollRule` creation.

#### User Story: As a Payroll Admin, I can onboard employees, so that their master data is available for payroll processing.
*   **Actor:** Payroll Admin
*   **Goal:** To ingest `EMPLOYEE` data.
*   **Business Value:** Populates the system with necessary employee information, enabling payroll calculations for individuals.
*   **Acceptance Criteria:**
    *   Given valid JSON for `EMPLOYEE` records, new `EMPLOYEE` records are created for the `WORKSPACE`.
    *   `EMPLOYEE.personal_details_encrypted` passes JSON Schema validation.
    *   `employee_number` is unique within the `WORKSPACE`.
*   **Validation Logic Enforced:** JSON Schema validation, uniqueness of `employee_number`, valid `workspace_id`.
*   **Tables Affected:** `EMPLOYEE` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `EMPLOYEE` creation.

#### User Story: As a Payroll Admin, I can update employee data, so that changes to their information are reflected in the system.
*   **Actor:** Payroll Admin
*   **Goal:** To update `EMPLOYEE` data.
*   **Business Value:** Ensures employee records are current and accurate, supporting correct payroll calculations.
*   **Acceptance Criteria:**
    *   Given valid JSON for `EMPLOYEE` updates, existing `EMPLOYEE` records are modified.
    *   `EMPLOYEE.personal_details_encrypted` passes JSON Schema validation.
    *   The system confirms successful update.
*   **Validation Logic Enforced:** JSON Schema validation, `employee_id` existence, valid `workspace_id`.
*   **Tables Affected:** `EMPLOYEE` (update).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `EMPLOYEE` update.

### Milestone 2 – Deterministic Payroll Calculation Engine

#### User Story: As a Payroll Admin, I can initiate a payroll run for a specific period, so that the system prepares for calculation with locked rules.
*   **Actor:** Payroll Admin
*   **Goal:** To create a `PAYROLL_RUN` and lock its rules context.
*   **Business Value:** Sets up the context for a payroll calculation, ensuring consistency and compliance by locking the rules in effect.
*   **Acceptance Criteria:**
    *   Given a `workspace_id`, `period_start`, `period_end`, and `pay_date`, a new `PAYROLL_RUN` record is created with `status: DRAFT`.
    *   The `PAYROLL_RUN.rules_context_snapshot` is automatically populated with all active `STATUTORY_RULE`s, `TAX_BAND`s, `SALARY_DEFINITION`s, and `PayrollRule`s for the `pay_date`.
    *   The system confirms successful run initiation.
*   **Validation Logic Enforced:** Valid period dates, `workspace_id` existence, all required rules found for snapshotting.
*   **Tables Affected:** `PAYROLL_RUN` (write), `STATUTORY_RULE` (read), `TAX_BAND` (read), `SALARY_DEFINITION` (read), `PayrollRule` (read).
*   **State Transitions Triggered:** `PAYROLL_RUN` status: `DRAFT`.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` creation and update (for `rules_context_snapshot`).

#### User Story: As a System, I can calculate an employee's gross pay, so that all salary components are correctly determined.
*   **Actor:** System
*   **Goal:** To calculate `gross_components_jsonb` for an employee.
*   **Business Value:** Accurately determines the employee's total earnings before deductions, a critical step in payroll.
*   **Acceptance Criteria:**
    *   Given an `EMPLOYEE` and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` calculates all gross components based on the `SALARY_DEFINITION` within the snapshot.
    *   The `PAYROLL_RESULT.gross_components_jsonb` is correctly populated.
*   **Validation Logic Enforced:** `RulesEngine` logic for component calculation, dependency resolution.
*   **Tables Affected:** `PAYROLL_RESULT` (write).
*   **State Transitions Triggered:** None (internal calculation step).
*   **Audit Logs Generated:** `EventStore` entry for `GrossPayCalculated` (internal event).

#### User Story: As a System, I can calculate an employee's statutory and custom deductions, so that all mandatory and client-specific deductions are correctly applied.
*   **Actor:** System
*   **Goal:** To calculate `deductions_jsonb` for an employee.
*   **Business Value:** Ensures compliance with tax and pension laws and applies client-specific deductions, leading to correct net pay.
*   **Acceptance Criteria:**
    *   Given an `EMPLOYEE`, calculated gross pay, and the `PAYROLL_RUN.rules_context_snapshot`, the `RulesEngine` calculates all statutory (PAYE, Pension, NHF) and custom deductions based on rules within the snapshot.
    *   The `PAYROLL_RESULT.deductions_jsonb` is correctly populated.
*   **Validation Logic Enforced:** `RulesEngine` logic for statutory and custom deduction calculation, including `TAX_BAND` application for PAYE.
*   **Tables Affected:** `PAYROLL_RESULT` (write).
*   **State Transitions Triggered:** None (internal calculation step).
*   **Audit Logs Generated:** `EventStore` entry for `DeductionsCalculated` (internal event).

#### User Story: As a System, I can generate a detailed calculation snapshot for each employee, so that every payroll result is fully explainable and auditable.
*   **Actor:** System
*   **Goal:** To populate `PAYROLL_RESULT.calculations_snapshot_jsonb`.
*   **Business Value:** Provides irrefutable proof of how a payroll result was derived, crucial for audit, compliance, and dispute resolution.
*   **Acceptance Criteria:**
    *   After gross and deductions are calculated, the `PAYROLL_RESULT.calculations_snapshot_jsonb` contains a detailed, immutable record of all inputs, rules (with versions), and intermediate steps.
*   **Validation Logic Enforced:** `calculations_snapshot_jsonb` structure conforms to its JSON Schema.
*   **Tables Affected:** `PAYROLL_RESULT` (write).
*   **State Transitions Triggered:** None (internal calculation step).
*   **Audit Logs Generated:** `EventStore` entry for `EmployeeProcessed` (includes `payroll_result_id`).

### Milestone 3 – End-to-End Payroll Run & Immutability

#### User Story: As a Payroll Admin, I can run payroll for all employees of a client, so that the entire monthly payroll is processed efficiently.
*   **Actor:** Payroll Admin
*   **Goal:** To trigger batch processing for a `PAYROLL_RUN`.
*   **Business Value:** Automates the processing for all employees, drastically reducing manual effort and processing time for the payroll bureau.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RUN` in `DRAFT` status, the system processes all active employees in the associated `WORKSPACE`.
    *   For each employee, a `PAYROLL_RESULT` is generated.
    *   The `PAYROLL_RUN` status transitions from `DRAFT` to `CALCULATING` and then to `CALCULATED`.
    *   `PAYROLL_RUN` totals (`total_gross_pay`, `total_deduction`, `total_net_pay`) are correctly aggregated.
*   **Validation Logic Enforced:** `PAYROLL_RUN` status transitions, aggregation logic.
*   **Tables Affected:** `PAYROLL_RUN` (update), `EMPLOYEE` (read), `PAYROLL_RESULT` (write), `EventStore` (write).
*   **State Transitions Triggered:** `PAYROLL_RUN` status: `DRAFT` → `CALCULATING` → `CALCULATED`.
*   **Audit Logs Generated:** `AUDIT_LOG` entries for `PAYROLL_RUN` status updates, `PAYROLL_RESULT` creation, `EventStore` entries.

#### User Story: As a Payroll Reviewer, I can approve a calculated payroll run, so that it can proceed to finalization.
*   **Actor:** Payroll Reviewer
*   **Goal:** To transition `PAYROLL_RUN` status to `APPROVED`.
*   **Business Value:** Provides a formal checkpoint for verification, ensuring accuracy before locking the payroll.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RUN` in `CALCULATED` status, the Payroll Reviewer can trigger an approval action.
    *   The `PAYROLL_RUN` status transitions to `APPROVED`.
*   **Validation Logic Enforced:** `PAYROLL_RUN` status is `CALCULATED`, user has `PayrollReviewer` role.
*   **Tables Affected:** `PAYROLL_RUN` (update).
*   **State Transitions Triggered:** `PAYROLL_RUN` status: `CALCULATED` → `APPROVED`.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` status update.

#### User Story: As a Payroll Admin, I can lock an approved payroll run, so that its results become immutable and tamper-proof.
*   **Actor:** Payroll Admin
*   **Goal:** To transition `PAYROLL_RUN` status to `LOCKED`.
*   **Business Value:** Guarantees the integrity and immutability of payroll records, crucial for compliance and dispute resolution.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RUN` in `APPROVED` status, the Payroll Admin can trigger a lock action.
    *   The `PAYROLL_RUN` status transitions to `LOCKED`.
    *   Any subsequent attempt to `UPDATE` or `DELETE` `PAYROLL_RESULT` records associated with this run is rejected by the system.
*   **Validation Logic Enforced:** `PAYROLL_RUN` status is `APPROVED`, user has `PayrollAdmin` role, immutability enforcement on `PAYROLL_RESULT`.
*   **Tables Affected:** `PAYROLL_RUN` (update), `PAYROLL_RESULT` (read for immutability check).
*   **State Transitions Triggered:** `PAYROLL_RUN` status: `APPROVED` → `LOCKED`.
*   **Audit Logs Generated:** `AUDIT_LOG` entry for `PAYROLL_RUN` status update.

### Milestone 4 – Explainable Payroll & Compliance Completion

#### User Story: As a Payroll Admin, I can generate payslips for a locked payroll run, so that employees receive their detailed earnings statements.
*   **Actor:** Payroll Admin
*   **Goal:** To produce payslip documents.
*   **Business Value:** Provides employees with transparent and detailed records of their pay, fulfilling a legal and operational requirement.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RUN` in `LOCKED` status, the system can retrieve all associated `PAYROLL_RESULT`s.
    *   For each `PAYROLL_RESULT`, a human-readable payslip document (e.g., PDF) is generated using data from `gross_components_jsonb`, `deductions_jsonb`, `net_pay`, and `calculations_snapshot_jsonb`.
*   **Validation Logic Enforced:** `PAYROLL_RUN` status is `LOCKED`.
*   **Tables Affected:** `PAYROLL_RESULT` (read).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None (read-only operation).

#### User Story: As a Payroll Admin, I can extract data for LIRS and Federal compliance reports, so that I can manually file statutory obligations.
*   **Actor:** Payroll Admin
*   **Goal:** To generate compliance report data.
*   **Business Value:** Provides the necessary aggregated data for regulatory filings, reducing manual data compilation effort and compliance risk.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RUN` in `LOCKED` status, the system can aggregate required data (e.g., total PAYE, total Pension) from `PAYROLL_RESULT`s.
    *   The aggregated data is presented in a structured format suitable for manual filing.
*   **Validation Logic Enforced:** `PAYROLL_RUN` status is `LOCKED`.
*   **Tables Affected:** `PAYROLL_RESULT` (read).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None (read-only operation).

#### User Story: As a Compliance Officer, I can retrieve audit logs, so that I can investigate changes and verify system actions.
*   **Actor:** Compliance Officer
*   **Goal:** To access `AUDIT_LOG` entries.
*   **Business Value:** Enables forensic analysis, dispute resolution, and regulatory compliance by providing a tamper-proof record of all system activities.
*   **Acceptance Criteria:**
    *   Given search criteria (e.g., `entity_type`, `entity_id`, `action`, date range), the system returns relevant `AUDIT_LOG` entries.
    *   Each entry includes `old_value_jsonb` and `new_value_jsonb` for data changes.
*   **Validation Logic Enforced:** User authorization for audit data access.
*   **Tables Affected:** `AUDIT_LOG` (read).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None (read-only operation).

#### User Story: As a Compliance Officer, I can explain any payroll result, so that I can confidently address employee or regulatory inquiries.
*   **Actor:** Compliance Officer
*   **Goal:** To use `PAYROLL_RESULT.calculations_snapshot_jsonb` for explanation.
*   **Business Value:** Provides full transparency and defensibility for every payroll calculation, building trust and simplifying dispute resolution.
*   **Acceptance Criteria:**
    *   Given a `PAYROLL_RESULT`, the `calculations_snapshot_jsonb` field contains a complete, understandable breakdown of all rules, inputs, and intermediate steps.
    *   The Compliance Officer can use this information to articulate *how* the net pay was derived.
*   **Validation Logic Enforced:** `PAYROLL_RESULT` is immutable.
*   **Tables Affected:** `PAYROLL_RESULT` (read).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None (read-only operation).

## 5️⃣ Slice by Roadmap Milestones

This section organizes the user stories under the previously defined roadmap milestones, ensuring that the build sequence directly supports risk reduction and outcome achievement.

*(Note: The user stories in Section 4 are already organized under their respective milestones, fulfilling this requirement.)*

## 6️⃣ Identify Technical Enablers

These are non-user-facing stories that are critical for building the foundational architecture and enabling the user stories.

#### Technical Story: Implement RulesEngine Core Scaffolding
*   **Actor:** System
*   **Goal:** To provide the core framework for interpreting and executing metadata-driven payroll rules.
*   **Business Value:** Enables the flexible and configurable calculation of payroll components, reducing hardcoded logic.
*   **Acceptance Criteria:**
    *   A core `RulesEngine` component exists that can load and interpret `STATUTORY_RULE.calculation_logic_jsonb`, `SALARY_DEFINITION.components_jsonb`, and `PayrollRule.rule_definition_json`.
    *   The engine can resolve dependencies between components (e.g., calculate `HousingAllowance` as a percentage `of BasicSalary`).
    *   The engine can apply `TAX_BAND`s for PAYE calculation.
*   **Validation Logic Enforced:** Internal unit and integration tests for rule execution.
*   **Tables Affected:** `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule` (read).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None.

#### Technical Story: Develop State Machine for PAYROLL_RUN Lifecycle
*   **Actor:** System
*   **Goal:** To enforce strict state transitions for `PAYROLL_RUN` records.
*   **Business Value:** Ensures process integrity, prevents out-of-order operations, and provides clear visibility into the payroll run status.
*   **Acceptance Criteria:**
    *   A state machine is implemented that governs transitions: `DRAFT` → `CALCULATING` → `CALCULATED` → `APPROVED` → `LOCKED`.
    *   Invalid state transitions are rejected.
    *   Associated business logic is triggered on state changes (e.g., `rules_context_snapshot` population on `DRAFT` creation, immutability enforcement on `LOCKED`).
*   **Validation Logic Enforced:** State machine rules.
*   **Tables Affected:** `PAYROLL_RUN` (update).
*   **State Transitions Triggered:** All `PAYROLL_RUN` status changes.
*   **Audit Logs Generated:** `AUDIT_LOG` entries for `PAYROLL_RUN` status updates.

#### Technical Story: Implement PII Encryption for Employee Data
*   **Actor:** System
*   **Goal:** To protect sensitive employee Personal Identifiable Information (PII) at rest.
*   **Business Value:** Ensures compliance with data privacy regulations and enhances data security, building trust.
*   **Acceptance Criteria:**
    *   The `EMPLOYEE.personal_details_encrypted` field is stored in an encrypted format in the database.
    *   Data is encrypted upon `INSERT`/`UPDATE` and decrypted upon `READ` by authorized services.
*   **Validation Logic Enforced:** Encryption/decryption integrity checks.
*   **Tables Affected:** `EMPLOYEE` (read/write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** None.

#### Technical Story: Implement EventStore Append-Only Mechanism
*   **Actor:** System
*   **Goal:** To provide an immutable, append-only log for domain events.
*   **Business Value:** Creates a historical record of all significant payroll events, crucial for future AI agents, audit, and system debugging.
*   **Acceptance Criteria:**
    *   The `EventStore` table only allows `INSERT` operations.
    *   Attempts to `UPDATE` or `DELETE` records in `EventStore` are rejected.
    *   Events like `EmployeeProcessed` are successfully written to the `EventStore`.
*   **Validation Logic Enforced:** Database-level append-only constraint.
*   **Tables Affected:** `EventStore` (write).
*   **State Transitions Triggered:** None.
*   **Audit Logs Generated:** `AUDIT_LOG` entries for `EventStore` writes (via CDC).

## 7️⃣ Highlight Compliance-Critical Stories

These stories directly address the core risks of incorrect calculations, unauthorized modifications, missing audit trails, and data discrepancies, ensuring the system meets stringent compliance requirements.

*   **Incorrect Tax Calculation:**
    *   **User Story:** As a Payroll Admin, I can define statutory rules (PAYE, Pension, NHF) for Nigeria, so that the system can correctly calculate mandatory deductions.
    *   **User Story:** As a System, I can calculate an employee's statutory and custom deductions, so that all mandatory and client-specific deductions are correctly applied.
    *   **Technical Enabler:** Implement RulesEngine Core Scaffolding.
*   **Payroll Modification After Lock:**
    *   **User Story:** As a Payroll Admin, I can lock an approved payroll run, so that its results become immutable and tamper-proof.
    *   **Technical Enabler:** Develop State Machine for PAYROLL_RUN Lifecycle (specifically the `LOCKED` state enforcement).
*   **Missing Audit Trail:**
    *   **Technical Enabler:** Setup CDC for Audit Logging.
    *   **User Story:** As a Compliance Officer, I can retrieve audit logs, so that I can investigate changes and verify system actions.
*   **Report-Data Mismatch:**
    *   **User Story:** As a System, I can generate a detailed calculation snapshot for each employee, so that every payroll result is fully explainable and auditable.
    *   **User Story:** As a Payroll Admin, I can extract data for LIRS and Federal compliance reports, so that I can manually file statutory obligations.
    *   **User Story:** As a Compliance Officer, I can explain any payroll result, so that I can confidently address employee or regulatory inquiries.

## 8️⃣ Gap Analysis: Prompt vs. Final User Story Map

This section provides a clear analysis of how the final User Story Map aligns with the provided prompt, highlighting additional considerations and deferred items.

### Alignment (What I've Considered that is Specified)

*   **Actors:** All specified actors (`Payroll Admin`, `Payroll Reviewer`, `Bureau Owner`, `Compliance Officer`, `System`) are included with their goals, risks, and definitions of success.
*   **Backbone (User Journey):** The backbone activities (`Configure Client`, `Configure Salary Components`, `Onboard Employee`, `Prepare Payroll Period`, `Run Payroll Calculation`, `Review Payroll Results`, `Approve Payroll`, `Lock Payroll`, `Generate Compliance Data`, `Retrieve Audit Logs`) are all present and ordered chronologically.
*   **Task Breakdown:** Each backbone activity has a detailed task breakdown, including system validations, state changes, error states, and lock enforcement.
*   **User Stories:** Each story includes Actor, Goal, Business Value, Acceptance Criteria, Validation Logic, Tables Affected, State Transitions, and Audit Logs Generated.
*   **Slice by Roadmap Milestones:** Stories are organized under the four Phase 1 roadmap milestones.
*   **Technical Enablers:** Technical stories are clearly separated and marked as non-user-facing.
*   **Compliance-Critical Stories:** Stories protecting against specified risks (incorrect tax, modification after lock, missing audit, report mismatch) are highlighted.
*   **Exclusions:** All `Do NOT Include` items (Autonomous AI, Agent decision loops, Auto compliance filing, Multi-client scaling, Phase 2 automation) are strictly excluded.

### Additional Considerations (What I've Considered that was Not Explicitly Specified)

These are items I included in the architecture and user stories to enhance robustness and mitigate future risks, based on best practices for financial systems and the previous architectural discussions:

*   **`rules_context_snapshot` in `PAYROLL_RUN`:** This critical architectural decision, introduced for compliance locking, is explicitly reflected in the `Prepare Payroll Period` backbone and its associated user story. It ensures that rules are locked at the start of a run, preventing mid-month changes from affecting in-progress calculations.
*   **JSON Schema Validation Framework (Technical Enabler):** This was a key mitigation strategy for the "JSON Chaos" risk. It's included as a technical story to ensure all JSONB data conforms to predefined schemas, maintaining data integrity and agentic-readiness.
*   **PII Encryption for Employee Data (Technical Enabler):** The `EMPLOYEE.personal_details_encrypted` field is explicitly designed for encryption at rest, addressing a crucial security and compliance requirement for sensitive PII, even if not explicitly requested in the prompt.
*   **EventStore Append-Only Mechanism (Technical Enabler):** While the prompt mentioned audit logging, the explicit implementation of an append-only `EventStore` as a technical enabler ensures a robust, immutable historical record for future AI and deep audit, going beyond basic audit logs.
*   **State Machine for `PAYROLL_RUN` Lifecycle (Technical Enabler):** This ensures strict process integrity and prevents out-of-order operations, which is vital for a financial system.

### Deferred Items (What You Specified that is Not in Phase 1)

All items specified in the prompt's `Do NOT Include` section have been strictly adhered to and are implicitly deferred to later phases. No items from the `Must include` section of the prompt have been deferred; all are covered in Phase 1.

This comprehensive User Story Map provides a detailed, actionable plan for Phase 1, ensuring that every piece of work contributes to a secure, compliant, and AI-ready payroll platform.
