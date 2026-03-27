from pydantic import BaseModel
from typing import Optional


class PaisDTO(BaseModel):
    id: int
    nombre: str
    continente_id: int
    codigo_iso: Optional[str] = None
    was_created: Optional[bool] = (
        None  # Indica si fue creado (True) o ya existía (False)
    )
