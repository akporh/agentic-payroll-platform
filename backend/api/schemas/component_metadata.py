from pydantic import BaseModel
from typing import Dict

class ComponentMetadataCreateSchema(BaseModel):
    version: int
    rules_jsonb: Dict
    effective_from: str