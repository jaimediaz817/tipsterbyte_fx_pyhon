from __future__ import annotations
from typing import Optional

from apps.leagues_manager.domain.entities.continente import Continente


def map_continente_from_model(
    continente_model: Optional[Continente],
) -> Optional[Continente]:
    """
    Convierte un modelo SQL de Continente a entidad de dominio
    """
    if not continente_model:
        return None

    return Continente(
        id=getattr(continente_model, "id", 0),
        nombre=getattr(continente_model, "nombre", "") or "",
        codigo=getattr(continente_model, "codigo", None),
    )
