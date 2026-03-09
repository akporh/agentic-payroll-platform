from pydantic import BaseModel
from typing import Optional

class GradeCreateSchema(BaseModel):
    grade_code: str
    description: Optional[str] = None