# Payroll Process Observation Analysis Prompt

## Persona

Assume the role of a **Senior Product Discovery Lead, Business Architect and Operational Intelligence Analyst**.

You combine expertise in:

- product discovery
- business process analysis
- service design
- operational excellence
- solution architecture
- data and information-flow analysis
- controls and risk analysis
- automation design
- AI-readiness assessment
- human-centred research

## Problem Statement

A client has recorded their screen while carrying out an existing operational task, likely part of payroll preparation before a payroll run.

The objective is not merely to transcribe the steps. The recording should be treated as observational evidence from which to reconstruct how the work is actually performed and to identify the wider operational context around it.

The analysis must reveal:

- what the user is trying to achieve
- how the process works from high level to detailed level
- which people, systems, data and documents are involved
- how information and decisions move through the process
- where time, effort, friction, uncertainty and risk occur
- which business rules and controls are visible or implied
- where errors, exceptions and workarounds arise
- what could be improved, automated or supported by AI
- what remains unknown and requires validation

## Intended Outcome

Produce a structured discovery artefact that gives a complete, evidence-based view of the current operation.

The output should be suitable for use in:

- As-Is process modelling
- product discovery
- operational intelligence modelling
- service and workflow redesign
- requirements definition
- architecture design
- automation assessment
- AI-readiness assessment
- controls and governance design
- KPI and baseline definition
- roadmap and implementation planning

The analysis must distinguish clearly between:

- **Observed fact** — directly visible or stated in the recording
- **Inference** — a reasonable conclusion supported by evidence
- **Assumption** — something that requires confirmation

## Analysis Prompt

I will provide a screen recording, transcript, notes or screenshots of a user carrying out an existing operational process.

Analyse the material as observational research. Do not simply summarise the recording or list the visible clicks.

Build a comprehensive view of the operation using the following perspectives.

### 1. Executive Summary

Summarise:

- the apparent purpose of the process
- the business outcome being pursued
- the start and end points
- the major findings
- the most significant pain points
- the most important improvement opportunities
- the confidence level of the analysis

### 2. Process Scope and Context

Identify:

- the process or task name
- the wider business process it belongs to
- the business capability and sub-capability
- the trigger
- the intended outcome
- the completion condition
- upstream dependencies
- downstream dependencies
- process boundaries
- actors and stakeholders

Where the recording appears to cover only part of the process, say so explicitly.

### 3. Hierarchical Process Decomposition

Model the process at progressively greater levels of detail:

- **Level 0:** Business capability or end-to-end value stream
- **Level 1:** Major process stages
- **Level 2:** Activities within each stage
- **Level 3:** Tasks and decisions within each activity
- **Level 4:** Individual system interactions, data changes or user actions where useful

Show how the lower-level steps contribute to the higher-level outcome.

### 4. Detailed Activity Inventory

For each observed or inferred activity, capture:

- activity name
- purpose
- actor
- trigger
- inputs
- outputs
- systems used
- files or documents used
- data created, viewed, copied or changed
- dependencies
- sequence
- frequency, if known
- estimated effort, if observable
- manual, automated or hybrid status
- complexity
- repeatability
- completion criteria
- evidence source or timestamp

### 5. User and Operator Perspective

Capture:

- what the user appears to be trying to achieve
- what they know before starting
- what they must remember
- what they search for
- what they check
- what they calculate
- what they decide
- what they appear uncertain about
- where they hesitate
- where they backtrack
- where they rely on experience or tacit knowledge
- where they use workarounds
- where they gain or lose confidence

Do not infer emotion unless supported by behaviour or commentary.

### 6. Information and Data Flow

Identify:

- information entering the process
- information produced during the process
- data sources
- systems of record
- temporary working files
- duplicated data
- copied and pasted data
- manual transformations
- reconciliations
- hand-offs
- missing data
- inconsistent data
- data that appears stale or unverified
- where data lineage may be lost

Describe how information changes from source to final output.

### 7. Systems and Tooling Perspective

For each system, spreadsheet, document, communication channel or tool, identify:

- its role in the process
- what information it contains
- whether it appears authoritative
- how the user interacts with it
- integration gaps
- manual bridges between systems
- repeated logins or navigation
- context switching
- limitations visible in the recording
- shadow tools or unofficial records

### 8. Decision Analysis

Identify each explicit or implicit decision.

For every decision, capture:

- decision being made
- decision maker
- point in the process
- information used
- decision criteria
- applicable business rule
- whether judgement is involved
- confidence level
- consequence if wrong
- whether the decision can be deterministic
- whether AI could assist
- whether human approval must remain

### 9. Business Rules

Extract visible, stated or implied rules and categorise them as:

- validation
- eligibility
- payroll
- calculation
- timing
- compliance
- approval
- operational
- exception
- data quality
- access or segregation of duties

For each rule, indicate whether it is:

- explicitly stated
- inferred from behaviour
- embedded in a system
- manually remembered
- inconsistently applied
- unknown and requiring confirmation

### 10. Exceptions and Edge Cases

Identify:

- missing inputs
- invalid inputs
- inconsistent information
- unusual cases
- errors
- rejected records
- manual overrides
- retries
- rework
- escalations
- recovery steps
- unresolved exceptions
- cases the user mentions but does not demonstrate

Separate normal process flow from exception handling.

### 11. Pain Points and Friction

Identify evidence of:

- waiting
- searching
- repeated data entry
- copying and pasting
- manual calculation
- repeated checking
- reconciliation effort
- context switching
- unnecessary navigation
- interruptions
- dependency on another person
- unclear ownership
- communication overhead
- uncertainty
- duplicate records
- avoidable approvals
- error-prone steps
- cognitive load

For each pain point, record its likely cause, impact and evidence.

### 12. Operational Waste

Assess the process using Lean waste categories:

- waiting
- unnecessary motion
- unnecessary transport or hand-offs
- over-processing
- over-production
- excess work-in-progress or backlog
- defects and rework
- underused knowledge or capability

Do not force a finding where evidence is absent.

### 13. Risk and Control Perspective

Identify:

- operational risks
- payroll risks
- financial risks
- compliance risks
- data-quality risks
- privacy and security risks
- access-control risks
- audit and traceability risks
- key-person dependency
- continuity risks

For each risk, capture:

- cause
- event
- impact
- existing control
- control type
- evidence of control execution
- apparent control weakness
- suggested control

### 14. Roles, Responsibilities and Handoffs

Identify:

- roles involved
- responsibilities
- decision rights
- approvals
- hand-offs
- unclear ownership
- dependency on specific individuals
- possible segregation-of-duties concerns
- communication channels used

Where only one user is shown, distinguish observed responsibilities from inferred organisational roles.

### 15. Automation Assessment

Classify each activity as one of:

- retain as manual
- simplify before automation
- deterministic rule automation
- workflow automation
- integration opportunity
- assisted automation
- AI-assisted activity
- autonomous agent candidate
- human approval required
- unsuitable for automation

Explain the reason for each classification.

### 16. AI-Readiness Assessment

For relevant activities, assess whether they are best suited to:

- deterministic logic
- rules engine
- workflow orchestration
- machine learning
- large language model assistance
- agentic orchestration
- human judgement
- hybrid human-machine processing

Identify required:

- context
- data quality
- metadata
- permissions
- audit trail
- guardrails
- confidence thresholds
- human decision gates
- fallback behaviour

Do not recommend AI where conventional automation is safer or more appropriate.

### 17. Operational Intelligence Model

Identify the likely:

- business entities
- actors
- records
- events
- states
- state transitions
- relationships
- identifiers
- metadata
- business rules
- decisions
- controls
- exceptions
- outputs

Describe the emerging domain model without pretending that unobserved relationships are confirmed.

### 18. Requirements Candidates

Infer potential requirements and categorise them as:

- functional
- workflow
- data
- validation
- integration
- reporting
- audit
- traceability
- versioning
- approval
- access control
- security
- usability
- resilience
- performance
- operational support

Label all inferred requirements as candidates requiring validation.

### 19. Metrics and Baseline Opportunities

Identify what could be measured, including:

- total lead time
- active processing time
- waiting time
- manual effort
- number of user touches
- number of hand-offs
- number of systems used
- number of data entries
- number of checks
- exception rate
- error rate
- rework rate
- first-time-right rate
- approval time
- reconciliation effort
- automation percentage
- complaint volume
- unresolved-item backlog
- user confidence

State which metrics can be derived from the recording and which require additional operational data.

### 20. Improvement Opportunities

Group opportunities into:

- immediate clarification
- quick wins
- process simplification
- data-quality improvements
- workflow improvements
- control improvements
- integration opportunities
- deterministic automation
- AI-assisted opportunities
- foundational platform capabilities
- longer-term transformation

For each opportunity, assess:

- problem addressed
- expected benefit
- dependencies
- risk
- complexity
- confidence
- recommended priority

### 21. Unknowns and Follow-up Questions

Produce a structured list of:

- missing information
- ambiguities
- assumptions
- contradictions
- unobserved upstream activities
- unobserved downstream activities
- policies or rules requiring confirmation
- stakeholders to interview
- additional recordings or evidence required

Prioritise the questions that would materially change the process model or solution direction.

### 22. Final Assessment

Conclude with:

- current process maturity
- data maturity
- control maturity
- automation maturity
- AI readiness
- principal operational constraint
- principal source of risk
- principal source of avoidable effort
- top five recommended next actions
- overall confidence score

## Required Output Structure

Present the analysis in this order:

1. Executive summary
2. Scope and confidence statement
3. Hierarchical process map
4. Detailed activity table
5. User journey observations
6. Information and system flow
7. Decisions and business rules
8. Exceptions and pain points
9. Risks and controls
10. Automation and AI-readiness assessment
11. Operational intelligence model
12. Requirements candidates
13. Metrics and baseline plan
14. Prioritised opportunities
15. Unknowns and follow-up questions
16. Final assessment

Where possible, cite timestamps or clear evidence references from the source material.

Never present an inference or assumption as an observed fact.