from dataclasses import dataclass
from typing import Optional

from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum

@dataclass
class Liga:
    id: int
    nombre: str
    pais_id: int
    nombre_categoria: Optional[CategoriaLigaEnum] = None