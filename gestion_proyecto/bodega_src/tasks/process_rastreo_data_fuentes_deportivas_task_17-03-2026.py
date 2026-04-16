import asyncio
import uuid
from datetime import datetime
from loguru import logger
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

# Importamos los mocks
from apps.leagues_manager.tests.mock_repositories import MockPlatformRepository
from apps.leagues_manager.tests.mock_data_leagues import (
    MockTorneo,
    MockDetalleFuenteExtraccion,
)


def generate_run_id() -> str:
    """
    Genera un identificador único para una ejecución del scheduler.
    Formato: runid_YYYYMMDD_<uuid4>
    Ejemplo: runid_20260311_a3f1c2d4-8b9e-4f2a-b1c3-d4e5f6a7b8c9
    """
    date_prefix = datetime.now().strftime("%Y%m%d")
    return f"runid_{date_prefix}_{uuid.uuid4()}"


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

        process_repo = MockPlatformRepository(session)
        leagues = process_repo.get_all_leagues_with_full_details()

        print(">>> || LEAGUES: ", leagues)  # Debug: Ver qué datos se están obteniendo

        jobs = []
        logger.info("🔍 Generando lista de trabajos...")
        for league in leagues:
            if not league.is_active:
                continue
            for torneo in league.torneos:
                if not torneo.is_active:
                    continue
                for detalle in torneo.detalles_fuente:
                    if detalle.is_active and detalle.fuente:
                        jobs.append((torneo, detalle))

        if not jobs:
            logger.warning("🏁 No hay trabajos activos. Finalizando.")
            repo.complete_run(run_id)
            return

        logger.info(
            f"⚙️  {len(jobs)} trabajos listos. Concurrencia: {settings.MAX_CONCURRENT_CLIENTS}"
        )
        
        print(">>>>>>>>>>>>>>>>>>>>>> JOBS: ", jobs)

        async def run_job_with_semaphore_wrapper(
            torneo: MockTorneo, detalle: MockDetalleFuenteExtraccion
        ):
            fuente_name = (
                detalle.fuente.name if detalle.fuente is not None else "Sin fuente"
            )
            job_info = f"'{torneo.nombre}' (Fuente: {fuente_name})"
            if semaphore.locked():
                logger.info(f"⏳ En espera: {job_info}")
            async with semaphore:
                # --- PASAMOS repo al job_runner ---
                await job_runner.run_job(torneo, detalle, run_id, repo)

        tasks = [run_job_with_semaphore_wrapper(t, d) for t, d in jobs]

        try:
            await asyncio.gather(*tasks)
            repo.complete_run(run_id)
            logger.success(f"🏁 Orquestador finalizado. run_id={run_id}")
        except Exception as e:
            repo.fail_run(run_id)
            logger.error(f"❌ Orquestador falló. run_id={run_id}. Error: {e}")
            raise

    async def run_job_with_semaphore_wrapper(
        torneo: MockTorneo, detalle: MockDetalleFuenteExtraccion
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
        run_job_with_semaphore_wrapper(torneo, detalle) for torneo, detalle in jobs
    ]
    # Lanza todas las tareas y espera a que todas terminen.
    await asyncio.gather(*tasks)

    logger.success(
        "🏁 Orquestador de rastreo finalizado. Todos los trabajos han sido procesados."
    )
