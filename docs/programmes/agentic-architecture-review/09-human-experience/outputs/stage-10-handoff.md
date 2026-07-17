# Stage 09 → Stage 10 Handoff (Evaluation & Assurance)

Stage 08's handoff gave Stage 10 the mechanism-level verification hooks; this handoff adds the **UX-testable behaviours** — observable interface behaviours whose failure would break a designed guarantee even if the mechanism beneath is correct. Each names its design source; Stage 10 owns methodology.

## Boundary and refusal behaviours (C3)

1. **Five-condition refusal rendering** (`assistant-boundary-experience.md` §2): each condition produces its specified copy pattern; the historical-refusal answers as a refusal ~100% of the time on the eval set (Stage 04 safety metric); the null-trace refusal uses the verbatim contract text.
2. **No existence disclosure in copy**: cross-workspace and genuine not-found produce byte-identical response shapes at the UI layer — testable by fixture pair.
3. **Grounding footer completeness**: every substantive answer's "Based on" chips correspond 1:1 to the session's logged tool calls (`tool_call_log` rows) — no chip without a call, no consumed call without a chip.
4. **No confirm control in chat**: DOM/UI assertion that proposal cards in chat contain no confirmation action (T7) — the control exists only on the pending-actions surface.

## Confirmation surface (C10)

5. **Frozen-payload rendering** (`confirmation-experience.md` §2): fixture where chat text/agent restatement differs from `payload_jsonb` → the card renders payload values only.
6. **All four terminal states render** their specified presentations; INVALIDATED shows both states; EXPIRED copy asserts nothing executed.
7. **Double-submit convergence**: two rapid confirms (or two tabs) → one execution, both screens render the recorded outcome with the explanatory banner on the loser.

## Statutory approval (C12)

8. **Evidence-set completeness before decision**: the approve control is unreachable unless citation, diff, validation results and impact preview are all rendered (field-presence at the UI layer mirroring `payload_as_presented_jsonb` completeness).
9. **Step-up moment**: approve without fresh step-up → modal; expired/consumed event → re-prompt with the specified copy, no partial submission.
10. **Rejection requires reasoning**: empty reasoning blocks submission client- and server-side.
11. **Correction proposals**: consumed-runs statement and the required recalculation decision control render; approval without that selection is blocked.
12. **Own-proposal state**: proposer sees approve disabled with the stated reason (segregation pending DQ-007).

## Exception queue and notifications

13. **Badge/count exclusions**: shadow-mode C7 records excluded from the sidebar badge and open counts; visible only under the shadow toggle with the calibration marker.
14. **Suggested-vs-fact separation**: `recommended_action` renders in the labelled suggestion container, never inside the evidence region (DOM-level assertion).
15. **Frozen evidence**: correcting the underlying data does not change the rendered `evidence_jsonb` of the existing record.
16. **Dismiss friction**: dismissal path re-presents the evidence summary before confirm (the anti-reflex check backing the dismiss-without-review metric).
17. **Notifications are pointers**: no action other than navigation exists in the notification panel; resolving an exception never touches notification read state and vice versa.

## Onboarding flow (C13/C14)

18. **Proposal semantics**: no mapping commits without operator confirmation; low-confidence rows sort first; original header text visible on every mapped row.
19. **Dry-run distinctness**: dry-run results never appear in the Runs list; the no-payroll-created banner renders on every results view.
20. **Hash-gate UX**: editing staged rows post-dry-run disables Commit with the re-run message; server rejection on hash mismatch renders the same state (two-layer agreement).
21. **Upload/Enroll separation**: the committed import sends no `grade_code` to employee creation (existing standing rule, now with a UI flow that must keep honouring it).

## Auth and audit surfaces

22. **Switch-as-context-change**: workspace switch tears down workspace state (no stale data from the previous workspace renders post-switch — the P6 UX property).
23. **Pre-epoch labelling**: fixture rows either side of `auth_cutover_epoch` render labelled/unlabelled respectively, on every audit surface, including exports (extends Stage 08's epoch fixture test to the presentation layer).
24. **Uniform 404 surface**: member vs non-member deep links produce switch vs not-found with no distinguishing copy.
25. **Uniform login errors**: wrong-password and unknown-email produce identical UI states.

## Carried context

- The measurement framework's C3 volume-metric prohibition applies to any UX analytics Stage 10 proposes (no messages-per-operator success metrics).
- DQ-005 recommendation and its test implications live in `stage-11-handoff.md` — if CORRECTION gains contextual UI exposure later, behaviours for it are a Phase 3 addendum, not pre-designed here.
- The notification read-state single-operator posture (`notification-experience.md` §2) is a stated v1 constraint — Stage 10 should not write multi-operator read-state assurances against v1.
