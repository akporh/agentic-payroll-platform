# Phase 1: Visual Architecture for Nigerian Payroll Platform MVP

This document provides the Entity Relationship Diagram (ERD) and the High-Level Architectural Diagram specifically tailored for Phase 1 of the payroll platform roadmap. These diagrams highlight the minimal viable product (MVP) scope, focusing on a single client, manual JSON ingestion, and foundational backend services.

## 1. Phase 1 Entity Relationship Diagram (ERD)

The Phase 1 ERD illustrates the core entities required for the initial MVP. It emphasizes the manual provisioning of `Account` and `WORKSPACE` and the direct population of `EMPLOYEE`, `SALARY_DEFINITION`, `STATUTORY_RULE`, `TAX_BAND`, and `PayrollRule` via JSON. The `PAYROLL_RUN` includes the `rules_context_snapshot` for compliance, and `PAYROLL_RESULT` captures the immutable calculation breakdown. The `EventStore` is present as an append-only log, and `AUDIT_LOG` captures changes via CDC.

```mermaid
erDiagram
    direction TB

    Account {
        UUID account_id PK "Manually Provisioned"
        VARCHAR name
    }

    WORKSPACE {
        UUID workspace_id PK "Manually Provisioned"
        UUID account_id FK
        VARCHAR name
        VARCHAR country_code
    }

    EMPLOYEE {
        UUID employee_id PK
        UUID workspace_id FK
        VARCHAR employee_number
        VARCHAR status
        JSONB personal_details_encrypted
    }

    SALARY_DEFINITION {
        UUID salary_definition_id PK
        UUID workspace_id FK
        VARCHAR name
        JSONB components_jsonb
        INTEGER schema_version
        DATE effective_from
        DATE effective_to
    }

    STATUTORY_RULE {
        UUID statutory_rule_id PK
        VARCHAR country_code
        VARCHAR rule_type
        JSONB calculation_logic_jsonb
        DATE effective_from
        DATE effective_to
        INTEGER version_number
    }

    TAX_BAND {
        UUID tax_band_id PK
        UUID statutory_rule_id FK
        INTEGER band_order
        DECIMAL lower_bound
        DECIMAL upper_bound
        DECIMAL rate
        DATE effective_from
        DATE effective_to
    }

    PayrollRule {
        UUID rule_id PK
        UUID workspace_id FK
        VARCHAR rule_name
        VARCHAR rule_type
        JSONB rule_definition_json
        INTEGER schema_version
        BOOLEAN is_active
    }

    PAYROLL_RUN {
        UUID payroll_run_id PK
        UUID workspace_id FK
        DATE period_start
        DATE period_end
        DATE pay_date
        DECIMAL total_gross_pay
        DECIMAL total_deduction
        DECIMAL total_net_pay
        VARCHAR status
        JSONB rules_context_snapshot "Snapshot of rules active at run initiation"
    }

    PAYROLL_RESULT {
        UUID payroll_result_id PK
        UUID payroll_run_id FK
        UUID employee_id FK
        JSONB gross_components_jsonb
        JSONB deductions_jsonb
        DECIMAL net_pay
        JSONB calculations_snapshot_json "Immutable JSON of full calculation breakdown and inputs"
    }

    AUDIT_LOG {
        UUID audit_log_id PK
        UUID workspace_id FK
        VARCHAR entity_type
        UUID entity_id
        VARCHAR action
        JSONB old_value_jsonb
        JSONB new_value_jsonb
        VARCHAR performed_by
        TIMESTAMP performed_at
    }

    EventStore {
        UUID event_id PK
        UUID workspace_id FK
        UUID aggregate_id
        VARCHAR aggregate_type
        VARCHAR event_type
        JSONB event_payload
        TIMESTAMP occurred_at
    }

    Account ||--o{ WORKSPACE : "owns"
    WORKSPACE ||--o{ EMPLOYEE : "owns"
    WORKSPACE ||--o{ SALARY_DEFINITION : "defines"
    WORKSPACE ||--o{ PayrollRule : "defines"
    WORKSPACE ||--o{ PAYROLL_RUN : "executes"
    WORKSPACE ||--o{ AUDIT_LOG : "records"
    PAYROLL_RUN ||--o{ PAYROLL_RESULT : "produces"
    PAYROLL_RUN ||--o{ EventStore : "emits (append-only)"
    STATUTORY_RULE ||--o{ TAX_BAND : "contains"
    EMPLOYEE ||--o{ PAYROLL_RESULT : "receives"
```

## 2. Phase 1 High-Level Architectural Diagram

This diagram illustrates the streamlined architecture for the MVP. It focuses on the core backend services, manual data input, and the foundational data stores. The Event Bus and advanced microservices are intentionally omitted or simplified to reflect the initial scope.

```mermaid
graph LR
    subgraph CloudProvider["Cloud Provider"]
        subgraph PresentationLayer["Presentation Layer (Minimal/None)"]
            ManualJSONInput["Manual JSON Input (Files)"]
            APITrigger["API Trigger (for Payroll Run)"]
        end

        subgraph ApplicationLayer["Application Layer (Core Services)"]
            APIGateway("API Gateway")
            PayrollProcessingService("Payroll Processing Service")
            PayrollConfigService("Payroll Config Service")
            EmployeeHRService("Employee & HR Service")
            RulesEngine["Rules Engine"]
        end

        subgraph DataLayer["Data Layer"]
            RelationalDB[("PostgreSQL (All Entities)")]
            EventStore[("Event Store (Append-Only)")]
            AuditLogStore[("Audit Log Store (via CDC)")]
        end

        subgraph Infrastructure["Infrastructure & Operations"]
            CDCMechanism["CDC Mechanism (e.g., Debezium)"]
        end
    end

    ManualJSONInput --> APIGateway
    APITrigger --> APIGateway

    APIGateway --> PayrollProcessingService
    APIGateway --> PayrollConfigService
    APIGateway --> EmployeeHRService

    PayrollProcessingService --> EmployeeHRService
    PayrollProcessingService --> PayrollConfigService
    PayrollProcessingService --> RulesEngine
    PayrollProcessingService --> RelationalDB
    PayrollProcessingService -- "Emits Events" --> EventStore

    PayrollConfigService --> RelationalDB
    EmployeeHRService --> RelationalDB

    RulesEngine --> RelationalDB

    RelationalDB --> CDCMechanism
    CDCMechanism -- "Streams Changes" --> AuditLogStore
```
