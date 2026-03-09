from pydantic import BaseModel
from typing import Dict

class PayrollRuleCreateSchema(BaseModel):
    rule_name: str
    rule_definition_json: Dict
    rule_type: str