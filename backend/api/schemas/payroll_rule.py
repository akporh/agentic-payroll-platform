from pydantic import BaseModel
from typing import Dict, List, Optional

class PayrollRuleCreateSchema(BaseModel):
    rule_name: str
    rule_definition_json: Dict
    rule_type: str

class RuleSetRuleItem(BaseModel):
    rule_name: str
    rule_definition_json: Dict
    rule_type: Optional[str] = None
    effective_from: str  # ISO date e.g. "2026-04-01"

class RuleSetPublishSchema(BaseModel):
    rules: List[RuleSetRuleItem]
    created_by: Optional[str] = None  # UUID; defaults to system sentinel if omitted