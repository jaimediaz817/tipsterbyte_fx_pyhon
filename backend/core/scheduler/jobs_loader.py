from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apps.leagues_manager.scheduler.scheduled_jobs import PROCESS_MAP as PROCESS_MAP_LEAGUES_MANAGER
from shared.repositories.scheduler_repos.scheduled_process_config_repository import ScheduledProcessConfigRepository
from apps.platform_config.infrastructure.models.sql.scheduled_process_config import ScheduledProcessConfig
from core.db.sql.database_sql import SessionLocal
# from shared.repositories.scheduler_repos.scheduled_process_config_repository import ScheduledProcessConfigRepository
from core.scheduler.utils import schedule_async_job
from loguru import logger

# TODO: PENDIENTE: Completar el mapeo de todos los procesos programados
ALL_PROCESS_MAPS = {
    **PROCESS_MAP_LEAGUES_MANAGER,
    # agregar otros process maps aquí
}

def get_scheduled_jobs_from_db() -> list[dict]:
    """ 
        Obtiene las configuraciones de trabajos programados desde la base de datos.

    Returns:
        list[dict]: Lista de configuraciones de trabajos programados habilitados.
    """
    with SessionLocal() as db:
        """ 
        Obtiene las configuraciones de trabajos programados habilitados desde la base de datos.
        """
        repo = ScheduledProcessConfigRepository(db)
        configsRepository = repo.get_all_enabled()
        jobs = []

        for config in configsRepository:
            func = ALL_PROCESS_MAPS.get(config.process_name)
            if func:
                jobs.append({
                    "name": config.process_name,
                    "func": func,
                    "cron": config.cron_expression
                })
            else:
                logger.warning(f"⚠️ Job '{config.process_name}' no está registrado.")
                continue
                
        return jobs
    
def register_jobs(scheduler: AsyncIOScheduler):
    """_summary_
    Registra los trabajos programados en el scheduler.
    Args:
        scheduler (AsyncIOScheduler): _description_
    Returns:
        None
    """
    
    logger.info("⚙️  Registrando trabajos programados desde la base de datos...")    
    scheduled_jobs_config = get_scheduled_jobs_from_db()    
    
    for job_config in scheduled_jobs_config:
        print( job_config)
        job_name = job_config["name"]
        cron_expression = job_config["cron"]
        logger.debug(f"Procesando configuración para el trabajo: '{job_name}'")
        # NOTE: Testear si el job ya existe para evitar duplicados


        # --- ¡LÓGICA DE BÚSQUEDA IMPLEMENTADA! ---
        # Buscamos la función Python real en nuestro mapa.
        job_function = ALL_PROCESS_MAPS.get(job_name)

        # scheduler.add_job(
        #     schedule_async_job(job_config["func"]),
        #     trigger=CronTrigger.from_crontab(job_config["cron"]),
        #     id=job_name,
        #     name=job_name,
        #     replace_existing=True,
        #     misfire_grace_time=3600
        # )
        # logger.info(f"✅ Job '{job_name}' registrado con cron '{job_config['cron']}'")
        
        if job_function:
            # Si encontramos la función, la programamos.
            scheduler.add_job(
                job_function,
                trigger=CronTrigger.from_crontab(cron_expression),
                id=job_name,
                name=job_name,
                replace_existing=True # Importante para evitar duplicados al reiniciar
            )
            logger.success(f"✅ Trabajo '{job_name}' programado con cron '{cron_expression}'.")
        else:
            # Si no, registramos un error claro.
            logger.error(f"❌ No se encontró una función Python mapeada para el trabajo '{job_name}'. El trabajo será ignorado.")        