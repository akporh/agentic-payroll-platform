import pytest
from backend.domain.rules.snapshot import build_rules_context_snapshot


# ---------------------------------------------------------------------------
# v1 legacy format (no rule_set_id)
# ---------------------------------------------------------------------------

def test_v1_format_returns_id_only():
    result = build_rules_context_snapshot(
        statutory_rule_id="rule2026",
        statutory_version=1,
        payroll_rule_ids=["r1", "r2"],
    )
    assert result == {
        "statutory_rule": {
            "id": "rule2026",
            "version": 1,
        },
        "payroll_rules": ["r1", "r2"],
    }


def test_v1_format_empty_rule_ids():
    result = build_rules_context_snapshot(
        statutory_rule_id="sr-1",
        statutory_version=3,
    )
    assert result["payroll_rules"] == []
    assert "snapshot_version" not in result


# ---------------------------------------------------------------------------
# v2 full-content format (rule_set_id provided)
# ---------------------------------------------------------------------------

STAT_RULE_ID    = "sr-001"
STAT_VERSION    = 5
RULE_SET_ID     = "rs-abc"
TAX_BANDS       = [{"lower_limit": 0, "upper_limit": 300000, "rate": "0.07"}]
RULES_JSONB     = {"pension": {"employee_rate": "0.08", "employer_rate": "0.10"}}
RULE_SET_ITEMS  = [
    {"rule_name": "OVERTIME_PAY", "rule_definition_json": {"rate": 5000}, "rule_type": None}
]


def test_v2_format_full_content():
    result = build_rules_context_snapshot(
        statutory_rule_id        = STAT_RULE_ID,
        statutory_version        = STAT_VERSION,
        statutory_effective_from = "2024-01-01",
        statutory_rules_jsonb    = RULES_JSONB,
        statutory_tax_bands      = TAX_BANDS,
        rule_set_id              = RULE_SET_ID,
        rule_set_effective_from  = "2024-01-01",
        rule_set_items           = RULE_SET_ITEMS,
        historical_rule_sets     = [],
    )

    assert result["snapshot_version"] == 2
    assert result["statutory_rule"]["id"]             == STAT_RULE_ID
    assert result["statutory_rule"]["version"]        == STAT_VERSION
    assert result["statutory_rule"]["effective_from"] == "2024-01-01"
    assert result["statutory_rule"]["rules_jsonb"]    == RULES_JSONB
    assert result["statutory_rule"]["tax_bands"]      == TAX_BANDS
    assert result["rule_set"]["id"]                   == RULE_SET_ID
    assert result["rule_set"]["effective_from"]       == "2024-01-01"
    assert result["rule_set"]["items"]                == RULE_SET_ITEMS
    assert result["historical_rule_sets"]             == []


def test_v2_format_with_historical_rule_sets():
    historical = [
        {
            "id": "rs-prev",
            "effective_from": "2023-01-01",
            "items": [
                {"rule_name": "OVERTIME_PAY", "rule_definition_json": {"rate": 4500}, "rule_type": None}
            ],
        }
    ]
    result = build_rules_context_snapshot(
        statutory_rule_id        = STAT_RULE_ID,
        statutory_version        = STAT_VERSION,
        statutory_effective_from = "2024-01-01",
        statutory_rules_jsonb    = RULES_JSONB,
        statutory_tax_bands      = TAX_BANDS,
        rule_set_id              = RULE_SET_ID,
        rule_set_effective_from  = "2024-01-01",
        rule_set_items           = RULE_SET_ITEMS,
        historical_rule_sets     = historical,
    )
    assert len(result["historical_rule_sets"]) == 1
    assert result["historical_rule_sets"][0]["id"] == "rs-prev"


def test_v2_raises_when_required_param_missing():
    """rule_set_id provided but statutory_effective_from missing → ValueError."""
    with pytest.raises(ValueError, match="v2 params required"):
        build_rules_context_snapshot(
            statutory_rule_id       = STAT_RULE_ID,
            statutory_version       = STAT_VERSION,
            statutory_rules_jsonb   = RULES_JSONB,
            statutory_tax_bands     = TAX_BANDS,
            rule_set_id             = RULE_SET_ID,
            rule_set_effective_from = "2024-01-01",
            rule_set_items          = RULE_SET_ITEMS,
            historical_rule_sets    = [],
            # statutory_effective_from deliberately omitted
        )


def test_v2_raises_lists_all_missing_params():
    """Error message includes every missing param name."""
    with pytest.raises(ValueError) as exc_info:
        build_rules_context_snapshot(
            statutory_rule_id = STAT_RULE_ID,
            statutory_version = STAT_VERSION,
            rule_set_id       = RULE_SET_ID,
            # all other v2 params missing
        )
    msg = str(exc_info.value)
    for param in ("statutory_effective_from", "statutory_rules_jsonb",
                  "statutory_tax_bands", "rule_set_effective_from",
                  "rule_set_items", "historical_rule_sets"):
        assert param in msg
