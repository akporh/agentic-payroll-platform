# Payroll Engine Architecture — Phase 1

Five diagrams derived directly from the codebase.
No inferred or aspirational detail.

---

## 1. System Layer Architecture

```mermaid
flowchart TD
    subgraph API["API Layer  ·  FastAPI routers"]
        direction TB
        R_OB["onboarding.py\nPOST /onboarding/upload\nPOST /onboarding/preview\nPOST /onboarding/commit"]
        R_PAY["payroll.py\nPOST /payroll/run"]
        R_WS["workspace.py\nGET  /workspace/info\nPOST /{id}/transition\nPOST /{id}/pay_cycle\nPOST /{id}/grade\nPOST /{id}/designation\nPOST /{id}/salary_definition\nPOST /{id}/payroll_rule\nPOST /{id}/component_metadata"]
    end

    subgraph APP["Application Layer  ·  orchestration only"]
        direction TB
        SVC_PAY["payroll_run_service.py\nexecute_and_persist()"]
        SVC_OB["onboarding_service.py\ncreate_pay_cycle()\ncreate_grade()\ncreate_designation()\ncreate_salary_definition()\ncreate_payroll_rule()\ncreate_component_metadata()"]
        PERSISTER["payroll_run_persister.py\npersist_payroll_run_execution()"]
    end

    subgraph DOMAIN["Domain Layer  ·  pure functions, no DB access"]
        direction TB

        subgraph DOB["Onboarding"]
            LOADER["loader.py\nemit_onboarding_sql()"]
            REVIEW["review_runner.py\nreview_client_onboarding()"]
            HARD["hard_validator.py\nvalidate_client_json()"]
            AI["ai_critic.py\nreview_client_json()"]
            EMITTER["sql_emitter.py\nemit_onboarding_transaction()\nemit_employees_sql()\nemit_salary_definitions_sql()\nemit_payroll_rules_sql()"]
            WS_SM["workspace_state_machine.py\ntransition_workspace()"]
            WS_INF["state_inference.py\nauto_infer_workspace_state"]
        end

        subgraph DPAY["Payroll Execution"]
            RUN_EXEC["run_executor.py\nexecute_payroll_run_pure()"]
            BATCH["batch_processor.py\nprocess_payroll_run()"]
            SINGLE["executor.py\nexecute_single_employee_payroll()"]
            RES_B["result_builder.py\nbuild_payroll_result()"]
            GROSS["salary.py\ncalculate_gross()"]
            NET["calculator.py\ncalculate_net_pay()"]
            PAY_SM["state_machine.py\ntransition()"]
            AUD_B["audit_events.py\nbuild_transition_audit()\nbuild_transition_event()"]
        end

        subgraph DRULES["Rules"]
            PAYE["rules/paye.py\ncalculate_paye()"]
            SNAP["rules/snapshot.py\nbuild_rules_context_snapshot()"]
        end
    end

    subgraph INFRA["Infrastructure Layer  ·  DB access"]
        direction TB
        SESSION["db/session.py\nSessionLocal  ·  engine\nDATABASE_URL env var"]
        REPO_RUN["repositories/payroll_run_repo.py\nsave_payroll_run()"]
        REPO_RES["repositories/payroll_result_repo.py\nsave_payroll_result()"]
        REPO_AUD["repositories/audit_log_repo.py\nsave_audit_log()"]
        REPO_EVT["repositories/event_store_repo.py\nsave_event()"]
        REPO_WS["db/repositories/workspace_repo.py"]
    end

    subgraph DB["PostgreSQL Database"]
        direction TB
        PG[("Tables + Triggers\nsee Diagram 5")]
    end

    %% API → Application
    R_PAY  --> SVC_PAY
    R_WS   --> SVC_OB
    R_WS   --> WS_SM

    %% API → Domain (direct, no app service)
    R_OB   --> LOADER
    R_OB   --> REVIEW
    R_OB   --> SESSION

    %% Application → Domain
    SVC_PAY  --> RUN_EXEC
    SVC_PAY  --> PERSISTER
    SVC_OB   --> WS_INF

    %% Application → Infra
    PERSISTER --> REPO_RUN
    PERSISTER --> REPO_RES
    PERSISTER --> REPO_AUD
    PERSISTER --> REPO_EVT

    %% Domain Onboarding internals
    LOADER  --> REVIEW
    LOADER  --> EMITTER
    REVIEW  --> HARD
    REVIEW  --> AI

    %% Domain Payroll internals
    RUN_EXEC --> PAY_SM
    RUN_EXEC --> BATCH
    RUN_EXEC --> AUD_B
    BATCH    --> SINGLE
    SINGLE   --> RES_B
    SINGLE   --> SNAP
    RES_B    --> GROSS
    RES_B    --> NET
    NET      --> PAYE

    %% Infra → DB
    SESSION  --> PG
    REPO_RUN --> SESSION
    REPO_RES --> SESSION
    REPO_AUD --> SESSION
    REPO_EVT --> SESSION
    REPO_WS  --> SESSION
```

---

## 2. Onboarding Pipeline

```mermaid
flowchart TD
    CLIENT(["Client Request"])

    subgraph UPLOAD_FLOW["POST /onboarding/upload  —  no DB writes"]
        U1["Extract workspace_id\npayload.get('workspace_id')"]
        U2["emit_onboarding_sql(workspace_id, payload)"]
        U3["review_client_onboarding(payload)"]
        U4{"hard_validation\n== FAIL?"}
        U5["emit_onboarding_transaction()\nreturns SQL string only"]
        U6[/"Return status: BLOCKED\nreview with errors"/]
        U7[/"Return status: success\nreview + sql string"/]
    end

    subgraph HARD_VAL["Hard Validator  —  validate_client_json()  —  pure, no DB"]
        HV1{"salary_definitions\nhave BASIC + HOUSING\n+ TRANSPORT?\nAll amounts numeric?"}
        HV2{"Every payroll_rule\nmethod in\n{percentage, fixed_amount,\nper_day, statutory}?"}
        HV3{"At least one rule_code\ncontaining PENSION\nwith method=percentage?\nbase_components ⊇\n{BASIC,HOUSING,TRANSPORT}?"}
        HV4{"Every employee.biodata\ncontains TIN, BANK,\nACCOUNT_NUMBER, RSA?"}
        HV_PASS(["PASS"])
        HV_FAIL(["FAIL + errors list"])
    end

    subgraph COMMIT_FLOW["POST /onboarding/commit  —  DB writes"]
        C1["Extract workspace_id\npayload.get('workspace_id')"]
        C2["Re-run review_client_onboarding()\nnever trust preview"]
        C3{"hard_validation\n== FAIL?"}
        C4["SELECT 1 FROM workspace\nWHERE workspace_id = :wid"]
        C5{"workspace\nexists?"}
        C6["INSERT salary_definition\n(components wrapped in Json())"]
        C7["INSERT payroll_rule\n(definition wrapped in Json())"]
        C8["Derive full_name:\nemp.get('full_name')\nor biodata.FULL_NAME\nor employee_number"]
        C9["INSERT employee\n(status = ACTIVE)"]
        C10["Resolve salary_def_id\nfrom salary_def_id_map\nby salary_definition_name"]
        C11{"name\nresolved?"}
        C12["INSERT employee_contract\n(start_date = CURRENT_DATE)"]
        C13["db.commit()"]
        C_ERR[/"Return error\ndb.rollback()"/]
        C_OK[/"Return success"/]
    end

    CLIENT --> U1
    U1 --> U2
    U2 --> U3
    U3 --> HV1 --> HV2 --> HV3 --> HV4
    HV4 -->|all pass| HV_PASS
    HV1 & HV2 & HV3 & HV4 -->|any fail| HV_FAIL
    U3 --> U4
    U4 -->|yes| U6
    U4 -->|no| U5 --> U7

    CLIENT --> C1
    C1 --> C2 --> C3
    C3 -->|yes| C_ERR
    C3 -->|no| C4 --> C5
    C5 -->|no| C_ERR
    C5 -->|yes| C6 --> C7 --> C8 --> C9 --> C10 --> C11
    C11 -->|no| C_ERR
    C11 -->|yes| C12 --> C13 --> C_OK
```

---

## 3. Payroll Execution Pipeline

```mermaid
flowchart TD
    CLIENT(["POST /payroll/run\n{workspace_id}"])

    subgraph ROUTE["payroll.py  —  route handler"]
        P1["SELECT workspace — 404 if missing"]
        P2["SELECT employee + employee_contract\n+ salary_definition JOIN\nWHERE status=ACTIVE\nAND end_date IS NULL\nOR end_date >= CURRENT_DATE"]
        P3{"employees\nfound?"}
        P4["SELECT tax_band\nORDER BY lower_limit\n(empty = PAYE will be 0, no error)"]
        P5["SELECT statutory_rule\nORDER BY version DESC LIMIT 1\n— 400 if none"]
        P6["SELECT payroll_rule\nWHERE is_active=TRUE\nAND workspace_id=:workspace_id\n(empty = OK, stored as snapshot only)"]
        P7["generate payroll_run_id = uuid4()"]
    end

    subgraph APP["Application  —  execute_and_persist()"]
        A1["execute_payroll_run_pure()"]
        A2["persist_payroll_run_execution()"]
    end

    subgraph PURE["Domain  —  pure calculation, no DB"]
        direction TB
        SM1["transition(DRAFT → CALCULATING)"]
        BATCH["process_payroll_run()\nfor each employee"]

        subgraph EMP_LOOP["Per Employee  —  execute_single_employee_payroll()"]
            direction TB
            G["calculate_gross(components)\nsum all component amounts"]
            N["calculate_net_pay(gross, tax_bands)\napply progressive PAYE bands"]
            R["build_payroll_result()\ngross_components_jsonb\ndeductions_jsonb {PAYE}\nnet_pay\ncalculations_snapshot_json"]
            S["build_rules_context_snapshot()\n{statutory_rule_id, version,\npayroll_rule_ids}"]
        end

        SM2{"failure_count > 0?"}
        SM3["transition(CALCULATING → PARTIAL)"]
        SM4["transition(CALCULATING → CALCULATED)"]
        TOT["aggregate totals:\ntotal_gross_pay\ntotal_deduction\ntotal_net_pay\nsuccess_count / failure_count"]
        AUD["build_transition_audit()\nbuild_transition_event()\nfor each state change"]
    end

    subgraph PERSIST["Infrastructure  —  persist_payroll_run_execution()"]
        direction TB
        DB1["save_payroll_run()\nINSERT payroll_run\n(triggers fire here — see Diagram 4)"]
        DB2["save_payroll_result()\nINSERT per employee\n(Json() wraps all JSONB fields)"]
        DB3["save_audit_log()\nINSERT audit_log\nper state transition"]
        DB4["save_event()\nINSERT event_store\nper state transition"]
    end

    RESP[/"Return\n{status, payroll_run_id, summary{totals}}"/]

    CLIENT --> P1 --> P2 --> P3
    P3 -->|"no employees"| FAIL400(["HTTP 400"])
    P3 -->|yes| P4 --> P5 --> P6 --> P7
    P7 --> A1

    A1 --> SM1 --> BATCH
    BATCH --> G --> N --> R
    N --> S
    BATCH --> SM2
    SM2 -->|yes| SM3
    SM2 -->|no| SM4
    SM3 & SM4 --> TOT
    TOT --> AUD

    A1 --> A2
    A2 --> DB1 --> DB2 --> DB3 --> DB4

    DB4 --> RESP
```

---

## 4. State Machines

### 4a — Workspace Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DRAFT : workspace created\n(default)

    DRAFT --> STRUCTURE_DEFINED : POST /{id}/transition\nGates: pay_cycle exists\n+ grade exists\n+ designation exists

    STRUCTURE_DEFINED --> COMPENSATION_DEFINED : POST /{id}/transition\nGate: salary_definition exists

    COMPENSATION_DEFINED --> RULES_DEFINED : POST /{id}/transition\nGate: active payroll_rule exists

    RULES_DEFINED --> READY : POST /{id}/transition\nGate: component_metadata exists

    READY --> LIVE : POST /{id}/transition\n(no extra gate)

    LIVE --> [*] : terminal — no further transitions\nallowed (payroll can now run)

    note right of LIVE
        DB trigger trg_enforce_workspace_live
        blocks INSERT on payroll_run
        unless workspace.status = LIVE
    end note
```

### 4b — Payroll Run Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DRAFT : execute_payroll_run_pure()\ncalled with new payroll_run_id

    DRAFT --> CALCULATING : transition()\nbefore batch processing

    CALCULATING --> CALCULATED : transition()\nfailure_count == 0

    CALCULATING --> PARTIAL : transition()\nfailure_count > 0\n(isolated mode only;\natomic mode raises immediately)

    PARTIAL --> CALCULATED : future manual resolution\n(defined in state_machine.py,\nnot yet exposed via API)

    CALCULATED --> APPROVED : future approval step\n(defined in state_machine.py)

    APPROVED --> LOCKED : future lock step\n(defined in state_machine.py)

    LOCKED --> [*] : terminal — immutable\nMigrations enforce\nno updates after LOCKED

    note right of CALCULATED
        Status value saved on
        payroll_run.status via
        save_payroll_run() INSERT
    end note
```

---

## 5. Database Schema

```mermaid
erDiagram

    account {
        uuid account_id PK
        varchar name
        timestamp created_at
    }

    workspace {
        uuid workspace_id PK
        uuid account_id FK
        varchar name
        workspace_status status
        varchar country_code
        varchar base_currency
        varchar retry_strategy
        timestamp created_at
    }

    employee {
        uuid employee_id PK
        uuid workspace_id FK
        varchar full_name
        varchar employee_number
        varchar status
        jsonb personal_details_encrypted
        timestamp created_at
    }

    employee_contract {
        uuid contract_id PK
        uuid employee_id FK
        uuid salary_definition_id FK
        uuid designation_id FK
        date start_date
        date end_date
    }

    salary_definition {
        uuid salary_definition_id PK
        uuid workspace_id FK
        varchar name
        jsonb components_jsonb
        int schema_version
        date effective_from
        date effective_to
    }

    payroll_rule {
        uuid rule_id PK
        uuid workspace_id FK
        varchar rule_name
        jsonb rule_definition_json
        varchar rule_type
        int schema_version
        boolean is_active
        timestamp created_at
    }

    component_metadata {
        uuid component_metadata_id PK
        varchar country_code
        int version
        jsonb rules_jsonb
        date effective_from
        boolean is_active
        timestamp created_at
    }

    designation {
        uuid designation_id PK
        uuid workspace_id FK
        varchar designation_code
        varchar description
        timestamp created_at
    }

    pay_cycle {
        uuid pay_cycle_id PK
        uuid workspace_id FK
        varchar frequency
        int run_day
        int cutoff_day
        int payment_day
        boolean is_active
        timestamp created_at
    }

    statutory_rule {
        uuid statutory_rule_id PK
        varchar state
        int version
        jsonb rules_jsonb
        varchar tax_method
    }

    tax_band {
        uuid tax_band_id PK
        uuid statutory_rule_id FK
        numeric lower_limit
        numeric upper_limit
        numeric rate
    }

    payroll_run {
        uuid payroll_run_id PK
        uuid workspace_id FK
        varchar status
        date period_start
        date period_end
        date pay_date
        numeric total_gross_pay
        numeric total_deduction
        numeric total_net_pay
        json rules_context_snapshot
        timestamp created_at
    }

    payroll_result {
        uuid payroll_result_id PK
        uuid payroll_run_id FK
        uuid employee_id FK
        jsonb gross_components_jsonb
        jsonb deductions_jsonb
        numeric net_pay
        json calculations_snapshot_json
        varchar status
        text error_message
        timestamp generated_at
    }

    audit_log {
        uuid audit_log_id PK
        uuid workspace_id FK
        varchar entity_type
        uuid entity_id
        varchar action
        jsonb old_value_jsonb
        jsonb new_value_jsonb
        varchar performed_by
        timestamp performed_at
    }

    event_store {
        uuid event_id PK
        varchar aggregate_type
        uuid aggregate_id
        varchar event_type
        jsonb event_payload
        uuid workspace_id
        timestamp occurred_at
    }

    account         ||--o{ workspace         : "owns"
    workspace       ||--o{ employee          : "employs"
    workspace       ||--o{ salary_definition : "defines"
    workspace       ||--o{ payroll_rule      : "configures"
    workspace       ||--o{ designation       : "has"
    workspace       ||--o{ pay_cycle         : "has one"
    workspace       ||--o{ payroll_run       : "runs"
    workspace       ||--o{ audit_log         : "logs"
    employee        ||--o{ employee_contract : "holds"
    employee        ||--o{ payroll_result    : "receives"
    salary_definition ||--o{ employee_contract : "applied via"
    designation     ||--o{ employee_contract : "classifies"
    statutory_rule  ||--o{ tax_band          : "defines"
    payroll_run     ||--o{ payroll_result    : "produces"
```

---

## 6. DB Triggers on `payroll_run` INSERT

```mermaid
flowchart TD
    INSERT["INSERT INTO payroll_run\n(payroll_run_id, workspace_id, status)"]

    T1["TRIGGER trg_enforce_workspace_live\n(BEFORE INSERT — migration 0daab4ac893b)"]
    T2["TRIGGER trg_enforce_payroll_readiness\n(BEFORE INSERT — migration 4907cf6eb08f)"]

    T1C{"workspace.status\n= 'LIVE'?"}
    T2C["validate_payroll_readiness(\n  workspace_id,\n  period_start,\n  period_end\n)"]

    subgraph VPR["validate_payroll_readiness() checks"]
        V1["workspace.status = LIVE"]
        V2["statutory_rule row exists"]
        V3["tax_band row exists"]
        V4["component_metadata active\nfor workspace.country_code"]
        V5["salary_definition exists\nand effective for period"]
        V6["active payroll_rule exists\nfor workspace"]
        V7["all ACTIVE employees\nhave an open contract"]
        V8["contracts effective\nduring period"]
        V9["no payroll_run already\nexists for this period"]
    end

    OK(["Row inserted"])
    FAIL_T1(["EXCEPTION: workspace % is not LIVE"])
    FAIL_T2(["EXCEPTION: Payroll readiness failed: %errors%"])

    INSERT --> T1
    INSERT --> T2

    T1 --> T1C
    T1C -->|yes| OK
    T1C -->|no| FAIL_T1

    T2 --> T2C --> V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9
    V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9 -->|all pass| OK
    V1 & V2 & V3 & V4 & V5 & V6 & V7 & V8 & V9 -->|any fail| FAIL_T2
```
