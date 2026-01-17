from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduledProcessConfigDTO(BaseModel):
    process_name: str
    cron_expression: str
    enabled: bool
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None