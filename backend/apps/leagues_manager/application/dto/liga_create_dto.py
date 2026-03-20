from pydantic import BaseModel, Field
from typing import Optional

from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum

class LigaCreateDTO(BaseModel):
    nombre: str    
    pais_id: int
    nombre_categoria: Optional[CategoriaLigaEnum] = Field(None, description="Categoría de la liga (A, B, C, D)")