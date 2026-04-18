from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class FuenteExtraccion:
    """
    Entidad de Dominio para Fuente de Extracción
    Pura, sin dependencias externas, sin infraestructura
    """

    id: Optional[int]
    name: str
    type: str
    descripcion: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
