from pydantic import BaseModel
from typing import Optional

from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum

class LigaDTO(BaseModel):
    id: int
    nombre: str
    pais_id: int
    nombre_categoria:Optional[CategoriaLigaEnum]