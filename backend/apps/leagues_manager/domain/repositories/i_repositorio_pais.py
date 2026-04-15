"""
✅ Interfaz especifica para Pais
Cumpliendo Interface Segregation Principle (ISP)

✅ Unica responsabilidad: Operaciones sobre la entidad Pais
✅ Solo los metodos que realmente se usan
✅ Nada mas, nada menos
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.leagues_manager.domain.entities.pais import Pais


class IRepositorioPais(ABC):

    @abstractmethod
    def get_all_paises(self) -> list[Pais]:
        pass

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
