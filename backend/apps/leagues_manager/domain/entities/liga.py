from dataclasses import dataclass
from typing import Optional

@dataclass
class Liga:
    id: int
    nombre: str
    pais_id: int
    nombre_categoria: Optional[str] = None