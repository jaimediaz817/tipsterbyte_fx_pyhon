from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProcessDTO(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None