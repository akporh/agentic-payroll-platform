# S2 — Create Workspace (Modal)

**Actor:** Bureau Administrator (Chidi)
**Emotional state:** Task-focused, wants to get a new client live quickly

---

## Layout

```
┌─────────────────────────────────────────────────────┐
│  Create New Workspace                           [✕] │
├─────────────────────────────────────────────────────┤
│                                                     │
│  A workspace represents one client company.         │
│  You can configure it fully before going live.      │
│                                                     │
│  Company name *                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │ e.g. Acme Corporation                       │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Country *                                          │
│  ┌─────────────────────────────────────────────┐    │
│  │ Nigeria (NG)                            [▾] │    │
│  └─────────────────────────────────────────────┘    │
│  ℹ Determines statutory rules (PAYE, Pension, NHF)  │
│                                                     │
│  Base currency                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ NGN — Nigerian Naira                    [▾] │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│                                                     │
│                    [Cancel]  [Create Workspace →]   │
└─────────────────────────────────────────────────────┘
```

---

## States

### Error — Invalid Country Code (422)
```
│  Country *                                          │
│  ┌─────────────────────────────────────────────┐    │
│  │ XX                                          │    │
│  └─────────────────────────────────────────────┘    │
│  ✕ No statutory rules are configured for this      │
│    country. Contact your platform administrator.    │
```

### Submitting State
```
│                    [Cancel]  [Creating...    ●]     │
```
Button disabled during submission. Spinner replaces text.

### Success (closes modal, workspace card appears)
```
Toast: "Acme Corporation workspace created. Complete onboarding to go live."
```

---

## Key UX Decisions

**Modal, not a page:** Creating a workspace is a 3-field operation. A full page would be disproportionate. Modal keeps Chidi in the bureau dashboard context.

**Country as meaningful choice, not a code:** Show "Nigeria (NG)" not just "NG". The ℹ note explains why it matters without overwhelming the form.

**Currency pre-selected to NGN:** The platform is Nigerian payroll. NGN should be the default. Don't make Chidi select something he'll never change.

**Post-create redirect to Setup Wizard:** Immediately after creation, navigate to the workspace onboarding — the workspace is useless until configured.
