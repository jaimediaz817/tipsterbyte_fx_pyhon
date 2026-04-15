from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .jobs_loader import register_jobs

scheduler = AsyncIOScheduler(timezone="America/Bogota")


def start_scheduler():
    """
    Inicia el scheduler, registrando los trabajos desde la base de datos.
    """
    scheduler.remove_all_jobs()
    # TODO: pendiente: probar el registro de jobs desde la base de datos
    register_jobs(scheduler)
    scheduler.start()
