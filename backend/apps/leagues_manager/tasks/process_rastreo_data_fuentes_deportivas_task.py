

import asyncio
from loguru import logger
from core.config import settings
from core.db.sql.database_sql import SessionLocal
            
# --- CAMBIO CLAVE: Importamos la instancia del JobRunner ---
from apps.leagues_manager.application.job_runner_application import job_runner

# Importamos los mocks
from apps.leagues_manager.tests.mock_repositories import MockPlatformRepository
from apps.leagues_manager.tests.mock_data_leagues import MockTorneo, MockDetalleFuenteExtraccion


async def launch_process_rastreo_data_fuentes_deportivas_task():
    """
    Orquesta el proceso de rastreo. Genera una lista de todos los trabajos
    de extracción individuales y los ejecuta de forma concurrente.
    """
    logger.info("🚀 Iniciando orquestador de rastreo de fuentes deportivas.")
    
    # 🔒 Limitar a N procesos concurrentes reales
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CLIENTS)

    with SessionLocal() as session:
        # TODO: Refactor
        # process_repo = ProcessRepository(session)
        process_repo = MockPlatformRepository(session)
        leagues = process_repo.get_all_leagues_with_full_details()

        jobs = []
        logger.info("🔍 Generando lista de trabajos de extracción individuales...")
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
            logger.warning("🏁 No se encontraron trabajos de extracción activos para ejecutar. Finalizando.")
            return        
        logger.info(f"⚙️  {len(jobs)} trabajos listos. Ejecutando con una concurrencia de {settings.MAX_CONCURRENT_CLIENTS}. FROM: leagues_manager/tasks/process_rastreo_data_fuentes_deportivas_task.py")
        

    async def run_job_with_semaphore_wrapper(torneo: MockTorneo, detalle: MockDetalleFuenteExtraccion):
        """
        Wrapper que adquiere el semáforo y delega la ejecución de UN trabajo al runner.
        """
        job_info = f"Trabajo para '{torneo.name}' (Fuente: {detalle.fuente.name})"

        if semaphore.locked():
            logger.info(f"⏳ Cliente en espera: {job_info} (esperando cupo disponible...)")
            
        async with semaphore:
            # CONSIDERACIÓN IMPORTANTE:
            # Usamos 'await' directamente porque 'job_runner.run_job' es una función
            # asíncrona (`async def`). Está diseñada para cooperar con el bucle de
            # eventos de asyncio.
            # NO usamos 'asyncio.to_thread' porque eso es para ejecutar código
            # SÍNCRONO (bloqueante) en un hilo separado.
            await job_runner.run_job(torneo, detalle) 

    # Crea una lista de tareas (corutinas) para ser ejecutadas.
    tasks = [run_job_with_semaphore_wrapper(torneo, detalle) for torneo, detalle in jobs]
    # Lanza todas las tareas y espera a que todas terminen.
    await asyncio.gather(*tasks)

    logger.success("🏁 Orquestador de rastreo finalizado. Todos los trabajos han sido procesados.")