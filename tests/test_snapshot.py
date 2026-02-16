from backend.domain.rules.snapshot import build_rules_context_snapshot


def test_build_rules_context_snapshot():
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
