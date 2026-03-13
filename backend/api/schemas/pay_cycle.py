from pydantic import BaseModel
from typing import Dict, Literal, Optional


class PayCycleCreateSchema(BaseModel):
    frequency: Literal["monthly", "weekly", "biweekly"]
    run_day: int
    cutoff_day: int
    payment_day: int
    definition_json: Optional[Dict] = None