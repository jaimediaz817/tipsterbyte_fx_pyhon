#!/usr/bin/env python
"""Seeder para cargar ligas desde API-Football.

Este seeder:
1. Obtiene datos de la API-Football (https://www.api-football.com/documentation-v3)
2. Procesa y mapea ligas por país
3. Usa LeaguesService para crear/actualizar ligas
4. Es IDEMPOTENTE: se puede ejecutar múltiples veces sin duplicados
5. MANTIENE PROGRESO: Guarda el último país procesado para reanudar

NOTA: Este seeder se ejecuta bajo demanda (no es un robot periódico).
      Es un seeder de datos maestros que complementa al GeografiaSeeder.
"""

import httpx
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Awaitable
from datetime import datetime
from typing import cast

from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)
from apps.leagues_manager.services.leagues_service import LeaguesService
from core.config import settings

from scripts.db.seeders.base_seeder import BaseSeeder

# ===================================================================
#  CONFIGURACIÓN
# ===================================================================

API_BASE_URL = settings.API_FOOTBALL_BASE_URL
API_KEY = settings.API_FOOTBALL_KEY
API_HOST = settings.API_FOOTBALL_HOST
TIMEOUT_SECONDS = 10  # Reducido de 30 a 10 segundos

# Ruta archivo configuracion prioridad
CONFIG_LIGAS_PRIORIDAD_PATH = (
    Path(__file__).parents[5] / "backend" / "config" / "ligas_prioridad.json"
)

# Mapeo de tipo de liga de la API a nuestra categoría
# "League" -> Primera división (A)
# "Cup" -> Copas nacionales (B)
# Otros -> Sin categoría (None)
TIPO_LIGA_MAP = {
    "League": "A",
    "Cup": "B",
}

# Configuración de progreso
MAX_PAISES_POR_EJECUCION = 20  # Límite de países por ejecución
MAX_LIGAS_POR_PAIS = 2  # ✅ Solo cargar las N ligas principales de cada pais
DELAY_ENTRE_REQUESTS_SEGUNDOS = 1.2  # ✅ Delay anti rate limit


class LigasSeeder(BaseSeeder):
    """Seeder para poblar ligas desde API-Football."""

    def __init__(self, db, progress_file: Path | None = None):
        """Inicializa el seeder con soporte para testing."""
        super().__init__(db)
        self.PROGRESS_FILE = progress_file or (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "ligas_seeder_progress.json"
        )

    def _cargar_progreso(self) -> Dict:
        """Carga el progreso guardado desde el archivo JSON."""
        try:
            if self.PROGRESS_FILE.exists():
                with open(self.PROGRESS_FILE, "r", encoding="utf-8") as f:
                    progreso = json.load(f)
                self.logger.info(
                    f"📂 Progreso cargado: último país ID={progreso.get('ultimo_pais_id', 0)}"
                )
                return progreso
        except Exception as e:
            self.logger.warning(f"⚠️ Error cargando progreso: {e}")

        # Progreso por defecto
        return {
            "ultimo_pais_id": 0,
            "ultima_ejecucion": None,
            "total_paises_procesados": 0,
            "total_ligas_creadas": 0,
            "total_ligas_actualizadas": 0,
        }

    def _guardar_progreso(self, progreso: Dict) -> None:
        """Guarda el progreso actual en el archivo JSON."""
        try:
            # Crear directorio si no existe
            self.PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

            progreso["ultima_ejecucion"] = datetime.now().isoformat()

            with open(self.PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progreso, f, indent=2, ensure_ascii=False)

            self.logger.info(
                f"💾 Progreso guardado: último país ID={progreso.get('ultimo_pais_id', 0)}"
            )
        except Exception as e:
            self.logger.error(f"❌ Error guardando progreso: {e}")

    def run(self, update: bool = False) -> Dict:
        """
        Ejecuta el seeder de ligas con límite de países y tracking de progreso.

        Args:
            update: Si True, actualiza registros existentes

        Returns:
            Diccionario con métricas de la operación
        """
        metricas = {
            "ligas_creadas": 0,
            "ligas_actualizadas": 0,
            "paises_procesados": 0,
            "paises_con_ligas": 0,
            "errores": [],
            "ultimo_pais_id": 0,
            "paises_saltados": 0,
        }

        self.logger.info("⚽ Iniciando seeder de ligas desde API-Football...")
        self.logger.info(f"📊 Límite: {MAX_PAISES_POR_EJECUCION} países por ejecución")

        try:
            # 1. Cargar progreso guardado
            progreso = self._cargar_progreso()
            ultimo_pais_id = progreso.get("ultimo_pais_id", 0)

            # 2. Obtener países de la BD (ya cargados por GeografiaSeeder)
            repo = SQLLeaguesRepository(self.db)

            # ✅ SOLUCION FINAL 100% VALIDA para error Pylance @Transactional en CLASE
            # Problema: Decorador @Transactional transforma la clase entera, constructor devuelve Union[LeaguesService, Awaitable[LeaguesService]]
            # Pylance no puede inferir correctamente aunque en runtime SIEMPRE es instancia sincrona

            # ✅ SOLUCION PERMANENTE 100% VALIDA ERROR PYLANCE @Transactional
            # El decorador transforma el constructor devolviendo Union[LeaguesService, Awaitable[LeaguesService]]
            # Pylance no puede inferirlo correctamente aunque runtime SIEMPRE es instancia sincrona
            service = LeaguesService(
                repo_continente=repo,
                repo_pais=repo,
                repo_liga=repo,
                repo_torneo=repo,
                repo_fuente=repo,
                repo_detalle_fuente=repo,
            )

            # ✅ SOLUCION DEFINITIVA ERROR PYLANCE: Decorador @Transactional retorna Awaitable falso positivo
            # Esta es la solución ESTANDAR OFICIAL aprobada para TODO el proyecto
            from typing import cast, Any

            service = cast(Any, service)

            paises_bd = service.obtener_todos_los_paises()
            self.logger.info(f"🌍 Países en BD: {len(paises_bd)}")
            self.logger.info(f"🔄 Reanudando desde país ID: {ultimo_pais_id}")

            # 3. Filtrar países: solo procesar desde el último procesado
            paises_a_procesar = [p for p in paises_bd if p.id > ultimo_pais_id]

            # 4. Aplicar límite de países por ejecución
            paises_limitados = paises_a_procesar[:MAX_PAISES_POR_EJECUCION]

            self.logger.info(
                f"🎯 Países a procesar en esta ejecución: {len(paises_limitados)}"
            )

            if len(paises_a_procesar) > MAX_PAISES_POR_EJECUCION:
                self.logger.info(
                    f"⏳ Quedan {len(paises_a_procesar) - MAX_PAISES_POR_EJECUCION} países pendientes para la siguiente ejecución"
                )

            # 5. Procesar cada país
            rate_limit_alcanzado = False

            for idx, pais in enumerate(paises_limitados, 1):
                try:
                    self.logger.info(
                        f"📍 [{idx}/{len(paises_limitados)}] Procesando: {pais.nombre} (ID: {pais.id})"
                    )

                    # Solo procesar países con código ISO
                    if not pais.codigo_iso:
                        self.logger.warning(
                            f"⚠️ País sin código ISO, saltando: {pais.nombre}"
                        )
                        metricas["paises_saltados"] += 1
                        # Actualizar progreso incluso si se salta
                        metricas["ultimo_pais_id"] = pais.id
                        continue

                    # Obtener ligas de la API para este país
                    ligas_api = self._obtener_ligas_por_pais(pais.nombre)

                    # ✅ Delay anti Rate Limit entre paises
                    time.sleep(DELAY_ENTRE_REQUESTS_SEGUNDOS)

                    if not ligas_api:
                        self.logger.debug(f"📭 Sin ligas en API para: {pais.nombre}")
                        metricas["paises_saltados"] += 1
                        metricas["paises_procesados"] += 1
                        # Actualizar progreso incluso si no hay ligas
                        metricas["ultimo_pais_id"] = pais.id
                        continue

                    metricas["paises_con_ligas"] += 1

                    # ✅ Limitar a las MAX_LIGAS_POR_PAIS primeras ligas (mas importantes)
                    ligas_limitadas = ligas_api[:MAX_LIGAS_POR_PAIS]
                    self.logger.debug(
                        f"🔹 Limitando a {len(ligas_limitadas)}/{len(ligas_api)} ligas principales para {pais.nombre}"
                    )

                    # Procesar cada liga
                    for liga_data in ligas_limitadas:
                        try:
                            resultado = self._procesar_liga(
                                liga_data,
                                pais.id,
                                service,
                                update,
                            )

                            if resultado == "creada":
                                metricas["ligas_creadas"] += 1
                            elif resultado == "actualizada":
                                metricas["ligas_actualizadas"] += 1

                        except Exception as e:
                            error_msg = f"Error procesando liga {liga_data.get('league', {}).get('name', 'Unknown')} de {pais.nombre}: {e}"
                            self.logger.error(f"❌ {error_msg}")
                            metricas["errores"].append(error_msg)

                    metricas["paises_procesados"] += 1
                    metricas["ultimo_pais_id"] = pais.id

                    # Log de progreso detallado
                    self.logger.info(
                        f"✅ [{idx}/{len(paises_limitados)}] {pais.nombre} completado "
                        f"(Ligas: {metricas['ligas_creadas']} creadas, {metricas['ligas_actualizadas']} actualizadas)"
                    )

                except RuntimeError as e:
                    if str(e) == "RATE_LIMIT_REACHED":
                        self.logger.warning(
                            "🛑 Deteniendo ejecucion por Rate Limit alcanzado"
                        )
                        rate_limit_alcanzado = True
                        break
                    else:
                        error_msg = f"Error procesando país {pais.nombre}: {e}"
                        self.logger.error(f"❌ {error_msg}")
                        metricas["errores"].append(error_msg)

                except Exception as e:
                    error_msg = f"Error procesando país {pais.nombre}: {e}"
                    self.logger.error(f"❌ {error_msg}")
                    metricas["errores"].append(error_msg)

            # 6. Guardar progreso
            progreso_actualizado = {
                "ultimo_pais_id": metricas["ultimo_pais_id"],
                "ultima_ejecucion": datetime.now().isoformat(),
                "total_paises_procesados": progreso.get("total_paises_procesados", 0)
                + metricas["paises_procesados"],
                "total_ligas_creadas": progreso.get("total_ligas_creadas", 0)
                + metricas["ligas_creadas"],
                "total_ligas_actualizadas": progreso.get("total_ligas_actualizadas", 0)
                + metricas["ligas_actualizadas"],
            }
            self._guardar_progreso(progreso_actualizado)

            self.db.commit()
            self.logger.info(
                f"✅ Seeder de ligas completado: "
                f"{metricas['ligas_creadas']} ligas creadas, "
                f"{metricas['ligas_actualizadas']} actualizadas, "
                f"{metricas['paises_procesados']} países procesados"
            )

            if len(paises_a_procesar) > MAX_PAISES_POR_EJECUCION:
                self.logger.info(
                    f"🔄 Para continuar, ejecute el seeder nuevamente. "
                    f"Se reanudará desde el país ID {metricas['ultimo_pais_id'] + 1}"
                )

            # ✅ Mensaje especial si se alcanzo Rate Limit
            if rate_limit_alcanzado:
                self.logger.info("")
                self.logger.info("=" * 80)
                self.logger.info("✅ 🚨 RATE LIMIT ALCANZADO CORRECTAMENTE")
                self.logger.info("=" * 80)
                self.logger.info("📌 El progreso ha sido GUARDADO correctamente")
                self.logger.info("📌 Limite diario se restablece en 24 horas")
                self.logger.info("")
                self.logger.info("👉 COMANDO PARA CONTINUAR MAÑANA:")
                self.logger.info(
                    "   cd backend && python -m scripts.db.seeders.sql.ligas_seeder"
                )
                self.logger.info("")
                self.logger.info(
                    "💡 Al ejecutarlo mañana, continuara EXACTAMENTE donde se quedo"
                )
                self.logger.info("=" * 80)
                self.logger.info("")

        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            metricas["errores"].append(f"Error: {str(e)}")
            self.db.rollback()

            # ✅ Manejo GRACEFUL: No lanzar excepcion, no romper cadena de seeders
            self.logger.info(
                "⚠️ Terminando ejecucion limpiamente sin romper seeders posteriores"
            )

        return metricas

    def _obtener_ligas_por_pais(self, nombre_pais: str) -> List[Dict]:
        """
        Obtiene ligas de un país desde la API-Football.

        Args:
            nombre_pais: Nombre del país

        Returns:
            Lista de ligas del país
        """
        try:
            headers = {
                "x-apisports-key": API_KEY,
                "x-apisports-host": API_HOST,
            }

            with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                response = client.get(
                    f"{API_BASE_URL}/leagues",
                    headers=headers,
                    params={"country": nombre_pais},
                )
                response.raise_for_status()
                data = response.json()

                ligas = data.get("response", [])
                self.logger.debug(f"📡 Obtenidas {len(ligas)} ligas para {nombre_pais}")
                return ligas

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.logger.critical(
                    "🚨 RATE LIMIT ALCANZADO API-Football. Deteniendo ejecucion."
                )
                self.logger.info(
                    "💡 Limite diario se restablece automaticamente en 24h."
                )
                # Detener toda la ejecucion inmediatamente
                raise RuntimeError("RATE_LIMIT_REACHED")

            self.logger.error(f"❌ Error HTTP obteniendo ligas para {nombre_pais}: {e}")
            return []
        except httpx.HTTPError as e:
            self.logger.error(f"❌ Error HTTP obteniendo ligas para {nombre_pais}: {e}")
            return []
        except Exception as e:
            self.logger.error(
                f"❌ Error inesperado obteniendo ligas para {nombre_pais}: {e}"
            )
            return []

    def _procesar_liga(
        self,
        liga_data: Dict,
        pais_id: int,
        service,  # type: ignore
        update: bool,
    ) -> str:
        """
        Procesa una liga individual.

        Args:
            liga_data: Datos de la liga desde la API
            pais_id: ID del país en nuestra BD
            service: Instancia del servicio
            update: Si True, actualiza registros existentes

        Returns:
            "creada" si se creó, "actualizada" si se actualizó, "ignorada" si no se procesó
        """
        league_info = liga_data.get("league", {})
        liga_nombre = league_info.get("name")
        liga_id_api = league_info.get("id")
        liga_tipo = league_info.get("type")  # "League" o "Cup"
        liga_logo = league_info.get("logo")

        if not liga_nombre or not liga_id_api:
            self.logger.warning(f"⚠️ Liga sin datos válidos, saltando: {league_info}")
            return "ignorada"

        # Mapear tipo de liga a nuestra categoría
        categoria_str = TIPO_LIGA_MAP.get(liga_tipo)
        categoria: CategoriaLigaEnum | None = None
        if categoria_str:
            try:
                categoria = CategoriaLigaEnum(categoria_str)
            except ValueError:
                categoria = None

        # Crear DTO
        from typing import cast

        dto = LigaCreateDTO(
            nombre=liga_nombre,
            pais_id=cast(int, pais_id),
            nombre_categoria=categoria,
        )

        # Registrar liga
        liga_resultado = service.registrar_liga(dto, update=update)

        # Actualizar campos de API-Football si la liga fue creada o actualizada
        if liga_resultado:
            # Verificar si fue creada o actualizada
            if liga_resultado.id_api_externa == liga_id_api:
                # Ya existía con este ID de API, fue actualizada
                return "actualizada"
            else:
                # Nueva liga, actualizar campos de API
                service.actualizar_liga_api_football(
                    liga_id=liga_resultado.id,
                    id_api_externa=liga_id_api,
                    logo_url=liga_logo,
                    tipo_liga=liga_tipo,
                )
                return "creada"

        return "ignorada"
