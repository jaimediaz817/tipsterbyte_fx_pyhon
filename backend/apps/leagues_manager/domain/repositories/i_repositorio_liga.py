"""
✅ Interfaz especifica para Liga
Cumpliendo Interface Segregation Principle (ISP)

✅ Unica responsabilidad: Operaciones sobre la entidad Liga
✅ Solo los metodos que realmente se usan
✅ Nada mas, nada menos
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.leagues_manager.domain.entities.liga import Liga


class IRepositorioLiga(ABC):

    @abstractmethod
    def get_all_ligas(self) -> list[Liga]:
        pass

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

    @abstractmethod
    def update_liga_api_fields(
        self,
        liga_id: int,
        id_api_externa: int | None,
        logo_url: str | None,
        tipo_liga: str | None,
    ) -> Liga:
        pass
