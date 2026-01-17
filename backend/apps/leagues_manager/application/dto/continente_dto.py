# DTOs de salida (para API)
from pydantic import BaseModel
from typing import Optional

class ContinenteDTO(BaseModel):
    id: int
    nombre: str
    codigo: Optional[str] = None