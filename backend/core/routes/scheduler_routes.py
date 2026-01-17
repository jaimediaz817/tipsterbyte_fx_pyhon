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
