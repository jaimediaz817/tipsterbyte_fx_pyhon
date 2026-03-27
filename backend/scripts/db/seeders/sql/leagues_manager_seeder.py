# ...existing imports...
from apps.leagues_manager.application.dto.fuente_extraccion_create_dto import (
    FuenteExtraccionCreateDTO,
)
from apps.leagues_manager.application.dto.detalle_fuente_extraccion_create_dto import (
    DetalleFuenteExtraccionCreateDTO,
)

from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)
from apps.leagues_manager.services.leagues_service import LeaguesService

from scripts.db.seeders.base_seeder import BaseSeeder

# --- ¡NUEVAS IMPORTACIONES PARA OBTENER IDs DE PROCESO! ---
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import (
    SQLPlatformConfigRepository,
)
from apps.platform_config.application.services.platform_config_service import (
    PlatformConfigService,
)
from shared.constants.process.process_codes import (
    PROCESS_STANDINGS_EXTRACTION,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_CALENDAR_EXTRACTION,
    PROCESS_EXTRACT_DATA_FUENTES,
)

# NOTA: Los continentes y países ahora los crea el geografia_seeder
# Este seeder solo crea ligas, torneos y fuentes de extracción

# Se ajusta el valor de 'categoria' para que coincida con el Enum (A, B, C, D)
LIGAS = [
    {"nombre": "La Liga", "categoria": "A", "pais": "España"},  # <-- De "1" a "A"
    {"nombre": "Liga Betplay", "categoria": "A", "pais": "Colombia"},
]

TORNEOS = [
    {"nombre": "Temporada 2025-2026", "liga": "La Liga"},
    {"nombre": "Apertura 2026", "liga": "Liga Betplay"},
]


# --- FUENTES DE EXTRACCIÓN (mismas de antes) ---
FUENTES_EXTRACCION = [
    {
        "name": "Standings (SofaScore)",
        "type": RobotTypeEnum.STANDINGS,
        "descripcion": "Fuente para extraer tablas de posiciones de SofaScore.",
        "is_active": True,
    },
    {
        "name": "Odds (WPlay)",
        "type": RobotTypeEnum.ODDS_WPLAY,
        "descripcion": "Fuente para extraer cuotas de casas de apuestas como WPlay.",
        "is_active": True,
    },
    {
        "name": "Calendar (Official)",
        "type": RobotTypeEnum.CALENDAR,
        "descripcion": "Fuente para extraer calendarios oficiales de ligas.",
        "is_active": True,
    },
]

# --- DETALLES DE FUENTE DE EXTRACCIÓN (¡AHORA CON process_code!) ---
DETALLES_FUENTE_EXTRACCION = [
    {
        "torneo_nombre": "Temporada 2025-2026",
        "fuente_nombre": "Standings (SofaScore)",
        "url": "https://www.sofascore.com/es/torneo/football/spain/laliga/8",
        "is_active": True,
        "process_code": PROCESS_STANDINGS_EXTRACTION,  # <-- ¡NUEVO!
    },
    {
        "torneo_nombre": "Apertura 2026",
        "fuente_nombre": "Odds (WPlay)",
        "url": "https://www.wplay.co/deportes/futbol/colombia/liga-betplay",
        "is_active": True,
        "process_code": PROCESS_ODDS_WPLAY_EXTRACTION,  # <-- ¡NUEVO!
    },
    {
        "torneo_nombre": "Temporada 2025-2026",
        "fuente_nombre": "Calendar (Official)",
        "url": "https://www.laliga.com/calendario-y-resultados/laliga-easports/2025-2026",
        "is_active": True,
        "process_code": PROCESS_CALENDAR_EXTRACTION,  # <-- ¡NUEVO!
    },
]


class LeaguesManagerSeeder(BaseSeeder):

    def run(self, update: bool = False):
        self.logger.info("🌱 Ejecutando seeder del módulo Leagues Manager...")
        try:
            repo = SQLLeaguesRepository(self.db)
            service = LeaguesService(repo)

            # --- NUEVO: Repositorio y Servicio para obtener IDs de Procesos ---
            platform_repo = SQLPlatformConfigRepository(self.db)
            platform_service = PlatformConfigService(platform_repo)

            # --- NUEVO: Asegurar que los procesos existan (crearlos si no existen) ---
            # Esto hace el seeder más resiliente si se ejecuta antes que PlatformConfigSeeder
            from apps.platform_config.application.dto.process_create_dto import (
                ProcessCreateDTO,
            )

            processes_to_ensure = [
                {
                    "code": PROCESS_EXTRACT_DATA_FUENTES,
                    "name": "Orquestador de Rastreo de Datos de Fuentes Deportivas (General)",
                    "is_active": True,
                    "description": "Proceso principal que orquesta la extracción de datos de diversas fuentes deportivas.",
                },
                {
                    "code": PROCESS_STANDINGS_EXTRACTION,
                    "name": "Extracción de Tablas de Posiciones",
                    "is_active": True,
                    "description": "Proceso dedicado a la extracción de datos de tablas de posiciones (standings).",
                },
                {
                    "code": PROCESS_ODDS_WPLAY_EXTRACTION,
                    "name": "Extracción de Cuotas Deportivas (WPlay)",
                    "is_active": True,
                    "description": "Proceso dedicado a la extracción de cuotas de apuestas de la casa WPlay.",
                },
                {
                    "code": PROCESS_CALENDAR_EXTRACTION,
                    "name": "Extracción de Calendarios de Torneos",
                    "is_active": True,
                    "description": "Proceso dedicado a la extracción de calendarios de partidos y eventos de torneos.",
                },
            ]

            self.logger.info("Verificando/creando procesos necesarios...")
            for process_data in processes_to_ensure:
                dto = ProcessCreateDTO(**process_data)
                platform_service.registrar_process(dto, update=False)

            # --- NUEVO: Mapa para almacenar los IDs de los procesos ---
            process_ids_map = {}
            for process_code in [
                PROCESS_STANDINGS_EXTRACTION,
                PROCESS_ODDS_WPLAY_EXTRACTION,
                PROCESS_CALENDAR_EXTRACTION,
                PROCESS_EXTRACT_DATA_FUENTES,
            ]:
                process_entity = platform_service.obtener_process(process_code)
                if process_entity:
                    process_ids_map[process_code] = process_entity.id
                else:
                    self.logger.error(
                        f"❌ PROCESO NO ENCONTRADO después de intentar crearlo: '{process_code}'."
                    )
                    raise ValueError(
                        f"Proceso '{process_code}' no encontrado en la base de datos después de intentar crearlo."
                    )

            # --- MAPAS PARA GUARDAR ENTIDADES CREADAS ---
            # NOTA: Los continentes y países ahora los crea el geografia_seeder
            liga_map = {}
            torneo_map = {}
            fuente_map = {}

            # 1) Ligas
            # NOTA: Las ligas requieren países que ya deben existir (creados por geografia_seeder)
            self.logger.info("Poblando ligas...")
            for liga_item in LIGAS:
                pais_nombre = liga_item["pais"]
                # Buscar el país en la base de datos (debe existir por geografia_seeder)
                pais = repo.get_pais_by_nombre(pais_nombre)

                if not pais:
                    self.logger.warning(
                        f"País '{pais_nombre}' no encontrado para la liga '{liga_item['nombre']}'. "
                        f"Asegúrese de ejecutar geografia_seeder primero. Saltando..."
                    )
                    continue

                liga_dto = service.registrar_liga(
                    LigaCreateDTO(
                        nombre=liga_item["nombre"],
                        nombre_categoria=(
                            CategoriaLigaEnum(liga_item.get("categoria"))
                            if liga_item.get("categoria")
                            else None
                        ),
                        pais_id=pais.id,
                    ),
                    update=update,
                )
                liga_map[liga_dto.nombre] = liga_dto

            # 2) Torneos
            self.logger.info("Poblando torneos...")
            for torneo_item in TORNEOS:
                liga_nombre = torneo_item["liga"]
                liga = liga_map.get(liga_nombre)

                if not liga:
                    self.logger.warning(
                        f"Liga '{liga_nombre}' no encontrada para el torneo '{torneo_item['nombre']}'. Saltando..."
                    )
                    continue

                torneo_dto = service.registrar_torneo(
                    TorneoCreateDTO(nombre=torneo_item["nombre"], liga_id=liga.id),
                    update=update,
                )
                torneo_map[torneo_dto.nombre] = torneo_dto

            # --- 5) Fuentes de Extracción (igual que antes) ---
            self.logger.info("Poblando fuentes de extracción...")
            for fuente_item in FUENTES_EXTRACCION:
                fuente_dto = service.registrar_fuente_extraccion(
                    FuenteExtraccionCreateDTO(**fuente_item), update=update
                )
                fuente_map[fuente_dto.name] = fuente_dto

            # --- 6) Detalles de Fuente de Extracción (¡ACTUALIZADO!) ---
            self.logger.info("Poblando detalles de fuentes de extracción...")
            for detalle_item in DETALLES_FUENTE_EXTRACCION:
                torneo_dto = torneo_map.get(detalle_item["torneo_nombre"])
                fuente_dto = fuente_map.get(detalle_item["fuente_nombre"])
                # Obtener el process_id del mapa que creamos
                process_id = process_ids_map.get(detalle_item["process_code"])

                if not torneo_dto:
                    self.logger.warning(
                        f"Torneo '{detalle_item['torneo_nombre']}' no encontrado para el detalle de fuente. Saltando..."
                    )
                    continue
                if not fuente_dto:
                    self.logger.warning(
                        f"Fuente '{detalle_item['fuente_nombre']}' no encontrada para el detalle de fuente. Saltando..."
                    )
                    continue
                if not process_id:  # Validar que tenemos un ID de proceso
                    self.logger.error(
                        f"❌ ID de proceso no encontrado para el código '{detalle_item['process_code']}'. Saltando detalle."
                    )
                    continue

                service.registrar_detalle_fuente_extraccion(
                    DetalleFuenteExtraccionCreateDTO(
                        torneo_id=torneo_dto.id,
                        fuente_id=fuente_dto.id,
                        url=detalle_item["url"],
                        is_active=detalle_item["is_active"],
                        process_id=process_id,  # ¡PASAR EL ID DEL PROCESO!
                    ),
                    update=update,
                )
            self.db.commit()
            self.logger.success("✅ Seeder de Leagues Manager completado exitosamente.")
        except Exception as e:
            self.logger.error(f"❌ Error durante el seeder de Leagues Manager: {e}")
            self.db.rollback()
            raise
