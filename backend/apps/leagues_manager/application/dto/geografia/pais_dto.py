from pydantic import BaseModel
from typing import Optional


class PaisCreateDTO(BaseModel):
    nombre: str
    continente_id: int
    codigo_iso: Optional[str] = None


class PaisDTO(PaisCreateDTO):
    id: int
    was_created: Optional[bool] = (
        None  # Indica si fue creado (True) o ya existía (False)
    )
