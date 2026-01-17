from pydantic import BaseModel
from typing import Optional

class LigaDTO(BaseModel):
    id: int
    nombre: str
    pais_id: int
    nombre_categoria: Optional[str] = None