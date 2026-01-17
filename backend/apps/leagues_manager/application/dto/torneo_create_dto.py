from pydantic import BaseModel
from typing import Optional
from datetime import date

class TorneoCreateDTO(BaseModel):
    nombre: str
    liga_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None