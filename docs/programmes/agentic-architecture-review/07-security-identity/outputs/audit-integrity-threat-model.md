# Stage 07 Output: Audit-Store Integrity Threat Model

Treats `audit_log`/`event_store` integrity as a security property, per Stage 06's handoff ("an attacker who can UPDATE audit rows defeats non-repudiation"). Consumes F-06-02 (post-commit fire-and-forget writes) and F-06-03 (no immutability/retention protection) without re-verifying them. Disposes of the historical-rows cut-over epoch question. Mechanism build is Stage 08's (constraints stated in §4).

## 1. Assets

The records whose integrity non-repudiation depends on: `audit_log`, `event_store`, and — once built — the R4 approval records (C12/C10), the exception-resolution lifecycle records, and the agent/tool-call logs (SC-3). Everything below applies to all of them; the four Stage 06 integrity properties (attributable, reliably written, immutable, retained — `audit-expansion-requirements.md` §3) are the requirements this threat model justifies.

## 2. Threat actors and tampering paths

| Actor | Path | Current exposure (at `ea1590a`) | Required control |
|---|---|---|---|
| **External caller** | HTTP surface | No audit-mutation endpoint exists (good); but with zero auth (F-05-01), any caller can *generate* arbitrarily-attributed records via normal mutating routes — pollution, not tampering | C1; R1 derivation path. Keep the invariant: **no HTTP surface ever exposes UPDATE/DELETE on audit records** — an intentional permanent absence, stated so it survives future CRUD scaffolding habits |
| **App-credential DB actor** (compromised app, leaked credentials, or an insider using them) | Direct SQL | Full UPDATE/DELETE on both tables — the app's single DB role can silently rewrite history (F-06-03) | DB-layer append-only enforcement (§4) |
| **The application itself** (bugs, races) | Write path | Fire-and-forget post-commit writes can silently drop records (F-06-02) — integrity loss by omission | Outbox-coupled writes (§4) |
| **Service principals / scheduled jobs** | App code paths | Same as the app; additionally, misattribution if principals are shared | R3 named principals; T6 auth-event audit (`identity-architecture-requirements.md`) |
| **DB superuser / infrastructure operator** | Direct SQL as superuser | Can defeat any in-database control (triggers, role grants) | Out of scope for in-DB controls; bounded by §5 (residual risk statement) |

## 3. The two integrity failures ranked

1. **Loss by omission** (F-06-02) is the *live* failure mode — it requires no attacker, only a write failure in the post-commit window. Highest priority: audit writes join the state-change transaction via the outbox mechanism, explicitly including audit records, not just notification events (Stage 06's requirement, reaffirmed as a security property).
2. **Tampering by app-credential actor** (F-06-03) is the *non-repudiation* failure mode — records exist but cannot be stood behind against a disputing party, because any app-credentialed actor could have rewritten them. This caps the evidentiary value of every record written today, which is precisely what R4 forbids for approval-class records.

## 4. Required DB-layer protection (constraints on Stage 08's mechanism choice)

- **Minimum: trigger-based append-only enforcement** on `audit_log`, `event_store`, and every future compliance-evidence table — rejecting UPDATE and DELETE. The platform's own precedent is `3da637afb11b` (payroll_result PAID protection, both UPDATE and DELETE triggers); Stage 06 confirmed 10 trigger-bearing migrations exist and none covers the audit tables. Triggers are the floor because they work within today's single-role deployment.
- **Role separation is the stronger form** (an app role with INSERT/SELECT only on audit tables) and is preferred *if* the deployment gains role separation for other reasons; it defends against `DISABLE TRIGGER` by the app role. Stage 08 chooses; choosing triggers-only is acceptable with §5's residual risk recorded.
- **Corrections to audit records are themselves append-only**: a wrong audit row is never edited — a correction record references it (same principle as `statutory-change-control-design.md` §5 for rule corrections).
- **Retention**: keep-at-least-7-years posture; **no deletion/archival mechanism built** until DQ-008 resolves (Stage 06 §2 of the audit standard — unchanged). Append-only enforcement must not carve out a purge path in advance of that resolution.

## 5. Residual risk (stated, not hidden)

In-database controls do not bind a DB superuser or the infrastructure provider. For this platform's deployment shape (small bureau, managed Postgres), that residual is accepted at requirements level rather than countered with external anchoring (WORM storage, periodic hash anchoring), which would be disproportionate now. Two forward hooks keep the door open cheaply: (a) audit records carry insertion timestamps from the DB clock (not app-supplied), and (b) the record shape must not preclude later hash-chaining. If a future client or regulator demands stronger tamper-evidence, Stage 10's assurance framework is where that requirement lands. This acceptance is an executor conclusion within inherited risk framing — flagged for visibility in `decisions.md` (DEC-07-04), not a queued human decision, since no current obligation demands more.

## 6. Cut-over epoch for historical unverified-identity rows — confirmed, with two hardenings

Stage 06 forwarded the treatment (past audit rows carry self-asserted identity permanently; document an epoch — "records before X: identity unverified") as an implementation specification. **Confirmed correct** — the past cannot be re-attributed, and deleting or rewriting historical rows would itself violate append-only. Two hardenings beyond "documented":

1. **The epoch is data, not prose**: persisted where consumers can read it (a platform-metadata row or equivalent — Stage 08 shape), so every surface that renders or exports audit history can label pre-epoch rows `identity_unverified` mechanically. A documentation-only epoch will be missed by the next export feature.
2. **No verified-identity presentation of pre-epoch rows**: any UI/export/API presenting audit records must distinguish pre-epoch actors (e.g. `admin@internal (unverified — pre-auth era)`), so a compliance reviewer can never mistake placeholder attribution for verified attribution (R6's spirit applied backwards).

The epoch is set at C1's cut-over deployment; one epoch platform-wide (per-workspace epochs add complexity with no evidentiary gain for a single cut-over event).

## 7. Verification standard

- Committed test: UPDATE and DELETE against each protected audit table are rejected at the DB layer (F-06-03 closure evidence).
- Committed test: a forced audit-write failure cannot leave a committed state change without a durable record (F-06-02 closure evidence — outbox path).
- Epoch labelling test: a pre-epoch fixture row renders/exports as unverified; a post-epoch row carries a verified principal.
- Grep/enumeration check: no route or repository function performs UPDATE/DELETE on audit tables (the §2 permanent absence, kept true by test).
