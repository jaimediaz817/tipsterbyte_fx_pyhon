# # TODO: PENDIENTE IMPLEMENTAR:
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from core.services import scheduler_service

router = APIRouter()


@router.get("/scheduler/status", tags=["Scheduler"])
def scheduler_status():
    return scheduler_service.get_status()


@router.post("/scheduler/pause-all", tags=["Scheduler"])
def pause_all_jobs():
    return scheduler_service.pause_all()


@router.post("/scheduler/resume-all", tags=["Scheduler"])
def resume_all_jobs():
    return scheduler_service.resume_all()


@router.post("/scheduler/pause/{job_id}", tags=["Scheduler"])
def pause_job(job_id: str):
    try:
        return scheduler_service.pause(job_id)
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": str(e)})


@router.post("/scheduler/resume/{job_id}", tags=["Scheduler"])
def resume_job(job_id: str):
    try:
        return scheduler_service.resume(job_id)
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": str(e)})


@router.post("/scheduler/reload", tags=["Scheduler"])
def reload_jobs():
    return scheduler_service.reload_jobs()


# ============================================================================
# Endpoints específicos para el job de limpieza de logs
# ============================================================================


@router.get("/scheduler/log-cleanup/status", tags=["Scheduler - Log Cleanup"])
def get_log_cleanup_status():
    """Obtiene el estado específico del job de limpieza de logs."""
    return scheduler_service.get_log_cleanup_status()


@router.post("/scheduler/log-cleanup/pause", tags=["Scheduler - Log Cleanup"])
def pause_log_cleanup():
    """Pausa el job de limpieza de logs."""
    return scheduler_service.pause_log_cleanup()


@router.post("/scheduler/log-cleanup/resume", tags=["Scheduler - Log Cleanup"])
def resume_log_cleanup():
    """Reanuda el job de limpieza de logs."""
    return scheduler_service.resume_log_cleanup()


@router.post("/scheduler/log-cleanup/run-now", tags=["Scheduler - Log Cleanup"])
def run_log_cleanup_now():
    """Ejecuta el job de limpieza de logs inmediatamente."""
    return scheduler_service.run_log_cleanup_now()
