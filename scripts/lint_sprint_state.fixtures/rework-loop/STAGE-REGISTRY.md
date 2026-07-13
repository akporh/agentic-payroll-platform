# Stage Registry (fixture)

Synthetic, self-contained registry used only by `scripts/lint_sprint_state.py`'s
fixture tests. Deliberately smaller than and independent of the real
`docs/sprints/STAGE-REGISTRY.md` so fixture tests never drift if the real
registry changes. Mirrors the real registry's two notable parallel-
compatibility shapes: a symmetric positive pair (`verification`/`security`)
and a symmetric explicit prohibition (`implementation`/`audit`).

7 stage IDs: `roadmap`, `pm`, `implementation`, `verification`, `security`,
`audit`, `test`.

---

## `roadmap`

| Field | Value |
|---|---|
| Mandatory status | mandatory |
| Parallel compatibility | None |

## `pm`

| Field | Value |
|---|---|
| Mandatory status | mandatory |
| Parallel compatibility | None |

## `implementation`

| Field | Value |
|---|---|
| Mandatory status | mandatory |
| Parallel compatibility | None with `audit` (must never run concurrently with `audit`) |

## `verification`

| Field | Value |
|---|---|
| Mandatory status | conditional |
| Parallel compatibility | `security` |

## `security`

| Field | Value |
|---|---|
| Mandatory status | conditional |
| Parallel compatibility | `verification` |

## `audit`

| Field | Value |
|---|---|
| Mandatory status | conditional |
| Parallel compatibility | None — must never run concurrently with `implementation` |

## `test`

| Field | Value |
|---|---|
| Mandatory status | mandatory |
| Parallel compatibility | None declared |
