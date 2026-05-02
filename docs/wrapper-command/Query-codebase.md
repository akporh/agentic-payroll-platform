You are not allowed to assume system behavior.

Only answer using:
1. Actual code paths
2. Actual database writes
3. Explicit mappings

For each field, answer:

- Where is it written?
- What code writes it?
- What input feeds it?
- If not found, explicitly say: "NOT POPULATED ANYWHERE"

Trace end-to-end:
UI → API → Service → DB

Trace the full lifecycle of period inputs for a specific payroll run:

Context:
- PayrollRunId: <ID>
- EmployeeId: <ID>
- PeriodInputId (if known): <ID or NULL>

where payroll run context is not specified please set one up using the example docs/data/Client B/Client 2 setup.txt

Do not infer intended behavior. Only describe observed implementation.