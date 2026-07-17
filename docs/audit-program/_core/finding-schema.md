# Finding Schema

Every finding, in every stage's `findings.md` (or Stage 10's
`remediation-log.md`), must use this exact field set. Do not add narrative
outside these fields, and do not merge fields — the three-way split between
current implementation, intended behaviour, and defect status is the point:
it keeps what-is, what-should-be, and what-might-be-wrong from blurring
into one claim.

## Fields

| Field | Description |
|---|---|
| `id` | Stage-scoped identifier, e.g. `01-003`. |
| `stage` | Stage number and name, e.g. `01-system-inventory`. |
| `location` | File(s)/table(s)/route(s) the finding concerns — `file:line` where applicable. |
| `current implementation` | What the code/config/schema actually does today, stated factually, with a code or evidence citation. No interpretation here. |
| `intended behaviour` | What it should do — sourced from `CLAUDE.md`, the business rules catalogue, a migration comment, or an explicit human decision. Cite the source. If no authoritative source states the intended behaviour, say so explicitly rather than inferring one. |
| `suspected or confirmed defect` | The gap between the two rows above, stated as a hypothesis if unconfirmed, or as a demonstrated fact if confirmed. Never combine this with the "current implementation" row. |
| `evidence` | Relative path(s) into `evidence/`, or a direct `file:line` reference, per `evidence-standard.md`. |
| `status` | `unconfirmed` / `plausible` / `confirmed` / `rejected` — per `evidence-standard.md`. |
| `severity` | `S0` / `S1` / `S2` / `S3` — per `severity-model.md`. |
| `related invariant` | The `CLAUDE.md` data-contract invariant or standing rule this touches, if any. Leave blank if none. |

## Template

```markdown
### <id> — <one-line summary>

- **stage:** <stage-number>-<stage-name>
- **location:** <file:line / table / route>
- **current implementation:** <factual statement + citation>
- **intended behaviour:** <statement + source, or "no authoritative source found">
- **suspected or confirmed defect:** <the gap, as hypothesis or demonstrated fact>
- **evidence:** <path(s) or file:line>
- **status:** unconfirmed | plausible | confirmed | rejected
- **severity:** S0 | S1 | S2 | S3
- **related invariant:** <CLAUDE.md invariant, or "none">
```

## Do not duplicate business rules here

If a finding concerns a specific statutory rule or calculation invariant,
cite it from `CLAUDE.md`'s invariant table or
`docs/analysis/0.5-business-rules-catalogue.md` — do not restate the rule's
definition inside the finding.
