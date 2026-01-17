from abc import ABC, abstractmethod

from apps.leagues_manager.application.dto.continente_create_dto import ContinenteCreateDTO
from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.liga_dto import LigaDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.pais_dto import PaisDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.application.dto.torneo_dto import TorneoDTO

class ILeaguesService(ABC):
    
    @abstractmethod
    def obtener_todos_los_continentes(self) -> list[ContinenteDTO]: pass
    
    @abstractmethod
    def obtener_continente_por_id(self, continente_id: int) -> ContinenteDTO | None: pass
    
    @abstractmethod
    def registrar_continente(self, dto: ContinenteCreateDTO, update: bool = False) -> ContinenteDTO: pass

    @abstractmethod
    def registrar_pais(self, dto: PaisCreateDTO, update: bool = False) -> PaisDTO: pass

    @abstractmethod
    def registrar_liga(self, dto: LigaCreateDTO, update: bool = False) -> LigaDTO: pass

    @abstractmethod
    def registrar_torneo(self, dto: TorneoCreateDTO, update: bool = False) -> TorneoDTO: pass