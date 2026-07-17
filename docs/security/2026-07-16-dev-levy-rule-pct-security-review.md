# Security Review — `dev-levy-rule-pct` — 2026-07-16

**Reviewer:** Claude Code (`/security` skill)
**Scope:** `backend/api/routes/workspace.py` — `patch_component_override`, `list_platform_components` (diff only, per plan §5)

---

## Findings

### Medium — merge-not-replace increases the persistence of an unvalidated `overrides_json` key injection

**Location:** `backend/api/routes/workspace.py:1348-1374` (`patch_component_override`)

**Attack vector:** `payload.get("overrides_json")` is an untyped `dict` — no Pydantic schema constrains its keys. `_validate_override_amount` only runs against the single key named by this component's `workspace_override_key` (e.g. `amount`, `employee_rate`). Any other key in the caller's `overrides_json` (e.g. `component_class`, `is_pensionable`, `flat_amount` — real keys read elsewhere in the engine per this repo's documented data-contract rules) is merged into `client_component_metadata.overrides_json` with no validation at all.

This acceptance of arbitrary keys is **pre-existing**, not introduced by this diff — the prior wholesale-replace implementation had the same lack of a key allowlist. What this diff changes is the *blast radius*: under the old wholesale-replace semantics, a stray/malicious key was overwritten the next time any legitimate amount-only PATCH fired. Under the new merge-not-replace semantics (`{**existing_overrides, **incoming_overrides}`), a key not present in a later PATCH's payload survives indefinitely — an injected `component_class` override, for instance, would now persist across every subsequent unrelated edit to that component's override record until someone explicitly nulls it out.

**Impact:** A caller (any caller — see "no auth" note below) could set `component_class: "non_taxable"` on a component that should be taxable, silently changing its GROSS_PAY/NET_PAY/PAYE treatment per the `component_class` invariants in this repo's `CLAUDE.md`, and that change would now outlive future legitimate amount edits instead of being wiped by the next save.

**Fix:** Add an explicit allowlist of keys `patch_component_override` will merge from `overrides_json` (at minimum: the component's own `workspace_override_key`, plus any other keys this endpoint is intentionally designed to let operators set). Reject or silently drop any other key. This is a hardening item, not a blocker — worth a follow-up story, not a re-open of this sprint, since no evidence in this diff or its tests exercises this path maliciously and the field is only reachable from the internal admin UI today.

### Checked, no issue

- **SQL injection:** all queries are parameterized (`text(...)` with bound `:params`); `component_code.upper()` and `workspace_id` never concatenated into SQL. ✅
- **`str(e)` / exception-string leakage:** the outer `except Exception as e` logs the raw exception server-side (`_log.error(...)`) and returns a generic `"Failed to update component override"` — matches the standing prohibition. ✅
- **JSONB cast pattern:** `CAST(:overrides AS jsonb)` used, not `::jsonb` string interpolation — matches this repo's known SQLAlchemy pitfall (`feedback_sqlalchemy_jsonb_cast`). ✅
- **Decimal for money:** `_validate_override_amount` constructs `Decimal(str(value))`, never float; malformed input is caught and converted to a generic 422 (no `str(e)` leak) rather than raising. ✅
- **Amount range validation:** the validated key is bounded `0 <= amount <= 10,000,000` — rejects negative amounts before persistence, closing the "can a negative input flip a deduction into an addition" checklist item for the one key this endpoint is designed to control. ✅
- **Explicit-null-deletes-key convention:** confirmed it can only delete individual keys present in the incoming payload — a bare `overrides_json: {}` cannot wipe unrelated keys, matching the documented merge-not-replace intent. ✅
- **`list_platform_components` new field (`workspace_override_key`):** exposes an internal config key name (e.g. `"employee_rate"`), not a secret or PII — needed by the frontend to route the Amount Override field. Low sensitivity, no action needed.
- **Workspace/component validation (D-ARCH-8):** `component_code` is validated against `component_metadata` scoped to the workspace's own `country_code` before any write — a caller cannot write an override for a component code that doesn't exist for this workspace's country. ✅
- **New dependencies / secrets:** none introduced.

### Observations (pre-existing, out of this diff's scope — flagged for the backlog)

- **No authentication/authorization on this route file, or apparently anywhere in the API** (`grep` for `Depends`/auth patterns across `backend/api/main.py` and `backend/api/routes/workspace.py` returns nothing beyond CORS middleware). This means the Medium finding above is reachable by anyone who can reach the API, not just an authorized operator. This is a systemic, repo-wide gap predating this sprint by a wide margin — not something to fix inside this sprint, but it should be on record as the reason the Medium finding above isn't Low.
- **Read-modify-write race on `overrides_json` merge:** two concurrent PATCH calls for the same `(workspace_id, component_code)` could race between the `SELECT existing_overrides` and the `INSERT ... ON CONFLICT DO UPDATE`, silently losing one caller's key. Low severity given this is a single-operator admin panel today; would need a transaction-level lock (`SELECT ... FOR UPDATE`) or a JSONB merge expressed directly in the `UPDATE ... SET overrides_json = overrides_json || :incoming` to close fully. Not a blocker.

## Verdict

**PASS, with one Medium hardening item logged for the backlog (not a blocker for this sprint).** No new critical/high risk introduced by this diff. The amount-validation and merge-semantics work matches the plan's intent; the one finding above is a scope-widening consequence of the merge-not-replace fix that's worth a follow-up story, not a re-open.
