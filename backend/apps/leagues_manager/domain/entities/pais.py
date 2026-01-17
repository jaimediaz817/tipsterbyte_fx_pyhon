from dataclasses import dataclass
from typing import Optional

@dataclass
class Pais:
    id: int
    nombre: str
    continente_id: int
    codigo_iso: Optional[str] = None