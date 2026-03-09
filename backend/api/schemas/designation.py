from pydantic import BaseModel
from typing import Dict, Optional

class DesignationCreateSchema(BaseModel):
    designation_code: str
    description: Optional[str] = None