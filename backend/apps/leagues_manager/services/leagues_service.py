from apps.leagues_manager.application.dto.continente_create_dto import (
    ContinenteCreateDTO,
)
from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
from apps.leagues_manager.application.dto.detalle_fuente_extraccion_create_dto import (
    DetalleFuenteExtraccionCreateDTO,
)
from apps.leagues_manager.application.dto.detalle_fuente_extraccion_dto import (
    DetalleFuenteExtraccionDTO,
)
from apps.leagues_manager.application.dto.fuente_extraccion_create_dto import (
    FuenteExtraccionCreateDTO,
)
from apps.leagues_manager.application.dto.fuente_extraccion_dto import (
    FuenteExtraccionDTO,
)
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.liga_dto import LigaDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.pais_dto import PaisDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.application.dto.torneo_dto import TorneoDTO
from apps.leagues_manager.domain.repositories.i_leagues_repository import (
    ILeaguesRepository,
)
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

    def registrar_continente(
        self, dto: ContinenteCreateDTO, update: bool = False
    ) -> ContinenteDTO:
        existing = self.repo.get_continente_by_nombre(dto.nombre)
        if existing:
            if update:
                updated = self.repo.update_continente(existing.id, dto.model_dump())
                return ContinenteDTO(**updated.__dict__)
            return ContinenteDTO(**existing.__dict__)
        created = self.repo.create_continente(dto.nombre, dto.codigo)
        return ContinenteDTO(**created.__dict__)

    def registrar_pais(self, dto: PaisCreateDTO, update: bool = False) -> PaisDTO:
        existing = self.repo.get_pais_by_nombre_and_continente(
            dto.nombre, dto.continente_id
        )
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
        created = self.repo.create_torneo(
            dto.nombre, dto.liga_id, dto.fecha_inicio, dto.fecha_fin
        )
        return TorneoDTO(**created.__dict__)

    # --- Fuentes de Extracción (¡NUEVO!) ---
    def registrar_fuente_extraccion(
        self, dto: FuenteExtraccionCreateDTO, update: bool = False
    ) -> FuenteExtraccionDTO:
        existing = self.repo.get_fuente_extraccion_by_name(dto.name)
        if existing:
            if update:
                # Convierte el Enum a su valor de string para la actualización si es necesario
                data_to_update = dto.model_dump()
                data_to_update["type"] = data_to_update["type"].value
                updated = self.repo.update_fuente_extraccion(
                    existing.id.scalar(), data_to_update
                )
                return FuenteExtraccionDTO(**updated.__dict__)
            return FuenteExtraccionDTO(**existing.__dict__)

        # Convierte el Enum a su valor de string para la creación
        created = self.repo.create_fuente_extraccion(
            dto.name, dto.type.value, dto.descripcion, dto.is_active
        )
        return FuenteExtraccionDTO(**created.__dict__)

    # --- Detalles de Fuente de Extracción (¡NUEVO!) ---
    def registrar_detalle_fuente_extraccion(
        self, dto: DetalleFuenteExtraccionCreateDTO, update: bool = False
    ) -> DetalleFuenteExtraccionDTO:
        existing = self.repo.get_detalle_fuente_extraccion_by_torneo_and_fuente(
            dto.torneo_id, dto.fuente_id
        )
        if existing:
            if update:
                # .model_dump() de Pydantic 2.x ya maneja HttpUrl a string por defecto
                updated = self.repo.update_detalle_fuente_extraccion(
                    existing.id.scalar(), dto.model_dump()
                )
                return DetalleFuenteExtraccionDTO(**updated.__dict__)
            return DetalleFuenteExtraccionDTO(**existing.__dict__)

        # .model_dump() de Pydantic 2.x ya maneja HttpUrl a string por defecto
        created = self.repo.create_detalle_fuente_extraccion(
            dto.torneo_id, dto.fuente_id, str(dto.url), dto.is_active, dto.process_id
        )
        return DetalleFuenteExtraccionDTO(**created.__dict__)

    # --- NUEVOS MÉTODOS PARA PAUSAR/ACTIVAR ---

    def pausar_fuente_extraccion(self, fuente_id: int) -> FuenteExtraccionDTO:
        """Pausa una fuente de extracción (is_active=False)."""
        updated = self.repo.update_fuente_extraccion(fuente_id, {"is_active": False})
        return FuenteExtraccionDTO(**updated.__dict__)

    def reanudar_fuente_extraccion(self, fuente_id: int) -> FuenteExtraccionDTO:
        """Reanuda una fuente de extracción (is_active=True)."""
        updated = self.repo.update_fuente_extraccion(fuente_id, {"is_active": True})
        return FuenteExtraccionDTO(**updated.__dict__)

    def pausar_detalle_fuente_extraccion(
        self, detalle_id: int
    ) -> DetalleFuenteExtraccionDTO:
        """Pausa un detalle de fuente de extracción (is_active=False)."""
        updated = self.repo.update_detalle_fuente_extraccion(
            detalle_id, {"is_active": False}
        )
        return DetalleFuenteExtraccionDTO(**updated.__dict__)

    def reanudar_detalle_fuente_extraccion(
        self, detalle_id: int
    ) -> DetalleFuenteExtraccionDTO:
        """Reanuda un detalle de fuente de extracción (is_active=True)."""
        updated = self.repo.update_detalle_fuente_extraccion(
            detalle_id, {"is_active": True}
        )
        return DetalleFuenteExtraccionDTO(**updated.__dict__)

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
