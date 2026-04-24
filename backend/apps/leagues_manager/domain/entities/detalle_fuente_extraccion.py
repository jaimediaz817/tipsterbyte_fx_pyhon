from dataclasses import dataclass
from datetime import datetime
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

    # ✅ NUEVOS CAMPOS: Aislamiento Fuente de Extraccion
    provider_code: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    rate_limit_per_minute: Optional[int] = 60
    priority: Optional[int] = 1
    adapter_class: Optional[str] = None

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
