from __future__ import annotations
from typing import Optional


def map_detalle_fuente_extraccion_from_model(
    detalle_model: Optional[object],
) -> Optional[object]:
    """
    Convierte un modelo SQL de DetalleFuenteExtraccion a entidad de dominio
    Usa import lazy para evitar referencia circular
    """
    from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
        DetalleFuenteExtraccion,
    )

    if not detalle_model:
        return None

    return DetalleFuenteExtraccion(
        id=getattr(detalle_model, "id", None),
        torneo_id=getattr(detalle_model, "torneo_id", 0),
        fuente_id=getattr(detalle_model, "fuente_id", 0),
        url=getattr(detalle_model, "url", "") or "",
        is_active=getattr(detalle_model, "is_active", False),
        process_id=getattr(detalle_model, "process_id", None),
        created_at=getattr(detalle_model, "created_at", None),
        updated_at=getattr(detalle_model, "updated_at", None),
    )
