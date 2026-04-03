# Phase 1 Business Rule & Process Specification: Nigerian Payroll Platform MVP

This document reverse-engineers the complete set of business rules, workflows, and operational logic for Phase 1 of the Nigerian Payroll Platform MVP, based on the previously designed ERD and architectural diagrams. The focus is strictly on what is implied by the current design, without introducing new features or moving into later phases.

## 1️⃣ ERD Deconstruction

This section deconstructs each table in the Phase 1 ERD, explaining its business purpose, population, usage, and the significance of its relationships.

### Table Name: `Account`
*   **Business Purpose:** Represents the top-level billing and organizational entity. In Phase 1, it primarily serves as a placeholder for the single payroll bureau's account.
*   **Why it exists:** To establish the highest level of ownership and to support future multi-account scaling. It's the parent of `WORKSPACE`.
*   **Who/what populates it:** Manually provisioned by system administrators (e.g., via direct database insert or a backend script) during Phase 1 setup.
*   **When it is populated (trigger/event):** Once, during the initial system setup for the payroll bureau.
*   **How it is used in payroll processing:** Indirectly, by owning the `WORKSPACE` which directly participates in payroll. It provides the logical grouping for billing and overall service usage.
*   **Example row:**
    ```
    account_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    name: "Nigerian Payroll Bureau Inc."
    owner_email: "admin@payrollbureau.com"
    created_at: "2026-01-01T10:00:00Z"
    ```
*   **Why the relationships matter:** It forms the root of the multi-tenancy hierarchy. Without it, `WORKSPACE` would lack a top-level organizational context.
*   **What would break if this table did not exist:** There would be no logical parent for `WORKSPACE`s, complicating future multi-account management and billing. The system would lack a clear top-level tenant boundary.
*   **Foreign key logic:** None (it's the root entity).
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `Account` can own many `WORKSPACE`s).
*   **Why that decision was architecturally necessary:** To establish a clear, scalable hierarchy for multi-tenancy from day one, even if only one `Account` is used in Phase 1. This supports the 
goal of horizontal scaling across clients.

### Table Name: `WORKSPACE`
*   **Business Purpose:** Represents a single client company or a distinct operational unit within a client. It acts as the primary tenant boundary for data isolation.
*   **Why it exists:** To logically group all payroll-related data and configurations for a specific client. All core payroll entities (employees, rules, runs) are scoped to a `WORKSPACE`.
*   **Who/what populates it:** Manually provisioned by system administrators (e.g., via direct database insert or a backend script) during Phase 1 setup.
*   **When it is populated (trigger/event):** Once, during the initial system setup for the single client.
*   **How it is used in payroll processing:** All payroll operations (employee management, rule definition, payroll runs) are performed within the context of a specific `WORKSPACE`. It ensures strong tenant isolation by acting as a foreign key for most other tables.
*   **Example row:**
    ```
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    account_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    name: "Acme Corp Nigeria"
    country_code: "NG"
    base_currency: "NGN"
    created_at: "2026-01-01T10:05:00Z"
    ```
*   **Why the relationships matter:** It is the central hub for tenant-specific data. Its relationships to `EMPLOYEE`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, and `AUDIT_LOG` enforce tenant isolation at the database level.
*   **What would break if this table did not exist:** There would be no mechanism for data isolation between clients, making multi-tenancy impossible and violating security and compliance requirements. All data would be global, leading to data integrity issues.
*   **Foreign key logic:** `account_id` links to `Account` (1-to-many). All other tenant-specific tables link to `workspace_id`.
*   **Cardinality:** 1-to-1 with `Account` in Phase 1 (though architecturally 1-to-many). 1-to-many with `EMPLOYEE`, `SALARY_DEFINITION`, `PayrollRule`, `PAYROLL_RUN`, `AUDIT_LOG`, `EventStore`.
*   **Why that decision was architecturally necessary:** To provide strong tenant isolation (Schema-per-Tenant model) and a clear logical boundary for all client-specific data and operations from the very beginning. This is crucial for security, compliance, and future horizontal scaling.

### Table Name: `EMPLOYEE`
*   **Business Purpose:** Stores core master data for each employee within a specific `WORKSPACE`.
*   **Why it exists:** To hold all static and semi-static information about an individual employee necessary for payroll processing and HR functions.
*   **Who/what populates it:** Initially, system administrators via manual JSON ingestion. In later phases, HR users via UI or integration agents.
*   **When it is populated (trigger/event):** When a new employee is onboarded or existing employee data is updated.
*   **How it is used in payroll processing:** Provides essential employee attributes (e.g., employee number, status, personal details) that are inputs to payroll calculations and payslip generation.
*   **Example row:**
    ```
    employee_id: "e1234567-89ab-cdef-1234-567890abcdef"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    employee_number: "ACME001"
    status: "Active"
    personal_details_encrypted: {"first_name": "John", "last_name": "Doe", "dob": "1985-05-15", "bank_account": "0123456789", "nin": "12345678901"}
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. Indirectly linked to `PAYROLL_RESULT` (via `PAYROLL_RUN`) to associate results with an employee.
*   **What would break if this table did not exist:** Payroll cannot be processed for individuals. There would be no record of who is being paid.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many).
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` has many `EMPLOYEE`s). 1-to-many with `PAYROLL_RESULT` (one `EMPLOYEE` can have many `PAYROLL_RESULT`s over time).
*   **Why that decision was architecturally necessary:** To centralize employee data, ensuring it's scoped to a specific client and available for payroll calculations. The `JSONB personal_details_encrypted` field allows for flexible storage of PII while enforcing encryption, supporting future expansion without schema changes.

### Table Name: `SALARY_DEFINITION`
*   **Business Purpose:** Defines the structure of salary components (e.g., Basic, Housing, Transport) for a specific `WORKSPACE`.
*   **Why it exists:** To allow clients to define their unique salary structures as metadata, enabling flexible compensation models without requiring code changes. This is crucial for the metadata-driven rules engine.
*   **Who/what populates it:** System administrators via manual JSON ingestion in Phase 1.
*   **When it is populated (trigger/event):** When a client's salary structure is initially set up or updated.
*   **How it is used in payroll processing:** The `PayrollProcessingService` and `RulesEngine` read this definition to understand how an employee's gross pay components are structured and calculated.
*   **Example row:**
    ```
    salary_definition_id: "sd123456-7890-abcd-ef12-345678abcdef"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    name: "Standard Salaried Employee Structure"
    components_jsonb: [
        {"name": "Basic Salary", "type": "fixed", "value": "base_salary_amount"},
        {"name": "Housing Allowance", "type": "percentage", "of": "Basic Salary", "rate": 0.5},
        {"name": "Transport Allowance", "type": "fixed", "value": 50000}
    ]
    schema_version: 1
    effective_from: "2026-01-01"
    effective_to: "9999-12-31"
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. Implicitly linked to `EMPLOYEE` via `EMPLOYEE_CONTRACT` (Out of Phase 1 Scope) to assign a specific salary structure to an employee.
*   **What would break if this table did not exist:** Clients would not be able to define their own salary structures, forcing hardcoded logic or schema changes for every new client, violating the scalability goal.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many).
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` can define many `SALARY_DEFINITION`s). 1-to-many with `EMPLOYEE_CONTRACT` (Out of Phase 1 Scope).
*   **Why that decision was architecturally necessary:** To enable a metadata-driven payroll engine, allowing for extreme flexibility in defining compensation structures without database schema modifications. The `JSONB components_jsonb` is key to this flexibility, and `effective_from`/`effective_to` allow for historical changes.

### Table Name: `STATUTORY_RULE`
*   **Business Purpose:** Stores definitions for government-mandated payroll rules (e.g., PAYE, Pension rates, NHF contributions) that apply across all clients in a specific country/region.
*   **Why it exists:** To centralize and version statutory compliance logic, ensuring all clients adhere to the correct legal requirements for a given period. This is a system-owned rule type.
*   **Who/what populates it:** System administrators via manual JSON ingestion in Phase 1. Managed by the platform, not directly by clients.
*   **When it is populated (trigger/event):** When new statutory rules are introduced, existing ones are updated, or corrections are made.
*   **How it is used in payroll processing:** The `RulesEngine` retrieves the active `STATUTORY_RULE`s based on the `pay_date` of a `PAYROLL_RUN` to apply mandatory deductions and calculations.
*   **Example row:**
    ```
    statutory_rule_id: "sr123456-7890-abcd-ef12-345678abcdef"
    country_code: "NG"
    rule_type: "PAYE_CALCULATION"
    calculation_logic_jsonb: {"method": "progressive", "bands_ref": "tax_band_id_for_2026", "relief_allowance_formula": "200000 + 0.2 * annual_gross"}
    effective_from: "2026-01-01"
    effective_to: "9999-12-31"
    version_number: 1
    ```
*   **Why the relationships matter:** Linked to `TAX_BAND` (1-to-many) to define the specific tax brackets for a PAYE rule. Its `country_code` ensures applicability to the correct region.
*   **What would break if this table did not exist:** The system would not be able to accurately calculate statutory deductions, leading to non-compliance and legal issues. Each client would need to manually configure these, leading to errors and inconsistencies.
*   **Foreign key logic:** None (it's a top-level rule definition). `statutory_rule_id` is referenced by `TAX_BAND`.
*   **Cardinality:** 1-to-many with `TAX_BAND` (one `STATUTORY_RULE` can define many `TAX_BAND`s).
*   **Why that decision was architecturally necessary:** To centralize, version, and manage critical compliance logic independently of client-specific rules. The `JSONB calculation_logic_jsonb` allows for flexible definition of complex statutory formulas, and `effective_from`/`effective_to` support temporal rule changes.

### Table Name: `TAX_BAND`
*   **Business Purpose:** Stores the specific income brackets and corresponding rates for progressive tax calculations, linked to a `STATUTORY_RULE`.
*   **Why it exists:** To provide the granular data required by the PAYE `STATUTORY_RULE` for calculating income tax based on different income levels.
*   **Who/what populates it:** System administrators via manual JSON ingestion in Phase 1, as part of `STATUTORY_RULE` definition.
*   **When it is populated (trigger/event):** When a `STATUTORY_RULE` (specifically a tax calculation rule) is defined or updated.
*   **How it is used in payroll processing:** The `RulesEngine`, when executing a PAYE `STATUTORY_RULE`, queries `TAX_BAND` to find the applicable rates for an employee's taxable income.
*   **Example row:**
    ```
    tax_band_id: "tb123456-7890-abcd-ef12-345678abcdef"
    statutory_rule_id: "sr123456-7890-abcd-ef12-345678abcdef" (linking to PAYE_CALCULATION rule)
    band_order: 1
    lower_bound: 0.00
    upper_bound: 300000.00
    rate: 0.07
    effective_from: "2026-01-01"
    effective_to: "9999-12-31"
    ```
*   **Why the relationships matter:** It is a child of `STATUTORY_RULE`, ensuring that tax bands are always associated with a specific, versioned statutory tax rule. This maintains historical accuracy.
*   **What would break if this table did not exist:** The system would not be able to perform progressive income tax calculations, a fundamental requirement for Nigerian PAYE compliance.
*   **Foreign key logic:** `statutory_rule_id` links to `STATUTORY_RULE` (1-to-many).
*   **Cardinality:** 1-to-many with `STATUTORY_RULE` (one `STATUTORY_RULE` can have many `TAX_BAND`s).
*   **Why that decision was architecturally necessary:** To externalize and parameterize tax band data, making tax calculations configurable and historically traceable without hardcoding. `effective_from`/`effective_to` allow for temporal changes in tax brackets.

### Table Name: `PayrollRule`
*   **Business Purpose:** Stores client-specific, custom payroll rules (e.g., company-specific allowances, deductions, bonus calculations) for a given `WORKSPACE`.
*   **Why it exists:** To allow each client to define their unique business logic for payroll components that are not statutory. This is the core of the metadata-driven flexibility for clients.
*   **Who/what populates it:** System administrators via manual JSON ingestion in Phase 1.
*   **When it is populated (trigger/event):** When a client's custom payroll rule is initially set up or updated.
*   **How it is used in payroll processing:** The `RulesEngine` retrieves active `PayrollRule`s for a `WORKSPACE` to apply custom calculations during a `PAYROLL_RUN`.
*   **Example row:**
    ```
    rule_id: "pr123456-7890-abcd-ef12-345678abcdef"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    rule_name: "Performance Bonus Sales"
    rule_type: "BONUS_CALCULATION"
    rule_definition_json: {"method": "fixed_percentage_of_sales", "rate": 0.02, "threshold": 1000000}
    schema_version: 1
    is_active: true
    created_at: "2026-01-15T09:00:00Z"
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. Its `rule_type` and `rule_definition_json` are interpreted by the `RulesEngine`.
*   **What would break if this table did not exist:** Clients would not be able to customize their payroll beyond statutory requirements, severely limiting the platform's utility as a flexible payroll bureau solution.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many).
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` can define many `PayrollRule`s).
*   **Why that decision was architecturally necessary:** To provide the metadata-driven flexibility for client-specific payroll logic. The `JSONB rule_definition_json` is critical for this, allowing complex, custom logic to be stored as data, not code. `schema_version` is vital for governance.

### Table Name: `PAYROLL_RUN`
*   **Business Purpose:** Represents a single instance of a payroll processing cycle for a specific `WORKSPACE` and period.
*   **Why it exists:** To track the execution of a payroll, its status, and to link all associated `PAYROLL_RESULT`s. It serves as the central orchestrator for a payroll event.
*   **Who/what populates it:** The `PayrollProcessingService` initiates a new `PAYROLL_RUN`.
*   **When it is populated (trigger/event):** When a payroll administrator (or system, in later phases) triggers a payroll calculation for a given period.
*   **How it is used in payroll processing:** It defines the context (period, pay date, status) for all `PAYROLL_RESULT`s generated within that run. The `rules_context_snapshot` is crucial for compliance and replayability.
*   **Example row:**
    ```
    payroll_run_id: "prun1234-5678-90ab-cdef-1234567890ab"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    period_start: "2026-01-01"
    period_end: "2026-01-31"
    pay_date: "2026-02-05"
    total_gross_pay: 15000000.00
    total_deduction: 3000000.00
    total_net_pay: 12000000.00
    status: "CALCULATED"
    rules_context_snapshot: {"statutory_rules": [{"id": "sr1", "version": 1, "effective_from": "2026-01-01"}], "payroll_rules": [{"id": "pr1", "version": 1}]}
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. It is the parent of `PAYROLL_RESULT`s and `EventStore` events, providing the context for all payroll-related data.
*   **What would break if this table did not exist:** There would be no way to group individual payroll results into a coherent run, track its status, or ensure rule consistency across all employees in a single processing cycle. The compliance locking mechanism would fail.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many). `payroll_run_id` is referenced by `PAYROLL_RESULT` and `EventStore`.
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` has many `PAYROLL_RUN`s). 1-to-many with `PAYROLL_RESULT` and `EventStore`.
*   **Why that decision was architecturally necessary:** To provide a clear, auditable, and immutable record of each payroll processing event. The `rules_context_snapshot` is a critical architectural decision for compliance, ensuring that a payroll run is always calculated with a consistent set of rules, regardless of subsequent rule changes.

### Table Name: `PAYROLL_RESULT`
*   **Business Purpose:** Stores the immutable, detailed outcome of a single employee's payroll calculation for a specific `PAYROLL_RUN`. This serves as the definitive payslip data.
*   **Why it exists:** To provide a complete, auditable record of an employee's earnings and deductions for a given payroll period. It is the source data for payslip generation and reporting.
*   **Who/what populates it:** The `PayrollProcessingService` generates these records after calculating an employee's pay.
*   **When it is populated (trigger/event):** After an employee's payroll has been calculated within a `PAYROLL_RUN`.
*   **How it is used in payroll processing:** It is queried to generate payslips, provide payroll summaries, and support audit inquiries. The `calculations_snapshot_jsonb` is key for explaining the result.
*   **Example row:**
    ```
    payroll_result_id: "pr123456-7890-abcd-ef12-345678abcdef"
    payroll_run_id: "prun1234-5678-90ab-cdef-1234567890ab"
    employee_id: "e1234567-89ab-cdef-1234-567890abcdef"
    gross_components_jsonb: {"Basic Salary": 500000, "Housing Allowance": 250000, "Transport Allowance": 50000}
    deductions_jsonb: {"PAYE": 75000, "Pension": 40000}
    net_pay: 685000.00
    calculations_snapshot_json: {
        "inputs": {"annual_gross": 9600000, "taxable_income": 7200000},
        "steps": [
            {"component": "Basic Salary", "value": 500000, "rule_id": "sd1_basic"},
            {"component": "Housing Allowance", "value": 250000, "rule_id": "sd1_housing"},
            {"deduction": "PAYE", "value": 75000, "rule_id": "sr1_paye", "bands_applied": [...], "relief_used": ...}
        ]
    }
    generated_at: "2026-02-05T11:30:00Z"
    ```
*   **Why the relationships matter:** Linked to `PAYROLL_RUN` for context and `EMPLOYEE` to identify the recipient. It is an immutable record.
*   **What would break if this table did not exist:** There would be no historical record of what was paid to whom, making payslip generation impossible and auditability severely compromised. It is the core financial output.
*   **Foreign key logic:** `payroll_run_id` links to `PAYROLL_RUN` (1-to-many). `employee_id` links to `EMPLOYEE` (1-to-many).
*   **Cardinality:** 1-to-many with `PAYROLL_RUN` (one `PAYROLL_RUN` produces many `PAYROLL_RESULT`s). 1-to-many with `EMPLOYEE` (one `EMPLOYEE` receives many `PAYROLL_RESULT`s).
*   **Why that decision was architecturally necessary:** To provide a single, immutable source of truth for each payslip, including the full calculation breakdown. The `JSONB calculations_snapshot_json` is crucial for auditability, explainability, and future AI agent validation, making each result self-contained.

### Table Name: `AUDIT_LOG`
*   **Business Purpose:** Records significant actions and changes within a `WORKSPACE` for security, compliance, and forensic purposes.
*   **Why it exists:** To provide a tamper-proof, chronological record of 
who did what, when, and to what, ensuring accountability and meeting regulatory requirements.
*   **Who/what populates it:** The `AuditComplianceService` (implicitly, via CDC) and potentially core services for specific application-level events. In Phase 1, primarily populated by the `CDCMechanism` streaming changes from `RelationalDB`.
*   **When it is populated (trigger/event):** Continuously, whenever a significant data change or action occurs in the `RelationalDB` (via CDC) or an auditable event happens within the application.
*   **How it is used in payroll processing:** Provides a historical record for auditors, compliance officers, and for debugging. It helps answer questions like "Who changed this employee's salary?" or "When was this rule activated?"
*   **Example row:**
    ```
    audit_log_id: "al123456-7890-abcd-ef12-345678abcdef"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    entity_type: "EMPLOYEE"
    entity_id: "e1234567-89ab-cdef-1234-567890abcdef"
    action: "UPDATE"
    old_value_jsonb: {"status": "Pending"}
    new_value_jsonb: {"status": "Active"}
    performed_by: "system_admin_id" (or "CDC_SYSTEM")
    performed_at: "2026-01-02T14:00:00Z"
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. It is a standalone, immutable log, not directly linked to other business entities in a transactional sense, but rather observing them.
*   **What would break if this table did not exist:** The system would lack accountability, making it impossible to trace changes, resolve disputes, or meet regulatory compliance requirements for data integrity and security.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many).
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` generates many `AUDIT_LOG` entries).
*   **Why that decision was architecturally necessary:** To provide a robust, tamper-proof audit trail using Change Data Capture (CDC). This ensures that every change to the underlying relational data is recorded, fulfilling a critical non-functional requirement for security and compliance from day one.

### Table Name: `EventStore`
*   **Business Purpose:** An append-only log of domain events that represent state changes in the system. In Phase 1, it primarily acts as a 
 "flight recorder" for the payroll process.
*   **Why it exists:** To capture the sequence of domain events that occur during a payroll run, providing an immutable, chronological record of the process. This is the foundation for event sourcing and future AI agent integration.
*   **Who/what populates it:** The `PayrollProcessingService` emits events (e.g., `PayrollCalculated`, `EmployeeProcessed`) during a `PAYROLL_RUN`.
*   **When it is populated (trigger/event):** Continuously, as the `PayrollProcessingService` executes steps within a `PAYROLL_RUN` for each employee.
*   **How it is used in payroll processing:** In Phase 1, it is primarily an append-only log for recording the process. It is not actively queried for state reconstruction or projections in this phase, but it provides the raw data for future analysis and replayability.
*   **Example row:**
    ```
    event_id: "evt123456-7890-abcd-ef12-345678abcdef"
    workspace_id: "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    aggregate_id: "prun1234-5678-90ab-cdef-1234567890ab" (PAYROLL_RUN ID)
    aggregate_type: "PAYROLL_RUN"
    event_type: "EmployeeProcessed"
    event_payload: {"employee_id": "e1234567-89ab-cdef-1234-567890abcdef", "status": "calculated", "net_pay": 685000.00}
    occurred_at: "2026-02-05T11:30:05Z"
    ```
*   **Why the relationships matter:** Linked to `WORKSPACE` for tenant isolation. It is implicitly linked to `PAYROLL_RUN` via `aggregate_id` to provide context for the events.
*   **What would break if this table did not exist:** The system would lack a granular, immutable record of the payroll processing steps, making it impossible to reconstruct the exact sequence of events that led to a `PAYROLL_RESULT`. This would severely hamper future debugging, auditing, and AI agent training.
*   **Foreign key logic:** `workspace_id` links to `WORKSPACE` (1-to-many). `aggregate_id` implicitly links to `PAYROLL_RUN`.
*   **Cardinality:** 1-to-many with `WORKSPACE` (one `WORKSPACE` generates many `EventStore` entries). 1-to-many with `PAYROLL_RUN` (one `PAYROLL_RUN` generates many `EventStore` entries).
*   **Why that decision was architecturally necessary:** To lay the foundation for Event Sourcing and the Saga Pattern. In Phase 1, it serves as an append-only "flight recorder," capturing the raw events without complex processing. This ensures that the historical data needed for future phases (e.g., event replay, AI agent training) is collected from day one, adhering to the "no throwaway code" principle.

### Out of Phase 1 Scope (ERD Entities)

*   **`User`**: While present in the full ERD, in Phase 1, user authentication and management are handled externally or by direct system access. The `User` table is dormant.
*   **`GRADE` & `GRADE_HISTORY`**: Employee grading and its history are not actively managed in Phase 1. Salary structures are directly linked to `SALARY_DEFINITION`.
*   **`TAX_AUTHORITY` & `EMPLOYEE_TAX_ASSIGNMENT`**: While `STATUTORY_RULE` and `TAX_BAND` handle federal compliance, the explicit assignment of employees to specific tax authorities is deferred.
*   **`EMPLOYEE_CONTRACT`**: Employee contracts are not explicitly managed as separate entities in Phase 1. Salary definitions are implicitly applied to employees.

## 2️⃣ JSONB Field Decomposition

This section details the usage, structure, and implications of JSONB fields within the Phase 1 ERD, highlighting their role in flexibility and the metadata-driven approach.

### Field: `EMPLOYEE.personal_details_encrypted`
*   **Why JSONB was used instead of normalized tables:** To provide flexibility for storing diverse employee personal information without frequent schema migrations. It allows for different clients to have slightly varied PII requirements (e.g., additional national IDs) without altering the core `EMPLOYEE` table structure. The `_encrypted` suffix indicates a critical security requirement.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1985-05-15",
      "gender": "Male",
      "address": {
        "street": "123 Main St",
        "city": "Lagos",
        "state": "Lagos",
        "zip_code": "100001"
      },
      "bank_account_number": "0123456789",
      "bank_name": "First Bank of Nigeria",
      "national_identification_number": "NIN12345678901"
    }
    ```
*   **How the engine reads it:** The `EmployeeHRService` (and subsequently the `PayrollProcessingService`) will decrypt and parse this JSONB to extract necessary PII for payroll processing (e.g., bank account for disbursement, NIN for statutory reporting). Specific keys (e.g., `bank_account_number`) will be accessed directly.
*   **How it affects calculation flow:** Provides PII inputs for payroll (e.g., employee name for payslip, bank details for payment file). The encrypted nature means the service must handle decryption before use.
*   **A real payroll example showing it in action:** During a `PAYROLL_RUN`, the `PayrollProcessingService` retrieves an `EMPLOYEE` record. It decrypts `personal_details_encrypted` to get the `bank_account_number` for generating the bank payment file and the `first_name`, `last_name` for the payslip.
*   **What business flexibility it enables:** Allows for easy addition of new PII fields without database schema changes. Supports different data requirements across future clients. Enforces PII encryption.
*   **What risks it introduces:** If not properly managed (e.g., lack of JSON Schema validation, improper encryption key management), it can lead to data inconsistency, security vulnerabilities, and difficulty in querying specific PII fields.

### Field: `SALARY_DEFINITION.components_jsonb`
*   **Why JSONB was used instead of normalized tables:** To enable a highly flexible, metadata-driven definition of salary components. Each client can define their unique mix of basic pay, allowances, and their calculation methods without requiring schema changes. This is fundamental to the `RulesEngine`.
*   **What structure is expected inside it (example JSON):**
    ```json
    [
      {
        "component_name": "Basic Salary",
        "type": "fixed",
        "value_source": "employee_base_salary",
        "is_taxable": true,
        "is_pensionable": true
      },
      {
        "component_name": "Housing Allowance",
        "type": "percentage",
        "of": "Basic Salary",
        "rate": 0.5,
        "is_taxable": true,
        "is_pensionable": false
      },
      {
        "component_name": "Transport Allowance",
        "type": "fixed",
        "value": 50000,
        "is_taxable": true,
        "is_pensionable": false
      },
      {
        "component_name": "Meal Allowance",
        "type": "fixed",
        "value": 20000,
        "is_taxable": false,
        "is_pensionable": false
      }
    ]
    ```
*   **How the engine reads it:** The `RulesEngine` (specifically the `PayrollConfigService` and `PayrollProcessingService`) reads this JSONB to understand the components of an employee's salary. It iterates through the array, interpreting `type`, `value_source`, `of`, `rate`, and `value` to calculate each component. `is_taxable` and `is_pensionable` flags guide statutory deductions.
*   **How it affects calculation flow:** Directly dictates the gross pay calculation. The engine processes these components sequentially or based on defined dependencies to arrive at the total gross pay before deductions.
*   **A real payroll example showing it in action:** For an employee with a `SALARY_DEFINITION` linked to them, the `PayrollProcessingService` reads this JSONB. It first calculates Basic Salary, then Housing Allowance as 50% of Basic, then adds fixed Transport and Meal Allowances. It then sums these to get the total gross pay.
*   **What business flexibility it enables:** Allows clients to define highly customized salary structures without requiring code changes or database schema modifications. Supports various calculation methods (fixed, percentage, formula-based). Enables rapid onboarding of clients with diverse compensation plans.
*   **What risks it introduces:** Without strict JSON Schema validation and versioning, the structure can become inconsistent, leading to calculation errors. Complex inter-dependencies between components can be difficult to manage and debug if not well-defined.

### Field: `STATUTORY_RULE.calculation_logic_jsonb`
*   **Why JSONB was used instead of normalized tables:** To store the executable logic for statutory rules as metadata. This allows for versioning of rules and dynamic application by the `RulesEngine`, making compliance updates agile and historically traceable.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "rule_code": "PAYE_NG_2026",
      "description": "Pay As You Earn (PAYE) calculation for Nigeria, 2026 tax year.",
      "method": "progressive_tax",
      "taxable_income_formula": "annual_gross_income - (pension_deduction + national_housing_fund_deduction + consolidated_relief_allowance)",
      "consolidated_relief_allowance_formula": "MIN(200000 + 0.2 * annual_gross_income, 0.2 * annual_gross_income)",
      "bands_reference": "tax_band_id_for_2026_PAYE"
    }
    ```
*   **How the engine reads it:** The `RulesEngine` interprets this JSONB to execute the statutory calculation. For example, for a `PAYE_CALCULATION` rule, it would read the `method`, `taxable_income_formula`, `consolidated_relief_allowance_formula`, and then use `bands_reference` to fetch the relevant `TAX_BAND`s.
*   **How it affects calculation flow:** Directly implements the core statutory deductions. The engine uses the formulas and references within this JSONB to determine taxable income and apply the correct tax rates.
*   **A real payroll example showing it in action:** During a `PAYROLL_RUN`, after gross pay is determined, the `PayrollProcessingService` invokes the `RulesEngine` for PAYE. The engine retrieves the active `STATUTORY_RULE` for PAYE, reads its `calculation_logic_jsonb`, calculates the Consolidated Relief Allowance, determines taxable income, and then applies the progressive rates from the linked `TAX_BAND`s.
*   **What business flexibility it enables:** Allows for rapid updates to statutory rules (e.g., new tax laws) without code deployments. Enables historical accuracy by versioning rules. Supports complex, formula-based statutory calculations.
*   **What risks it introduces:** Incorrectly defined formulas can lead to massive compliance issues. Requires robust testing and validation of rule changes. The `schema_version` is critical to ensure the engine knows how to interpret the JSON structure.

### Field: `PayrollRule.rule_definition_json`
*   **Why JSONB was used instead of normalized tables:** Similar to `SALARY_DEFINITION`, this provides extreme flexibility for client-specific custom rules. It allows clients to define unique allowances, deductions, or bonus triggers as metadata.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "rule_code": "SALES_BONUS_Q1",
      "description": "Quarterly sales bonus for achieving target.",
      "type": "bonus",
      "trigger_condition": "employee_sales_target_achieved == true",
      "calculation_method": "percentage_of_basic",
      "rate": 0.10,
      "max_bonus": 500000
    }
    ```
*   **How the engine reads it:** The `RulesEngine` interprets this JSONB to execute client-specific rules. It evaluates `trigger_condition` and then applies `calculation_method` and `rate` or `value` to determine the outcome.
*   **How it affects calculation flow:** Adds custom gross components or deductions based on client-defined logic. These rules are typically applied after statutory rules or as part of gross pay calculation, depending on their `rule_type`.
*   **A real payroll example showing it in action:** A client defines a `PayrollRule` for a "Sales Bonus." During a `PAYROLL_RUN`, the `PayrollProcessingService` checks if an employee meets the `trigger_condition` (e.g., sales target achieved). If so, the `RulesEngine` calculates the bonus (e.g., 10% of basic salary) based on the `calculation_method` and adds it to the employee's gross pay.
*   **What business flexibility it enables:** Empowers clients to implement highly specific compensation policies. Reduces the need for custom code development for each client, accelerating onboarding and feature delivery.
*   **What risks it introduces:** Poorly defined or conflicting custom rules can lead to incorrect payroll. Requires strong JSON Schema validation and a clear understanding of rule execution order and dependencies. The `schema_version` is crucial for engine compatibility.

### Field: `PAYROLL_RUN.rules_context_snapshot`
*   **Why JSONB was used instead of normalized tables:** To create an immutable, self-contained record of all rules (statutory and custom) that were active and used for a specific `PAYROLL_RUN`. This is critical for compliance and replayability.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "statutory_rules_snapshot": [
        {
          "statutory_rule_id": "sr123456-7890-abcd-ef12-345678abcdef",
          "version_number": 1,
          "effective_from": "2026-01-01",
          "calculation_logic_jsonb": { ... full JSON of the rule ... },
          "tax_bands_snapshot": [
            { "tax_band_id": "tb1", "lower_bound": 0, "rate": 0.07, ... },
            { "tax_band_id": "tb2", "lower_bound": 300001, "rate": 0.11, ... }
          ]
        }
      ],
      "payroll_rules_snapshot": [
        {
          "rule_id": "pr123456-7890-abcd-ef12-345678abcdef",
          "version_number": 1,
          "rule_definition_json": { ... full JSON of the rule ... }
        }
      ],
      "salary_definitions_snapshot": [
        {
          "salary_definition_id": "sd123456-7890-abcd-ef12-345678abcdef",
          "version_number": 1,
          "components_jsonb": [ { ... full JSON of components ... } ]
        }
      ]
    }
    ```
*   **How the engine reads it:** When a `PAYROLL_RUN` is initiated, the `PayrollProcessingService` populates this field by taking a snapshot of all relevant `STATUTORY_RULE`s, `TAX_BAND`s, `PayrollRule`s, and `SALARY_DEFINITION`s active for the `pay_date`. During calculation, the `RulesEngine` primarily refers to this snapshot for rule application, ensuring consistency.
*   **How it affects calculation flow:** This snapshot guarantees that all employees within a single `PAYROLL_RUN` are calculated using the exact same set of rules, even if the global rules change mid-month. It provides the immutable context for the entire run.
*   **A real payroll example showing it in action:** A `PAYROLL_RUN` for January 2026 is initiated. The system takes a snapshot of all rules effective on January 1, 2026, and stores them in `rules_context_snapshot`. Even if a new tax law comes into effect on January 15, 2026, this `PAYROLL_RUN` will continue to use the January 1st rules, ensuring compliance and preventing recalculation issues.
*   **What business flexibility it enables:** Critical for compliance and auditability. Allows for rule changes without impacting in-progress or historical payroll runs. Enables precise historical replay of calculations.
*   **What risks it introduces:** Can lead to large JSONB objects if many rules are snapshotted. Requires careful management of the snapshotting process to ensure all relevant rules are captured correctly.

### Field: `PAYROLL_RESULT.gross_components_jsonb`
*   **Why JSONB was used instead of normalized tables:** To store the detailed breakdown of an employee's gross pay components in a flexible, self-contained format. This allows for varying numbers and types of components per employee/client without schema changes.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "Basic Salary": 500000.00,
      "Housing Allowance": 250000.00,
      "Transport Allowance": 50000.00,
      "Meal Allowance": 20000.00,
      "Performance Bonus": 0.00
    }
    ```
*   **How the engine reads it:** Populated by the `PayrollProcessingService` after calculating all gross components based on the `SALARY_DEFINITION` and `PayrollRule`s. It is primarily read for reporting and payslip generation.
*   **How it affects calculation flow:** It is the output of the gross calculation phase and an input for the deduction phase (e.g., for calculating taxable income).
*   **A real payroll example showing it in action:** After calculating an employee's Basic, Housing, Transport, and Meal allowances, these values are stored in this JSONB field. The sum of these values contributes to the `total_gross_pay` in `PAYROLL_RUN`.
*   **What business flexibility it enables:** Supports diverse and evolving gross pay structures across clients. Simplifies payslip generation by providing all gross details in one place.
*   **What risks it introduces:** Requires consistent naming conventions for components to enable aggregation across employees/clients. Lack of schema validation can lead to inconsistent data.

### Field: `PAYROLL_RESULT.deductions_jsonb`
*   **Why JSONB was used instead of normalized tables:** To store the detailed breakdown of an employee's deductions (statutory and custom) in a flexible, self-contained format. This accommodates varying deductions per employee/client.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "PAYE": 75000.00,
      "Pension": 40000.00,
      "NHF": 2500.00,
      "Loan Repayment": 10000.00
    }
    ```
*   **How the engine reads it:** Populated by the `PayrollProcessingService` after calculating all deductions based on `STATUTORY_RULE`s and `PayrollRule`s. Primarily read for reporting and payslip generation.
*   **How it affects calculation flow:** It is the output of the deduction calculation phase. The sum of these values is subtracted from gross pay to arrive at net pay.
*   **A real payroll example showing it in action:** After calculating PAYE, Pension, and NHF based on statutory rules, and a loan repayment based on a custom `PayrollRule`, these values are stored in this JSONB field. The sum of these values contributes to the `total_deduction` in `PAYROLL_RUN`.
*   **What business flexibility it enables:** Supports diverse and evolving deduction structures across clients. Simplifies payslip generation by providing all deduction details in one place.
*   **What risks it introduces:** Similar to `gross_components_jsonb`, requires consistent naming and schema validation to avoid inconsistencies.

### Field: `PAYROLL_RESULT.calculations_snapshot_json`
*   **Why JSONB was used instead of normalized tables:** This is the most critical JSONB field for auditability and explainability. It stores the full, immutable trace of how every gross component and deduction was calculated, including the specific rules, inputs, and intermediate steps. It is the "why" behind the numbers.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "employee_inputs": {
        "base_salary_amount": 500000,
        "pension_contribution_rate": 0.08,
        "nhf_contribution_rate": 0.025
      },
      "calculation_steps": [
        {
          "step_name": "Calculate Basic Salary",
          "rule_id": "sd1_basic",
          "rule_version": 1,
          "inputs": {"employee_base_salary": 500000},
          "output": 500000
        },
        {
          "step_name": "Calculate Housing Allowance",
          "rule_id": "sd1_housing",
          "rule_version": 1,
          "inputs": {"basic_salary": 500000, "rate": 0.5},
          "output": 250000
        },
        {
          "step_name": "Calculate PAYE",
          "rule_id": "sr1_paye",
          "rule_version": 1,
          "inputs": {"annual_gross": 9600000, "pension": 40000, "nhf": 2500},
          "intermediate_steps": [
            {"cra_formula_applied": "MIN(200000 + 0.2 * 9600000, 0.2 * 9600000)", "cra_value": 1920000},
            {"taxable_income": 9600000 - (40000 + 2500 + 1920000), "taxable_income_value": 7637500},
            {"band_1_tax": 300000 * 0.07, "band_2_tax": (600000-300000) * 0.11, ...}
          ],
          "output": 75000
        }
      ],
      "final_net_pay": 685000.00
    }
    ```
*   **How the engine reads it:** This JSONB is primarily *written* by the `PayrollProcessingService` during the calculation. It is *read* by reporting services, audit tools, and future AI validation agents to understand the full context of a payroll result. It is not used for recalculation but for explanation.
*   **How it affects calculation flow:** It is the final, detailed output of the entire payroll calculation process for a single employee. It provides the 
complete audit trail for each individual payslip.
*   **A real payroll example showing it in action:** When an employee disputes their PAYE deduction, an auditor can retrieve the `PAYROLL_RESULT` for that employee and period. By examining `calculations_snapshot_json`, they can see the exact `STATUTORY_RULE` version used, the `TAX_BAND`s applied, the intermediate calculations (e.g., Consolidated Relief Allowance), and the final PAYE amount, providing irrefutable proof of the calculation.
*   **What business flexibility it enables:** Unprecedented auditability and explainability for every single payroll result. Allows for detailed forensic analysis without re-running calculations. Crucial for compliance and dispute resolution. Provides rich, labeled data for training future AI validation agents.
*   **What risks it introduces:** Can be a very large JSONB object, impacting storage size and potentially query performance if not indexed properly. Requires careful design of the snapshot structure to ensure all necessary details are captured without excessive verbosity.

### Field: `EventStore.event_payload`
*   **Why JSONB was used instead of normalized tables:** To store the diverse and evolving payloads of domain events. Events can have different structures depending on their `event_type`, and JSONB provides the flexibility to accommodate this without schema changes.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "employee_id": "e1234567-89ab-cdef-1234-567890abcdef",
      "payroll_run_id": "prun1234-5678-90ab-cdef-1234567890ab",
      "status": "calculated",
      "net_pay": 685000.00,
      "triggered_by": "system_admin_id"
    }
    ```
    (For `event_type: "EmployeeProcessed"`)

    ```json
    {
      "rule_id": "pr123456-7890-abcd-ef12-345678abcdef",
      "old_definition": { ... },
      "new_definition": { ... },
      "changed_by": "system_admin_id"
    }
    ```
    (For `event_type: "PayrollRuleUpdated"` - Out of Phase 1 Scope for direct population, but recorded via CDC)

*   **How the engine reads it:** In Phase 1, the `EventStore` is primarily append-only. The `PayrollProcessingService` *writes* events to it. Future services (e.g., Read Model projectors, AI agents) will *read* and interpret these payloads based on `event_type` and `aggregate_type`.
*   **How it affects calculation flow:** In Phase 1, it doesn't directly affect the calculation flow but records its progress and outcomes. It provides the raw material for reconstructing the state of a `PAYROLL_RUN` or an `EMPLOYEE` over time.
*   **A real payroll example showing it in action:** After the `PayrollProcessingService` successfully calculates an employee's pay, it emits an `EmployeeProcessed` event to the `EventStore`. This event contains the `employee_id`, `payroll_run_id`, and the `net_pay`, marking a successful step in the payroll saga.
*   **What business flexibility it enables:** Provides a granular, immutable history of all significant domain events. Enables event sourcing for rebuilding state, supports CQRS for optimized reads, and forms the backbone for future AI agent training and real-time analytics.
*   **What risks it introduces:** Requires careful design of event schemas to ensure consistency and forward compatibility. Large volumes of events can impact storage and query performance if not managed (e.g., archiving). Complex event processing logic can be challenging to implement in later phases.

### Field: `AUDIT_LOG.old_value_jsonb` / `AUDIT_LOG.new_value_jsonb`
*   **Why JSONB was used instead of normalized tables:** To capture the full state of an entity before and after a change, regardless of the entity type or its schema. This provides a flexible, comprehensive, and self-contained audit record.
*   **What structure is expected inside it (example JSON):**
    ```json
    {
      "status": "Pending",
      "employee_number": "ACME001"
    }
    ```
    (For `old_value_jsonb` when `entity_type: "EMPLOYEE"` and `action: "UPDATE"`)

    ```json
    {
      "status": "Active",
      "employee_number": "ACME001"
    }
    ```
    (For `new_value_jsonb` for the same event)

*   **How the engine reads it:** Populated by the `CDCMechanism` (Change Data Capture) which streams changes from the `RelationalDB`. It is primarily read by audit tools and compliance officers to investigate historical data modifications.
*   **How it affects calculation flow:** Does not directly affect calculation flow. It provides an independent, tamper-proof record of all data changes that *could* impact calculations, crucial for forensic analysis.
*   **A real payroll example showing it in action:** An administrator manually updates an employee's status from "Pending" to "Active" in the `EMPLOYEE` table. The `CDCMechanism` captures this change, and the `AUDIT_LOG` records the `old_value_jsonb` (status: Pending) and `new_value_jsonb` (status: Active), along with who performed the action and when.
*   **What business flexibility it enables:** Provides a complete, immutable audit trail for all data changes, essential for regulatory compliance, dispute resolution, and security forensics. Supports the 
audit-first design principle.
*   **What risks it introduces:** Can consume significant storage if not managed properly (e.g., archiving). Requires careful configuration of the `CDCMechanism` to capture the right level of detail without excessive noise.

## 3️⃣ Complete Business Rules Extraction

This section extracts and formalizes the business rules implied by the Phase 1 ERD and architecture.

### Rule Name: `Salary Structure Validation`
*   **Plain English Description:** When a salary definition is created or updated, all its components must be valid and follow a consistent structure.
*   **Formal Rule Logic:** For each `SALARY_DEFINITION` row, the `components_jsonb` must be a valid JSON array. Each object in the array must have a `component_name`, `type`, and `value_source` or `value`. If `type` is `percentage`, an `of` field must exist and reference a valid component name within the same definition.
*   **Trigger Condition:** `INSERT` or `UPDATE` on `SALARY_DEFINITION` table.
*   **Validation Logic:** The `PayrollConfigService` must validate the `components_jsonb` against a predefined JSON Schema before persisting it to the database.
*   **Example:** A `SALARY_DEFINITION` with a `Housing Allowance` component of type `percentage` but missing the `of` field would be rejected.
*   **Why it matters legally or operationally:** Ensures that salary structures are well-defined and calculable, preventing errors in gross pay calculation.
*   **What happens if violated:** Inconsistent or invalid salary structures would cause the `PayrollProcessingService` to fail, leading to incorrect payroll calculations and potential payment errors.

### Rule Name: `PAYE Calculation Logic`
*   **Plain English Description:** Pay As You Earn (PAYE) tax must be calculated based on the employee's taxable income, applying the progressive tax bands defined by the active statutory rule.
*   **Formal Rule Logic:** `PAYE = (Taxable_Income - Band_Lower_Bound) * Band_Rate` for each applicable tax band. `Taxable_Income = Annual_Gross_Income - (Pension_Deduction + NHF_Deduction + Consolidated_Relief_Allowance)`. `Consolidated_Relief_Allowance = MIN(200000 + 0.2 * Annual_Gross_Income, 0.2 * Annual_Gross_Income)`.
*   **Trigger Condition:** During a `PAYROLL_RUN`, for each employee, after gross pay and pension/NHF deductions are calculated.
*   **Validation Logic:** The `RulesEngine` must find an active `STATUTORY_RULE` of type `PAYE_CALCULATION` for the `pay_date`. It must also find the corresponding `TAX_BAND`s. If any are missing, the calculation fails.
*   **Example:** An employee with an annual gross of ₦9,600,000 would have a CRA of ₦1,920,000. If their pension and NHF are ₦40,000 and ₦2,500 respectively, their taxable income would be ₦7,637,500. The PAYE would then be calculated by applying the progressive tax rates from the `TAX_BAND` table to this amount.
*   **Why it matters legally or operationally:** This is a fundamental legal requirement for payroll in Nigeria. Failure to calculate PAYE correctly leads to non-compliance, penalties, and legal issues.
*   **What happens if violated:** Incorrect tax deductions, leading to underpayment or overpayment of taxes, resulting in financial penalties and employee dissatisfaction.

### Rule Name: `Pension Deduction Rules`
*   **Plain English Description:** A mandatory pension contribution must be deducted from the employee's salary, calculated as a percentage of their pensionable earnings.
*   **Formal Rule Logic:** `Pension_Deduction = Pensionable_Earnings * Pension_Rate`. `Pensionable_Earnings` is the sum of all components in `SALARY_DEFINITION.components_jsonb` where `is_pensionable` is `true`. The `Pension_Rate` is defined in a `STATUTORY_RULE` of type `PENSION_CALCULATION`.
*   **Trigger Condition:** During a `PAYROLL_RUN`, for each employee, after gross pay components are calculated.
*   **Validation Logic:** The `RulesEngine` must find an active `STATUTORY_RULE` of type `PENSION_CALCULATION` for the `pay_date`. The `Pensionable_Earnings` must be greater than zero.
*   **Example:** If an employee's pensionable earnings (e.g., Basic + Housing) are ₦750,000 and the statutory pension rate is 8%, the pension deduction would be ₦60,000.
*   **Why it matters legally or operationally:** This is a mandatory legal requirement in Nigeria. Failure to deduct and remit pension contributions is a serious compliance violation.
*   **What happens if violated:** Legal penalties, employee disputes, and failure to meet statutory obligations.

### Rule Name: `Tax Thresholds`
*   **Plain English Description:** Tax calculations must respect the income thresholds defined in the `TAX_BAND` table. Each portion of income should be taxed at the rate corresponding to its band.
*   **Formal Rule Logic:** For a given `Taxable_Income`, the `RulesEngine` must iterate through the `TAX_BAND`s in ascending `band_order`. For each band, it calculates the tax on the portion of income that falls within that band's `lower_bound` and `upper_bound`.
*   **Trigger Condition:** During the PAYE calculation step within a `PAYROLL_RUN`.
*   **Validation Logic:** The `TAX_BAND`s for a given `STATUTORY_RULE` must be contiguous and non-overlapping. The `upper_bound` of one band must equal the `lower_bound` of the next.
*   **Example:** If the first tax band is 0-300,000 at 7%, and the second is 300,001-600,000 at 11%, an income of 400,000 would be taxed as (300,000 * 0.07) + ((400,000 - 300,000) * 0.11).
*   **Why it matters legally or operationally:** Correctly applying tax thresholds is fundamental to progressive tax calculation and legal compliance.
*   **What happens if violated:** Incorrect tax calculations, leading to non-compliance and financial penalties.

### Rule Name: `Component Dependencies`
*   **Plain English Description:** A salary component that is calculated as a percentage of another component must have its dependency correctly defined and calculated first.
*   **Formal Rule Logic:** In `SALARY_DEFINITION.components_jsonb`, if a component has `type: "percentage"`, its `of` field must reference another component's `component_name` within the same JSONB. The `RulesEngine` must process components in an order that respects these dependencies (e.g., using a topological sort).
*   **Trigger Condition:** During the gross pay calculation step within a `PAYROLL_RUN`.
*   **Validation Logic:** When a `SALARY_DEFINITION` is created, the system must validate that all `of` references are valid and that there are no circular dependencies.
*   **Example:** If `Housing Allowance` is 50% of `Basic Salary`, the `RulesEngine` must calculate `Basic Salary` before it can calculate `Housing Allowance`.
*   **Why it matters legally or operationally:** Ensures that gross pay is calculated correctly and consistently, preventing errors in subsequent deduction calculations.
*   **What happens if violated:** Incorrect gross pay calculation, leading to incorrect net pay and compliance issues.

### Rule Name: `Audit Logging Requirements`
*   **Plain English Description:** All changes to critical data entities must be recorded in an immutable audit log.
*   **Formal Rule Logic:** Any `INSERT`, `UPDATE`, or `DELETE` operation on tables such as `EMPLOYEE`, `SALARY_DEFINITION`, `STATUTORY_RULE`, `PayrollRule`, and `PAYROLL_RUN` must result in a corresponding entry in the `AUDIT_LOG` table. This entry must capture the old and new values, the user who performed the action, and the timestamp.
*   **Trigger Condition:** Any CUD operation on designated auditable tables.
*   **Validation Logic:** The `CDCMechanism` must be configured to monitor the transaction logs of the `RelationalDB` and stream changes to the `AuditLogStore`.
*   **Example:** An administrator updates an employee's status. The `CDCMechanism` captures this change and creates an `AUDIT_LOG` entry with `entity_type: "EMPLOYEE"`, `action: "UPDATE"`, and the old and new status values in `old_value_jsonb` and `new_value_jsonb`.
*   **Why it matters legally or operationally:** Provides a tamper-proof record of all significant changes, essential for security, compliance, dispute resolution, and forensic analysis.
*   **What happens if violated:** The system would lack accountability, making it impossible to trace changes, resolve disputes, or meet regulatory requirements.

### Rule Name: `Data Immutability Rules`
*   **Plain English Description:** Once a payroll run is finalized, its results are immutable and cannot be changed. The same applies to the events in the `EventStore` and the logs in the `AUDIT_LOG`.
*   **Formal Rule Logic:** The `PAYROLL_RESULT` table should not allow `UPDATE` operations after a `PAYROLL_RUN` reaches a `LOCKED` status. The `EventStore` and `AUDIT_LOG` tables should only allow `INSERT` operations (append-only).
*   **Trigger Condition:** Any attempt to `UPDATE` or `DELETE` records in `PAYROLL_RESULT`, `EventStore`, or `AUDIT_LOG`.
*   **Validation Logic:** Database constraints and application logic should prevent modification of immutable records.
*   **Example:** An attempt to update a `PAYROLL_RESULT` for a `LOCKED` payroll run would be rejected by the application or database.
*   **Why it matters legally or operationally:** Ensures the integrity and historical accuracy of payroll records, crucial for compliance and auditability.
*   **What happens if violated:** Loss of data integrity, compromised audit trail, and potential for fraudulent activity.

### Rule Name: `Payroll Locking Rules`
*   **Plain English Description:** A payroll run must be calculated using a consistent set of rules, locked at the time of initiation.
*   **Formal Rule Logic:** When a `PAYROLL_RUN` is created, the `PayrollProcessingService` must take a snapshot of all active `STATUTORY_RULE`s, `TAX_BAND`s, `PayrollRule`s, and `SALARY_DEFINITION`s and store them in the `rules_context_snapshot` JSONB field. All subsequent calculations for that run must use the rules from this snapshot.
*   **Trigger Condition:** `INSERT` on `PAYROLL_RUN` table.
*   **Validation Logic:** The `PayrollProcessingService` must ensure that the `rules_context_snapshot` is populated before starting calculations. The `RulesEngine` must be configured to read from this snapshot for the duration of the run.
*   **Example:** A payroll run for January is initiated on January 25th. The system snapshots all rules active on that date. Even if a new tax law is added on January 28th, the January payroll run will continue to use the January 25th rules, ensuring consistency.
*   **Why it matters legally or operationally:** Prevents mid-month rule changes from affecting in-progress payroll runs, ensuring compliance and consistency. Provides a clear, auditable record of which rules were used for a specific run.
*   **What happens if violated:** Inconsistent payroll calculations, compliance issues, and difficulty in auditing historical payroll runs.

### Rule Name: `Reporting Constraints`
*   **Plain English Description:** Payroll reports must be generated from the immutable `PAYROLL_RESULT` data, not from live or re-calculated data.
*   **Formal Rule Logic:** Any service that generates reports (e.g., payslips, payroll summaries) must query the `PAYROLL_RESULT` table and use the data stored within it, including the `gross_components_jsonb`, `deductions_jsonb`, and `net_pay`.
*   **Trigger Condition:** When a user requests a payroll report or payslip.
*   **Validation Logic:** The reporting service should not have direct access to the `RulesEngine` for recalculation. It should only read from the `PAYROLL_RESULT` table.
*   **Example:** A user requests a payslip for an employee from a previous month. The reporting service retrieves the corresponding `PAYROLL_RESULT` record and uses its data to render the payslip PDF.
*   **Why it matters legally or operationally:** Ensures that reports always reflect the actual, finalized payroll data, maintaining consistency and historical accuracy.
*   **What happens if violated:** Reports could show different figures from what was actually paid, leading to confusion, disputes, and compliance issues.

## 4️⃣ Phase 1 Business Process Workflows

This section documents the end-to-end business process workflows for Phase 1, detailing the actors, triggers, steps, and outcomes.

### Business Process 1: Workspace Setup & Configuration
*   **Actors involved:** System Administrator.
*   **Trigger event:** Onboarding of the first client.
*   **Step-by-step process:**
    1.  **Create Account:** The System Administrator manually inserts a new record into the `Account` table to represent the payroll bureau.
    2.  **Create Workspace:** The System Administrator manually inserts a new record into the `WORKSPACE` table, linking it to the newly created `Account`, to represent the first client.
    3.  **Define Statutory Rules:** The System Administrator manually inserts records into the `STATUTORY_RULE` and `TAX_BAND` tables for Nigerian federal compliance (PAYE, Pension, NHF) via JSON ingestion scripts.
    4.  **Define Salary Structure:** The System Administrator manually inserts a record into the `SALARY_DEFINITION` table for the client's salary structure via a JSON ingestion script.
    5.  **Define Custom Rules:** The System Administrator manually inserts records into the `PayrollRule` table for any client-specific allowances or deductions via JSON ingestion scripts.
*   **Tables touched at each step:** `Account`, `WORKSPACE`, `STATUTORY_RULE`, `TAX_BAND`, `SALARY_DEFINITION`, `PayrollRule`.
*   **Validation checks:** JSON Schema validation for all ingested rule and definition files.
*   **Error states:** Invalid JSON format, missing required fields, database connection errors.
*   **Audit records created:** The `CDCMechanism` captures all `INSERT` operations and creates corresponding entries in the `AUDIT_LOG` table.
*   **Final outputs generated:** A fully configured `WORKSPACE` ready for employee onboarding and payroll processing.
*   **Example:** The System Administrator creates an `Account` for "Payroll Bureau Inc." and a `WORKSPACE` for "Acme Corp Nigeria." They then run scripts to load the 2026 Nigerian tax bands and Acme Corp's standard salary definition from JSON files.

### Business Process 2: Employee Onboarding / Management
*   **Actors involved:** System Administrator.
*   **Trigger event:** Receiving a list of employees for the client.
*   **Step-by-step process:**
    1.  **Prepare Employee Data:** The System Administrator prepares a JSON file containing the master data for all employees, including personal details, employee number, and status.
    2.  **Ingest Employee Data:** The System Administrator runs a script that parses the JSON file and inserts new records into the `EMPLOYEE` table, linking them to the client's `WORKSPACE`.
    3.  **Update Employee Data (if needed):** For any changes, the System Administrator prepares a JSON file with the updated data and runs a script that updates the corresponding records in the `EMPLOYEE` table.
*   **Tables touched at each step:** `EMPLOYEE`.
*   **Validation checks:** JSON Schema validation for the employee data file. Check for duplicate employee numbers within the same `WORKSPACE`.
*   **Error states:** Invalid JSON format, missing required fields, duplicate employee numbers.
*   **Audit records created:** The `CDCMechanism` captures all `INSERT` and `UPDATE` operations on the `EMPLOYEE` table and creates corresponding entries in the `AUDIT_LOG` table.
*   **Final outputs generated:** The `EMPLOYEE` table is populated with the client's employee data, ready for payroll processing.
*   **Example:** The System Administrator receives a JSON file with 50 employees for Acme Corp Nigeria. They run an ingestion script that populates the `EMPLOYEE` table with these 50 records.

### Business Process 3: Payroll Calculation & Processing (Monthly)
*   **Actors involved:** System Administrator (via API trigger).
*   **Trigger event:** The start of the monthly payroll processing cycle.
*   **Step-by-step process:**
    1.  **Initiate Payroll Run:** The System Administrator makes an API call to the `PayrollProcessingService` to initiate a new `PAYROLL_RUN` for the client's `WORKSPACE`, specifying the `period_start`, `period_end`, and `pay_date`.
    2.  **Lock Rules Context:** The `PayrollProcessingService` creates a new `PAYROLL_RUN` record and immediately populates the `rules_context_snapshot` by taking a snapshot of all active `STATUTORY_RULE`s, `TAX_BAND`s, `PayrollRule`s, and `SALARY_DEFINITION`s.
    3.  **Process Employees:** The `PayrollProcessingService` retrieves all "Active" employees for the `WORKSPACE`.
    4.  **For each employee:**
        a.  **Calculate Gross Pay:** The `RulesEngine` reads the `SALARY_DEFINITION` from the `rules_context_snapshot` and calculates all gross pay components.
        b.  **Calculate Deductions:** The `RulesEngine` reads the `STATUTORY_RULE`s and `PayrollRule`s from the `rules_context_snapshot` and calculates all deductions (PAYE, Pension, NHF, etc.).
        c.  **Calculate Net Pay:** The service calculates `Net_Pay = Gross_Pay - Deductions`.
        d.  **Create Payroll Result:** The service creates a new `PAYROLL_RESULT` record for the employee, populating `gross_components_jsonb`, `deductions_jsonb`, `net_pay`, and the detailed `calculations_snapshot_json`.
        e.  **Emit Event:** The service emits an `EmployeeProcessed` event to the `EventStore`.
    5.  **Update Payroll Run Status:** After all employees are processed, the `PayrollProcessingService` updates the `PAYROLL_RUN` status to `CALCULATED` and aggregates the totals (`total_gross_pay`, `total_deduction`, `total_net_pay`).
*   **Tables touched at each step:** `PAYROLL_RUN`, `EMPLOYEE`, `SALARY_DEFINITION`, `STATUTORY_RULE`, `TAX_BAND`, `PayrollRule`, `PAYROLL_RESULT`, `EventStore`.
*   **Validation checks:** Ensure `PAYROLL_RUN` is in a valid state to start. Ensure all required rules and definitions are present in the `rules_context_snapshot`.
*   **Error states:** Missing rules, invalid employee data, calculation errors. The run would be marked as `FAILED`.
*   **Audit records created:** The `CDCMechanism` captures the creation and updates of the `PAYROLL_RUN` and `PAYROLL_RESULT` records. The `EventStore` captures the `EmployeeProcessed` events.
*   **Final outputs generated:** A `PAYROLL_RUN` with status `CALCULATED` and a complete set of `PAYROLL_RESULT` records for all employees.
*   **Example:** The System Administrator triggers the January 2026 payroll for Acme Corp Nigeria. The system locks the rules, processes all 50 employees, and generates 50 `PAYROLL_RESULT` records. The `PAYROLL_RUN` is then marked as `CALCULATED`.

### Business Process 4: Payslip Generation & Distribution
*   **Actors involved:** System Administrator.
*   **Trigger event:** After a `PAYROLL_RUN` is successfully `CALCULATED`.
*   **Step-by-step process:**
    1.  **Retrieve Payroll Results:** The System Administrator makes an API call to a reporting service (or directly to the `PayrollProcessingService` in Phase 1) to retrieve all `PAYROLL_RESULT` records for a given `PAYROLL_RUN`.
    2.  **Render Payslips:** The reporting service (or an external tool) uses the data from each `PAYROLL_RESULT` (including `gross_components_jsonb`, `deductions_jsonb`, and `net_pay`) to render payslips in a human-readable format (e.g., PDF).
    3.  **Distribute Payslips:** The System Administrator manually distributes the generated payslip files to the client.
*   **Tables touched at each step:** `PAYROLL_RESULT` (read-only).
*   **Validation checks:** Ensure the `PAYROLL_RUN` is in a `CALCULATED` or `LOCKED` state.
*   **Error states:** `PAYROLL_RUN` not found or not in a valid state.
*   **Audit records created:** None (this is a read-only process).
*   **Final outputs generated:** Payslip documents (e.g., PDFs) for each employee.
*   **Example:** After the January 2026 payroll for Acme Corp Nigeria is calculated, the System Administrator makes an API call to retrieve the 50 `PAYROLL_RESULT`s. They use a script to generate 50 PDF payslips and email them to the client's HR manager.

### Business Process 5: Compliance Reporting (LIRS + Federal)
*   **Actors involved:** System Administrator.
*   **Trigger event:** After a `PAYROLL_RUN` is successfully `CALCULATED` and verified.
*   **Step-by-step process:**
    1.  **Aggregate Data:** The System Administrator runs a script that queries the `PAYROLL_RESULT` table for a given period to aggregate the necessary data for compliance reports (e.g., total PAYE deducted, total pension contributions).
    2.  **Generate Report Files:** The script formats the aggregated data into the required file format for submission to tax authorities (e.g., CSV, XML).
    3.  **Manual Submission:** The System Administrator manually uploads the generated report files to the relevant government portals (e.g., LIRS for Lagos State, Federal tax portal).
*   **Tables touched at each step:** `PAYROLL_RESULT` (read-only).
*   **Validation checks:** Ensure the `PAYROLL_RUN` is in a `CALCULATED` or `LOCKED` state.
*   **Error states:** `PAYROLL_RUN` not found or not in a valid state.
*   **Audit records created:** None (this is a read-only process).
*   **Final outputs generated:** Compliance report files (e.g., CSV, XML).
*   **Example:** After the January 2026 payroll is finalized, the System Administrator runs a script to generate a CSV file with the total PAYE deductions for all employees. They then manually upload this file to the LIRS portal.

### Workflow 7: Audit Retrieval
*   **Actors involved:** System Administrator, Auditor.
*   **Trigger event:** A request to investigate a data change or a payroll result.
*   **Step-by-step process:**
    1.  **Query Audit Log:** The System Administrator queries the `AUDIT_LOG` table to find specific changes. They can filter by `entity_type`, `entity_id`, `action`, or `performed_at`.
    2.  **Review Changes:** The administrator reviews the `old_value_jsonb` and `new_value_jsonb` to understand what was changed.
    3.  **Query Payroll Result:** For a payroll dispute, the administrator queries the `PAYROLL_RESULT` table for the specific employee and period.
    4.  **Analyze Calculation Snapshot:** The administrator examines the `calculations_snapshot_json` to understand the exact rules, inputs, and steps used in the calculation.
*   **Tables touched at each step:** `AUDIT_LOG` (read-only), `PAYROLL_RESULT` (read-only).
*   **Validation checks:** Ensure the user has the necessary permissions to access audit data.
*   **Error states:** User not authorized, log not found.
*   **Audit records created:** None (this is a read-only process).
*   **Final outputs generated:** A clear explanation of a data change or a payroll calculation, supported by immutable log data.
*   **Example:** An auditor asks why an employee's net pay changed in January. The administrator queries the `AUDIT_LOG` to see if their salary was updated. They then query the `PAYROLL_RESULT` and analyze the `calculations_snapshot_json` to show the exact tax bands and deductions applied.

## 5️⃣ Business Rules & Validation

This section is a placeholder as the detailed business rules have been extracted and documented in Section 3.

## 6️⃣ Data Lifecycle & State Transitions

This section explains the lifecycle of a `PAYROLL_RUN` and the mechanisms that enforce data immutability.

*   **State Transitions:** The `status` field in the `PAYROLL_RUN` table tracks the lifecycle of a payroll run. The expected state transitions are:
    *   `DRAFT` → `CALCULATING` → `CALCULATED` → `APPROVED` → `LOCKED`
    *   `CALCULATING` → `FAILED`
*   **What table tracks state:** The `PAYROLL_RUN` table, specifically the `status` column.
*   **What enforces immutability:**
    *   **`PAYROLL_RESULT`:** Application logic should prevent any `UPDATE` or `DELETE` operations on this table. Once created, it is immutable.
    *   **`EventStore` & `AUDIT_LOG`:** These tables are append-only by design. Application logic should only allow `INSERT` operations.
    *   **`rules_context_snapshot`:** This JSONB field in `PAYROLL_RUN` ensures that the rules used for a run are immutable once the run is initiated.
*   **What prevents recalculation after lock:** The application logic in the `PayrollProcessingService` should check the `status` of a `PAYROLL_RUN`. If the status is `LOCKED`, any API call to recalculate the run should be rejected.
*   **How corrections are handled in Phase 1:** Corrections are handled by creating a new, separate "Correction Run." The incorrect `PAYROLL_RUN` is marked as `VOID` or `ARCHIVED`, but its records are not deleted. A new `PAYROLL_RUN` is created for the same period, which will generate a new set of `PAYROLL_RESULT`s. This ensures that the audit trail remains intact and all changes are explicitly recorded.

## 7️⃣ System Interactions & Dependencies

### Database Interactions
*   All services interact with the `RelationalDB` (PostgreSQL) for their primary data storage and retrieval.
*   The `PayrollProcessingService` writes to the `EventStore` (append-only).
*   The `CDCMechanism` reads from the `RelationalDB`'s transaction log and writes to the `AuditLogStore`.

### External Integrations
*   **Out of Phase 1 Scope:** There are no external integrations in Phase 1. All data is ingested manually via JSON files, and all reports are generated for manual submission.

## 7️⃣ Exception Handling

*   **Calculation Errors:** If the `RulesEngine` encounters an error during calculation (e.g., missing rule, invalid data), it should fail the processing for that specific employee and log the error. The `PAYROLL_RUN` status would be set to `FAILED`.
*   **Data Validation Errors:** The JSON ingestion scripts must have robust error handling to report invalid data formats or missing fields, preventing corrupt data from entering the system.
*   **Database Errors:** Standard database transaction management (commit/rollback) should be used to ensure data consistency, especially during the multi-step payroll processing.

## 7️⃣ Architectural Justifications

*   **Why event-driven?** To create a decoupled, scalable, and auditable system. In Phase 1, it's primarily for recording events (append-only `EventStore`), laying the foundation for future asynchronous processing, CQRS, and AI agent integration.
*   **Why rule engine over hardcoded logic?** To enable flexibility and agility. It allows payroll rules to be managed as data, enabling rapid updates for compliance and client-specific needs without code deployments. This is crucial for a multi-tenant payroll bureau.
*   **Why Maker-Critic pattern?** (Out of Phase 1 Scope) This is a future governance mechanism to ensure accuracy and prevent errors in critical rule changes. It is not implemented in Phase 1.
*   **Why JSON-based rule storage?** To provide a flexible, schema-less way to define complex and varied payroll logic. It allows for rich, structured data to be stored as metadata, which is essential for the `RulesEngine` and for supporting diverse client requirements.
*   **Why audit-first design?** Because payroll is a high-stakes financial system, auditability and compliance are non-negotiable. By implementing CDC and an immutable `AUDIT_LOG` from day one, we ensure that every change is tracked, providing a tamper-proof record for security and dispute resolution.
*   **Why multi-tenant capable schema even in Phase 1?** To adhere to the "no throwaway code" principle. By building the schema with multi-tenancy in mind (e.g., `workspace_id` as a foreign key), we ensure that the system can scale horizontally to support multiple clients in Phase 2 without a major database redesign.

## 7️⃣ Phase 1 Boundaries

### What is implemented
*   Core backend services for payroll calculation (`PayrollProcessingService`, `RulesEngine`).
*   Manual provisioning of a single `Account` and `WORKSPACE`.
*   Manual ingestion of employee data and payroll rules via JSON files.
*   API-driven initiation of payroll runs.
*   Generation of immutable `PAYROLL_RESULT`s with detailed calculation snapshots.
*   Append-only `EventStore` for recording payroll events.
*   CDC-based `AUDIT_LOG` for tracking data changes.

### What is intentionally deferred
*   **UI:** All user interfaces for client onboarding, user management, employee management, rule configuration, and payroll run management are deferred to Phase 2.
*   **Multi-Tenancy (Operational):** While the schema is multi-tenant capable, the operational aspects of managing multiple clients are deferred. Phase 1 focuses on a single client.
*   **Advanced Payroll Features:** Approvals, hourly/shift-based pay, complex allowances, and automated reporting are deferred to Phase 3.
*   **AI/Agentic Features:** All AI-driven ingestion, validation, and processing are deferred to Phase 4.
*   **External Integrations:** All integrations with external systems (e.g., banks, tax portals, HRIS) are deferred.

### What schema elements are dormant for future phases
*   **`User` table:** Present but not actively used for authentication/authorization in Phase 1.
*   **`GRADE` & `GRADE_HISTORY` tables:** Present but not actively used for managing employee grades.
*   **`TAX_AUTHORITY` & `EMPLOYEE_TAX_ASSIGNMENT` tables:** Present but not actively used for assigning employees to specific tax authorities.
*   **`EMPLOYEE_CONTRACT` table:** Present but not actively used for managing employee contracts.

### Which tables are Phase 2 ready but Phase 1 inactive
*   The `Account` and `WORKSPACE` tables are designed for multi-tenancy but will only hold a single record each in Phase 1.
*   The `User` table is ready for multi-user management in Phase 2 but is inactive in Phase 1.

## Gap Analysis: Your Document vs. My Phase 1 Design

After reviewing your attached document, I can confirm that my proposed Phase 1 design aligns almost perfectly with your specified scope and deliverables. Here is a summary of the alignment and any minor differences:

### Alignment (What I've Considered that is Specified)

*   **Single Client, Salaried Staff, Monthly Payroll:** My Phase 1 design is explicitly scoped to this, with manual setup for the single client.
*   **Federal Compliance & Auditability:** The design includes `STATUTORY_RULE` for compliance and a CDC-based `AUDIT_LOG` from day one, matching your requirements.
*   **ERD Deconstruction, JSONB Decomposition, Business Rules Extraction, Workflows:** I have followed your mandatory format to provide a detailed breakdown of these elements as implied by the architecture.
*   **Data Lifecycle & Architectural Justifications:** I have explained the state transitions and the reasoning behind key architectural decisions as requested.
*   **Phase 1 Boundaries:** I have clearly defined what is in and out of scope for Phase 1, including dormant schema elements.

### Additional Considerations (What I've Considered that was Not Explicitly Specified)

*   **`rules_context_snapshot` in `PAYROLL_RUN`:** This is a critical feature I included to ensure payroll locking and prevent mid-month rule changes from affecting in-progress runs. This is a crucial detail for compliance and auditability that was implied but not explicitly named in your document.
*   **`EventStore` as a "Flight Recorder":** I have explicitly defined the `EventStore`'s role in Phase 1 as an append-only log, laying the groundwork for future event sourcing without the complexity of event replay in the MVP. This aligns with the "no throwaway code" principle.
*   **`personal_details_encrypted` in `EMPLOYEE`:** I have specified that the JSONB field for personal details should be encrypted, a critical security consideration for handling PII.
*   **Schema Versioning in JSONB fields:** I have included `schema_version` in `SALARY_DEFINITION` and `PayrollRule` to support future evolution of the JSON structures, a key governance mechanism.

### Deferred Items (What You Specified that is Not in Phase 1)

*   **`Business Process 5: Compliance Reporting (LIRS + Federal)`:** While my design includes the data necessary for this, I have clarified that the generation of the report files is a manual script-driven process in Phase 1, and the submission is manual. Fully automated reporting is deferred.
*   **`Workflow 7: Audit Retrieval`:** I have documented this workflow, but it's important to note that in Phase 1, this is a manual process performed by a System Administrator with direct database query access. A user-facing UI for audit retrieval is not part of the MVP.
*   **`Maker-Critic pattern`:** Your document asks for a justification of this pattern. I have clarified that this is an architectural consideration for future phases and is not implemented in Phase 1.

Overall, the alignment is very strong. My design provides a robust, compliant, and future-proof foundation for Phase 1, with the additional considerations I've highlighted serving to strengthen the architecture and mitigate future risks.
