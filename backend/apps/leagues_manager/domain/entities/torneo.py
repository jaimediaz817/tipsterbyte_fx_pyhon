from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Torneo:
    id: int
    nombre: str
    liga_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None