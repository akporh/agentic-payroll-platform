# Artefact 4 — Actor List

> Source: Route structures, `X-Performed-By` header usage, audit log fields, page layout
> (`BureauDashboard.tsx` vs `WorkspaceDashboard.tsx`), and the approval/lock/pay step separation.
>
> **Important caveat:** No role-based access control (RBAC) is implemented in the current backend code.
> The routes enforce no role checks — `workspace_id` scoping is the only access boundary.
> The `X-Performed-By` header is optional and defaults to `"admin@internal"`.
> The actors below are inferred from: (a) page structure, (b) the multi-step approval workflow,
> and (c) domain knowledge of Nigerian payroll bureau operations.
> They describe intended users, not enforced system roles. RBAC would need to be added
> before the actors below have real access separation.

---

## Actor 1 — Bureau Administrator
**Scope:** Platform-wide (all workspaces)

The person who manages the payroll bureau itself. Creates new client workspaces, monitors overall system health, and sees cross-workspace summaries. Corresponds to the `BureauDashboard.tsx` page.

---

## Actor 2 — Payroll Operator
**Scope:** One or more assigned workspaces

The person who runs payroll day-to-day. Enters variable inputs (overtime, leave, etc.), triggers payroll runs, reviews results per employee, retries failed employees, and advances the run through CALCULATED → APPROVED. This is the primary day-to-day user.

---

## Actor 3 — Finance Authoriser
**Scope:** One or more assigned workspaces

The person with sign-off authority over money leaving the business. Advances the run from APPROVED → LOCKED and then LOCKED → PAID after verifying bank disbursement. Downloads the bank upload CSV. Submits the actual payment total for reconciliation and resolves any MISMATCH.

---

## Actor 4 — HR / Onboarding Administrator
**Scope:** One workspace

The person responsible for setting up and maintaining the employee master data. Manages employees, salary definitions, grades, designations, and contract dates. Performs initial workspace onboarding. May be the same person as the Payroll Operator in smaller bureaux.

---

## Actor 5 — Compliance Officer (inferred, not coded)
**Scope:** One or more workspaces

The person responsible for statutory reporting. Downloads PAYE remittance and pension contribution CSVs after a run is locked. Primarily a read-only consumer of completed payroll data. No dedicated screen exists yet — they use the exports on the PayrollResults or Runs page.

**Note:** This actor is inferred from the existence of the PAYE and pension export endpoints. No distinct page or role is coded for them.
