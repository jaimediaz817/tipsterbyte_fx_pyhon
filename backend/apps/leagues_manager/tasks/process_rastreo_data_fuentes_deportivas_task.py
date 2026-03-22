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
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
)
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

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
    process_code: str = SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
):  # ¡NUEVO PARÁMETRO CON DEFAULT!
    """
    Orquesta el proceso de rastreo. Genera una lista de todos los trabajos
    de extracción individuales y los ejecuta de forma concurrente,
    filtrando por un código de proceso específico.

    Args:
        process_code: El código del proceso que debe orquestar esta ejecución.
                      Por defecto, usa el orquestador general.
    """
    run_id = generate_run_id()
    logger.info(
        f"🚀 Iniciando orquestador para proceso '{process_code}'. run_id={run_id}"
    )
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CLIENTS)

    # ✅ Crear instancia local de JobRunner (Fase 2: Inyección de dependencias)
    job_runner = JobRunnerApplication()

    with SessionLocal() as session:
        # --- CONECTAR ProcessRunRepository ---
        repo = ProcessRunRepository(db=session)

        # PRIMERO: Verificar si el proceso existe y está activo ANTES de crear el ProcessRun
        platform_config_repo = SQLPlatformConfigRepository(session)
        process_entity = platform_config_repo.get_process_by_code(process_code)
        if not process_entity:
            raise ProcessNotFoundException(process_code)

        # Validar si el proceso está activo
        is_active: bool = cast(bool, process_entity.is_active)
        if not is_active:
            raise ProcessInactiveException(process_code, cast(int, process_entity.id))

        logger.info(
            f"✅ Proceso '{process_code}' está ACTIVO (is_active=True). Procediendo con la ejecución..."
        )

        # SOLO crear ProcessRun si el proceso está activo
        run = repo.create_run(run_id, process_code)
        if not run:
            raise ProcessRunCreationException(process_code, run_id)

        target_process_id: int | None = cast(
            int, process_entity.id
        )  # Este es el ID que usaremos para filtrar

        # Verificar si es el orquestador general (debe ejecutar TODOS los trabajos)
        is_general_orchestrator = (
            process_code == SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
        )

        # Obtener todas las ligas (la filtración por process_id se hará en _build_jobs_from_leagues)
        leagues = SqlPlatformRepository(session).get_all_leagues_with_full_details()

        logger.info("🔍 Generando lista de trabajos...")
        flat_jobs_for_execution, grouped_jobs_for_display = _build_jobs_from_leagues(
            leagues, target_process_id, is_general_orchestrator
        )

        if not flat_jobs_for_execution:
            repo.complete_run(run_id)
            raise NoActiveJobsException(process_code)

        # Resumen de fuentes por tipo
        fuentes_por_tipo = {}
        for torneo, detalle in flat_jobs_for_execution:
            if detalle.fuente and hasattr(detalle.fuente, "type"):
                tipo = (
                    detalle.fuente.type.value
                    if hasattr(detalle.fuente.type, "value")
                    else str(detalle.fuente.type)
                )
                if tipo not in fuentes_por_tipo:
                    fuentes_por_tipo[tipo] = 0
                fuentes_por_tipo[tipo] += 1

        logger.info(
            f"⚙️  {len(flat_jobs_for_execution)} trabajos listos para proceso '{process_code}'. Concurrencia: {settings.MAX_CONCURRENT_CLIENTS}"
        )
        logger.info(f"📊 Distribución de fuentes por tipo: {fuentes_por_tipo}")

        logger.info(">>>>>>>>>>>>>>>>>>>>>> JOBS (AGRUPADOS):")
        logger.info(
            json.dumps(
                {"torneos": grouped_jobs_for_display}, indent=2, ensure_ascii=False
            )
        )

        async def run_job_with_semaphore_wrapper(
            torneo: Torneo, detalle: DetalleFuenteExtraccion
        ):
            """
            Wrapper que adquiere el semáforo y delega la ejecución de UN trabajo al runner.
            """
            fuente_name = (
                detalle.fuente.name if detalle.fuente is not None else "Sin fuente"
            )
            job_info = f"Trabajo para '{torneo.nombre}' (Fuente: {fuente_name})"

            if semaphore.locked():
                logger.info(
                    f"⏳ Cliente en espera: {job_info} (esperando cupo disponible...)"
                )

            async with semaphore:
                await job_runner.run_job(torneo, detalle, run_id, repo)

        tasks = [
            run_job_with_semaphore_wrapper(torneo, detalle)
            for torneo, detalle in flat_jobs_for_execution
        ]

        try:
            await asyncio.gather(*tasks)
            repo.complete_run(run_id)
            logger.success(
                f"🏁 Orquestador finalizado para proceso '{process_code}'. run_id={run_id}"
            )
        except Exception as e:
            repo.fail_run(run_id)
            logger.error(
                f"❌ Orquestador falló para proceso '{process_code}'. run_id={run_id}. Error: {e}"
            )
            raise
