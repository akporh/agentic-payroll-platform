# Finding Schema

Every finding recorded in any stage's `findings.md` must use this schema. Draft and confirmed findings are kept in visually separate sections of the file — a reader must never have to infer status from prose alone.

## `findings.md` structure

```markdown
## Draft Findings

(hypotheses / observations not yet confirmed — MUST NOT be cited by other stages)

### D-<stage-prefix>-<n>: <short title>
...fields as below...

---

## Confirmed Findings

(meet the evidence standard — safe to cite from later stages)

### F-<stage-prefix>-<n>: <short title>
...fields as below...

---

## Parked / Rejected

### P-<stage-prefix>-<n>: <short title>
- **Reason parked/rejected**: ...
```

## Required fields per finding

| Field | Description |
|---|---|
| **ID** | `D-` (draft), `F-` (confirmed), or `P-` (parked/rejected) + stage prefix (e.g. `01`) + sequence number |
| **Title** | Short, neutral, one line |
| **Current implementation** | What actually happens today. Cited to evidence. Leave blank / "not yet observed" if not established. |
| **Intended design** | What the design intent was, and its source (spec/ticket/CLAUDE.md/human statement). State "undocumented" if no source exists — do not infer. |
| **Identified gap** | The delta between the two, stated neutrally. State "none" if implementation matches intent. |
| **Evidence** | Citation(s) per `EVIDENCE-STANDARD.md` — file path, `evidence/` filename, or human decision reference |
| **Severity** | Per `SEVERITY-MODEL.md` — only required on confirmed findings |
| **Status** | `draft` / `confirmed` / `parked` / `rejected` |
| **Date** | Date the finding was recorded or last updated |
| **Raised by** | Stage and, if applicable, sub-investigation |

## Promotion rule

A finding moves from `D-` to `F-` (renumbered accordingly) only when:

1. All three of current implementation / intended design / identified gap are populated (or explicitly marked "undocumented" / "none" where genuinely applicable).
2. At least one evidence citation meets `EVIDENCE-STANDARD.md`.
3. The promotion itself is noted in the stage's `decisions.md` if it required a judgment call (e.g. adjudicating conflicting evidence).

A `D-` finding is never silently deleted — if it turns out to be wrong or irrelevant, it moves to `Parked / Rejected` with a one-line reason, preserving the audit trail.

## Cross-stage citation rule

Later stages may cite `F-` findings from earlier stages by ID (e.g. "per F-01-03..."). Later stages must never cite a `D-` or `P-` finding from another stage as though it were established fact.
