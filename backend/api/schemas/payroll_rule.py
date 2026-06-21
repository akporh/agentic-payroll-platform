from datetime import date
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class PayrollRuleCreateSchema(BaseModel):
    rule_name: str = Field(max_length=255)
    rule_definition_json: Dict
    rule_type: Literal["EARNING", "DEDUCTION"]
    effective_from: date


class PayrollRuleToggleSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')
    is_active: bool


class RuleSetRuleItem(BaseModel):
    rule_name: str
    rule_definition_json: Dict
    rule_type: Optional[str] = None
    effective_from: str  # ISO date e.g. "2026-04-01"


class RuleSetPublishSchema(BaseModel):
    rules: List[RuleSetRuleItem]
    created_by: Optional[str] = None  # UUID; defaults to system sentinel if omitted