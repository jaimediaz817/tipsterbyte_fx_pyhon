# NOTA: Necesitarás importar el modelo ScheduledProcessConfig
from apps.leagues_manager.application.dto.continente_create_dto import (
    ContinenteCreateDTO,
)
from apps.leagues_manager.application.dto.detalle_fuente_extraccion_create_dto import (
    DetalleFuenteExtraccionCreateDTO,
)
from apps.leagues_manager.application.dto.fuente_extraccion_create_dto import (
    FuenteExtraccionCreateDTO,
)
from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)

# from apps.leagues_manager.services.leagues_service import LeaguesService
from apps.leagues_manager.services.leagues_service import LeaguesService

# from scripts.db.seeders.seeder_utils import update_from_dict
from scripts.db.seeders.base_seeder import BaseSeeder

# Datos a poblar
CONTINENTES = [
    {"nombre": "Europa", "codigo": "UEFA"},
    {"nombre": "América del Sur", "codigo": "CONMEBOL"},
]

PAISES = [
    {"nombre": "España", "codigo_iso": "ESP", "continente": "Europa"},
    {"nombre": "Colombia", "codigo_iso": "COL", "continente": "América del Sur"},
]

# Se ajusta el valor de 'categoria' para que coincida con el Enum (A, B, C, D)
LIGAS = [
    {"nombre": "La Liga", "categoria": "A", "pais": "España"},  # <-- De "1" a "A"
    {"nombre": "Liga Betplay", "categoria": "A", "pais": "Colombia"},
]

TORNEOS = [
    {"nombre": "Temporada 2025-2026", "liga": "La Liga"},
    {"nombre": "Apertura 2026", "liga": "Liga Betplay"},
]

# --- ¡NUEVOS DATOS PARA FUENTES DE EXTRACCIÓN! ---
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

# --- ¡NUEVOS DATOS PARA DETALLES DE FUENTE DE EXTRACCIÓN! ---
# Nota: Usamos los nombres de torneo y fuente para mapear los IDs.
DETALLES_FUENTE_EXTRACCION = [
    # Detalle para "Temporada 2025-2026" (La Liga) y "Standings (SofaScore)"
    {
        "torneo_nombre": "Temporada 2025-2026",
        "fuente_nombre": "Standings (SofaScore)",
        "url": "https://www.sofascore.com/es/torneo/football/spain/laliga/8",
        "is_active": True,
    },
    # Detalle para "Apertura 2026" (Liga Betplay) y "Odds (WPlay)"
    {
        "torneo_nombre": "Apertura 2026",
        "fuente_nombre": "Odds (WPlay)",
        "url": "https://www.wplay.co/deportes/futbol/colombia/liga-betplay",
        "is_active": True,
    },
    # Puedes añadir más detalles aquí según tus necesidades
    {
        "torneo_nombre": "Temporada 2025-2026",
        "fuente_nombre": "Calendar (Official)",
        "url": "https://www.laliga.com/calendario-y-resultados/laliga-easports/2025-2026",
        "is_active": True,
    },
]


class LeaguesManagerSeeder(BaseSeeder):

    def run(self, update: bool = False):
        repo = SQLLeaguesRepository(self.db)
        service = LeaguesService(repo)

        # --- MAPAS PARA GUARDAR ENTIDADES CREADAS ---
        continente_map = {}
        pais_map = {}
        liga_map = {}

        torneo_map = {}  # <-- ¡NUEVO MAPA PARA TORNEOS!
        fuente_map = {}  # <-- ¡NUEVO MAPA PARA FUENTES DE EXTRACCIÓN!

        # 1) Continentes
        self.logger.info("Poblando continentes...")
        for continente_item in CONTINENTES:
            continente_dto = service.registrar_continente(
                ContinenteCreateDTO(**continente_item), update=update
            )
            continente_map[continente_dto.nombre] = continente_dto

        # 2) Países
        self.logger.info("Poblando países...")
        for pais_item in PAISES:
            continente_nombre = pais_item["continente"]
            continente = continente_map.get(continente_nombre)

            if not continente:
                self.logger.warning(
                    f"Continente '{continente_nombre}' no encontrado para el país '{pais_item['nombre']}'. Saltando..."
                )
                continue

            pais_dto = service.registrar_pais(
                PaisCreateDTO(
                    nombre=pais_item["nombre"],
                    codigo_iso=pais_item.get("codigo_iso"),
                    continente_id=continente.id,
                ),
                update=update,
            )
            pais_map[pais_dto.nombre] = pais_dto

        # 3) Ligas
        self.logger.info("Poblando ligas...")
        for liga_item in LIGAS:
            pais_nombre = liga_item["pais"]
            pais = pais_map.get(pais_nombre)

            if not pais:
                self.logger.warning(
                    f"País '{pais_nombre}' no encontrado para la liga '{liga_item['nombre']}'. Saltando..."
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

        # 4) Torneos
        self.logger.info("Poblando torneos...")
        for torneo_item in TORNEOS:
            liga_nombre = torneo_item["liga"]
            liga = liga_map.get(liga_nombre)

            if not liga:
                self.logger.warning(
                    f"Liga '{liga_nombre}' no encontrada para el torneo '{torneo_item['nombre']}'. Saltando..."
                )
                continue

            # --- ¡CORRECCIÓN CLAVE AQUÍ! Guardar el DTO en el mapa. ---
            torneo_dto = service.registrar_torneo(
                TorneoCreateDTO(nombre=torneo_item["nombre"], liga_id=liga.id),
                update=update,
            )
            torneo_map[torneo_dto.nombre] = (
                torneo_dto  # <-- Usamos el nombre del torneo como clave
            )

        # --- 5) Fuentes de Extracción (¡NUEVO BLOQUE!) ---
        self.logger.info("Poblando fuentes de extracción...")
        for fuente_item in FUENTES_EXTRACCION:
            fuente_dto = service.registrar_fuente_extraccion(
                FuenteExtraccionCreateDTO(**fuente_item), update=update
            )
            fuente_map[fuente_dto.name] = (
                fuente_dto  # Almacenamos por nombre para fácil acceso
            )

        # --- 6) Detalles de Fuente de Extracción (¡NUEVO BLOQUE!) ---
        self.logger.info("Poblando detalles de fuentes de extracción...")
        for detalle_item in DETALLES_FUENTE_EXTRACCION:
            # --- ¡CORRECCIÓN CLAVE AQUÍ! Búsqueda directa en el mapa. ---
            torneo_dto = torneo_map.get(detalle_item["torneo_nombre"])
            fuente_dto = fuente_map.get(detalle_item["fuente_nombre"])

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

            service.registrar_detalle_fuente_extraccion(
                DetalleFuenteExtraccionCreateDTO(
                    torneo_id=torneo_dto.id,
                    fuente_id=fuente_dto.id,
                    url=detalle_item["url"],
                    is_active=detalle_item["is_active"],
                ),
                update=update,
            )
        self.db.commit()  # Asegúrate de que el commit final se haga después de todos los registros
