from dataclasses import dataclass
from typing import Optional

@dataclass
class Continente:
    id: int
    nombre: str
    codigo: Optional[str] = None