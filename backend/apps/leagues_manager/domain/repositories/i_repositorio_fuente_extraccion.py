from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from apps.leagues_manager.domain.entities.fuente_extraccion import FuenteExtraccion


class IRepositorioFuenteExtraccion(ABC):

    @abstractmethod
    def get_fuente_extraccion_by_name(self, name: str) -> FuenteExtraccion | None:
        pass

    @abstractmethod
    def create_fuente_extraccion(
        self, name: str, type: str, descripcion: str | None, is_active: bool
    ) -> FuenteExtraccion:
        pass

    @abstractmethod
    def update_fuente_extraccion(self, fuente_id: int, data: dict) -> FuenteExtraccion:
        pass
