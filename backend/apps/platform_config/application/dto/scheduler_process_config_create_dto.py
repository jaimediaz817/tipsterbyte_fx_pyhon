from pydantic import BaseModel
from typing import Optional

class ScheduledProcessConfigCreateDTO(BaseModel):
    process_name: str
    cron_expression: str
    enabled: bool = False
    description: Optional[str] = None