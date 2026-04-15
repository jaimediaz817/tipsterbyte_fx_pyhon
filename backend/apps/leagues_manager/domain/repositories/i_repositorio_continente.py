"""
✅ Interfaz especifica para Continente
Cumpliendo Interface Segregation Principle (ISP)

✅ Unica responsabilidad: Operaciones sobre la entidad Continente
✅ Solo los metodos que realmente se usan
✅ Nada mas, nada menos
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.leagues_manager.domain.entities.continente import Continente


class IRepositorioContinente(ABC):

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
