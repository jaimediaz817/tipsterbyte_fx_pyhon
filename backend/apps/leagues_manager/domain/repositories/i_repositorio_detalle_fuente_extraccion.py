from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)


class IRepositorioDetalleFuenteExtraccion(ABC):

    @abstractmethod
    def get_detalle_fuente_extraccion_by_torneo_and_fuente(
        self, torneo_id: int, fuente_id: int
    ) -> DetalleFuenteExtraccion | None:
        pass

    @abstractmethod
    def create_detalle_fuente_extraccion(
        self,
        torneo_id: int,
        fuente_id: int,
        url: str,
        is_active: bool,
        process_id: int | None = None,
    ) -> DetalleFuenteExtraccion:
        pass

    @abstractmethod
    def update_detalle_fuente_extraccion(
        self, detalle_id: int, data: dict
    ) -> DetalleFuenteExtraccion:
        pass
