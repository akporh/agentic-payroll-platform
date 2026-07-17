# Stage 08 Output: Tool Contracts (11 tools + guard-wrapper shape)

Answers Stage 08 Q3: field-level contracts for the approved tool portfolio (`03-agent-portfolio/outputs/tool-portfolio-matrix.md` — 10 original + the C13 catalog tool), and the structural implementation shape for the tool-guard wrapper within `07-security-identity/outputs/tool-layer-security-pattern.md`'s P1–P8. Cross-cutting rules bound throughout: independent workspace verification (Stage 02 Principle 11), Decimal-as-string, facts-not-conclusions, explicit null semantics.

## 1. Wrapper structural choice: decorator-registered registry (not middleware)

**Choice: a `ToolRegistry` with a registration decorator.** Middleware (intercepting a generic tool-dispatch call) would check tools by name at dispatch time — config lookup can silently miss (exactly the fail-open risk P3 forbids). A registration decorator binds the declarative config at import time:

```
@registry.tool(
    name="get_employee", version="1",
    scoping=OwnershipCheck(table="employee", pk="employee_id", param="employee_id"),
    params=GetEmployeeParams,          # Pydantic, extra="forbid", bounds enforced
    returns=EmployeeFacts,             # serializer applies PII policy + Decimal-as-string
)
def get_employee(...)
```

- **P1**: the agent runtime resolves tools only through `registry.invoke(name, session_ctx, params)` — bodies are module-private; nothing imports them directly.
- **P2**: `session_ctx` carries the verified principal + active `workspace_id` from C1's session. No params model may declare a `workspace_id` field — the registry rejects such a model at startup (schema introspection), making "workspace as tool parameter" structurally impossible.
- **P3 (fail closed)**: `scoping=` is a required keyword with no default. Omission is a `TypeError` at import; a registry-completeness startup check additionally asserts every registered tool's config validated.
- **P4**: `OwnershipCheck` executes as the wrapper's **own query** (`SELECT 1 FROM <table> WHERE <pk> = :param AND workspace_id = :session_wid`, or the declared join path) before the body runs — independent of whatever the repository does. Declared join paths for tables without `workspace_id` are part of the config (e.g. through `payroll_run` or `employee`).
- **P5**: ownership failure and not-found are the same refusal: outcome `REFUSED`, tool result "not found", logged with attempted params (SC-3).
- **P6**: the exit serializer applies the **versioned PII sanitizer** (ruleset id stamped per invocation), renders every Decimal as a string, renders untrusted DB strings as JSON data values only (never concatenated into instruction-position text — threat-model §3.4), and maps declared nullable dependencies to explicit contract states.
- **P7**: every invocation writes one `tool_call_log` row (`event-audit-foundation-design.md` §7) — success, empty, refused, or error.
- **P8**: blocked tools are **absent from the registry** (no code registers `get_reconciliation`); the uniformity test pins the registered set to the approved list.

Capability-scoped registries (SS-4): each capability constructs its session from a declared subset — `C3: {get_employee, get_employees, get_payroll_run, get_enrollment_status, get_salary_definitions}`; `C5: {get_run_results, explain_component_trace}`; `C7-narration: {}` (narrates from the exception record passed in context; no tools); `C11: {get_statutory_rules}` only (context isolation, T4/SG-11); `C13: {get_workspace_catalog}`. Subsets are constants checked by test against the capability matrix.

## 2. Common contract elements

- **Params**: Pydantic models, `extra="forbid"`, UUIDs validated as UUIDs, list limits enforced server-side regardless of what the model asks for.
- **Errors**: `REFUSED` (ownership/not-found/null-dependency refusal), `EMPTY` (valid query, zero rows), `ERROR` (internal — generic message out, detail logged server-side; the standing `str(e)` prohibition applies to tool results too).
- **PII**: strip `full name, TIN, RSA pin, bank account, employee_number`; keep UUIDs, amounts-as-strings, component names, dates, statuses (source document PII table, kept). Frontend maps UUID → name for display.

## 3. Per-tool contracts

### 3.1 `get_employee` (C3)
- **Params**: `employee_id: UUID`.
- **Scoping**: `employee.workspace_id` via `employee_id`.
- **Returns**: `{employee_id, status, hire_date, grade_code, designation_code, enrollment: {salary_definition_code|null}, contract: {start_date, end_date|null}|null}`.
- **Nulls**: no live contract → `contract: null` (explicit, not omitted).

### 3.2 `get_employees` (C3)
- **Params**: `status?: enum(ACTIVE|INACTIVE)`, `enrolled?: bool`, `limit?: int ≤ 50` (default 50), `offset?: int`.
- **Scoping**: query filtered by session `workspace_id` (list tool — the filter *is* the check; wrapper additionally asserts the declared filter column exists).
- **Returns**: `{total_count, rows: [{employee_id, status, grade_code, enrolled}]}` — max 50 rows. Zero matches → `EMPTY` with `rows: []`.

### 3.3 `get_payroll_run` (C3)
- **Params**: `run_id: UUID`.
- **Scoping**: `payroll_run.workspace_id` via `run_id`.
- **Returns**: `{run_id, status, run_type, period_start, period_end, created_at, totals: {gross, deductions, net} | null}` — totals as strings; `null` before CALCULATED.

### 3.4 `get_run_results` (C5)
- **Params**: `run_id: UUID`, `employee_id?: UUID`, `limit?: int ≤ 100`.
- **Scoping**: through `payroll_run.workspace_id` via `run_id` (results carry no workspace column — declared join path).
- **Returns**: per row `{employee_id, status, gross_pay, net_pay, component_trace: [...] | null}` — all amounts strings.
- **Nulls**: `component_trace_jsonb IS NULL` (legacy-executor rows) → `component_trace: null` with sibling `trace_available: false` — a distinct, explicit state (matrix rule 4). The wrapper's null-handling is independent of the HTTP-layer coercion at `payroll.py:1129` (which coerces to `[]` — a tool must not inherit that ambiguity; see `remediation-designs.md` §6 for the repo-layer guard).

### 3.5 `explain_component_trace` (C5)
- **Params**: `run_id: UUID`, `employee_id: UUID`.
- **Scoping**: inherits 3.4's declared path — declared explicitly again in its own config (never "inherited" implicitly, per the matrix).
- **Behaviour**: fetches the trace via the same guarded path, then fills named prose slots from trace values. The serialization layer programmatically checks every numeric token in the output against the source trace set (CG-5's zero-hallucination check is an *output contract*, not just an eval).
- **Null trace (F-03-15 resolved)**: **refuse cleanly.** Returns `REFUSED` with reason code `TRACE_UNAVAILABLE` and the fixed operator-facing text ("a calculation trace is not available for this result; it was produced by the legacy execution path"). No degraded generic explanation — a generic explanation of a specific employee's pay is exactly the plausible-but-ungrounded output the capability exists to prevent.
- **Audit**: logs the trace fields actually surfaced (matrix row requirement).

### 3.6 `get_reconciliation` — **NOT REGISTERED** (P8)
Blocked per D-02-02 until the repository-level fix (`remediation-designs.md` §1) **and** the wrapper's independent check are both live with committed regression tests. Contract to be written at unblock time; no placeholder registration, no disabled flag.

### 3.7 `get_pending_inputs` (C3/C7 context)
- **Params**: `employee_id?: UUID`, `input_code?: str(≤50)`, `limit?: int ≤ 200`.
- **Scoping**: `payroll_input.workspace_id` filter (list tool) — only unclaimed rows (`payroll_run_id IS NULL`).
- **Returns**: `{rows: [{payroll_input_id, employee_id, input_code, input_category, quantity, reference_date}]}` — quantities as strings.

### 3.8 `get_enrollment_status` (C3) — facts-only per F-03-08
- **Params**: `employee_id: UUID`.
- **Scoping**: through `employee.workspace_id` (employee_contract carries no workspace column — declared join path, F-01-15).
- **Returns** (individual facts, no packaged "why" conclusion):
  `{employee_id, status, enrolled: bool, salary_definition_code: str|null, grade_code: str|null, contract: {start_date, end_date|null, active_today: bool}|null, in_next_run_eligible: bool}` — `in_next_run_eligible` is the deterministic conjunction the engine itself applies (ACTIVE + enrolled + live contract), computed server-side, so C3's narrative composes from stated facts.

### 3.9 `get_statutory_rules` (C3/C11)
- **Params**: `as_of_date?: date` (default today).
- **Scoping**: declared `scoping: platform-level` (affirmative — P3). Wrapper still runs audit/serialization. Country resolved from the session workspace's `country_code` for C3; C11's platform session passes `country_code` explicitly.
- **Returns**: the resolved rule via date-driven resolution only (`effective_from <= as_of ORDER BY effective_from DESC, version DESC` — the platform's own resolution shape, F-08-01): `{statutory_rule_id, country_code, effective_from, version, components: {...}, tax_bands: [...]}` — rates as strings. No "current rule" shortcut exists in the contract.

### 3.10 `get_salary_definitions` (C3)
- **Params**: `limit?: int ≤ 50`.
- **Scoping**: `salary_definition.workspace_id` filter.
- **Returns**: `{rows: [{salary_definition_code, grade_code, components: [{code, amount}]}]}` — amounts as strings.

### 3.11 `get_workspace_catalog` (C13 — the new tool, Stage 03 handoff item 8)
- **Params**: none (catalog is small; no pagination in v1).
- **Scoping**: session workspace filter across all three catalog tables.
- **Returns**: `{grades: [{grade_code, name}], designations: [{designation_code, name}], salary_definitions: [{salary_definition_code, grade_code, component_codes: [...]}]}` — the mapping targets C13 proposes against. No employee data, no amounts (amounts are not needed for header mapping and would widen C13's exposure for no gain; if a later mapping heuristic needs amounts, that is a contract version bump, logged as such per SC-3's tool-version field).
- **Exposure**: catalog-only; contains no PII by construction.

## 4. PII sanitizer versioning

The sanitizer is a versioned ruleset constant (`PII_RULESET_VERSION = "1"` with the field lists in code, changed only by PR); every `tool_call_log` row stamps the version applied (SC-3). Version history lives in the repo; the active version is also exposed via a platform-ops read for Stage 10's evidence gathering.

## 5. Verification standard (tool-layer-security-pattern §3, restated as this design's closure evidence)

1. **Uniformity test**: registry enumeration == approved list (11 minus blocked = 10 registered); every entry has validated scoping config.
2. **Per-tool negative path**: cross-workspace fixture → `REFUSED` + logged record, for every workspace-scoped tool.
3. **Wrapper independence**: stub a repo function to return foreign-workspace rows → wrapper still refuses (P4 proven real).
4. **Fail-closed**: registering a tool without scoping config fails startup (test asserts the `TypeError`).
5. **Serialization**: property test — no Decimal/float leaves any tool un-stringified; no PII field name appears in any serialized output; every numeric token in `explain_component_trace` output exists in the source trace.
