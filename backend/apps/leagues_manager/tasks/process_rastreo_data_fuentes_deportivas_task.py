import asyncio
import json
import uuid
from datetime import datetime
from typing import cast, Optional, Protocol


from shared.repositories.scheduler_repos import IProcessRunRepository


# --- INTERFACE LOCAL PARA DIP ---
class IPlatformRepository(Protocol):
    def get_process_by_code(self, code: str):
        """Obtener proceso por codigo"""
        ...


import asyncio
import json
import uuid
from datetime import datetime
from typing import cast
from loguru import logger
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
    SqlPlatformRepository,
)
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import (
    SQLPlatformConfigRepository,
)
from core.config import settings
from core.db.sql.database_sql import SessionLocal
from shared.constants.process.process_codes import (
    PROCESS_EXTRACT_DATA_FUENTES,
)
from shared.repositories.scheduler_repos import ProcessRunRepositoryFactory

# --- CAMBIO CLAVE: Importamos la CLASE JobRunner (no el singleton) ---
from apps.leagues_manager.application.job_runner_application import (
    JobRunnerApplication,
)
from apps.leagues_manager.tasks.utils import generate_run_id

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import (
    ProcessNotFoundException,
    ProcessInactiveException,
    ProcessRunCreationException,
    NoActiveJobsException,
)

# --- CONFIGURACIÓN DE SEMÁFOROS DIFERENCIADOS ---
from core.config_semaphore import get_semaphore_for_robot_type
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum

# --- LOGGING MEJORADO ---
from core.robot_logging import (
    LogSymbols,
    get_robot_emoji,
    log_semaphore_status,
)


def _build_jobs_from_leagues(
    leagues, target_process_id: int | None = None, is_general_orchestrator: bool = False
):
    """
    Filtra y construye la estructura de trabajos a partir de las ligas,
    filtrando opcionalmente por un process_id de DetalleFuenteExtraccion.

    Args:
        leagues: Lista de ligas con sus torneos y detalles de fuente
        target_process_id: Opcional, ID del proceso para filtrar los detalles de fuente.
        is_general_orchestrator: Si es True, ejecuta todos los trabajos sin filtrar por process_id.

    Returns:
        tuple: (flat_jobs_for_execution, grouped_jobs_for_display)
            - flat_jobs_for_execution: Lista plana de tuplas (torneo, detalle) para ejecución
            - grouped_jobs_for_display: Lista de diccionarios agrupados por torneo para visualización
    """
    flat_jobs_for_execution = []
    torneo_map_for_display = {}

    logger.info(f"📊 Ligas cargadas: {len(leagues)}")
    for league in leagues:
        if not league.is_active:
            logger.debug(f"   ⏭️  Liga inactiva: {league.nombre}")
            continue

        logger.info(f"   🏟️  Liga activa: {league.nombre} (ID: {league.id})")

        for torneo in league.torneos:
            if not torneo.is_active:
                logger.debug(f"      ⏭️  Torneo inactivo: {torneo.nombre}")
                continue

            # Prepara la entrada del torneo para la visualización si no existe
            if torneo.id not in torneo_map_for_display:
                torneo_map_for_display[torneo.id] = {
                    "id": torneo.id,
                    "nombre": torneo.nombre,
                    "fuentes": [],
                }

            logger.info(f"      🏆 Torneo activo: {torneo.nombre} (ID: {torneo.id})")
            logger.info(
                f"         📄 Detalles de fuente encontrados: {len(torneo.detalles_fuente)}"
            )

            for detalle in torneo.detalles_fuente:
                fuente_name = detalle.fuente.name if detalle.fuente else "Sin fuente"
                logger.debug(
                    f"         📋 Detalle ID={detalle.id} | Fuente: {fuente_name} | "
                    f"is_active={detalle.is_active} | process_id={detalle.process_id} | "
                    f"target_process_id={target_process_id}"
                )

                if detalle.is_active and detalle.fuente and detalle.fuente.is_active:
                    # --- Lógica de filtrado por process_id ---
                    # Si es el orquestador general, ejecutar TODOS los trabajos
                    # Si es un proceso específico, filtrar solo los que coincidan
                    if not is_general_orchestrator and target_process_id is not None:
                        if detalle.process_id != target_process_id:
                            logger.debug(
                                f"            ❌ FILTRADO: process_id={detalle.process_id} != target={target_process_id}"
                            )
                            continue  # Saltar este detalle si no coincide con el process_id objetivo
                        else:
                            logger.info(
                                f"            ✅ MATCH: process_id={detalle.process_id} == target={target_process_id}"
                            )
                    else:
                        logger.info(
                            f"            ✅ ORQUESTADOR GENERAL: Incluyendo todos los trabajos"
                        )

                    # Añadir a la lista plana para la ejecución
                    flat_jobs_for_execution.append((torneo, detalle))

                    # Añadir a la estructura agrupada para la visualización
                    torneo_map_for_display[torneo.id]["fuentes"].append(
                        {"type": detalle.fuente.type, "url": detalle.url}
                    )
                else:
                    logger.debug(
                        f"            ⏭️  Saltado: is_active={detalle.is_active}, tiene_fuente={detalle.fuente is not None}"
                    )

    # Convertir el mapa a la lista final de torneos para la visualización
    grouped_jobs_for_display = list(torneo_map_for_display.values())

    logger.info(
        f"📊 Resumen: {len(flat_jobs_for_execution)} trabajos seleccionados de {len(leagues)} ligas"
    )

    return flat_jobs_for_execution, grouped_jobs_for_display


async def launch_process_rastreo_data_fuentes_deportivas_task(
    process_code: str = PROCESS_EXTRACT_DATA_FUENTES,
    platform_repo=None,
    process_run_repo=None,
):
    """
    ✅ TASK AHORA ES SOLO UN PROXY
    ✅ NO TIENE NINGUNA LOGICA DE ORQUESTACION
    ✅ TODA LA LOGICA ESTA EN JobRunnerApplication.run_full_orchestrator()
    ✅ FIRMA DEL METODO 100% IGUAL, RETROCOMPATIBLE
    """
    job_runner = JobRunnerApplication()
    await job_runner.run_full_orchestrator(
        process_code, platform_repo, process_run_repo
    )
