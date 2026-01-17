# NOTA: Necesitarás importar el modelo ScheduledProcessConfig
from apps.leagues_manager.application.dto.continente_create_dto import ContinenteCreateDTO
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import SQLLeaguesRepository
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

LIGAS = [
    {"nombre": "La Liga", "categoria": "1", "pais": "España"},
    {"nombre": "Liga Betplay", "categoria": "A", "pais": "Colombia"},
]

TORNEOS = [
    {"nombre": "Temporada 2025-2026", "liga": "La Liga"},
    {"nombre": "Apertura 2026", "liga": "Liga Betplay"},
]


class LeaguesManagerSeeder(BaseSeeder):
       
    def run(self, update: bool = False):
        repo = SQLLeaguesRepository(self.db)
        service = LeaguesService(repo)

        # --- MAPAS PARA GUARDAR ENTIDADES CREADAS ---
        continente_map = {}
        pais_map = {}
        liga_map = {}

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
                self.logger.warning(f"Continente '{continente_nombre}' no encontrado para el país '{pais_item['nombre']}'. Saltando...")
                continue

            pais_dto = service.registrar_pais(PaisCreateDTO(
                nombre=pais_item["nombre"],
                codigo_iso=pais_item.get("codigo_iso"),
                continente_id=continente.id
            ), update=update)
            pais_map[pais_dto.nombre] = pais_dto

        # 3) Ligas
        self.logger.info("Poblando ligas...")
        for liga_item in LIGAS:
            pais_nombre = liga_item["pais"]
            pais = pais_map.get(pais_nombre)

            if not pais:
                self.logger.warning(f"País '{pais_nombre}' no encontrado para la liga '{liga_item['nombre']}'. Saltando...")
                continue

            liga_dto = service.registrar_liga(LigaCreateDTO(
                nombre=liga_item["nombre"],
                nombre_categoria=liga_item.get("categoria"),
                pais_id=pais.id
            ), update=update)
            liga_map[liga_dto.nombre] = liga_dto

        # 4) Torneos
        self.logger.info("Poblando torneos...")
        for torneo_item in TORNEOS:
            liga_nombre = torneo_item["liga"]
            liga = liga_map.get(liga_nombre)

            if not liga:
                self.logger.warning(f"Liga '{liga_nombre}' no encontrada para el torneo '{torneo_item['nombre']}'. Saltando...")
                continue
            
            service.registrar_torneo(TorneoCreateDTO(
                nombre=torneo_item["nombre"],
                liga_id=liga.id
            ), update=update)