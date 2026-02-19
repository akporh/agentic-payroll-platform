"""
AI Critic for Client Onboarding JSON.

Produces a soft review report using heuristics (no LLM integration yet).
This review never blocks onboarding — it surfaces warnings, questions,
and suggestions for human review.

No database access — pure heuristic analysis.

Reference: Phase 1 Business Spec — Onboarding Review Requirements.
"""

from backend.domain.onboarding.report_types import AICriticReport


def review_client_json(client_json: dict) -> AICriticReport:
    """Produce a heuristic-based review of client onboarding config.

    Args:
        client_json: The full client onboarding configuration dict
            containing salary_definitions, payroll_rules, and employees.

    Returns:
        AICriticReport with warnings, questions, and suggestions.
    """
    warnings: list[str] = []
    questions: list[str] = []
    suggestions: list[str] = []

    for sd in client_json.get("salary_definitions", []):
        name = sd.get("name", "UNKNOWN")
        components = sd.get("components", {})

        if "CONSOLIDATED" in components:
            warnings.append(
                f"{name}: CONSOLIDATED component found — confirm taxable vs informational."
            )

        basic = components.get("BASIC", {})
        if isinstance(basic.get("amount"), (int, float)) and basic["amount"] == 0:
            questions.append(
                f"{name}: BASIC amount is 0 — is this intentional?"
            )

    for emp in client_json.get("employees", []):
        emp_num = emp.get("employee_number", "UNKNOWN")
        biodata = emp.get("biodata", {})
        if not biodata.get("TIN"):
            suggestions.append(
                f"{emp_num}: missing TIN — PAYE remittance will fail."
            )

    for rule in client_json.get("payroll_rules", []):
        rule_code = rule.get("rule_code", "UNKNOWN")
        definition = rule.get("definition", {})
        if definition.get("method") == "statutory":
            tax_year = definition.get("tax_year")
            if tax_year is None:
                warnings.append(
                    f"{rule_code}: statutory rule missing tax_year."
                )
            elif tax_year != 2026:
                warnings.append(
                    f"{rule_code}: statutory rule tax_year is {tax_year}, expected 2026."
                )

    summary = "Heuristic review complete."
    if warnings or questions or suggestions:
        summary = (
            f"Heuristic review complete: {len(warnings)} warning(s), "
            f"{len(questions)} question(s), {len(suggestions)} suggestion(s)."
        )

    return AICriticReport(
        summary=summary,
        warnings=warnings,
        questions=questions,
        suggestions=suggestions,
    )
