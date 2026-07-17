# Stage 06 Output: Tenant-Isolation Control Assessment

Answers the stage question: is the reconciliation workspace-scoping gap (F-05-03) a **compliance control failure** in addition to a security defect — and does any other confirmed gap rise to the same classification? Consumes Stage 05's re-verified facts (F-05-01, F-05-03, F-05-11) without re-deriving them; the classification and control-evidence requirements are this stage's contribution.

## 1. The isolation obligation a payroll bureau owes its clients

Sandy is a payroll bureau: each workspace holds a distinct client company's payroll data (salaries, deductions, reconciliation totals, employee identifiers). Client-to-client confidentiality is not a feature preference — it is a baseline professional obligation of the bureau model and an implied term of every client engagement, and payroll data is personal and financially sensitive data under any applicable data-protection framing. A mechanism that lets Client A's operator (or anyone) read Client B's reconciliation state is a breach of that obligation, not merely a bug.

## 2. Classification: reconciliation scoping (F-05-03) — **confirmed compliance control failure**

**Definitive classification: control failure, not only a security defect.** Three reasons:

1. **The obligation exists and the control does not.** The data path is unscoped end-to-end (model → repo → service → route, per Stage 05's table) — there is no failing control to fix; the control is absent.
2. **The control *appears* to exist.** The nominally workspace-scoped routes accept `workspace_id` and discard it. To an API consumer, a reviewer, or a client-facing assurance statement, the surface asserts isolation it does not provide. A control that falsely attests is a more serious compliance posture than a control that is visibly absent — it defeats review.
3. **Corroborated independently** — the parallel audit programme classifies the same facts at S0/S1 (09-002/09-004, cited by Stage 05).

This holds **in addition to** the systemic fact beneath it (§4): fixing reconciliation scoping alone does not restore isolation while `workspace_id` itself is unauthenticated.

## 3. Control evidence required to close it (not just the code fix)

D-02-02 already fixed the remediation shape (repo-level fix mandatory; tool-layer check is defence-in-depth, not a substitute). Stage 05 named the code/test closure evidence. What *this* stage adds — the control-evidence layer:

1. **Code fix** per Stage 05's five items (column, repo filters, service threading, route enforcement, with route enforcement first as the false-attestation fix).
2. **Regression test named for the invariant** (cross-workspace access rejected) — per the project's standing rule; the test is the *repeatable* control evidence, not just the fix commit.
3. **A negative-path check in the test for every route** that presents as workspace-scoped — not only reconciliation: the test pattern must assert the `workspace_id` a route accepts is actually enforced, so "decorative scoping" cannot recur silently on the next scaffolded route.
4. **An isolation control statement** (one page, maintained): which tables carry workspace scoping, which are platform-level by design (`statutory_rule` per F-01-45), and where enforcement lives. This is what a bureau can show a client or an external reviewer; today no such artefact exists and the codebase's actual posture could not honestly populate one.
5. **Closure is demonstrated, not planned** — consistent with D-02-02/Stage 05: committed code + passing regression tests; no capability gated on this (C8, `get_reconciliation`) unblocks on a plan.

## 4. Other confirmed gaps assessed against the same bar

| Gap | Same classification? | Reasoning |
|---|---|---|
| **F-05-01 — no authentication; `workspace_id` caller-supplied everywhere** | **Yes — control-environment failure** (broader than a single control failure) | Isolation guarantees currently have no enforcement layer beneath them anywhere: every scoped query protects against honest callers only. This is the absence of the platform's entire authentication control environment, within which every individual scoping gap sits. Classifying it here changes its framing for Stage 07/13: auth is remediation of an absent compliance control environment for a multi-client bureau — not a feature on a roadmap. |
| **F-05-11 — `load_inputs_for_run` unscoped; `workspace_info()` arbitrary `LIMIT 1`** | **Control weakness, not (yet) control failure** | Both are internal functions currently safe via caller discipline; neither is exposed on a surface asserting isolation. They become failures the moment either is wrapped as a tool — hence the existing gate (fix before wrapping) is the right treatment. No upgrade to failure classification while unexposed. |
| **Legacy unscoped reconciliation routes** (`/payroll/run/{run_id}/reconcile`) | Subsumed into §2 | Same data path; the audit programme's 09-002 covers it at S0. |

No other confirmed finding from Stages 01–05 presents client-to-client data exposure on an exposed surface; the remaining scoping-related findings are either fixed, internal-only, or platform-level-by-design.

## 5. Consequence for the control-gate register

- CG-8 (C8 Reconciliation Investigation) carries this closure as a hard gate (it already did via D-02-02; restated with the §3 control-evidence list).
- CG-1 (C1) inherits §4's control-environment framing.
- Every tool row in `control-gate-register.md` carries the independent tool-layer workspace check (D-02-02 defence-in-depth, Stage 03 cross-cutting requirement 1) as a standing control, not a per-capability optional.
