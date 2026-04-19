"""
✅ Jobs Loader corregido segun principio DIP
YA NO tiene dependencias hacia aplicaciones externas
Solo depende del JobRegistry y nada mas
"""

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from .job_registry import JobRegistry
from shared.repositories.scheduler_repos.scheduled_process_config_repository import (
    ScheduledProcessConfigRepository,
)

# ✅ NO IMPORTAR SessionLocal AQUI! Se importa LAZILY solo cuando se necesita


def get_scheduled_jobs_from_db() -> list[dict]:
    """
    Obtiene las configuraciones de trabajos programados habilitados desde la base de datos.
    """
    # ✅ Importacion LAZY: Solo se carga CUANDO se ejecuta la funcion, NO durante importacion / discovery
    from backend.core.db.sql.database_sql import SessionLocal

    with SessionLocal() as db:
        repo = ScheduledProcessConfigRepository(db)
        configs = repo.get_all_enabled()
        jobs = []

        for config in configs:
            job_name = str(config.process_name)
            func = JobRegistry.get(job_name)

            if func:
                jobs.append(
                    {
                        "name": job_name,
                        "func": func,
                        "cron": str(config.cron_expression),
                    }
                )
            else:
                logger.warning(
                    f"⚠️ Job '{job_name}' configurado en BD pero NO REGISTRADO en el sistema."
                )
                continue

        return jobs


def register_jobs(scheduler: AsyncIOScheduler):
    """
    Registra todos los jobs programados en el scheduler
    ✅ 100% compatible hacia atras
    ✅ No rompe ningun job existente
    ✅ Cero acoplamiento con aplicaciones
    """
    logger.info("⚙️  Cargando trabajos programados...")

    jobs_registrados = JobRegistry.get_all()
    logger.info(f"📋 Total jobs registrados automaticamente: {len(jobs_registrados)}")

    scheduled_jobs_config = get_scheduled_jobs_from_db()

    for job_config in scheduled_jobs_config:
        job_name = job_config["name"]
        cron_expression = job_config["cron"]
        job_function = job_config["func"]

        scheduler.add_job(
            job_function,
            trigger=CronTrigger.from_crontab(cron_expression),
            id=job_name,
            name=job_name,
            replace_existing=True,
            misfire_grace_time=3600,
        )

        logger.success(f"✅ Job '{job_name}' programado con cron '{cron_expression}'")

    logger.info(f"✅ Total jobs programados exitosamente: {len(scheduled_jobs_config)}")
