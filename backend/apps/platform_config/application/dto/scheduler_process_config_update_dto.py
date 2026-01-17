from pydantic import BaseModel
from typing import Optional

class ScheduledProcessConfigUpdateDTO(BaseModel):
    cron_expression: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None