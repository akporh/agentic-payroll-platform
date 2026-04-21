# Gate 1 — Design Decisions Log

> Every major design decision with its rationale, the alternative considered, and the risk.
> This log exists so Gate 2 and Gate 3 can be built on understood foundations,
> not guessed-at ones.

---

## UX Architecture Decisions

### DD-1 — Two-Tier Navigation: Global Top Bar + Workspace Sidebar

**Decision:** Bureau-level navigation lives in a persistent top bar. Workspace-level navigation lives in a left sidebar that appears only when inside a workspace.

**Why:** The two mental models (managing all clients vs. operating inside one) are fundamentally different tasks. Mixing them in one navigation creates confusion about scope. The top bar handles the "which client am I in?" question. The sidebar handles "what do I do inside this client?".

**Alternative considered:** Single horizontal top nav with workspace as a tab. Rejected: doesn't scale beyond 6 sections, and collapses poorly on smaller screens.

**Risk:** Users who switch between workspaces frequently may find the workspace picker in the top bar slow. Mitigation: Persistent "recent workspaces" in the picker dropdown.

---

### DD-2 — Run Detail Uses Tabs, Not Separate Pages

**Decision:** Results, Reconciliation, Timeline, and Audit Log are tabs on a single Run Detail page, not separate navigable pages.

**Why:** All four views are facets of the same payroll run object. Emeka needs to switch between Results (verify numbers) and Reconciliation (enter payment) and Audit Log (verify approver) without losing context. Tabs keep the run header — status, period, totals — permanently visible.

**Alternative considered:** Separate pages with breadcrumb navigation. Rejected: loses the run summary on every page, requiring Emeka to re-orient each time.

**Risk:** The Results tab is very information-dense (142 employees, expandable rows). Mobile layout needs careful consideration for the tab pattern.

---

### DD-3 — Action Area Is Status-Driven, Single Primary Action

**Decision:** The Run Results page has a contextual action panel below the totals summary. The panel content is completely determined by the current run status. Only one primary action is ever shown.

**Why:** Payroll runs have strict, one-directional state transitions. Showing multiple action buttons (Approve + Retry + Lock) simultaneously would confuse users about what they should do. The status machine dictates the next step — the UI reflects this.

**Alternative considered:** Show all available actions as buttons, disable the inappropriate ones. Rejected: disabled buttons still compete for attention and create confusion. "Why can't I click this?"

**Risk:** Users who don't understand the status progression may not know what to do when they see "Awaiting Lock" with no button visible. Mitigation: Status labels should include brief explanatory text ("Approved. Finance team needs to lock this run.").

---

### DD-4 — PAID Confirmation Dialog Is Intentionally Friction-Heavy

**Decision:** Marking a run as PAID shows a confirmation modal with: a warning icon, a clear statement of irreversibility, the run details (period, workspace, net pay), and a red "Mark as Paid" button.

**Why:** This is the most consequential irreversible action in the system. Loss aversion and peak-end rule both support making this feel serious. The friction is intentional — Emeka should feel the weight of this action.

**Alternative considered:** Simple "Are you sure?" dialog. Rejected: doesn't communicate the specific consequences (no future changes, no undo).

**Risk:** Over-engineered warnings can train users to dismiss dialogs without reading them. Mitigation: Keep the dialog copy specific to what's happening (not generic), short, and factual.

---

### DD-5 — Empty States Always Have an Action

**Decision:** Every list screen has a designed empty state with an icon, an explanation of why it's empty, and a specific next action.

**Why:** Empty states are often the first thing a new user sees. A blank table with "No data" is a dead end. An empty state with context and a CTA is a starting point.

**Example:** Empty runs list for a LIVE workspace says "No payroll runs yet. Add variable inputs and run your first payroll." with a "+ New Run" button.

**Risk:** If the workspace is NOT LIVE, showing a "+ New Run" button in the empty state is misleading. Mitigation: The empty state is context-aware — if not LIVE, it shows "Complete setup to unlock payroll runs" with a "Continue Setup" button instead.

---

### DD-6 — Input Code Dropdown Groups by Category

**Decision:** When Adaeze picks an input type, the dropdown shows codes grouped under EARNING, DEDUCTION, and INFORMATION section headers.

**Why:** A flat alphabetical list of 15 codes is harder to scan than a grouped list. Adaeze thinks in terms of what type of event she's recording. Grouping aids recognition.

**Alternative considered:** Flat list with category shown as text after the code. Rejected: harder to scan for the right code when managing multiple event types at once.

---

### DD-7 — Reconciliation: Expected Total Is the Hero

**Decision:** On the Reconciliation screen, the expected total (from the engine) is displayed in a large card before the input form. The input form asks only for the actual amount — it does not repeat the expected total.

**Why:** Emeka's job is to confirm what the bank disbursed against what the engine said. He has already seen the expected total on the Results page. The reconciliation page anchors on that figure and asks for the one piece of information he needs to provide.

**Alternative considered:** Show expected and actual in side-by-side fields. Rejected: makes the form feel like a dual-entry form when only one field is user-editable.

---

### DD-8 — Inputs Are Framed as an "Inbox"

**Decision:** The payroll inputs screen is titled "Payroll Inputs" with a subtitle "Variable events to be included in the next payroll run" and a pending count ("47 pending").

**Why:** The inbox metaphor positions inputs as things to be processed before running payroll — a checklist mindset. Adaeze is trying to clear her inbox before month-end. This framing aligns with her mental model.

**Alternative considered:** "Variable Pay" as the section name. Rejected: less clear about the workflow connection to the payroll run.

---

## Visual Design Decisions

### DD-9 — Typeface: Sans-Serif with Good Numeric Rendering

**Decision:** Primary typeface will be Inter (or equivalent: DM Sans, Plus Jakarta Sans). This drives two requirements: clear tabular number alignment (for financial figures) and good readability at 14px for dense data tables.

**Why:** Financial data requires tabular figures (equal-width numerals) so that amounts align correctly in columns. Inter provides tabular numeral support via `font-variant-numeric: tabular-nums`. Many display fonts don't.

**Risk:** If the design system requires a custom brand typeface that lacks tabular numerals, a fallback stack must be specified for all monetary amount displays.

---

### DD-10 — Type Scale: 1.200 (Minor Third) Ratio

**Decision:** Use a Minor Third type scale (ratio 1.2) generating: 12, 14, 17, 20, 24, 29, 35px.

**Why:** This is a data-dense enterprise application. The Major Third (1.25) creates too much size contrast — headlines feel oversized next to table content. The Minor Third provides enough hierarchy without visual whiplash.

**Used as:** 12px (labels, secondary) | 14px (body, table rows) | 17px (subheadings, card values) | 20px (section headings) | 24px (page titles) | 29px (KPI numbers) | 35px (hero numbers on bureau dashboard if needed)

---

### DD-11 — Colour Strategy: Neutral-Dominant with Semantic Accents

**Decision:** The UI is 60% neutral (white/grey background), 30% surface (cards, sidebars), 10% accent (primary blue for actions, semantic colours for status).

**Primary action colour:** Professional blue (e.g. #2563EB / Tailwind blue-600)
**Semantic colours:**
- Status CALCULATING/APPROVED: blue variants
- Status PARTIAL/MISMATCH: amber (#D97706)
- Status PAID/MATCHED/SUCCESS: green (#16A34A)
- Status LOCKED: indigo (#4F46E5)
- FAILED/Error/Destructive: red (#DC2626)
- Neutral text: #111827 (near-black) on white backgrounds

**Why:** Payroll is a high-stakes professional domain. Consumer-friendly pastels or bold colour schemes would undermine confidence. Neutral backgrounds make status badges pop — the colour carries semantic meaning, not decoration.

---

### DD-12 — Status Badges Use Both Colour AND Text

**Decision:** Status badges always show a coloured dot + text label. They never rely on colour alone.

**Why:** WCAG 2.1 AA compliance requires that information is not conveyed by colour alone. A red badge without the word "MISMATCH" is inaccessible to users with colour vision deficiency. The text label also removes ambiguity — "PARTIAL" is more specific than an amber dot.

---

### DD-13 — Border-Radius: 8px (Medium SaaS)

**Decision:** Primary border-radius is 8px for cards and modals. 6px for buttons. 4px for inputs. 24px for badges/chips. 0px for table rows (no radius on zebra-style tables).

**Why:** 8px is the "modern professional SaaS" sweet spot. It reads as contemporary without feeling playful. Smaller radii (0–4px) feel dated or harsh. Larger radii (16px+) feel consumer/mobile. Consistent values create unconscious trust.

---

### DD-14 — Spacing: 8pt Grid

**Decision:** All spacing uses multiples of 8px: 4, 8, 12, 16, 24, 32, 48, 64, 96px.

**Key spacings:**
- Between sidebar items: 4px
- Sidebar section gap: 24px
- Card padding: 24px
- Between cards: 24px (gap === padding at top level — exception to the rule, justified by the card container's border)
- Between form fields: 16px (gap must exceed label-to-input gap of 4px)
- Between table rows: content height (40px per row), no additional gap — rows use background colour for separation

---

### DD-15 — Responsive Strategy: Desktop-Primary, Mobile-Aware

**Decision:** This is a professional tool used on desktop at the office (Adaeze, Emeka). Design desktop-first at 1280px and 1440px wide. Ensure mobile (375px) is usable but not the primary experience.

**Why:** Payroll bureau operators work at desks. The data density required (employee results tables, component traces, reconciliation forms) is not suited to a mobile-first design. Forcing mobile-first would compromise the desktop experience.

**Mobile treatment:** Sidebar collapses to bottom tab bar or hamburger drawer. Tables become card views. Totals summary becomes scrollable horizontal strip. Export buttons remain accessible.

**Tablet (768–1024px):** Sidebar collapses to icon-only. Main content expands. Two-column layouts collapse to one.

---

### DD-16 — Dark Mode Is Planned but Not Gate 2 Scope

**Decision:** The design token system (Gate 2) will define both light and dark palettes, but only the light theme is implemented in Gate 3. Dark mode can be enabled by swapping token values.

**Why:** Building tokens correctly from the start means dark mode is a toggle, not a rewrite. Doing it later without tokens means duplicating all styles.

---

## Interaction and Motion Decisions

### DD-17 — Expandable Table Rows: 200ms Ease-Out

**Decision:** Employee pay breakdown rows expand with a smooth 200ms ease-out animation. Height animates from 0 to content height using CSS grid rows (not max-height, which flickers).

**Why:** `max-height` animation is an anti-pattern — it jumps at the end of the animation when max-height is much larger than the content. Grid row expansion is the correct technique. 200ms is long enough to communicate that something happened, short enough not to feel slow.

---

### DD-18 — Run Polling: Every 5 Seconds on CALCULATING Status

**Decision:** When the Payroll Runs list shows a CALCULATING run, the page polls the run status endpoint every 5 seconds. When status changes, update the badge and show a toast.

**Why:** The run calculation may be synchronous and slow (see DRIFT-5). The user cannot know when it completes without either manually refreshing or polling. 5s is frequent enough to feel responsive without hammering the server.

**Alternative:** WebSocket real-time update. Deferred — not currently in the backend. Polling is the correct approach for now.

---

## Risks and Open Questions

### RISK-1 — Auth / Identity
No RBAC is implemented. The "Approve Run" button will be visible to any logged-in user, including Adaeze, who should not be able to approve her own run. If the platform launches without RBAC, document this gap prominently in the UI ("Note: user permissions are not yet enforced. All users have full access.").

### RISK-2 — Payroll Calculation Performance
Run creation may block for 30–90 seconds (DRIFT-5). The UI must handle this with a persistent progress state. If the connection drops mid-calculation, the idempotency key should allow the frontend to re-check whether the run was actually created.

### RISK-3 — Personal Data Display
`personal_details_encrypted` may not be encrypted (DRIFT-1). Bank account numbers are displayed directly in the Bank Upload CSV. The UI should not display raw account numbers on-screen — mask them (e.g. ****1234) except in the downloaded CSV. This needs security sign-off before Gate 3.

### RISK-4 — Missing Template Download Endpoint
No endpoint exists to serve a blank CSV template for bulk input uploads (DRIFT-9). Gate 2/3 must either embed the template as a static asset in the frontend, or a new backend endpoint must be added.

### RISK-5 — BureauDashboard Content
The exact content of `BureauDashboard.tsx` was not read in full (DRIFT-8). The S1 wireframe is based on reasonable inference from the IA and domain context. Verify against the actual component before Gate 3 implementation of S1.
