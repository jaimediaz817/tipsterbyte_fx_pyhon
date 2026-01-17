from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ScheduledProcessConfig:
    process_name: str
    cron_expression: str
    enabled: bool
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None