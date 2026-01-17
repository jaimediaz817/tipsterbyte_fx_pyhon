# DTOs de salida (para API)
from datetime import date
from pydantic import BaseModel
from typing import Optional

class TorneoDTO(BaseModel):
    id: int
    nombre: str
    liga_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None