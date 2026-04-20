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
from apps.leagues_manager.application.dto.geografia.pais_dto import PaisDTO
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.liga_dto import LigaDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.application.dto.torneo_dto import TorneoDTO
from apps.leagues_manager.domain.repositories.i_repositorio_continente import (
    IRepositorioContinente,
)
from apps.leagues_manager.domain.repositories.i_repositorio_pais import IRepositorioPais
from apps.leagues_manager.domain.repositories.i_repositorio_liga import IRepositorioLiga
from apps.leagues_manager.domain.repositories.i_repositorio_torneo import (
    IRepositorioTorneo,
)
from apps.leagues_manager.domain.repositories.i_repositorio_fuente_extraccion import (
    IRepositorioFuenteExtraccion,
)
from apps.leagues_manager.domain.repositories.i_repositorio_detalle_fuente_extraccion import (
    IRepositorioDetalleFuenteExtraccion,
)
from apps.leagues_manager.domain.services.i_leagues_service import ILeaguesService
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)
from typing import cast
from backend.core.db.transactional import Transactional


@Transactional()
class LeaguesService(ILeaguesService):
    def __init__(
        self,
        repo_continente: IRepositorioContinente | None = None,
        repo_pais: IRepositorioPais | None = None,
        repo_liga: IRepositorioLiga | None = None,
        repo_torneo: IRepositorioTorneo | None = None,
        repo_fuente: IRepositorioFuenteExtraccion | None = None,
        repo_detalle_fuente: IRepositorioDetalleFuenteExtraccion | None = None,
    ):
        """
        ✅ FASE 1 Refactor Repositorios @Repository
        Constructor 100% compatible hacia atras.
        Si no se pasan repositorios, se instancia la implementacion por defecto automaticamente.
        En tests se puede inyectar Mocks directamente sin necesidad de @patch

        ✅ CARACTERISTICAS:
        - Todas las dependencias son opcionales
        - Retrocompatibilidad 100%: `LeaguesService()` sigue funcionando exactamente igual
        - En tests: `LeaguesService(repo_continente=Mock())` funciona directamente
        - No rompe absolutamente ningun codigo existente
        - Soluciona definitivamente los problemas de pytest discovery
        """
        from typing import cast

        # ✅ SI NOS PASARON TODOS LOS REPOSITORIOS: NO CARGAMOS NADA DE BD!
        # Esto es lo que permite que los tests funcionen sin tocar absolutamente nada de infraestructura
        todos_repositorios_proporcionados = all(
            [
                repo_continente is not None,
                repo_pais is not None,
                repo_liga is not None,
                repo_torneo is not None,
                repo_fuente is not None,
                repo_detalle_fuente is not None,
            ]
        )

        repositorio_real: SQLLeaguesRepository

        if not todos_repositorios_proporcionados:
            # ✅ SOLO SI FALTA ALGUN REPOSITORIO: cargamos la implementacion real
            from backend.core.db.sql.database_sql import SessionLocal

            repositorio_real = SQLLeaguesRepository(SessionLocal())
        else:
            # ✅ En modo TEST: todos son Mocks, este valor NUNCA se usa
            # Solo declaramos el tipo para engañar a Pylance, no tiene ningun efecto en runtime
            repositorio_real = cast(SQLLeaguesRepository, None)

        self.repo_continente = repo_continente or repositorio_real
        self.repo_pais = repo_pais or repositorio_real
        self.repo_liga = repo_liga or repositorio_real
        self.repo_torneo = repo_torneo or repositorio_real
        self.repo_fuente = repo_fuente or repositorio_real
        self.repo_detalle_fuente = repo_detalle_fuente or repositorio_real

    def obtener_todos_los_continentes(self) -> list[ContinenteDTO]:
        continentes = self.repo_continente.get_all_continentes()
        return [ContinenteDTO(**c.__dict__) for c in continentes]

    def obtener_todos_los_paises(self) -> list[PaisDTO]:
        """Obtiene todos los países."""
        paises = self.repo_pais.get_all_paises()
        return [PaisDTO(**p.__dict__) for p in paises]

    def actualizar_liga_api_football(
        self,
        liga_id: int,
        id_api_externa: int | None,
        logo_url: str | None,
        tipo_liga: str | None,
    ) -> LigaDTO:
        """Actualiza los campos de API-Football de una liga."""
        liga = self.repo_liga.update_liga_api_fields(
            liga_id, id_api_externa, logo_url, tipo_liga
        )
        return LigaDTO(**liga.__dict__)

    def obtener_continente_por_id(self, continente_id: int) -> ContinenteDTO | None:
        continentes = self.repo_continente.get_all_continentes()
        for c in continentes:
            if cast(int, c.id) == continente_id:
                return ContinenteDTO(**c.__dict__)
        return None

    def registrar_continente(
        self, dto: ContinenteCreateDTO, update: bool = False
    ) -> ContinenteDTO:
        existing = self.repo_continente.get_continente_by_nombre(dto.nombre)
        if existing:
            if update:
                updated = self.repo_continente.update_continente(
                    cast(int, existing.id), dto.model_dump()
                )
                return ContinenteDTO(**updated.__dict__)
            return ContinenteDTO(**existing.__dict__)
        created = self.repo_continente.create_continente(dto.nombre, dto.codigo)
        return ContinenteDTO(**created.__dict__)

    def registrar_pais(self, dto: PaisCreateDTO, update: bool = False) -> PaisDTO:
        existing = self.repo_pais.get_pais_by_nombre_and_continente(
            dto.nombre, dto.continente_id
        )
        if existing:
            if update:
                updated = self.repo_pais.update_pais(existing.id, dto.model_dump())
                return PaisDTO(**updated.__dict__, was_created=False)
            return PaisDTO(**existing.__dict__, was_created=False)
        created = self.repo_pais.create_pais(
            dto.nombre, dto.codigo_iso, dto.continente_id
        )
        return PaisDTO(**created.__dict__, was_created=True)

    def registrar_liga(self, dto: LigaCreateDTO, update: bool = False) -> LigaDTO:
        existing = self.repo_liga.get_liga_by_nombre_and_pais(dto.nombre, dto.pais_id)
        if existing:
            if update:
                updated = self.repo_liga.update_liga(existing.id, dto.model_dump())
                return LigaDTO(**updated.__dict__)
            return LigaDTO(**existing.__dict__)
        created = self.repo_liga.create_liga(
            dto.nombre, dto.nombre_categoria, dto.pais_id
        )
        return LigaDTO(**created.__dict__)

    def registrar_torneo(self, dto: TorneoCreateDTO, update: bool = False) -> TorneoDTO:
        existing = self.repo_torneo.get_torneo_by_nombre_and_liga(
            dto.nombre, dto.liga_id
        )
        if existing:
            if update:
                updated = self.repo_torneo.update_torneo(existing.id, dto.model_dump())
                return TorneoDTO(**updated.__dict__)
            return TorneoDTO(**existing.__dict__)
        created = self.repo_torneo.create_torneo(
            dto.nombre, dto.liga_id, dto.fecha_inicio, dto.fecha_fin
        )
        return TorneoDTO(**created.__dict__)

    # --- Fuentes de Extracción (¡NUEVO!) ---
    def registrar_fuente_extraccion(
        self, dto: FuenteExtraccionCreateDTO, update: bool = False
    ) -> FuenteExtraccionDTO:
        existing = self.repo_fuente.get_fuente_extraccion_by_name(dto.name)
        if existing:
            if update:
                # Convierte el Enum a su valor de string para la actualización si es necesario
                data_to_update = dto.model_dump()
                data_to_update["type"] = data_to_update["type"].value
                assert existing.id is not None
                updated = self.repo_fuente.update_fuente_extraccion(
                    existing.id, data_to_update
                )
                return FuenteExtraccionDTO(**updated.__dict__)
            return FuenteExtraccionDTO(**existing.__dict__)

        # Convierte el Enum a su valor de string para la creación
        created = self.repo_fuente.create_fuente_extraccion(
            dto.name, dto.type.value, dto.descripcion, dto.is_active
        )
        return FuenteExtraccionDTO(**created.__dict__)

    # --- Detalles de Fuente de Extracción (¡NUEVO!) ---
    def registrar_detalle_fuente_extraccion(
        self, dto: DetalleFuenteExtraccionCreateDTO, update: bool = False
    ) -> DetalleFuenteExtraccionDTO:
        existing = (
            self.repo_detalle_fuente.get_detalle_fuente_extraccion_by_torneo_and_fuente(
                dto.torneo_id, dto.fuente_id
            )
        )
        if existing:
            if update:
                # .model_dump() de Pydantic 2.x ya maneja HttpUrl a string por defecto
                assert existing.id is not None
                updated = self.repo_detalle_fuente.update_detalle_fuente_extraccion(
                    existing.id, dto.model_dump()
                )
                return DetalleFuenteExtraccionDTO(**updated.__dict__)
            return DetalleFuenteExtraccionDTO(**existing.__dict__)

        # .model_dump() de Pydantic 2.x ya maneja HttpUrl a string por defecto
        created = self.repo_detalle_fuente.create_detalle_fuente_extraccion(
            dto.torneo_id, dto.fuente_id, str(dto.url), dto.is_active, dto.process_id
        )
        return DetalleFuenteExtraccionDTO(**created.__dict__)

    # --- NUEVOS MÉTODOS PARA PAUSAR/ACTIVAR ---

    def pausar_fuente_extraccion(self, fuente_id: int) -> FuenteExtraccionDTO:
        """Pausa una fuente de extracción (is_active=False)."""
        updated = self.repo_fuente.update_fuente_extraccion(
            fuente_id, {"is_active": False}
        )
        return FuenteExtraccionDTO(**updated.__dict__)

    def reanudar_fuente_extraccion(self, fuente_id: int) -> FuenteExtraccionDTO:
        """Reanuda una fuente de extracción (is_active=True)."""
        updated = self.repo_fuente.update_fuente_extraccion(
            fuente_id, {"is_active": True}
        )
        return FuenteExtraccionDTO(**updated.__dict__)

    def pausar_detalle_fuente_extraccion(
        self, detalle_id: int
    ) -> DetalleFuenteExtraccionDTO:
        """Pausa un detalle de fuente de extracción (is_active=False)."""
        updated = self.repo_detalle_fuente.update_detalle_fuente_extraccion(
            detalle_id, {"is_active": False}
        )
        return DetalleFuenteExtraccionDTO(**updated.__dict__)

    def reanudar_detalle_fuente_extraccion(
        self, detalle_id: int
    ) -> DetalleFuenteExtraccionDTO:
        """Reanuda un detalle de fuente de extracción (is_active=True)."""
        updated = self.repo_detalle_fuente.update_detalle_fuente_extraccion(
            detalle_id, {"is_active": True}
        )
        return DetalleFuenteExtraccionDTO(**updated.__dict__)
