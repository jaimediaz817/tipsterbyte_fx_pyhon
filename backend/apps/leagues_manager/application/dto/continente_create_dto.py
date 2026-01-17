from pydantic import BaseModel
from typing import Optional

class ContinenteCreateDTO(BaseModel):
    nombre: str
    codigo: Optional[str] = None