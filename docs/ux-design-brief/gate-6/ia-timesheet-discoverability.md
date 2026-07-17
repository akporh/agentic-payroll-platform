   1 # IA Decision Record: Timesheet Mode Discoverability
   2 
   3 **Date:** 2026-05-21
   4 **Status:** Decision made — Option B selected, Option A as interim step
   5
   6 ---
   7
   8 ## Problem
   9
  10 A payroll bureau operator setting up a new client workspace cannot find the "Timesheet Mode" toggle intuitively. The c
     urrent path requires:
  11
  12 ```
  13 Config page → OT & Holidays tab → Edit slide-over → scroll to bottom → toggle
  14 ```
  15
  16 That is 4 interactions to reach a binary feature switch. No visible label on the Config page or in the sidebar indicat
     es that "Timesheet Mode" exists as a configurable option.
  17
  18 **Root cause:** Timesheet Mode is a workspace-level feature flag, but it is grouped semantically with OT and public ho
     liday *rules*. The tab label "OT & Holidays" has zero information scent pointing toward timesheet configuration.
  19
  20 **Secondary problem (chicken-and-egg):** The Attendance Configuration page (`/attendance-configuration`) has a route b
     ut no sidebar entry. It is only surfaced via an in-page link *after* timesheet is already enabled — meaning a user who
      doesn't know timesheets exist cannot navigate there.
  21
  22 ---
  23
  24 ## Current Sidebar Structure
  25
  26 ```
  27 PAYROLL
  28   Runs
  29   Inputs
  30
  31 PEOPLE
  32   Employees
  33
  34 SETTINGS
  35   Configuration
  36   Public Holidays
  37   Rate Codes
  38
  39 [Setup Wizard]  (shown when workspace is not LIVE)
  40 ```
  41
  42 ---
  43
  44 ## Options Evaluated
  45
  46 ### Option A — Minimal (surface as top-level Config card)
  47 Move the Timesheet Mode toggle out of the OT & Holidays slide-over and display it as a standalone card on the Configur
     ation page, at the same tier as Pay Cycle.
  48
  49 - Pros: no new routes, no sidebar changes, very low risk
  50 - Cons: still no sidebar entry; Attendance Configuration page remains orphaned
  51
  52 ### Option B — First-class sidebar entry (selected)
  53 Add "Attendance" as a standalone sidebar item under Settings. The Attendance page becomes a unified area covering:
  54 1. Timesheet Mode toggle (top of page, with enable/disable confirmation)
  55 2. Attendance code configuration (currently at `/attendance-configuration` but orphaned)
  56 3. Link to timesheet upload (`/timesheet`)
  57
  58 - Pros: navigation convention makes the feature discoverable; Attendance Configuration is no longer orphaned; aligns w
     ith the architectural direction (see below)
  59 - Cons: slightly more work; needs a new unified page or the existing AttendanceConfiguration page promoted and expande
     d
  60
  61 ### Option B sidebar structure
  62 ```
  63 SETTINGS
  64   Configuration
  65   Public Holidays
  66   Rate Codes
  67   Attendance          ← new
  68 ```
  69
  70 ---
  71
  72 ## Decision: Option B
  73
  74 **Rationale:** Option A fixes discoverability of the toggle but leaves the Attendance Configuration page orphaned and
     treats Attendance as a sub-setting of OT configuration. Option B promotes Attendance to a first-class concept in the n
     avigation, which correctly reflects its scope — it is not a sub-setting, it is a distinct operational area. This also
     aligns with the architectural direction articulated below.
  75
  76 **Implementation notes:**
  77 - The Timesheet Mode toggle should remain on the Attendance page, not the Configuration page
  78 - The OT & Holidays edit slide-over should drop the Timesheet section entirely once the Attendance page exists
  79 - The "Manage attendance codes →" link inside OT & Holidays (currently conditional on `timesheet_enabled`) should be r
     eplaced with a persistent sidebar link
  80 - Timesheet Mode enable/disable is a consequential action (seeds attendance codes) — confirm with a dialog, not a bare
      toggle
  81
  82 ---
  83
  84 ## Architectural Context
  85
  86 See `docs/planning/period-data-ingestion-vision.md` for the longer-term architectural direction that shapes why Attend
     ance deserves its own navigation area.
  87
  88 The short version: the system is moving toward consuming *period data bundles* (employee roster + events + attendance)
      rather than housing employees as a standing record. Attendance — including the timesheet upload — is the primary inge
     st surface for that bundle for timesheet-enabled clients. Elevating it in the nav reflects that it is an *operational*
      area, not a *settings* area.