#!/usr/bin/env python
"""Seeder para cargar continentes y países desde REST Countries API.

Este seeder:
1. Obtiene datos de la API REST Countries
2. Procesa y agrupa países por continente
3. Usa LeaguesService para crear/actualizar continentes y países
4. Es IDEMPOTENTE: se puede ejecutar múltiples veces sin duplicados

NOTA: Este seeder se ejecuta UNA SOLA VEZ (o cuando la DB se reinicia).
No es un robot periódico, es un seeder de datos maestros.
"""

import httpx
from typing import Dict, List

from apps.leagues_manager.application.dto.continente_create_dto import (
    ContinenteCreateDTO,
)
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)
from apps.leagues_manager.services.leagues_service import LeaguesService

from scripts.db.seeders.base_seeder import BaseSeeder

# ===================================================================
#  CONFIGURACIÓN
# ===================================================================

API_URL = (
    "https://restcountries.com/v3.1/all?fields=name,continents,region,subregion,cca2"
)
TIMEOUT_SECONDS = 30

# Mapeo de continentes a códigos
CODIGOS_CONTINENTE = {
    "Africa": "AF",
    "Antarctica": "AN",
    "Asia": "AS",
    "Europe": "EU",
    "North America": "NA",
    "Oceania": "OC",
    "South America": "SA",
}


class GeografiaSeeder(BaseSeeder):
    """Seeder para poblar continentes y países desde REST Countries API."""

    def run(self, update: bool = False) -> Dict:
        """
        Ejecuta el seeder de geografía.

        Args:
            update: Si True, actualiza registros existentes

        Returns:
            Diccionario con métricas de la operación
        """
        metricas = {
            "continentes_creados": 0,
            "continentes_actualizados": 0,
            "paises_creados": 0,
            "paises_actualizados": 0,
            "errores": [],
        }

        self.logger.info("🌍 Iniciando seeder de geografía...")

        try:
            # 1. Obtener datos de la API
            datos_api = self._obtener_datos_api()

            # 2. Agrupar por continente
            datos_agrupados = self._agrupar_por_continente(datos_api)

            # 3. Procesar con servicio
            repo = SQLLeaguesRepository(self.db)
            service = LeaguesService(repo)

            # Cache de continentes para evitar consultas repetidas
            cache_continentes = {}

            for nombre_continente, paises_data in datos_agrupados.items():
                # Registrar continente
                codigo = CODIGOS_CONTINENTE.get(nombre_continente)
                dto_continente = ContinenteCreateDTO(
                    nombre=nombre_continente, codigo=codigo
                )
                continente_dto = service.registrar_continente(
                    dto_continente, update=update
                )
                cache_continentes[nombre_continente] = continente_dto

                # Determinar si fue creado o actualizado
                todos_continentes = service.obtener_todos_los_continentes()
                if continente_dto.id not in [c.id for c in todos_continentes]:
                    metricas["continentes_creados"] += 1
                    self.logger.info(f"➕ Continente creado: {nombre_continente}")
                else:
                    metricas["continentes_actualizados"] += 1
                    self.logger.debug(f"🔄 Continente actualizado: {nombre_continente}")

                # Registrar países
                for pais_data in paises_data:
                    try:
                        nombre_pais = pais_data.get("name", {}).get("common")
                        codigo_iso = pais_data.get("cca2")

                        if not nombre_pais or not codigo_iso:
                            self.logger.warning(
                                f"⚠️ País sin datos válidos, saltando: {pais_data}"
                            )
                            metricas["errores"].append(f"País sin datos: {pais_data}")
                            continue

                        dto_pais = PaisCreateDTO(
                            nombre=nombre_pais,
                            codigo_iso=codigo_iso,
                            continente_id=continente_dto.id,
                        )
                        pais_resultado = service.registrar_pais(dto_pais, update=update)

                        # Contabilizar correctamente si fue creado o ya existía
                        if pais_resultado.was_created:
                            metricas["paises_creados"] += 1
                        else:
                            metricas["paises_actualizados"] += 1

                        # Log de progreso cada 50 países
                        total_procesados = (
                            metricas["paises_creados"] + metricas["paises_actualizados"]
                        )
                        if total_procesados % 50 == 0:
                            self.logger.info(
                                f"📊 Progreso: {total_procesados} países procesados "
                                f"(creados: {metricas['paises_creados']}, "
                                f"actualizados: {metricas['paises_actualizados']})"
                            )

                    except Exception as e:
                        error_msg = f"Error procesando país {pais_data.get('name', {}).get('common', 'Unknown')}: {e}"
                        self.logger.error(f"❌ {error_msg}")
                        metricas["errores"].append(error_msg)

            self.db.commit()
            self.logger.info(
                f"✅ Seeder de geografía completado: "
                f"{metricas['continentes_creados']} continentes, "
                f"{metricas['paises_creados']} países"
            )

        except httpx.HTTPError as e:
            self.logger.error(f"❌ Error de conexión con API: {e}")
            metricas["errores"].append(f"HTTP Error: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            metricas["errores"].append(f"Error: {str(e)}")
            self.db.rollback()
            raise

        return metricas

    def _obtener_datos_api(self) -> List[Dict]:
        """
        Obtiene datos de la API REST Countries.

        Returns:
            Lista de países con sus datos

        Raises:
            httpx.HTTPError: Si hay error en la petición HTTP
        """
        self.logger.info(f"📡 Obteniendo datos de {API_URL}")

        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(API_URL)
            response.raise_for_status()
            datos = response.json()

        self.logger.info(f"✅ Obtenidos {len(datos)} países de la API")
        return datos

    def _agrupar_por_continente(self, datos_api: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa los países por continente.

        Args:
            datos_api: Lista de países de la API

        Returns:
            Diccionario con continentes como keys y listas de países como values
        """
        agrupados: Dict[str, List[Dict]] = {}

        for pais in datos_api:
            # La API retorna una lista de continentes, tomamos el primero
            continentes = pais.get("continents", ["Unknown"])
            continente_nombre = continentes[0] if continentes else "Unknown"

            if continente_nombre not in agrupados:
                agrupados[continente_nombre] = []

            agrupados[continente_nombre].append(pais)

        self.logger.info(f"🌍 Datos agrupados en {len(agrupados)} continentes")
        return agrupados
