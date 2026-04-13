from __future__ import annotations
from typing import Optional

from apps.leagues_manager.domain.entities.liga import Liga, CategoriaLigaEnum
from apps.leagues_manager.infrastructure.models.sql.liga import Liga as LigaModel


def map_liga_from_model(liga_model: LigaModel) -> Liga:
    """
    Convierte un modelo SQL de Liga a entidad de dominio
    """
    nombre_categoria_value = getattr(liga_model, "nombre_categoria", None)
    if nombre_categoria_value is not None and nombre_categoria_value != "":
        try:
            nombre_categoria_enum = CategoriaLigaEnum(nombre_categoria_value)
        except ValueError:
            nombre_categoria_enum = None
    else:
        nombre_categoria_enum = None

    return Liga(
        id=(
            getattr(liga_model, "id", 0)
            if getattr(liga_model, "id", None) is not None
            else 0
        ),
        nombre=getattr(liga_model, "nombre", "") or "",
        pais_id=(
            getattr(liga_model, "pais_id", 0)
            if getattr(liga_model, "pais_id", None) is not None
            else 0
        ),
        nombre_categoria=nombre_categoria_enum,
    )
