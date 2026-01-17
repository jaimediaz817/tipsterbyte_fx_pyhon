from pydantic import BaseModel
from typing import Optional

class ProcessCreateDTO(BaseModel):
    code: str
    name: str
    is_active: bool = True
    description: Optional[str] = None