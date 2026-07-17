"""
Rules Context Snapshot Builder.

Captures a deterministic, fully self-contained record of which rules were
applied during a payroll run.  The snapshot is stored on the PAYROLL_RUN row
so that retries and audits can reconstruct exactly what ran without issuing
any live DB queries against rule tables.

Two formats are emitted:

  snapshot_version 1 (legacy)
    Produced when the caller supplies no statutory v2 content at all (very
    old callers). Stores only statutory IDs — insufficient for retry to
    recalculate from (see audit finding 04-001).

  snapshot_version 2 (full content)
    Produced whenever full statutory content (rules_jsonb, tax_bands, etc.)
    is supplied. Embeds the full statutory config, tax bands, and — when the
    workspace has one — the run's rule set items and historical rule sets
    used for cross-period inputs. A workspace with no published rule_set
    (no payroll rule carries an effective_from) still gets a v2 snapshot:
    "no custom payroll rules configured" is a normal, common workspace
    state, not a reason to withhold the statutory content retry depends on.
    v2 emission was originally (incorrectly) coupled to rule_set_id
    presence — see audit finding 04-001's remediation
    (docs/audit-program/remediation/04-001-05-001/summary.md) for why the
    two concerns were decoupled: statutory obligations (PAYE, pension, etc.)
    apply to every workspace regardless of whether it has any custom
    payroll rules.

No database access — payload construction only.
"""
from __future__ import annotations


def build_rules_context_snapshot(
    statutory_rule_id: str,
    statutory_version: int,
    payroll_rule_ids: list[str] | None = None,
    *,
    # ── v2 full-content parameters ────────────────────────────────────────────
    # All keyword-only. When statutory_rules_jsonb (and the other statutory
    # v2 params) are provided, v2 format is emitted regardless of whether
    # this workspace has a published rule_set — see module docstring.
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
            Presence (not None) of this, statutory_rules_jsonb, and
            statutory_tax_bands together triggers v2 format emission.
        statutory_rules_jsonb:
            Full rules_jsonb dict from the statutory_rule row.
        statutory_tax_bands:
            List of tax band dicts used for PAYE calculation.
        rule_set_id:
            UUID of the rule set used for this run, if the workspace has
            one published. May be None — a workspace with no custom
            payroll rules still gets a v2 snapshot with `"rule_set": None`.
        rule_set_effective_from:
            ISO date string of the rule set's effective_from. Required only
            when rule_set_id is provided.
        rule_set_items:
            List of rule item dicts [{rule_name, rule_type,
            rule_definition_json}] from the run's rule set. Required only
            when rule_set_id is provided.
        historical_rule_sets:
            List of dicts [{id, effective_from, items}] — one entry per
            distinct historical rule set used for cross-period inputs.
            Must be [] (not None) when no cross-period inputs are present.
            Always required for v2 emission (independent of rule_set_id).

    Returns:
        Dict suitable for storage in PAYROLL_RUN.rules_context_snapshot.

    Raises:
        ValueError: If the statutory v2 params are provided but incomplete,
            or if rule_set_id is provided but rule_set_effective_from/
            rule_set_items are not.
    """
    # ── v2: full-content snapshot ─────────────────────────────────────────────
    # Triggered by statutory content OR rule_set_id — deliberately not just
    # rule_set_id alone (audit finding 04-001 remediation; a workspace with
    # zero custom payroll rules, hence no rule_set_id, must still get its
    # statutory content frozen). Also not statutory content alone: a caller
    # that passes rule_set_id without statutory content is still a v2-format
    # request and must go through the same required-params validation below,
    # rather than silently falling through to a v1 snapshot that drops the
    # rule_set_id entirely.
    _v2_requested = (
        statutory_effective_from is not None
        or statutory_rules_jsonb is not None
        or statutory_tax_bands is not None
        or rule_set_id is not None
    )

    if _v2_requested:
        missing = [
            name for name, val in [
                ("statutory_effective_from", statutory_effective_from),
                ("statutory_rules_jsonb",    statutory_rules_jsonb),
                ("statutory_tax_bands",      statutory_tax_bands),
                ("historical_rule_sets",     historical_rule_sets),
            ]
            if val is None
        ]
        if rule_set_id is not None:
            missing += [
                name for name, val in [
                    ("rule_set_effective_from", rule_set_effective_from),
                    ("rule_set_items",          rule_set_items),
                ]
                if val is None
            ]
        if missing:
            raise ValueError(
                f"build_rules_context_snapshot: v2 params required but missing: {missing}"
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
            "rule_set": (
                {
                    "id":             rule_set_id,
                    "effective_from": rule_set_effective_from,
                    "items":          rule_set_items,
                }
                if rule_set_id is not None else None
            ),
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
