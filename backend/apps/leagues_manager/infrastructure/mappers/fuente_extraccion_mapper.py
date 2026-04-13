from __future__ import annotations
from typing import Optional


def map_fuente_extraccion_from_model(
    fuente_model: Optional[object],
) -> Optional[object]:
    """
    Convierte un modelo SQL de FuenteExtraccion a entidad de dominio
    Usa import lazy para evitar referencia circular
    """
    from apps.leagues_manager.domain.entities.fuente_extraccion import (
        FuenteExtraccion,
    )

    if not fuente_model:
        return None

    return FuenteExtraccion(
        id=getattr(fuente_model, "id", None),
        name=getattr(fuente_model, "name", "") or "",
        type=getattr(fuente_model, "type", "") or "",
        descripcion=getattr(fuente_model, "descripcion", None),
        is_active=getattr(fuente_model, "is_active", False),
    )
