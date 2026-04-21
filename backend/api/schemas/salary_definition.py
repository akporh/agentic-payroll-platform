from pydantic import BaseModel
from typing import Dict, Optional


class SalaryDefinitionCreateSchema(BaseModel):
    name: str
    code: str
    components_jsonb: Dict
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    