"""
Rules Context Snapshot Builder.

Captures a deterministic, fully self-contained record of which rules were
applied during a payroll run.  The snapshot is stored on the PAYROLL_RUN row
so that retries and audits can reconstruct exactly what ran without issuing
any live DB queries against rule tables.

Two formats are emitted:

  snapshot_version 1 (legacy)
    Produced when rule_set_id is not provided.  Stores only IDs — used by
    old runs that pre-date temporal rule versioning.

  snapshot_version 2 (full content)
    Produced when rule_set_id is provided.  Embeds the full statutory config,
    tax bands, run rule set items, and all historical rule sets used for
    cross-period inputs.  Sufficient for complete replay without DB access.

No database access — payload construction only.
"""
from __future__ import annotations


def build_rules_context_snapshot(
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str] | None = None,
    *,
    # ── v2 full-content parameters ────────────────────────────────────────────
    # All keyword-only.  When rule_set_id is provided every other v2 param
    # must also be provided; the function raises ValueError if any is absent.
    statutory_effective_from: str | None = None,
    statutory_rules_jsonb: dict | None = None,
    statutory_tax_bands: list | None = None,
    rule_set_id: str | None = None,
    rule_set_effective_from: str | None = None,
    rule_set_items: list[dict] | None = None,
    historical_rule_sets: list[dict] | None = None,
) -> dict:
    """Build a rules context snapshot for a payroll run.

    Args:
        statutory_rule_id:
            UUID of the statutory rule applied (e.g. PAYE bands).
        statutory_version:
            Integer version of the statutory rule at time of run.
        payroll_rule_ids:
            List of workspace payroll rule UUIDs (v1 format only).

        -- v2 keyword-only params --
        statutory_effective_from:
            ISO date string of the statutory rule's effective_from.
        statutory_rules_jsonb:
            Full rules_jsonb dict from the statutory_rule row.
        statutory_tax_bands:
            List of tax band dicts used for PAYE calculation.
        rule_set_id:
            UUID of the rule set used for this run.  Presence of this param
            triggers v2 format emission.
        rule_set_effective_from:
            ISO date string of the rule set's effective_from.
        rule_set_items:
            List of rule item dicts [{rule_name, rule_type,
            rule_definition_json}] from the run's rule set.
        historical_rule_sets:
            List of dicts [{id, effective_from, items}] — one entry per
            distinct historical rule set used for cross-period inputs.
            Must be [] (not None) when no cross-period inputs are present.

    Returns:
        Dict suitable for storage in PAYROLL_RUN.rules_context_snapshot.

    Raises:
        ValueError: If rule_set_id is provided but any other v2 param is None.
    """
    # ── v2: full-content snapshot ─────────────────────────────────────────────
    if rule_set_id is not None:
        missing = [
            name for name, val in [
                ("statutory_effective_from", statutory_effective_from),
                ("statutory_rules_jsonb",    statutory_rules_jsonb),
                ("statutory_tax_bands",      statutory_tax_bands),
                ("rule_set_effective_from",  rule_set_effective_from),
                ("rule_set_items",           rule_set_items),
                ("historical_rule_sets",     historical_rule_sets),
            ]
            if val is None
        ]
        if missing:
            raise ValueError(
                f"build_rules_context_snapshot: v2 params required when "
                f"rule_set_id is provided but missing: {missing}"
            )

        return {
            "snapshot_version": 2,
            "statutory_rule": {
                "id":             statutory_rule_id,
                "version":        statutory_version,
                "effective_from": statutory_effective_from,
                "rules_jsonb":    statutory_rules_jsonb,
                "tax_bands":      statutory_tax_bands,
            },
            "rule_set": {
                "id":             rule_set_id,
                "effective_from": rule_set_effective_from,
                "items":          rule_set_items,
            },
            "historical_rule_sets": historical_rule_sets,
        }

    # ── v1: legacy ID-only snapshot (backward compatible) ────────────────────
    return {
        "statutory_rule": {
            "id":      statutory_rule_id,
            "version": statutory_version,
        },
        "payroll_rules": payroll_rule_ids or [],
    }
