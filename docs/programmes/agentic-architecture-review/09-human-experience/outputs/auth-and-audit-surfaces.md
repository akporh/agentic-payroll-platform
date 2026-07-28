# Stage 09 Output: Auth and Audit Surfaces (Q7 + Q8)

Designs the operator-facing authentication surfaces and the audit-history presentation rules. **Mechanisms rendered**: C1 login/session/switch/step-up (`08-technical-architecture/outputs/auth-foundation-design.md` §§1–2, 5), the cut-over epoch (`platform_metadata.auth_cutover_epoch`, §1.6), statutory provenance labels (`statutory-change-mechanism-design.md` §2.3). **Grounding**: today's frontend has a TopBar user menu with no auth behind it, and a workspace picker that is pure client navigation (`MainLayout.tsx:61` — evidence file §§1–2).

## Q7.1 — Login and workspace selection

- **Login page** (the only unauthenticated surface besides health — allowlist §3.3): email + password. Failure copy is uniform regardless of which check failed ("Invalid email or password" — mechanism §5's uniform-error rule); no "email not found" variant, no lockout disclosure.
- **Workspace selection from memberships** at login: single-membership operators are auto-selected straight into their workspace (the overwhelmingly common case — single-operator bureau); multi-membership operators pick from a list (name + status badge). The selection is part of login because the token is workspace-locked (`wid` claim) — there is no "logged in but nowhere" state.
- Post-login landing: the selected workspace's dashboard; `PLATFORM_ADMIN` operators land the same way (platform areas are reachable from the chrome, not a separate login mode).

## Q7.2 — Workspace switch as a context change (P6)

Today's picker does `navigate()` — the workspace is a filter. Post-C1 it is a **session change** (revoke + reissue, mechanism §2), and the UI must present it as one:

- The TopBar picker keeps its position (NAV-1) but lists **memberships only**, and selecting triggers the switch call with a full-screen transitional state ("Switching to {workspace}…") that tears down and reloads all workspace context — no in-place data morphing, no preserved scroll/tab state, breadcrumbs reset. The pause *is* the message: you are somewhere else now.
- In-flight unsaved work: the switcher warns before switching when a dirty form is open (standard unsaved-changes guard). No confirm dialog otherwise — switching is non-destructive.
- The frontend's stored workspace selection becomes navigation state only (Stage 08 handoff item 1): deep links to a non-token workspace resolve through the membership check — a member gets the switch transition; a non-member gets the uniform 404 surface (no existence disclosure, R2).

## Q7.3 — Session expiry (8h, no refresh)

- On any 401 from an expired/revoked session: a **session-expired interstitial** ("Your session has ended — sign in to continue"), preserving the intended destination for post-login return. Never a silent redirect that loses the operator's place; never a broken half-rendered page.
- The 8h token spans a working day (mechanism §1.3 rationale) — mid-day expiry is the exception, not the rhythm. For long-form surfaces (bulk imports, mapping review), Phase 3 should prefer draft-preserving behaviour on 401 where the surface already has draft state; no new draft infrastructure is designed for this.
- Logout lives in the user menu; it revokes the session (not just clears the client).

## Q7.4 — The step-up modal (shared component)

One modal, used wherever step-up is demanded (v1: C12 approval only):

- **Copy states why**: "Approving a statutory change requires re-entering your password." Password field (TOTP slot appears with MFA enrollment — DEC-07-03/DQ-007, the modal does not pre-empt that decision).
- On success, the invoking action **submits immediately** with the returned `step_up_event_id` — the modal is invoked at the decision moment, so the 5-minute freshness window is consumed in seconds by design (Stage 08 handoff: "submit promptly or expect a fresh prompt").
- Expired/consumed/foreign event → 403 → the modal re-presents with "your confirmation expired — re-enter your password." Failures are `auth_event`s server-side; the UI adds nothing.
- Step-up is visually distinct from login (modal over the current context, not a redirect) — the operator must understand they are still signed in and confirming *this specific action*.

## Q7.5 — User menu

Operator display name + avatar initial (chrome already exists — evidence file §1), role label, Sign out. `PLATFORM_ADMIN` additionally sees platform entries here (Statutory Changes; platform ops). The menu is the IA home for "who am I, what am I allowed to do."

## Q8 — Audit-history presentation (every audit surface, one rule set)

Applies to: the run-detail Audit Log tab (today rendering raw `performed_by` strings — `PayrollResults.tsx:1174`, evidence file §3), exception lifecycle histories, pending-action records, statutory proposal/approval histories, auth-event views (platform ops), and any future audit rendering. **These are presentation rules, not per-surface designs — Phase 3 implements them as one shared actor-display component.**

1. **Actor display = UUID → display name via operator join** (records store operator UUIDs — mechanism §4). Service principals display as their `svc:` name with a "service" chip (`principal_type` join), never disguised as humans.
2. **Pre-epoch labelling is mechanical**: every row whose timestamp predates `platform_metadata.auth_cutover_epoch` renders its legacy actor string with the label **"identity unverified (pre-auth era)"** — a muted chip adjacent to the actor, compared row-by-row against the epoch value, not hardcoded per surface. **UX-critical invariant (threat-model §6)**: no UI may present a pre-epoch actor as verified — the label is not collapsible, not tooltip-only, and appears in exports as a column.
3. **Post-epoch rows carry verified identity** — rendered without qualification. The visual contrast between labelled and unlabelled rows is the feature: audit readers see exactly where attribution became trustworthy.
4. **Statutory provenance**: statutory rules without `applied_change_id` are labelled **"migration-seeded (pre-C12)"** wherever rules are displayed (mechanism §2.3); rows with it link to their approval record.
5. **Timestamps** display in the operator's locale but sort/export on the stored DB-clock values; no UI-side clock arithmetic beyond display.

## Notes for Phase 3 (carried, not designed here)

- The `userName` prop plumbing already exists in the TopBar; C1 wires it to the session principal.
- The Audit Log tab's `TimelineTable` adapter (`auditEntries` mapping) is the natural seam for the shared actor-display component — one adapter change covers the highest-traffic audit surface.
