from __future__ import annotations

from typing import TYPE_CHECKING

from apps.leagues_manager.domain.entities.pais import Pais

if TYPE_CHECKING:
    from apps.leagues_manager.infrastructure.models.sql.pais import Pais as PaisModel


def map_pais_from_model(pais_model: "PaisModel") -> Pais:
    """
    Convierte un modelo SQL de Pais a entidad de dominio
    """
    return Pais(
        id=(
            getattr(pais_model, "id", 0)
            if getattr(pais_model, "id", None) is not None
            else 0
        ),
        nombre=getattr(pais_model, "nombre", "") or "",
        continente_id=(
            getattr(pais_model, "continente_id", 0)
            if getattr(pais_model, "continente_id", None) is not None
            else 0
        ),
        codigo_iso=getattr(pais_model, "codigo_iso", None),
    )
