from __future__ import annotations

from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo as TorneoModel


def map_torneo_from_model(torneo_model: TorneoModel) -> Torneo:
    """
    Convierte un modelo SQL de Torneo a entidad de dominio
    """
    return Torneo(
        id=(
            getattr(torneo_model, "id", 0)
            if getattr(torneo_model, "id", None) is not None
            else 0
        ),
        nombre=getattr(torneo_model, "nombre", "") or "",
        liga_id=(
            getattr(torneo_model, "liga_id", 0)
            if getattr(torneo_model, "liga_id", None) is not None
            else 0
        ),
        fecha_inicio=getattr(torneo_model, "fecha_inicio", None),
        fecha_fin=getattr(torneo_model, "fecha_fin", None),
    )
