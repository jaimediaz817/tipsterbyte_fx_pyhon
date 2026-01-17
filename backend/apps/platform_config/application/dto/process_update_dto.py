from pydantic import BaseModel
from typing import Optional

class ProcessUpdateDTO(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None