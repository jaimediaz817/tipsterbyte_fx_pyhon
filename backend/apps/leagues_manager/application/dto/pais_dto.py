from pydantic import BaseModel
from typing import Optional

class PaisDTO(BaseModel):
    id: int
    nombre: str
    continente_id: int
    codigo_iso: Optional[str] = None