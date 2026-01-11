from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MockFuenteExtraccion:
    """
    Simula un registro de la tabla catalogo FuenteExtraccion.
    Define el 'QUÉ' se extrae (ej. 'Standings de ESPN').
    """
    id: int
    name: str  # ej: "Standings (ESPN)", "Odds (WPlay)"
    type: str  # ej: "standings", "odds" (para identificar el robot a usar)

@dataclass
class MockDetalleFuenteExtraccion:
    """
    Simula la tabla pivote que une un Torneo con una Fuente y una URL.
    Define el 'CÓMO' y 'DÓNDE'.
    """
    torneo_id: int
    fuente_id: int
    url: str
    is_active: bool = True
    # Opcional: Podríamos tener el objeto 'Fuente' directamente aquí para facilitar el acceso
    fuente: Optional[MockFuenteExtraccion] = None

@dataclass
class MockTorneo:
    """Simula un registro de la tabla Torneo."""
    id: int
    name: str
    is_active: bool
    # La lista de detalles ahora contiene la información completa de la fuente.
    detalles_fuente: List[MockDetalleFuenteExtraccion] = field(default_factory=list)

@dataclass
class MockLiga:
    """Simula un registro de la tabla Liga. Este es nuestro "Cliente"."""
    id: int
    name: str
    is_active: bool
    torneos: List[MockTorneo] = field(default_factory=list)