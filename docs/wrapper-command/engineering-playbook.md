# Engineering Playbook

## Purpose
This document defines how all system changes must be reasoned about.

It is used by:
- Engineers
- Reviewers
- AI agents (Casper)

---

## Core System Categories

All changes must be evaluated across:

1. **Guarantees**
   - Determinism
   - Idempotency
   - Immutability
   - Financial correctness

2. **Engine**
   - Execution flow
   - Rule evaluation
   - Ordering

3. **Data Model**
   - Schema design
   - Source of truth
   - Relationships

4. **Temporal / Versioning**
   - Historical correctness
   - Retroactivity
   - Effective-dated rules (source of truth)
   - Snapshotting at payroll run (execution layer)
   - Immutable payroll results (storage layer)

5. **Execution & Retry**
   - Retry strategy
  
   - Partial execution
  
   - Reprocessing safety

6. **Audit & Traceability**
   - Logs
  
   - Snapshots
  
   - Reproducibility

7. **Integration Boundaries**
   - APIs
  
   - External dependencies

8. **Testing & Validation**
   - Invariants
  
   - Edge cases
  
   - Regression coverage

9. **Failure Modes**
    - Race conditions
  
    - Partial writes
  
    - Data inconsistency
---
## Required Process for Any Change

### 1. Problem Understanding
- Restate the problem
- Identify the real underlying problem (not just symptoms)
- Identify which categories are impacted
- Highlight risks and hidden edge cases across each category
- Propose multiple approaches
- Recommend the best approach with reasoning
- What is being changed?

### 2. Design
- Provide a solution that explicitly addresses EACH category above.
- Must address ALL categories
- Justify omissions

### 3. Stress TestBreak the design across
- Time (historical vs current)
- Failures (partial execution, retries)
- Data consistency (stale vs snapshot)
- Edge cases
- List failure points and fix them.

### 4. Invariants
- Define what must NEVER break (guarantees).These must NEVER be violated.


### 5. Implementation Rules
- Do not bypass guarantees
- Do not duplicate sources of truth
- Do not patch over failing tests
- Fix root causes only

### 6. VALIDATION RULES

- Skipping categories is not allowed
- Missing invariants is not allowed
- Hidden assumptions are not allowed
- Weak retry/idempotency is not allowed

If any rule is violated:
→ STOP and explain why


### Act as:- 
- Architect (design) 
- Reviewer (challenge)

The reviewer must:
- Identify flaws
- Challenge assumptions
- Highlight long-term risks

