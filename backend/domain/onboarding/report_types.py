"""
Report Types for Client Onboarding Validation.

Defines the data structures used by the hard validator and AI critic
to communicate validation results and review findings.

No database access — type definitions only.
"""

from dataclasses import dataclass, field


@dataclass
class ValidationError:
    category: str
    message: str


@dataclass
class HardValidationResult:
    status: str
    errors: list[ValidationError] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "errors": [
                {"category": e.category, "message": e.message}
                for e in self.errors
            ],
        }


@dataclass
class AICriticReport:
    summary: str
    warnings: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "warnings": self.warnings,
            "questions": self.questions,
            "suggestions": self.suggestions,
        }
