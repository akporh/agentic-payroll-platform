from pydantic import BaseModel
from typing import Dict


class ComponentMetadataCreateSchema(BaseModel):
    component_code: str
    overrides_json: Dict
