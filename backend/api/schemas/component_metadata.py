from pydantic import BaseModel
from typing import Dict

class ComponentMetadataCreateSchema(BaseModel):
    component_code: str
    version: int
    metadata_json: Dict
    effective_from: str