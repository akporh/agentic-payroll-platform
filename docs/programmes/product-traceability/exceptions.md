# Exceptions — Product Traceability Programme

Structured log of stop-condition events, per `POLICY.md`'s "Stop conditions" list. Use the schema below for each entry. If no exception occurred during a phase, that is stated explicitly rather than leaving this file silent.

## Schema

```text
Exception ID:
Phase:
Type:
Evidence:
Affected items:
Options:
Executor recommendation:
Effect of deferral:
Exact human decision required:
```

---

## Discovery phase (Phase 1)

**No exception occurred during the discovery phase.**

None of the seven stop conditions in `POLICY.md` were triggered:

- Authoritative sources did not materially contradict one another in a way that could not be resolved by reading further. Where `docs/ROADMAP.md` marks an item ✅ with only a narrative reference (no separate test-report line), this was recorded as `strongly inferred` rather than `confirmed`, and as an unresolved question where the gap was material — not escalated as a contradiction.
- No sensitive or personal information was discovered in the inspected documentation (no PII, credentials, or client-confidential financial data appeared in the roadmap, story files, audit reports, or test reports reviewed).
- The phase was completed within the authorised paths (`docs/diagnostics/`, `docs/programmes/product-traceability/`); no attempt to write outside them was needed.
- No destructive or irreversible change was required — all outputs are new files.
- All requested evidence was accessible (repository files and git history were readable; no external system access was required).
- Fewer than 10% of identified items required `requires human classification` — see the discovery document's confidence summary; the great majority classified at least `tentative` or higher.
- No validation failed in a way that could not be corrected within scope.

If a future amendment pass (post-critic-review) surfaces a stop condition, it will be appended below as a new dated entry rather than overwriting this statement.
