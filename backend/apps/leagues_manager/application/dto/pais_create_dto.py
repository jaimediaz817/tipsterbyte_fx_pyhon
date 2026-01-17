from pydantic import BaseModel
from typing import Optional

class PaisCreateDTO(BaseModel):
    nombre: str
    codigo_iso: Optional[str] = None
    continente_id: int