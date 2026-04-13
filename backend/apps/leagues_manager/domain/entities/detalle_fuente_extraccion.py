from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class DetalleFuenteExtraccion:
    """
    Entidad de Dominio para Detalle de Fuente de Extracción
    Pura, sin dependencias externas, sin infraestructura
    """

    id: Optional[int]
    torneo_id: int
    fuente_id: int
    url: str
    is_active: bool
    process_id: Optional[int]
