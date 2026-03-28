from abc import ABC, abstractmethod
from typing import Optional, List

from apps.leagues_manager.domain.entities.continente import Continente
from apps.leagues_manager.domain.entities.liga import Liga
from apps.leagues_manager.domain.entities.pais import Pais
from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion,
)


class ILeaguesRepository(ABC):
    # Continente
    @abstractmethod
    def get_all_continentes(self) -> List[Continente]:
        pass

    @abstractmethod
    def get_continente_by_nombre(self, nombre: str) -> Optional[Continente]:
        pass

    @abstractmethod
    def create_continente(self, nombre: str, codigo: str | None) -> Continente:
        pass

    @abstractmethod
    def update_continente(self, continente_id: int, data: dict) -> Continente:
        pass

    # País
    @abstractmethod
    def get_pais_by_nombre_and_continente(
        self, nombre: str, continente_id: int
    ) -> Optional[Pais]:
        pass

    @abstractmethod
    def get_pais_by_nombre(self, nombre: str) -> Optional[Pais]:
        pass

    @abstractmethod
    def create_pais(
        self, nombre: str, codigo_iso: str | None, continente_id: int
    ) -> Pais:
        pass

    @abstractmethod
    def update_pais(self, pais_id: int, data: dict) -> Pais:
        pass

    # Liga
    @abstractmethod
    def get_liga_by_nombre_and_pais(self, nombre: str, pais_id: int) -> Optional[Liga]:
        pass

    @abstractmethod
    def get_liga_by_nombre(self, nombre: str) -> Optional[Liga]:
        pass

    @abstractmethod
    def create_liga(
        self, nombre: str, nombre_categoria: str | None, pais_id: int
    ) -> Liga:
        pass

    @abstractmethod
    def update_liga(self, liga_id: int, data: dict) -> Liga:
        pass

    # Torneo
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

    # --- FuenteExtraccion (¡NUEVO!) ---
    @abstractmethod
    def get_fuente_extraccion_by_name(self, name: str) -> FuenteExtraccion | None:
        pass

    @abstractmethod
    def create_fuente_extraccion(
        self, name: str, type: str, descripcion: str | None, is_active: bool
    ) -> "FuenteExtraccion":
        pass

    @abstractmethod
    def update_fuente_extraccion(
        self, fuente_id: int, data: dict
    ) -> "FuenteExtraccion":
        pass

    # --- DetalleFuenteExtraccion (¡NUEVO!) ---
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

    @abstractmethod
    def get_all_paises(self) -> list[Pais]:
        pass

    @abstractmethod
    def get_all_ligas(self) -> list[Liga]:
        pass

    @abstractmethod
    def update_liga_api_fields(
        self,
        liga_id: int,
        id_api_externa: int | None,
        logo_url: str | None,
        tipo_liga: str | None,
    ) -> Liga:
        pass
