from pydantic import BaseModel
from typing import Optional

class LigaCreateDTO(BaseModel):
    nombre: str
    nombre_categoria: Optional[str] = None
    pais_id: int