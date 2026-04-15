"""
✅ Interfaz especifica para Torneo
Cumpliendo Interface Segregation Principle (ISP)

✅ Unica responsabilidad: Operaciones sobre la entidad Torneo
✅ Solo los metodos que realmente se usan
✅ Nada mas, nada menos
"""

from abc import ABC, abstractmethod
from typing import Optional

from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)


class IRepositorioTorneo(ABC):

    @abstractmethod
    def get_torneo_by_nombre_and_liga(
        self, nombre: str, liga_id: int
    ) -> Optional[Torneo]:
        pass

    @abstractmethod
    def create_torneo(
        self, nombre: str, liga_id: int, fecha_inicio=None, fecha_fin=None
    ) -> Torneo:
        pass

    @abstractmethod
    def update_torneo(self, torneo_id: int, data: dict) -> Torneo:
        pass

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
