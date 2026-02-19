"""
Unified Review Runner for Client Onboarding.

Combines hard validation and AI critic review into a single deterministic
output. Both sections are always present in the result, even if hard
validation fails.

No database access — orchestration of pure functions only.

Reference: Phase 1 Business Spec — Onboarding Pipeline.
"""

from backend.domain.onboarding.hard_validator import validate_client_json
from backend.domain.onboarding.ai_critic import review_client_json


def review_client_onboarding(client_json: dict) -> dict:
    """Run full onboarding review: hard validation + AI critic.

    Args:
        client_json: The full client onboarding configuration dict.

    Returns:
        Dict with hard_validation and ai_review sections, both always present.
    """
    hard_result = validate_client_json(client_json)
    ai_report = review_client_json(client_json)

    return {
        "hard_validation": hard_result.to_dict(),
        "ai_review": ai_report.to_dict(),
    }
