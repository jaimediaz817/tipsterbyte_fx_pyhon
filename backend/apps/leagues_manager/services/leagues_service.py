from apps.leagues_manager.application.dto.continente_create_dto import ContinenteCreateDTO
from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.liga_dto import LigaDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.pais_dto import PaisDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.application.dto.torneo_dto import TorneoDTO
from apps.leagues_manager.domain.repositories.i_leagues_repository import ILeaguesRepository
from apps.leagues_manager.domain.services.i_leagues_service import ILeaguesService


class LeaguesService(ILeaguesService):
    def __init__(self, repo: ILeaguesRepository):
        self.repo = repo

    def obtener_todos_los_continentes(self) -> list[ContinenteDTO]:
        continentes = self.repo.get_all_continentes()
        return [ContinenteDTO(**c.__dict__) for c in continentes]

    def obtener_continente_por_id(self, continente_id: int) -> ContinenteDTO | None:
        continentes = self.repo.get_all_continentes()
        for c in continentes:
            if c.id == continente_id:
                return ContinenteDTO(**c.__dict__)
        return None

    def registrar_continente(self, dto: ContinenteCreateDTO, update: bool = False) -> ContinenteDTO:
        existing = self.repo.get_continente_by_nombre(dto.nombre)
        if existing:
            if update:
                updated = self.repo.update_continente(existing.id, dto.model_dump())
                return ContinenteDTO(**updated.__dict__)
            return ContinenteDTO(**existing.__dict__)
        created = self.repo.create_continente(dto.nombre, dto.codigo)
        return ContinenteDTO(**created.__dict__)

    def registrar_pais(self, dto: PaisCreateDTO, update: bool = False) -> PaisDTO:
        existing = self.repo.get_pais_by_nombre_and_continente(dto.nombre, dto.continente_id)
        if existing:
            if update:
                updated = self.repo.update_pais(existing.id, dto.model_dump())
                return PaisDTO(**updated.__dict__)
            return PaisDTO(**existing.__dict__)
        created = self.repo.create_pais(dto.nombre, dto.codigo_iso, dto.continente_id)
        return PaisDTO(**created.__dict__)

    def registrar_liga(self, dto: LigaCreateDTO, update: bool = False) -> LigaDTO:
        existing = self.repo.get_liga_by_nombre_and_pais(dto.nombre, dto.pais_id)
        if existing:
            if update:
                updated = self.repo.update_liga(existing.id, dto.model_dump())
                return LigaDTO(**updated.__dict__)
            return LigaDTO(**existing.__dict__)
        created = self.repo.create_liga(dto.nombre, dto.nombre_categoria, dto.pais_id)
        return LigaDTO(**created.__dict__)

    def registrar_torneo(self, dto: TorneoCreateDTO, update: bool = False) -> TorneoDTO:
        existing = self.repo.get_torneo_by_nombre_and_liga(dto.nombre, dto.liga_id)
        if existing:
            if update:
                updated = self.repo.update_torneo(existing.id, dto.model_dump())
                return TorneoDTO(**updated.__dict__)
            return TorneoDTO(**existing.__dict__)
        created = self.repo.create_torneo(dto.nombre, dto.liga_id, dto.fecha_inicio, dto.fecha_fin)
        return TorneoDTO(**created.__dict__)

    # def registrar_continente(self, dto: ContinenteCreateDTO) -> ContinenteDTO:
    #     existing = self.repo.get_continente_by_nombre(dto.nombre)
    #     if existing:
    #         return ContinenteDTO(**existing.__dict__)
    #     created = self.repo.create_continente(dto.nombre, dto.codigo)
    #     return ContinenteDTO(**created.__dict__)

    # def registrar_pais(self, dto: PaisCreateDTO) -> PaisDTO:
    #     existing = self.repo.get_pais_by_nombre_and_continente(dto.nombre, dto.continente_id)
    #     if existing:
    #         return PaisDTO(**existing.__dict__)
    #     created = self.repo.create_pais(dto.nombre, dto.codigo_iso, dto.continente_id)
    #     return PaisDTO(**created.__dict__)

    # def registrar_liga(self, dto: LigaCreateDTO) -> LigaDTO:
    #     existing = self.repo.get_liga_by_nombre_and_pais(dto.nombre, dto.pais_id)
    #     if existing:
    #         return LigaDTO(**existing.__dict__)
    #     created = self.repo.create_liga(dto.nombre, dto.nombre_categoria, dto.pais_id)
    #     return LigaDTO(**created.__dict__)

    # def registrar_torneo(self, dto: TorneoCreateDTO) -> TorneoDTO:
    #     existing = self.repo.get_torneo_by_nombre_and_liga(dto.nombre, dto.liga_id)
    #     if existing:
    #         return TorneoDTO(**existing.__dict__)
    #     created = self.repo.create_torneo(dto.nombre, dto.liga_id, dto.fecha_inicio, dto.fecha_fin)
    #     return TorneoDTO(**created.__dict__)