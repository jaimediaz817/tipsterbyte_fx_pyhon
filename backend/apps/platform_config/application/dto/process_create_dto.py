from pydantic import BaseModel, Field
from typing import Optional


class ProcessCreateDTO(BaseModel):
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=150)
    is_active: bool = True
    description: str | None = Field(None, max_length=255)
