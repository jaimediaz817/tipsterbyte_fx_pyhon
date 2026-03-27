# TODO: tb-task-hu-scheduler-01: implementar el servicio scheduler_service.py
from core.scheduler.jobs_loader import register_jobs
from core.scheduler import scheduler
from fastapi.responses import JSONResponse
import pytz
from loguru import logger


def get_status():
    if not scheduler.running:
        return JSONResponse(
            status_code=503, content={"error": "Scheduler no está activo"}
        )

    jobs = scheduler.get_jobs()
    return {
        "status": "running",
        "active_jobs": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": (
                    job.next_run_time.astimezone(
                        pytz.timezone("America/Bogota")
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    if job.next_run_time
                    else None
                ),
                "status": "paused" if job.next_run_time is None else "scheduled",
                "func": job.func_ref,
            }
            for job in jobs
        ],
    }


def pause_all():
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.pause_job(job.id)
    return {"message": f"{len(jobs)} jobs pausados correctamente"}


def resume_all():
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.resume_job(job.id)
    return {"message": f"{len(jobs)} jobs reanudados correctamente"}


def pause(job_id: str):
    scheduler.pause_job(job_id)
    return {"message": f"Job {job_id} pausado correctamente"}


def resume(job_id: str):
    scheduler.resume_job(job_id)
    return {"message": f"Job {job_id} reanudado correctamente"}


def reload_jobs():
    scheduler.remove_all_jobs()
    register_jobs(scheduler)
    return {"message": "Jobs recargados desde base de datos exitosamente"}


# ============================================================================
# Control específico para el job de limpieza de logs
# ============================================================================

LOG_CLEANUP_JOB_ID = "PROCESS_LOG_CLEANUP"


def get_log_cleanup_status():
    """
    Obtiene el estado específico del job de limpieza de logs.

    Returns:
        dict con información del estado del job de limpieza
    """
    if not scheduler.running:
        return JSONResponse(
            status_code=503, content={"error": "Scheduler no está activo"}
        )

    try:
        job = scheduler.get_job(LOG_CLEANUP_JOB_ID)

        if job is None:
            return {
                "status": "not_registered",
                "message": "Job de limpieza de logs no está registrado en el scheduler",
                "job_id": LOG_CLEANUP_JOB_ID,
            }

        return {
            "status": "running" if job.next_run_time else "paused",
            "job_id": job.id,
            "name": job.name,
            "next_run_time": (
                job.next_run_time.astimezone(pytz.timezone("America/Bogota")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if job.next_run_time
                else None
            ),
            "trigger": str(job.trigger),
            "func": job.func_ref,
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado del job de limpieza: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error obteniendo estado: {str(e)}"},
        )


def pause_log_cleanup():
    """
    Pausa el job de limpieza de logs.

    Returns:
        dict con confirmación de la pausa
    """
    if not scheduler.running:
        return JSONResponse(
            status_code=503, content={"error": "Scheduler no está activo"}
        )

    try:
        scheduler.pause_job(LOG_CLEANUP_JOB_ID)
        logger.info(f"⏸️ Job de limpieza de logs pausado: {LOG_CLEANUP_JOB_ID}")
        return {
            "message": f"Job de limpieza de logs pausado correctamente",
            "job_id": LOG_CLEANUP_JOB_ID,
        }
    except Exception as e:
        logger.error(f"Error pausando job de limpieza: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error pausando job: {str(e)}"},
        )


def resume_log_cleanup():
    """
    Reanuda el job de limpieza de logs.

    Returns:
        dict con confirmación de la reanudación
    """
    if not scheduler.running:
        return JSONResponse(
            status_code=503, content={"error": "Scheduler no está activo"}
        )

    try:
        scheduler.resume_job(LOG_CLEANUP_JOB_ID)
        logger.info(f"▶️ Job de limpieza de logs reanudado: {LOG_CLEANUP_JOB_ID}")
        return {
            "message": f"Job de limpieza de logs reanudado correctamente",
            "job_id": LOG_CLEANUP_JOB_ID,
        }
    except Exception as e:
        logger.error(f"Error reanudando job de limpieza: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error reanudando job: {str(e)}"},
        )


def run_log_cleanup_now():
    """
    Ejecuta el job de limpieza de logs inmediatamente.

    Returns:
        dict con resultado de la ejecución
    """
    if not scheduler.running:
        return JSONResponse(
            status_code=503, content={"error": "Scheduler no está activo"}
        )

    try:
        from core.scheduler.log_cleanup_jobs import LOG_CLEANUP_PROCESS_MAP

        job = LOG_CLEANUP_PROCESS_MAP.get(LOG_CLEANUP_JOB_ID)
        if job is None:
            return JSONResponse(
                status_code=404,
                content={"error": f"Job {LOG_CLEANUP_JOB_ID} no encontrado"},
            )

        # Ejecutar el job inmediatamente
        logger.info(f"🚀 Ejecutando limpieza de logs inmediata...")
        job()

        return {
            "message": "Limpieza de logs ejecutada inmediatamente",
            "job_id": LOG_CLEANUP_JOB_ID,
        }
    except Exception as e:
        logger.error(f"Error ejecutando limpieza inmediata: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error ejecutando limpieza: {str(e)}"},
        )
