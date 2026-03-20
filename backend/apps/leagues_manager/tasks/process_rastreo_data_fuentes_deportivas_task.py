import asyncio
import json
import uuid
from datetime import datetime
from loguru import logger
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
    SqlPlatformRepository,
)
from core.config import settings
from core.db.sql.database_sql import SessionLocal
from shared.constants.process.process_codes import (
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
)
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

# --- CAMBIO CLAVE: Importamos la instancia del JobRunner ---
from apps.leagues_manager.application.job_runner_application import job_runner
from apps.leagues_manager.tasks.utils import generate_run_id


def _build_jobs_from_leagues(leagues):
    """
    Filtra y construye la estructura de trabajos a partir de las ligas.

    Args:
        leagues: Lista de ligas con sus torneos y detalles de fuente

    Returns:
        tuple: (flat_jobs_for_execution, grouped_jobs_for_display)
            - flat_jobs_for_execution: Lista plana de tuplas (torneo, detalle) para ejecución
            - grouped_jobs_for_display: Lista de diccionarios agrupados por torneo para visualización
    """
    flat_jobs_for_execution = []
    torneo_map_for_display = {}

    for league in leagues:
        if not league.is_active:
            continue

        for torneo in league.torneos:
            if not torneo.is_active:
                continue

            # Prepara la entrada del torneo para la visualización si no existe
            if torneo.id not in torneo_map_for_display:
                torneo_map_for_display[torneo.id] = {
                    "id": torneo.id,
                    "nombre": torneo.nombre,
                    "fuentes": [],
                }

            for detalle in torneo.detalles_fuente:
                if detalle.is_active and detalle.fuente:
                    # Añadir a la lista plana para la ejecución
                    flat_jobs_for_execution.append((torneo, detalle))

                    # Añadir a la estructura agrupada para la visualización
                    torneo_map_for_display[torneo.id]["fuentes"].append(
                        {"type": detalle.fuente.type, "url": detalle.url}
                    )

    # Convertir el mapa a la lista final de torneos para la visualización
    grouped_jobs_for_display = list(torneo_map_for_display.values())

    return flat_jobs_for_execution, grouped_jobs_for_display


async def launch_process_rastreo_data_fuentes_deportivas_task():
    """
    Orquesta el proceso de rastreo. Genera una lista de todos los trabajos
    de extracción individuales y los ejecuta de forma concurrente.
    """
    run_id = generate_run_id()
    logger.info(f"🚀 Iniciando orquestador. run_id={run_id}")
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CLIENTS)

    with SessionLocal() as session:
        # --- CONECTAR ProcessRunRepository ---
        repo = ProcessRunRepository(db=session)
        run = repo.create_run(run_id, SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS)
        if not run:
            logger.error(
                f"❌ No se pudo crear el ProcessRun. Verifica que el proceso exista en BD."
            )
            return

        process_repo = SqlPlatformRepository(session)
        leagues = process_repo.get_all_leagues_with_full_details()

        # --- Usar función auxiliar para filtrar y construir jobs ---
        logger.info("🔍 Generando lista de trabajos...")
        flat_jobs_for_execution, grouped_jobs_for_display = _build_jobs_from_leagues(
            leagues
        )

        if not flat_jobs_for_execution:
            logger.warning("🏁 No hay trabajos activos. Finalizando.")
            repo.complete_run(run_id)
            return

        logger.info(
            f"⚙️  {len(flat_jobs_for_execution)} trabajos listos. Concurrencia: {settings.MAX_CONCURRENT_CLIENTS}"
        )

        # Imprimir los trabajos en el formato agrupado deseado
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
                # CONSIDERACIÓN IMPORTANTE:
                # Usamos 'await' directamente porque 'job_runner.run_job' es una función
                # asíncrona (`async def`). Está diseñada para cooperar con el bucle de
                # eventos de asyncio.
                # NO usamos 'asyncio.to_thread' porque eso es para ejecutar código
                # SÍNCRONO (bloqueante) en un hilo separado.
                await job_runner.run_job(torneo, detalle, run_id, repo)

        # Crea una lista de tareas (corutinas) para ser ejecutadas.
        tasks = [
            run_job_with_semaphore_wrapper(torneo, detalle)
            for torneo, detalle in flat_jobs_for_execution
        ]

        try:
            # Lanza todas las tareas y espera a que todas terminen.
            await asyncio.gather(*tasks)
            repo.complete_run(run_id)
            logger.success(f"🏁 Orquestador finalizado. run_id={run_id}")
        except Exception as e:
            repo.fail_run(run_id)
            logger.error(f"❌ Orquestador falló. run_id={run_id}. Error: {e}")
            raise  # Re-lanza la excepción para que el proceso padre sepa que falló

    # --- ELIMINADO: Bloque de código duplicado que definía run_job_with_semaphore_wrapper y ejecutaba asyncio.gather de nuevo ---
    # Lo he integrado en el bloque superior para asegurar que solo se ejecute una vez.
